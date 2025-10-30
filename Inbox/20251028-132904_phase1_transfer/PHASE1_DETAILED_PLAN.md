# N5 OS Core - Phase 1 Detailed Plan
# Core Infrastructure

**Thread**: con_2rD2ojBNmRthdfVR  
**Date**: 2025-10-28  
**Planning Mode**: THINK → PLAN → EXECUTE  
**Status**: 📋 Planning

---

## THINK Phase: What Are We Building?

### Purpose
Phase 1 creates the **core infrastructure** that enables N5 OS to track, maintain, and understand itself. This is the foundation for all higher-level capabilities.

### Why Phase 1 Matters
- **Self-awareness**: System knows what conversations exist, their type, and state
- **Safety**: Prevents destructive operations before they happen
- **Transparency**: AI can see system evolution and troubleshoot issues
- **Coordination**: Multiple conversations can coordinate through shared state

### Components Overview
1. **Session State Manager** - Conversation initialization and tracking
2. **System Bulletins** - Change log for AI transparency
3. **Conversation Registry** - SQLite database for conversation metadata
4. **Safety System** - Pre-execution validation and dry-run enforcement

### Trap Doors (Irreversible Decisions)
- **Database choice**: SQLite (vs Postgres/other) - reversible but costly
- **State file format**: Markdown with frontmatter (vs JSON/YAML) - low cost to change
- **Bulletin format**: JSONL (vs database table) - easily migratable

**Decision**: All choices are reversible at acceptable cost. Proceed with simple defaults.

### Trade-offs
| Choice | Pro | Con | Decision |
|--------|-----|-----|----------|
| SQLite vs Postgres | Simple, portable, no daemon | Single-writer, no network | ✅ SQLite (YAGNI) |
| Markdown vs JSON for state | Human-readable, git-friendly | Harder to parse | ✅ Markdown (P1) |
| JSONL vs DB for bulletins | Appendable, simple | No queries | ✅ JSONL (flow over pools) |

---

## PLAN Phase: Detailed Specification

### Phase 1.1: Session State Manager

**Purpose**: Initialize conversation context and track state throughout conversation lifecycle.

**Files to Create**:
- `/N5/scripts/session_state_manager.py` - Core script
- `/N5/templates/session_state/` - State templates by type
  - `build.template.md` - For build conversations
  - `research.template.md` - For research conversations
  - `discussion.template.md` - For general discussions
  - `planning.template.md` - For planning sessions

**Functionality**:
```python
# CLI Interface
n5_session init --convo-id <id> --type <type> [--load-system]
n5_session update --convo-id <id> --focus "..." --objective "..."
n5_session complete --convo-id <id> --summary "..."
n5_session list [--type <type>] [--status <status>]
```

**State File Schema** (Markdown):
```markdown
# Session State — <Type>

**Conversation ID**: <id>
**Type**: <type>
**Created**: <timestamp>
**Timezone**: <user_timezone>

---

## Focus
*What are we building/researching/discussing?*

---

## Objective
*Specific deliverables for this session*

- [ ] Item 1
- [ ] Item 2

---

## Context
*Key information*

- **Target**: 
- **Requirements**: 
- **Constraints**: 

---

## Progress

### Completed
- 

### In Progress
- 

### Blocked
- 

### Next Steps
1. 

---

## Tags
`<type>` `<domain>`

---

**Last Updated**: <timestamp>
```

**Database Integration**:
- Insert conversation record on init
- Update status on complete
- Query for cross-conversation coordination

**Success Criteria**:
- ✅ Creates state file in conversation workspace
- ✅ Registers conversation in database
- ✅ Auto-detects conversation type from user's first message
- ✅ Loads system files when --load-system flag used
- ✅ Updates state via CLI or Python API
- ✅ Idempotent (safe to run multiple times)
- ✅ Dry-run support
- ✅ Exit code 0 on success, 1 on failure

---

### Phase 1.2: System Bulletins

**Purpose**: Provide AI with transparent change log for troubleshooting and context.

**Files to Create**:
- `/N5/data/system_bulletins.jsonl` - Bulletin storage
- `/N5/scripts/add_bulletin.py` - Add bulletin script
- `/N5/templates/bulletins/` - Bulletin templates
  - `change.template.json` - System changes
  - `issue.template.json` - Known issues
  - `resolved.template.json` - Issue resolutions

**Functionality**:
```python
# CLI Interface
n5_bulletin add --type <type> --severity <level> --title "..." --body "..."
n5_bulletin list [--type <type>] [--severity <level>] [--since <date>]
n5_bulletin resolve --id <bulletin_id> --resolution "..."
```

**Bulletin Schema** (JSON):
```json
{
  "id": "uuid",
  "timestamp": "ISO8601",
  "type": "change|issue|resolved",
  "severity": "info|warning|critical",
  "title": "Brief description",
  "body": "Detailed explanation",
  "affected_components": ["component1", "component2"],
  "resolution": "How it was fixed (if resolved)",
  "resolved_at": "ISO8601 (if resolved)"
}
```

**Integration with Rules**:
- Rule template references bulletins for troubleshooting
- AI checks bulletins when encountering errors
- Bulletins inform system evolution understanding

**Success Criteria**:
- ✅ Appends to JSONL without corruption
- ✅ Lists bulletins with filtering
- ✅ Resolves issues and updates entries
- ✅ Human-readable format
- ✅ AI can query and understand
- ✅ Exit code 0 on success, 1 on failure

---

### Phase 1.3: Conversation Registry

**Purpose**: SQLite database for conversation metadata and cross-conversation coordination.

**Files to Create**:
- `/N5/data/conversations.db` - SQLite database
- `/N5/scripts/conversation_registry.py` - Database operations
- `/N5/schemas/conversation.schema.json` - Schema documentation

**Database Schema**:
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT CHECK(type IN ('build', 'research', 'discussion', 'planning')),
    status TEXT CHECK(status IN ('active', 'paused', 'complete', 'abandoned')) DEFAULT 'active',
    focus TEXT,
    tags TEXT,  -- JSON array
    workspace_path TEXT,
    parent_conversation_id TEXT,  -- For threaded work
    metadata TEXT  -- JSON object for extensibility
);

CREATE INDEX idx_type ON conversations(type);
CREATE INDEX idx_status ON conversations(status);
CREATE INDEX idx_created_at ON conversations(created_at);
```

**Functionality**:
```python
# Python API (used by session_state_manager.py)
from n5_conversation_registry import ConversationRegistry

registry = ConversationRegistry()
registry.create(convo_id, type, focus, tags)
registry.update(convo_id, status=None, focus=None, tags=None)
registry.get(convo_id)
registry.list(type=None, status=None, since=None)
registry.complete(convo_id, summary)
```

**Success Criteria**:
- ✅ Creates database on first run
- ✅ CRUD operations work correctly
- ✅ Queries filter properly
- ✅ Thread-safe (WAL mode)
- ✅ Backups created before schema changes
- ✅ Idempotent operations
- ✅ Returns proper exit codes

---

### Phase 1.4: Safety System

**Time**: 2-3 hours

**Purpose**: Pre-execution validation layer

**Components**:

1. **n5_protect.py** (File Guard System)
   - `.n5protected` marker files for directory protection
   - Check command integration (before move/delete operations)
   - Auto-protect for registered services
   - List/protect/unprotect commands
   - **References**: file 'Documents/N5-File-Protection-System.md'

2. **n5_safety.py** (Safety Validation)
   - Pre-execution checks
   - Dry-run enforcement
   - Destructive operation warnings
   - Integration with detection_rules.md

3. **detection_rules.md** (Risk Detection)
   - Pattern matching for risky operations
   - Classification by severity
   - Action recommendations

**Detection Rules Schema** (Markdown):
```markdown
# N5 Safety Detection Rules

## File Protection Rules

### Rule: Protected Directory Detection
**Pattern**: `\.n5protected` file present
**Action**: BLOCK delete/move operations
**Severity**: CRITICAL

### Rule: Bulk Delete Detection
**Pattern**: Delete >10 files in single operation
**Action**: REQUIRE dry-run + confirmation
**Severity**: WARNING

## Database Rules

### Rule: Production Database Modification
**Pattern**: Write to conversations.db without backup
**Action**: REQUIRE backup confirmation
**Severity**: CRITICAL

## System Rules

### Rule: Config Overwrite
**Pattern**: Overwrite existing user config
**Action**: REQUIRE confirmation + backup
**Severity**: WARNING
```

**Functionality**:
```python
# CLI Interface
n5_safety check --operation <op> --targets <paths> [--dry-run]
n5_safety protect --path <path> --reason "..."
n5_safety unprotect --path <path>
n5_safety status --path <path>
```

**Integration**:
- Called by incantum engine before destructive operations
- Used in rules template to enforce safety protocols
- Provides dry-run simulation before real execution

**Success Criteria**:
- ✅ Detects all rule violations
- ✅ Returns actionable error messages
- ✅ Dry-run mode simulates without executing
- ✅ Protection files work correctly
- ✅ Exit code 1 on violation, 0 on pass
- ✅ Logs all safety checks

---

## EXECUTE Phase: Implementation Order

### Build Order (Sequential Dependencies)
1. **Conversation Registry** (no dependencies)
   - Create database schema
   - Build Python API
   - Test CRUD operations

2. **System Bulletins** (no dependencies)
   - Create bulletin add/list scripts
   - Test JSONL operations
   - Create templates

3. **Session State Manager** (depends on: Registry)
   - Build state initialization
   - Integrate with registry
   - Create templates for each type

4. **Safety System** (no dependencies, but integrates with all)
   - Build detection rule parser
   - Implement validation logic
   - Create protection system

### Testing Strategy
- **Unit Tests**: Each script tested independently
- **Integration Tests**: Scripts interact correctly
- **Production Tests**: Works in actual Zo environment
- **Fresh Thread Test**: Can someone else use this?

### Rollout Plan
1. Build on **Demonstrator** account (vademonstrator.zo.computer)
2. Test in clean environment
3. Push to GitHub (zo-n5os-core repo)
4. Create Phase 1 release tag
5. Update documentation

---

## REVIEW Phase: Success Metrics

| Component | Tests | Coverage | Criteria |
|-----------|-------|----------|----------|
| Session State | 8 | 100% | Init, update, complete, list work |
| Bulletins | 5 | 100% | Add, list, resolve work |
| Registry | 10 | 100% | CRUD, queries, thread-safety work |
| Safety | 12 | 100% | Detection, protection, dry-run work |

**Overall Phase 1 Success**:
- ✅ 35+ tests passing
- ✅ All components integrate
- ✅ Documentation complete
- ✅ Production validated
- ✅ GitHub release created
- ✅ Fresh thread test passed

---

## Principles Applied

**Planning**:
- ✅ P22 (Language Selection): Python for all (LLM corpus + maintainability)
- ✅ Think→Plan→Execute (70-20-10 split)
- ✅ Nemawashi (explored SQLite vs Postgres, JSONL vs DB)
- ✅ Simple Over Easy (SQLite + JSONL vs complex setup)

**Implementation**:
- ✅ P1 (Human-Readable): Markdown state files, clear schemas
- ✅ P2 (SSOT): Database is truth for conversation metadata
- ✅ P5 (Anti-Overwrite): Safety system prevents destructive ops
- ✅ P7 (Dry-Run): All scripts support --dry-run
- ✅ P11 (Failure Modes): Error handling for all operations
- ✅ P15 (Complete Before Claiming): Test all criteria before marking done
- ✅ P18 (Verify State): Check writes succeeded
- ✅ P19 (Error Handling): Try/except with specific errors
- ✅ P21 (Document Assumptions): Explicit in code and docs

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Planning (this doc) | 1.5h | 1.5h |
| 1.1 Session State | 2h | 3.5h |
| 1.2 Bulletins | 1h | 4.5h |
| 1.3 Registry | 1.5h | 6h |
| 1.4 Safety | 2h | 8h |
| Integration Testing | 1h | 9h |
| Documentation | 1h | 10h |
| GitHub Release | 0.5h | 10.5h |

**Target**: 10-11 hours (compare to Phase 0: 6.5h)

---

## Next Actions

1. **Review this plan with V** - Get approval, clarify ambiguities
2. **Create orchestrator brief** - Instructions for Demonstrator execution
3. **Switch to Demonstrator** - Begin Phase 1.1 implementation
4. **Iterate with Main** - Update plan based on learnings

---

*Created: 2025-10-28 01:42 ET*  
*Planning Prompt: Loaded*  
*Status: Ready for Review*
