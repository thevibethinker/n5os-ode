# Distributed AI Build Principles
**Version:** 1.0 (Draft)  
**Date:** 2025-10-15  
**Context:** Multi-conversation coordination architecture

---

## Core Concept

**YES - Your understanding is correct:**

The orchestrator thread acts as controller/overseer while worker threads handle focused implementation. This enables:
- **Intelligence multiplication:** Multiple independent AI reasoning processes
- **Context multiplication:** N workers × context_window = massive effective capacity
- **Quality control:** Orchestrator tests integration after each worker change
- **Parallel execution:** Multiple streams progress simultaneously

**Architecture:**
```
ORCHESTRATOR (Controller)
├─ Maintains big picture, architecture, integration
├─ Tests after worker changes
├─ Validates cross-cutting concerns
└─ Resolves conflicts, coordinates work

WORKER A (Focused implementation)
├─ Deep context on one module
├─ Independent reasoning
└─ Signals completion with test criteria

WORKER B (Focused implementation)
├─ Different module, full context budget
├─ Independent reasoning  
└─ Signals completion with test criteria
```

---

## Three-Tier Architecture

### **TRACKER (Passive Monitor)**
**Role:** Help V stay on top of all work  
**Responsibilities:**
- Monitor all conversation workspaces
- Display BUILD_MAP dashboard
- Show git status, task states
- **Read-only** - observes, doesn't control

**Example:** One tracker conversation V keeps open to see everything

### **ORCHESTRATOR (Active Coordinator)**
**Role:** Manage workers building a specific system  
**Responsibilities:**
- Assign tasks to worker conversations
- Review and approve worker changes
- Run integration tests
- Resolve conflicts between workers
- Maintain system architecture

**Example:** One orchestrator per major feature/system being built

### **WORKER (Focused Implementer)**
**Role:** Implement specific modules  
**Responsibilities:**
- Focus on bounded implementation task
- Report status via SESSION_STATE.md
- Request help/approval from orchestrator
- Stay within defined scope

**Example:** Any build conversation can be a worker

**Key Distinction:**
- **Tracker = "What's happening?"** (observer for V)
- **Orchestrator = "Make this happen"** (controller for system)
- **Worker = "Implement this"** (builder for module)

---

## Architectural Principles for Distributed AI Builds

### **A1: Single Orchestrator Pattern**
ONE conversation maintains system view, integration authority.

**Orchestrator responsibilities:**
- Full dependency graph visibility
- Cross-boundary change approval
- Integration testing
- Conflict resolution
- Final merge authority

**Worker responsibilities:**
- Focused implementation within boundary
- Unit testing
- State updates
- Request permission for cross-cutting changes

---

### **A2: Bounded Context Per Worker**
Each worker owns clearly defined module/subsystem.

**Boundary definition:**
```markdown
WORKER A Context:
- Owns: N5/scripts/auth/*
- Reads: N5/schemas/auth.schema.json
- Cannot modify: N5/config/*, other modules
```

**Benefits:**
- Prevents conflicts
- Enables parallel work
- Maintains modularity (P20)

---

### **A3: State Synchronization Protocol**
Workers PUSH state → Orchestrator PULLS and validates.

**Flow:**
1. Worker makes change → Updates SESSION_STATE.md
2. Worker signals "ready for review"
3. Orchestrator refreshes tracker (pulls all states)
4. Orchestrator validates, tests integration
5. Orchestrator approves/rejects

**No worker-to-worker direct communication** (orchestrator mediates).

---

### **A4: Test-After-Integrate Pattern**
Orchestrator tests after each worker commit.

**Protocol:**
```markdown
WORKER: "✅ Auth complete. Test: pytest tests/test_auth.py"
ORCHESTRATOR: [runs test] → Result
ORCHESTRATOR (if pass): "✅ Approved"
ORCHESTRATOR (if fail): "Fix X, retest"
```

**Catches:** Integration bugs, premature completion (P15), missing error handling (P19).

---

### **A5: Git-Based Coordination**
Answer to your Question #1: **YES, use git staging strategically.**

**Pattern:**
```bash
# WORKER conversation
git checkout -b worker-a-auth
# Make changes
git add N5/scripts/auth/*
git commit -m "feat: JWT implementation"

# Signal orchestrator: "Ready for review, branch: worker-a-auth"

# ORCHESTRATOR conversation  
git checkout worker-a-auth
# Review changes: git diff main...worker-a-auth
# Test integration
git checkout main && git merge worker-a-auth  # if approved
```

**Benefits:**
- Orchestrator sees EXACTLY what changed via `git diff`
- Staging = "this is what I'm working on now"
- Branches = worker isolation
- Merge = orchestrator approval

---

### **A6: Message-Driven Coordination**
Communication via structured messages in SESSION_STATE.md.

**Message types:**
- REQUEST: Need resource from other worker
- UPDATE: Task progress
- COMPLETE: Done, ready for review
- APPROVE: Orchestrator approval
- REJECT: Orchestrator rejection with feedback
- BLOCKED: Can't proceed
- UNBLOCK: Blocker resolved

**Example:**
```markdown
## Outbox (Messages to orchestrator/workers)
- [2025-10-15 21:00] COMPLETE: Auth module ready | Test: pytest tests/auth/
- [2025-10-15 21:05] REQUEST: Need schema from Worker B | Status: blocked

## Inbox (Messages from orchestrator/workers)
- [2025-10-15 21:10] APPROVE: Auth module approved, merged to main
```

---

### **A7: Context Budget Allocation**
Strategically assign work based on complexity.

| Task Type | Assign To | Rationale |
|-----------|-----------|-----------|
| System design | Orchestrator | Needs full view |
| Deep refactor | Worker | Detail focus |
| Integration test | Orchestrator | Cross-module |
| Single-module bug | Worker | Bounded scope |
| API design | Worker + Orchestrator review | Detail then validation |

**Context multiplication math:**
- Serial: 1 × 200K tokens
- Distributed (3 workers + orchestrator): 4 × 200K = 800K effective

---

### **A8: Checkpoint Protocol**
Regular sync points across all workers.

**Checklist:**
```markdown
## Checkpoint: 2025-10-15 21:30

Worker A: 3 commits, tests passing
Worker B: 1 commit, blocked (needs schema)
Worker C: 2 commits, tests passing

Integration: No conflicts
Action: Assign schema to Worker D, unblock Worker B
Next checkpoint: 30 min
```

---

### **A9: Completion Verification (P15 Extended)**
Orchestrator independently verifies "done" claims.

**Verification:**
```markdown
WORKER: "✅ Done"
ORCHESTRATOR checks:
- ✅ Tests pass
- ✅ Documentation complete  
- ✅ No placeholders (P21)
- ✅ Error handling (P19)
- ❌ Missing: Migration script

ORCHESTRATOR: "Not complete, need migration"
WORKER: [adds migration]
ORCHESTRATOR: "✅ VERIFIED COMPLETE"
```

---

## Operational Workflows

### **Feature Implementation**
1. Orchestrator: Break into modules
2. Orchestrator: Assign workers
3. Workers: Implement in parallel
4. Orchestrator: Monitor via tracker
5. Workers: Signal completion
6. Orchestrator: Test integration
7. Orchestrator: Merge branches
8. Orchestrator: Final validation

**Speedup:** 3 workers = ~2-3× faster than serial

---

### **System Refactoring**
1. Orchestrator: Analyze, plan phases
2. Orchestrator: Assign workers respecting dependencies
3. Workers: Refactor in phases
4. Orchestrator: Validate each phase
5. Orchestrator: Coordinate merge order
6. Orchestrator: System-wide test

---

## Integration with N5 Principles

| N5 Principle | Distributed Application |
|--------------|-------------------------|
| P0 (Rule-of-Two) | Workers load ≤2 files each |
| P2 (SSOT) | Orchestrator = authoritative |
| P5 (Anti-Overwrite) | Workers on branches |
| P15 (Complete) | Orchestrator verifies |
| P18 (Verify State) | Orchestrator tests |
| P20 (Modular) | Workers = modules |

---

## Anti-Patterns

**❌ Worker-to-worker communication** → Fix: Route through orchestrator  
**❌ Orchestrator implementing** → Fix: Delegate to workers  
**❌ Unbounded worker scope** → Fix: Enforce boundaries  
**❌ Merge without testing** → Fix: Test-After-Integrate (A4)  
**❌ Implicit dependencies** → Fix: Declare in SESSION_STATE.md

---

## SESSION_STATE.md Format

Answer to your Questions #3-4: **Markdown is better** (human-readable, git-friendly, easy to edit).

**Structure:**
```markdown
# Session State
**Conversation:** con_ABC123
**Type:** build-worker
**Module:** auth-refactor
**Started:** 2025-10-15 20:00 UTC

---

## Configuration
- Persona: Vibe Builder
- Mode: implementation
- Output: terse, code-focused
- Context: auth module only

---

## Current Objectives
1. Refactor JWT authentication
2. Add refresh token support

## Active Tasks
- **JWT validation** (in progress, 70%)
  - ✅ Parse token
  - ✅ Verify signature
  - ⏳ Check expiration
  - ⏳ Error handling

## Progress Log
**[21:00]** Started JWT validation
**[21:15]** Completed signature verification
**[21:20]** BLOCKED: Need token schema from Worker B

---

## Git State
**Branch:** worker-a-auth
**Commits:** 3
**Files changed:** N5/scripts/auth/jwt.py, tests/test_jwt.py
**Staged:** Yes (ready for review)

---

## Dependencies
### Needs From Others
- FROM: Worker B | RESOURCE: auth.schema.json | STATUS: blocked

### Provides To Others
- TO: Worker C | RESOURCE: JWT validation function | STATUS: available

---

## Messages

### Outbox
- [21:20] REQUEST to Worker B: Need auth.schema.json
- [21:25] UPDATE to Orchestrator: 70% complete, blocked

### Inbox
- [21:22] RESPONSE from Orchestrator: Worker B assigned schema work
- [21:23] INFO from Orchestrator: ETA 10 min for schema

---

## Test Criteria
- `pytest tests/test_jwt.py` passes
- Integration test: `pytest tests/integration/test_auth_flow.py`
- Manual test: Token validation with expired token

---

## Notes & Decisions
- Using PyJWT library (already in requirements.txt)
- Token expiration: 1 hour (configurable in config)
- Error handling: Raise AuthenticationError with specific codes
```

---

## Tracker Integration

BUILD_MAP shows:
```markdown
## Worker Status

🔵 Worker A (con_ABC) - auth-refactor
   Status: 70% complete, BLOCKED
   Blocker: Waiting for schema from Worker B
   Branch: worker-a-auth (3 commits, staged)
   Recent: jwt.py, test_jwt.py

🔵 Worker B (con_XYZ) - schema-design  
   Status: 50% complete, ACTIVE
   Task: auth.schema.json
   Branch: worker-b-schema (1 commit)
   ETA: 10 min

🟢 Worker C (con_DEF) - api-endpoints
   Status: 90% complete, ACTIVE
   Waiting for: JWT validation from Worker A
   Branch: worker-c-api (5 commits)
```

---

## What This Solves

**Your realization:** Orchestrator maintains big picture while workers handle details with full context budgets.

**Enables:**
1. Parallel work streams
2. Deep technical focus per worker
3. Quality control via orchestrator testing
4. Integration validation at each step
5. Conflict detection before merge
6. Independent AI reasoning per module
7. Context multiplication (N × window_size)

**Next-level insight:** This is essentially **microservices architecture for AI development** - bounded contexts, message passing, orchestration layer.

---

## Status & Next Steps

**Phase 1:** ✅ Build tracker working  
**Phase 1.5:** Create SESSION_STATE.md template + integration (ready to build)  
**Phase 2:** Cross-conversation coordination (design complete above)

**Ready to implement Phase 1.5?**

---

*2025-10-15 21:10 ET*
