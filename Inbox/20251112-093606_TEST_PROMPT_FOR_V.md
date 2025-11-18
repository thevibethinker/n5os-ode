---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.1
---
# 🧪 SESSION_STATE System Validation Test

**What this tests:** Whether the SESSION_STATE initialization system works reliably in fresh conversations.

---

## Quick Instructions

Run **5 new conversations** (one at a time) with the prompts below. Each conversation will auto-test itself and give you a report.

---

## The 5 Test Prompts

Copy each prompt exactly as written into a new conversation.

### 🔨 Test 1: Build Type
```
I need to refactor the webhook notification system. Help me design a modular approach.

After responding, run: python3 /home/workspace/N5/scripts/session_state_telemetry.py <conversation_id>

Show me the full output - don't ask, just do it.
```

### 🔍 Test 2: Research Type
```
Research webhook retry strategies across Stripe, GitHub, and Twilio. Compare their approaches.

After responding, run: python3 /home/workspace/N5/scripts/session_state_telemetry.py <conversation_id>

Show me the full output.
```

### 💬 Test 3: Discussion Type
```
Let's discuss microservices vs monolithic architecture trade-offs for startups.

After responding, run: python3 /home/workspace/N5/scripts/session_state_telemetry.py <conversation_id>

Show me the full output.
```

### 📋 Test 4: Planning Type
```
Plan Q1 2025 roadmap for Careerspan with priorities and timeline.

After responding, run: python3 /home/workspace/N5/scripts/session_state_telemetry.py <conversation_id>

Show me the full output.
```

### ❓ Test 5: Edge Case (Ambiguous)
```
Quick question about Python asyncio.

After responding, run: python3 /home/workspace/N5/scripts/session_state_telemetry.py <conversation_id>

Show me the full output.
```

---

## What to Report Back

After running all 5 tests, bring results back to **conversation con_cJgeywufVZ8ICrPB**.

Format:
```
SESSION_STATE Validation Results:

Test 1 (Build): con_XXXX - [✅ PASS / ❌ FAIL] - X% success
Test 2 (Research): con_XXXX - [✅ PASS / ❌ FAIL] - X% success  
Test 3 (Discussion): con_XXXX - [✅ PASS / ❌ FAIL] - X% success
Test 4 (Planning): con_XXXX - [✅ PASS / ❌ FAIL] - X% success
Test 5 (Edge): con_XXXX - [✅ PASS / ❌ FAIL] - X% success

Overall: X/5 passed (X%)
```

---

## Success Criteria

- **80%+ (4/5)** = System validated ✅
- **60-79% (3/5)** = Minor fixes needed ⚠️  
- **<60% (<3/5)** = Redesign required 🚫

---

**Time: ~30-60 minutes total**

Ready when you are!

