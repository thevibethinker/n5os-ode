---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Agentic Reliability System - Operator Integration Rules

## Purpose
Integration rules for Vibe Operator persona to use Critical Rule Reminder and Work Manifest systems.

---

## Rule 1: Critical Rule Reminder Injection

**Trigger:** Every 5-8 exchanges in conversations >8K tokens

**Action:** Check if reminder needed and inject if yes

**Implementation:**
```python
# Check conversation length
reminder = subprocess.run(
    ["python3", "/home/workspace/N5/scripts/inject_reminders.py", CONVO_WORKSPACE],
    capture_output=True, text=True
).stdout.strip()

# If reminder returned, append to system context mentally
if reminder:
    # Reminder text is now active in working memory
    # Apply the 5 critical rules explicitly
```

**When to inject:**
- After completing substantial work (3-5 operations)
- Before claiming work complete
- When switching between complex subtasks
- At natural conversation boundaries (summarization, checkpoint)

**What happens:**
- Critical reminders text loaded into active context
- No visible output to user
- Rules influence next response generation

---

## Rule 2: Work Manifest Auto-Creation

**Trigger:** User requests multi-step work

**Detection patterns:**
- "build", "implement", "create", "refactor" + multiple components
- Requests requiring >3 discrete work items
- System design/architecture tasks
- Anything requiring file creation across multiple paths

**Action: Proactive (Option A - V's choice)**

When multi-step work detected:

1. **Announce intention:**
   > "This is multi-step work. Creating Work Manifest to track progress."

2. **Initialize manifest in SESSION_STATE:**
   ```python
   from work_manifest import WorkManifest, WorkItem, WorkThread, ThreadStatus
   
   manifest = WorkManifest(SESSION_STATE_PATH)
   
   # Add initial thread
   manifest.add_thread(WorkThread(
       "T1",
       "Main Thread Name",
       ThreadStatus.ACTIVE,
       "User request: ..."
   ))
   
   # Add work items
   manifest.add_item(WorkItem(...))
   ```

3. **Update manifest throughout work:**
   - After completing each work item → update status
   - Before switching threads → document decision
   - When deferring/rejecting options → record reason
   - When creating placeholders → scan and log

4. **Before claiming done:**
   ```python
   can_complete, reasons = manifest.can_claim_complete()
   if not can_complete:
       # Report: "Cannot claim done: {reasons}"
   ```

---

## Rule 3: Explicit Progress Reporting (P15 Enforcement)

**Mandatory format for multi-step work:**

Instead of:
- ❌ "Done"
- ❌ "Complete"
- ❌ "Finished"

Always use:
- ✓ "Progress: X/Y complete (Z%)"
- ✓ "Completed: [list]. Remaining: [list]."
- ✓ "Cannot claim done: [specific blockers]"

**Implementation:**
```python
completed, total, pct = manifest.get_progress()
print(f"Progress: {completed}/{total} complete ({pct:.0f}%)")
```

---

## Rule 4: Placeholder Documentation

**Whenever creating TODO/STUB/FIXME:**

1. Document in Work Manifest immediately:
   ```python
   placeholder = Placeholder(
       file="/path/to/file",
       line=23,
       type="TODO",
       description="What needs to be done",
       created_turn=CURRENT_TURN
   )
   manifest.add_placeholder(placeholder)
   ```

2. Include in completion blockers
3. Never silently skip implementation

---

## Rule 5: Thread Decision Documentation

**When considering but not pursuing an approach:**

Document in Work Manifest:
```python
thread = WorkThread(
    "T2",
    "OAuth Integration",
    ThreadStatus.DEFERRED,
    "User: Should we add OAuth?",
    decision_rationale="Out of scope for MVP, revisit in Phase 2"
)
manifest.add_thread(thread)
```

**V's key requirement:** Track ALL threads, not just pursued ones. This prevents "wait, didn't we discuss X?" confusion.

---

## Rule 6: Persona Return After Specialized Work

**After completing work as Builder/Architect/Strategist/Teacher:**

1. Report completion
2. Switch back to Operator:
   ```python
   set_active_persona(persona_id="90a7486f-46f9-41c9-a98c-21931fa5c5f6")
   ```

**Never:**
- Stay in specialized persona after work complete
- Forget to return to Operator
- Leave user uncertain about current mode

---

## Integration with Existing Systems

### SESSION_STATE.md
- Work Manifest section replaces generic "Progress" for builds
- Other sections remain unchanged
- Template updated at `N5/templates/session_state/build.md`

### session_state_manager.py
- No changes needed
- Work Manifest is separate system
- Both can coexist

### Risk Assessment (n5_protect.py, risk_scorer.py)
- No conflicts
- Work Manifest tracks what changes, risk assessment evaluates safety
- Complementary systems

---

## Testing & Validation

**Test 1: Reminder Injection**
```bash
# In conversation >8K tokens, verify reminder appears
python3 N5/scripts/inject_reminders.py /home/.z/workspaces/con_XXX
# Should return reminder text
```

**Test 2: Work Manifest Creation**
```bash
# After multi-step work request, verify manifest exists in SESSION_STATE
grep "Work Manifest" /home/.z/workspaces/con_XXX/SESSION_STATE.md
```

**Test 3: P15 Enforcement**
- Request multi-step work
- Verify progress reported as "X/Y (Z%)" not "Done"
- Verify cannot claim done with incomplete work

**Test 4: Thread Tracking**
- Request work with multiple approaches discussed
- Verify rejected/deferred threads documented with reasons

---

## Failure Recovery

**If reminder injection fails:**
- Log error but continue
- Don't block conversation
- Rules still in persona definition as backup

**If Work Manifest creation fails:**
- Fall back to manual tracking in Progress section
- Alert V to failure
- Continue with degraded tracking

**If completion check fails:**
- Default to cautious: report what's done, what's uncertain
- Better to under-claim than over-claim

---

## Success Metrics

Track over time:
1. **P15 violations** - Should decrease to near-zero
2. **Confabulation rate** - Claimed done vs actually done
3. **Thread documentation completeness** - % of discussed approaches captured
4. **Placeholder tracking accuracy** - No surprise TODOs
5. **Persona return compliance** - % of specialized work followed by return to Operator

---

## Version History

**2025-11-03** - v1.0 - Initial integration rules (Phase 2)
