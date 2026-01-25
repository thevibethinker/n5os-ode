#!/usr/bin/env python3
"""
Send Bot - Ad-hoc bot dispatch to any meeting URL

Usage:
    python3 send_bot.py <meeting_url> [--name "Bot Name"]
    python3 send_bot.py https://meet.google.com/abc-def-ghi
    python3 send_bot.py https://zoom.us/j/123456789 --name "My Recorder"

This creates a bot that joins immediately (or within ~1 minute).
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Import config and client
try:
    from .recall_client import RecallClient
    from .config import DEFAULT_BOT_CONFIG
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from recall_client import RecallClient
    from config import DEFAULT_BOT_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def send_bot(meeting_url: str, bot_name: str = None) -> dict:
    """
    Send a bot to join a meeting immediately
    
    Args:
        meeting_url: Video conference URL (Zoom, Meet, Teams, etc.)
        bot_name: Optional custom name for the bot
    
    Returns:
        Bot creation response with id, status, etc.
    """
    client = RecallClient()
    
    # Use default bot name if not specified
    name = bot_name or DEFAULT_BOT_CONFIG.get("bot_name", "Jared Dunn, Chief of Staff (AI Notetaker)")
    
    logger.info(f"Sending bot '{name}' to {meeting_url}")
    
    # Create bot without join_at = immediate join
    result = client.create_bot(
        meeting_url=meeting_url,
        bot_name=name,
        join_at=None,  # No join_at = join immediately
    )
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Send a Recall bot to any meeting URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 send_bot.py https://meet.google.com/abc-def-ghi
    python3 send_bot.py https://zoom.us/j/123456789 --name "Project Recorder"
    python3 send_bot.py "https://teams.microsoft.com/l/meetup-join/..." 
        """
    )
    parser.add_argument("meeting_url", help="Video conference URL to join")
    parser.add_argument("--name", "-n", help="Custom bot name (optional)")
    parser.add_argument("--json", "-j", action="store_true", help="Output full JSON response")
    
    args = parser.parse_args()
    
    try:
        result = send_bot(args.meeting_url, args.name)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            bot_id = result.get("id")
            bot_name = result.get("bot_name")
            meeting_info = result.get("meeting_url", {})
            platform = meeting_info.get("platform", "unknown") if isinstance(meeting_info, dict) else "unknown"
            
            print(f"\n✓ Bot dispatched!")
            print(f"  ID: {bot_id}")
            print(f"  Name: {bot_name}")
            print(f"  Platform: {platform}")
            print(f"\nThe bot will join the meeting shortly.")
            print(f"Track status: python3 recall_client.py get-bot {bot_id}")
            
    except Exception as e:
        logger.error(f"Failed to send bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
