#!/usr/bin/env python3
"""
ZoBridge Bootstrap Sender
Automatically sends remaining bootstrap messages to ChildZo
"""
import argparse
import json
import logging
import sqlite3
import time
from pathlib import Path
from datetime import datetime
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "N5/data/zobridge.db"
CONFIG_PATH = WORKSPACE / "N5/services/zobridge/zobridge.config.json"
CHILDZO_URL = "https://zobridge-vademonstrator.zocomputer.io"
STATE_FILE = WORKSPACE / "N5/data/bootstrap_sender_state.json"

# Bootstrap message sequence
BOOTSTRAP_MESSAGES = [
    {
        "message_id": "msg_003",
        "phase": "Phase 1",
        "task": "Install core N5 schemas",
        "content": {
            "instruction": "Create N5 schema files",
            "files": [
                {
                    "path": "N5/schemas/command.schema.json",
                    "purpose": "Command registration schema"
                },
                {
                    "path": "N5/schemas/list-item.schema.json",
                    "purpose": "List item schema"
                }
            ]
        }
    },
    {
        "message_id": "msg_005",
        "phase": "Phase 2",
        "task": "Install core scripts",
        "content": {
            "instruction": "Create core N5 automation scripts",
            "files": [
                {
                    "path": "N5/scripts/n5_add_to_list.py",
                    "purpose": "Add items to lists"
                }
            ]
        }
    }
    # More messages will be added based on the full bootstrap plan
]


class BootstrapSender:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.secret = self._load_secret()
        self.state = self._load_state()
        
    def _load_secret(self) -> str:
        """Load ZoBridge secret from config"""
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                return config.get("secret", "")
        except Exception as e:
            logger.error(f"Failed to load secret: {e}")
            raise
    
    def _load_state(self) -> dict:
        """Load sender state"""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
                # Ensure all fields exist
                if "started_at" not in state:
                    state["started_at"] = None
                if "completed_at" not in state:
                    state["completed_at"] = None
                if "sent_messages" not in state:
                    state["sent_messages"] = []
                if "failed_messages" not in state:
                    state["failed_messages"] = []
                if "last_sent_message" not in state:
                    state["last_sent_message"] = None
                return state
        return {
            "last_sent_message": None,
            "sent_messages": [],
            "failed_messages": [],
            "started_at": None,
            "completed_at": None
        }
    
    def _save_state(self):
        """Save sender state"""
        if not self.dry_run:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, separators=(',', ':'), indent=2, fp=f)
            logger.info(f"State saved: {len(self.state['sent_messages'])} messages sent")
    
    def _get_sent_messages_from_db(self) -> set:
        """Get message IDs already sent (from ParentZo)"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT message_id FROM messages WHERE from_system = 'ParentZo'"
            )
            sent = {row[0] for row in cursor.fetchall()}
            conn.close()
            return sent
        except Exception as e:
            logger.error(f"DB query failed: {e}")
            return set()
    
    def _send_message(self, message_id: str, content: dict) -> bool:
        """Send message to ChildZo inbox"""
        
        # Load secret
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            secret = config["secret"]
        
        message = {
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": "ParentZo",
            "to": "ChildZo",
            "thread_id": "n5_bootstrap_001",
            "type": "instruction",
            "content": content
        }
        
        url = f"{CHILDZO_URL}/api/zobridge/inbox"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would POST to {url}")
            return True
            
        try:
            response = requests.post(
                url,
                json=message,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {secret}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Sent {message_id}: {message['task']}")
                return True
            else:
                logger.error(
                    f"✗ Failed to send {message_id}: "
                    f"{response.status_code} {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"✗ Exception sending {message_id}: {e}")
            return False
    
    def _wait_for_response(self, message_id: str, timeout: int = 60) -> bool:
        """Wait for ChildZo to acknowledge the message"""
        if self.dry_run:
            return True
            
        start_time = time.time()
        expected_response = message_id.replace("msg_", "msg_")
        # ChildZo responds with even-numbered messages
        response_num = int(message_id.split("_")[1]) + 1
        expected_response_id = f"msg_{response_num}"
        
        while time.time() - start_time < timeout:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM messages WHERE message_id = ? AND from_system = 'ChildZo'",
                    (expected_response_id,)
                )
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 0:
                    logger.info(f"✓ Received response {expected_response_id}")
                    return True
                    
            except Exception as e:
                logger.error(f"Error checking for response: {e}")
            
            time.sleep(2)
        
        logger.warning(f"⏱ Timeout waiting for {expected_response_id}")
        return False
    
    def run(self, start_from: str = None, limit: int = None) -> int:
        """Run the automated sender"""
        logger.info("Starting ZoBridge Bootstrap Sender")
        logger.info(f"Dry run: {self.dry_run}")
        
        # Get already-sent messages
        already_sent = self._get_sent_messages_from_db()
        logger.info(f"Already sent: {len(already_sent)} messages")
        
        # Filter messages to send
        to_send = []
        started = start_from is None
        
        for msg in BOOTSTRAP_MESSAGES:
            msg_id = msg["message_id"]
            
            # Skip if already sent
            if msg_id in already_sent:
                logger.info(f"⊘ Skipping {msg_id} (already sent)")
                continue
            
            # Skip if before start_from
            if not started:
                if msg_id == start_from:
                    started = True
                else:
                    continue
            
            to_send.append(msg)
            
            # Stop at limit
            if limit and len(to_send) >= limit:
                break
        
        if not to_send:
            logger.info("✓ No messages to send")
            return 0
        
        logger.info(f"Sending {len(to_send)} messages...")
        
        # Initialize state if first run
        if not self.state["started_at"]:
            self.state["started_at"] = datetime.utcnow().isoformat()
        
        # Send messages sequentially
        sent_count = 0
        failed_count = 0
        
        for message in to_send:
            msg_id = message["message_id"]
            
            # Send message
            if self.dry_run:
                logger.info(f"[DRY RUN] Would send {msg_id}")
                sent_count += 1
                continue
                
            if self._send_message(msg_id, message["content"]):
                sent_count += 1
                self.state["sent_messages"].append(msg_id)
                self.state["last_sent_message"] = msg_id
                self._save_state()
                
                # Wait for response
                if not self._wait_for_response(msg_id):
                    logger.warning(f"No response for {msg_id}, continuing anyway...")
                
                # Delay between messages
                if not self.dry_run:
                    time.sleep(3)
            else:
                failed_count += 1
                self.state["failed_messages"].append(msg_id)
                self._save_state()
                logger.error(f"Failed to send {msg_id}, stopping")
                break
        
        # Mark completion if all sent
        if failed_count == 0 and sent_count == len(to_send):
            self.state["completed_at"] = datetime.utcnow().isoformat()
            self._save_state()
        
        logger.info(f"✓ Sent: {sent_count}, ✗ Failed: {failed_count}")
        return 0 if failed_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="ZoBridge Bootstrap Sender - Automatically send bootstrap messages"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be sent without actually sending"
    )
    parser.add_argument(
        "--start-from",
        help="Start from specific message ID (e.g., msg_003)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of messages to send"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current sender status"
    )
    
    args = parser.parse_args()
    
    sender = BootstrapSender(dry_run=args.dry_run)
    
    if args.status:
        print(f"\nBootstrap Sender Status:")
        print(f"  Started: {sender.state.get('started_at', 'Not started')}")
        print(f"  Completed: {sender.state.get('completed_at', 'In progress')}")
        print(f"  Sent: {len(sender.state['sent_messages'])} messages")
        print(f"  Failed: {len(sender.state['failed_messages'])} messages")
        print(f"  Last sent: {sender.state.get('last_sent_message', 'None')}")
        return 0
    
    return sender.run(start_from=args.start_from, limit=args.limit)


if __name__ == "__main__":
    exit(main())
