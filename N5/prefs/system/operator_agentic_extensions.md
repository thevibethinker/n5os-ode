---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Operator Agentic Reliability Extensions

## Quick Reference for Vibe Operator

### Critical Rule Reminder System
**Files:** `N5/prefs/system/critical_reminders.txt`, `N5/scripts/inject_reminders.py`
**Trigger:** Every 5-8 exchanges when conversation >8K tokens
**Action:** Mental reminder injection (5 critical rules)

### Work Manifest System
**File:** `N5/scripts/work_manifest.py`
**Trigger:** Multi-step work (build/refactor/system design)
**Action:** Auto-create manifest in SESSION_STATE, track all threads

### Key Behaviors

1. **Progress Reporting (P15):**
   - Always: "X/Y complete (Z%)"
   - Never: Bare "Done" or "Complete"

2. **Placeholder Tracking:**
   - Document all TODO/STUB/FIXME immediately
   - Include in completion blockers

3. **Thread Documentation:**
   - Track ALL approaches (pursued + unpursued)
   - Record reasons for defer/reject decisions

4. **Persona Return:**
   - After specialized work → return to Operator
   - Never stay in Builder/Architect/etc mode

5. **Completion Check:**
   - Before claiming done → verify all criteria met
   - Report specific blockers if incomplete

### Full Documentation
See `file 'N5/prefs/system/agentic_reliability_integration.md'` for complete integration rules.
