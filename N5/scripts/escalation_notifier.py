#!/usr/bin/env python3
"""
Escalation notifier orchestrator script.
Checks pending decisions and sends notifications based on priority and timing rules.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Reminder schedule: hours before expiry to send reminders
REMINDER_SCHEDULE = {
    'low': [],  # No reminders
    'normal': [],  # No reminders, just initial
    'high': [6],  # Reminder at 6 hours before expiry
    'critical': [2, 1]  # Reminders at 2h and 1h before expiry
}

def run_pending_decisions_cmd(cmd_args: List[str]) -> Optional[Dict]:
    """Run pending_decisions.py command and return JSON result."""
    try:
        cmd = ['python3', '/home/workspace/N5/scripts/pending_decisions.py'] + cmd_args + ['--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error running pending_decisions command {cmd_args}: {e}")
        return None

def run_notification_cmd(cmd_args: List[str]) -> bool:
    """Run notification script and return success status."""
    try:
        cmd = ['python3', '/home/workspace/Skills/human-escalation/scripts/notify.py'] + cmd_args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running notification command {cmd_args}: {e}")
        return False

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def get_notifications_sent(decision: Dict) -> List[Dict]:
    """Extract notifications sent from decision context."""
    context = decision.get('context', {})
    if isinstance(context, str):
        try:
            context = json.loads(context)
        except json.JSONDecodeError:
            return []
    return context.get('notifications_sent', [])

def needs_initial_notification(decision: Dict) -> bool:
    """Check if decision needs initial notification."""
    notifications = get_notifications_sent(decision)
    
    # Check if we already sent initial notification
    for notif in notifications:
        if notif.get('type') == 'initial':
            return False
    
    return True

def needs_reminder(decision: Dict) -> bool:
    """Check if decision needs a reminder notification."""
    priority = decision.get('priority', 'normal')
    reminder_hours = REMINDER_SCHEDULE.get(priority, [])
    
    if not reminder_hours:
        return False
    
    # Parse expiry time
    expiry_str = decision.get('expires_at')
    if not expiry_str:
        return False
        
    expiry = parse_datetime(expiry_str)
    if not expiry:
        return False
    
    now = datetime.now(expiry.tzinfo) if expiry.tzinfo else datetime.now()
    
    # Check each reminder threshold
    notifications = get_notifications_sent(decision)
    
    for hours_before in reminder_hours:
        reminder_time = expiry - timedelta(hours=hours_before)
        
        # If we've passed the reminder time
        if now >= reminder_time:
            # Check if we already sent this reminder
            already_sent = False
            for notif in notifications:
                if (notif.get('type') == 'reminder' and 
                    notif.get('hours_remaining') == hours_before):
                    already_sent = True
                    break
            
            if not already_sent:
                return True
    
    return False

def list_pending_decisions() -> List[Dict]:
    """Get list of all pending decisions."""
    result = run_pending_decisions_cmd(['list', '--status', 'pending'])
    if result and 'decisions' in result:
        return result['decisions']
    return []

def check_and_notify():
    """Check for decisions needing notification and send them."""
    print("Checking for decisions needing notifications...")
    
    pending = list_pending_decisions()
    print(f"Found {len(pending)} pending decisions")
    
    notifications_sent = 0
    
    for decision in pending:
        decision_id = decision['id']
        short_id = decision_id[:8]
        
        if needs_initial_notification(decision):
            print(f"Sending initial notification for decision {short_id}")
            success = run_notification_cmd(['send', decision_id])
            if success:
                notifications_sent += 1
                
        elif needs_reminder(decision):
            print(f"Sending reminder notification for decision {short_id}")
            success = run_notification_cmd(['send', decision_id, '--reminder'])
            if success:
                notifications_sent += 1
    
    print(f"Sent {notifications_sent} notifications")

def send_notification(decision_id: str, force: bool = False):
    """Send notification for specific decision."""
    decision = run_pending_decisions_cmd(['get', decision_id])
    if not decision:
        print(f"Decision {decision_id} not found")
        return False
    
    if decision['status'] != 'pending' and not force:
        print(f"Decision {decision_id} is {decision['status']}, use --force to send anyway")
        return False
    
    print(f"Sending notification for decision {decision_id}")
    return run_notification_cmd(['send', decision_id])

def show_status():
    """Show notification status for all pending decisions."""
    pending = list_pending_decisions()
    
    if not pending:
        print("No pending decisions")
        return
    
    print(f"Status of {len(pending)} pending decisions:\n")
    
    for decision in pending:
        decision_id = decision['id']
        short_id = decision_id[:8]
        priority = decision.get('priority', 'normal')
        summary = decision.get('summary', 'No summary')[:50]
        
        notifications = get_notifications_sent(decision)
        
        print(f"Decision: {short_id} ({priority})")
        print(f"Summary: {summary}")
        
        if notifications:
            print("Notifications sent:")
            for notif in notifications:
                notif_type = notif.get('type', 'unknown')
                sent_at = notif.get('sent_at', 'unknown')
                print(f"  - {notif_type} at {sent_at}")
        else:
            print("No notifications sent yet")
        
        # Check what notifications are needed
        if needs_initial_notification(decision):
            print("  → Needs initial notification")
        if needs_reminder(decision):
            print("  → Needs reminder notification")
        
        print()

def main():
    parser = argparse.ArgumentParser(description="Escalation notification orchestrator")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check and send pending notifications')
    
    # Send command  
    send_parser = subparsers.add_parser('send', help='Force send notification for specific decision')
    send_parser.add_argument('decision_id', help='Decision ID to notify about')
    send_parser.add_argument('--force', action='store_true', help='Send even if not pending')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show notification status')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_and_notify()
    elif args.command == 'send':
        success = send_notification(args.decision_id, args.force)
        sys.exit(0 if success else 1)
    elif args.command == 'status':
        show_status()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()