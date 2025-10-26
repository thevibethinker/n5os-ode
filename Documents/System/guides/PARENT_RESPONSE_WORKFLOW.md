# Parent Response Workflow

**Quick guide for responding to demonstrator questions during bootstrap**

---

## Setup (One-Time)

### Terminal 1: Monitor for Questions

```bash
cd /home/workspace
tail -f N5/logs/bootstrap_conversations.jsonl | grep --line-buffered '"role": "demonstrator"'
```

This will show you only demonstrator questions as they arrive.

### Terminal 2: Response Terminal

Keep this open for submitting responses.

---

## When Question Arrives

### Step 1: See the Question

In Terminal 1, you'll see:
```json
{"conversation_id": "conv_abc123", "role": "demonstrator", "content": "What should I do for phase 1?", "timestamp": "...", "metadata": {}}
```

**Copy the `conversation_id`** - you'll need it to respond.

### Step 2: Review Full Context (Optional)

```bash
# See full conversation history
CONV_ID="conv_abc123"
curl http://localhost:8769/api/converse/history/$CONV_ID | python3 -m json.tool
```

This shows all previous Q&A in this conversation.

### Step 3: Formulate Your Answer

Think about what demonstrator needs:
- Clear, actionable guidance
- File paths if relevant
- Next steps
- Context they might be missing

### Step 4: Submit Response

```bash
CONV_ID="conv_abc123"
ANSWER="First, verify the N5 directory structure exists. Run: ls -la N5/. You should see scripts/, docs/, schemas/ directories. If missing, create them with: mkdir -p N5/{scripts,docs,schemas,logs}"

curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"answer\": \"$ANSWER\"}"
```

**Or use this helper script:**

```bash
# Create a quick response helper
cat > /tmp/respond.sh << 'EOF'
#!/bin/bash
CONV_ID="$1"
ANSWER="$2"
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\": \"$CONV_ID\", \"answer\": \"$ANSWER\"}"
echo ""
EOF
chmod +x /tmp/respond.sh

# Use it:
/tmp/respond.sh "conv_abc123" "Your answer here"
```

### Step 5: Verify Delivered

Check that your response was logged:
```bash
tail -2 N5/logs/bootstrap_conversations.jsonl
```

You should see your response with `"role": "parent"`.

---

## Example Workflow

**Terminal 1 shows:**
```
{"conversation_id": "conv_f4d2e", "role": "demonstrator", "content": "I don't see the bootstrap_minimal.py file. Where should it be?", "timestamp": "2025-10-19T01:30:00"}
```

**You in Terminal 2:**
```bash
# Quick response
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_f4d2e",
    "answer": "The bootstrap_minimal.py file should be in /home/workspace/Deliverables/N5_Bootstrap_Minimal_v1.0.0/. If it is not there, you can download it from the bootstrap package. Alternatively, check if it is in your current working directory."
  }'
```

**Result:** Demonstrator gets your answer in ~1 second.

---

## Tips for Good Responses

### Be Specific
❌ "Check the files"  
✅ "Run: `ls -la N5/scripts/` to verify these files exist: n5_safety.py, bootstrap_client.py"

### Provide Commands
❌ "Create the directory"  
✅ "Run: `mkdir -p /home/workspace/N5/scripts`"

### Give Context
❌ "Do phase 2"  
✅ "Phase 2 involves copying core scripts. First verify phase 1 is complete by checking: file N5/docs/N5.md exists"

### Anticipate Follow-ups
Instead of just answering the immediate question, provide related info:
```
"The schema files go in N5/schemas/. You'll need:
- index.schema.json
- knowledge.schema.json  
- lists.schema.json

Copy them from the bootstrap package with:
cp bootstrap_package/schemas/* N5/schemas/"
```

---

## Common Question Categories

### Location Questions
- "Where is file X?"
- "Where should I put Y?"

**Response pattern:** Provide absolute path, verification command, and copy command if applicable.

### Next Step Questions
- "What do I do next?"
- "Is this step complete?"

**Response pattern:** Explain completion criteria for current step, then describe next step with specific actions.

### Error Questions
- "I got error X"
- "This isn't working"

**Response pattern:** Explain cause, provide fix command, suggest verification step.

### Clarification Questions
- "What does X mean?"
- "Why do I need Y?"

**Response pattern:** Brief explanation, connection to bootstrap goals, practical example.

---

## Responding as Parent Zo (AI)

If you're the parent AI and want to automate responses, here's a Python pattern:

```python
import json
import time
import requests
from pathlib import Path

LOG_FILE = Path("/home/workspace/N5/logs/bootstrap_conversations.jsonl")
API_URL = "http://localhost:8769"

def watch_and_respond():
    """Watch for questions and respond automatically"""
    
    # Track processed questions
    processed = set()
    
    with open(LOG_FILE, 'r') as f:
        # Start from current end
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            
            entry = json.loads(line)
            
            # Only process new demonstrator questions
            if entry["role"] != "demonstrator":
                continue
            
            conv_id = entry["conversation_id"]
            question = entry["content"]
            
            # Skip if already answered
            if conv_id in processed:
                continue
            
            # Generate answer (this is where your AI logic goes)
            answer = generate_answer(question, conv_id)
            
            # Submit response
            response = requests.post(f"{API_URL}/api/converse/respond", json={
                "conversation_id": conv_id,
                "answer": answer
            })
            
            if response.ok:
                print(f"✓ Answered: {question[:50]}...")
                processed.add(conv_id)
            else:
                print(f"✗ Failed to respond to {conv_id}")

def generate_answer(question: str, conv_id: str) -> str:
    """Generate answer to demonstrator's question
    
    This is where you'd implement your AI reasoning.
    For now, you can use templates or call your AI.
    """
    
    # Get conversation context
    resp = requests.get(f"{API_URL}/api/converse/history/{conv_id}")
    history = resp.json()["history"]
    
    # Example: Simple keyword matching
    question_lower = question.lower()
    
    if "where" in question_lower and "script" in question_lower:
        return "Scripts should be in /home/workspace/N5/scripts/. Verify with: ls -la N5/scripts/"
    
    if "next" in question_lower or "what do" in question_lower:
        return "Check your current phase in the bootstrap checklist, then proceed to the next uncompleted step."
    
    # Default
    return "I see your question. Let me think about that..."

# Run it
if __name__ == "__main__":
    print("Watching for demonstrator questions...")
    watch_and_respond()
```

---

## Multi-Question Conversations

Demonstrator might ask several questions in the same conversation:

**Question 1:**
```json
{"conversation_id": "conv_xyz", "role": "demonstrator", "content": "Where are schemas?"}
```

**Your Response:**
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -d '{"conversation_id": "conv_xyz", "answer": "Schemas are in N5/schemas/"}'
```

**Question 2 (same conversation):**
```json
{"conversation_id": "conv_xyz", "role": "demonstrator", "content": "Which schemas are required?"}
```

**Your Response:**
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -d '{"conversation_id": "conv_xyz", "answer": "Required: index.schema.json, knowledge.schema.json, lists.schema.json"}'
```

The `conversation_id` stays the same, building conversation context.

---

## Emergency: Demonstrator is Stuck

If demonstrator asks:
```
"I'm completely blocked. Nothing is working."
```

**Your response should be systematic:**
```json
{
  "conversation_id": "...",
  "answer": "Let's debug systematically:
  
1. Verify you're in the workspace: pwd (should show /home/workspace)
2. Check N5 directory exists: ls -la N5
3. Check what files you have: find N5 -type f
4. Check bootstrap phase file: cat N5/.bootstrap_phase 2>/dev/null || echo 'No phase file'
5. Share the output of these commands in your next question.

This will help me understand where you are and what's missing."
}
```

---

## Done!

With this workflow, you can:
- Monitor demonstrator questions in real-time
- Respond quickly with clear guidance
- Build multi-turn conversations
- Debug issues systematically

**Ready to support demonstrator during bootstrap! 🚀**

---

**Workflow Guide v1.0 | 2025-10-19**
