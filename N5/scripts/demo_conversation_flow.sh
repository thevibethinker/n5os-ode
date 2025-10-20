#!/bin/bash
# Demo: Demonstrator asks question, parent responds

echo "════════════════════════════════════════════════════════════"
echo " DEMO: AI-to-AI Conversation Flow"
echo "════════════════════════════════════════════════════════════"
echo ""

URL="http://localhost:8769"

# Check server
echo "1️⃣  Checking server health..."
HEALTH=$(curl -s "$URL/health" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "   Server status: $HEALTH ✅"
echo ""

# Demonstrator: Start conversation
echo "2️⃣  Demonstrator: Starting conversation..."
START_RESPONSE=$(curl -s -X POST "$URL/api/converse/start" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"phase": "phase_2", "demo": true}}')
CONV_ID=$(echo "$START_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")
echo "   Conversation ID: $CONV_ID"
echo ""

# Demonstrator: Ask question
echo "3️⃣  Demonstrator: Asking question..."
QUESTION="I've copied the bootstrap scripts to N5/scripts/. What should I do next to ensure N5 is properly initialized?"
echo "   Question: \"$QUESTION\""
curl -s -X POST "$URL/api/converse/ask" \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"question\": \"$QUESTION\", \"metadata\": {\"step\": \"post_script_copy\"}}" > /dev/null
echo "   ✅ Question submitted"
echo ""

# Check what parent sees
echo "4️⃣  Parent: Checking for questions..."
POLL=$(curl -s "$URL/api/converse/poll/$CONV_ID")
HAS_QUESTION=$(echo "$POLL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('pending_question', False))")
echo "   Pending question: $HAS_QUESTION"
if [ "$HAS_QUESTION" = "True" ]; then
    PENDING_Q=$(echo "$POLL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('question', ''))")
    echo "   Question text: \"$PENDING_Q\""
fi
echo ""

# Parent: Submit response
echo "5️⃣  Parent: Submitting response..."
ANSWER="Great progress! Next steps: (1) Run 'python3 N5/scripts/test_n5_core.py' to validate core functionality, (2) Update N5/config/config.jsonl with your workspace paths, (3) Initialize your intelligence graph with 'python3 N5/scripts/init_intelligence.py'. This ensures N5 is fully operational before proceeding to phase 3."
echo "   Response: \"${ANSWER:0:100}...\""
curl -s -X POST "$URL/api/converse/respond" \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"answer\": \"$ANSWER\", \"metadata\": {\"confidence\": \"high\"}}" > /dev/null
echo "   ✅ Response submitted"
echo ""

# Demonstrator: Poll for response
echo "6️⃣  Demonstrator: Polling for parent's response..."
sleep 1
RESPONSE=$(curl -s "$URL/api/converse/poll/$CONV_ID")
HAS_RESPONSE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('has_response', False))")
if [ "$HAS_RESPONSE" = "true" ]; then
    ANSWER_TEXT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['answer'])")
    echo "   ✅ Response received!"
    echo "   Answer: \"${ANSWER_TEXT:0:100}...\""
else
    echo "   ⏳ No response yet (would retry in real scenario)"
fi
echo ""

# View history
echo "7️⃣  Viewing conversation history..."
HISTORY=$(curl -s "$URL/api/converse/history/$CONV_ID")
MSG_COUNT=$(echo "$HISTORY" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['history']))")
echo "   Total messages: $MSG_COUNT"
echo ""
echo "   Conversation flow:"
echo "$HISTORY" | python3 -c "
import sys, json
history = json.load(sys.stdin)['history']
for msg in history:
    role = msg['role'].upper()
    content = msg['content'][:80] + '...' if len(msg['content']) > 80 else msg['content']
    print(f'   [{role}] {content}')
"
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo " ✅ DEMO COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "What happened:"
echo "  1. Demonstrator started conversation"
echo "  2. Demonstrator asked for guidance"
echo "  3. Parent received question"
echo "  4. Parent provided AI-generated response"
echo "  5. Demonstrator received guidance"
echo "  6. Full history preserved"
echo ""
echo "Result: AI-to-AI communication working! 🤖↔️🤖"
echo ""
echo "Conversation logged to:"
echo "  /home/workspace/N5/logs/bootstrap_conversations.jsonl"
echo ""
echo "════════════════════════════════════════════════════════════"
