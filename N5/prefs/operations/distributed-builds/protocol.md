# Distributed Build Protocol

**Version:** 1.0  
**Purpose:** High-level workflow for multi-conversation build orchestration

---

## Overview

Distributed builds split complex changes across multiple independent conversations (workers), coordinated by a central orchestrator thread.

**When to use:** See `file 'decision-tree.md'`

**Core principle:** Context isolation = quality multiplication

---

## Roles

### Orchestrator (Conversation 1)
- **Persona:** Vibe Builder
- **Responsibilities:**
  - Frame the problem
  - Decompose into workers
  - Generate assignments
  - Monitor progress
  - Integrate worker outputs
  - Validate quality
  - Generate after-action report

**What orchestrator DOESN'T do:** Write implementation code (that's for workers)

### Workers (Conversations 2-N)
- **Persona:** Vibe Builder (or task-appropriate specialist)
- **Responsibilities:**
  - Read assignment
  - Update state
  - Implement deliverables
  - Test their work
  - Generate summary
  - Flag blockers

**What workers DON'T do:** Coordinate with each other directly (orchestrator handles coordination)

### You (V)
- **Responsibilities:**
  - Initiate build
  - Open worker conversations
  - Ferry messages between orchestrator and workers
  - Make final decisions on blockers
  - Approve integration

---

## Workflow

### Stage 1: Framing (Orchestrator)

**Duration:** 20-40 minutes  
**Location:** Orchestrator conversation

**Steps:**
1. **You say:** "I want to build [X]"
2. **Orchestrator asks:** 3-5 clarifying questions
3. **You answer:** Provide context, constraints, priorities
4. **Orchestrator documents:** Understanding in BUILD_STATE_SESSION.md

**Output:** Shared mental model

**Quality gate:** Both you and orchestrator agree on:
- What problem we're solving
- What's in/out of scope
- What success looks like

---

### Stage 2: Decomposition (Orchestrator)

**Duration:** 30-60 minutes  
**Location:** Orchestrator conversation

**Steps:**
1. **Analyze codebase** - Read relevant files, understand current state
2. **Identify modules** - Natural boundaries, clear responsibilities
3. **Map dependencies** - Which modules depend on which
4. **Decompose into workers** - Each worker = 1 bounded task
5. **Define interfaces** - Explicit contracts between workers
6. **Generate assignments** - Use template, be extremely explicit

**Output:**
- `/home/workspace/N5/logs/builds/[build-name]/BUILD_STATE_SESSION.md`
- `/home/workspace/N5/logs/builds/[build-name]/assignments/WORKER_[N]_ASSIGNMENT.md` (for each worker)

**Quality gate:** Can you explain:
- What each worker will build?
- Why in this order?
- What interfaces connect them?

**Orchestrator tells you:** "Setup complete. Open `WORKER_1_ASSIGNMENT.md` in a new conversation to begin."

---

### Stage 3: Worker Execution (Worker Threads)

**Duration:** Variable per worker  
**Location:** Individual worker conversations

**You do:**
1. Open new chat
2. Add `file 'N5/logs/builds/[build-name]/assignments/WORKER_[N]_ASSIGNMENT.md'` to conversation
3. Say: "Execute this assignment"

**Worker does:**
1. **Load assignment** - Read fully, understand scope
2. **Update state** - `BUILD_STATE_SESSION.md` → status: IN_PROGRESS
3. **Read dependencies** - Understand what to build on
4. **Implement** - Write code to `/home/workspace/[target-location]/`
5. **Test** - Run specified tests, validate acceptance criteria
6. **Document** - Generate summary with design decisions
7. **Update state** - `BUILD_STATE_SESSION.md` → status: REVIEW
8. **Complete** - "Done. Summary at [path]. Return to orchestrator."

**If blocked:**
1. Generate error report (see `file 'error-tracking-guide.md'`)
2. Update state → status: BLOCKED
3. Tell you: "BLOCKED: [code]. Report at [path]."

**Output:**
- Code at final destination: `/home/workspace/[wherever-it-belongs]/`
- Summary: `/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_SUMMARY.md`
- (If errors): `/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_ERROR_LOG.md`

---

### Stage 4: Integration (Orchestrator)

**Duration:** 15-45 minutes per worker  
**Location:** Orchestrator conversation

**You do:** Return to orchestrator, say "Worker [N] complete"

**Orchestrator does:** (see `file 'templates/INTEGRATION_CHECKLIST.md'`)

1. **Pre-integration checks**
   - Read worker summary
   - Verify status = REVIEW
   - Run worker tests in isolation

2. **Review worker code**
   - Read all modified files
   - Understand design decisions
   - Check against assignment

3. **Validate interfaces**
   - Function signatures match spec?
   - Data structures compatible?
   - File modifications in bounds?

4. **Integration test**
   - Run system-level tests
   - Check for side effects
   - Validate against principles

5. **Decision**
   - ✅ ACCEPT: Integrate as-is
   - 🔄 REVISE: Minor fixes by orchestrator
   - ❌ REJECT: Send back to worker

6. **Update state**
   - Mark worker INTEGRATED
   - Update error log (if any issues)
   - Update lessons learned

7. **Next worker** - Repeat for Worker N+1

**Output:**
- Integrated code in workspace
- Updated BUILD_STATE_SESSION.md
- Integration notes

**Quality gate:** Each worker integration includes:
- All tests pass
- No principle violations
- Interfaces work as specified

---

### Stage 5: Validation (Orchestrator)

**Duration:** 30-60 minutes  
**Location:** Orchestrator conversation

**After ALL workers integrated:**

1. **System test** - End-to-end flows work?
2. **Principle check** - Review entire change against `file 'Knowledge/architectural/architectural_principles.md'`
3. **Documentation** - Update READMEs, architecture docs
4. **After-action report** - Comprehensive build retrospective

**Output:**
- Fully functional integrated system
- Updated documentation
- After-action report

**Quality gate:**
- [ ] All workers integrated
- [ ] System tests pass
- [ ] Principles validated
- [ ] Documentation current
- [ ] Lessons documented

---

### Stage 6: Archival

**Duration:** 5 minutes  
**Location:** Orchestrator conversation

**Orchestrator does:**
```bash
mv /home/workspace/N5/logs/builds/[build-name] \
   /home/workspace/N5/logs/threads/$(date +%Y-%m-%d)_[build-name]_[short-id]/
```

**Result:** Build artifacts preserved for posterity

---

## Communication Patterns

### Orchestrator → You → Worker
```
Orchestrator: "Worker 2 can begin now. Open WORKER_2_ASSIGNMENT.md."
You: [Opens new chat with that file]
Worker 2: [Starts work]
```

### Worker → You → Orchestrator
```
Worker 2: "Complete. Summary at /path/W2_SUMMARY.md"
You: [Returns to orchestrator] "Worker 2 done"
Orchestrator: [Reads summary, integrates]
```

### Worker → You → Orchestrator (Error)
```
Worker 2: "BLOCKED: E104. Report at /path/W2_ERROR_LOG.md"
You: [Returns to orchestrator] "Worker 2 blocked, error E104"
Orchestrator: [Reads report, decides resolution]
Orchestrator: "Update Worker 2 assignment with clarification at [path]"
You: [Adds updated file to Worker 2 conversation]
Worker 2: [Resumes]
```

---

## Best Practices

### For Orchestrator

**DO:**
- Spend serious time on framing (30% of effort)
- Make interfaces EXPLICIT (write them out)
- Keep workers small and focused (100-300 LOC each)
- Integrate incrementally (one at a time)
- Document lessons after EACH integration
- Celebrate good worker outputs

**DON'T:**
- Rush decomposition (garbage in = garbage out)
- Leave interfaces implicit ("they'll figure it out")
- Make workers too large (>500 LOC = split it)
- Integrate multiple workers simultaneously (unless dependencies allow)
- Skip quality gates
- Forget to update lessons learned

### For Workers

**DO:**
- Read assignment fully before starting
- Update state promptly
- Stay within bounds (resist scope creep)
- Test thoroughly
- Write detailed summaries
- Flag blockers immediately

**DON'T:**
- Assume anything not explicit in assignment
- Modify files outside whitelist
- Skip tests
- Deliver incomplete work
- Let blockers sit (communicate!)

### For You

**DO:**
- Trust the process
- Be available for blockers
- Read summaries before saying "next"
- Learn from each build
- Refine templates over time

**DON'T:**
- Rush integration
- Skip quality gates
- Ignore error patterns
- Forget to archive builds

---

## Success Criteria

A distributed build is successful when:

1. **Functional:** Builds work as specified
2. **Quality:** Passes all tests, no principle violations
3. **Documented:** Code + decisions documented
4. **Learned:** Lessons captured for next time
5. **Sustainable:** Process felt manageable, not chaotic

---

## Common Pitfalls

See `file 'troubleshooting.md'` for detailed guidance. Quick reference:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Workers constantly blocked | Dependencies wrong | Reassess execution order |
| Integration takes forever | Interfaces unclear | Be more explicit in assignments |
| Lots of rework | Scope unclear | Improve assignment clarity |
| Quality issues | Skipping gates | Enforce quality checks |
| Orchestrator overwhelmed | Workers too large | Decompose more granularly |

---

## Next Steps

**First time using distributed builds?**
1. Read `file 'decision-tree.md'` - Confirm this is right approach
2. Pick a pilot build - 800-1200 LOC, 3-4 workers
3. Follow this protocol step-by-step
4. Document lessons in after-action report
5. Refine templates based on experience

**Ready to start?**
1. Operator activates Vibe Builder persona
2. Load `file 'Knowledge/architectural/architectural_principles.md'`
3. Say: "I want to build [X]"
4. Let orchestrator guide you through framing

---

**Remember:** This is an investment in quality. The coordination overhead pays dividends in fewer bugs, better architecture, and maintainable systems.
