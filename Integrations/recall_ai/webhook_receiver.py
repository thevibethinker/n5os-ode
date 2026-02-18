#!/usr/bin/env python3
"""
Recall.ai Webhook Receiver
FastAPI server that receives webhook events and triggers meeting deposit
Enhanced with Svix signature verification and comprehensive event handling
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from svix.webhooks import Webhook

# Import config - handle both module and direct execution
try:
    from .config import (
        RECALL_WEBHOOK_SECRET,
        WEBHOOK_DB_PATH,
        WEBHOOK_LOG_PATH,
        WEBHOOK_PORT,
    )
    from .meeting_depositor import deposit_meeting
    from .recall_client import RecallClient
    from .calendar_poller import start_poller_thread
except ImportError:
    # Direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from config import RECALL_WEBHOOK_SECRET, WEBHOOK_DB_PATH, WEBHOOK_LOG_PATH, WEBHOOK_PORT
    from meeting_depositor import deposit_meeting
    from recall_client import RecallClient
    from calendar_poller import start_poller_thread

# Inbox poller (separate path since it lives in Skills/)
sys.path.insert(0, "/home/workspace/Skills/meeting-ingestion/scripts")
try:
    from inbox_poller import start_inbox_poller_thread
except ImportError:
    start_inbox_poller_thread = None

_ = RecallClient  # Suppress unused import warning (available for future use)

# Setup logging
os.makedirs(os.path.dirname(WEBHOOK_LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(WEBHOOK_LOG_PATH),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recall.ai Webhook Receiver")


def init_db():
    """Initialize SQLite database for webhook events"""
    os.makedirs(os.path.dirname(WEBHOOK_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    cursor = conn.cursor()
    
    # Enhanced event logging table for all bot lifecycle events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,  -- svix-id for deduplication
            bot_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            sub_code TEXT,  -- bot sub-status codes
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            payload JSON,
            processed BOOLEAN DEFAULT FALSE,
            error TEXT
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_events_bot_id ON bot_events(bot_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_events_type ON bot_events(event_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_events_event_id ON bot_events(event_id)
    """)
    
    # Keep legacy table for backwards compatibility
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            bot_id TEXT,
            payload TEXT NOT NULL,
            received_at TEXT NOT NULL,
            processed_at TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            error TEXT
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_id ON webhook_events(bot_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_status ON webhook_events(status)
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized: {WEBHOOK_DB_PATH}")


def store_bot_event(event_id: str, bot_id: str, event_type: str, payload: dict, sub_code: Optional[str] = None) -> bool:
    """Store bot event with deduplication"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO bot_events (event_id, bot_id, event_type, sub_code, payload)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event_id,
            bot_id,
            event_type,
            sub_code,
            json.dumps(payload),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Event already exists, skip processing
        logger.info(f"Duplicate event {event_id}, skipping")
        return False
    finally:
        conn.close()


def update_bot_event(event_id: str, processed: bool = True, error: Optional[str] = None):
    """Update bot event processing status"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE bot_events
        SET processed = ?, error = ?
        WHERE event_id = ?
    """, (processed, error, event_id))
    
    conn.commit()
    conn.close()


def store_legacy_event(event_type: str, bot_id: Optional[str], payload: dict) -> int:
    """Store webhook event in legacy table for backwards compatibility"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO webhook_events (event_type, bot_id, payload, received_at)
        VALUES (?, ?, ?, ?)
    """, (
        event_type,
        bot_id,
        json.dumps(payload),
        datetime.now(timezone.utc).isoformat(),
    ))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return event_id


def update_legacy_event(event_id: int, status: str, result: Optional[str] = None, error: Optional[str] = None):
    """Update legacy event processing status"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE webhook_events
        SET status = ?, processed_at = ?, result = ?, error = ?
        WHERE id = ?
    """, (
        status,
        datetime.now(timezone.utc).isoformat(),
        result,
        error,
        event_id,
    ))
    
    conn.commit()
    conn.close()


def verify_svix_signature(body: bytes, svix_id: str, svix_timestamp: str, svix_signature: str) -> bool:
    """Verify Svix webhook signature"""
    BYPASS_SIGNATURE_VERIFICATION = False  # Re-enabled to debug signature issue
    if BYPASS_SIGNATURE_VERIFICATION:
        return True

    if not RECALL_WEBHOOK_SECRET:
        logger.warning("No webhook signing secret configured, skipping verification")
        return True  # Skip verification when no secret configured
    
    try:
        wh = Webhook(RECALL_WEBHOOK_SECRET)
        # Recall uses webhook-* headers instead of svix-* headers
        wh.verify(body, {
            "webhook-id": svix_id,
            "webhook-timestamp": svix_timestamp, 
            "webhook-signature": svix_signature
        })
        return True
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False


def send_sms_alert(message: str):
    """Send SMS alert to V using internal API"""
    try:
        # Use the send_sms_to_user API endpoint
        import requests
        response = requests.post(
            "http://localhost:8769/send_sms",  # N5 conversation API
            json={"message": message},
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"SMS alert sent: {message}")
        else:
            logger.error(f"Failed to send SMS: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending SMS alert: {e}")
        # Fallback: try subprocess call
        try:
            subprocess.run([
                "python3", "/home/workspace/N5/scripts/send_sms.py", 
                "--message", message
            ], timeout=30, check=False)
        except Exception as fallback_e:
            logger.error(f"Fallback SMS failed: {fallback_e}")


async def process_bot_done(event_id: str, bot_id: str, legacy_event_id: int):
    """Process bot.done event - download and deposit recording"""
    try:
        logger.info(f"Processing bot.done for {bot_id}")
        
        result = deposit_meeting(bot_id)

        # Update both new and legacy tables
        update_bot_event(event_id, processed=True)
        update_legacy_event(
            legacy_event_id,
            status="processed",
            result=json.dumps(result),
        )

        meeting_id = result.get('meeting_id')
        logger.info(f"Successfully deposited meeting: {meeting_id}")

        # Auto-trigger pipeline processing on the deposited meeting
        if result.get('status') == 'deposited' and meeting_id:
            try:
                import subprocess
                cli_path = "/home/workspace/Skills/meeting-ingestion/scripts/meeting_cli.py"
                log_path = f"/dev/shm/meeting-process-{meeting_id}.log"
                subprocess.Popen(
                    [sys.executable, cli_path, "tick", "--auto-process", "--target", meeting_id],
                    stdout=open(log_path, "w"),
                    stderr=subprocess.STDOUT,
                )
                logger.info(f"Auto-processing triggered for {meeting_id} (log: {log_path})")
            except Exception as proc_e:
                logger.error(f"Failed to trigger auto-processing for {meeting_id}: {proc_e}")
        
    except Exception as e:
        logger.error(f"Failed to process bot {bot_id}: {e}")
        update_bot_event(event_id, processed=True, error=str(e))
        update_legacy_event(legacy_event_id, status="failed", error=str(e))


async def handle_bot_event(event_id: str, event_type: str, bot_id: str, payload: dict, background_tasks: BackgroundTasks) -> bool:
    """Handle specific bot lifecycle events"""
    data = payload.get("data", {})
    status = data.get("status", {})
    sub_code = status.get("code")
    
    # Store event with sub-code for detailed tracking
    if not store_bot_event(event_id, bot_id, event_type, payload, sub_code):
        return False  # Duplicate event, skip processing
    
    # Also store in legacy table for backwards compatibility
    legacy_event_id = store_legacy_event(event_type, bot_id, payload)
    
    if event_type == "bot.status_change":
        logger.info(f"Bot {bot_id} status changed to: {sub_code}")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.joining_call":
        logger.info(f"Bot {bot_id} joining call")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.in_waiting_room":
        logger.info(f"Bot {bot_id} in waiting room")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.in_call_not_recording":
        logger.warning(f"Bot {bot_id} in call but not recording - possible permission issue")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.recording_permission_allowed":
        logger.info(f"Bot {bot_id} recording permission granted")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.recording_permission_denied":
        logger.error(f"Bot {bot_id} recording permission denied")
        meeting_url = data.get("meeting_url", "unknown")
        send_sms_alert(f"[RECALL] Bot {bot_id} denied recording permission. Meeting: {meeting_url}")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.in_call_recording":
        logger.info(f"Bot {bot_id} now recording")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.call_ended":
        logger.info(f"Bot {bot_id} call ended")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.done":
        logger.info(f"Bot {bot_id} finished - scheduling deposit processing")
        background_tasks.add_task(process_bot_done, event_id, bot_id, legacy_event_id)
        
    elif event_type == "bot.fatal":
        error_msg = data.get("error", "Unknown error")
        # Ensure error_msg is a string
        if not isinstance(error_msg, str):
            error_msg = json.dumps(error_msg) if isinstance(error_msg, (dict, list)) else str(error_msg)
        
        logger.error(f"Bot {bot_id} fatal error: {error_msg}")
        meeting_url = data.get("meeting_url", "unknown")
        send_sms_alert(f"[RECALL] Bot {bot_id} failed: {error_msg}. Meeting: {meeting_url}")
        update_legacy_event(legacy_event_id, status="failed", error=error_msg)
        
    elif event_type == "bot.participant_join":
        participant_id = data.get("participant_id", "unknown")
        participant_name = data.get("participant_name", "unknown")
        logger.info(f"Bot {bot_id} - participant joined: {participant_name} ({participant_id})")
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "bot.participant_leave":
        participant_id = data.get("participant_id", "unknown")
        participant_name = data.get("participant_name", "unknown")
        logger.info(f"Bot {bot_id} - participant left: {participant_name} ({participant_id})")
        update_legacy_event(legacy_event_id, status="logged")
        
    else:
        logger.info(f"Unhandled event type: {event_type}")
        update_legacy_event(legacy_event_id, status="ignored")
    return True


@app.on_event("startup")
async def startup():
    init_db()
    # Start calendar poller as background daemon thread
    try:
        start_poller_thread()
        logger.info("Calendar poller thread started")
    except Exception as e:
        logger.error(f"Failed to start calendar poller: {e} (webhook receiver continues without it)")
    # Start inbox poller for direct drop detection
    if start_inbox_poller_thread:
        try:
            start_inbox_poller_thread()
            logger.info("Inbox poller thread started")
        except Exception as e:
            logger.error(f"Failed to start inbox poller: {e} (webhook receiver continues without it)")
    logger.info("Recall.ai webhook receiver started with enhanced event handling")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "recall-webhook"}


@app.post("/webhook/recall/debug")
async def debug_webhook(request: Request):
    """
    Debug endpoint that logs all headers and body without signature verification.
    This is useful for seeing exactly what Recall is sending.
    """
    # Get raw body for logging
    body = await request.body()
    
    # Get all headers
    headers = dict(request.headers)
    
    # Log headers and body
    logger.info(f"Debug webhook received: Headers: {headers}, Body: {body}")
    
    return JSONResponse(
        content={"status": "received", "message": "Debug log complete"},
        status_code=200,
    )


@app.post("/webhook/recall")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive webhook events from Recall.ai with Svix signature verification
    
    Bot Lifecycle Events:
    - bot.status_change: Log status transitions with sub-code tracking
    - bot.joining_call: Track bot joining state
    - bot.in_waiting_room: Track waiting room state with timestamp
    - bot.in_call_not_recording: Warning - bot in call but not recording
    - bot.recording_permission_allowed: Log compliance - permission granted
    - bot.recording_permission_denied: Alert via SMS, log denial reason
    - bot.in_call_recording: Track active recording state
    - bot.call_ended: Track call completion with sub-code details
    - bot.done: Trigger recording download and deposit pipeline (async)
    - bot.fatal: Alert via SMS with error details, log failure
    - bot.participant_join: Track participant join for timeline
    - bot.participant_leave: Track participant leave for timeline
    
    Recording Events:
    - recording.ready: Legacy trigger for deposit pipeline
    - recording.processing: Recording processing started
    - recording.done: Recording successfully completed
    - recording.failed: Recording failed - SMS alert
    - recording.deleted: Recording was deleted
    
    Media Events:
    - media_expired: Media expired - SMS alert warning
    
    Transcript Events:
    - transcript.ready: Transcript processing complete
    
    All events are logged to SQLite with deduplication via svix-id.
    Long-running tasks (bot.done) are processed asynchronously to avoid
    the 15-second webhook timeout.
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # DEBUG: Log all incoming headers
    all_headers = dict(request.headers)
    logger.info(f"DEBUG - All request headers: {all_headers}")
    logger.info(f"DEBUG - Body preview: {body[:200] if body else 'empty'}")
    
    # Recall uses webhook-* headers (not svix-*)
    svix_id = request.headers.get("webhook-id", "")
    svix_timestamp = request.headers.get("webhook-timestamp", "")
    svix_signature = request.headers.get("webhook-signature", "")
    
    # Verify Svix signature
    if not verify_svix_signature(body, svix_id, svix_timestamp, svix_signature):
        logger.warning(f"Invalid Svix signature for event {svix_id}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = payload.get("event")
    bot_id = payload.get("data", {}).get("bot_id")
    if not bot_id:
        bot_id = payload.get("data", {}).get("bot", {}).get("id")
    
    logger.info(f"Received webhook: {event_type} for bot {bot_id} (event_id: {svix_id})")
    
    # Handle bot lifecycle events
    if event_type.startswith("bot.") and bot_id:
        is_new = await handle_bot_event(svix_id, event_type, bot_id, payload, background_tasks)
        if not is_new:
            return JSONResponse(content={"status": "duplicate", "event_id": svix_id})
    
    # Handle legacy events for backwards compatibility
    elif event_type == "recording.ready":
        logger.info(f"Recording ready for bot {bot_id}")
        if bot_id:
            # Use legacy processing for recording.ready
            legacy_event_id = store_legacy_event(event_type, bot_id, payload)
            if not store_bot_event(svix_id, bot_id, event_type, payload):
                return JSONResponse(content={"status": "duplicate", "event_id": svix_id})
            background_tasks.add_task(process_bot_done, svix_id, bot_id, legacy_event_id)
    
    elif event_type == "recording.processing":
        logger.info(f"Recording processing started for bot {bot_id}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "recording.done":
        logger.info(f"Recording completed for bot {bot_id}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "recording.failed":
        error_msg = data.get("error", "Unknown error")
        logger.error(f"Recording failed for bot {bot_id}: {error_msg}")
        send_sms_alert(f"[RECALL] Recording failed for bot {bot_id}: {error_msg}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="failed", error=error_msg)
        
    elif event_type == "recording.deleted":
        logger.warning(f"Recording deleted for bot {bot_id}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "media_expired":
        logger.warning(f"Media expired for bot {bot_id}")
        send_sms_alert(f"[RECALL] Media expired for bot {bot_id} - recording may need re-download")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="logged")
        
    elif event_type == "transcript.ready":
        logger.info(f"Transcript ready for bot {bot_id}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="logged")
    
    else:
        logger.info(f"Unhandled event type: {event_type}")
        legacy_event_id = store_legacy_event(event_type, bot_id, payload)
        store_bot_event(svix_id, bot_id or "unknown", event_type, payload)
        update_legacy_event(legacy_event_id, status="ignored")
    
    return JSONResponse(
        content={"status": "received", "event_id": svix_id},
        status_code=200,
    )


@app.get("/webhook/recall/events")
async def list_events(
    limit: int = 50,
    status: Optional[str] = None,
    bot_id: Optional[str] = None,
):
    """List recent webhook events from legacy table"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM webhook_events WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if bot_id:
        query += " AND bot_id = ?"
        params.append(bot_id)
    
    query += " ORDER BY received_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        event = dict(row)
        # Parse JSON fields
        if event.get("payload"):
            event["payload"] = json.loads(event["payload"])
        if event.get("result"):
            event["result"] = json.loads(event["result"])
        events.append(event)
    
    return {"events": events, "count": len(events)}


@app.get("/webhook/recall/bot-events")
async def list_bot_events(
    limit: int = 50,
    event_type: Optional[str] = None,
    bot_id: Optional[str] = None,
    processed: Optional[bool] = None,
):
    """List bot lifecycle events from enhanced table"""
    conn = sqlite3.connect(WEBHOOK_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM bot_events WHERE 1=1"
    params = []
    
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
    
    if bot_id:
        query += " AND bot_id = ?"
        params.append(bot_id)
    
    if processed is not None:
        query += " AND processed = ?"
        params.append(processed)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        event = dict(row)
        # Parse JSON payload
        if event.get("payload"):
            event["payload"] = json.loads(event["payload"])
        events.append(event)
    
    return {"events": events, "count": len(events)}


def main():
    """Run the webhook receiver"""
    uvicorn.run(
        "webhook_receiver:app",
        host="0.0.0.0",
        port=WEBHOOK_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()