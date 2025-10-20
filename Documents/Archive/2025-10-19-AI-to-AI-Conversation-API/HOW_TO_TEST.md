# How to Test the Conversational API

## Easiest Way: Run the Automated Test

```bash
python3 /home/workspace/N5/scripts/test_conversation_api.py --url http://localhost:8769
```

**Expected:** 6/6 tests pass ✅

---

## Manual Test (See How It Works)

### Option 1: Run the Quick Test Script

```bash
/home/.z/workspaces/con_3aNDddr4AJg0Vt6W/QUICK_TEST_COMMANDS.sh
```

This runs through a full conversation flow automatically.

### Option 2: Step-by-Step (Understanding the Flow)

Open 2 terminals:

**Terminal 1 - Monitor (Parent View):**
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl
```

**Terminal 2 - Demonstrator Simulation:**

```bash
# 1. Start conversation
curl -X POST http://localhost:8769/api/converse/start \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"test": true}}'

# Note the conversation_id returned (e.g., conv_abc123)

# 2. Ask a question
curl -X POST http://localhost:8769/api/converse/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "question": "What directory should I create first?",
    "metadata": {"urgency": "high"}
  }'

# You should see this appear in Terminal 1!

# 3. Parent responds (in Terminal 2 or 3)
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "answer": "Create N5/scripts first, then N5/lists."
  }'

# 4. Demonstrator polls for response
curl http://localhost:8769/api/converse/poll/conv_abc123

# You should see the answer!

# 5. View full history
curl http://localhost:8769/api/converse/history/conv_abc123 | python3 -m json.tool
```

---

## What Demonstrator Does (Real Bootstrap)

### Setup (Once)

```bash
# Demonstrator gets your IP
export PARENT_IP="192.168.1.100"  # You provide this
export API_URL="http://${PARENT_IP}:8769"

# Install client dependencies
pip install requests

# Test connection
curl $API_URL/health
```

### During Bootstrap (When Needed)

**Using the Python client (recommended):**

```bash
# Start conversation at beginning of bootstrap
python3 scripts/bootstrap_conversation_client.py \
  --url $API_URL \
  --action start \
  --metadata '{"bootstrap_session": "2025-10-19"}'
# Returns: conv_xyz789

# When demonstrator has a question
python3 scripts/bootstrap_conversation_client.py \
  --url $API_URL \
  --action ask \
  --conversation-id conv_xyz789 \
  --question "Should I use rsync or cp for copying scripts?" \
  --metadata '{"current_task": "phase_2_setup"}'

# Poll for your answer
python3 scripts/bootstrap_conversation_client.py \
  --url $API_URL \
  --action poll \
  --conversation-id conv_xyz789
```

**Using curl (if Python client not available):**

```bash
# Ask question
curl -X POST $API_URL/api/converse/ask \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "conv_xyz789", "question": "Your question here"}'

# Poll for response
curl $API_URL/api/converse/poll/conv_xyz789
```

---

## What YOU Do (Parent During Bootstrap)

### Before Bootstrap Starts

1. **Start server** (if not already running):
   ```bash
   ps aux | grep conversational_server  # Check if running
   
   # If not running:
   nohup python3 /home/workspace/N5/scripts/n5_bootstrap_conversational_server.py \
     --port 8769 > /tmp/conv_server.log 2>&1 &
   ```

2. **Open monitoring terminal:**
   ```bash
   # Watch for questions
   tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | \
     grep --line-buffered '"role": "demonstrator"'
   ```

3. **Keep this response function handy:**
   ```bash
   # Add to your shell
   respond() {
     curl -X POST http://localhost:8769/api/converse/respond \
       -H "Content-Type: application/json" \
       -d "{\"conversation_id\": \"$1\", \"answer\": \"$2\"}"
   }
   
   # Usage example:
   respond "conv_xyz789" "Use rsync with --checksum flag for reliability"
   ```

### During Bootstrap

1. **Watch monitor** - questions appear in real-time
2. **When question appears:**
   - Note conversation ID
   - Read the question
   - Check context if needed: `curl http://localhost:8769/api/converse/history/conv_xyz789`
3. **Respond:**
   ```bash
   respond "conv_xyz789" "Your detailed answer here with specific commands or guidance"
   ```
4. **Verify delivery** - should see response in log

---

## Testing Checklist

Before bootstrap:
- [ ] Server health check passes: `curl http://localhost:8769/health`
- [ ] Automated tests pass: `python3 test_conversation_api.py`
- [ ] Can start conversation
- [ ] Can ask question and see it in logs
- [ ] Can respond and demonstrator receives it
- [ ] Network accessible from demonstrator location

---

## Troubleshooting

**Server not responding?**
```bash
ps aux | grep conversational_server
lsof -i :8769
# Restart if needed
```

**Can't connect from demonstrator machine?**
```bash
# On parent: Get your IP
ip addr show | grep "inet "

# On demonstrator: Test connection
ping PARENT_IP
nc -zv PARENT_IP 8769
curl http://PARENT_IP:8769/health
```

**Response not received?**
```bash
# Check if response was submitted
grep "conv_xyz789" /home/workspace/N5/logs/bootstrap_conversations.jsonl | grep parent

# Verify conversation ID is correct
curl http://localhost:8769/api/converse/history/conv_xyz789
```

---

## Quick Reference

**Monitor questions:**
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | grep demonstrator
```

**Respond quickly:**
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "CONV_ID", "answer": "YOUR ANSWER"}'
```

**View history:**
```bash
curl http://localhost:8769/api/converse/history/CONV_ID | python3 -m json.tool
```

---

**Full documentation:** `file 'N5/docs/CONVERSATION_API_TESTING_GUIDE.md'`

**Ready to test! Start with the automated test, then try manual flow.** 🚀
