#!/usr/bin/env python3
"""Push feedback to the Zo team via Slack with Google Drive context folder.

Respects business hours: messages sent outside 9 AM - 6 PM ET are scheduled
for the next available window.
"""
import argparse
import logging
import sys
import shutil
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# =============================================================================
# CHANNEL CONFIGURATION - Easy to swap between test and production
# =============================================================================
CHANNELS = {
    "production": {
        "id": "C09NDHKEXEJ",      # ext-zo-vrijen
        "name": "ext-zo-vrijen"
    },
    "test": {
        "id": "C085K7QE17C",       # vrijen-slack-backend
        "name": "vrijen-slack-backend"
    }
}

# Default to test channel for safety - change to "production" when ready
DEFAULT_CHANNEL = "production"

# =============================================================================
# BUSINESS HOURS CONFIGURATION
# =============================================================================
TIMEZONE = ZoneInfo("America/New_York")
BUSINESS_HOURS_START = time(9, 0)   # 9:00 AM ET
BUSINESS_HOURS_END = time(18, 0)    # 6:00 PM ET
BUSINESS_DAYS = {0, 1, 2, 3, 4}     # Monday=0 through Friday=4

# =============================================================================
# GOOGLE DRIVE CONFIGURATION
# =============================================================================
ZO_FEEDBACK_FOLDER_ID = "1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl"
ZO_FEEDBACK_FOLDER_NAME = "Zo Feedback"
DRIVE_EMAIL = "vrijen@mycareerspan.com"

# =============================================================================
# SUPPORTED FILE TYPES
# =============================================================================
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
SUPPORTED_VIDEOS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
SUPPORTED_FILES = SUPPORTED_IMAGES | SUPPORTED_VIDEOS


def get_next_business_time() -> tuple[datetime, bool]:
    """
    Get the next valid time to send a message.
    
    Returns:
        tuple: (datetime to send, is_immediate: bool)
        - If within business hours, returns (now, True)
        - If outside business hours, returns (next valid time, False)
    """
    now = datetime.now(TIMEZONE)
    current_time = now.time()
    current_weekday = now.weekday()
    
    # Check if we're in business hours
    in_business_hours = (
        current_weekday in BUSINESS_DAYS and
        BUSINESS_HOURS_START <= current_time < BUSINESS_HOURS_END
    )
    
    if in_business_hours:
        return now, True
    
    # Calculate next business hours start
    if current_weekday in BUSINESS_DAYS and current_time < BUSINESS_HOURS_START:
        # Today, but before business hours - schedule for 9 AM today
        next_time = now.replace(
            hour=BUSINESS_HOURS_START.hour,
            minute=BUSINESS_HOURS_START.minute,
            second=0,
            microsecond=0
        )
    else:
        # After hours or weekend - find next business day
        days_ahead = 1
        next_day = (current_weekday + days_ahead) % 7
        
        while next_day not in BUSINESS_DAYS:
            days_ahead += 1
            next_day = (current_weekday + days_ahead) % 7
        
        next_date = now + timedelta(days=days_ahead)
        next_time = next_date.replace(
            hour=BUSINESS_HOURS_START.hour,
            minute=BUSINESS_HOURS_START.minute,
            second=0,
            microsecond=0
        )
    
    return next_time, False


def load_slack_client() -> WebClient:
    token = get_secret("SLACK_N5_BOT_SECRET", required=False)
    if not token:
        token = get_secret("SLACK_BOT_TOKEN")
    return WebClient(token=token)


def format_slack_bluf(bluf: str, category: str = None, priority: str = None, folder_url: str = None) -> str:
    """Format BLUF-only Slack message with link to Drive folder."""
    cat_emoji = {
        "bug": ":bug:",
        "feature": ":bulb:",
        "ux": ":art:",
        "question": ":question:",
        "praise": ":star:",
    }.get(category.lower() if category else "", ":speech_balloon:")
    
    priority_indicator = ""
    if priority:
        priority_emoji = {"high": ":rotating_light:", "medium": ":warning:", "low": ":information_source:"}.get(priority.lower(), "")
        if priority_emoji:
            priority_indicator = f" {priority_emoji}"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    
    result = f"{cat_emoji}{priority_indicator} *Zo Feedback*\n\n{bluf}"
    
    if folder_url:
        result += f"\n\n:file_folder: <{folder_url}|View details & attachments>"
    
    result += f"\n\n_Sent from Zo Computer • {timestamp}_"
    return result


def generate_context_markdown(bluf: str, context: str = None, category: str = None, priority: str = None, files: list = None) -> str:
    """Generate full context markdown for Drive folder."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    md = f"""---
created: {date_str}
last_edited: {date_str}
version: 1.0
type: zo-feedback
category: {category or 'general'}
priority: {priority or 'normal'}
---

# Zo Feedback

**Submitted:** {timestamp}  
**Category:** {category.title() if category else 'General'}  
**Priority:** {priority.upper() if priority else 'Normal'}

---

## BLUF (Bottom Line Up Front)

{bluf}

"""
    
    if context:
        md += f"""## Full Context

{context}

"""
    
    if files:
        md += """## Attachments

"""
        for f in files:
            fname = Path(f).name
            ext = Path(f).suffix.lower()
            if ext in SUPPORTED_IMAGES:
                md += f"![{fname}](./{fname})\n\n"
            elif ext in SUPPORTED_VIDEOS:
                md += f"- 🎬 [{fname}](./{fname})\n"
            else:
                md += f"- 📎 [{fname}](./{fname})\n"
    
    md += """
---

*Generated by N5 zo-feedback command*
"""
    return md


def validate_files(file_paths: list) -> tuple[list[Path], list[str]]:
    """Validate files exist and are supported types."""
    valid = []
    errors = []
    
    for fp in file_paths:
        path = Path(fp)
        if not path.exists():
            errors.append(f"File not found: {fp}")
            continue
        if path.suffix.lower() not in SUPPORTED_FILES:
            errors.append(f"Unsupported file type: {fp}")
            continue
        valid.append(path)
    
    return valid, errors


def send_slack_message(client: WebClient, channel_id: str, text: str, 
                       force_immediate: bool = False) -> dict:
    """
    Send or schedule a Slack message respecting business hours.
    
    Args:
        client: Slack WebClient
        channel_id: Channel to send to
        text: Message text
        force_immediate: If True, send immediately regardless of time
        
    Returns:
        dict with 'ts', 'scheduled', and 'scheduled_time' keys
    """
    send_time, is_immediate = get_next_business_time()
    
    if is_immediate or force_immediate:
        # Send immediately
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            mrkdwn=True
        )
        return {
            "ts": response["ts"],
            "scheduled": False,
            "scheduled_time": None
        }
    else:
        # Schedule for next business hours
        post_at = int(send_time.timestamp())
        response = client.chat_scheduleMessage(
            channel=channel_id,
            text=text,
            post_at=post_at
        )
        return {
            "ts": response["scheduled_message_id"],
            "scheduled": True,
            "scheduled_time": send_time.strftime("%Y-%m-%d %H:%M ET")
        }


def send_feedback(bluf: str, context: str = None, attachments: list = None, 
                  category: str = None, priority: str = None, 
                  test: bool = False, force_immediate: bool = False) -> int:
    """
    Send feedback to Slack with Drive folder for full context.
    
    Args:
        bluf: Short summary (goes in Slack message)
        context: Full context/details (goes in Drive markdown)
        attachments: List of file paths (uploaded to Drive)
        category: bug, feature, ux, question, praise
        priority: high, medium, low
        test: If True, send to test channel instead of production
        force_immediate: If True, send immediately (ignore business hours)
    """
    try:
        # Select channel
        channel_key = "test" if test else DEFAULT_CHANNEL
        channel = CHANNELS[channel_key]
        channel_id = channel["id"]
        channel_name = channel["name"]
        
        # Validate attachments
        valid_files = []
        if attachments:
            valid_files, errors = validate_files(attachments)
            for err in errors:
                logger.error(err)
        
        # If we have context or attachments, create Drive folder
        if context or valid_files:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            
            # Prepare files for staging
            staging_dir = Path("/tmp/zo_feedback_staging")
            staging_dir.mkdir(exist_ok=True)
            
            # Clean previous staging
            for f in staging_dir.iterdir():
                f.unlink()
            
            # Generate context markdown
            md_content = generate_context_markdown(bluf, context, category, priority, 
                                                    [f.name for f in valid_files])
            md_path = staging_dir / "feedback.md"
            md_path.write_text(md_content)
            logger.info(f"Created: feedback.md")
            
            # Copy media files to staging
            staged_files = [md_path]
            for f in valid_files:
                dest = staging_dir / f.name
                shutil.copy2(f, dest)
                staged_files.append(dest)
                logger.info(f"Staged: {f.name}")
            
            # Calculate send time for manifest
            send_time, is_immediate = get_next_business_time()
            
            # Create manifest for Zo to process
            manifest = {
                "action": "upload_folder_to_drive",
                "parent_folder_id": ZO_FEEDBACK_FOLDER_ID,
                "parent_folder_name": ZO_FEEDBACK_FOLDER_NAME,
                "subfolder_name": f"feedback_{timestamp}",
                "staging_dir": str(staging_dir),
                "files": [str(f) for f in staged_files],
                "slack": {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "bluf": bluf,
                    "category": category,
                    "priority": priority,
                    "force_immediate": force_immediate,
                    "scheduled_time": None if (is_immediate or force_immediate) else send_time.strftime("%Y-%m-%d %H:%M ET")
                }
            }
            
            manifest_path = Path("/tmp/zo_feedback_manifest.json")
            manifest_path.write_text(json.dumps(manifest, indent=2))
            
            logger.info(f"Manifest written to {manifest_path}")
            if manifest["slack"]["scheduled_time"]:
                logger.info(f"Will be scheduled for: {manifest['slack']['scheduled_time']}")
            logger.info(f"Ready for Drive upload → #{channel_name}")
            
            # Signal Zo to complete the workflow
            print(f"\n__ZO_FEEDBACK_READY__:{manifest_path}")
            return 0
        
        else:
            # Simple text-only feedback - send directly to Slack
            client = load_slack_client()
            formatted = format_slack_bluf(bluf, category, priority)
            
            logger.info(f"Sending to #{channel_name}...")
            result = send_slack_message(client, channel_id, formatted, force_immediate)
            
            if result["scheduled"]:
                logger.info(f"✓ Scheduled for {result['scheduled_time']}: {result['ts']}")
            else:
                logger.info(f"✓ Sent immediately: {result['ts']}")
            return 0
        
    except SlackApiError as e:
        logger.error(f"Slack error: {e.response['error']}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Send feedback to the Zo team",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick feedback (text only, direct to Slack)
  zo-feedback -m "Image gen is blazing fast!" -c praise
  
  # Bug report with screenshot
  zo-feedback -m "Button broken on mobile" -x "Tried on iPhone 14, Safari." -a screenshot.png -c bug -p high
  
  # Feature request with context
  zo-feedback -m "Add dark mode" -x "Would help with late night usage." -a mockup.png -c feature
  
  # Test mode (sends to vrijen-slack-backend)
  zo-feedback -m "Testing" --test
  
  # Force immediate send (bypass business hours check)
  zo-feedback -m "Urgent bug" -c bug -p high --now
  
Categories: bug, feature, ux, question, praise
Priorities: high, medium, low

Business hours: 9 AM - 6 PM ET, Monday-Friday
Messages outside business hours are automatically scheduled.

Output structure:
- Slack: BLUF + link to Drive folder
- Drive: feedback.md (full context) + media files
        """
    )
    parser.add_argument("-m", "--message", required=True, 
                        help="BLUF - short summary (appears in Slack)")
    parser.add_argument("-x", "--context", 
                        help="Full context/details (saved to Drive markdown)")
    parser.add_argument("-a", "--attachments", nargs="+", metavar="FILE",
                        help="Files to attach (images or videos)")
    parser.add_argument("-s", "--screenshot", 
                        help="(Legacy) Path to screenshot file")
    parser.add_argument("-c", "--category", 
                        choices=["bug", "feature", "ux", "question", "praise"],
                        help="Feedback category")
    parser.add_argument("-p", "--priority", 
                        choices=["high", "medium", "low"],
                        help="Priority level")
    parser.add_argument("--test", action="store_true",
                        help="Send to test channel (vrijen-slack-backend)")
    parser.add_argument("--now", action="store_true",
                        help="Force immediate send (bypass business hours)")
    
    args = parser.parse_args()
    
    # Combine legacy -s with -a
    attachments = args.attachments or []
    if args.screenshot:
        attachments.append(args.screenshot)
    
    sys.exit(send_feedback(
        bluf=args.message,
        context=args.context,
        attachments=attachments or None,
        category=args.category,
        priority=args.priority,
        test=args.test,
        force_immediate=args.now
    ))


if __name__ == "__main__":
    main()



