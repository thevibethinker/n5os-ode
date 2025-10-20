#!/bin/bash
# Demo AI-to-AI Conversation
# Shows complete flow: question → response → poll

set -e

PARENT_URL="${1:-http://localhost:8769}"

echo "======================================================================"
echo "AI-to-AI Conversation Demo"
echo "======================================================================"
echo ""
echo "Server: $PARENT_URL"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Health check
echo -e "${BLUE}[1/6] Health Check${NC}"
echo "Command: curl $PARENT_URL/health"
echo ""
curl -s $PARENT_URL/health | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Server is healthy${NC}"
echo ""
sleep 2

# Step 2: Start conversation
echo "======================================================================"
echo -e "${BLUE}[2/6] Starting Conversation (Demonstrator)${NC}"
echo "Command: POST /api/converse/start"
echo ""

START_RESP=$(curl -s -X POST $PARENT_URL/api/converse/start \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"demo": true, "phase": "testing"}}')

echo "$START_RESP" | python3 -m json.tool
CONV_ID=$(echo "$START_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")
echo ""
echo -e "${GREEN}✓ Conversation started: $CONV_ID${NC}"
echo ""
sleep 2

# Step 3: Ask question
echo "======================================================================"
echo -e "${BLUE}[3/6] Asking Question (Demonstrator)${NC}"
echo "Command: POST /api/converse/ask"
echo ""

QUESTION="What are the key steps in bootstrap phase 1?"

ASK_RESP=$(curl -s -X POST $PARENT_URL/api/converse/ask \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"question\": \"$QUESTION\", \"metadata\": {\"demo\": true}}")

echo "$ASK_RESP" | python3 -m json.tool
echo ""
echo -e "${YELLOW}📩 Demonstrator asked: \"$QUESTION\"${NC}"
echo ""
sleep 2

# Step 4: Parent responds
echo "======================================================================"
echo -e "${BLUE}[4/6] Parent Responding${NC}"
echo "Command: POST /api/converse/respond"
echo ""
echo -e "${YELLOW}(In real bootstrap, parent sees question in log and responds)${NC}"
echo ""

ANSWER="Phase 1: (1) Verify directory structure exists, (2) Copy core schema files to N5/schemas/, (3) Copy bootstrap scripts to N5/scripts/, (4) Verify safety checks in place, (5) Create initial config files. Each step should be verified before proceeding."

RESPOND_RESP=$(curl -s -X POST $PARENT_URL/api/converse/respond \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"answer\": \"$ANSWER\"}")

echo "$RESPOND_RESP" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Parent submitted response${NC}"
echo ""
sleep 2

# Step 5: Poll for response
echo "======================================================================"
echo -e "${BLUE}[5/6] Demonstrator Polling for Response${NC}"
echo "Command: GET /api/converse/poll/$CONV_ID"
echo ""

POLL_RESP=$(curl -s $PARENT_URL/api/converse/poll/$CONV_ID)
echo "$POLL_RESP" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Demonstrator received parent's answer!${NC}"
echo ""
sleep 2

# Step 6: Get history
echo "======================================================================"
echo -e "${BLUE}[6/6] Full Conversation History${NC}"
echo "Command: GET /api/converse/history/$CONV_ID"
echo ""

HISTORY_RESP=$(curl -s $PARENT_URL/api/converse/history/$CONV_ID)
echo "$HISTORY_RESP" | python3 -m json.tool
echo ""

# Count messages
MESSAGE_COUNT=$(echo "$HISTORY_RESP" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['history']))")
echo -e "${GREEN}✓ Conversation has $MESSAGE_COUNT messages${NC}"
echo ""

# Summary
echo "======================================================================"
echo -e "${GREEN}Demo Complete! 🎉${NC}"
echo "======================================================================"
echo ""
echo "What just happened:"
echo "  1. ✓ Demonstrator started a conversation"
echo "  2. ✓ Demonstrator asked a question"
echo "  3. ✓ Parent submitted an answer"
echo "  4. ✓ Demonstrator retrieved the answer"
echo "  5. ✓ Full conversation history is preserved"
echo ""
echo "Conversation log saved to:"
echo "  /home/workspace/N5/logs/bootstrap_conversations.jsonl"
echo ""
echo -e "${BLUE}View the log:${NC}"
echo "  tail /home/workspace/N5/logs/bootstrap_conversations.jsonl"
echo ""
echo "======================================================================"
echo -e "${GREEN}Ready for real bootstrap! 🚀${NC}"
echo "======================================================================"
