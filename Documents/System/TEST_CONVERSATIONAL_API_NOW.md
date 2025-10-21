# Test Conversational API Right Now

**Quick test to see it in action**

---

## Option 1: Run Demo Script (Easiest)

This shows the complete flow automatically:

```bash
cd /home/workspace
./N5/scripts/demo_conversation.sh
```

This will:
1. Check server health
2. Start a conversation
3. Ask a question (as demonstrator)
4. Submit an answer (as parent)
5. Poll for the answer (as demonstrator)
6. Show conversation history

**Takes ~10 seconds, shows everything working!**

---

## Option 2: Manual Testing

### Terminal 1: Watch for activity

```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl
```

### Terminal 2: Simulate demonstrator

```bash
cd /home/workspace

# Start conversation
python3 N5/scripts/bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  start

# Copy the conversation_id from output
# Let's say it's: conv_test123
```

```bash
# Ask a question
python3 N5/scripts/bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --conv-id conv_test123 \
  ask "What should I do first in the bootstrap process?"
```

**Now check Terminal 1** - you'll see the question appear!

### Terminal 3: Simulate parent response

```bash
# Respond to the question
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test123",
    "answer": "First, verify the N5 directory structure exists. Run: ls -la N5/"
  }'
```

### Back to Terminal 2: Get the answer

```bash
# Poll for parent's response
python3 N5/scripts/bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --conv-id conv_test123 \
  poll
```

**You should see the parent's answer!**

---

## Option 3: Test From Demonstrator Machine

If you have a demonstrator machine/workspace:

### On Demonstrator:

```bash
# 1. Install dependencies
pip install requests

# 2. Get parent IP (replace with actual IP)
PARENT_IP="192.168.1.100"  # or wherever parent is

# 3. Test connectivity
curl http://$PARENT_IP:8769/health

# 4. Start conversation
python3 scripts/bootstrap_conversation_client.py \
  --url http://$PARENT_IP:8769 \
  start

# 5. Ask question
python3 scripts/bootstrap_conversation_client.py \
  --url http://$PARENT_IP:8769 \
  --conv-id <conv_id> \
  ask "Where should I find the bootstrap documentation?"
```

### On Parent:

```bash
# Watch for question
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl

# When you see the question, respond:
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "<conv_id>",
    "answer": "Bootstrap documentation is in N5/docs/. Start with BOOTSTRAP_GUIDE.md"
  }'
```

### Back on Demonstrator:

```bash
# Get the answer
python3 scripts/bootstrap_conversation_client.py \
  --url http://$PARENT_IP:8769 \
  --conv-id <conv_id> \
  poll
```

---

## What You're Testing

✅ **Server is running** - Health check passes  
✅ **Can start conversations** - Get conversation ID  
✅ **Questions are logged** - Appear in parent's log  
✅ **Responses can be submitted** - Parent can answer  
✅ **Responses are retrieved** - Demonstrator gets answer  
✅ **History is preserved** - Full conversation saved  

---

## Expected Output (Demo Script)

```
======================================================================
AI-to-AI Conversation Demo
======================================================================

Server: http://localhost:8769

[1/6] Health Check
{
    "status": "healthy",
    "service": "N5 Bootstrap Conversational Server",
    "version": "2.0.0",
    ...
}
✓ Server is healthy

======================================================================
[2/6] Starting Conversation (Demonstrator)
{
    "conversation_id": "conv_abc123",
    "message": "Conversation started"
}
✓ Conversation started: conv_abc123

======================================================================
[3/6] Asking Question (Demonstrator)
{
    "message": "Question queued"
}
📩 Demonstrator asked: "What are the key steps in bootstrap phase 1?"

======================================================================
[4/6] Parent Responding
{
    "message": "Response queued"
}
✓ Parent submitted response

======================================================================
[5/6] Demonstrator Polling for Response
{
    "has_response": true,
    "response": "Phase 1 key steps: ...",
    ...
}
✓ Demonstrator received parent's answer!

======================================================================
[6/6] Full Conversation History
{
    "conversation_id": "conv_abc123",
    "message_count": 3,
    "history": [...]
}
✓ Conversation has 3 messages

======================================================================
Demo Complete! 🎉
======================================================================
```

---

## Troubleshooting

### Server not running?

```bash
# Check
ps aux | grep conversational_server

# If not running, start it:
python3 /home/workspace/N5/scripts/n5_bootstrap_conversational_server.py --port 8769 &
```

### Permission errors on log file?

```bash
mkdir -p /home/workspace/N5/logs
chmod 755 /home/workspace/N5/logs
```

### Can't connect from demonstrator?

```bash
# Check firewall/network
ping PARENT_IP
nc -zv PARENT_IP 8769

# From parent, verify server is listening on all interfaces
lsof -i :8769
```

---

## After Testing

If all tests pass, you're ready to:

1. ✅ Include client in bootstrap package
2. ✅ Give demonstrator the INSTRUCTIONS_FOR_DEMONSTRATOR_AI_CONVERSATION.md
3. ✅ Start bootstrap with AI-to-AI communication enabled!

**No human relay needed during bootstrap! 🚀**

---

## Quick Reference

**Run demo:** `./N5/scripts/demo_conversation.sh`  
**Watch logs:** `tail -f N5/logs/bootstrap_conversations.jsonl`  
**Health check:** `curl localhost:8769/health`  
**Full test suite:** `python3 N5/scripts/test_conversation_api.py`

---

**Ready to test! Run the demo script now! ⚡**
