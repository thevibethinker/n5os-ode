# Build Orchestrator System

**Purpose:** Parallel AI worker coordination for complex system builds

---

## What Is This?

The Build Orchestrator is a pattern for decomposing large system builds into discrete, parallelizable tasks executed by independent AI worker conversations.

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

1. **Orchestrator** (`orchestrator.py`)
   - Tracks worker conversations in SQLite DB
   - Monitors progress
   - Validates deliverables
   - Resolves blockers

2. **Worker Spawner** (`spawn_worker.py`)
   - Creates new Zo conversations via API
   - Passes brief/instructions
   - Returns conversation ID

3. **Worker Briefs** (Markdown files)
   - Self-contained task specifications
   - Include context, deliverables, tests
   - Stored permanently in `N5/orchestration/<project>/`

4. **Conversation Registry** (`conversation_registry.py`)
   - SQLite database tracking all conversations
   - Worker status, metadata, relationships

---

## Workflow

### Phase 1: Planning (Orchestrator)

1. **Decompose system** into discrete tasks
2. **Create worker briefs** (one per task)
3. **Define dependencies** (sequential vs parallel)
4. **Create monitoring dashboard**

### Phase 2: Execution (Orchestrator + Workers)

1. **Orchestrator spawns workers** via `spawn_worker.py`
2. **Workers execute independently** following their briefs
3. **Orchestrator monitors** via conversation DB
4. **Validates deliverables** after each completion

### Phase 3: Integration (Orchestrator)

1. **Run integration tests**
2. **Verify system cohesion**
3. **Document** final state
4. **Archive** worker threads

---

## Example: 5-Worker Build

```
Worker 1: Database Schema
Worker 2: Core Models (depends on W1)
Worker 3: API Endpoints (depends on W2)
Worker 4: CLI Interface (depends on W2)
Worker 5: Tests & Documentation (depends on W3, W4)
```

**Timeline:**
- W1: 20 min
- W2 (after W1): 30 min
- W3, W4 (parallel after W2): 20 min each
- W5 (after W3, W4): 15 min

**Total: ~85 min** (vs 105 min sequential)

---

## Key Files

### Scripts
- `N5/scripts/orchestrator.py` - Core orchestration logic
- `N5/scripts/spawn_worker.py` - Worker conversation spawner
- `N5/scripts/conversation_registry.py` - DB management

### Documentation
- `N5/prefs/operations/orchestrator-protocol.md` - Full protocol
- `N5/schemas/conversations_schema.sql` - Database schema

### Storage
- `N5/orchestration/<project>/` - Project directory
  - `WORKER_N_*.md` - Worker briefs
  - `ORCHESTRATOR_MONITOR.md` - Progress tracker
  - `ORCHESTRATOR_DASHBOARD.md` - Launch sequence

---

## Quick Start

### 1. Create Project Structure

```bash
mkdir -p /home/workspace/N5/orchestration/my-project
cd /home/workspace/N5/orchestration/my-project
```

### 2. Create Worker Briefs

```markdown
# WORKER_1_task_name.md

## Mission
Build database schema for user management

## Deliverables
- /home/workspace/N5/schemas/users.json
- Test script validation

## Requirements
- SQLite compatible
- Follow N5 conventions

[... full brief with implementation guide ...]
```

### 3. Launch Workers

```python
from N5.scripts.spawn_worker import spawn_worker

worker_id = spawn_worker(
    instruction="Load file 'N5/orchestration/my-project/WORKER_1_users_schema.md' and execute",
    metadata={"project": "my-project", "worker": "W1"}
)
```

### 4. Monitor Progress

```python
from N5.scripts.orchestrator import Orchestrator

orch = Orchestrator(project="my-project")
status = orch.get_worker_status(worker_id)
```

---

## Benefits

✅ **Parallelization** - 20-40% faster for multi-component builds  
✅ **Isolation** - Workers can't interfere with each other  
✅ **Modularity** - Reusable worker briefs  
✅ **Trackability** - Full audit trail in DB  
✅ **Resumability** - Can pause/resume orchestration  
✅ **Scalability** - Spawn 10+ workers if needed  

---

## Design Principles

### P0: Rule-of-Two
Orchestrator loads only 2 briefs at a time for spawning

### P2: SSOT
Conversation DB is single source of truth for worker status

### P20: Modular
Workers are independent, self-contained units

### P24: Simulation
Dry-run validation before spawning workers

---

## Advanced Patterns

### Retry Failed Workers
```python
orch.retry_worker(worker_id, updated_brief_path)
```

### Parallel Batch Spawning
```python
worker_ids = orch.spawn_batch([brief1, brief2, brief3])
```

### Conditional Dependencies
```python
if orch.worker_succeeded(w1_id):
    orch.spawn_worker(brief_w2)
else:
    orch.spawn_worker(brief_w2_fallback)
```

---

## Protocol

**Full specification:** file 'N5/prefs/operations/orchestrator-protocol.md'

Key rules:
1. Store briefs in permanent location (`N5/orchestration/`)
2. Track all conversation IDs
3. Validate after each worker
4. Run integration tests before completion
5. Document everything

---

## Use Cases

**Perfect for:**
- Multi-component system builds (5+ scripts)
- Independent module development
- Large refactoring projects
- System migrations
- Test suite creation

**Not ideal for:**
- Simple single-file scripts
- Tightly coupled changes
- Exploratory coding
- Quick prototypes

---

## Real-World Example

**Output Review Tracker** (Oct 2025)
- 5 workers, 3 hours total
- Worker 1: Schema + DB
- Worker 2: Classification system
- Worker 3: API endpoints
- Worker 4: CLI interface
- Worker 5: Tests + docs

**Result:** Fully functional system, parallel execution, zero conflicts.

---

## Troubleshooting

**Worker stalled?**
- Check conversation DB status
- Review worker thread for errors
- Spawn replacement with updated brief

**Integration failures?**
- Validate each component individually
- Check file paths and imports
- Review architectural principles compliance

**DB corruption?**
- Conversation registry auto-creates schema
- Safe to reset: `rm N5/data/conversations.db && python3 conversation_registry.py init`

---

## Next Steps

1. Read full protocol: file 'N5/prefs/operations/orchestrator-protocol.md'
2. Study schema: file 'N5/schemas/conversations_schema.sql'
3. Try orchestrator.py: `python3 N5/scripts/orchestrator.py --help`
4. Create first project in `N5/orchestration/`

---

## System Architecture

```
Orchestrator Conversation
├── Spawns → Worker 1 (independent conversation)
├── Spawns → Worker 2 (independent conversation)  
├── Spawns → Worker 3 (independent conversation)
└── Monitors, validates, integrates results
```

### Components

1. **Orchestrator** (`orchestrator.py`)
   - Tracks worker conversations in SQLite DB
   - Monitors progress
   - Validates deliverables
   - Resolves blockers

2. **Worker Spawner** (`spawn_worker.py`)
   - Creates new Zo conversations via API
   - Passes brief/instructions
   - Returns conversation ID

3. **Worker Briefs** (Markdown files)
   - Self-contained task specifications
   - Include context, deliverables, tests
   - Stored permanently in `N5/orchestration/<project>/`

4. **Conversation Registry** (`conversation_registry.py`)
   - SQLite database tracking all conversations
   - Worker status, metadata, relationships

---

## Validation System (New: 2025-10-28)

### Problem
Workers complete tasks in isolation, leading to:
- Stub implementations left in code
- TODO/FIXME placeholders
- Broken imports/references
- Missing function contracts

These issues weren't caught until final integration, wasting time.

### Solution
**Proactive validation** integrated into orchestrator. After each worker completes, validation scans output for common issues.

**Architecture:** Validation is part of orchestrator (not separate worker) to minimize overhead.

### Capabilities
- **Stub Detection:** `raise NotImplementedError`, `def foo(): pass`
- **Placeholder Detection:** `TODO`, `FIXME`, `XXX`, `HACK`
- **Import Validation:** AST-based broken import detection
- **Contract Checking:** Missing type hints, docstrings

### Usage

**Standalone:**
```bash
# Quick scan
python3 N5/scripts/validation.py sweep /path/to/project --all

# JSON output
python3 N5/scripts/validation.py sweep /path/to/project --json
```

**Orchestrator Integration:**
```bash
# Validate project
python3 N5/scripts/orchestrator.py validate /path/to/project

# Fail on errors
python3 N5/scripts/orchestrator.py validate /path/to/project --fail-on-error
```

### Output
- Console: Errors (blocking), Warnings (non-blocking), Info (best practices)
- Report: `<orchestrator_workspace>/VALIDATION_REPORT.md`
- Exit code: `0` (pass), `1` (fail)

**See:** `n5os-core/Documents/VALIDATION_SYSTEM.md` for full documentation.

---

## Worker Brief Structure

### Components

1. **Brief Header**
   - **Title:** Short, descriptive name
   - **Description:** Detailed task description
   - **Deliverables:** Expected output
   - **Dependencies:** Other workers required

2. **Task Specification**
   - **Context:** Background information
   - **Implementation:** Step-by-step instructions
   - **Tests:** Verification checks

3. **Metadata**
   - **Project:** Project name
   - **Worker ID:** Unique identifier
   - **Status:** Current progress
   - **Timestamps:** Created, started, completed

4. **Attachments**
   - **Code Snippets:** Relevant code samples
   - **References:** External links
   - **Notes:** Additional context

---

## Quick Start

### 1. Create Project Structure

```bash
mkdir -p /home/workspace/N5/orchestration/my-project
cd /home/workspace/N5/orchestration/my-project
```

### 2. Create Worker Briefs

```markdown
# WORKER_1_task_name.md

## Mission
Build database schema for user management

## Deliverables
- /home/workspace/N5/schemas/users.json
- Test script validation

## Requirements
- SQLite compatible
- Follow N5 conventions

[... full brief with implementation guide ...]
```

### 3. Launch Workers

```python
from N5.scripts.spawn_worker import spawn_worker

worker_id = spawn_worker(
    instruction="Load file 'N5/orchestration/my-project/WORKER_1_users_schema.md' and execute",
    metadata={"project": "my-project", "worker": "W1"}
)
```

### 4. Monitor Progress

```python
from N5.scripts.orchestrator import Orchestrator

orch = Orchestrator(project="my-project")
status = orch.get_worker_status(worker_id)
```

---

## Benefits

✅ **Parallelization** - 20-40% faster for multi-component builds  
✅ **Isolation** - Workers can't interfere with each other  
✅ **Modularity** - Reusable worker briefs  
✅ **Trackability** - Full audit trail in DB  
✅ **Resumability** - Can pause/resume orchestration  
✅ **Scalability** - Spawn 10+ workers if needed  

---

## Design Principles

### P0: Rule-of-Two
Orchestrator loads only 2 briefs at a time for spawning

### P2: SSOT
Conversation DB is single source of truth for worker status

### P20: Modular
Workers are independent, self-contained units

### P24: Simulation
Dry-run validation before spawning workers

---

## Advanced Patterns

### Retry Failed Workers
```python
orch.retry_worker(worker_id, updated_brief_path)
```

### Parallel Batch Spawning
```python
worker_ids = orch.spawn_batch([brief1, brief2, brief3])
```

### Conditional Dependencies
```python
if orch.worker_succeeded(w1_id):
    orch.spawn_worker(brief_w2)
else:
    orch.spawn_worker(brief_w2_fallback)
```

---

## Protocol

**Full specification:** file 'N5/prefs/operations/orchestrator-protocol.md'

Key rules:
1. Store briefs in permanent location (`N5/orchestration/`)
2. Track all conversation IDs
3. Validate after each worker
4. Run integration tests before completion
5. Document everything

---

## Use Cases

**Perfect for:**
- Multi-component system builds (5+ scripts)
- Independent module development
- Large refactoring projects
- System migrations
- Test suite creation

**Not ideal for:**
- Simple single-file scripts
- Tightly coupled changes
- Exploratory coding
- Quick prototypes

---

## Real-World Example

**Output Review Tracker** (Oct 2025)
- 5 workers, 3 hours total
- Worker 1: Schema + DB
- Worker 2: Classification system
- Worker 3: API endpoints
- Worker 4: CLI interface
- Worker 5: Tests + docs

**Result:** Fully functional system, parallel execution, zero conflicts.

---

## Troubleshooting

**Worker stalled?**
- Check conversation DB status
- Review worker thread for errors
- Spawn replacement with updated brief

**Integration failures?**
- Validate each component individually
- Check file paths and imports
- Review architectural principles compliance

**DB corruption?**
- Conversation registry auto-creates schema
- Safe to reset: `rm N5/data/conversations.db && python3 conversation_registry.py init`

---

## Next Steps

1. Read full protocol: file 'N5/prefs/operations/orchestrator-protocol.md'
2. Study schema: file 'N5/schemas/conversations_schema.sql'
3. Try orchestrator.py: `python3 N5/scripts/orchestrator.py --help`
4. Create first project in `N5/orchestration/`

---

**Version:** 2.0  
**Created:** 2025-10-26  
**Status:** Production Ready
