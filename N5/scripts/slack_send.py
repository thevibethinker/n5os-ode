#!/usr/bin/env python3
"""Send messages to Slack channels via N5 OS."""
import argparse
import json
import logging
import sys
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
    # If it starts with C, assume it's an ID
    if channel_input.startswith("C"):
        return channel_input
    
    # Remove # prefix if present
    channel_name = channel_input.lstrip("#")
    
    # Look up in map
    if channel_name in channels_map:
        return channels_map[channel_name]
    
    logger.error(f"Channel not found: {channel_input}")
    logger.info(f"Available channels: {', '.join(sorted(channels_map.keys()))}")
    sys.exit(1)

def send_message(channel_id: str, text: str, thread_ts: str = None, client: WebClient = None) -> dict:
    """Send a message to a Slack channel."""
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        return response
    except SlackApiError as e:
        # Try to join channel if not a member
        if e.response['error'] == 'not_in_channel':
            try:
                logger.info("Not in channel, attempting to join...")
                client.conversations_join(channel=channel_id)
                logger.info("✓ Joined channel successfully")
                # Retry sending message
                response = client.chat_postMessage(
                    channel=channel_id,
                    text=text,
                    thread_ts=thread_ts
                )
                return response
            except SlackApiError as join_error:
                if join_error.response['error'] == 'method_not_supported_for_channel_type':
                    logger.error("Cannot auto-join private channel. Please invite the bot manually:")
                    logger.error(f"  Go to the channel and type: /invite @n5_os_bot_v2")
                else:
                    logger.error(f"Failed to join channel: {join_error.response['error']}")
                sys.exit(1)
        else:
            logger.error(f"Slack API error: {e.response['error']}")
            sys.exit(1)

def send_file(channel_id: str, file_path: str, comment: str = None, client: WebClient = None) -> dict:
    """Upload a file to a Slack channel."""
    try:
        response = client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            initial_comment=comment
        )
        return response
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        sys.exit(1)

def main(channel: str, message: str = None, file: str = None, thread: str = None) -> int:
    """Main entry point."""
    try:
        # Load config
        creds = load_credentials()
        channels_map = load_channels()
        client = WebClient(token=creds["bot_token"])
        
        # Resolve channel
        channel_id = resolve_channel(channel, channels_map)
        
        # Send file if provided
        if file:
            file_path = Path(file)
            if not file_path.exists():
                logger.error(f"File not found: {file}")
                return 1
            
            logger.info(f"Uploading file to #{channel}...")
            response = send_file(channel_id, str(file_path), comment=message, client=client)
            logger.info(f"✓ File uploaded: {response['file']['permalink']}")
            return 0
        
        # Send message
        if not message:
            logger.error("No message or file provided")
            return 1
        
        logger.info(f"Sending message to #{channel}...")
        response = send_message(channel_id, message, thread_ts=thread, client=client)
        logger.info(f"✓ Message sent: {response['ts']}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send messages to Slack channels")
    parser.add_argument("channel", help="Channel name (e.g., 'general' or '#general') or ID")
    parser.add_argument("-m", "--message", help="Message text")
    parser.add_argument("-f", "--file", help="File path to upload")
    parser.add_argument("-t", "--thread", help="Thread timestamp to reply to")
    
    args = parser.parse_args()
    
    if not args.message and not args.file:
        parser.error("Either --message or --file must be provided")
    
    sys.exit(main(args.channel, args.message, args.file, args.thread))
