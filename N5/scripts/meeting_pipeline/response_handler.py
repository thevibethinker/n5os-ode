#!/usr/bin/env python3
"""
AI Response Handler
Processes completed AI responses and finalizes meetings.
"""
import sqlite3
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ROOT = Path("/home/workspace")
RESPONSE_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_responses"
REQUEST_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_requests"
PROCESSED_RESPONSES = RESPONSE_QUEUE / "processed"
PROCESSED_REQUESTS = REQUEST_QUEUE / "processed"
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
MEETING_INBOX = WORKSPACE_ROOT / "Personal/Meetings/Inbox"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def scan_responses():
    """Find all unprocessed responses."""
    if not RESPONSE_QUEUE.exists():
        return []
    
    responses = []
    for resp_file in RESPONSE_QUEUE.glob("*.json"):
        if resp_file.is_file():
            try:
                data = json.loads(resp_file.read_text())
                responses.append((resp_file, data))
            except Exception as e:
                logger.error(f"Error reading {resp_file.name}: {e}")
    
    return responses


def update_meeting_status(meeting_id, status, completed_at=None, notes=None):
    """Update meeting status in database."""
    conn = sqlite3.connect(PIPELINE_DB)
    
    if completed_at:
        conn.execute("""
            UPDATE meetings
            SET status = ?, completed_at = ?, notes = ?
            WHERE meeting_id = ?
        """, (status, completed_at, notes, meeting_id))
    else:
        conn.execute("""
            UPDATE meetings
            SET status = ?, notes = ?
            WHERE meeting_id = ?
        """, (status, notes, meeting_id))
    
    conn.commit()
    conn.close()


def register_blocks(meeting_id, blocks_data):
    """Register generated blocks in database."""
    conn = sqlite3.connect(PIPELINE_DB)
    
    for block in blocks_data:
        block_id = f"{meeting_id}_{block['block_type']}"
        
        conn.execute("""
            INSERT OR REPLACE INTO blocks 
            (block_id, meeting_id, block_type, file_path, status, generated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            block_id,
            meeting_id,
            block['block_type'],
            block.get('file_path', ''),
            block.get('status', 'complete'),
            datetime.now(timezone.utc).isoformat()
        ))
    
    conn.commit()
    conn.close()


def mark_transcript_processed(meeting_id):
    """Mark transcript file as processed."""
    for transcript_path in MEETING_INBOX.glob(f"{meeting_id}.transcript.md"):
        if not transcript_path.name.startswith("[IMPORTED-TO-ZO]"):
            new_name = f"[IMPORTED-TO-ZO] {transcript_path.name}"
            new_path = transcript_path.parent / new_name
            transcript_path.rename(new_path)
            logger.info(f"  ✓ Marked transcript: {new_name}")
            return True
    return False


def finalize_meeting(meeting_id, response_data):
    """Finalize meeting by updating status and renaming folder."""
    conn = sqlite3.connect(PIPELINE_DB)
    
    # Update database
    completed_at = response_data.get("completed_at", datetime.now(timezone.utc).isoformat())
    summary = response_data.get("outputs", {}).get("summary", "")
    update_meeting_status(meeting_id, "complete", completed_at, summary)
    
    conn.commit()
    conn.close()
    
    # Rename folder with 👍
    rename_to_complete(meeting_id)
    
    logger.info(f"  ✓ Meeting finalized: {meeting_id}")
    return True


def main():
    logger.info("AI Response Handler")
    
    responses = scan_responses()
    
    if not responses:
        logger.info("No responses to process")
        return 0
    
    logger.info(f"Found {len(responses)} response(s)")
    
    PROCESSED_RESPONSES.mkdir(parents=True, exist_ok=True)
    PROCESSED_REQUESTS.mkdir(parents=True, exist_ok=True)
    
    for resp_file, response_data in responses:
        request_id = response_data["request_id"]
        status = response_data["status"]
        
        logger.info(f"Processing response: {request_id}")
        logger.info(f"  Status: {status}")
        
        # Extract meeting_id from request_id (format: meeting_{meeting_id}_{timestamp})
        if not request_id.startswith("meeting_"):
            logger.warning(f"  ⚠ Unknown request format: {request_id}")
            continue
        
        parts = request_id.split("_")
        if len(parts) < 3:
            logger.warning(f"  ⚠ Cannot parse meeting_id from: {request_id}")
            continue
        
        # meeting_id is everything between "meeting_" and the timestamp
        meeting_id = "_".join(parts[1:-1])
        
        if status == "success":
            # Register blocks
            if "outputs" in response_data and "blocks" in response_data["outputs"]:
                blocks = response_data["outputs"]["blocks"]
                logger.info(f"  Registering {len(blocks)} blocks")
                register_blocks(meeting_id, blocks)
            
            # Update meeting status
            completed_at = response_data.get("completed_at", datetime.now(timezone.utc).isoformat())
            summary = response_data.get("outputs", {}).get("summary", "")
            update_meeting_status(meeting_id, "complete", completed_at, summary)
            
            # Mark transcript as processed
            mark_transcript_processed(meeting_id)
            
            logger.info(f"  ✓ Meeting complete: {meeting_id}")
        
        elif status == "failed":
            error = response_data.get("error", "Unknown error")
            logger.error(f"  ✗ Processing failed: {error}")
            update_meeting_status(meeting_id, "failed", notes=f"AI processing failed: {error}")
        
        # Move response to processed
        processed_resp_file = PROCESSED_RESPONSES / resp_file.name
        resp_file.rename(processed_resp_file)
        
        # Move corresponding request to processed
        req_file = REQUEST_QUEUE / f"{request_id}.json"
        if req_file.exists():
            processed_req_file = PROCESSED_REQUESTS / req_file.name
            req_file.rename(processed_req_file)
    
    logger.info(f"✓ Processed {len(responses)} response(s)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
