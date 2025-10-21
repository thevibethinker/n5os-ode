# Orchestrator Build Capability - Complete Reference

**Loaded:** 2025-10-18 13:47 ET  
**Conversation:** con_DRisiUTGBztT3KRS  
**Persona:** Vibe Teacher

---

## What Is This System?

The **Distributed Build System** is a multi-conversation orchestration framework for implementing major software changes efficiently. It splits large builds across independent "worker" conversations coordinated by a central "orchestrator" conversation.

### Core Innovation

**Context isolation = quality multiplication**

Instead of one conversation handling 1000+ lines of code across 8 files (→ context overload, high error rate), you split into:
- 1 orchestrator (planning, coordination, integration)
- 3-5 worker conversations (each handling 100-300 LOC, 1-2 files)

### When To Use

**Use distributed builds when:**
- ✅ Task is >500 LOC
- ✅ Multiple files (>2)
- ✅ Natural module boundaries exist
- ✅ Quality is critical
- ✅ Complex dependencies

**Don't use when:**
- ❌ Simple task <500 LOC
- ❌ Single file or tightly coupled
- ❌ Need to deeply understand every detail yourself
- ❌ Extreme time pressure (coordination overhead)

---

## Core Architecture

### Three Roles

**1. Orchestrator Conversation (You start here)**
- Frames the problem (30-40 min)
- Decomposes into workers (30-60 min)
- Generates assignments
- Integrates worker outputs (15-45 min per worker)
- Validates system (30-60 min)

**2. Worker Conversations (Parallel execution)**
- Each receives a WORKER_ASSIGNMENT.md
- Implements bounded scope (100-300 LOC, 1-2 files)
- Updates SESSION_STATE.md with progress
- Generates W[N]_SUMMARY.md when complete

**3. You (V)**
- Initiate build with orchestrator
- Open worker conversations
- Ferry status updates between conversations
- Make final decisions on blockers
- Approve integrations

---

## Key Files & Scripts

### Core Scripts

**`/home/workspace/N5/scripts/orchestrator.py`**
- Assign tasks to workers
- Check worker status
- Review changes
- Approve completed work
- Commands:
  ```bash
  python3 orchestrator.py assign "Task" --to con_WORKER
  python3 orchestrator.py check-worker con_WORKER
  python3 orchestrator.py review-changes con_WORKER
  python3 orchestrator.py approve con_WORKER
  ```

**`/home/workspace/N5/scripts/task_deconstructor.py`**
- Analyzes orchestrator SESSION_STATE.md
- Identifies module boundaries
- Generates worker assignments
- Creates execution plan with dependency graph
- Usage:
  ```bash
  python3 task_deconstructor.py --orchestrator con_ORCH_123
  python3 task_deconstructor.py --orchestrator con_ORCH_123 --dry-run
  ```

**`/home/workspace/N5/scripts/build_tracker.py`**
- Monitors worker progress in real-time
- Scans SESSION_STATE.md across conversations
- Generates BUILD_MAP.md dashboard
- Usage:
  ```bash
  python3 build_tracker.py --orchestrator con_ORCH --watch  # Live
  python3 build_tracker.py --orchestrator con_ORCH          # Snapshot
  ```

**`/home/workspace/N5/scripts/dependency_graph.py`**
- Visualizes worker relationships
- Shows execution order
- Highlights orchestrator
- Outputs D2 diagram
- Usage:
  ```bash
  python3 dependency_graph.py --orchestrator con_ORCH
  ```

### Templates

**`BUILD_STATE_SESSION.md`** (Orchestrator's central tracking file)
- Worker status (ASSIGNED → IN_PROGRESS → REVIEW → INTEGRATED)
- Dependencies graph
- Error log
- Quality metrics
- Lessons learned after each integration
- Timeline

**`WORKER_ASSIGNMENT.md`** (Given to each worker)
- Bounded task definition
- Files to modify (whitelist)
- Dependencies on other workers
- Interface contracts (exact signatures)
- Success criteria (checkboxes)
- Quality gates
- Output locations

**`W[N]_SUMMARY.md`** (Worker generates when complete)
- What was built
- Design decisions and rationale
- Edge cases handled
- Integration notes for orchestrator
- Warnings/caveats

---

## The Workflow (6 Stages)

### Stage 1: Framing (Orchestrator, 20-40 min)

**You:** "I want to build [X]"

**Orchestrator:** Asks 3-5 clarifying questions

**Output:** Clear objective in SESSION_STATE.md

**Quality gate:** Both agree on:
- What problem we're solving
- What's in/out of scope
- What success looks like

---

### Stage 2: Decomposition (Orchestrator, 30-60 min)

**Orchestrator:**
1. Analyzes codebase
2. Identifies natural module boundaries
3. Maps dependencies
4. Generates worker assignments (1 per module)

**You:** Review the plan:
- [ ] Are modules truly independent?
- [ ] Any circular dependencies?
- [ ] Does critical path make sense?
- [ ] Are interfaces defined clearly?

**Output:**
- `BUILD_STATE_SESSION.md` with all workers tracked
- `assignments/WORKER_[N]_ASSIGNMENT.md` for each worker
- `DECOMPOSITION_REPORT.md` with execution plan

---

### Stage 3: Worker Execution (Parallel)

**You:**
1. Open new conversation for Worker 1
2. Paste WORKER_1_ASSIGNMENT.md
3. Say: "Execute this assignment"
4. Repeat for Workers 2, 3, 4...

**Each worker:**
1. Reads assignment
2. Updates BUILD_STATE_SESSION.md → IN_PROGRESS
3. Implements code (100-300 LOC, 1-2 files)
4. Tests work
5. Generates W[N]_SUMMARY.md
6. Updates BUILD_STATE_SESSION.md → REVIEW

**If blocked:**
- Worker generates W[N]_ERROR_LOG.md with error code
- Updates status → BLOCKED
- Tells you: "BLOCKED: E[code]. Report at [path]."

**Monitor progress from orchestrator:**
```bash
python3 build_tracker.py --orchestrator con_ORCH --watch
```

---

### Stage 4: Integration (Orchestrator, 15-45 min per worker)

**You:** Return to orchestrator, say "Worker 1 complete"

**Orchestrator:**
1. Reads W1_SUMMARY.md
2. Reviews code changes
3. Validates interfaces match spec
4. Runs integration tests
5. Decision:
   - ✅ ACCEPT: Integrate as-is
   - 🔄 REVISE: Minor fixes by orchestrator
   - ❌ REJECT: Send back to worker
6. Updates BUILD_STATE_SESSION.md → INTEGRATED
7. Captures lessons learned

**Repeat for each worker, one at a time**

**Integration pattern:** Incremental (one worker at a time), not big-bang

---

### Stage 5: Validation (Orchestrator, 30-60 min)

After ALL workers integrated:

1. **System test** - End-to-end flows work?
2. **Principle check** - Against `file 'Knowledge/architectural/architectural_principles.md'`
3. **Documentation** - Update READMEs, docs
4. **After-action report** - Comprehensive retrospective

**Quality gate:**
- [ ] All workers integrated
- [ ] System tests pass
- [ ] Principles validated
- [ ] Documentation current
- [ ] Lessons documented

---

### Stage 6: Archival (Orchestrator, 5 min)

Move build artifacts to permanent storage:

```bash
mv /home/workspace/N5/logs/builds/[build-name] \
   /home/workspace/N5/logs/threads/$(date +%Y-%m-%d)_[build-name]_[id]/
```

---

## Key Design Patterns

### Pattern 1: Interface-First Design

**Before implementation starts:**
1. Orchestrator defines ALL interfaces
2. Includes exact function signatures in worker assignments
3. Workers implement to contract
4. No surprises during integration

**Example:**
```python
# Orchestrator defines in shared interfaces doc:
class AuthService:
    def authenticate(self, username: str, password: str) -> Token: ...
    def validate_token(self, token: str) -> User: ...
```

### Pattern 2: Rule-of-Two (P0)

**Each worker limited to:**
- Max 2 files actively modified
- Max 5 files for reference
- <500 LOC total

**If bigger:** Split into more workers

### Pattern 3: Incremental Integration

**NOT:** Merge all workers at once → "something broke"

**YES:** Merge one at a time:
1. Merge W1 → Test ✓
2. Merge W2 → Test ✓
3. Merge W3 → Test ✓

**Benefit:** Easy to pinpoint failures

### Pattern 4: Risk-Based Prioritization

**High-risk modules first:**
- External API integrations
- Performance-critical code
- Novel algorithms
- Multi-system coordination

**Why:** Fail fast, avoid late-stage rework

### Pattern 5: Explicit Assumptions

**In every WORKER_ASSIGNMENT.md:**
```
## Assumptions
- Authentication service is already deployed
- Database schema matches version 2.3
- Max 10K requests/second
- Users are pre-validated upstream
```

**Worker validates assumptions first, documents new ones discovered**

---

## File Organization

### During Active Build

```
/home/workspace/N5/logs/builds/[build-name]/
├── BUILD_STATE_SESSION.md          # Central coordination
├── assignments/
│   ├── WORKER_1_ASSIGNMENT.md      # V opens in new conversation
│   ├── WORKER_2_ASSIGNMENT.md
│   └── WORKER_N_ASSIGNMENT.md
├── workers/
│   ├── W1_SUMMARY.md               # Worker writes when complete
│   ├── W1_ERROR_LOG.md             # If errors occur
│   └── W2_SUMMARY.md
└── integration/
    └── INTEGRATION_LOG.md           # Orchestrator tracks integration
```

### After Completion

```
/home/workspace/N5/logs/threads/[date]_[build-name]_[id]/
[Entire build folder moves here]
```

### Implementation Code

```
/home/workspace/[wherever-it-belongs]/
[Workers write actual code to final destination]
```

---

## Communication Patterns

### Pattern A: Orchestrator → Worker (Assignment)

**Orchestrator:** "Worker 2 can begin now. Open WORKER_2_ASSIGNMENT.md."

**You:** [Opens new conversation, pastes assignment]

**Worker 2:** [Starts work]

---

### Pattern B: Worker → Orchestrator (Completion)

**Worker 2:** "Complete. Summary at W2_SUMMARY.md"

**You:** [Returns to orchestrator] "Worker 2 done"

**Orchestrator:** [Reads summary, integrates]

---

### Pattern C: Worker → Orchestrator (Blocker)

**Worker 2:** "BLOCKED: E104. Report at W2_ERROR_LOG.md"

**You:** [Returns to orchestrator] "Worker 2 blocked, error E104"

**Orchestrator:** [Reads report, provides clarification]

**Orchestrator:** "Update Worker 2 assignment with clarification at [path]"

**You:** [Adds updated file to Worker 2 conversation]

**Worker 2:** [Resumes work]

---

## Success Metrics

**Track to improve over time:**

| Metric | Target | Formula |
|--------|--------|---------|
| Parallel efficiency | >60% | `1 - (parallel_time / serial_time)` |
| Rework rate | <20% | `reworked_workers / total_workers` |
| Integration failures | <10% | `failed_merges / total_merges` |
| Context violations | 0% | `workers_exceeding_2_files / total_workers` |
| Principle compliance | >90% | `workers_passing_checks / total_workers` |

---

## Example Walkthrough

### Task: Build User Auth System (1500 LOC, 6 files)

**Decomposition (6 workers):**

**Batch 1 (foundation):**
- Worker 1: `models/user.py` (250 LOC) [low complexity]

**Batch 2 (parallel utilities):**
- Worker 2: `auth/jwt.py` (200 LOC) [medium complexity]
- Worker 3: `auth/password.py` (150 LOC) [low complexity]

**Batch 3 (parallel endpoints):**
- Worker 4: `api/login.py` (250 LOC) [medium complexity]
- Worker 5: `api/register.py` (250 LOC) [medium complexity]

**Batch 4 (testing):**
- Worker 6: `tests/test_auth.py` (400 LOC) [high complexity]

**Critical Path:** W1 → W2 → W4 → W6

**Timeline:**
- Serial: 6 hours
- Parallel: 2.5 hours (58% time reduction)

**Quality:**
- All tests pass
- No principle violations
- Zero rework needed

---

## Common Pitfalls & Fixes

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Over-decomposition | 20 workers for 1000 LOC | Aim for 200-400 LOC per worker |
| Under-decomposition | 1 worker for 2000 LOC | Follow Rule-of-Two (P0) |
| Unclear interfaces | Workers make incompatible assumptions | Interface-First Design |
| Hidden dependencies | Worker blocked waiting | Data Flow Mapping |
| Big-bang integration | Merge all, tests fail, debug hell | Incremental Integration |
| Vague assignments | Worker unclear on scope | Use task_deconstructor |
| No quality gates | Merge broken code | Test + principle check before every merge |

---

## Error System

**Error Codes:**
- **E0xx:** Assignment/Setup (E001 = scope unclear, E004 = missing acceptance criteria)
- **E1xx:** Dependencies/Interfaces (E104 = API signature mismatch)
- **E2xx:** Implementation Quality (E203 = doesn't meet style standards)
- **E3xx:** Integration (E302 = breaks existing functionality)
- **E4xx:** Testing (E403 = coverage below threshold)
- **E5xx:** Principles/Architecture (E501 = principle violation)
- **W0xx-W5xx:** Warnings (non-blocking)

**When blocked:**
1. Worker generates W[N]_ERROR_LOG.md with code
2. Updates BUILD_STATE_SESSION.md → BLOCKED
3. Orchestrator reads report, provides resolution
4. Worker resumes after clarification

---

## Tool Quick Reference

| Need | Command | Output |
|------|---------|--------|
| Decompose task | `task_deconstructor.py --orchestrator con_ORCH` | Assignments + plan |
| Monitor progress | `build_tracker.py --orchestrator con_ORCH --watch` | Live dashboard |
| Visualize | `dependency_graph.py --orchestrator con_ORCH` | D2 diagram |
| Assign worker | `orchestrator.py assign "Task" --to con_W` | Assignment created |
| Check worker | `orchestrator.py check-worker con_W` | Status + progress |
| Review changes | `orchestrator.py review-changes con_W` | File changes |
| Approve worker | `orchestrator.py approve con_W` | Work approved |

---

## Documentation Deep Dive

### Core System Docs

**`file 'N5/prefs/operations/distributed-builds/SYSTEM_OVERVIEW.md'`**
- What it is, when to use
- Quick start (5 minutes)
- All 6 stages explained
- Roles, components, file locations
- Success metrics, common pitfalls

**`file 'N5/prefs/operations/distributed-builds/protocol.md'`**
- High-level workflow
- Roles and responsibilities
- Each stage in detail
- Communication patterns
- Best practices (DO/DON'T)
- Quality gates, success criteria

**`file 'Documents/System/HOW_TO_USE_DISTRIBUTED_BUILDS.md'`**
- Step-by-step practical guide
- Example walkthrough (auth system)
- Decision framework (when to use)
- Design patterns
- Advanced techniques
- Troubleshooting

**`file 'Knowledge/patterns/distributed_build_patterns.md'`**
- 8 design patterns with examples
- Efficient user behaviors
- Decision framework
- Common pitfalls
- Success metrics
- Tool reference

### Supporting Docs

**`file 'N5/prefs/operations/distributed-builds/error-tracking-guide.md'`**
- Complete error code reference
- Severity levels
- Resolution procedures
- Logging format
- Recovery protocols

**`file 'N5/prefs/operations/distributed-builds/troubleshooting.md'`**
- Common issues by symptom
- Root cause analysis
- Resolution steps
- Prevention strategies

---

## Key Principles

**From `file 'Knowledge/architectural/architectural_principles.md'`:**

**P0 (Rule-of-Two):** Max 2 files per worker  
**P2 (SSOT):** Orchestrator is authoritative  
**P7 (Dry-Run):** Test approach before full implementation  
**P15 (Complete):** Orchestrator verifies done = actually done  
**P18 (Verify State):** Orchestrator tests integration  
**P19 (Error Handling):** Workers include try/except, logging  
**P20 (Modular):** Natural boundaries, bounded contexts  
**P21 (Explicit Assumptions):** Document all assumptions

---

## Next Steps for Your Use

**First time using distributed builds?**

1. **Identify a pilot build:**
   - 800-1200 LOC
   - 3-4 clear modules
   - New feature (greenfield > refactor for first build)

2. **Start orchestrator conversation:**
   - Load Vibe Builder persona
   - Say: "I want to build [X]"
   - Let orchestrator guide framing

3. **Follow protocol exactly:**
   - Don't improvise on first build
   - Document everything
   - Review lessons at end

4. **Refine templates:**
   - Based on what worked/didn't work
   - Update for next build

---

## Philosophy

**Traditional problem:**
- 1000+ LOC in one conversation = LLM loses track
- Multiple modules = cognitive overload
- Complex dependencies = more bugs

**Distributed solution:**
- Each worker = 100-300 LOC = manageable context
- Bounded scope = full attention
- Clear interfaces = fewer integration bugs
- Incremental testing = catch issues early

**Trade-off:**
- Time: +30-60 min coordination overhead
- Benefit: Fewer bugs, better architecture, maintainable systems

**Worth it when:** Any critical change >500 LOC

---

## Loaded Files Reference

**All files now loaded in this conversation:**

Core system:
- `file 'Documents/N5.md'`
- `file 'N5/prefs/prefs.md'`

Distributed builds documentation:
- `file 'N5/prefs/operations/distributed-builds/SYSTEM_OVERVIEW.md'`
- `file 'N5/prefs/operations/distributed-builds/protocol.md'`
- `file 'Documents/System/HOW_TO_USE_DISTRIBUTED_BUILDS.md'`
- `file 'Knowledge/patterns/distributed_build_patterns.md'`

Scripts:
- `file 'N5/scripts/orchestrator.py'`
- `file 'N5/scripts/build_tracker.py'`
- `file 'N5/scripts/task_deconstructor.py'`

Templates:
- `file 'N5/prefs/operations/distributed-builds/templates/WORKER_ASSIGNMENT.md'`
- `file 'N5/prefs/operations/distributed-builds/templates/BUILD_STATE_SESSION.md'`

**Ready to use!**

---

**Generated:** 2025-10-18 13:47 ET  
**For:** V  
**By:** Vibe Teacher (Zo)
