#!/usr/bin/env python3
"""
Human Escalation Notifier - Core notification logic
Created for D3.2 Drop: zoputer-autonomy-v2
"""

import sys
import json
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Add N5 scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')
from pending_decisions import get_decision, init_db

# Notification state database
NOTIFICATION_DB = "/home/workspace/N5/data/notifications.db"

def init_notifications_db():
    """Initialize notifications tracking database."""
    Path(NOTIFICATION_DB).parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(NOTIFICATION_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notification_log (
                decision_id TEXT,
                notification_type TEXT, -- 'initial' or 'reminder'
                sent_at TEXT,
                message_preview TEXT,
                hours_remaining INTEGER,
                PRIMARY KEY (decision_id, notification_type, sent_at)
            )
        """)
        conn.commit()

def get_short_id(decision_id: str) -> str:
    """Generate a 4-character short ID for SMS replies."""
    return decision_id[:4].lower()

def format_sms_notification(decision: dict, is_reminder: bool = False) -> str:
    """Format decision into SMS-friendly message."""
    priority = decision['priority']
    summary = decision['summary']
    short_id = get_short_id(decision['id'])
    
    # Prefix for reminders
    prefix = "🔔 Reminder" if is_reminder else "🔔 Decision needed"
    
    # Build message components
    first_line = f"{prefix} ({priority})"
    
    # Ensure summary fits in remaining space
    # Target: ~150 chars total (SMS limit 160, leave buffer)
    reply_line = f"Reply: n5 decision {short_id}"
    available_chars = 150 - len(first_line) - len(reply_line) - 4  # 4 for newlines/spacing
    
    if len(summary) > available_chars:
        summary = summary[:available_chars - 3] + "..."
    
    message = f"{first_line}\n{summary}\n\n{reply_line}"
    
    return message

def has_notification_been_sent(decision_id: str, notification_type: str) -> bool:
    """Check if notification has already been sent."""
    init_notifications_db()
    
    with sqlite3.connect(NOTIFICATION_DB) as conn:
        cursor = conn.execute("""
            SELECT COUNT(*) FROM notification_log 
            WHERE decision_id = ? AND notification_type = ?
        """, (decision_id, notification_type))
        
        return cursor.fetchone()[0] > 0

def log_notification(decision_id: str, notification_type: str, message: str, hours_remaining: int = None):
    """Log that a notification was sent."""
    init_notifications_db()
    
    with sqlite3.connect(NOTIFICATION_DB) as conn:
        conn.execute("""
            INSERT INTO notification_log 
            (decision_id, notification_type, sent_at, message_preview, hours_remaining)
            VALUES (?, ?, ?, ?, ?)
        """, (
            decision_id, 
            notification_type,
            datetime.utcnow().isoformat() + "Z",
            message[:50] + "..." if len(message) > 50 else message,
            hours_remaining
        ))
        conn.commit()

def send_notification(message: str) -> bool:
    """Send SMS notification via Zo's send_sms_to_user capability."""
    # Import here to avoid import issues in non-Zo environments
    try:
        # This is a simulation - in actual Zo environment, this would call the tool
        # For now, we'll just print to stdout with a marker that the orchestrator can detect
        print(f"SMS_NOTIFICATION:{message}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def notify_human(decision_id: str, immediate: bool = False, is_reminder: bool = False) -> bool:
    """
    Send SMS notification to V about a pending decision.
    
    Args:
        decision_id: The pending decision to notify about
        immediate: Skip any batching, send now
        is_reminder: Whether this is a reminder notification
    
    Returns:
        True if SMS sent successfully
    """
    # Get decision data
    decision = get_decision(decision_id)
    if not decision:
        print(f"Error: Decision {decision_id} not found")
        return False
    
    # Check if already notified (unless immediate flag set)
    if not immediate:
        notification_type = "reminder" if is_reminder else "initial"
        if has_notification_been_sent(decision_id, notification_type):
            print(f"Notification type '{notification_type}' already sent for {decision_id}")
            return True
    
    # Format message
    message = format_sms_notification(decision, is_reminder)
    
    # Send notification
    success = send_notification(message)
    
    if success:
        notification_type = "reminder" if is_reminder else "initial"
        log_notification(decision_id, notification_type, message)
        print(f"✓ SMS notification sent for decision {decision_id}")
    else:
        print(f"✗ Failed to send SMS for decision {decision_id}")
    
    return success

def main():
    """CLI interface for human escalation notifications."""
    parser = argparse.ArgumentParser(description="Send SMS notifications for pending decisions")
    parser.add_argument("decision_id", help="Decision ID to notify about")
    parser.add_argument("--immediate", action="store_true", help="Send immediately, skip duplicate checks")
    parser.add_argument("--reminder", action="store_true", help="Mark as reminder notification")
    parser.add_argument("--test", action="store_true", help="Test format without sending")
    
    args = parser.parse_args()
    
    # Initialize databases
    init_db()
    init_notifications_db()
    
    if args.test:
        # Test mode - just show the formatted message
        decision = get_decision(args.decision_id)
        if not decision:
            print(f"Error: Decision {args.decision_id} not found")
            return
        
        message = format_sms_notification(decision, args.reminder)
        print("Test message format:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        print(f"Length: {len(message)} chars")
        return
    
    # Send notification
    success = notify_human(args.decision_id, args.immediate, args.reminder)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()