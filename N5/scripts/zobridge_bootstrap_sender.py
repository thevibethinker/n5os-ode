#!/usr/bin/env python3
"""
ZoBridge Bootstrap Sender
Sends bootstrap messages to ChildZo sequentially based on received confirmations.
"""
import sqlite3
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "/home/workspace/N5/data/zobridge.db"
SECRET = "temp_shared_secret_2025"
CHILDZO_URL = "https://zobridge-vademonstrator.zocomputer.io/api/zobridge/inbox"
STATE_FILE = "/home/workspace/N5/data/bootstrap_sender_state.json"

def load_state():
    """Load sender state"""
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_sent": 1, "messages_sent": [], "waiting_for": "msg_002"}

def save_state(state):
    """Save sender state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_latest_childzo_message():
    """Get the latest message from ChildZo"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id, content_json, created_at 
        FROM messages 
        WHERE from_system = 'ChildZo' 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    msg_id, content_json, created_at = row
    content = json.loads(content_json)
    return {"message_id": msg_id, "content": content, "created_at": created_at}

def send_message(msg_id, content):
    """Send message to ChildZo"""
    message = {
        "message_id": msg_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "from": "ParentZo",
        "to": "ChildZo",
        "type": "instruction",
        "thread_id": "n5_bootstrap_001",
        "content": content
    }
    
    # Save to temp file
    temp_file = f"/tmp/{msg_id}.json"
    with open(temp_file, 'w') as f:
        json.dump(message, f, indent=2)
    
    # Send via curl
    result = subprocess.run([
        'curl', '-s', '-X', 'POST', CHILDZO_URL,
        '-H', f'Authorization: Bearer {SECRET}',
        '-H', 'Content-Type: application/json',
        '-d', f'@{temp_file}'
    ], capture_output=True, text=True)
    
    try:
        response = json.loads(result.stdout)
        if "error" in response:
            logger.error(f"Failed to send {msg_id}: {response['error']}")
            return False
    except:
        pass
    
    logger.info(f"✓ Sent {msg_id}")
    return True

def get_next_message_content(msg_num):
    """Generate content for the next message"""
    
    # Load architectural principles for msg_009
    if msg_num == 9:
        try:
            with open("/home/workspace/Knowledge/architectural/principles/core.md") as f:
                core_principles = f.read()
            return {
                "phase": "Phase 3: Core Principles - Detailed",
                "task": "Load core architectural principles module",
                "file_to_create": "Knowledge/architectural/principles/core.md",
                "file_content": core_principles,
                "action_required": [
                    "Create file at specified path",
                    "Study SSOT and context efficiency principles",
                    "Be ready to apply in all work"
                ]
            }
        except FileNotFoundError:
            pass
    
    # Load safety principles for msg_011
    if msg_num == 11:
        try:
            with open("/home/workspace/Knowledge/architectural/principles/safety.md") as f:
                safety_principles = f.read()
            return {
                "phase": "Phase 3: Safety Principles - Detailed",
                "task": "Load safety principles module",
                "file_to_create": "Knowledge/architectural/principles/safety.md",
                "file_content": safety_principles,
                "action_required": [
                    "Create file at specified path",
                    "Internalize anti-overwrite, dry-run, error handling",
                    "Apply to all subsequent operations"
                ]
            }
        except FileNotFoundError:
            pass
    
    # Default template for other messages
    phases = {
        range(9, 14): ("Phase 3: Core Scripts", "Deploy essential N5 automation scripts"),
        range(14, 26): ("Phase 4: Knowledge System", "Build out Knowledge directory structure and content"),
        range(26, 41): ("Phase 5: Lists & Commands", "Set up list management and command registry"),
        range(41, 51): ("Phase 6: Integration & Testing", "Verify full system operation")
    }
    
    for msg_range, (phase, task) in phases.items():
        if msg_num in msg_range:
            return {
                "phase": phase,
                "task": f"{task} - Step {msg_num}",
                "instruction": f"Continue building N5 system - message {msg_num} of 50",
                "notes": "Detailed instructions will be provided as we progress through each phase."
            }
    
    return {
        "phase": "Unknown",
        "task": f"Bootstrap step {msg_num}",
        "instruction": "Continue N5 system bootstrap"
    }

def main():
    """Main sender logic"""
    logger.info("Starting bootstrap sender check...")
    
    # Load state
    state = load_state()
    logger.info(f"Last sent: msg_{str(state['last_sent']).zfill(3)}")
    
    # Get latest ChildZo message
    latest = get_latest_childzo_message()
    if not latest:
        logger.info("No messages from ChildZo yet")
        return
    
    logger.info(f"Latest from ChildZo: {latest['message_id']}")
    
    # Parse message number from latest ChildZo response
    # ChildZo sends even numbers (002, 004, 006, 008...)
    # ParentZo sends odd numbers (001, 003, 005, 007, 009...)
    
    msg_id = latest['message_id']
    # Handle both msg_XXX and resp_msg_XXX or resp_XXX formats
    if msg_id.startswith('resp_msg_'):
        childzo_num = int(msg_id.replace('resp_msg_', ''))
    elif msg_id.startswith('resp_'):
        childzo_num = int(msg_id.replace('resp_', ''))
    else:
        childzo_num = int(msg_id.replace('msg_', ''))
    
    next_parent_num = childzo_num + 1
    
    # Check if we should send next message
    if next_parent_num <= state['last_sent']:
        logger.info(f"Already sent msg_{str(next_parent_num).zfill(3)}, waiting for ChildZo response")
        return
    
    # Check if ChildZo confirmed previous message
    content = latest['content']
    if content.get('status') in ['received', 'complete', 'deployment_complete']:
        logger.info(f"ChildZo confirmed, sending next: msg_{str(next_parent_num).zfill(3)}")
        
        # Generate and send next message
        msg_id = f"msg_{str(next_parent_num).zfill(3)}"
        msg_content = get_next_message_content(next_parent_num)
        
        if send_message(msg_id, msg_content):
            state['last_sent'] = next_parent_num
            state['messages_sent'].append(msg_id)
            state['waiting_for'] = f"msg_{str(next_parent_num + 1).zfill(3)}"
            save_state(state)
            logger.info(f"✅ Sent {msg_id}, now waiting for ChildZo response")
        else:
            logger.error(f"❌ Failed to send {msg_id}")
    else:
        logger.info(f"ChildZo status: {content.get('status')}, waiting before sending next")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)
