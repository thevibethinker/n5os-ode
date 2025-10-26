# Zo Internal LLM Pattern

**Pattern for N5 scripts to request LLM decisions from Zo**

---

## Architecture

Instead of calling external LLM APIs, scripts request intelligence from Zo (the executing assistant) via a simple file-based RPC mechanism.

### How It Works

```
Python Script (running in scheduled task)
    ↓
Writes prompt to: /home/workspace/N5/.llm_requests/{req_id}.request.json
    ↓
Polls for: /home/workspace/N5/.llm_requests/{req_id}.response.txt
    ↓
Zo (executing the scheduled task) monitors for requests
    ↓
Zo reads request, generates response, writes response file
    ↓
Script reads response and continues execution
```

### Benefits

- ✅ No external API keys needed
- ✅ No cost (uses Zo's default model)
- ✅ Faster (no network latency)
- ✅ More context-aware (Zo has full system context)
- ✅ Auditable (all requests/responses logged)

---

## Usage in Scripts

```python
from helpers.llm_helper import call_llm

# Request LLM decision
response = call_llm(
    prompt="Is meeting A a duplicate of meeting B?",
    timeout=20  # seconds
)

if response:
    # Parse and use response
    print(f"LLM said: {response}")
else:
    # Fallback to heuristics
    print("LLM unavailable, using heuristics")
```

---

## Scheduled Task Integration

When a scheduled task runs scripts that may need LLM help:

### 1. Before Running Script

```python
# Check for pending LLM requests from previous runs
python3 N5/scripts/helpers/llm_request_handler.py
```

If pending requests found, Zo responds to them before proceeding.

### 2. Run Main Script

```bash
python3 N5/scripts/n5_meeting_transcript_scanner.py
```

Script may create LLM requests during execution.

### 3. After Script Completes

```python
# Check if script created any LLM requests
python3 N5/scripts/helpers/llm_request_handler.py
```

If requests found, Zo responds to them.

### 4. Optional: Re-run Script

If LLM requests were processed, optionally re-run the script so it can use the responses.

---

## Scheduled Task Template

```
STEP 1: Check and respond to any pending LLM requests
Run: python3 /home/workspace/N5/scripts/helpers/llm_request_handler.py

If output shows pending requests:
  - Read each request prompt
  - Generate appropriate response
  - Write response to the specified response file
  - Continue to next step

STEP 2: Run main script
Run: python3 /home/workspace/N5/scripts/[main_script].py

STEP 3: Check for new LLM requests created during execution  
Run: python3 /home/workspace/N5/scripts/helpers/llm_request_handler.py

If output shows new requests:
  - Read each request prompt  
  - Generate appropriate response
  - Write response to the specified response file
  - Optionally re-run main script to use responses

STEP 4: Report results
[normal task output]
```

---

## Example: Meeting Deduplication

**Script creates request:**
```json
{
  "request_id": "req_20251026_123456_789012",
  "prompt": "Is 'Sam Partnership Call-transcript-17:32' a duplicate of existing '2025-10-24_external-sam'?",
  "timestamp": "2025-10-26T12:34:56Z",
  "timeout": 20
}
```

**Zo LLM responds:**
```
IS_DUPLICATE: yes
MATCHING_ID: 2025-10-24_external-sam-partnership-discovery-call  
REASON: Same date and participants, only timestamp differs
```

**Script parses response and skips duplicate.**

---

## Files

- `/home/workspace/N5/scripts/helpers/llm_helper.py` - Client library
- `/home/workspace/N5/scripts/helpers/llm_request_handler.py` - Request monitor
- `/home/workspace/N5/.llm_requests/` - Request/response directory

---

## Monitoring

**Check for stuck requests:**
```bash
ls -lh /home/workspace/N5/.llm_requests/
```

**Manual cleanup:**
```bash
rm /home/workspace/N5/.llm_requests/*.request.json
rm /home/workspace/N5/.llm_requests/*.response.txt
```

---

**Pattern Status**: Implemented and ready for use.
