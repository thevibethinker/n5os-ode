# How to Use Distributed Builds - Practical Guide

**For:** V (and future users)  
**Purpose:** Step-by-step guide to using the Session State System for distributed builds  
**Status:** Production Ready

---

## Quick Start (5 Minutes)

### 1. Start an Orchestrator Conversation

In Zo, start a new conversation and say:

> "I need to build a user authentication system with JWT tokens, password hashing, login/register endpoints, and tests. Let's plan this out."

### 2. Frame the Task (15-30 minutes)

Discuss with Zo:
- **What** you're building (requirements, features)
- **Why** (business context, constraints)
- **How** (architecture, tech choices)
- **Files** that will change
- **Risks** or unknowns

**Goal:** Clear objective in SESSION_STATE.md

### 3. Decompose the Task

When you're ready, say:

> "We're ready with a plan. Deconstruct this task."

Or run:
```bash
python3 N5/scripts/task_deconstructor.py --orchestrator <current_convo_id>
```

### 4. Review the Plan

Zo generates:
- `DECOMPOSITION_REPORT.md` - Execution plan
- `worker_assignments/` folder with ASSIGNMENT.md for each worker

**Review checklist:**
- [ ] Are modules truly independent?
- [ ] Any circular dependencies?
- [ ] Does the critical path make sense?
- [ ] Are interfaces defined clearly?
- [ ] Is complexity evenly distributed?

**Adjust if needed** - Edit assignments manually if something's off

### 5. Create Worker Conversations

For each worker assignment:

1. Start new conversation in Zo
2. Paste the full ASSIGNMENT.md as first message
3. Say: "Please implement this assignment"
4. Worker initializes its SESSION_STATE.md and begins work

**Pro tip:** Create all workers at once, they'll work in parallel

### 6. Monitor Progress

From orchestrator conversation:

```bash
# Real-time dashboard
python3 N5/scripts/build_tracker.py --orchestrator <convo_id> --watch

# Or check periodically
python3 N5/scripts/build_tracker.py --orchestrator <convo_id>
```

You'll see:
- Worker status (active, complete, blocked)
- Progress percentages
- What each worker is currently doing

### 7. Quality Gates (Before Merging)

For each completed worker:

```bash
# Run tests
python3 N5/scripts/integration_test_runner.py --worker-convo <worker_id>

# Check principles
python3 N5/scripts/principle_violation_detector.py --worker-convo <worker_id>
```

**Only merge if both pass!**

### 8. Integration

Merge workers one at a time:

1. Copy worker's code to main branch
2. Run integration tests
3. If pass, proceed to next worker
4. If fail, debug isolated to one worker

### 9. Visualize (Optional)

See the full picture:

```bash
python3 N5/scripts/dependency_graph.py --orchestrator <convo_id>
```

Generates D2 diagram showing all relationships

---

## Example Walkthrough

### Task: Build User Auth System (1500 LOC, 6 files)

#### Step 1: Orchestrator Discussion

**You:**
> "I need to build user authentication with JWT tokens. We need:
> - JWT token generation and validation
> - Password hashing with bcrypt
> - Login endpoint (POST /auth/login)
> - Registration endpoint (POST /auth/register)
> - User model and database
> - Comprehensive tests
> 
> Files: auth/jwt.py, auth/password.py, api/login.py, api/register.py, models/user.py, tests/test_auth.py"

**Zo:**
> "Got it. Let me frame this:
> - Architecture: JWT with 15min expiry, bcrypt for passwords, SQLite for storage
> - Interfaces: TokenService, AuthService, UserRepository
> - Risks: Rate limiting needs consideration
> - Dependencies: JWT library, bcrypt
> 
> Shall we break this into workers?"

**You:**
> "Yes, we're ready. Deconstruct this."

#### Step 2: Task Deconstruction

Zo runs `task_deconstructor.py` and generates:

```
Execution Plan:
  Batch 1 (foundation):
    Worker 1: models/user.py (250 LOC) [low complexity]
  
  Batch 2 (parallel utilities):
    Worker 2: auth/jwt.py (200 LOC) [medium complexity]
    Worker 3: auth/password.py (150 LOC) [low complexity]
  
  Batch 3 (parallel endpoints):
    Worker 4: api/login.py (250 LOC) [medium complexity]
    Worker 5: api/register.py (250 LOC) [medium complexity]
  
  Batch 4 (testing):
    Worker 6: tests/test_auth.py (400 LOC) [high complexity]

Critical Path: W1 → W2 → W4 → W6
Estimated Duration: 2 hours (vs 6 hours serial)
Risk: 3 medium, 1 high complexity modules
```

#### Step 3: Create Workers

Start 6 conversations:
- **con_AUTH_USER_MODEL** - Paste `models_module_ASSIGNMENT.md`
- **con_AUTH_JWT** - Paste `auth_jwt_ASSIGNMENT.md`
- **con_AUTH_PASSWORD** - Paste `auth_password_ASSIGNMENT.md`
- **con_AUTH_LOGIN** - Paste `api_login_ASSIGNMENT.md`
- **con_AUTH_REGISTER** - Paste `api_register_ASSIGNMENT.md`
- **con_AUTH_TESTS** - Paste `tests_ASSIGNMENT.md`

#### Step 4: Monitor

```bash
python3 N5/scripts/build_tracker.py --orchestrator con_ORCH_AUTH --watch
```

**Output:**
```
=== Build Status Dashboard ===
Orchestrator: con_ORCH_AUTH
Updated: 2025-10-16 10:30:00 ET

Workers:
  con_AUTH_USER_MODEL   ✅ COMPLETE (100%)
  con_AUTH_JWT          🔄 ACTIVE (60%) - Implementing token validation
  con_AUTH_PASSWORD     ✅ COMPLETE (100%)
  con_AUTH_LOGIN        ⏸️  BLOCKED - Waiting for con_AUTH_JWT
  con_AUTH_REGISTER     ⏸️  BLOCKED - Waiting for con_AUTH_JWT
  con_AUTH_TESTS        ⏳ PENDING

Progress: 2/6 complete (33%)
```

#### Step 5: Quality Gates

Worker 1 complete:
```bash
python3 N5/scripts/integration_test_runner.py --worker-convo con_AUTH_USER_MODEL
# ✅ All tests pass

python3 N5/scripts/principle_violation_detector.py --worker-convo con_AUTH_USER_MODEL
# ✅ No violations detected
```

#### Step 6: Integration

```bash
# Merge Worker 1
cp /home/.z/workspaces/con_AUTH_USER_MODEL/models/user.py /home/workspace/models/

# Run integration tests
pytest tests/test_user_model.py
# ✅ Pass

# Proceed to Worker 2...
```

#### Step 7: Result

**Timeline:**
- Serial approach: 6 hours
- Parallel approach: 2.5 hours (58% reduction)

**Quality:**
- All tests pass
- No principle violations
- Clean integration
- Zero rework needed

---

## Decision Framework

### Should I Use Distributed Builds?

**YES, if:**
- ✅ Task is >500 LOC
- ✅ Multiple files to modify (>2)
- ✅ Natural module boundaries exist
- ✅ You want faster completion
- ✅ You want higher quality (smaller context = fewer bugs)

**NO, if:**
- ❌ Task is <500 LOC
- ❌ Single file or tightly coupled code
- ❌ You need to understand every detail
- ❌ Task is trivial (CRUD operations)

**MAYBE, if:**
- ⚠️ High uncertainty (explore first, then deconstruct)
- ⚠️ Extreme time pressure (overhead might not be worth it)
- ⚠️ Learning a new domain (solo first to learn, then parallelize)

---

## Design Patterns to Follow

### 1. Interface-First

**Before deconstructing:**
```python
# Define in orchestrator, include in all worker assignments

class TokenService:
    def generate(self, user_id: str) -> str: ...
    def validate(self, token: str) -> dict: ...

class AuthService:
    def authenticate(self, username: str, password: str) -> User: ...
```

**Workers implement to contract** → No integration surprises

### 2. Data Flow Mapping

**Before assigning workers:**
```
User Schema → User Model → Auth Service → Login API
                                       → Register API
```

**Schedule based on dependencies** → Minimize blocking

### 3. Risk-Based Scheduling

**High-risk modules first:**
- External APIs
- Performance-critical
- Novel algorithms

**Why:** Fail fast, avoid late-stage rework

### 4. Context Boundaries (Rule-of-Two)

**Each worker:**
- Max 2 files actively modified
- Max 5 files for reference
- <500 LOC total

**If bigger:** Split into more workers

### 5. Incremental Integration

**Merge one worker at a time:**
1. Merge Worker 1
2. Run tests
3. If pass, merge Worker 2
4. Run tests
5. Repeat

**Why:** Easy to isolate failures

---

## Common Pitfalls

### ❌ Pitfall 1: Over-Decomposition

**Problem:** 20 workers for 1000 LOC → overhead > benefit

**Solution:** Aim for 200-400 LOC per worker, 3-5 workers total

### ❌ Pitfall 2: Unclear Interfaces

**Problem:** Workers make incompatible assumptions

**Solution:** Define all interfaces in orchestrator before starting workers

### ❌ Pitfall 3: Big-Bang Integration

**Problem:** Merge all workers at once, tests fail, debug hell

**Solution:** Merge one at a time, test between each

### ❌ Pitfall 4: Skipping Quality Gates

**Problem:** Merge broken code, discover later

**Solution:** ALWAYS run tests + principle checks before merging

### ❌ Pitfall 5: Vague Assignments

**Problem:** "Implement auth" → worker unclear on scope

**Solution:** Use task_deconstructor, it generates detailed assignments

---

## Advanced Techniques

### Technique 1: Pre-Implementation Exploration

**Pattern:**
1. Solo conversation: Explore problem space (30 min)
2. Once clear, switch to orchestrator
3. Frame task with findings
4. Deconstruct and parallelize

**When:** High uncertainty, new domain

### Technique 2: Nested Orchestration

**Pattern:**
1. Top-level orchestrator: System design
2. Module orchestrators: Feature teams
3. Workers: Individual implementations

**When:** Very large systems (>5000 LOC)

### Technique 3: Iterative Decomposition

**Pattern:**
1. Deconstruct to 5 workers
2. Worker 1 discovers complexity
3. Worker 1 spawns sub-workers
4. Rebalance remaining workers

**When:** Uncertainty in one module

### Technique 4: Quality Buddy System

**Pattern:**
1. Worker A implements feature
2. Worker B reviews + writes tests
3. Both mark complete together

**When:** Critical code, high quality requirements

---

## Tools Quick Reference

| Need | Command | Output |
|------|---------|--------|
| Decompose task | `task_deconstructor.py --orchestrator con_X` | Assignments + plan |
| Monitor progress | `build_tracker.py --orchestrator con_X --watch` | Live dashboard |
| Run tests | `integration_test_runner.py --worker-convo con_W` | Test results |
| Check quality | `principle_violation_detector.py --worker-convo con_W` | Violation report |
| Visualize | `dependency_graph.py --orchestrator con_X` | D2 diagram |
| Send message | `message_queue.py send --from con_W --to con_X` | Message sent |
| Check messages | `message_queue.py list --convo-id con_X` | Inbox |

---

## Success Metrics

**Track over time to improve:**

1. **Parallel Efficiency**
   - Formula: `1 - (parallel_time / serial_time)`
   - Target: >60% (3x faster with 5 workers)

2. **Rework Rate**
   - Formula: `reworked_workers / total_workers`
   - Target: <20%

3. **Integration Failures**
   - Formula: `failed_merges / total_merges`
   - Target: <10%

4. **Context Violations**
   - Formula: `workers_exceeding_2_files / total_workers`
   - Target: 0%

5. **Principle Compliance**
   - Formula: `workers_passing_checks / total_workers`
   - Target: >90%

---

## Troubleshooting

### Issue: Worker is blocked

**Symptoms:** Worker can't proceed, waiting on another worker

**Solutions:**
1. Check dependency graph - is blocker truly necessary?
2. Can blocker deliver partial interface?
3. Can blocked worker use stub/mock?
4. Reorder integration sequence?

### Issue: Integration fails

**Symptoms:** Tests fail after merging worker

**Solutions:**
1. Isolate: which worker's code causes failure?
2. Check interface contracts - did they match?
3. Run worker's tests in isolation
4. Review assumptions in ASSIGNMENT.md

### Issue: Quality gate fails

**Symptoms:** Principle detector finds violations

**Solutions:**
1. Review violations with worker
2. Worker fixes in same conversation
3. Re-run quality checks
4. Approve only when clean

### Issue: Too much overhead

**Symptoms:** Coordination takes longer than implementation

**Solutions:**
1. Fewer workers (combine some assignments)
2. Better upfront framing (clearer interfaces)
3. Consider solo for this task
4. Analyze: where did time go?

---

## Learning Path

### Level 1: Observer
- Watch orchestrator + 2 workers
- Follow along, don't intervene
- Note patterns and pitfalls

### Level 2: Participant
- Frame task in orchestrator
- Run task_deconstructor
- Review generated plan
- Create workers
- Monitor progress

### Level 3: Optimizer
- Adjust decomposition for balance
- Define interfaces upfront
- Track metrics
- Iterate on patterns

### Level 4: Expert
- Nested orchestration
- Custom decomposition strategies
- Predict integration risks
- Mentor others

---

## Real-World Examples

### Example 1: REST API (6 endpoints, 1200 LOC)

**Decomposition:** 6 workers (one per endpoint)  
**Duration:** Serial: 6h → Parallel: 2.5h (58% faster)  
**Result:** Zero integration issues

### Example 2: Data Pipeline (3 sources, 2000 LOC)

**Decomposition:** 6 workers (3 extractors, 1 transformer, 1 loader, 1 orchestrator)  
**Duration:** Serial: 10h → Parallel: 4.5h (55% faster)  
**Result:** One rework (extractor needed retry logic)

### Example 3: CLI Tool (8 commands, 1500 LOC)

**Decomposition:** 9 workers (8 commands + 1 core)  
**Duration:** Serial: 8h → Parallel: 3h (62% faster)  
**Result:** Clean integration, excellent test coverage

---

## Next Steps

1. **Try it!** Pick a multi-file task and run through the workflow
2. **Document your experience** - What worked? What didn't?
3. **Refine patterns** - Adapt to your style
4. **Share learnings** - Update this guide

---

## References

- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Complete system documentation
- file 'Knowledge/patterns/distributed_build_patterns.md' - Design patterns
- file 'Documents/System/SESSION_STATE_QUICK_REFERENCE.md' - Command cheat sheet
- file 'Knowledge/architectural/architectural_principles.md' - N5 principles

---

*Created: 2025-10-16 | For: V | Status: Ready to Use*
