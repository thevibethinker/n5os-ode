#!/usr/bin/env python3
"""
Close Conversation Bridge - Allows external tools (Claude Code) to trigger N5 conversation close.

This is a lightweight bridge that:
1. Creates a session record for the external tool session
2. Triggers the appropriate conversation-end workflow via Zo API
3. Returns confirmation

Usage:
    python3 close_convo_bridge.py --summary "Built feature X, refactored Y"
    python3 close_convo_bridge.py --summary "..." --tier 2
    python3 close_convo_bridge.py --summary "..." --source claude-code --session-id abc123
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
N5_DATA = WORKSPACE / "N5" / "data"
CONVERSATIONS_DB = N5_DATA / "conversations.db"

def generate_session_id(source: str) -> str:
    """Generate a unique session ID for external tool sessions."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{source}_{timestamp}"

def log_external_session(
    session_id: str,
    source: str,
    summary: str,
    tier: int
) -> bool:
    """Log the external session to conversations.db for tracking."""
    try:
        conn = sqlite3.connect(CONVERSATIONS_DB)
        cursor = conn.cursor()
        
        # Check if external_sessions table exists, create if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_sessions (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                summary TEXT,
                tier INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                closed_at TEXT
            )
        """)
        
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO external_sessions (id, source, summary, tier, created_at, closed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, source, summary, tier, now, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Logged external session: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to log session: {e}")
        return False

def trigger_zo_close(summary: str, tier: int) -> dict:
    """
    Trigger Zo to run the conversation close workflow.
    Uses the /zo/ask API if available, otherwise falls back to local script.
    """
    zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    if zo_token:
        # Use Zo API to trigger close
        import requests
        
        prompt = f"""You are being triggered by Claude Code to close an external coding session.

Session Summary: {summary}
Requested Tier: {tier}

Please:
1. Log this as an external session close
2. Extract any key decisions or artifacts mentioned in the summary
3. Return a brief confirmation of what was recorded

Do NOT run the full conversation-end workflow - this is a lightweight external session log."""

        try:
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": zo_token,
                    "content-type": "application/json"
                },
                json={"input": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "response": result.get("output", "Logged")}
            else:
                logger.warning(f"Zo API returned {response.status_code}, falling back to local")
        except Exception as e:
            logger.warning(f"Zo API unavailable: {e}, falling back to local")
    
    # Fallback: just log locally without full Zo workflow
    return {"success": True, "response": "Session logged locally (Zo API unavailable)"}

def spawn_zo_close_background(summary: str, tier: int, session_id: str) -> None:
    """Spawn Zo API call in background process (fire-and-forget).

    WS3 optimization: Don't block MCP bridge on Zo API response.
    """
    # Create a background script that handles the Zo API call
    script = f'''
import os
import requests
import json

zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
if zo_token:
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={{"authorization": zo_token, "content-type": "application/json"}},
            json={{"input": "External session closed. Session: {session_id}, Summary: {summary[:200]}"}},
            timeout=30
        )
    except:
        pass  # Fire and forget - errors are acceptable
'''
    # Spawn detached process that will run independently
    subprocess.Popen(
        ["python3", "-c", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True  # Detach from parent process
    )


def main():
    parser = argparse.ArgumentParser(description="Bridge for external tools to trigger N5 conversation close")
    parser.add_argument("--summary", required=True, help="Summary of work completed")
    parser.add_argument("--tier", type=int, default=1, choices=[1, 2, 3], help="Close tier (1=quick, 2=standard, 3=full)")
    parser.add_argument("--source", default="claude-code", help="Source tool identifier")
    parser.add_argument("--session-id", help="Optional session ID (auto-generated if not provided)")
    parser.add_argument("--async", dest="async_mode", action="store_true",
                       help="Run Zo API call in background (non-blocking)")

    args = parser.parse_args()

    # Generate or use provided session ID
    session_id = args.session_id or generate_session_id(args.source)

    # Log the session (always synchronous - fast local operation)
    logged = log_external_session(
        session_id=session_id,
        source=args.source,
        summary=args.summary,
        tier=args.tier
    )

    if not logged:
        print(json.dumps({"success": False, "error": "Failed to log session"}))
        sys.exit(1)

    # Handle Zo API call based on mode
    if args.async_mode:
        # WS3 optimization: Fire-and-forget Zo API call
        spawn_zo_close_background(args.summary, args.tier, session_id)
        output = {
            "success": True,
            "session_id": session_id,
            "source": args.source,
            "tier": args.tier,
            "message": f"Session closed: {args.summary[:100]}...",
            "zo_response": "Background task spawned (async mode)"
        }
    else:
        # Original synchronous behavior
        result = trigger_zo_close(args.summary, args.tier)
        output = {
            "success": True,
            "session_id": session_id,
            "source": args.source,
            "tier": args.tier,
            "message": f"Session closed: {args.summary[:100]}...",
            "zo_response": result.get("response", "")
        }

    print(json.dumps(output, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())

