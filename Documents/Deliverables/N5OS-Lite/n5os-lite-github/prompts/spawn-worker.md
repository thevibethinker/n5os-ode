---
tool: true
description: Spawn parallel AI worker thread with context handoff
tags: [orchestration, parallel, workers, distributed]
version: 1.0
created: 2025-11-03
---

# Spawn Worker

Create independent AI worker threads for parallel execution of tasks.

**Use When:**
- Complex build with independent components
- Research + implementation happening simultaneously  
- Want to try multiple approaches in parallel
- Task can be cleanly separated with clear handoff

---

## Quick Start

**Tell your AI:**
```
"Spawn a worker to research OAuth2 alternatives and create comparison table.
Pass current project context."
```

**AI will:**
1. Capture relevant parent context
2. Create worker brief file
3. Tell you to open it in new conversation
4. Set up communication channel

---

## What Gets Passed

**Automatic context handoff:**
- Current SESSION_STATE (if exists)
- Recent artifacts list
- Project objectives
- Relevant file references

**Worker receives:**
- Clear mission statement
- Success criteria
- Dependencies (what it needs from parent)
- Deliverables (what parent expects back)

---

## Worker Lifecycle

```
Parent Conversation
    ↓ spawns
Worker Conversation (independent)
    ↓ completes work
    ↓ writes to shared location
Parent reviews & integrates
```

**Communication:**
- Worker writes artifacts to designated directory
- Parent monitors or worker notifies when complete
- Async: no blocking, both conversations independent

---

## Example: Research Worker

**Parent spawns:**
```
Mission: Research authentication alternatives to Firebase Auth
Success: Comparison table with pros/cons/costs
Deadline: 30 minutes
Deliverable: auth_comparison.md in worker_outputs/
```

**Worker (new conversation):**
1. Opens with worker brief loaded
2. Conducts research
3. Creates comparison table
4. Writes to specified location
5. Updates status file

**Parent:**
- Continues other work
- Checks worker_outputs/ when ready
- Integrates findings

---

## Example: Build Worker

**Parent spawns 3 workers:**
- W1: Data models
- W2: API endpoints (depends on W1)
- W3: UI components (depends on W2)

**Coordination:**
- W1 completes → writes models to shared dir → notifies
- W2 starts when W1 done
- W3 starts when W2 done
- Parent integrates all three

---

## Worker Brief Template

```markdown
# WORKER: [Task Name]

## Mission
[One sentence: what to accomplish]

## Context
[Background from parent]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Deliverables
**Files to create:**
- path/to/artifact1.md
- path/to/artifact2.py

**Location:** worker_outputs/worker_N/

## Dependencies
- Access to: [files/data worker needs]
- Requires from parent: [what parent must provide first]

## Timeline
Estimated: XX minutes
Deadline: [if any]

---

*Spawned from: [parent conversation ID]*  
*Status updates: worker_updates/worker_N_status.md*
```

---

## Best Practices

**Do:**
- Clear, focused mission (one worker = one cohesive task)
- Explicit success criteria
- Document dependencies
- Designate delivery location

**Don't:**
- Circular dependencies between workers
- Overly fine-grained tasks (context-switch overhead)
- Vague missions ("improve the system")
- Expect perfect coordination (async by nature)

---

## Troubleshooting

**Worker blocked:**
- Check dependencies met
- Verify worker has needed context
- Ensure file paths accessible

**Results not integrated:**
- Check deliverable location
- Verify file naming matches expectation
- Review worker status file

**Too much coordination overhead:**
- Maybe don't need parallel workers
- Consider sequential with clear phases
- Use orchestrator pattern (see `build_orchestrator.md`)

---

## Related

- System: `build_orchestrator.md` - Full orchestration pattern
- Principles: P36 (Orchestration Pattern)
- Examples: `worker_brief_template.md`
- Examples: `orchestrator_project.md`

---

*Parallel execution: When independent tasks can run simultaneously.*
