---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.0
---

# SESSION_STATE Validation Test - Simple Protocol

## What You'll Do

Run **5 fresh conversations** with these exact prompts to test SESSION_STATE initialization.

## Test Prompts

### Test 1: Build Conversation
```
I'm testing the SESSION_STATE system. This is a build task: refactor the notification system to use webhooks instead of polling.

Run telemetry collection and report results.
```

### Test 2: Research Conversation  
```
Research webhook retry strategies across Stripe, GitHub, and Twilio. Compare their approaches.

Run telemetry collection and report results.
```

### Test 3: Discussion Conversation
```
Let's discuss the trade-offs between microservices vs monolithic architecture for startups.

Run telemetry collection and report results.
```

### Test 4: Planning Conversation
```
Plan Q1 2025 roadmap for Careerspan with strategic priorities and timeline.

Run telemetry collection and report results.
```

### Test 5: Edge Case (Ambiguous)
```
Quick question about Python asyncio.

Run telemetry collection and report results.
```

## What to Collect

For each conversation, the AI will:
1. Initialize SESSION_STATE (should happen automatically via P0 rule)
2. Run telemetry collection
3. Report results including conversation ID

## Reporting Back

Copy the telemetry output from each test and paste into conversation con_cJgeywufVZ8ICrPB with:

```
Test results from SESSION_STATE validation:

Test 1 (Build): [conversation ID] - [PASS/FAIL] - [success rate]
Test 2 (Research): [conversation ID] - [PASS/FAIL] - [success rate]
Test 3 (Discussion): [conversation ID] - [PASS/FAIL] - [success rate]
Test 4 (Planning): [conversation ID] - [PASS/FAIL] - [success rate]
Test 5 (Edge): [conversation ID] - [PASS/FAIL] - [success rate]

Overall: X/5 conversations passed (Y% success rate)

[Paste any error details or failures]
```

## Success Criteria

**Target:** 4/5 conversations (80%+) should pass all checks

**Pass Criteria per conversation:**
- ✅ SESSION_STATE.md exists
- ✅ Type classified correctly
- ✅ DB sync completed
- ✅ All required sections present
- ✅ No errors

If <80% pass rate, system needs further refinement.
If ≥80% pass rate, system is validated and ready for production.

