#!/usr/bin/env python3
"""
Message Queue System
Enables conversations to send/receive messages to each other.

Usage:
    python3 message_queue.py send --from con_A --to con_B --content "Message text"
    python3 message_queue.py check --convo-id con_A
    python3 message_queue.py read --message-id MSG_123
    python3 message_queue.py ack --message-id MSG_123
"""

import argparse
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

MESSAGES_DIR = Path("/home/workspace/N5/.state/messages")
CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")


class MessageQueue:
    def __init__(self):
        MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    def send(self, from_id: str, to_id: str, content: str, msg_type: str = "info") -> str:
        """Send a message from one conversation to another."""
        try:
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            timestamp = datetime.now(timezone.utc).isoformat()
            
            message = {
                "id": message_id,
                "from": from_id,
                "to": to_id,
                "content": content,
                "type": msg_type,
                "timestamp": timestamp,
                "status": "unread"
            }
            
            # Store in recipient's message file
            recipient_file = MESSAGES_DIR / f"{to_id}.jsonl"
            with recipient_file.open("a") as f:
                f.write(json.dumps(message) + "\n")
            
            # Also create notification in recipient workspace
            recipient_workspace = CONVO_WORKSPACES_ROOT / to_id
            recipient_workspace.mkdir(parents=True, exist_ok=True)
            
            notification_file = recipient_workspace / "MESSAGES.md"
            if notification_file.exists():
                existing = notification_file.read_text()
            else:
                existing = "# Messages\n\n"
            
            new_msg = f"""
## New Message [{message_id}]
**From:** {from_id}  
**Received:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  
**Type:** {msg_type}

{content}

---
"""
            notification_file.write_text(existing + new_msg)
            
            logger.info(f"✓ Sent message {message_id}")
            logger.info(f"  From: {from_id}")
            logger.info(f"  To: {to_id}")
            logger.info(f"  Type: {msg_type}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return ""
    
    def check(self, convo_id: str) -> List[Dict]:
        """Check for messages sent to a conversation."""
        try:
            message_file = MESSAGES_DIR / f"{convo_id}.jsonl"
            
            if not message_file.exists():
                logger.info(f"No messages for {convo_id}")
                return []
            
            messages = []
            with message_file.open("r") as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
            
            # Filter to unread only
            unread = [m for m in messages if m.get("status") == "unread"]
            
            logger.info(f"✓ Found {len(unread)} unread message(s) for {convo_id}")
            for msg in unread:
                logger.info(f"  [{msg['id']}] from {msg['from']}: {msg['content'][:50]}...")
            
            return unread
            
        except Exception as e:
            logger.error(f"Failed to check messages: {e}")
            return []
    
    def read(self, message_id: str) -> Optional[Dict]:
        """Read a specific message by ID."""
        try:
            # Search all message files
            for msg_file in MESSAGES_DIR.glob("*.jsonl"):
                with msg_file.open("r") as f:
                    for line in f:
                        if line.strip():
                            msg = json.loads(line)
                            if msg.get("id") == message_id:
                                logger.info(f"✓ Found message {message_id}")
                                return msg
            
            logger.warning(f"Message {message_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to read message: {e}")
            return None
    
    def acknowledge(self, message_id: str) -> bool:
        """Mark a message as read."""
        try:
            # Find and update message status
            for msg_file in MESSAGES_DIR.glob("*.jsonl"):
                messages = []
                updated = False
                
                with msg_file.open("r") as f:
                    for line in f:
                        if line.strip():
                            msg = json.loads(line)
                            if msg.get("id") == message_id:
                                msg["status"] = "read"
                                msg["read_at"] = datetime.now(timezone.utc).isoformat()
                                updated = True
                            messages.append(msg)
                
                if updated:
                    # Rewrite file
                    with msg_file.open("w") as f:
                        for msg in messages:
                            f.write(json.dumps(msg) + "\n")
                    
                    logger.info(f"✓ Acknowledged message {message_id}")
                    return True
            
            logger.warning(f"Message {message_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Message Queue System")
    parser.add_argument("action", choices=["send", "check", "read", "ack"])
    parser.add_argument("--from", dest="from_id", help="Sender conversation ID")
    parser.add_argument("--to", dest="to_id", help="Recipient conversation ID")
    parser.add_argument("--content", help="Message content")
    parser.add_argument("--type", dest="msg_type", default="info", 
                       choices=["info", "task", "question", "update", "blocker"],
                       help="Message type")
    parser.add_argument("--convo-id", help="Conversation ID (for check)")
    parser.add_argument("--message-id", help="Message ID (for read/ack)")
    
    args = parser.parse_args()
    
    queue = MessageQueue()
    
    if args.action == "send":
        if not args.from_id or not args.to_id or not args.content:
            logger.error("--from, --to, and --content required for send")
            return 1
        message_id = queue.send(args.from_id, args.to_id, args.content, args.msg_type)
        if message_id:
            print(json.dumps({"message_id": message_id}))
            return 0
        return 1
    
    elif args.action == "check":
        if not args.convo_id:
            logger.error("--convo-id required for check")
            return 1
        messages = queue.check(args.convo_id)
        print(json.dumps({"messages": messages}, indent=2))
        return 0
    
    elif args.action == "read":
        if not args.message_id:
            logger.error("--message-id required for read")
            return 1
        message = queue.read(args.message_id)
        if message:
            print(json.dumps(message, indent=2))
            return 0
        return 1
    
    elif args.action == "ack":
        if not args.message_id:
            logger.error("--message-id required for ack")
            return 1
        success = queue.acknowledge(args.message_id)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    exit(main())
