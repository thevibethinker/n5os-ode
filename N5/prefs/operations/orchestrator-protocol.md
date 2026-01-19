# Orchestrator-Worker Protocol

**Version:** 1.0  
**Created:** 2025-10-17  
**Purpose:** Standard protocol for orchestrating multi-worker builds

---

## Overview

For complex system builds, use the orchestrator-worker model where one conversation (orchestrator) manages multiple independent worker conversations executing discrete tasks in parallel or sequence.

---

## Orchestrator Setup Phase

### 1. Create Project Directory

```bash
mkdir -p /home/workspace/N5/builds/<project-name>
```

**Location:** Always under `N5/builds/` for permanent storage

### 1.5 MECE Validation (MANDATORY)

**Before creating worker briefs, validate MECE principles.**

Reference: `N5/prefs/operations/mece-worker-framework.md`

**Why:** Ensures work is divided in a mutually exclusive, collectively exhaustive way while minimizing worker count.

**Steps:**
1. List ALL scope items from the plan (files, responsibilities, deliverables)
2. Assign each item to exactly ONE worker
3. Verify no overlaps (same item in multiple workers)
4. Verify no gaps (items without an owner)
5. Check token budgets (target <30%, hard limit <40% of context)
6. After creating briefs, run: `python3 N5/scripts/mece_validator.py <project-name>`
7. Fix any issues before launching workers

**MECE Checklist:**
- [ ] All scope items explicitly assigned
- [ ] No overlapping scope between workers
- [ ] No gaps in scope coverage
- [ ] Each worker's token budget within limits
- [ ] Validator passes: `python3 N5/scripts/mece_validator.py <slug>`

### 2. Create Worker Briefs

Each worker brief must be a **self-contained markdown file** with:

**Required Sections:**
- **Mission:** Clear, single-sentence objective
- **Context:** Why this task matters, how it fits in system
- **Dependencies:** What must exist before starting
- **Deliverables:** Exact files/outputs expected
- **Requirements:** Technical specs, constraints
- **Implementation Guide:** Code templates, patterns, examples
- **Testing:** How to verify success
- **Report Back:** What to communicate to orchestrator

**Naming Convention:** `WORKER_N_DESCRIPTION.md`

**Location:** `/home/workspace/N5/builds/<project-name>/WORKER_N_*.md`

### 3. Create Orchestrator Monitor

**File:** `ORCHESTRATOR_MONITOR.md` in project directory

**Required Sections:**
- Worker status tracker (with checkboxes)
- Monitoring commands for validation
- Integration test procedures
- Blocker resolution protocol
- Progress visualization

### 4. Create Supporting Docs

- `ORCHESTRATOR_DASHBOARD.md` - Quick reference, launch sequence
- `ORCHESTRATOR_DEPLOYMENT_GUIDE.md` - Step-by-step instructions
- `<project>-design.md` - Full technical design
- Schema files, if applicable

---

## File Storage Rules

### ✅ CORRECT: Permanent Storage

```bash
# Worker briefs
/home/workspace/N5/builds/<project>/WORKER_*.md

# Orchestrator docs
/home/workspace/N5/builds/<project>/ORCHESTRATOR_*.md

# Design docs
/home/workspace/N5/builds/<project>/<project>-design.md

# Schemas (if creating)
/home/workspace/N5/schemas/<schema-name>.json
```

### ❌ INCORRECT: Conversation Workspace Only

```bash
# Don't leave briefs here - V can't access in new conversations!
/home/.z/workspaces/con_XXXXXX/WORKER_*.md
```

**Why:** Files in conversation workspace are not accessible to new worker conversations. V needs to reference permanent files when launching workers.

---

## Worker Launch Protocol

### For V (Manual Launch)

1. **Open new conversation** for each worker
2. **Reference the permanent brief:**
   ```
   Load file 'N5/builds/<project>/WORKER_N_*.md' and execute this task.
   Report back when complete.
   ```
3. **Track conversation ID** in orchestrator monitor
4. **Wait for completion** before launching dependent workers

### For Orchestrator Conversation

**Role:** Monitor, validate, unblock, integrate

**Do NOT:** Execute worker tasks in orchestrator conversation

---

## Monitoring Phase

### Orchestrator Responsibilities

1. **Track Progress**
   - Update `ORCHESTRATOR_MONITOR.md` with worker status
   - Record conversation IDs
   - Check off deliverables as completed

2. **Validate Deliverables**
   - Run validation commands after each worker
   - Verify files exist and are correct
   - Test functionality

3. **Resolve Blockers**
   - Analyze root cause
   - Create patch briefs if needed
   - Adjust dependencies
   - Re-assign tasks

4. **Integration Testing**
   - Run final integration tests after all workers complete
   - Verify end-to-end functionality
   - Check architectural principles compliance

---

## Worker Reporting Protocol

### Workers Must Report

When complete, workers should report:
1. ✅ All deliverables created
2. ✅ Tests passed
3. ✅ Any issues encountered
4. ✅ Files created (with paths)
5. ✅ Ready for next phase

### Orchestrator Records

Update monitoring file with:
- Status: complete
- Timestamp
- Conversation ID
- Deliverable checkmarks
- Any notes

---

## Validation Commands

### After Each Worker

Orchestrator runs verification specific to that worker's deliverables.

**Examples:**

```bash
# Verify file exists
ls -lh /path/to/deliverable

# Validate JSON
cat file.json | jq .

# Test import
python3 -c "from module import Class; print('OK')"

# Run tests
python3 script.py --test --dry-run
```

### Final Integration Test

Comprehensive end-to-end test that:
- Uses all components together
- Tests realistic workflows
- Validates against success criteria
- Checks architectural principles

---

## Blocker Resolution

### When Worker Encounters Blocker

1. **Worker reports** in their conversation
2. **V notifies orchestrator** with details
3. **Orchestrator analyzes** and proposes solution
4. **Options:**
   - Create patch brief for same worker
   - Adjust worker brief and restart
   - Create micro-worker for specific fix
   - Adjust dependencies/sequencing

5. **Re-test** affected component
6. **Continue** deployment

---

## Dependency Management

### Sequential Dependencies

```
W1 → W2 → W3
```

Launch W2 only after W1 completes.

### Parallel Execution

```
    ┌─> W2 ─┐
W1 ─┤       ├─> W4
    └─> W3 ─┘
```

W2 and W3 can run simultaneously after W1.

### Complex Graph

```
W1 ─┬─> W2 ─┬─> W4 ─> W5
    └─> W3 ─┘
```

Track carefully in monitoring file.

---

## Best Practices

### Worker Briefs

- **Self-contained:** All context included, no external assumptions
- **Specific:** Clear deliverables, no ambiguity
- **Tested:** Include test procedures
- **Bounded:** Single responsibility, ~30-60 min tasks
- **Documented:** Code templates, examples, patterns

### Orchestrator

- **Hands-off execution:** Let workers work independently
- **Active monitoring:** Track progress, validate continuously
- **Quick unblocking:** Resolve issues fast
- **Integration focus:** Ensure components work together

### File Organization

```
N5/builds/<project>/
├── WORKER_1_<task>.md
├── WORKER_2_<task>.md
├── WORKER_N_<task>.md
├── ORCHESTRATOR_MONITOR.md
├── ORCHESTRATOR_DASHBOARD.md
├── ORCHESTRATOR_DEPLOYMENT_GUIDE.md
├── <project>-design.md
├── <project>-orchestrator-plan.md
└── <supporting-files>
```

---

## Completion Checklist

Before marking project complete:

- [ ] All workers reported completion
- [ ] All deliverables created and validated
- [ ] Integration tests pass
- [ ] No blockers remaining
- [ ] Documentation updated
- [ ] Architectural principles followed (P0-P22)
- [ ] Fresh conversation test passed (P12)
- [ ] System ready for production use

---

## Templates

### Worker Brief Template

```markdown
# Worker N: Task Name

**Orchestrator:** con_XXXXXXXXXXXX  
**Task ID:** WN-SHORT-NAME  
**Estimated Time:** XX minutes  
**Dependencies:** Worker M (or None)

---

## Mission
[One sentence objective]

---

## Context
[Why this matters, how it fits]

---

## Dependencies
[What must exist first]

---

## Deliverables
1. File path 1
2. File path 2
3. Test results

---

## Requirements
[Technical specs]

---

## Implementation Guide
[Code templates, patterns]

---

## Testing
[Validation procedures]

---

## Report Back
[What to communicate]

---

**Orchestrator Contact:** con_XXXXXXXXXXXX  
**Created:** YYYY-MM-DD HH:MM ET
```

### Monitor Template

See `ORCHESTRATOR_MONITOR.md` in this project as reference.

---

## Anti-Patterns

### ❌ Don't

- Store briefs only in conversation workspace
- Launch workers without tracking conversation IDs
- Skip validation steps
- Let workers block without resolution
- Skip integration tests
- Forget to update monitor file

### ✅ Do

- Store all briefs in permanent N5 location
- Track every worker conversation ID
- Validate after each worker
- Actively monitor and unblock
- Run comprehensive integration tests
- Keep monitor file current

---

## Example: Output Review Tracker

**Reference implementation:**
`/home/workspace/N5/builds/output-review-tracker/`

5 workers, ~3 hours total, sequential and parallel execution.

---

**Version:** 1.0  
**Status:** Active Protocol  
**Updated:** 2025-10-17 21:10 ET
