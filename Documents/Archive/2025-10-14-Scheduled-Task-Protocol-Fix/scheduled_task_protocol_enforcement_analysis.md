# Scheduled Task Protocol Enforcement Analysis

**Date:** 2025-10-14  
**Context:** User reported protocol violations in scheduled task creation  
**Status:** Root cause identified, solution proposed

---

## Problem Statement

Scheduled tasks have been created recently without adhering to the documented protocol at `file 'N5/prefs/operations/scheduled-task-protocol.md'`.

**Examples of violations:**
- Missing dry-run testing phase
- Incomplete instruction structure
- No explicit success criteria
- Missing error handling specifications
- Undocumented assumptions

---

## Root Cause

**Finding:** The protocol exists but is **not automatically invoked** during scheduled task creation workflows.

**Current State:**
- ✅ Protocol exists: `file 'N5/prefs/operations/scheduled-task-protocol.md'`
- ✅ Protocol is comprehensive (v1.0.0, created 2025-10-13)
- ❌ No conditional rule triggers protocol loading
- ❌ AI instances create tasks without consulting protocol

**Comparison with other operations:**
```markdown
✅ System operations → Rule exists → Check commands.jsonl first
✅ Major refactoring → Rule exists → Load architectural principles
❌ Scheduled task creation → NO RULE → Protocol not consulted
```

---

## Verification

Searched user rules for scheduled task references:
- ❌ No conditional rule for `"When I request creating a scheduled task"`
- ❌ No conditional rule for `"scheduled task" or "create_scheduled_task"`
- ❌ Protocol file exists but never referenced in rules

Searched for similar successful patterns:
- ✅ `CONDITION: Before executing system operations` → Check commands.jsonl
- ✅ `CONDITION: When I request building... significant system components` → Load architectural principles

---

## Proposed Solution

### Option 1: Add Conditional Rule (Recommended)

**Location:** User rules section (presented at rule configuration UI)

**Proposed rule:**
```markdown
CONDITION: When I request creating, modifying, or reviewing a scheduled task
RULE: Load and follow `file 'N5/prefs/operations/scheduled-task-protocol.md'` before proceeding. This protocol includes:
- Safety requirements (user consent, impact assessment, rollback plan)
- Instruction structure standards
- Testing checklist (dry-run, verification, monitoring)
- Model selection guidelines
- Integration with digest protocol
- Documentation requirements
```

**Why this works:**
- Explicit trigger condition
- References the correct file path
- Includes key protocol highlights for context
- Matches existing rule pattern (architecture principles rule)

### Option 2: Reference in Prefs.md

**Alternative:** Add explicit reference in `file 'N5/prefs/prefs.md'`

Current relevant section:
```markdown
**For scheduled task operations** (creating, modifying tasks):
[No specific protocol reference currently]
```

**Proposed update:**
```markdown
**For scheduled task operations** (creating, modifying tasks):
- **ALWAYS load** `file 'N5/prefs/operations/scheduled-task-protocol.md'` before proceeding
- Follow testing checklist (dry-run → deploy → monitor)
- Document in task notes field per protocol standards
- Verify compliance with safety requirements (P11, P16, P19)
```

**Why this helps:**
- More prominent placement in loaded context
- Reinforces protocol importance
- Provides quick reference to key steps

### Option 3: Command-First Approach

**Create dedicated command:** `scheduled-task-create`

**Benefits:**
- Enforces protocol via code (automated checks)
- Follows existing "command-first" pattern from user rules
- Can validate RRULE, check file paths, preview schedule
- Generates compliant instruction template

**File:** `N5/commands/scheduled-task-create.md`  
**Script:** `N5/scripts/n5_scheduled_task_create.py`

**Implementation effort:** Higher, but most robust solution

---

## Recommendation

**Implement Option 1 + Option 2:**

1. **User Rule (Option 1):**
   - Adds conditional trigger for scheduled task operations
   - Ensures protocol is loaded automatically
   - Consistent with existing rule patterns

2. **Prefs Enhancement (Option 2):**
   - Makes protocol visible in loaded prefs context
   - Provides quick checklist even if rule not triggered
   - Low-effort, high-impact addition

**Future Enhancement:** Consider Option 3 (command) if violations continue after rule addition.

---

## Implementation Steps

### Step 1: Add Conditional Rule

**Action:** User adds rule via settings UI or direct configuration

**Proposed rule text:**
```
CONDITION: When I request creating, modifying, or reviewing a scheduled task
RULE: Load and follow file 'N5/prefs/operations/scheduled-task-protocol.md' before proceeding. This includes safety requirements, testing checklist, instruction structure, and documentation standards.
```

### Step 2: Update Prefs.md

**File:** `file 'N5/prefs/prefs.md'`

**Current section (line 227):**
```markdown
**For scheduled task operations** (creating, modifying tasks):
```

**Proposed update:**
```markdown
**For scheduled task operations** (creating, modifying tasks):
- **MANDATORY:** Load `file 'N5/prefs/operations/scheduled-task-protocol.md'` FIRST
- Follow testing workflow: dry-run → manual test → schedule → monitor first run
- Document task in notes field with purpose, dependencies, output, monitor metrics
- Verify safety requirements: user consent, impact assessment, error handling
- Use appropriate model: mini for routine ops, full for complex reasoning
```

### Step 3: Verification Test

After implementation, test with:
```
"Create a scheduled task to check list health every Monday at 8am"
```

**Expected behavior:**
1. AI loads protocol file first
2. Shows proposed schedule for confirmation
3. Presents instruction following protocol template
4. Includes success criteria and error handling
5. Requests explicit approval before creation
6. Documents in task notes per standards

---

## Success Criteria

- [ ] Conditional rule added and active
- [ ] Prefs.md updated with protocol reference
- [ ] Test task creation follows complete workflow
- [ ] No protocol violations in next 5 scheduled task creations
- [ ] User confirms improved compliance

---

## Notes

**Why the current approach failed:**
- Protocol created recently (2025-10-13)
- Not yet integrated into conditional rules system
- AI instances default to direct tool usage without protocol consultation
- Similar to pre-architectural-principles era (before that rule was added)

**Lessons learned:**
- New protocols need explicit rule triggers to be consistently applied
- Documentation alone insufficient for enforcement
- Conditional rules are the primary mechanism for mandatory workflows
- Protocol should be referenced in multiple locations (rules + prefs)

---

## Next Steps

1. **User decision:** Which option(s) to implement?
2. **Implementation:** Add rule via settings UI
3. **Update prefs.md:** Add protocol reference (Option 2)
4. **Test:** Create sample task and verify compliance
5. **Monitor:** Track protocol adherence over next week
6. **Consider:** If violations persist, implement Option 3 (command)

---

**Status:** Analysis complete, awaiting user decision on implementation approach.
