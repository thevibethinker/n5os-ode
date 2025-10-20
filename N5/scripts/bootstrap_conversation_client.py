#!/usr/bin/env python3
"""
Bootstrap Conversation Client
For demonstrator Zo to communicate with parent Zo during bootstrap
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Run: pip install requests")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class BootstrapConversationClient:
    """Client for AI-to-AI conversation during bootstrap"""
    
    def __init__(self, server_url: str, conversation_id: Optional[str] = None):
        self.server_url = server_url.rstrip("/")
        self.conversation_id = conversation_id
        self.state_file = Path("/home/workspace/.bootstrap_conversation_state.json")
    
    def start_conversation(self, context: Optional[Dict] = None) -> str:
        """Start new conversation"""
        payload = {
            "initiator": "demonstrator_zo",
            "context": context or {}
        }
        
        response = requests.post(
            f"{self.server_url}/api/converse/start",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        self.conversation_id = data["conversation_id"]
        
        # Save state
        self._save_state()
        
        logger.info(f"✓ Started conversation: {self.conversation_id}")
        return self.conversation_id
    
    def ask_question(self, question: str, metadata: Optional[Dict] = None) -> bool:
        """Ask question to parent Zo"""
        if not self.conversation_id:
            logger.error("No active conversation. Start one first.")
            return False
        
        payload = {
            "conversation_id": self.conversation_id,
            "question": question,
            "metadata": metadata or {}
        }
        
        response = requests.post(
            f"{self.server_url}/api/converse/ask",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info(f"❓ Question sent: {question[:80]}...")
        return True
    
    def poll_for_response(self, timeout: int = 60, interval: int = 5) -> Optional[str]:
        """Poll for response with timeout"""
        if not self.conversation_id:
            logger.error("No active conversation")
            return None
        
        start_time = time.time()
        attempts = 0
        
        while time.time() - start_time < timeout:
            attempts += 1
            
            response = requests.get(
                f"{self.server_url}/api/converse/poll/{self.conversation_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "response_available":
                answer = data["response"]
                logger.info(f"💬 Response received: {answer[:80]}...")
                return answer
            
            logger.info(f"⏳ Polling attempt {attempts}, no response yet...")
            time.sleep(interval)
        
        logger.warning(f"⏱️ Timeout after {timeout}s")
        return None
    
    def get_history(self) -> list:
        """Get conversation history"""
        if not self.conversation_id:
            return []
        
        response = requests.get(
            f"{self.server_url}/api/converse/history/{self.conversation_id}",
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()["history"]
    
    def _save_state(self):
        """Save conversation state"""
        state = {
            "conversation_id": self.conversation_id,
            "server_url": self.server_url
        }
        
        with open(self.state_file, "w") as f:
            json.dump(state, f)
    
    def _load_state(self) -> bool:
        """Load saved conversation state"""
        if not self.state_file.exists():
            return False
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            self.conversation_id = state.get("conversation_id")
            logger.info(f"Loaded conversation state: {self.conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Bootstrap conversation client")
    parser.add_argument("--server", required=True, help="Server URL (e.g., http://10.0.0.5:8769)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start conversation")
    start_parser.add_argument("--context", help="Context JSON string")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask question")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--metadata", help="Metadata JSON string")
    ask_parser.add_argument("--wait", action="store_true", help="Wait for response")
    ask_parser.add_argument("--timeout", type=int, default=60, help="Poll timeout (seconds)")
    
    # Poll command
    poll_parser = subparsers.add_parser("poll", help="Poll for response")
    poll_parser.add_argument("--timeout", type=int, default=60, help="Timeout (seconds)")
    
    # History command
    subparsers.add_parser("history", help="Get conversation history")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        client = BootstrapConversationClient(args.server)
        
        if args.command == "start":
            context = json.loads(args.context) if args.context else {}
            conv_id = client.start_conversation(context)
            print(f"Conversation ID: {conv_id}")
        
        elif args.command == "ask":
            # Load existing conversation
            client._load_state()
            
            metadata = json.loads(args.metadata) if args.metadata else {}
            client.ask_question(args.question, metadata)
            
            if args.wait:
                answer = client.poll_for_response(timeout=args.timeout)
                if answer:
                    print(f"\nAnswer: {answer}\n")
                else:
                    print("No response received within timeout")
        
        elif args.command == "poll":
            client._load_state()
            answer = client.poll_for_response(timeout=args.timeout)
            if answer:
                print(f"\nAnswer: {answer}\n")
        
        elif args.command == "history":
            client._load_state()
            history = client.get_history()
            print(json.dumps(history, indent=2))
        
        return 0
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
