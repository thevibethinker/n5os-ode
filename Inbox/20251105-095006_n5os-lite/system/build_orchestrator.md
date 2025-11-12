# N5OS Lite Build Orchestrator

**Version:** 1.0  
**Purpose:** Coordinate parallel AI workers for complex system builds  
**Status:** Advanced pattern for multi-component projects

---

## What Is This?

The Build Orchestrator decomposes large system builds into discrete, parallelizable tasks executed by independent AI worker conversations.

**Key Innovation:** Instead of one long conversation doing everything sequentially, spawn multiple focused conversations working in parallel, coordinated by an orchestrator.

---

## Architecture

```
Orchestrator Conversation
├── Spawns → Worker 1 (independent conversation)
├── Spawns → Worker 2 (independent conversation)  
├── Spawns → Worker 3 (independent conversation)
└── Monitors, validates, integrates results
```

### Components

1. **Orchestrator Conversation**
   - Breaks down work into worker briefs
   - Spawns worker conversations
   - Tracks progress
   - Validates deliverables
   - Integrates results

2. **Worker Briefs** (Markdown files)
   - Self-contained task specifications
   - Context, deliverables, tests
   - Success criteria
   - Related principles

3. **Worker Conversations**
   - Independent AI sessions
   - Execute one specific brief
   - Deliver artifacts
   - Report completion

4. **Progress Tracking**
   - Worker status monitoring
   - Blocker identification
   - Dependency management

---

## When to Use

✅ **Perfect for:**
- Multi-component system builds (5+ scripts/modules)
- Independent module development
- Large refactoring projects
- Test suite creation
- Documentation generation

❌ **Not ideal for:**
- Simple single-file scripts
- Tightly coupled changes
- Exploratory coding
- Quick prototypes
- Sequential dependent work

---

## Workflow

### Phase 1: Planning (Orchestrator)

1. **Decompose system** into discrete tasks
   - Each task = 1 worker
   - Minimize dependencies
   - Define clear deliverables

2. **Create worker briefs** (one per task)
   - Mission statement
   - Deliverables list
   - Success criteria
   - Implementation guidance
   - Related principles

3. **Map dependencies**
   - Which workers can run in parallel?
   - Which must wait for others?
   - Create dependency graph

4. **Estimate timeline**
   - Per-worker estimates
   - Total sequential time
   - Total parallel time

### Phase 2: Execution (Orchestrator + Workers)

1. **Spawn parallel workers**
   - Start all independent workers simultaneously
   - Pass them their briefs
   - Track conversation IDs

2. **Monitor progress**
   - Check worker status regularly
   - Identify blockers early
   - Provide clarifications as needed

3. **Validate deliverables**
   - After each worker completes
   - Verify all deliverables exist
   - Run basic quality checks

4. **Spawn dependent workers**
   - As prerequisites complete
   - Maximum parallelization

### Phase 3: Integration (Orchestrator)

1. **Collect all artifacts**
   - Verify file locations
   - Check completeness

2. **Run integration tests**
   - Do components work together?
   - Any conflicts or gaps?

3. **Validate system cohesion**
   - Architecture matches plan?
   - Principles compliance?
   - Quality standards met?

4. **Document & Archive**
   - Create completion report
   - Archive worker conversations
   - Update project docs

---

## Example: 5-Worker Build

**Goal:** Build a CLI tool with database backend

```
Worker 1: Database Schema
├─ Deliverables: schema.sql, migrations
├─ Duration: 20 min
└─ Dependencies: None

Worker 2: Core Models (depends on W1)
├─ Deliverables: models.py, validators
├─ Duration: 30 min  
└─ Dependencies: W1 complete

Worker 3: API Layer (depends on W2)
├─ Deliverables: api.py, error handling
├─ Duration: 20 min
└─ Dependencies: W2 complete

Worker 4: CLI Interface (depends on W2)
├─ Deliverables: cli.py, commands
├─ Duration: 20 min
└─ Dependencies: W2 complete

Worker 5: Tests & Docs (depends on W3, W4)
├─ Deliverables: test_suite.py, README.md
├─ Duration: 15 min
└─ Dependencies: W3, W4 complete
```

**Timeline:**
- W1: 20 min
- W2 (after W1): 30 min
- W3, W4 (parallel after W2): 20 min each
- W5 (after W3, W4): 15 min

**Total: ~85 min** (vs 105 min sequential)  
**Speedup: 19%**

---

## Worker Brief Structure

```markdown
# WORKER_N: Task Name

## Mission
[One sentence: what is this worker building?]

## Context
[Background information worker needs]

## Deliverables
1. /path/to/file1.py - Description
2. /path/to/file2.md - Description

## Success Criteria
- [ ] All deliverables exist
- [ ] Tests pass
- [ ] Follows principles P15, P16

## Implementation Guide

### Step 1: [First step]
[Detailed instructions]

### Step 2: [Second step]
[Detailed instructions]

### Step 3: Testing
[How to verify it works]

## Dependencies
- Worker X must complete first
- Requires file from Worker Y

## Related Principles
- P15: Complete Before Claiming
- P2: Single Source of Truth
- P20: Modular Design

## Estimated Duration
30 minutes

---

*This is Worker N of M in the [Project Name] build*
```

---

## Progress Tracking Template

```markdown
# Orchestrator Monitor

**Project:** Project Name  
**Started:** 2025-11-03 08:00  
**Status:** In Progress

## Workers

### Worker 1: Database Schema
- **Status:** ✅ Complete
- **Conversation:** con_ABC123
- **Duration:** 18 min (est: 20)
- **Deliverables:** All verified

### Worker 2: Core Models
- **Status:** 🔄 In Progress (80%)
- **Conversation:** con_DEF456
- **Duration:** 25 min so far (est: 30)
- **Blockers:** None

### Worker 3: API Layer
- **Status:** ⏸️  Waiting (depends on W2)
- **Conversation:** Not started
- **Dependencies:** W2 must complete

## Timeline

```
W1 [████████████] ✅ 18/20 min
W2 [██████████░░] 🔄 25/30 min  
W3 [            ] ⏸️  Waiting
```

## Next Actions
1. Monitor W2 completion
2. Spawn W3 immediately after W2
3. Begin integration planning
```

---

## Benefits

✅ **20-40% faster** for multi-component builds  
✅ **Better isolation** - Workers can't conflict  
✅ **Clearer structure** - Explicit task breakdown  
✅ **Trackable progress** - Know exactly where you are  
✅ **Resumable** - Can pause/continue orchestration  
✅ **Reusable briefs** - Save for similar projects  
✅ **Quality focus** - Each worker has clear criteria  

---

## Design Principles

**P2: Single Source of Truth**
- Worker briefs are SSOT for that task
- Progress tracker is SSOT for overall status

**P15: Complete Before Claiming**
- Workers must deliver ALL specified artifacts
- Validation checks before marking complete

**P20: Modular Design**
- Workers are independent, self-contained
- Minimal coupling between workers

**P36: Orchestration Pattern**
- Coordinator spawns specialists
- Clear phase boundaries
- Explicit success criteria

---

## Common Patterns

### Sequential Chain
```
W1 → W2 → W3 → W4
```
Use when: Strong dependencies

### Parallel Batch
```
      ┌─ W2
W1 ─┼─ W3
      └─ W4
```
Use when: Independent tasks after setup

### Diamond
```
      ┌─ W2 ─┐
W1 ─┤       ├─ W5
      └─ W3 ─┘
        │
        W4
```
Use when: Converging streams

---

## Troubleshooting

**Worker stalled?**
- Check for blockers in worker conversation
- Verify dependencies were met
- Clarify ambiguous brief sections

**Integration failures?**
- Validate each component individually first
- Check import paths and dependencies
- Review architectural principles compliance

**Timing way off?**
- Adjust estimates for future projects
- Break down large workers into smaller ones
- Check for hidden complexity

---

## Advanced Techniques

### Dynamic Worker Generation
Orchestrator creates worker briefs on-the-fly based on discovered requirements.

### Conditional Workflows
```python
if worker_1_output == "complex":
    spawn(worker_2a)  # Complex path
else:
    spawn(worker_2b)  # Simple path
```

### Worker Retries
If worker fails, spawn replacement with updated brief incorporating lessons learned.

---

## Templates & Examples

**See:**
- `examples/worker_brief_template.md` - Standard brief format
- `examples/orchestrator_monitor_template.md` - Progress tracker
- `examples/5_worker_build/` - Complete example project

---

## Related

- System: `state_management.md` - Worker state tracking
- Principles: P36 (Orchestration Pattern)
- Principles: P15 (Complete Before Claiming)
- Principles: P20 (Modular Design)

---

**The orchestrator pattern is the highest leverage technique for building complex systems with AI assistance.**

*Last Updated: 2025-11-03*
