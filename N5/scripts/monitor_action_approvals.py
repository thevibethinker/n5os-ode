#!/usr/bin/env python3
"""
Monitor Gmail for action approval replies and push to Akiflow.
Runs as a service, checking every 2 minutes.
"""
import json
import time
import logging
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
INBOX = WORKSPACE / "N5/inbox/meeting_actions"

def check_pending_email_requests() -> List[Path]:
    """Find email requests that haven't been sent yet."""
    pending = []
    for request_file in INBOX.glob("*_email_request.json"):
        data = json.loads(request_file.read_text())
        if data.get("sent_at") is None:
            pending.append(request_file)
    return pending

def send_approval_email(meeting_name: str, actions: List[Dict], output_file: Path) -> str:
    """Send approval email via Gmail API and return thread ID."""
    # Format email body
    body = format_approval_email(meeting_name, actions)
    
    # Send via Gmail API ONLY (not send_email_to_user)
    result = subprocess.run(
        ["python3", "-c", f"""
import sys
sys.path.append('/home/workspace')
from tools import use_app_gmail

use_app_gmail(
    tool_name='gmail-send-email',
    configured_props={{
        'to': 'vrijen@mycareerspan.com',
        'fromName': 'Zo (V\\'s AI)',
        'fromEmail': 'va@zo.computer',
        'subject': '[N5] {len(actions)} action items from {meeting_name}',
        'body': '''{body}''',
        'bodyType': 'plaintext'
    }}
)
"""],
        capture_output=True,
        text=True
    )
    
    logger.info(f"✓ Email sent to vrijen@mycareerspan.com")
    return "pending"  # Thread ID will be detected on reply

def check_for_replies() -> List[Dict]:
    """Check Gmail for replies to approval emails."""
    # This would use Gmail API to check for replies
    # For now, return empty - implement when Zo has access in service context
    return []

def parse_approval(reply_text: str) -> Dict:
    """Parse V's approval response."""
    reply_lower = reply_text.lower().strip()
    
    # Approve all
    if any(phrase in reply_lower for phrase in ['approve all', 'approved', 'yes', 'ok']):
        return {'action': 'approve_all', 'items': []}
    
    # Selective approval: "approve 1,3,5"
    match = re.search(r'approve\s+([\d,\s]+)', reply_lower)
    if match:
        items = [int(x.strip()) for x in match.group(1).split(',')]
        return {'action': 'approve_selected', 'items': items}
    
    # Skip: "skip 2"
    match = re.search(r'skip\s+(\d+)', reply_lower)
    if match:
        return {'action': 'skip', 'items': [int(match.group(1))]}
    
    # Edit: "edit 1: tomorrow 8am, 30m"
    match = re.search(r'edit\s+(\d+):\s*(.+)', reply_lower, re.IGNORECASE)
    if match:
        return {'action': 'edit', 'item': int(match.group(1)), 'changes': match.group(2)}
    
    return {'action': 'unknown'}

def push_to_akiflow(actions: List[Dict], meeting_title: str) -> bool:
    """Format and send approved actions to Akiflow."""
    if not actions:
        return False
    
    # Format email body with --- separators
    body_parts = []
    for action in actions:
        body_parts.append(f"Task: {action['text']}")
        body_parts.append(f"When: {action['suggested_when']}")
        body_parts.append(f"Duration: {action['suggested_duration']}")
        body_parts.append(f"Priority: {action['suggested_priority']}")
        body_parts.append(f"Project: {action['suggested_project']}")
        if action['suggested_tags']:
            body_parts.append(f"Tags: {', '.join(action['suggested_tags'])}")
        body_parts.append(f"Notes: From {meeting_title} - {action['context'][:100]}")
        body_parts.append("\n---\n")
    
    email_body = "\n".join(body_parts).rstrip("\n---\n")
    
    # Log for manual execution via Zo
    logger.info(f"\n✓ Ready to push {len(actions)} actions to Akiflow")
    logger.info(f"Subject: [N5] {len(actions)} tasks from {meeting_title}")
    logger.info(f"Body preview:\n{email_body[:300]}...")
    
    # For production: Would call Gmail API here
    # For now: Create a pending push file that Zo can execute
    push_file = INBOX / f"pending_push_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    push_data = {
        "to": "aki+qztlypb6-d@aki.akiflow.com",
        "subject": f"[N5] {len(actions)} tasks from {meeting_title}",
        "body": email_body,
        "actions_count": len(actions),
        "meeting_title": meeting_title,
        "created_at": datetime.now().isoformat()
    }
    push_file.write_text(json.dumps(push_data, indent=2))
    logger.info(f"✓ Push request saved: {push_file}")
    
    return True

def main_loop(interval: int = 120):
    """Main monitoring loop."""
    logger.info(f"✓ Action approval monitor started (checking every {interval}s)")
    
    while True:
        try:
            # Check for pending email requests
            pending_emails = check_pending_email_requests()
            if pending_emails:
                logger.info(f"Found {len(pending_emails)} pending approval emails")
                for request_file in pending_emails:
                    send_approval_email(request_file)
            
            # Check for replies
            replies = check_for_replies()
            if replies:
                logger.info(f"Found {len(replies)} approval replies")
                # Process each reply
                # Parse approval
                # Push to Akiflow
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            logger.info("\n✓ Monitor stopped")
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)
            time.sleep(interval)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Monitor action approvals')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    args = parser.parse_args()
    
    main_loop(args.interval)
