# Conversational API Testing Guide

**Purpose:** Step-by-step guide to test AI-to-AI conversation system  
**Audience:** Parent Zo preparing for Mobius Maneuver

---

## Quick Test (Right Now - Single Machine)

You can test the full flow on your current machine by simulating both parent and demonstrator:

### Step 1: Verify Server is Running

```bash
curl http://localhost:8769/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "N5 Bootstrap Conversational Server",
  "version": "2.0.0",
  "features": ["read-only guidance", "ai-to-ai conversation"]
}
```

### Step 2: Open Two Terminal Windows

**Terminal 1 (Parent Monitor):**
```bash
# Watch for demonstrator questions in real-time
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl
```

**Terminal 2 (Simulated Demonstrator):**
```bash
# Navigate to scripts
cd /home/workspace/N5/scripts
```

### Step 3: Simulate Demonstrator Asking Question

**In Terminal 2 (Demonstrator):**
```bash
# Start a conversation
python3 bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --action start \
  --metadata '{"phase": "bootstrap_test"}'
```

**Expected output:**
```
Conversation started: conv_abc123xyz
```

**Save that conversation ID!** You'll need it for the next steps.

### Step 4: Demonstrator Asks Question

**In Terminal 2:**
```bash
# Replace conv_abc123xyz with your actual ID from step 3
export CONV_ID=conv_abc123xyz

python3 bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --action ask \
  --conversation-id $CONV_ID \
  --question "What is the first step in phase 2 of bootstrap?" \
  --metadata '{"urgency": "high"}'
```

**Expected output:**
```
Question sent successfully
Conversation ID: conv_abc123xyz
```

**In Terminal 1 (Parent Monitor):** You should see:
```json
{"conversation_id": "conv_abc123xyz", "timestamp": "...", "role": "demonstrator", "content": "What is the first step in phase 2 of bootstrap?", "metadata": {"urgency": "high"}}
```

### Step 5: Parent Submits Answer

Now you (parent) respond. In a **third terminal** or Terminal 2:

```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123xyz",
    "answer": "The first step in phase 2 is to copy core N5 scripts to N5/scripts/ directory using rsync with --checksum flag.",
    "metadata": {"confidence": "high"}
  }'
```

**Expected output:**
```json
{"status": "success", "conversation_id": "conv_abc123xyz"}
```

### Step 6: Demonstrator Polls for Response

**In Terminal 2:**
```bash
python3 bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --action poll \
  --conversation-id $CONV_ID
```

**Expected output:**
```
Response received:
The first step in phase 2 is to copy core N5 scripts to N5/scripts/ directory using rsync with --checksum flag.

Metadata: {'confidence': 'high'}
```

### Step 7: View Full Conversation History

**Either terminal:**
```bash
python3 bootstrap_conversation_client.py \
  --url http://localhost:8769 \
  --action history \
  --conversation-id $CONV_ID
```

**Expected output:**
```json
[
  {
    "role": "system",
    "content": "Conversation started",
    "timestamp": "2025-10-19T01:30:00.000Z"
  },
  {
    "role": "demonstrator",
    "content": "What is the first step in phase 2 of bootstrap?",
    "timestamp": "2025-10-19T01:30:15.000Z"
  },
  {
    "role": "parent",
    "content": "The first step in phase 2 is to copy core N5 scripts...",
    "timestamp": "2025-10-19T01:30:45.000Z"
  }
]
```

---

## Full Flow Test (Simpler Version)

Run the automated test suite:

```bash
python3 /home/workspace/N5/scripts/test_conversation_api.py \
  --url http://localhost:8769
```

This tests all endpoints automatically. Expected: **6/6 tests pass**.

---

## Actual Demonstrator Usage (During Real Bootstrap)

### What Demonstrator Needs

**Files to include in bootstrap package:**
1. `bootstrap_conversation_client.py` - Client script
2. `INSTRUCTIONS_FOR_DEMONSTRATOR_AI_CONVERSATION.md` - Usage guide
3. `AI_TO_AI_CONVERSATION_GUIDE.md` - API reference

**Installation on demonstrator:**
```bash
pip install requests
```

### Demonstrator Workflow

**1. At Bootstrap Start:**
```bash
# Demonstrator sets parent IP (you'll provide this)
export PARENT_IP="192.168.1.100"  # Replace with actual IP
export PARENT_PORT="8769"
export BOOTSTRAP_API="http://${PARENT_IP}:${PARENT_PORT}"

# Test connectivity
curl $BOOTSTRAP_API/health

# Start conversation for this bootstrap session
python3 scripts/bootstrap_conversation_client.py \
  --url $BOOTSTRAP_API \
  --action start \
  --metadata '{"bootstrap_version": "1.0", "phase": "initialization"}'

# Save conversation ID
export CONV_ID=<returned_id>
```

**2. When Demonstrator Has Question:**
```bash
python3 scripts/bootstrap_conversation_client.py \
  --url $BOOTSTRAP_API \
  --action ask \
  --conversation-id $CONV_ID \
  --question "Should I create N5/scripts first or N5/lists first?" \
  --metadata '{"current_step": "phase_2_setup"}'
```

**3. Poll for Your Answer:**
```bash
# Demonstrator polls (could retry with backoff)
python3 scripts/bootstrap_conversation_client.py \
  --url $BOOTSTRAP_API \
  --action poll \
  --conversation-id $CONV_ID
```

**4. Continue Based on Answer:**
Demonstrator proceeds with the guidance received.

---

## What YOU Do During Actual Bootstrap

### Setup Before Bootstrap

1. **Start the server:**
```bash
nohup python3 /home/workspace/N5/scripts/n5_bootstrap_conversational_server.py \
  --port 8769 > /tmp/conv_server.log 2>&1 &
```

2. **Open monitoring terminal:**
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | \
  grep --line-buffered '"role": "demonstrator"' | \
  jq '.content'
```

3. **Prepare response terminal** with this helper function:
```bash
# Add to your shell session
respond() {
  local conv_id=$1
  local answer=$2
  curl -X POST http://localhost:8769/api/converse/respond \
    -H "Content-Type: application/json" \
    -d "{\"conversation_id\": \"$conv_id\", \"answer\": \"$answer\"}"
}

# Usage: respond "conv_abc123" "Your answer here"
```

### During Bootstrap

1. **Watch monitor terminal** for demonstrator questions
2. **When question appears**, note the conversation ID
3. **Review context:**
   ```bash
   curl http://localhost:8769/api/converse/history/conv_abc123 | jq
   ```
4. **Submit response:**
   ```bash
   respond "conv_abc123" "Copy N5/scripts first, then create lists. Use rsync -av --checksum from bootstrap package."
   ```
5. **Verify delivery** (should see response in log)

---

## Testing Checklist

### Pre-Bootstrap Test

- [ ] Server health check passes
- [ ] Can start conversation
- [ ] Can ask question
- [ ] Question appears in log
- [ ] Can submit response
- [ ] Can poll and receive response
- [ ] Full history retrieval works
- [ ] Network accessible from planned demonstrator location

### Integration Test

- [ ] Demonstrator machine can reach parent IP:8769
- [ ] Firewall allows port 8769
- [ ] Client script works from demonstrator machine
- [ ] End-to-end question/answer cycle completes
- [ ] Responses are actionable and helpful

### Stress Test (Optional)

```bash
# Multiple conversations
for i in {1..5}; do
  python3 test_conversation_api.py --url http://localhost:8769
done
```

---

## Troubleshooting

### Server Not Responding

```bash
# Check if running
ps aux | grep conversational_server

# Check port
lsof -i :8769

# Restart
pkill -f conversational_server
python3 N5/scripts/n5_bootstrap_conversational_server.py --port 8769 &

# Check logs
tail -20 /tmp/conv_server.log
```

### Demonstrator Can't Connect

```bash
# On parent: Check if port is open
netstat -tuln | grep 8769

# On demonstrator: Test connectivity
nc -zv PARENT_IP 8769
curl http://PARENT_IP:8769/health

# Check firewall (parent)
iptables -L -n | grep 8769
```

### Response Not Received

```bash
# Check if response was actually submitted
grep "conv_abc123" /home/workspace/N5/logs/bootstrap_conversations.jsonl | grep '"role": "parent"'

# Verify conversation ID matches
curl http://localhost:8769/api/converse/history/conv_abc123 | jq '.[-1]'
```

---

## Quick Reference Commands

**Start monitoring:**
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | grep --color demonstrator
```

**Submit response (quick):**
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "CONV_ID", "answer": "YOUR_ANSWER"}'
```

**Check conversation:**
```bash
curl http://localhost:8769/api/converse/history/CONV_ID | jq
```

**Get all questions from a conversation:**
```bash
curl -s http://localhost:8769/api/converse/history/CONV_ID | \
  jq '[.[] | select(.role == "demonstrator") | .content]'
```

---

## Expected Timeline

**Test conversation (single Q&A):**
- Start: instant
- Ask: instant  
- Parent sees: <1 second
- Parent responds: 10-30 seconds (thinking time)
- Demonstrator polls: 1-2 seconds
- **Total: ~15-35 seconds**

**Real bootstrap conversation:**
- Question complexity varies
- Parent may need to check context
- Typical: 30 seconds - 2 minutes per Q&A
- Still 10-30x faster than human relay!

---

## Success Criteria

✅ **System works** if:
1. Questions appear in parent log within 1 second
2. Responses reach demonstrator within 1 second of submission
3. History is preserved correctly
4. No lost messages
5. Demonstrator can continue work based on answers

✅ **Ready for production** if:
1. All automated tests pass (6/6)
2. Manual end-to-end test succeeds
3. Network connectivity confirmed
4. Parent can monitor and respond comfortably
5. Demonstrator documentation is clear

---

**You're ready to test! Start with the "Quick Test" section above.** 🚀

*Testing Guide v1.0 | 2025-10-19*
