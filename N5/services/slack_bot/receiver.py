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
from typing import Optional

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


def is_user_authorized(user_id: str) -> bool:
    """Check if user is on the whitelist."""
    authorized = user_id in config.get("authorized_users", [])
    
    if config.get("audit_log", True):
        status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
        logger.info(f"Auth check: {user_id} -> {status}")
    
    return authorized


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
        # Use real Zo AI integration
        response = ask_zo(message, user_id, context)
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
        
        # Ignore bot messages
        if event.get("bot_id"):
            return Response(status_code=200)
        
        logger.info(f"Event: {event_type} from user {user_id}")
        
        # Check authorization
        if not is_user_authorized(user_id):
            logger.warning(f"Unauthorized access attempt by {user_id}")
            # Silently ignore (don't even acknowledge)
            return Response(status_code=200)
        
        # Check rate limit
        if not check_rate_limit(user_id):
            await send_slack_message(
                event.get("channel"),
                "⚠️ Rate limit exceeded. Please wait a moment before sending more messages.",
                event.get("thread_ts") or event.get("ts")
            )
            return Response(status_code=200)
        
        # Handle app mentions
        if event_type == "app_mention":
            message = event.get("text", "")
            # Remove bot mention from message
            message = message.split(">", 1)[-1].strip()
            
            # If message is empty after removing mention, provide helpful prompt
            if not message:
                message = "Hello! How can I help you?"
            
            channel = event.get("channel")
            thread_ts = event.get("thread_ts") or event.get("ts")
            
            logger.info(f"Processing mention: '{message}' in {channel}")
            
            # Forward to conversation API
            context = {
                "channel": channel,
                "thread_ts": thread_ts,
                "event_type": "mention"
            }
            response = await forward_to_conversation_api(message, user_id, context)
            
            # Send response
            logger.info(f"Sending response to channel {channel}")
            await send_slack_message(channel, response, thread_ts)
            logger.info("Response sent successfully")
        
        # Handle direct messages
        elif event_type == "message" and event.get("channel_type") == "im":
            message = event.get("text", "")
            channel = event.get("channel")
            thread_ts = event.get("ts")  # Get message timestamp for threading
            
            logger.info(f"Processing DM: '{message}'")
            
            # Forward to conversation API
            context = {
                "channel": channel,
                "event_type": "dm"
            }
            response = await forward_to_conversation_api(message, user_id, context)
            
            # Send response
            logger.info(f"Sending response to channel {channel}")
            await send_slack_message(channel, response, thread_ts)  # Pass thread_ts
            logger.info("Response sent successfully")
    
    return Response(status_code=200)


@app.post("/admin/reload")
async def reload_config():
    """Reload configuration (for adding users to whitelist)."""
    load_config()
    return {"status": "reloaded", "authorized_users": len(config.get("authorized_users", []))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8775, log_level="info")









