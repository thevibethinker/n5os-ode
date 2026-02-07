# Debug Logging Auto-Behavior

**Version:** 1.2  
**Updated:** 2026-02-07  
**Purpose:** Explicit reflexes for USING debug log during problem-solving

---

## CRITICAL: Log While Working, Not After

**The Problem:** Building the tool isn't enough - must USE it reflexively during debugging.

**The Solution:** Explicit triggers for logging attempts in real-time.

---

## When to Log (Explicit Triggers)

### Trigger 1: After Attempting a Fix

**When:**
- You tried to fix something
- You ran a command/made a change
- You're about to check if it worked

**Action:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "<what you're fixing>" \
  --problem "<what's wrong>" \
  --hypothesis "<what you think will fix it>" \
  --actions "<what you just did>" \
  --outcome <success|failure|partial> \
  --skill-phase "<root_cause|pattern|hypothesis|implementation>" \
  --notes "<any insights>"
```

### Trigger 2: Before 3rd Attempt on Same Problem

**When:**
- This is the 2nd or 3rd time trying to fix the same issue
- Previous attempt failed

**Action:**
1. Log the current attempt (as above)
2. Check for circular patterns:
```bash
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id <current> --window 10 --threshold 2
```
3. If pattern detected → Stop and analyze OR switch to Vibe Debugger persona

### Trigger 3: When Stuck/Confused

**When:**
- You're not sure what's wrong
- Multiple things tried, none worked
- Root cause unclear

**Action:**
1. Log what you know so far (outcome: partial)
2. Review recent attempts:
```bash
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id <current> --n 5 --format display
```
3. Synthesize pattern from recent attempts
4. Consider switching to Vibe Debugger persona with planning

### Trigger 4: Prompt Execution Attempts

**When:**
- Executing a workflow prompt from Prompts/
- Prompt encounters errors or missing dependencies
- Prompt workflow doesn't complete as expected

**Action:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "prompt:<prompt_name>" \
  --problem "<what failed in prompt execution>" \
  --hypothesis "<expected vs actual behavior>" \
  --actions "<what steps completed before failure>" \
  --outcome <failure|partial> \
  --skill-phase "<root_cause|pattern|hypothesis|implementation>" \
  --notes "<missing deps, config issues, etc>"
```

**Example:**
```bash
# Failed prompt execution
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id con_xyz123 \
  --component "prompt:drive_meeting_ingestion" \
  --problem "Tool call did not complete when reading prompt file" \
  --hypothesis "Prompt file should be readable but tool errored" \
  --actions "Called read_file on Prompts/drive_meeting_ingestion.md" \
  --outcome failure \
  --skill-phase root_cause \
  --notes "Switched to manual tool calls instead of prompt orchestration"
```

---

## Skill Phase Tracking

When logging debug attempts, include the skill phase from `systematic-debugging`:

| Phase | Value | When to Use |
|-------|-------|-------------|
| Root Cause | `root_cause` | Investigating before any fix |
| Pattern Analysis | `pattern` | Comparing working vs broken |
| Hypothesis Testing | `hypothesis` | Testing a specific theory |
| Implementation | `implementation` | Applying a fix |

Example:
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id con_xyz --component "api-auth" \
  --problem "Token validation failing" \
  --hypothesis "Token format changed in v2" \
  --actions "Compared v1 and v2 token structures" \
  --outcome partial --skill-phase root_cause \
  --notes "Found format difference, need to trace source"
```

---

## Behavioral Pattern

**OLD (Wrong):**
```
Think → Try fix → Check result → Think again → Try another fix
[No logging, patterns invisible, circular debugging undetected]
```

**NEW (Correct):**
```
Think → Log hypothesis → Try fix → Log outcome → Check patterns → Next attempt
[Logged trail, patterns visible, circular detection active]
```

---

## Quick Command Templates

### Success
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id $CONVO_ID --component "$COMPONENT" \
  --problem "$PROBLEM" --hypothesis "$HYPOTHESIS" \
  --actions "$ACTIONS" --outcome success \
  --skill-phase "root_cause|pattern|hypothesis|implementation" \
  --notes "$NOTES"
```

### Failure
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id $CONVO_ID --component "$COMPONENT" \
  --problem "$PROBLEM" --hypothesis "$HYPOTHESIS" \
  --actions "$ACTIONS" --outcome failure \
  --skill-phase "root_cause|pattern|hypothesis|implementation" \
  --notes "$NOTES"
```

### Check Recent + Patterns (After 2nd Failure)
```bash
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id $CONVO_ID --n 5 --format display

python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id $CONVO_ID --window 10 --threshold 2
```

---

## Integration with Vibe Operator

**Vibe Operator persona should:**

1. **Detect build/debug context** (conversation has DEBUG_LOG.jsonl)
2. **Log significant attempts** (after fix attempts, not trivial reads)
3. **Check patterns proactively** (after 2nd failure on same component)
4. **Surface warnings to V** (when circular pattern detected)
5. **Consider Debugger persona** (if 3+ similar failures)

---

## Reinforcement Checklist

Before claiming "done" on any debugging session:
- [ ] Significant attempts logged to DEBUG_LOG.jsonl
- [ ] Pattern check run (if 3+ attempts made)
- [ ] Root cause identified and logged
- [ ] Success entry logged with resolution notes

---

**Status:** Explicit reflexes defined  
**Version:** 1.2 (added skill phase tracking)  
**Load:** This should be in system prompt for build/debug conversations

*Updated: 2026-02-07T08:30 ET*
