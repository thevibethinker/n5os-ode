# Example: Multi-Worker Build Orchestration

**Project:** Simple Task Management API  
**Approach:** Parallel AI workers coordinated by orchestrator  
**Workers:** 3 (Data, API, Tests)  
**Duration:** ~90 minutes with orchestration vs ~120 sequential

---

## Project Structure

```
Coordinator (Main Conversation)
├── Worker 1: Data Models & Database
├── Worker 2: API Endpoints (depends on W1)
└── Worker 3: Test Suite (depends on W1, W2)
```

---

## Phase 1: Planning & Brief Creation

**Coordinator creates 3 worker briefs:**

### WORKER_1: Data Layer

**Mission:** Design and implement data models + SQLite setup

**Deliverables:**
- `models.py` - Task, User, Project classes
- `database.py` - SQLite initialization
- `schema.sql` - Database schema
- `migrations/001_initial.sql` - Migration script

**Success Criteria:**
- Models have all required fields
- SQLite database creates successfully
- Basic CRUD operations work
- Schema documented

**Timeline:** 30 minutes

---

### WORKER_2: API Layer

**Mission:** Build REST API endpoints using data models from W1

**Dependencies:**
- Requires: `models.py` from Worker 1
- Waits for: W1 completion signal

**Deliverables:**
- `api.py` - Flask/FastAPI endpoints
- `routes/tasks.py` - Task CRUD endpoints
- `routes/users.py` - User endpoints
- `API_DOCS.md` - Endpoint documentation

**Success Criteria:**
- All CRUD endpoints implemented
- Input validation works
- Error handling included
- Documentation complete

**Timeline:** 30 minutes (starts after W1)

---

### WORKER_3: Test Suite

**Mission:** Create comprehensive test coverage

**Dependencies:**
- Requires: `models.py` from W1
- Requires: `api.py` from W2
- Waits for: W1 and W2 completion

**Deliverables:**
- `tests/test_models.py` - Unit tests
- `tests/test_api.py` - API integration tests
- `tests/fixtures.py` - Test data
- `TEST_REPORT.md` - Coverage report

**Success Criteria:**
- >80% code coverage
- All tests pass
- Edge cases covered
- Performance benchmarks included

**Timeline:** 30 minutes (starts after W2)

---

## Phase 2: Execution

**Coordinator:**
1. Spawns all 3 workers with briefs
2. W1 starts immediately
3. W2 and W3 wait for dependencies

**Worker 1:**
- Opens brief in new conversation
- Builds data layer
- Writes to `worker_outputs/w1/`
- Updates `worker_updates/w1_status.md`
- Marks complete

**Coordinator** (monitoring):
- Checks W1 status
- Sees completion → notifies W2 to start

**Worker 2:**
- Opens brief in new conversation
- Loads W1 outputs
- Builds API layer
- Writes to `worker_outputs/w2/`
- Updates status
- Marks complete

**Coordinator:**
- Checks W2 status
- Sees completion → notifies W3 to start

**Worker 3:**
- Opens brief
- Loads W1 + W2 outputs
- Builds test suite
- Writes to `worker_outputs/w3/`
- Runs tests, reports results
- Marks complete

---

## Phase 3: Integration

**Coordinator reviews all outputs:**

```
worker_outputs/
├── w1/
│   ├── models.py
│   ├── database.py
│   ├── schema.sql
│   └── migrations/001_initial.sql
├── w2/
│   ├── api.py
│   ├── routes/tasks.py
│   ├── routes/users.py
│   └── API_DOCS.md
└── w3/
    ├── tests/test_models.py
    ├── tests/test_api.py
    ├── tests/fixtures.py
    └── TEST_REPORT.md
```

**Coordinator:**
1. Reviews each worker's output
2. Checks integration points
3. Runs full test suite (W3's tests)
4. Identifies any issues
5. Spawns fix workers if needed
6. Integrates all code into main project
7. Creates final documentation

---

## Coordination Workflow

```
T=0min:  Spawn W1, W2, W3 (all have briefs)
T=0min:  W1 starts (no dependencies)
T=0min:  W2 waits (needs W1)
T=0min:  W3 waits (needs W1 + W2)

T=30min: W1 completes → signals coordinator
T=30min: Coordinator reviews W1 → approves
T=30min: W2 starts (dependency met)

T=60min: W2 completes → signals coordinator
T=60min: Coordinator reviews W2 → approves
T=60min: W3 starts (dependencies met)

T=90min: W3 completes → signals coordinator
T=90min: Coordinator integrates all three
T=100min: Integration complete, system working
```

**Total: ~100 minutes with coordination overhead**  
**Sequential: ~120+ minutes (W1→W2→W3 with context switching)**

---

## Communication Protocol

**Worker → Coordinator:**
- Status file: `worker_updates/wN_status.md`
- Content: `[status] [progress] [blockers] [next_steps]`
- Updated: Every major milestone

**Coordinator → Worker:**
- Dependency signal: File appears in `worker_inputs/wN/`
- Content: "W1 complete - models.py ready"
- Triggers: Worker checks for this before starting

---

## Handling Issues

**Worker blocked:**
```
W2 blocked: "models.py missing Task.priority field"
→ Coordinator spawns W1-fix: "Add priority field to Task model"
→ W1-fix completes quickly
→ W2 resumes
```

**Integration conflict:**
```
W2 and W3 have conflicting assumptions about error format
→ Coordinator identifies issue
→ Spawns W2-fix: "Update error format to match W3 expectations"
→ Re-integrate
```

---

## Key Success Factors

✅ **Clear Dependencies** - Each worker knew exactly what it needed  
✅ **Explicit Deliverables** - No ambiguity about outputs  
✅ **Status Updates** - Coordinator could monitor progress  
✅ **Async Coordination** - No blocking, workers independent  
✅ **Integration Plan** - Coordinator knew how pieces fit together

---

## When to Use This Pattern

**Good for:**
- Multi-component builds
- Independent subsystems
- Parallel research + implementation
- Exploration of alternatives (spawn 3 different approaches)

**Not good for:**
- Tightly coupled work
- Highly iterative design (too much back-and-forth)
- Simple, linear tasks
- Tasks requiring constant coordination

---

## Lessons Learned

1. **Spend time on briefs** - Clear briefs = smooth execution
2. **Explicit dependencies** - No assumptions about what's available
3. **Status updates matter** - Silent workers create uncertainty
4. **Integration is work** - Budget time for coordinator review
5. **Async is powerful** - When it works, huge time savings

---

**See also:**
- System: `build_orchestrator.md` - Full pattern documentation
- Prompts: `spawn-worker.md` - How to spawn workers
- Templates: `worker_brief_template.md` - Brief structure
- Principles: P36 (Orchestration Pattern)

---

*Orchestration: The art of coordinating independent agents toward a unified goal.*
