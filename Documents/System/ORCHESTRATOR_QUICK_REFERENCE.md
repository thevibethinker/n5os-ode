# Orchestrator System - Quick Reference Guide
**Version:** 1.0  
**Updated:** 2025-10-27  
**Status:** Active

---

## Overview

N5 has multiple "orchestrator" scripts, each serving a distinct purpose. This guide helps you choose the right tool for your task.

---

## The Orchestrators

### 1. **orchestrator.py** - Task Assignment to Workers
**Purpose:** Assigns tasks to worker conversations and tracks completion

**Use when:**
- Coordinating parallel work across multiple conversations
- Need to split a large task into sub-tasks
- Tracking worker progress and collecting results

**Example:**
```bash
python3 N5/scripts/orchestrator.py \
  --task "Implement OAuth flow" \
  --workers con_ABC,con_DEF,con_GHI \
  --check-progress
```

**Key features:**
- Reads worker SESSION_STATE files
- Tracks task assignment and completion
- Collects worker outputs
- Generates progress reports

**Related:** file 'Recipes/Tools/Spawn Worker.md'

---

### 2. **convo_supervisor.py** - Conversation Batch Operations  ⭐ NEW
**Purpose:** Groups, summarizes, and proposes batch operations for conversations

**Use when:**
- Need to find related conversations
- Want to improve conversation titles in bulk
- Ready to archive old completed work
- Generating unified summaries across threads

**Example:**
```bash
# List related build conversations
python3 N5/scripts/convo_supervisor.py list-related --type build --window-days 7

# Propose title improvements
python3 N5/scripts/convo_supervisor.py propose-rename --strategy focus_based

# Propose archive moves
python3 N5/scripts/convo_supervisor.py propose-archive --older-than-days 30
```

**Key features:**
- Integrated with conversations.db
- Groups by type/focus/time/parent
- Generates rename proposals (focus-based or pattern-based)
- Proposes archive operations
- Dry-run by default, --execute to apply

**Related:** file 'Recipes/System/Conversation Diagnostics.md'

---

### 3. **reflection_orchestrator.py** - Full Reflection Pipeline
**Purpose:** End-to-end processing of reflection audio/text into knowledge

**Use when:**
- Processing a reflection from audio → transcript → knowledge
- Need full pipeline: transcription, classification, synthesis, voice generation

**Example:**
```bash
python3 N5/scripts/reflection_orchestrator.py \
  --input /path/to/reflection.m4a \
  --dry-run
```

**Pipeline:**
```
Audio/Text Input
  ↓
Transcription (if audio)
  ↓
Classification (type, audience, purpose)
  ↓
Content Synthesis
  ↓
Voice Profile Selection
  ↓
Draft Generation
  ↓
Approval → Final Output
```

**Key features:**
- Calls transcription service
- Uses classification models
- Generates proposals for approval
- Extracts semi-stable beliefs
- Integrates with registry system

**Related:** file 'Recipes/Knowledge/Reflection Worker.md'

---

### 4. **reflection_ingest_bridge.py** - Drive/Gmail Ingestion
**Purpose:** Bridge layer between Google Drive/Gmail and reflection system

**Use when:**
- Auto-ingesting reflections from Google Drive folder
- Processing email-triggered reflections with `[Reflect]` subject
- Need to stage files for downstream processing

**Example:**
```bash
# Ingest from Drive
python3 N5/scripts/reflection_ingest_bridge.py \
  --source drive \
  --dry-run

# Process email-triggered reflections
python3 N5/scripts/reflection_ingest_bridge.py \
  --source gmail \
  --query 'subject:[Reflect] newer_than:10m'
```

**Key features:**
- Downloads from Drive/Gmail
- Stages in `N5/records/reflections/incoming/`
- Tracks state in `.state.json`
- Deduplicates by message_id/file_id
- Preserves email body as context

**Related:** file 'Recipes/Knowledge/Reflection Email Orchestrator.md'

---

### 5. **deliverable_orchestrator.py** - Deliverable Generation
**Purpose:** Generates client deliverables from meeting intelligence

**Use when:**
- Creating follow-up emails from meetings
- Generating meeting summaries for clients
- Need deliverable content from meeting blocks

**Example:**
```bash
python3 N5/scripts/deliverable_orchestrator.py \
  --meeting-id carly-careerspan-2025-09-23 \
  --type email-followup \
  --dry-run
```

**Key features:**
- Reads meeting intelligence blocks
- Applies deliverable templates
- Generates stakeholder-specific content
- Integrates with registry system

---

### 6. **spawn_worker.py** - Worker Assignment Creator
**Purpose:** Creates worker assignment files for parallel work

**Use when:**
- Need to delegate a task to a separate conversation
- Want to fork work without blocking current thread
- Creating worker with full parent context

**Example:**
```bash
python3 N5/scripts/spawn_worker.py \
  --parent con_PARENT \
  --instruction "Research OAuth2 alternatives" \
  --dry-run
```

**Output:**
- Creates `WORKER_ASSIGNMENT_*.md` in Records/Temporary/
- Updates parent SESSION_STATE
- Creates `worker_updates/` directory
- Captures parent context

**Next step:** Open assignment file in NEW conversation

**Related:** file 'Recipes/Tools/Spawn Worker.md'

---

## Decision Tree

```
Need to...
├─ Coordinate parallel tasks across workers?
│  └─ Use: orchestrator.py
│
├─ Find/group/rename/archive conversations?
│  └─ Use: convo_supervisor.py  ⭐
│
├─ Process reflection audio → knowledge?
│  └─ Use: reflection_orchestrator.py
│
├─ Auto-ingest reflections from Drive/Gmail?
│  └─ Use: reflection_ingest_bridge.py
│
├─ Generate deliverables from meetings?
│  └─ Use: deliverable_orchestrator.py
│
└─ Delegate task to new worker thread?
   └─ Use: spawn_worker.py
```

---

## Common Patterns

### Pattern 1: Reflection Auto-Processing
```bash
# Step 1: Ingest from Drive/Gmail
python3 N5/scripts/reflection_ingest_bridge.py --source drive

# Step 2: Process each staged reflection
python3 N5/scripts/reflection_orchestrator.py \
  --input N5/records/reflections/incoming/file.m4a
```

### Pattern 2: Worker Coordination
```bash
# Step 1: Spawn workers
python3 N5/scripts/spawn_worker.py --parent con_MAIN --instruction "Task 1"
python3 N5/scripts/spawn_worker.py --parent con_MAIN --instruction "Task 2"

# Step 2: Track progress
python3 N5/scripts/orchestrator.py --parent con_MAIN --check-progress

# Step 3: Collect results
python3 N5/scripts/orchestrator.py --parent con_MAIN --collect-outputs
```

### Pattern 3: Conversation Maintenance
```bash
# Weekly: Review and improve titles
python3 N5/scripts/convo_supervisor.py propose-rename --window-days 7

# Monthly: Archive old work
python3 N5/scripts/convo_supervisor.py propose-archive --older-than-days 30

# Quarterly: Health check
python3 N5/scripts/convo_supervisor.py list-related --window-days 90 --include-artifacts
```

### Pattern 4: Meeting → Deliverable
```bash
# Step 1: Process meeting (handled by Zo directly)
# Creates intelligence blocks in N5/records/meetings/

# Step 2: Generate deliverable
python3 N5/scripts/deliverable_orchestrator.py \
  --meeting-id <meeting-slug> \
  --type email-followup
```

---

## Key Principles

**P1 - Human-Readable:** All orchestrators output human-readable logs  
**P2 - SSOT:** Orchestrators read from single source (db, registry, state files)  
**P7 - Dry-Run:** All support `--dry-run` for safety  
**P15 - Complete:** Verify state before claiming success  
**P19 - Error Handling:** Try/except with context logging  

---

## File Locations

```
N5/
├── scripts/
│   ├── orchestrator.py              # Task assignment
│   ├── convo_supervisor.py          # Conversation ops ⭐
│   ├── reflection_orchestrator.py   # Reflection pipeline
│   ├── reflection_ingest_bridge.py  # Drive/Gmail bridge
│   ├── deliverable_orchestrator.py  # Deliverable gen
│   └── spawn_worker.py              # Worker creator
│
├── data/
│   └── conversations.db             # Conversation metadata (used by supervisor)
│
└── records/
    ├── reflections/incoming/        # Staged reflections
    └── meetings/                    # Meeting intelligence
```

---

## See Also

- file 'Recipes/System/Orchestrator Thread.md' - Orchestrator workflow planning
- file 'Recipes/System/Conversation Diagnostics.md' - Conversation health checks
- file 'Recipes/Tools/Spawn Worker.md' - Worker spawning guide
- file 'N5/prefs/operations/orchestrator-protocol.md' - Orchestrator protocol
- file 'Documents/N5.md' - Overall system architecture
- file 'Knowledge/architectural/planning_prompt.md' - System design principles

---

## Quick Commands

```bash
# Find what needs attention
python3 N5/scripts/convo_supervisor.py list-related --status active --window-days 7

# Health check
sqlite3 N5/data/conversations.db "SELECT status, COUNT(*) FROM conversations GROUP BY status;"

# Recent work summary
python3 N5/scripts/convo_supervisor.py summarize --window-days 7 --include-artifacts

# Archive old completed work
python3 N5/scripts/convo_supervisor.py propose-archive --older-than-days 30 --status complete
```

---

**Last Updated:** 2025-10-27 by Vibe Builder  
**Version:** 1.0
