# Instructions for Demonstrator: AI-to-AI Conversation

**Version:** 2.0 - Enhanced with Conversational API  
**Date:** 2025-10-19  
**For:** Demonstrator Zo in new workspace

---

## What's New: Direct AI-to-AI Communication 🤖↔️🤖

You can now **ask questions directly to parent Zo** and receive AI-generated responses without human relay! This eliminates communication bottlenecks during bootstrap.

---

## Quick Start: Using Conversation API

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Start Conversation

```bash
python3 /path/to/bootstrap_conversation_client.py \
  --server http://PARENT_IP:8769 \
  start --context '{"phase": "bootstrap_init"}'
```

This creates a **conversation_id** that's automatically saved to `.bootstrap_conversation_state.json`

### 3. Ask Questions Anytime

```bash
# Ask and wait for response
python3 /path/to/bootstrap_conversation_client.py \
  --server http://PARENT_IP:8769 \
  ask "What should I do after creating directory structure?" \
  --wait --timeout 60

# Or ask without waiting
python3 /path/to/bootstrap_conversation_client.py \
  --server http://PARENT_IP:8769 \
  ask "Which files go in Knowledge/architectural?"
```

### 4. Poll for Responses

```bash
# Check for responses
python3 /path/to/bootstrap_conversation_client.py \
  --server http://PARENT_IP:8769 \
  poll --timeout 60
```

---

## When to Use Conversational API

### ✅ Use AI-to-AI conversation for:

- **Clarifying instructions** - "What does 'setup conditional rules' mean?"
- **Error diagnosis** - "FileNotFoundError for principles.md, where should it be?"
- **Next steps** - "Phase 2 complete, what's next?"
- **Validation** - "Does my directory structure look correct?"
- **File locations** - "Where does architectural_principles.md go?"

### ❌ Don't use for:

- Fetching file contents (use GET endpoints: `/bootstrap/principles`, etc.)
- Directory structure info (use GET `/bootstrap/structure`)
- Health checks (use GET `/health`)

---

## Bootstrap Flow with Conversations

```
Phase 1: Setup
├─ Create directories
├─ ASK: "Created dirs, verify structure?"
└─ POLL: Get confirmation

Phase 2: Copy Files  
├─ Fetch files from bootstrap server
├─ ASK: "Error copying X, should I skip?"
└─ POLL: Get guidance

Phase 3: Configuration
├─ Setup configs
├─ ASK: "How do I handle missing config values?"
└─ POLL: Get solution

Phase 4: Validation
├─ Run tests
├─ ASK: "All tests pass, ready for production?"
└─ POLL: Get final approval
```

---

## Python Integration Example

```python
import sys
sys.path.append("/path/to/bootstrap_package/scripts")

from bootstrap_conversation_client import BootstrapConversationClient

# Initialize
client = BootstrapConversationClient("http://PARENT_IP:8769")
client.start_conversation({"phase": "phase_2"})

# During bootstrap, ask questions as needed
def bootstrap_phase_2():
    try:
        # Do work...
        copy_files()
    except FileNotFoundError as e:
        # Ask parent for help
        client.ask_question(
            f"FileNotFoundError: {e}. Which directory should this file be in?",
            metadata={"error_type": "FileNotFoundError", "phase": "phase_2"}
        )
        
        # Wait for response
        answer = client.poll_for_response(timeout=60)
        
        if answer:
            print(f"Parent guidance: {answer}")
            # Follow guidance...
        else:
            print("No response, checking logs...")
```

---

## Response Patterns

### Expected Response Times

- **Simple questions** (file locations, next steps): 10-30 seconds
- **Complex questions** (error diagnosis, strategy): 30-60 seconds
- **No response after 60s**: Check connection, retry

### Polling Best Practices

```python
# Good: Poll with reasonable interval
for i in range(12):  # 60 seconds total
    response = poll()
    if response:
        break
    time.sleep(5)

# Bad: Continuous polling
while True:
    response = poll()  # Too aggressive
```

---

## Conversation Log

All conversations are logged at:
`/home/workspace/N5/logs/bootstrap_conversations.jsonl`

Parent Zo monitors this log and responds to questions.

**Log format:**
```json
{
  "conversation_id": "conv_abc123",
  "timestamp": "2025-10-19T01:30:00Z",
  "role": "demonstrator",
  "content": "What's next after phase 2?",
  "metadata": {"phase": "phase_2"}
}
```

---

## Troubleshooting

### Connection Refused

```bash
# Test connection
curl http://PARENT_IP:8769/health

# If fails, check:
# 1. Server is running
# 2. IP address is correct
# 3. Port 8769 is accessible
```

### No Response After 60s

1. **Check conversation history:**
   ```bash
   python3 bootstrap_conversation_client.py \
     --server http://PARENT_IP:8769 history
   ```

2. **Verify question was received:**
   - Check if question appears in history
   - If not, retry asking

3. **Parent may be busy:**
   - Wait longer (try 120s timeout)
   - Ask simpler, more specific question

### Invalid Conversation ID

```bash
# State file corrupted, restart conversation
rm .bootstrap_conversation_state.json

python3 bootstrap_conversation_client.py \
  --server http://PARENT_IP:8769 \
  start
```

---

## API Reference

See full documentation: `file 'N5/docs/AI_TO_AI_CONVERSATION_GUIDE.md'`

**Key endpoints:**
- `POST /api/converse/start` - Start conversation
- `POST /api/converse/ask` - Ask question
- `GET /api/converse/poll/{id}` - Poll for response  
- `GET /api/converse/history/{id}` - Get history

---

## Example Conversation Session

```bash
# Session start
$ python3 client.py --server http://10.0.0.5:8769 start
Conversation ID: conv_f3a2b9c8

# Phase 2: Copying files
$ python3 client.py --server http://10.0.0.5:8769 \
  ask "I'm in phase 2. Which files should I copy first?" --wait

Answer: Start with core scripts from N5/scripts/. Copy in this order:
1. n5_safety.py (validation)
2. session_state_manager.py (state tracking)
3. spawn_worker.py (parallel execution)

# Later in Phase 2
$ python3 client.py --server http://10.0.0.5:8769 \
  ask "FileNotFoundError for architectural_principles.md. Where is it?"

$ python3 client.py --server http://10.0.0.5:8769 poll --timeout 60

Answer: That file is at Knowledge/architectural/architectural_principles.md
You can fetch it via GET /bootstrap/principles endpoint.

# Phase 3: Validation
$ python3 client.py --server http://10.0.0.5:8769 \
  ask "All files copied. Should I run validation now?" --wait

Answer: Yes. Run validation: python3 N5/scripts/n5_safety.py --check-all
Report any failures here.
```

---

## Benefits of AI-to-AI Communication

✅ **No human relay** - Direct AI-to-AI conversation  
✅ **Real-time guidance** - Get answers during execution  
✅ **Context-aware** - Parent sees full bootstrap state  
✅ **Persistent** - All conversations logged for debugging  
✅ **Async** - Don't block on responses, continue work  

---

**You're now equipped for bidirectional AI-to-AI communication during bootstrap! 🚀**

*Questions? Just ask via the conversation API!*
