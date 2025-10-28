#!/usr/bin/env python3
"""Read messages from Slack channels via N5 OS."""
import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Add N5 lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def load_credentials():
    """Load Slack credentials from Zo secrets."""
    # Support both naming conventions
    bot_token = get_secret("SLACK_N5_BOT_SECRET", required=False)
    if not bot_token:
        bot_token = get_secret("SLACK_BOT_TOKEN")
    
    return {"bot_token": bot_token}

def load_channels():
    """Load channel mapping from config."""
    channels_path = Path("/home/workspace/N5/config/slack_channels.json")
    if not channels_path.exists():
        logger.error(f"Channels not found: {channels_path}")
        sys.exit(1)
    channels = json.loads(channels_path.read_text())
    return {ch["name"]: ch["id"] for ch in channels}

def resolve_channel(channel_input: str, channels_map: dict) -> str:
    """Resolve channel name or ID to channel ID."""
    if channel_input.startswith("C"):
        return channel_input
    channel_name = channel_input.lstrip("#")
    if channel_name in channels_map:
        return channels_map[channel_name]
    logger.error(f"Channel not found: {channel_input}")
    sys.exit(1)

def fetch_messages(channel_id: str, limit: int = 10, hours: int = None, client: WebClient = None) -> list:
    """Fetch recent messages from a channel."""
    try:
        kwargs = {"channel": channel_id, "limit": limit}
        
        # Add time filter if hours specified
        if hours:
            oldest_time = datetime.now() - timedelta(hours=hours)
            kwargs["oldest"] = oldest_time.timestamp()
        
        response = client.conversations_history(**kwargs)
        return response["messages"]
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        sys.exit(1)

def format_message(msg: dict, client: WebClient = None) -> str:
    """Format a message for display."""
    # Get user info
    user_id = msg.get("user", "Unknown")
    try:
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"] or user_info["user"]["name"]
    except:
        user_name = user_id
    
    # Format timestamp
    ts = float(msg["ts"])
    dt = datetime.fromtimestamp(ts)
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Get text
    text = msg.get("text", "")
    
    return f"[{time_str}] {user_name}: {text}"

def main(channel: str, limit: int = 10, hours: int = None, output: str = None, raw: bool = False) -> int:
    """Main entry point."""
    try:
        # Load config
        creds = load_credentials()
        channels_map = load_channels()
        client = WebClient(token=creds["bot_token"])
        
        # Resolve channel
        channel_id = resolve_channel(channel, channels_map)
        
        # Fetch messages
        logger.info(f"Fetching messages from #{channel}...")
        messages = fetch_messages(channel_id, limit=limit, hours=hours, client=client)
        
        if not messages:
            logger.info("No messages found")
            return 0
        
        # Format output
        if raw:
            result = json.dumps(messages, indent=2)
        else:
            formatted = [format_message(msg, client=client) for msg in reversed(messages)]
            result = "\n".join(formatted)
        
        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(result)
            logger.info(f"✓ Saved {len(messages)} messages to: {output_path}")
        else:
            print("\n" + result)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read messages from Slack channels")
    parser.add_argument("channel", help="Channel name or ID")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of messages (default: 10)")
    parser.add_argument("--hours", type=int, help="Only messages from last N hours")
    parser.add_argument("-o", "--output", help="Save to file instead of printing")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    sys.exit(main(args.channel, args.limit, args.hours, args.output, args.raw))
