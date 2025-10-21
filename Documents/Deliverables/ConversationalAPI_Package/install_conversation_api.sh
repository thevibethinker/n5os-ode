#!/bin/bash
# AI-to-AI Conversational API Installer for Demonstrator
# Single-command installation script

set -e

echo "════════════════════════════════════════════════════════════"
echo " Installing AI-to-AI Conversation API Client"
echo "════════════════════════════════════════════════════════════"
echo ""

# Configuration
PARENT_SERVER_URL="${BOOTSTRAP_API:-http://PARENT_IP:8769}"
INSTALL_DIR="/home/workspace"

echo "📦 Installation Configuration:"
echo "   Install directory: $INSTALL_DIR"
echo "   Parent server: $PARENT_SERVER_URL"
echo ""

# Check if we're in a workspace
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Error: $INSTALL_DIR not found"
    echo "   Are you running this in a Zo workspace?"
    exit 1
fi

echo "1️⃣  Creating N5 directories..."
mkdir -p "$INSTALL_DIR/N5/scripts"
mkdir -p "$INSTALL_DIR/N5/docs"
mkdir -p "$INSTALL_DIR/N5/logs"
echo "   ✅ Directories created"
echo ""

echo "2️⃣  Installing conversation client..."

# Extract embedded client script
cat > "$INSTALL_DIR/N5/scripts/bootstrap_conversation_client.py" << 'EMBEDDED_CLIENT_EOF'
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
import os

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


class ConversationClient:
    def __init__(self, base_url: str, conversation_id: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.conversation_id = conversation_id
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def start_conversation(self, metadata: Optional[Dict] = None) -> str:
        """Start new conversation with parent"""
        data = {"metadata": metadata or {}}
        response = self.session.post(
            f"{self.base_url}/api/converse/start",
            json=data,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        self.conversation_id = result["conversation_id"]
        logger.info(f"Started conversation: {self.conversation_id}")
        return self.conversation_id
    
    def ask_question(
        self,
        question: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Ask parent a question"""
        if not self.conversation_id:
            raise ValueError("No active conversation. Call start_conversation() first")
        
        data = {
            "conversation_id": self.conversation_id,
            "question": question,
            "metadata": metadata or {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/converse/ask",
            json=data,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info("Question submitted to parent")
        return True
    
    def poll_response(self, timeout: int = 30, interval: int = 2) -> Optional[Dict]:
        """Poll for parent's response with timeout"""
        if not self.conversation_id:
            raise ValueError("No active conversation")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.session.get(
                f"{self.base_url}/api/converse/poll/{self.conversation_id}",
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result["status"] == "response_ready":
                logger.info("Received response from parent")
                return result["response"]
            
            time.sleep(interval)
        
        logger.warning(f"No response after {timeout}s")
        return None
    
    def get_history(self) -> list:
        """Get full conversation history"""
        if not self.conversation_id:
            raise ValueError("No active conversation")
        
        response = self.session.get(
            f"{self.base_url}/api/converse/history/{self.conversation_id}",
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()["history"]


def main():
    parser = argparse.ArgumentParser(
        description="Communicate with parent Zo during bootstrap"
    )
    
    parser.add_argument(
        "--url",
        default=os.getenv("BOOTSTRAP_API", "http://localhost:8769"),
        help="Parent server URL (default: $BOOTSTRAP_API or localhost:8769)"
    )
    parser.add_argument(
        "--conversation-id",
        "--conv-id",
        help="Existing conversation ID (optional)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "ask", "poll", "history"],
        required=True,
        help="Action to perform"
    )
    parser.add_argument(
        "--question",
        help="Question to ask (for 'ask' action)"
    )
    parser.add_argument(
        "--metadata",
        type=json.loads,
        default={},
        help='Metadata as JSON (e.g., \'{"urgency": "high"}\')'
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Poll timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    try:
        client = ConversationClient(args.url, args.conversation_id)
        
        if args.action == "start":
            conv_id = client.start_conversation(args.metadata)
            print(json.dumps({"conversation_id": conv_id}))
        
        elif args.action == "ask":
            if not args.question:
                logger.error("--question required for 'ask' action")
                return 1
            
            client.ask_question(args.question, args.metadata)
            print(json.dumps({"status": "question_submitted"}))
        
        elif args.action == "poll":
            response = client.poll_response(timeout=args.timeout)
            if response:
                print(json.dumps(response, indent=2))
            else:
                print(json.dumps({"status": "no_response"}))
                return 1
        
        elif args.action == "history":
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
EMBEDDED_CLIENT_EOF

chmod +x "$INSTALL_DIR/N5/scripts/bootstrap_conversation_client.py"
echo "   ✅ Client installed"
echo ""

echo "3️⃣  Installing documentation..."

cat > "$INSTALL_DIR/INSTRUCTIONS_FOR_AI_CONVERSATION.md" << 'EMBEDDED_DOCS_EOF'
# Using AI-to-AI Conversation During Bootstrap

**You are the demonstrator.** You can ask questions directly to parent Zo and receive AI-generated responses!

## Quick Start

### Set Parent Server URL

```bash
export BOOTSTRAP_API="http://PARENT_IP:8769"
```

Replace `PARENT_IP` with the actual IP address of parent's server.

### Start a Conversation

```bash
CONV_ID=$(python3 N5/scripts/bootstrap_conversation_client.py \
  --action start | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")

echo "Conversation ID: $CONV_ID"
```

### Ask a Question

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
  --action ask \
  --conversation-id $CONV_ID \
  --question "What should I do after copying the bootstrap scripts?"
```

### Wait for Response

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
  --action poll \
  --conversation-id $CONV_ID \
  --timeout 60
```

## Full Example

```bash
# Set server URL
export BOOTSTRAP_API="http://parent.server.ip:8769"

# Start conversation
CONV_ID=$(python3 N5/scripts/bootstrap_conversation_client.py --action start | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")

# Ask question
python3 N5/scripts/bootstrap_conversation_client.py \
  --action ask \
  --conversation-id $CONV_ID \
  --question "I've copied bootstrap scripts to N5/scripts/. What's next?"

# Get response (waits up to 60 seconds)
python3 N5/scripts/bootstrap_conversation_client.py \
  --action poll \
  --conversation-id $CONV_ID \
  --timeout 60
```

## When to Use

Use this when you:
- Need clarification on a step
- Encounter unexpected behavior
- Want to verify your approach
- Need guidance on the next step

**Response time:** Usually 5-30 seconds

## Tips

1. **Be specific** in your questions
2. **Include context** about what you've done
3. **Save your conversation ID** for follow-up questions
4. **Don't block** - continue other work while waiting for responses

---

**You have AI-to-AI communication! Use it whenever you need guidance. 🤖↔️🤖**
EMBEDDED_DOCS_EOF

echo "   ✅ Documentation installed"
echo ""

echo "4️⃣  Checking dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "   📦 Installing requests library..."
    pip install -q requests
}
echo "   ✅ Dependencies ready"
echo ""

echo "5️⃣  Testing connection to parent..."
if curl -s --connect-timeout 5 "$PARENT_SERVER_URL/health" > /dev/null 2>&1; then
    echo "   ✅ Connected to parent server"
else
    echo "   ⚠️  Could not connect to parent server at $PARENT_SERVER_URL"
    echo "   Make sure to set BOOTSTRAP_API environment variable:"
    echo "   export BOOTSTRAP_API=\"http://PARENT_IP:8769\""
fi
echo ""

echo "════════════════════════════════════════════════════════════"
echo " ✅ Installation Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Set parent server URL:"
echo "   export BOOTSTRAP_API=\"http://PARENT_IP:8769\""
echo ""
echo "2. Read instructions:"
echo "   cat INSTRUCTIONS_FOR_AI_CONVERSATION.md"
echo ""
echo "3. Test the connection:"
echo "   python3 N5/scripts/bootstrap_conversation_client.py --action start"
echo ""
echo "You can now ask questions to parent Zo during bootstrap! 🚀"
echo ""
