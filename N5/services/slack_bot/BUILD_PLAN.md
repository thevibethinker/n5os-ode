---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# Slack ↔ Zo AI Full Integration Build Plan

## Objective
Enable real-time AI-powered responses from Zo to Slack messages using Zo Computer's internal conversation API.

## Architecture

```
Slack Message → Slack Bot Receiver → Zo AI Bridge → Zo Computer API → AI Response → Slack
```

### Components

1. **Slack Bot Receiver** (✅ EXISTS)
   - Receives webhook events from Slack
   - Validates signatures
   - Authorizes users
   - Calls forwarding function

2. **Zo AI Bridge** (🔨 BUILD)
   - Accepts message from Slack bot
   - Creates/manages conversation with Zo
   - Waits for/retrieves AI response
   - Returns response to Slack bot
   
3. **Response Handler** (🔨 BUILD)
   - Formats AI response for Slack
   - Handles errors gracefully
   - Provides fallbacks

## Implementation Strategy

### Option A: Use Existing Conversation API with Polling
- Start conversation via `/api/converse/start`
- Ask question via `/api/converse/ask`
- Poll `/api/converse/poll/{conv_id}` for response
- **Pro:** Uses existing infrastructure
- **Con:** Polling delay, complexity

### Option B: Direct Subprocess Call to Zo
- Create temporary conversation file
- Execute Zo command directly
- Capture output
- **Pro:** Simpler, more direct
- **Con:** Relies on subprocess execution

### Option C: Internal Zo Python API (if exists)
- Import Zo's internal modules
- Call conversation handler directly
- **Pro:** Most direct, fastest
- **Con:** May not exist/be documented

## Decision: Start with Option B (Subprocess), refactor to C if needed

### Build Steps

1. ✅ Create build plan (this file)
2. 🔨 Build `zo_ai_caller.py` - Subprocess-based Zo caller
3. 🔨 Update `receiver.py` - Integrate new caller
4. 🔨 Add error handling and logging
5. 🔨 Test with real Slack messages
6. 🔨 Document and deploy

## Testing Plan

1. Unit test: zo_ai_caller with simple questions
2. Integration test: Slack bot end-to-end
3. Error scenarios: timeouts, failures, edge cases
4. Load test: Multiple rapid messages

## Success Criteria

- ✅ Slack message → Real AI response (not placeholder)
- ✅ Response time < 30 seconds
- ✅ Error handling graceful
- ✅ Logging comprehensive
- ✅ No crashes or hangs

## Rollback Plan

If build fails, existing placeholder responses continue working.

