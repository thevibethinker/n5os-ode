# N5 Architecture Overview

**Purpose:** Explain how N5 is structured and how components interact

---

## System Layers

N5 is organized into distinct layers with clear responsibilities:

```
┌─────────────────────────────────────┐
│     USER INTERFACE (Zo Chat)        │
│  Slash Commands + Natural Language  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       COMMAND LAYER (N5/commands/)  │
│   User-facing workflows & shortcuts │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       SCRIPT LAYER (N5/scripts/)    │
│   Core automation & processing      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│      DATA LAYER (Schemas + Files)   │
│   Knowledge, Lists, Records, Config │
└─────────────────────────────────────┘
```

---

## Core Subsystems

### 1. Knowledge Management

**Purpose:** Capture and retrieve information

**Components:**
- Scripts: `n5_knowledge_*.py`
- Commands: `/knowledge-add`, `/knowledge-find`, `/knowledge-ingest`
- Storage: `Knowledge/` directory
- Schema: `knowledge.facts.schema.json`

**Flow:**
```
Conversation → Extract insight → Validate → Store in Knowledge/ → Index → Retrieve on demand
```

### 2. Meeting Intelligence

**Purpose:** Process meeting transcripts into actionable intelligence

**Components:**
- Scripts: `meeting_*.py`
- Commands: `/meeting-process`, `/meeting-approve`, `/auto-process-meetings`
- Storage: `N5/records/meetings/`
- Schema: `meeting-metadata.schema.json`

**Flow:**
```
Transcript file → Detect → Extract metadata → Generate blocks → Store → Generate follow-ups
```

**Block Types:**
- B08: Stakeholder Intelligence
- B25: Deliverable Content Map
- B31: Stakeholder Research
- B36: Strategic Synthesis
- And 20+ more...

### 3. List Management

**Purpose:** Track tasks, opportunities, and action items

**Components:**
- Scripts: `n5_lists_*.py`
- Commands: `/lists-add`, `/lists-create`, `/list-view`
- Storage: `Lists/` directory
- Schema: `lists.item.schema.json`, `lists.registry.schema.json`

**Flow:**
```
Create list → Add items → Track metadata → Monitor health → Export → Archive
```

### 4. Session Management

**Purpose:** Maintain conversation context and state

**Components:**
- Script: `session_state_manager.py`
- Commands: `/init-state-session`, `/check-state-session`
- Storage: `SESSION_STATE.md` (per conversation)
- Schema: Internal state structure

**Flow:**
```
Init session → Load system files → Track focus/objectives → Update state → Persist
```

### 5. Command System

**Purpose:** Provide user-facing workflow orchestration

**Components:**
- Registry: `N5/config/commands.jsonl`
- Definitions: `N5/commands/*.md`
- Manager: `n5_commands_manage.py`
- Schema: `commands.schema.json`

**Structure:**
```json
{
  "trigger": "meeting-process",
  "script_path": "/home/workspace/N5/scripts/meeting_processor.py",
  "description": "Process a meeting transcript",
  "tags": ["meetings", "intelligence"]
}
```

---

## Data Flow Patterns

### Pattern 1: Ingestion
```
External source → Records/ (staging) → Process → Knowledge/ or Lists/ → Index
```

### Pattern 2: Retrieval
```
User query → Search index → Find relevant files → Extract → Present
```

### Pattern 3: Workflow
```
Trigger command → Load config → Execute scripts → Validate → Store → Notify
```

---

## File Organization

### By Function

- **Operational Data:** `N5/records/`, `N5/intelligence/`
- **Reference Data:** `Knowledge/`, `Documents/`
- **Action Data:** `Lists/`
- **Configuration:** `N5/config/`
- **Code:** `N5/scripts/`, `N5/commands/`

### By Lifecycle

- **Staging:** `Records/` - Temporary, unprocessed
- **Active:** `Lists/`, `Knowledge/` - Current, in use
- **Archive:** `Documents/Archive/` - Historical

---

## Key Design Patterns

### 1. Registry Pattern
Central registries for discoverability:
- Commands: `commands.jsonl`
- Lists: `registry.jsonl` in each list directory
- Blocks: `block_type_registry.json`

### 2. Schema-First
Every data type has a JSON schema:
- Validates structure
- Documents format
- Enables tooling

### 3. Markdown + Frontmatter
Human-readable with machine-parseable metadata:
```markdown
---
type: knowledge
tags: [architecture, n5]
date: 2025-10-18
---

# Content here
```

### 4. Modular Scripts
Each script is self-contained:
- Imports from standard library or explicit deps
- Accepts CLI arguments
- Returns exit codes
- Includes dry-run mode

---

## Extension Points

### Adding New Subsystems

1. Create schemas in `N5/schemas/`
2. Write scripts in `N5/scripts/`
3. Create commands in `N5/commands/`
4. Register in `N5/config/commands.jsonl`
5. Document in `Knowledge/architectural/`

### Adding New Data Types

1. Define schema in `N5/schemas/`
2. Choose storage location (Knowledge/ or Lists/)
3. Create CRUD scripts
4. Add validation logic
5. Update index builder

---

## Dependency Graph

```
Commands → Scripts → Schemas ← Data Files
                ↓
         Config Files
                ↓
         External APIs (optional)
```

**Key Dependencies:**
- Python 3.12+
- Standard library (pathlib, json, logging, argparse)
- Optional: anthropic, openai (for LLM features)
- Optional: Google APIs (for Drive/Gmail integration)

---

## Performance Considerations

### Indexing
- Full rebuild: `O(n)` where n = total files
- Incremental update: `O(1)` per file
- Search: `O(log n)` with proper indexing

### Storage
- Prefer markdown over binary
- Use JSONL for append-only logs
- Compress old records

### Processing
- Async where possible (meeting monitor)
- Batch operations for lists
- Cache frequently accessed configs

---

## Security & Safety

### File Protection
- Dry-run mode for destructive ops
- Backup before overwrite (P5)
- Explicit confirmation for bulk deletes

### Data Isolation
- No personal data in scripts
- Credentials in separate directory
- API keys from environment variables

### Validation
- Schema validation on write
- Input sanitization
- Path traversal prevention

---

## Future Architecture Considerations

### Scalability
- Consider database (SQLite) for large lists
- Implement caching layer
- Add background job queue

### Integration
- Webhook support for external systems
- REST API for programmatic access
- Plugin system for extensions

### Observability
- Structured logging
- Performance metrics
- Health check endpoints

---

For implementation details, see:
- `file 'Knowledge/architectural/architectural_principles.md'`
- `file 'N5/prefs/prefs.md'`
- Individual script docstrings
