#!/usr/bin/env python3
"""
SMS Notification Helper
Sends SMS notifications via Zo Computer's SMS API

Usage:
    python3 send_sms_notification.py "Your message here"
    
Version: 1.0.0
Date: 2025-10-13
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def send_sms_via_zo(message: str) -> bool:
    """
    Send SMS notification via Zo Computer's notification system.
    
    This writes a notification request that will be picked up by Zo's
    scheduling/notification system.
    
    Args:
        message: SMS message content
        
    Returns:
        bool: True if notification queued successfully
    """
    notification_queue = Path("/home/workspace/N5/inbox/notifications")
    notification_queue.mkdir(parents=True, exist_ok=True)
    
    # Create notification payload
    notification = {
        "type": "sms",
        "message": message,
        "timestamp": "now",
        "priority": "normal"
    }
    
    # Write to notification queue
    try:
        import time
        timestamp = int(time.time())
        notification_file = notification_queue / f"sms_{timestamp}.json"
        notification_file.write_text(json.dumps(notification, indent=2))
        logger.info(f"✓ SMS notification queued: {notification_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue SMS notification: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Send SMS notification via Zo Computer"
    )
    parser.add_argument(
        "message",
        help="SMS message content"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview message without sending"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print(f"[DRY RUN] Would send SMS:")
        print(f"---")
        print(args.message)
        print(f"---")
        return 0
    
    success = send_sms_via_zo(args.message)
    
    if success:
        logger.info("✓ SMS notification sent successfully")
        return 0
    else:
        logger.error("❌ Failed to send SMS notification")
        return 1


if __name__ == "__main__":
    sys.exit(main())
