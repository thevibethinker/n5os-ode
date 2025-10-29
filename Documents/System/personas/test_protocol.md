# Persona System Test Protocol

**Version:** 1.0  
**Date:** 2025-10-28  
**Purpose:** Validate Core + Specialist architecture deployment

---

## Quick Validation (5 minutes)

Run these 5 tests in separate messages to confirm auto-activation:

### Test 1: Builder Mode
**Prompt:** "Create a simple Python script that prints 'Hello N5'"  
**Expected:** Operator activates Builder, creates script, doesn't ask which mode  
**Pass criteria:** Script created, Builder activated automatically

### Test 2: Writer Mode
**Prompt:** "Draft a quick email to a colleague saying thanks for the meeting"  
**Expected:** Operator activates Writer, loads voice system, writes email  
**Pass criteria:** Email drafted in your voice, Writer activated

### Test 3: Debugger Mode
**Prompt:** "Verify the squawk log file exists and is properly formatted"  
**Expected:** Operator activates Debugger, checks file, reports status  
**Pass criteria:** Verification complete, Debugger activated

### Test 4: Researcher Mode
**Prompt:** "Research the top 3 Python CLI frameworks"  
**Expected:** Operator activates Researcher, searches, synthesizes findings  
**Pass criteria:** Research delivered with sources, Researcher activated

### Test 5: Strategist Mode
**Prompt:** "Should I use SQLite or PostgreSQL for a personal task tracker? Give me options."  
**Expected:** Operator activates Strategist, provides 2-3 options with tradeoffs  
**Pass criteria:** Options with clear tradeoffs, recommendation, Strategist activated

---

## Pass/Fail Criteria

**PASS if 4/5 tests:**
- Correct mode auto-activated
- No manual "Load X" needed
- Quality output delivered
- Seamless experience

**FAIL if <3/5 tests pass:**
- Log issues to squawk log
- Review signal detection logic
- Check for conflicts in rules

---

## Extended Validation (Optional, 30 minutes)

### Chained Modes Test
**Prompt:** "Research task tracking best practices, evaluate SQLite vs Postgres, then build the winner"  
**Expected:** Researcher → Strategist → Builder (sequential)  
**Pass criteria:** Smooth handoffs, each mode contributes, integrated result

### Ambiguous Signal Test
**Prompt:** "Check the latest architectural principles"  
**Expected:** Operator asks "verify (Debugger) or read/learn (Researcher)?"  
**Pass criteria:** Clarifying question asked, correct mode after answer

### Complex Build Test
**Prompt:** "Build a distributed system for processing emails with workers and orchestrator"  
**Expected:** Builder activates WITH planning prompt loaded  
**Pass criteria:** Think→Plan→Execute followed, planning prompt referenced

### Voice Fidelity Test
**Prompt:** "Write a LinkedIn post about the importance of simplicity in system design"  
**Expected:** Writer loads voice transformation, matches your style metrics  
**Pass criteria:** Sounds like you (warmth, conciseness, hooks), not generic AI

---

## Monitoring (Week 1)

**Daily check:**
```bash
tail -20 /home/workspace/N5/logs/squawk_log.jsonl | jq -r '.description'
```

**Look for:**
- ✅ Pattern: Auto-activations working
- ⚠️ Pattern: Repeated mode mismatches
- 🔴 Pattern: "Mode not activated" errors

**Success metrics (Week 1):**
- 10+ tasks with auto-activation
- <3 manual overrides needed
- <2 activation errors logged
- Feedback: "Just works"

---

## Rollback Plan (If Needed)

**If system fails validation:**

1. **Quick fix:** Add explicit rules for failing patterns
2. **Medium fix:** Adjust signal keywords in Operator
3. **Full rollback:** Revert to standalone personas (v1.x files still exist)

**Rollback command:**
```
Remove vibe_operator_persona.md from Settings → default persona
Use old "Load Vibe X persona" pattern
```

---

## Report Template

After testing, log to squawk log:

```json
{
  "timestamp": "2025-10-29T00:00:00Z",
  "type": "test_report",
  "severity": "info",
  "component": "persona_system",
  "description": "Test protocol results: X/5 quick tests passed, Y issues found",
  "context": "Details: [what worked, what didn't]",
  "conversation": "con_xxx"
}
```

---

**Ready to run Quick Validation? Just start with Test 1 in your next message.**

---

*Test protocol v1.0 | 2025-10-28*
