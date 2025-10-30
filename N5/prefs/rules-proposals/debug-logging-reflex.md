# Proposed Rule: Debug Logging Reflex

**Version:** 1.0  
**Created:** 2025-10-29  
**Purpose:** Reinforce behavior of logging to DEBUG_LOG.jsonl during debugging

---

## Proposed Conditional Rule

**CONDITION:** When DEBUG_LOG.jsonl exists in conversation workspace (build/debug threads)

**RULE:**
```markdown
Log significant problem-solving attempts to DEBUG_LOG.jsonl in real-time:

1. **After attempting a fix:**
   - Log: component, problem, hypothesis, actions, outcome
   - Use: python3 /home/workspace/N5/scripts/debug_logger.py append

2. **Before 3rd attempt on same problem:**
   - Check for circular patterns
   - Use: python3 /home/workspace/N5/scripts/debug_logger.py patterns
   - If detected: Stop, analyze, or activate Debugger mode

3. **When multiple attempts fail:**
   - Review recent attempts
   - Use: python3 /home/workspace/N5/scripts/debug_logger.py recent
   - Synthesize patterns before next attempt

Pattern: Think → Log hypothesis → Try → Log outcome → Check patterns → Continue

Load: file 'N5/prefs/operations/debug-logging-auto-behavior.md' for full behavior guide
```

---

## Why This Helps

**Problem:** Tool exists but behavior isn't reflexive
**Solution:** Explicit condition-triggered rule in system prompt
**Benefit:** Automatic logging during debugging, pattern detection active

---

## Alternative: Vibe Operator Persona Update

Could also add to Vibe Operator persona directly:

```markdown
**Debug Log Reflex (build/debug conversations):**
- After fix attempt → Log to DEBUG_LOG.jsonl
- After 2nd failure → Check patterns
- After 3rd failure → Review recent, activate Debugger if circular
```

---

## Recommendation

**Add both:**
1. **Conditional rule** (catches all build/debug conversations)
2. **Operator persona mention** (reinforces in baseline behavior)

This creates layered reinforcement: rule triggers behavior, persona maintains it.

---

**Next Step:** V decides if this should be added as a formal rule in user_rules

*Proposal created: 2025-10-29T04:13 ET*
