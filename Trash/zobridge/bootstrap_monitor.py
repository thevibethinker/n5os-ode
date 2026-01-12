#!/usr/bin/env python3
"""
ZoBridge Bootstrap Monitor
Processes ChildZo messages and sends SMS notifications at major milestones.
CRITICAL: Does NOT make changes to ParentZo. Only processes messages and notifies V.
"""
import sqlite3
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
DB_PATH = Path("/home/workspace/N5/data/zobridge.db")
STATE_FILE = Path("/home/workspace/N5/data/bootstrap_monitor_state.json")

# Major milestones that trigger SMS
MILESTONE_MESSAGES = {
    "msg_100": "✅ ChildZo deployed ZoBridge",
    "msg_004": "✅ ChildZo created N5 directory structure",
    "msg_010": "🎯 Phase 2: Architectural principles loaded",
    "msg_020": "🎯 Phase 3: Core scripts operational",
    "msg_030": "🎯 Phase 4: Knowledge system active",
    "msg_040": "🎯 Phase 5: List management working",
    "msg_050": "🎉 Bootstrap Complete!"
}

def load_state() -> Dict:
    """Load previous monitoring state"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_processed_timestamp": None,
        "processed_messages": [],
        "notifications_sent": []
    }

def save_state(state: Dict):
    """Save monitoring state"""
    STATE_FILE.write_text(json.dumps(state, indent=2))
    logger.info(f"State saved: {len(state['processed_messages'])} messages processed")

def get_unprocessed_messages(last_timestamp: Optional[str]) -> List[Dict]:
    """Fetch unprocessed messages from ChildZo"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if last_timestamp:
        cursor.execute("""
            SELECT * FROM messages 
            WHERE from_system = 'ChildZo' 
            AND created_at > ?
            ORDER BY created_at ASC
        """, (last_timestamp,))
    else:
        cursor.execute("""
            SELECT * FROM messages 
            WHERE from_system = 'ChildZo'
            ORDER BY created_at ASC
        """)
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def parse_message_content(msg: Dict) -> Dict:
    """Parse message content JSON"""
    try:
        return json.loads(msg['content_json'])
    except:
        return {}

def format_message_summary(msg: Dict) -> str:
    """Create readable summary of message"""
    content = parse_message_content(msg)
    msg_id = msg['message_id']
    
    lines = [f"\n📨 **{msg_id}** ({msg['created_at']})"]
    
    # Status
    if 'status' in content:
        lines.append(f"Status: {content['status']}")
    
    # Key info
    if 'phase' in content:
        lines.append(f"Phase: {content['phase']}")
    if 'task' in content:
        lines.append(f"Task: {content['task']}")
    if 'verification' in content and isinstance(content['verification'], dict):
        lines.append(f"Verification: {len(content['verification'])} checks")
    
    # Readiness
    if content.get('ready_for_next'):
        lines.append("✅ Ready for next step")
    
    return "\n".join(lines)

def should_notify(msg_id: str, state: Dict) -> bool:
    """Check if this message warrants SMS notification"""
    # Already notified?
    if msg_id in state['notifications_sent']:
        return False
    
    # Is it a milestone?
    return msg_id in MILESTONE_MESSAGES

def send_sms_notification(msg_id: str, summary: str):
    """Send SMS via Zo's send_sms_to_user (simulation)"""
    milestone = MILESTONE_MESSAGES.get(msg_id, "Progress update")
    message = f"🤖 ZoBridge Bootstrap\n\n{milestone}\n{summary}"
    
    logger.info(f"📱 SMS NOTIFICATION: {milestone}")
    logger.info(message)
    
    # In actual implementation, call:
    # send_sms_to_user(message=message)
    print(f"\n{'='*60}")
    print("📱 SMS NOTIFICATION")
    print('='*60)
    print(message)
    print('='*60 + "\n")

def process_messages():
    """Main processing loop"""
    logger.info("Starting ZoBridge Bootstrap Monitor")
    
    state = load_state()
    logger.info(f"Loaded state: {len(state['processed_messages'])} messages already processed")
    
    messages = get_unprocessed_messages(state['last_processed_timestamp'])
    logger.info(f"Found {len(messages)} new messages from ChildZo")
    
    if not messages:
        logger.info("No new messages to process")
        return
    
    # Process each message
    for msg in messages:
        msg_id = msg['message_id']
        logger.info(f"Processing {msg_id}")
        
        # Create summary
        summary = format_message_summary(msg)
        print(summary)
        
        # Check if milestone
        if should_notify(msg_id, state):
            send_sms_notification(msg_id, summary)
            state['notifications_sent'].append(msg_id)
        
        # Mark processed
        state['processed_messages'].append(msg_id)
        state['last_processed_timestamp'] = msg['created_at']
    
    # Save state
    save_state(state)
    logger.info(f"✅ Processed {len(messages)} messages")
    
    # Summary report
    print(f"\n{'='*60}")
    print(f"Bootstrap Progress: {len(state['processed_messages'])} total messages")
    print(f"Notifications sent: {len(state['notifications_sent'])}")
    print('='*60)

def show_status():
    """Show current bootstrap status"""
    state = load_state()
    
    print("\n" + "="*60)
    print("ZoBridge Bootstrap Status")
    print("="*60)
    print(f"Total messages processed: {len(state['processed_messages'])}")
    print(f"Notifications sent: {len(state['notifications_sent'])}")
    print(f"Last update: {state['last_processed_timestamp'] or 'Never'}")
    
    if state['processed_messages']:
        print(f"\nProcessed messages: {', '.join(state['processed_messages'][-10:])}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "status":
            show_status()
        else:
            process_messages()
    except Exception as e:
        logger.error(f"Monitor error: {e}", exc_info=True)
        sys.exit(1)
