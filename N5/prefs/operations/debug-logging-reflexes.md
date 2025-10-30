# Debug Logging Reflexes for Vibe Operator

**Version:** 1.0  
**Created:** 2025-10-29  
**Integrated with:** Vibe Operator persona  
**Purpose:** Auto-detect circular debugging, maintain situational awareness

---

## Core Reflexes

### Reflex 1: Log Significant Attempts

**Trigger:** After attempting to fix a problem in build/debug conversation

**Conditions:**
- Conversation type is `build` or `debug`
- Made specific hypothesis + took action
- Got definitive outcome (success/failure/partial)

**Action:**
```python
from debug_logger import DebugLogger
logger = DebugLogger(current_convo_id)
logger.append(
    component="<file/module>",
    problem="<what's wrong>",
    hypothesis="<what we tried>",
    actions=["<step 1>", "<step 2>"],
    outcome="success|failure|partial",
    notes="<learnings>"
)
```

**Don't log:**
- Research/exploration (no hypothesis yet)
- Simple verification checks
- Non-debugging activities

---

### Reflex 2: Check Patterns After 3rd Failure

**Trigger:** 3rd consecutive failure on same component

**Action:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id <current> \
  --window 10 \
  --threshold 3
```

**If circular detected:**
1. Display warning to self (internal awareness)
2. Review recent attempts: `debug_logger.py recent --n 5`
3. **Decision tree:**
   - Same approach 3 times? → Try fundamentally different angle
   - Complex system? → Activate Debugger mode WITH planning prompt
   - Out of ideas? → Escalate to V with 3+ attempts documented

**Example internal monologue:**
```
⚠️ Pattern detected: 3 similar failures on api_client.py

Recent attempts:
1. Increased timeout → failed (timeout wasn't issue)
2. Added delay → failed (rate limit still hit)
3. Increased delay → failed (still hitting limit)

Analysis: All attempts are variations of "slow down requests"
New angle needed: Exponential backoff on retry, not just delay
```

---

### Reflex 3: Review Before 4th Attempt

**Trigger:** About to try 4th approach on same component

**Action:**
1. **STOP** - Don't immediately try approach 4
2. **Review:** `debug_logger.py recent --n 5 --format display`
3. **Analyze:**
   - What patterns do I see?
   - Am I varying the approach or just parameters?
   - Have I considered root cause vs symptoms?
   - Should I activate Debugger mode?
4. **Decide:** Continue with fresh approach OR mode shift OR escalate

**Anti-pattern:** Blindly trying 4th, 5th, 6th approaches without reflection

---

### Reflex 4: Extract Learnings on Success

**Trigger:** Success after ≥3 failures

**Action:**
1. Log success with detailed notes
2. Document what breakthrough insight led to solution
3. Consider if pattern should be added to N5 knowledge base

**Example:**
```bash
python3 debug_logger.py append --convo-id con_ABC \
  --component "api_client.py" \
  --problem "Rate limit 429" \
  --hypothesis "Exponential backoff on retry" \
  --actions "Implemented backoff decorator" "5s, 15s, 45s" \
  --outcome success \
  --notes "KEY LEARNING: Rate limits need backoff on retry, not just delays between requests. Simple sleep() doesn't handle bursty failures."
```

---

## Integration with Mode System

### When to Activate Debugger Mode

**Criteria:**
1. Circular pattern detected (3+ similar failures)
2. Complex system with unclear root cause
3. 5+ total attempts without progress
4. V explicitly requests systematic verification

**Handoff:**
```markdown
**Activating Debugger Mode**

**Objective:** Systematic root cause analysis for [component]
**Scope:** [boundaries]
**Success:** Root cause identified, fix verified, no regression
**Context:** file 'DEBUG_LOG.jsonl' shows [N] attempts with circular pattern
**Planning:** Yes (need structured Think→Plan→Verify approach)
```

---

## Squawk Log Integration

### When to Escalate to Squawk Log

**Criteria:**
- Same problem across multiple conversations (cross-conversation pattern)
- Systemic issue (not one-off debugging)
- Affects N5 infrastructure/scripts
- Requires architectural decision

**Action:**
```bash
# After identifying systemic issue from DEBUG_LOG patterns
python3 /home/workspace/N5/scripts/squawk_log_manager.py add \
  --type pattern \
  --severity medium \
  --component "api_client.py" \
  --description "Rate limit handling pattern: requires exponential backoff, not simple delays" \
  --workaround "Use backoff decorator" \
  --root-cause known \
  --conv <current>
```

---

## Conversation Type Detection

### Auto-Enable Debug Logging

**Enabled for:**
- `type: build`
- `type: debug` (if we add this type)
- Detected build keywords in session_state classification

**Not enabled for:**
- `type: research`
- `type: discussion`
- `type: planning`

**Implementation:**
Check `SESSION_STATE.md` → if type=build, assume debug logging active

---

## Example Workflow

**Debugging Session:**

```
[Initial attempt]
Operator: Trying approach A
→ Failed
→ Log entry: component=X, hypothesis=A, outcome=failure

[2nd attempt]
Operator: Trying approach B
→ Failed
→ Log entry: component=X, hypothesis=B, outcome=failure

[3rd attempt - AUTO CHECK]
Operator: Before trying C, checking patterns...
→ Run: debug_logger.py patterns
→ Result: ⚠️ 2 similar failures detected
→ Internal: Review recent, am I varying approach enough?
→ Decision: Try fundamentally different angle (not parameter tweak)

[3rd attempt executed]
Operator: Trying approach C (different paradigm)
→ Success!
→ Log entry: outcome=success, notes="Key insight: [X]"
```

---

## Self-Check Questions

Before logging:
- [ ] Is this a significant debugging attempt? (hypothesis + action + outcome)
- [ ] Do I have a clear outcome? (not "trying..." but "tried and X happened")
- [ ] Did I capture the key learning in notes?

After 3rd failure:
- [ ] Did I check for patterns?
- [ ] Am I varying approach or just parameters?
- [ ] Should I activate Debugger mode?
- [ ] Have I documented all 3 attempts for V if escalating?

On success after failures:
- [ ] Did I capture what breakthrough led to success?
- [ ] Is this pattern reusable? (add to knowledge base?)

---

## Commands Quick Reference

```bash
# Log attempt
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <id> --component <name> --problem <desc> \
  --hypothesis <guess> --actions <a1> <a2> --outcome <result> \
  --notes <learning>

# Check recent
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id <id> --n 5 --format display

# Detect patterns
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id <id> --window 10 --threshold 3
```

---

**Status:** Active reflexes for Vibe Operator  
**Load:** Automatically in build/debug conversations  
**Recipe:** `file 'Recipes/Debug Log.md'` for usage guide  
**Documentation:** `file 'Knowledge/systems/debug-logging.md'` for system details

*Created: 2025-10-29T04:03 ET*
