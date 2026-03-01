#!/usr/bin/env python3
"""
Slack Bot Receiver - Bidirectional Slack ↔ Zo integration
Security: User whitelist with cryptographic signature verification
"""
import asyncio
import hashlib
import hmac
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import aiohttp
from fastapi import FastAPI, Request, Response, HTTPException
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.secrets import get_secret

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Slack Bot Receiver")

# Configuration
CONFIG_PATH = Path("/home/workspace/N5/config/slack_bot_config.json")
CONVERSATION_API_URL = "http://localhost:8769/api/converse/ask"

# Global state
config = {}
slack_client: Optional[AsyncWebClient] = None
rate_limiter = {}  # Simple rate limiting by user
processed_events = set()  # Track recent event IDs to prevent duplicates
MAX_TRACKED_EVENTS = 1000

from zo_ai_caller import ask_zo
from candidate_processor import process_candidate_submission, is_candidate_submission


def load_config():
    """Load bot configuration."""
    global config
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
    else:
        # Default config
        config = {
            "authorized_users": [],  # Will be populated after user adds scope
            "signing_secret": get_secret("SLACK_SIGNING_SECRET"),
            "bot_token": get_secret("SLACK_N5_BOT_SECRET") or get_secret("SLACK_BOT_TOKEN"),
            "rate_limit_messages": 10,
            "rate_limit_window_seconds": 60,
            "audit_log": True
        }
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
    
    logger.info(f"Config loaded. Authorized users: {len(config.get('authorized_users', []))}")


def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Verify request is from Slack using cryptographic signature."""
    signing_secret = config.get("signing_secret", "")
    if not signing_secret:
        logger.error("No signing secret configured!")
        return False
    
    # Prevent replay attacks (timestamp should be recent)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        logger.warning("Request timestamp too old - possible replay attack")
        return False
    
    # Compute expected signature
    sig_basestring = f"v0:{timestamp}:{request_body.decode()}"
    expected_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


def is_user_authorized(user_id: str, channel_id: Optional[str], event_type: str, channel_type: Optional[str]) -> Tuple[bool, str]:
    """Check if user is globally authorized or authorized via scoped channel policy."""
    if user_id in config.get("authorized_users", []):
        return True, "global_whitelist"

    scoped_users: Dict[str, Dict[str, Any]] = config.get("scoped_authorized_users", {})
    user_scope: Dict[str, Any] = scoped_users.get(user_id, {})

    if not user_scope:
        return False, "not_whitelisted"

    allow_dm = bool(user_scope.get("allow_dm", False))
    allowed_channels = set(user_scope.get("channels", []))
    channel_routes = config.get("channel_routes", {})
    allowed_route_keys = set(user_scope.get("route_keys", []))

    if channel_type == "im":
        return (allow_dm, "scoped_dm_allowed" if allow_dm else "scoped_dm_denied")

    if channel_id and channel_id in allowed_channels:
        return True, "scoped_channel_match"

    if channel_id and allowed_route_keys:
        route_key = channel_routes.get(channel_id)
        if route_key and route_key in allowed_route_keys:
            return True, "scoped_route_match"

    return False, "scoped_channel_denied"


def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting: N messages per time window."""
    now = time.time()
    window = config.get("rate_limit_window_seconds", 60)
    limit = config.get("rate_limit_messages", 10)
    
    if user_id not in rate_limiter:
        rate_limiter[user_id] = []
    
    # Clean old entries
    rate_limiter[user_id] = [
        ts for ts in rate_limiter[user_id]
        if now - ts < window
    ]
    
    # Check limit
    if len(rate_limiter[user_id]) >= limit:
        logger.warning(f"Rate limit exceeded for {user_id}")
        return False
    
    rate_limiter[user_id].append(now)
    return True


async def forward_to_conversation_api(message: str, user_id: str, context: dict) -> str:
    """Forward message to Zo (simplified direct integration)."""
    try:
        # ask_zo is synchronous/subprocess-based; run it off the event loop.
        response = await asyncio.to_thread(ask_zo, message, user_id, context)
        logger.info(f"Generated response: {response[:100]}...")
        return response
    except Exception as e:
        logger.error(f"Error forwarding to Zo: {e}")
        return "Sorry, I encountered an error processing your request."


async def send_slack_message(channel: str, text: str, thread_ts: Optional[str] = None):
    """Send message back to Slack."""
    try:
        await slack_client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
    except SlackApiError as e:
        logger.error(f"Error sending Slack message: {e}")


def resolve_reply_target(event: Dict[str, Any]) -> Optional[str]:
    """
    Reply behavior:
    - If mention happened inside a thread, stay in thread.
    - Otherwise reply as top-level (None thread_ts).
    - DMs continue using thread_ts for context continuity.
    """
    if event.get("channel_type") == "im":
        return event.get("ts")
    return event.get("thread_ts")


async def process_event_async(event: Dict[str, Any], user_id: str):
    """Process event in background after immediate Slack ACK."""
    event_type = event.get("type")
    channel = event.get("channel")
    channel_type = event.get("channel_type")
    route_key = config.get("channel_routes", {}).get(channel, "default")

    if event_type == "app_mention":
        message = event.get("text", "")
        message = message.split(">", 1)[-1].strip()

        if not message:
            message = "Hello! How can I help you?"

        reply_thread_ts = resolve_reply_target(event)

        # Candidate submission detection for recruiting channels
        if route_key == "emb_cx_recruiting" and is_candidate_submission(event):
            logger.info(f"[bg] Candidate submission detected from {user_id} in {channel}")
            try:
                response = await process_candidate_submission(
                    event, slack_client, channel, config.get("bot_token", "")
                )
            except Exception as e:
                logger.error(f"[bg] Candidate processing error: {e}", exc_info=True)
                response = f"Error processing candidate submission: {str(e)[:200]}. Please try again or contact V."
            await send_slack_message(channel, response, reply_thread_ts)
            logger.info(f"[bg] Candidate processing response posted to {channel}")
            return

        logger.info(f"[bg] Processing mention from {user_id} in {channel} route={route_key}: '{message}'")

        context = {
            "channel": channel,
            "channel_type": channel_type,
            "thread_ts": event.get("thread_ts") or event.get("ts"),
            "reply_thread_ts": reply_thread_ts,
            "event_type": "mention",
            "route_key": route_key,
            "top_level_reply": reply_thread_ts is None
        }
        response = await forward_to_conversation_api(message, user_id, context)

        await send_slack_message(channel, response, reply_thread_ts)
        logger.info(f"[bg] Response posted to channel={channel} thread_ts={reply_thread_ts}")
        return

    if event_type == "message" and channel_type == "im":
        message = event.get("text", "")
        reply_thread_ts = resolve_reply_target(event)

        logger.info(f"[bg] Processing DM from {user_id}: '{message}'")

        context = {
            "channel": channel,
            "channel_type": channel_type,
            "event_type": "dm",
            "route_key": route_key,
            "reply_thread_ts": reply_thread_ts
        }
        response = await forward_to_conversation_api(message, user_id, context)

        await send_slack_message(channel, response, reply_thread_ts)
        logger.info("[bg] DM response sent")
        return

    logger.info(f"[bg] Ignoring unsupported event type={event_type}")


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    global slack_client
    load_config()
    slack_client = AsyncWebClient(token=config["bot_token"])
    logger.info("Slack Bot Receiver started")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "authorized_users": len(config.get("authorized_users", [])),
        "conversation_api": CONVERSATION_API_URL
    }


@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events."""
    body = await request.body()
    headers = request.headers
    
    # Verify signature
    if not verify_slack_signature(body, headers.get("x-slack-request-timestamp", ""), headers.get("x-slack-signature", "")):
        logger.warning("Invalid Slack signature!")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = json.loads(body)
    
    # Handle URL verification
    if data.get("type") == "url_verification":
        return Response(content=json.dumps({"challenge": data["challenge"]}), media_type="application/json")
    
    # Duplicate event detection
    event = data.get("event", {})
    event_id = event.get("event_ts") or event.get("client_msg_id") or event.get("ts")
    if event_id and event_id in processed_events:
        logger.info(f"Duplicate event detected: {event_id}, skipping")
        return Response(status_code=200)
    
    # Add to processed events (keep size bounded)
    if event_id:
        processed_events.add(event_id)
        if len(processed_events) > MAX_TRACKED_EVENTS:
            # Remove oldest half
            processed_events.clear()
    
    # Handle events
    if data.get("type") == "event_callback":
        event = data.get("event", {})
        event_type = event.get("type")
        user_id = event.get("user")
        channel_id = event.get("channel")
        channel_type = event.get("channel_type")
        
        # Ignore bot messages
        if event.get("bot_id"):
            return Response(status_code=200)
        
        logger.info(f"Event: {event_type} from user {user_id} channel={channel_id}")
        
        # Check authorization
        authorized, reason = is_user_authorized(user_id, channel_id, event_type, channel_type)
        if config.get("audit_log", True):
            status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
            logger.info(f"Auth check: user={user_id} channel={channel_id} type={event_type} -> {status} ({reason})")
        if not authorized:
            logger.warning(f"Unauthorized access attempt by {user_id} ({reason})")
            return Response(status_code=200)
        
        # Check rate limit
        if not check_rate_limit(user_id):
            asyncio.create_task(
                send_slack_message(
                    channel_id,
                    "⚠️ Rate limit exceeded. Please wait a moment before sending more messages.",
                    resolve_reply_target(event)
                )
            )
            return Response(status_code=200)
        
        # Slack requires quick ACK. Process in background.
        asyncio.create_task(process_event_async(event, user_id))
    
    return Response(status_code=200)


@app.post("/admin/reload")
async def reload_config():
    """Reload configuration (for adding users to whitelist)."""
    load_config()
    return {"status": "reloaded", "authorized_users": len(config.get("authorized_users", []))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8775, log_level="info")







