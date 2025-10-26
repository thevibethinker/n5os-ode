# Testing the AI-to-AI Conversational API

**Guide for:** Testing the conversation system between parent and demonstrator  
**Status:** Server running on port 8769  
**Version:** 1.0

---

## Quick Test Overview

You'll simulate being both the demonstrator (asking questions) and the parent (answering them) to verify the full conversation flow works.

---

## Method 1: Automated Test Suite (Easiest)

This runs through all scenarios automatically:

```bash
cd /home/workspace
python3 N5/scripts/test_conversation_api.py --url http://localhost:8769
```

**Expected output:**
```
✓ Health check passed
✓ Conversation started
✓ Question asked successfully
✓ Response submitted successfully
✓ Response retrieved
✓ History retrieved: 3 messages
🎉 All tests passed!
```

This validates everything works end-to-end.

---

## Method 2: Manual Testing with Client (Most Realistic)

This simulates what the demonstrator will actually do:

### Step 1: Parent - Start the Server (if not running)

```bash
cd /home/workspace
python3 N5/scripts/n5_bootstrap_conversational_server.py --port 8769 &
```

Check it's healthy:
```bash
curl http://localhost:8769/health
```

### Step 2: Demonstrator - Start a Conversation

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
    --url http://localhost:8769 \
    start \
    --context '{"phase": "phase_2", "current_step": "copying_scripts"}'
```

**Output:**
```json
{
  "conversation_id": "conv_abc123...",
  "status": "started"
}
```

**Save that conversation_id** - you'll need it for the next steps!

### Step 3: Demonstrator - Ask a Question

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
    --url http://localhost:8769 \
    ask \
    --conversation-id "conv_abc123..." \
    --question "What should I do after copying core scripts to N5/scripts?"
```

**Output:**
```json
{
  "status": "question_queued",
  "message": "Question submitted, waiting for parent response"
}
```

### Step 4: Parent - Check for Questions

```bash
# Watch the log file for incoming questions
tail -n 20 /home/workspace/N5/logs/bootstrap_conversations.jsonl
```

Or query directly:
```bash
curl -s "http://localhost:8769/api/converse/poll/conv_abc123..." | python3 -m json.tool
```

You'll see:
```json
{
  "has_response": false,
  "pending_question": true,
  "question": "What should I do after copying core scripts to N5/scripts?"
}
```

### Step 5: Parent - Submit a Response

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
    --url http://localhost:8769 \
    respond \
    --conversation-id "conv_abc123..." \
    --answer "Next, you should update the config files in N5/config/ to point to the new locations."
```

**Output:**
```json
{
  "status": "response_submitted",
  "message": "Response queued for demonstrator"
}
```

### Step 6: Demonstrator - Poll for the Response

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
    --url http://localhost:8769 \
    poll \
    --conversation-id "conv_abc123..."
```

**Output:**
```json
{
  "has_response": true,
  "answer": "Next, you should update the config files in N5/config/ to point to the new locations.",
  "responded_at": "2025-10-19T01:30:00Z"
}
```

### Step 7: View Full Conversation History

```bash
python3 N5/scripts/bootstrap_conversation_client.py \
    --url http://localhost:8769 \
    history \
    --conversation-id "conv_abc123..."
```

**Output:**
```json
[
  {
    "role": "system",
    "content": "Conversation started",
    "timestamp": "..."
  },
  {
    "role": "demonstrator",
    "content": "What should I do after copying core scripts...",
    "timestamp": "..."
  },
  {
    "role": "parent",
    "content": "Next, you should update the config files...",
    "timestamp": "..."
  }
]
```

---

## Method 3: Raw API Calls (Understanding the Protocol)

If you want to understand exactly what's happening under the hood:

### Start Conversation
```bash
curl -X POST http://localhost:8769/api/converse/start \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"phase": "phase_2"}
  }'
```

### Ask Question
```bash
curl -X POST http://localhost:8769/api/converse/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123...",
    "question": "Where should I put the bootstrap scripts?",
    "metadata": {"urgency": "high"}
  }'
```

### Submit Response (Parent)
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123...",
    "answer": "Put them in N5/scripts/bootstrap/",
    "metadata": {"confidence": "high"}
  }'
```

### Poll for Response (Demonstrator)
```bash
curl -s "http://localhost:8769/api/converse/poll/conv_abc123..." | python3 -m json.tool
```

### Get History
```bash
curl -s "http://localhost:8769/api/converse/history/conv_abc123..." | python3 -m json.tool
```

---

## What Demonstrator Will Actually Do

In practice, the demonstrator Zo will use Python code like this:

```python
import requests

# 1. Start conversation
response = requests.post(
    "http://localhost:8769/api/converse/start",
    json={"metadata": {"phase": "phase_2"}}
)
conv_id = response.json()["conversation_id"]

# 2. Ask question
requests.post(
    "http://localhost:8769/api/converse/ask",
    json={
        "conversation_id": conv_id,
        "question": "What's the next step after copying scripts?",
        "metadata": {"step": "script_setup"}
    }
)

# 3. Poll for response (with retry logic)
import time
for attempt in range(30):  # Try for 30 seconds
    response = requests.get(f"http://localhost:8769/api/converse/poll/{conv_id}")
    data = response.json()
    
    if data["has_response"]:
        answer = data["answer"]
        print(f"Parent says: {answer}")
        break
    
    time.sleep(1)  # Wait 1 second between polls
```

The demonstrator can use the provided client library for convenience:

```python
from bootstrap_conversation_client import BootstrapConversationClient

client = BootstrapConversationClient("http://localhost:8769")
conv_id = client.start_conversation(metadata={"phase": "phase_2"})
client.ask_question(conv_id, "What should I do next?")
response = client.poll_for_response(conv_id, max_attempts=30, delay=1.0)
print(f"Parent answered: {response}")
```

---

## Monitoring During Testing

### Watch questions come in (parent perspective):
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | \
  grep '"role": "demonstrator"'
```

### Watch responses go out (parent perspective):
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | \
  grep '"role": "parent"'
```

### See full conversation flow:
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | \
  python3 -c 'import sys, json; [print(f"{json.loads(l)[\"role\"]}: {json.loads(l)[\"content\"]}") for l in sys.stdin]'
```

---

## Troubleshooting Tests

### Server not responding?
```bash
# Check if running
ps aux | grep conversational_server

# Check logs
tail -20 /home/workspace/N5/logs/bootstrap_server.log

# Restart
pkill -f conversational_server
python3 N5/scripts/n5_bootstrap_conversational_server.py --port 8769 &
```

### Can't connect?
```bash
# Verify port is listening
netstat -tlnp | grep 8769

# Test basic connectivity
curl http://localhost:8769/health
```

### Questions not being logged?
```bash
# Check log directory exists
ls -la /home/workspace/N5/logs/

# Check permissions
ls -la /home/workspace/N5/logs/bootstrap_conversations.jsonl
```

---

## Success Criteria

✅ **Automated tests pass** (6/6)  
✅ **Manual question/response cycle works**  
✅ **Conversation history persists**  
✅ **Logs capture all messages**  
✅ **Client library works correctly**  

---

## Next Steps After Testing

Once you've verified everything works:

1. **Package for demonstrator:**
   - Include `bootstrap_conversation_client.py` in bootstrap package
   - Include `INSTRUCTIONS_FOR_DEMONSTRATOR_AI_CONVERSATION.md`
   - Update demonstrator's main instructions to reference conversation capability

2. **Start responding to real questions:**
   - Monitor `/home/workspace/N5/logs/bootstrap_conversations.jsonl`
   - When demonstrator asks questions, submit thoughtful responses
   - Use conversation history to provide context-aware guidance

3. **Iterate based on usage:**
   - Track what questions get asked
   - Update documentation based on patterns
   - Improve response times if needed

---

**Ready to test! Start with Method 1 (automated tests), then try Method 2 for the full experience. 🚀**

*Testing Guide v1.0 | 2025-10-19*
