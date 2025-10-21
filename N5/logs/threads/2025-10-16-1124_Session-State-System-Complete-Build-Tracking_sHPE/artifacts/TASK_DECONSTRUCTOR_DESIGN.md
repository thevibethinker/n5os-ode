# Task Deconstructor - Design Document

**Purpose:** Intelligently decompose complex tasks into parallel/sequential worker conversations  
**Date:** 2025-10-16  
**Status:** Design → Implementation

---

## Vision

**User workflow:**
1. Start orchestrator conversation
2. Discuss and frame the task (requirements, constraints, approach)
3. Reach agreement: "We're ready with a plan"
4. Run: `deconstruct task` or `python3 N5/scripts/task_deconstructor.py`
5. System generates:
   - Worker conversation kickoff documents (ASSIGNMENT.md)
   - Dependency graph (what blocks what)
   - Execution sequence (parallel batches + sequential ordering)
   - Estimated effort/risk per worker
6. User reviews plan, adjusts if needed
7. User creates worker conversations with generated kickoffs
8. Monitor progress from orchestrator

**Goal:** Maximize parallelism, minimize context, catch risks early

---

## Design Patterns for Distributed Builds

### 1. **Modular Decomposition (P20)**
**Pattern:** Break into independent, loosely-coupled modules  
**Why:** Enables parallelism, reduces context per worker  
**How:**
- One module = one worker conversation
- Clear interfaces between modules
- Minimal shared state
- Each worker has <500 LOC scope

**Example:**
```
Bad:  "Build authentication system" (1 worker, 2000 LOC, 8 files)
Good: "Build authentication system" →
      - Worker 1: JWT token generation/validation (200 LOC)
      - Worker 2: Password hashing utilities (150 LOC)
      - Worker 3: Login endpoint (200 LOC)
      - Worker 4: Registration endpoint (200 LOC)
      - Worker 5: Session management (300 LOC)
```

### 2. **Interface-First Design (P2 SSOT)**
**Pattern:** Define interfaces before implementation  
**Why:** Workers can work in parallel without blocking  
**How:**
- Orchestrator defines all interfaces upfront
- Workers implement to interface contracts
- Integration test validates contracts
- No cross-worker dependencies on implementation

**Example:**
```python
# Orchestrator defines in ASSIGNMENT.md:
# auth/interfaces.py
class TokenGenerator:
    def generate(self, user_id: str) -> str: ...
    def validate(self, token: str) -> dict: ...

# Worker 1 implements TokenGenerator
# Worker 3 uses TokenGenerator interface (doesn't wait for impl)
```

### 3. **Data Flow Mapping (P1 Human-Readable)**
**Pattern:** Explicit data dependencies  
**Why:** Identifies bottlenecks, enables scheduling  
**How:**
- Map what data each worker needs
- Map what data each worker produces
- Identify critical path (longest dependency chain)
- Parallelize non-dependent workers

**Example:**
```
DB Schema (Worker 1) 
  ↓
Models (Worker 2)
  ↓ ↘
API (Worker 3)  Tests (Worker 4)

Worker 2,3,4 can start as soon as Worker 1 completes.
Worker 3 and 4 can run in parallel.
```

### 4. **Risk-Based Prioritization**
**Pattern:** Tackle risky/complex workers first  
**Why:** Fail fast, avoid rework  
**How:**
- Flag high-risk workers (new tech, complex logic, external deps)
- Schedule risky workers in early batches
- If risky worker fails, reassess plan before continuing

**Complexity indicators:**
- External API integrations
- Performance-critical code
- Novel algorithms
- Multi-file refactoring

### 5. **Context Boundaries (P0 Rule-of-Two)**
**Pattern:** Limit worker scope to 2 files actively edited  
**Why:** Prevents context overload, maintains quality  
**How:**
- Each worker assignment: ≤2 files to modify
- Read-only context: up to 5 related files
- Larger tasks → more workers

### 6. **Incremental Integration (P7 Dry-Run)**
**Pattern:** Integrate workers one at a time  
**Why:** Isolate failures, easier debugging  
**How:**
- Merge workers sequentially (even if built in parallel)
- Run integration tests after each merge
- If tests fail, fix before next merge
- Track integration order in SESSION_STATE

### 7. **Explicit Assumptions (P21)**
**Pattern:** Document all assumptions in worker kickoff  
**Why:** Prevents divergence, enables validation  
**How:**
- Orchestrator lists assumptions in ASSIGNMENT.md
- Worker validates assumptions first
- Worker documents new assumptions discovered
- Orchestrator reviews assumptions during approval

---

## Task Deconstructor Algorithm

### Input (from orchestrator conversation):
1. Overall objective
2. Approach/architecture (from discussion)
3. Files to modify
4. Success criteria

### Analysis Phase:
1. **Identify modules** (by file, by feature, by layer)
2. **Build dependency graph** (what needs what)
3. **Estimate complexity** (LOC, risk factors)
4. **Detect parallelism** (independent modules)
5. **Calculate critical path** (longest sequential chain)

### Output:
1. **Execution plan** (batches of parallel workers + sequence)
2. **Worker assignments** (ASSIGNMENT.md for each worker)
3. **Dependency graph** (D2 visualization)
4. **Risk assessment** (complexity/risk per worker)
5. **Estimated timeline** (based on critical path)

---

## Deconstructor Script Design

```python
# N5/scripts/task_deconstructor.py

class TaskDeconstructor:
    def __init__(self, orchestrator_convo_id: str):
        self.orchestrator = orchestrator_convo_id
        self.session_state = self.load_session_state()
    
    def analyze(self):
        """Parse objective, files, discussion to identify modules."""
        # 1. Extract objective from SESSION_STATE
        # 2. Parse files mentioned in conversation
        # 3. Identify natural module boundaries
        # 4. Estimate complexity per module
        return modules
    
    def build_dependency_graph(self, modules):
        """Detect dependencies between modules."""
        # Parse imports, interfaces, data flow
        return graph
    
    def generate_execution_plan(self, modules, graph):
        """Calculate parallel batches and sequence."""
        # Topological sort for sequence
        # Group independent modules into batches
        return plan
    
    def generate_worker_assignments(self, modules, plan):
        """Create ASSIGNMENT.md for each worker."""
        # For each module:
        #   - Objective
        #   - Files to modify
        #   - Interface contracts
        #   - Dependencies (what to wait for)
        #   - Success criteria
        #   - Assumptions
        return assignments
    
    def generate_report(self, plan, assignments):
        """Create human-readable decomposition report."""
        return report
```

---

## Efficient Behaviors for Users

### Pre-Decomposition (Setup Phase):
1. **Discuss architecture first** - Frame approach before decomposing
2. **Define interfaces early** - Specify contracts upfront
3. **Identify risks** - Flag complex/uncertain parts
4. **Estimate scope** - Rough LOC/file counts
5. **Set success criteria** - What does "done" mean?

### During Decomposition:
1. **Review plan before executing** - Check dependencies, adjust if needed
2. **Question parallelism** - "Can these really run independently?"
3. **Validate assumptions** - "What are we assuming here?"
4. **Check critical path** - "What's the longest chain?"

### During Execution:
1. **Monitor from orchestrator** - Use `python3 N5/scripts/build_tracker.py`
2. **Integrate incrementally** - One worker at a time
3. **Run quality checks** - Tests + principle violations before merge
4. **Communicate blockers** - Workers message orchestrator ASAP
5. **Review before approving** - Check output matches assignment

### Post-Execution:
1. **Capture lessons** - What worked? What didn't?
2. **Update principles** - Codify new patterns discovered
3. **Archive conversation lineage** - Track which conversations built what

---

## Decision Framework

**When to deconstruct vs. work solo:**

| Factor | Solo | Deconstruct |
|--------|------|-------------|
| Total LOC | <500 | >500 |
| Files to modify | ≤2 | >2 |
| Independent modules | No | Yes |
| Time pressure | High | Medium/Low |
| Learning goal | Understand all | Ship fast |
| Risk | Low | High (isolate) |

**Rule of thumb:** If it takes >2 hours solo, consider deconstructing.

---

## Integration with Existing System

**Auto-trigger:** Add to orchestrator workflow  
**Command:** `deconstruct task` or `n5 deconstruct`  
**Input:** SESSION_STATE.md (objective, context, files)  
**Output:** Worker kickoff docs + execution plan  
**Validation:** Dependency graph visualization  

---

## Next Steps

1. Implement `task_deconstructor.py` script
2. Add `deconstruct` command to commands.jsonl
3. Create worker assignment template
4. Test on real multi-file task
5. Iterate based on learnings

---

*Design by: V + Vibe Builder*  
*Date: 2025-10-16 06:21 EST*
