#!/usr/bin/env python3
"""
Human Escalation Notifier - SMS notifications for pending decisions
Part of the zoputer-autonomy-v2 build (D3.2)

Sends SMS notifications to V when human decision input is needed.
Integrates with pending_decisions store and uses Zo's SMS capability.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add workspace to path for pending_decisions import
sys.path.insert(0, '/home/workspace/N5/scripts')
from pending_decisions import get_decision, list_pending, get_context_for_sms

# Notification tracking file
NOTIFICATION_LOG_PATH = "/home/workspace/N5/data/notification_log.json"

# Reminder schedule by priority (hours before expiry)
REMINDER_SCHEDULE = {
    'low': [],           # No reminders
    'normal': [],        # Initial only
    'high': [6],         # Reminder at 6 hours before expiry
    'critical': [2, 1]   # Reminders at 2h and 1h before expiry
}

def load_notification_log() -> Dict[str, Any]:
    """Load the notification tracking log."""
    if os.path.exists(NOTIFICATION_LOG_PATH):
        with open(NOTIFICATION_LOG_PATH, 'r') as f:
            return json.load(f)
    return {"notifications": {}}

def save_notification_log(log: Dict[str, Any]) -> None:
    """Save the notification tracking log."""
    os.makedirs(os.path.dirname(NOTIFICATION_LOG_PATH), exist_ok=True)
    with open(NOTIFICATION_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def get_short_id(decision_id: str) -> str:
    """Get a short reference ID for SMS commands."""
    return decision_id[:4]

def format_sms_notification(decision: Dict[str, Any], is_reminder: bool = False) -> str:
    """
    Format a decision into an SMS-friendly message.
    Must be under 160 characters ideally, but up to 320 is acceptable.
    """
    priority = decision['priority']
    summary = decision['summary']
    short_id = get_short_id(decision['id'])
    origin = decision.get('origin', 'unknown')
    
    # Prefix based on origin
    origin_prefix = "Zoputer: " if origin == "zoputer" else ""
    
    # Reminder prefix
    reminder_prefix = "⏰ REMINDER: " if is_reminder else ""
    
    # Calculate time remaining for reminders
    if is_reminder:
        expires_at = datetime.fromisoformat(decision['expires_at'].replace('Z', '+00:00'))
        now = datetime.now(expires_at.tzinfo)
        hours_left = max(0, (expires_at - now).total_seconds() / 3600)
        reminder_info = f" ({hours_left:.0f}h left)" if hours_left < 24 else ""
    else:
        reminder_info = ""
    
    # Build message
    header = f"{reminder_prefix}🔔 Decision needed ({priority}){reminder_info}"
    body = f"{origin_prefix}{summary}"
    footer = f"Reply: n5 decision {short_id}"
    
    # Truncate body if needed to fit in SMS
    max_body_len = 160 - len(header) - len(footer) - 4  # 4 for newlines
    if len(body) > max_body_len:
        body = body[:max_body_len - 3] + "..."
    
    return f"{header}\n{body}\n\n{footer}"

def needs_initial_notification(decision_id: str, log: Dict[str, Any]) -> bool:
    """Check if a decision needs its initial notification."""
    return decision_id not in log.get('notifications', {})

def needs_reminder(decision: Dict[str, Any], log: Dict[str, Any]) -> bool:
    """Check if a decision needs a reminder notification."""
    decision_id = decision['id']
    priority = decision['priority']
    
    # No reminder schedule for this priority
    reminder_hours = REMINDER_SCHEDULE.get(priority, [])
    if not reminder_hours:
        return False
    
    # Parse expiration time
    expires_at = datetime.fromisoformat(decision['expires_at'].replace('Z', '+00:00'))
    now = datetime.utcnow().replace(tzinfo=expires_at.tzinfo)
    hours_until_expiry = (expires_at - now).total_seconds() / 3600
    
    if hours_until_expiry <= 0:
        return False  # Already expired
    
    # Get sent reminders
    notif_record = log.get('notifications', {}).get(decision_id, {})
    sent_reminders = notif_record.get('reminders_sent', [])
    
    # Check if any reminder threshold is crossed
    for reminder_hour in reminder_hours:
        if hours_until_expiry <= reminder_hour and reminder_hour not in sent_reminders:
            return True
    
    return False

def get_next_reminder_hour(decision: Dict[str, Any], log: Dict[str, Any]) -> Optional[int]:
    """Get the next reminder hour that should be triggered."""
    decision_id = decision['id']
    priority = decision['priority']
    
    reminder_hours = REMINDER_SCHEDULE.get(priority, [])
    if not reminder_hours:
        return None
    
    expires_at = datetime.fromisoformat(decision['expires_at'].replace('Z', '+00:00'))
    now = datetime.utcnow().replace(tzinfo=expires_at.tzinfo)
    hours_until_expiry = (expires_at - now).total_seconds() / 3600
    
    notif_record = log.get('notifications', {}).get(decision_id, {})
    sent_reminders = notif_record.get('reminders_sent', [])
    
    for reminder_hour in sorted(reminder_hours, reverse=True):
        if hours_until_expiry <= reminder_hour and reminder_hour not in sent_reminders:
            return reminder_hour
    
    return None

def log_notification_sent(decision_id: str, notif_type: str, message: str, 
                          reminder_hour: Optional[int] = None) -> None:
    """Log that a notification was sent."""
    log = load_notification_log()
    
    if decision_id not in log['notifications']:
        log['notifications'][decision_id] = {
            'initial_sent': None,
            'reminders_sent': [],
            'history': []
        }
    
    record = log['notifications'][decision_id]
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    if notif_type == 'initial':
        record['initial_sent'] = timestamp
    elif notif_type == 'reminder' and reminder_hour is not None:
        if reminder_hour not in record['reminders_sent']:
            record['reminders_sent'].append(reminder_hour)
    
    record['history'].append({
        'type': notif_type,
        'sent_at': timestamp,
        'message_preview': message[:50] + '...' if len(message) > 50 else message,
        'reminder_hour': reminder_hour
    })
    
    save_notification_log(log)

def send_sms_notification(message: str) -> bool:
    """
    Send SMS via Zo's capability.
    
    This function writes a request file that triggers the Zo SMS system.
    In practice, this would be called by the scheduled agent or directly
    through the Zo API.
    """
    # Write to a request file that can be picked up
    request_path = "/home/workspace/N5/data/sms_outbox"
    os.makedirs(request_path, exist_ok=True)
    
    request_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    request_file = os.path.join(request_path, f"decision_notify_{request_id}.json")
    
    with open(request_file, 'w') as f:
        json.dump({
            'type': 'decision_notification',
            'message': message,
            'created_at': datetime.utcnow().isoformat() + "Z",
            'status': 'pending'
        }, f, indent=2)
    
    print(f"[SMS Request] Written to {request_file}")
    print(f"[Message Preview]\n{message}")
    return True

def notify_human(decision_id: str, immediate: bool = False, is_reminder: bool = False) -> bool:
    """
    Send SMS notification to V about a pending decision.
    
    Args:
        decision_id: The pending decision to notify about
        immediate: Skip any batching, send now
        is_reminder: Whether this is a reminder vs initial notification
    
    Returns:
        True if notification was sent/queued successfully
    """
    decision = get_decision(decision_id)
    
    if not decision:
        print(f"Error: Decision {decision_id} not found")
        return False
    
    if decision['status'] != 'pending':
        print(f"Decision {decision_id} is not pending (status: {decision['status']})")
        return False
    
    log = load_notification_log()
    reminder_hour = None
    
    if is_reminder:
        reminder_hour = get_next_reminder_hour(decision, log)
        if reminder_hour is None:
            print(f"No reminder needed for decision {decision_id}")
            return False
    
    # Format the SMS message
    message = format_sms_notification(decision, is_reminder=is_reminder)
    
    # Send the notification
    success = send_sms_notification(message)
    
    if success:
        notif_type = 'reminder' if is_reminder else 'initial'
        log_notification_sent(decision_id, notif_type, message, reminder_hour)
        print(f"✓ Notification sent for decision {decision_id[:8]}...")
    
    return success

def check_and_notify() -> Dict[str, int]:
    """
    Check for decisions needing notification and send them.
    
    Returns:
        Dict with counts of initial and reminder notifications sent
    """
    log = load_notification_log()
    pending = list_pending(status='pending')
    
    counts = {'initial': 0, 'reminders': 0, 'skipped': 0}
    
    for decision in pending:
        decision_id = decision['id']
        
        if needs_initial_notification(decision_id, log):
            if notify_human(decision_id):
                counts['initial'] += 1
        elif needs_reminder(decision, log):
            if notify_human(decision_id, is_reminder=True):
                counts['reminders'] += 1
        else:
            counts['skipped'] += 1
    
    return counts

def get_notification_status() -> Dict[str, Any]:
    """Get current notification status for all pending decisions."""
    log = load_notification_log()
    pending = list_pending(status='pending')
    
    status = {
        'pending_count': len(pending),
        'notified_count': 0,
        'needs_initial': [],
        'needs_reminder': [],
        'up_to_date': []
    }
    
    for decision in pending:
        decision_id = decision['id']
        short_id = get_short_id(decision_id)
        
        if needs_initial_notification(decision_id, log):
            status['needs_initial'].append({
                'short_id': short_id,
                'full_id': decision_id,
                'priority': decision['priority'],
                'summary': decision['summary'][:50]
            })
        elif needs_reminder(decision, log):
            status['needs_reminder'].append({
                'short_id': short_id,
                'full_id': decision_id,
                'priority': decision['priority'],
                'next_reminder': get_next_reminder_hour(decision, log)
            })
        else:
            status['up_to_date'].append(short_id)
            status['notified_count'] += 1
    
    return status

def main():
    """CLI interface for human escalation notifications."""
    parser = argparse.ArgumentParser(
        description="Send SMS notifications for pending decisions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Send command
    send_parser = subparsers.add_parser("send", help="Send notification for a decision")
    send_parser.add_argument("decision_id", help="Decision ID (full or short)")
    send_parser.add_argument("--reminder", action="store_true", help="Send as reminder")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check and send pending notifications")
    check_parser.add_argument("--dry-run", action="store_true", help="Show what would be sent")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show notification status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Remind command
    remind_parser = subparsers.add_parser("remind", help="Force send a reminder")
    remind_parser.add_argument("decision_id", help="Decision ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "send":
        # Handle short ID lookup
        decision_id = args.decision_id
        if len(decision_id) <= 8:
            # Try to find full ID
            pending = list_pending(status='pending')
            matches = [d for d in pending if d['id'].startswith(decision_id)]
            if len(matches) == 1:
                decision_id = matches[0]['id']
            elif len(matches) > 1:
                print(f"Ambiguous short ID. Matches: {[d['id'][:8] for d in matches]}")
                return
            else:
                print(f"No pending decision found starting with {decision_id}")
                return
        
        notify_human(decision_id, is_reminder=args.reminder)
    
    elif args.command == "check":
        if args.dry_run:
            status = get_notification_status()
            print(f"Pending decisions: {status['pending_count']}")
            print(f"Would send initial notifications: {len(status['needs_initial'])}")
            for d in status['needs_initial']:
                print(f"  - {d['short_id']} ({d['priority']}): {d['summary']}...")
            print(f"Would send reminders: {len(status['needs_reminder'])}")
            for d in status['needs_reminder']:
                print(f"  - {d['short_id']} ({d['priority']}): {d['next_reminder']}h reminder")
        else:
            counts = check_and_notify()
            print(f"Notifications sent:")
            print(f"  Initial: {counts['initial']}")
            print(f"  Reminders: {counts['reminders']}")
            print(f"  Skipped (already notified): {counts['skipped']}")
    
    elif args.command == "status":
        status = get_notification_status()
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Pending Decisions: {status['pending_count']}")
            print(f"Already Notified: {status['notified_count']}")
            
            if status['needs_initial']:
                print(f"\nNeeds Initial Notification ({len(status['needs_initial'])}):")
                for d in status['needs_initial']:
                    print(f"  {d['short_id']} | {d['priority']:8} | {d['summary']}...")
            
            if status['needs_reminder']:
                print(f"\nNeeds Reminder ({len(status['needs_reminder'])}):")
                for d in status['needs_reminder']:
                    print(f"  {d['short_id']} | {d['priority']:8} | {d['next_reminder']}h before expiry")
            
            if status['up_to_date']:
                print(f"\nUp to Date: {', '.join(status['up_to_date'])}")
    
    elif args.command == "remind":
        decision_id = args.decision_id
        if len(decision_id) <= 8:
            pending = list_pending(status='pending')
            matches = [d for d in pending if d['id'].startswith(decision_id)]
            if len(matches) == 1:
                decision_id = matches[0]['id']
            elif len(matches) > 1:
                print(f"Ambiguous short ID. Matches: {[d['id'][:8] for d in matches]}")
                return
            else:
                print(f"No pending decision found starting with {decision_id}")
                return
        
        notify_human(decision_id, immediate=True, is_reminder=True)

if __name__ == "__main__":
    main()
