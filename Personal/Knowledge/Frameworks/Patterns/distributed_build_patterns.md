---
date: "2025-10-16T00:00:00Z"
version: 1
category: patterns
priority: high
related_files: "['Documents/System/SESSION_STATE_SYSTEM.md', 'Knowledge/architectural/architectural_principles.md']"
---
# Distributed Build Patterns

**Purpose:** Design patterns and behaviors for efficient distributed builds  
**Version:** 1.0  
**Status:** Production

---

## Core Philosophy

**Goal:** Maximize parallelism, minimize context, maximize quality

**Approach:** Surgical conversations with central monitoring

**Benefits:**
- Each worker focuses on <500 LOC
- Parallel execution reduces wall-clock time
- Smaller context = fewer mistakes
- Central orchestrator maintains coherence
- Quality gates before integration

---

## Pattern 1: Modular Decomposition (P20)

**When:** Any multi-file or >500 LOC task

**Pattern:** Break into independent, loosely-coupled modules

**How:**
1. Identify natural boundaries (files, features, layers)
2. Ensure each module is independently testable
3. Limit to 2 files per worker (minimal context loading)
4. Define clear interfaces between modules

**Example:**
```
Authentication System (2000 LOC, 8 files)
↓
Worker 1: JWT utilities (200 LOC, 1 file)
Worker 2: Password hashing (150 LOC, 1 file)
Worker 3: Login endpoint (200 LOC, 1 file)
Worker 4: Registration endpoint (200 LOC, 1 file)
Worker 5: Session management (300 LOC, 2 files)
```

**Anti-pattern:** Single worker, 2000 LOC, 8 files → context overload, high error rate

---

## Pattern 2: Interface-First Design (P2 SSOT)

**When:** Multiple workers need to integrate

**Pattern:** Define all interfaces before implementation starts

**How:**
1. Orchestrator documents interfaces upfront
2. Include in worker ASSIGNMENT.md
3. Workers implement to contract
4. Integration tests validate contracts

**Example:**
```python
# Orchestrator defines in shared interfaces file:
class AuthService:
    def authenticate(self, username: str, password: str) -> Token: ...
    def validate_token(self, token: str) -> User: ...

# Worker A implements AuthService
# Worker B uses AuthService (doesn't wait for implementation)
```

**Benefit:** Workers can proceed in parallel without blocking

**Anti-pattern:** Workers discover interfaces during implementation → rework, delays

---

## Pattern 3: Data Flow Mapping

**When:** Complex dependencies between modules

**Pattern:** Explicitly map what data each worker needs/produces

**How:**
1. Draw data flow diagram before decomposing
2. Identify critical path (longest dependency chain)
3. Schedule independent workers in parallel
4. Track data dependencies in SESSION_STATE.md

**Example:**
```
User Schema (W1) → User Model (W2) → User API (W3)
                                   ↘ User Tests (W4)

Schedule:
- Batch 1: W1 (blocker)
- Batch 2: W2 (depends on W1)
- Batch 3: W3 + W4 in parallel (both depend on W2)
```

**Tool:** `python3 N5/scripts/dependency_graph.py --orchestrator con_ORCH`

**Anti-pattern:** Start all workers simultaneously → blockers discovered late

---

## Pattern 4: Risk-Based Prioritization

**When:** Mix of simple and complex modules

**Pattern:** Tackle risky/complex modules first

**Why:** Fail fast, avoid late-stage rework

**Risk indicators:**
- External API integrations
- Performance-critical code
- Novel algorithms
- Multi-system coordination
- New technologies

**How:**
1. Tag modules as low/medium/high complexity
2. Schedule high-risk in Batch 1
3. If high-risk fails, reassess entire plan
4. Simple modules provide quick wins later

**Example:**
```
Batch 1: Payment integration (high risk) ← Start here
Batch 2: User endpoints (medium risk)
Batch 3: UI components (low risk) ← Quick wins
```

**Anti-pattern:** Easy tasks first → discover hard problem at 80% complete

---

## Pattern 5: Context Boundaries (Minimal Context)

**Problem:** Workers get overloaded with too much context
**Solution:** Load only essential files; prefer minimal, focused context

---

## Pattern 6: Incremental Integration (P7 Dry-Run)

**When:** Merging multiple worker outputs

**Pattern:** Integrate one worker at a time, test between each

**How:**
1. Workers complete in parallel (fast)
2. Orchestrator merges sequentially (safe)
3. Run tests after each merge
4. If failure, isolate to single worker
5. Fix before proceeding to next merge

**Sequence:**
```bash
# Workers complete in parallel
Worker 1 ✓  Worker 2 ✓  Worker 3 ✓

# Orchestrator integrates sequentially
Merge W1 → Test ✓ → Merge W2 → Test ✓ → Merge W3 → Test ✓
```

**Tool:** `python3 N5/scripts/integration_test_runner.py --worker-convo con_W1`

**Benefit:** Easy to pinpoint failures

**Anti-pattern:** Merge all at once → "something broke, not sure what"

---

## Pattern 7: Explicit Assumptions (P21)

**When:** Any ambiguity in requirements

**Pattern:** Document all assumptions in ASSIGNMENT.md

**How:**
1. Orchestrator lists assumptions
2. Worker validates assumptions first
3. Worker documents new assumptions discovered
4. Orchestrator reviews assumptions before approval

**Example assumptions:**
```
- Authentication service is already deployed
- Database schema matches version 2.3
- Max 10K requests/second
- Users are pre-validated upstream
```

**Benefit:** Surfaces misalignment early

**Anti-pattern:** Implicit assumptions → "I thought you meant..."

---

## Pattern 8: Clear Success Criteria

**When:** Always

**Pattern:** Checkboxes, not vague goals

**Good:**
```
- [ ] Login endpoint returns 200 for valid credentials
- [ ] Login endpoint returns 401 for invalid credentials
- [ ] JWT token expires after 1 hour
- [ ] Tests achieve >80% coverage
```

**Bad:**
```
- [ ] Implement authentication
- [ ] Make it work
```

**How:**
1. Orchestrator defines criteria in ASSIGNMENT.md
2. Worker checks off as completed
3. Orchestrator validates before approval
4. Integration tests enforce criteria

**Anti-pattern:** "Done" means different things → rework

---

## Efficient User Behaviors

### Pre-Decomposition (Setup Phase)

**Do this in orchestrator conversation:**

1. **Frame the problem** - Discuss requirements, constraints, approach
2. **Define success** - What does "done" look like?
3. **Identify files** - Which files will change?
4. **Sketch architecture** - High-level design
5. **Spot risks** - What's hard/uncertain?
6. **Estimate scope** - Roughly how much code?

**Output:** Clear objective in SESSION_STATE.md

**Time:** 15-30 minutes of discussion

### Decomposition

**When:** You say "We're ready with a plan"

**Command:** `python3 N5/scripts/task_deconstructor.py --orchestrator con_ORCH`

**Review checklist:**
- [ ] Are modules truly independent?
- [ ] Is complexity evenly distributed?
- [ ] Are interfaces defined?
- [ ] Does critical path make sense?
- [ ] Any circular dependencies?

**Adjust if needed** - Manual editing of generated assignments is OK

### Execution

**Create workers:**
1. Start one conversation per worker
2. Copy ASSIGNMENT.md into each worker's first message
3. Workers initialize their own SESSION_STATE.md
4. Workers execute in parallel

**Monitor progress:**
```bash
# Dashboard view
python3 N5/scripts/build_tracker.py --orchestrator con_ORCH --watch

# Or check periodically
python3 N5/scripts/build_tracker.py --orchestrator con_ORCH
```

**Handle questions:**
- Workers send messages to orchestrator
- Orchestrator checks messages: `python3 N5/scripts/message_queue.py list --convo-id con_ORCH`
- Orchestrator responds with clarifications

### Quality Gates

**Before merging each worker:**

```bash
# 1. Run tests
python3 N5/scripts/integration_test_runner.py --worker-convo con_W1

# 2. Check principles
python3 N5/scripts/principle_violation_detector.py --worker-convo con_W1

# 3. Review output
python3 N5/scripts/orchestrator.py review --worker con_W1

# 4. If all pass, approve
python3 N5/scripts/orchestrator.py approve --worker con_W1
```

**Integration:**
```bash
# Merge worker code (manual for now)
# Run integration tests
# If pass, proceed to next worker
```

### Post-Execution

**After all workers integrated:**
1. Run full test suite
2. Update documentation
3. Capture lessons learned
4. Archive conversation lineage

**Document in orchestrator SESSION_STATE.md:**
- What worked well?
- What caused problems?
- How to improve next time?

---

## Decision Framework

### When to Deconstruct?

| Factor | Solo | Deconstruct |
|--------|------|-------------|
| Total LOC | <500 | >500 |
| Files to modify | ≤2 | >2 |
| Independent modules? | No | Yes |
| Time pressure | Very high | Medium/Low |
| Learning goal | Understand everything | Ship fast |
| Risk level | Low | High |
| Team size | Just me | Could parallelize |

**Rule of thumb:** If it'll take >2 hours solo, consider deconstructing

### How Many Workers?

**Formula:** `workers = ceil(total_LOC / 400) * difficulty_multiplier`

**Difficulty multipliers:**
- Simple CRUD: 1.0x
- Business logic: 1.5x
- Integration: 2.0x
- Performance-critical: 2.5x

**Examples:**
- 1500 LOC CRUD → 4 workers
- 1500 LOC integration → 8 workers

**Constraints:**
- Min: 1 worker (duh)
- Max: ~10 workers (coordination overhead increases)
- Sweet spot: 3-5 workers

---

## Common Pitfalls

### ❌ Over-decomposition
**Problem:** 20 workers for 1000 LOC → coordination nightmare  
**Fix:** Aim for 200-400 LOC per worker

### ❌ Under-decomposition
**Problem:** 1 worker for 2000 LOC → context overload, bugs  
**Fix:** Follow minimal context principle (P8)

### ❌ Unclear interfaces
**Problem:** Workers make incompatible assumptions  
**Fix:** Interface-First Design (Pattern 2)

### ❌ Hidden dependencies
**Problem:** Worker blocked waiting for another  
**Fix:** Data Flow Mapping (Pattern 3)

### ❌ Big-bang integration
**Problem:** Merge all workers, tests fail, debug hell  
**Fix:** Incremental Integration (Pattern 6)

### ❌ Vague assignments
**Problem:** "Implement user management" → worker unclear on scope  
**Fix:** Specific files, clear criteria, explicit assumptions

### ❌ No quality gates
**Problem:** Merge broken code, discover later  
**Fix:** Test + principle check before every merge

---

## Success Metrics

Track these to improve over time:

- **Parallel efficiency:** Wall-clock time vs. serial time
- **Rework rate:** % of workers requiring revision
- **Integration failures:** # of merge conflicts or test failures
- **Context violations:** # of workers exceeding P0 boundaries
- **Principle compliance:** % of workers passing violation detector

**Target:**
- Parallel efficiency: >60% (3x faster with 5 workers)
- Rework rate: <20%
- Integration failures: <10%
- Context violations: 0%
- Principle compliance: >90%

---

## Tools Reference

| Tool | Purpose | Command |
|------|---------|---------|
| Task Deconstructor | Generate worker assignments | `python3 N5/scripts/task_deconstructor.py --orchestrator con_ORCH` |
| Build Tracker | Monitor worker progress | `python3 N5/scripts/build_tracker.py --orchestrator con_ORCH --watch` |
| Integration Tests | Validate worker output | `python3 N5/scripts/integration_test_runner.py --worker-convo con_W1` |
| Principle Detector | Check quality | `python3 N5/scripts/principle_violation_detector.py --worker-convo con_W1` |
| Dependency Graph | Visualize relationships | `python3 N5/scripts/dependency_graph.py --orchestrator con_ORCH` |
| Orchestrator | Coordinate workers | `python3 N5/scripts/orchestrator.py [command]` |
| Message Queue | Worker ↔ orchestrator | `python3 N5/scripts/message_queue.py [command]` |

---

## Examples

### Example 1: REST API (Medium Complexity)

**Task:** Build user management REST API (1200 LOC, 6 files)

**Decomposition:**
1. Worker 1: User model + DB schema (2 files, 250 LOC)
2. Worker 2: GET /users endpoints (1 file, 200 LOC)
3. Worker 3: POST/PUT endpoints (1 file, 250 LOC)
4. Worker 4: DELETE endpoint + auth (2 files, 250 LOC)
5. Worker 5: Integration tests (1 file, 250 LOC)

**Schedule:**
- Batch 1: Worker 1 (foundation)
- Batch 2: Workers 2, 3, 4 (parallel, depend on W1)
- Batch 3: Worker 5 (depends on W2, W3, W4)

**Duration:** Serial: 6 hours → Parallel: 2.5 hours (60% efficient)

### Example 2: Data Pipeline (High Complexity)

**Task:** ETL pipeline with 3 sources (2000 LOC, 8 files)

**Decomposition:**
1. Worker 1: Source A extractor (2 files, 300 LOC) [high risk]
2. Worker 2: Source B extractor (2 files, 300 LOC) [high risk]
3. Worker 3: Source C extractor (2 files, 300 LOC) [high risk]
4. Worker 4: Transform layer (1 file, 400 LOC)
5. Worker 5: Load layer (1 file, 300 LOC)
6. Worker 6: Orchestration + error handling (2 files, 400 LOC)

**Schedule:**
- Batch 1: Workers 1, 2, 3 (parallel, high-risk first)
- Batch 2: Worker 4 (depends on extractors)
- Batch 3: Worker 5 (depends on transform)
- Batch 4: Worker 6 (depends on all)

**Duration:** Serial: 10 hours → Parallel: 4.5 hours (55% efficient)

---

## Future Enhancements

**Phase 5 (Platform Integration):**
- Auto-export threads with lineage
- One-click worker creation from assignments
- Real-time dashboard in Zo UI
- Native SESSION_STATE support

**Phase 6 (Intelligence):**
- Auto-suggest decomposition from objective
- Learn from past builds (what worked?)
- Predict integration risks
- Auto-adjust plan based on worker progress

---

## References

- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Complete system docs
- file 'Knowledge/architectural/architectural_principles.md' - Core principles
- file 'N5/scripts/task_deconstructor.py' - Implementation

---

*Version 1.0 | Created: 2025-10-16 | Author: V + Vibe Builder*
