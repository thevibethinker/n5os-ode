# AI-to-AI Conversation Guide

**For:** N5 Bootstrap Demonstrator\
**Purpose:** Enable direct conversation between demonstrator Zo and parent Zo\
**Version:** 1.0

---

## Overview

The conversational API allows demonstrator Zo to ask questions and receive AI-generated responses from parent Zo during bootstrap, eliminating the need for human relay.

**Architecture:**

- **Demonstrator Zo** (new workspace) → asks questions via API
- **Conversational Server** (parent workspace) → routes and queues messages
- **Parent Zo** → monitors and responds to questions

---

## Quick Start

### 1. Start Conversation

```bash
curl -X POST http://PARENT_IP:8769/api/converse/start \
  -H "Content-Type: application/json" \
  -d '{
    "initiator": "demonstrator_zo",
    "context": {
      "phase": "bootstrap_phase_2",
      "workspace": "/home/workspace"
    }
  }'
```

**Response:**

```json
{
  "conversation_id": "conv_abc123def456",
  "status": "started",
  "poll_endpoint": "/api/converse/poll/conv_abc123def456"
}
```

**Save the conversation_id** - you'll need it for all subsequent requests.

---

### 2. Ask Question

```bash
curl -X POST http://PARENT_IP:8769/api/converse/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123def456",
    "question": "I encountered FileNotFoundError for architectural_principles.md. Which directory should this be in?",
    "metadata": {
      "error_type": "FileNotFoundError",
      "current_phase": "phase_2"
    }
  }'
```

**Response:**

```json
{
  "status": "received",
  "conversation_id": "conv_abc123def456",
  "message": "Question logged. Parent Zo will respond."
}
```

---

### 3. Poll for Response

```bash
curl http://PARENT_IP:8769/api/converse/poll/conv_abc123def456
```

**Response (when answer available):**

```json
{
  "status": "response_available",
  "conversation_id": "conv_abc123def456",
  "timestamp": "2025-10-19T01:30:00Z",
  "response": "The architectural_principles.md file should be in Knowledge/architectural/. You can fetch it via GET /bootstrap/principles endpoint.",
  "metadata": {}
}
```

**Response (no answer yet):**

```json
{
  "status": "no_response",
  "conversation_id": "conv_abc123def456",
  "message": "No pending responses"
}
```

---

## Conversation Flow

```markdown
1. Demonstrator starts conversation
   → Server creates conversation_id
   
2. Demonstrator asks question
   → Server logs question
   → Parent Zo sees question in logs
   
3. Parent Zo reviews conversation history
   → GET /api/converse/history/{conv_id}
   
4. Parent Zo submits response
   → POST /api/converse/respond
   → Server queues response
   
5. Demonstrator polls for response
   → GET /api/converse/poll/{conv_id}
   → Receives answer
   
6. Repeat steps 2-5 as needed
```

---

## API Endpoints

### POST /api/converse/start

Start new conversation

**Request:**

```json
{
  "initiator": "string",
  "context": {}
}
```

**Response:** `{ conversation_id, status, poll_endpoint }`

---

### POST /api/converse/ask

Ask question to parent Zo

**Request:**

```json
{
  "conversation_id": "string",
  "question": "string",
  "metadata": {}
}
```

**Response:** `{ status, conversation_id, message }`

---

### GET /api/converse/poll/{conv_id}

Poll for pending responses

**Response:**

- `{ status: "response_available", response, timestamp }`
- `{ status: "no_response", message }`

---

### GET /api/converse/history/{conv_id}

Get full conversation history

**Response:**

```json
{
  "conversation_id": "string",
  "message_count": 5,
  "history": [
    {
      "timestamp": "...",
      "role": "demonstrator|parent",
      "content": "...",
      "metadata": {}
    }
  ]
}
```

---

### POST /api/converse/respond

Submit response (parent Zo only)

**Request:**

```json
{
  "conversation_id": "string",
  "answer": "string",
  "metadata": {}
}
```

**Response:** `{ status: "queued" }`

---

## Python Example (Demonstrator)

```python
import requests
import time

BASE_URL = "http://PARENT_IP:8769"

# Start conversation
response = requests.post(f"{BASE_URL}/api/converse/start", json={
    "initiator": "demonstrator_zo",
    "context": {"phase": "bootstrap_phase_2"}
})
conv_id = response.json()["conversation_id"]

# Ask question
requests.post(f"{BASE_URL}/api/converse/ask", json={
    "conversation_id": conv_id,
    "question": "What should I do after creating directory structure?"
})

# Poll for response (with retry)
for attempt in range(10):
    response = requests.get(f"{BASE_URL}/api/converse/poll/{conv_id}")
    data = response.json()
    
    if data["status"] == "response_available":
        print(f"Parent response: {data['response']}")
        break
    
    time.sleep(5)  # Wait 5 seconds before next poll
```

---

## Python Example (Parent Zo)

```python
import requests

BASE_URL = "http://localhost:8769"
conv_id = "conv_abc123def456"

# Get conversation history
response = requests.get(f"{BASE_URL}/api/converse/history/{conv_id}")
history = response.json()["history"]

# Find unanswered questions
for msg in history:
    if msg["role"] == "demonstrator":
        question = msg["content"]
        # Generate answer...
        answer = "Here's the answer..."
        
        # Submit response
        requests.post(f"{BASE_URL}/api/converse/respond", json={
            "conversation_id": conv_id,
            "answer": answer
        })
```

---

## Best Practices

### For Demonstrator Zo:

1. **Include context** in questions (phase, error messages, what you tried)
2. **Poll periodically** (every 5-10 seconds) rather than continuously
3. **Track conversation_id** - save it to a file for reference
4. **Use metadata** to provide structured context (error types, file paths)

### For Parent Zo:

1. **Monitor logs** for new questions: `tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl`
2. **Check history** before responding to understand full context
3. **Provide actionable answers** with specific commands or file paths
4. **Use metadata** to categorize response types (error_fix, guidance, validation)

---

## Troubleshooting

### "Conversation not found"

- Check conversation_id is correct
- Verify conversation was started successfully
- Server may have restarted (conversations are in-memory)

### "No response available"

- Parent hasn't responded yet
- Continue polling every 5-10 seconds
- Check conversation history to confirm question was logged

### Connection refused

- Verify server is running: `curl http://PARENT_IP:8769/health`
- Check firewall/network connectivity
- Confirm port 8769 is correct

---

## Logging

All conversations are logged to:\
`file N5/logs/bootstrap_conversations.jsonl` 

Each line is a JSON object:

```json
{
  "conversation_id": "conv_...",
  "timestamp": "...",
  "role": "demonstrator|parent",
  "content": "...",
  "metadata": {}
}
```

Use this for debugging and reviewing conversation history after bootstrap.

---

**Ready to converse AI-to-AI! 🤖↔️🤖**