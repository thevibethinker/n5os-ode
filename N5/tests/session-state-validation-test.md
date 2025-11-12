---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.0
---

# SESSION_STATE System Validation Test

**Purpose:** Empirically measure SESSION_STATE initialization reliability and collect telemetry for final validation.

## Test Protocol

### Test 1: Fresh Conversation Initialization (PRIMARY)

**Prompt to use in NEW conversation:**

```
I'm testing the SESSION_STATE initialization system. This is a build conversation about refactoring the notification system to use webhooks instead of polling.

Before responding to this message, please:
1. Execute your P0 initialization protocol
2. Collect and report telemetry using the test framework at: file 'N5/scripts/session_state_telemetry.py'
3. Report all findings

After completing the test, provide a summary with the conversation ID so I can analyze the results.
```

**Expected Behavior:**
- ✅ SESSION_STATE.md should exist BEFORE first response
- ✅ Conversation type classified as "build"
- ✅ Mode inferred from "refactoring notification system"
- ✅ DB sync should complete
- ✅ Conversation ID declared
- ✅ No errors

### Test 2-5: Classification Accuracy

Run 4 more fresh conversations with these prompts:

**Test 2 (Research):**
```
I need to understand how webhook retry strategies work across different platforms like Stripe, GitHub, and Twilio. Help me research and compare their approaches.

Collect SESSION_STATE telemetry before responding.
```

**Test 3 (Discussion):**
```
Let's think through the trade-offs between microservices and monolithic architecture for a startup with a small team. I want to explore this conceptually.

Collect SESSION_STATE telemetry before responding.
```

**Test 4 (Planning):**
```
I need to plan out Q1 2025 roadmap for Careerspan. Help me organize the strategic priorities and create a timeline.

Collect SESSION_STATE telemetry before responding.
```

**Test 5 (Edge Case - Ambiguous):**
```
Hey, quick question about Python asyncio.

Collect SESSION_STATE telemetry before responding.
```

## Telemetry Collection Script

The test will use this automated collector:

