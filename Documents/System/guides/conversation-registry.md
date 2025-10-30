# Conversation Registry System

**Version:** 1.0.0  
**Created:** 2025-10-24  
**Status:** Production

---

## Overview

The Conversation Registry is a central SQLite database that tracks all conversations, their artifacts, issues, learnings, and design decisions. It serves as the single source of truth for conversation metadata and enables powerful cross-conversation queries.

**Key Benefits:**
- **Simplified orchestrator workflows:** No custom tracking logic needed
- **Cross-conversation search:** "Which conversation implemented auth?"
- **Learning consolidation:** All learnings queryable from one place  
- **Issue tracking:** System-wide issue patterns visible
- **Complete provenance:** Audit trail of what was built where
- **Resume support:** New threads can discover related prior work

---

## Database Schema

### `conversations` Table
Core conversation metadata:
- `id` - Conversation ID (con_XXX)
- `type` - build, research, discussion, planning, content
- `status` - active, complete, archived, blocked
- `mode` - standalone, orchestrator, worker
- `created_at`, `updated_at`, `completed_at` - Timestamps
- `focus`, `objective`, `tags` - Content metadata
- `parent_id` - For worker threads, links to orchestrator
- `related_ids` - JSON array for peer relationships
- `starred` - User-marked important conversations
- `progress_pct` - 0-100% completion
- `workspace_path`, `state_file_path`, `aar_path` - File system links

### `artifacts` Table
Files/outputs created during conversation:
- `conversation_id` - Parent conversation
- `filepath` - Absolute path
- `artifact_type` - script, document, data, config, command
- `description` - Human-readable description

### `issues` Table
Significant problems (blockers, system threats, learning opportunities):
- `conversation_id` - Parent conversation
- `severity` - blocker, system_threat, learning_opportunity
- `category` - tool_failure, logic_error, external_api, design_flaw
- `message`, `context`, `resolution` - Issue details
- `resolved` - Boolean flag

### `learnings` Table
Lessons extracted from conversations:
- `conversation_id` - Parent conversation
- `lesson_id` - UUID from lessons.jsonl
- `type` - technique, strategy, pattern, anti_pattern, troubleshooting
- `title`, `description` - Learning content
- `principle_refs` - JSON array of principle IDs
- `status` - pending, approved, archived, rejected

### `decisions` Table
Design decisions made:
- `conversation_id` - Parent conversation
- `decision` - What was decided
- `rationale`, `alternatives`, `outcome` - Decision details

---

## Integration Points

### 1. Session State Manager

**Automatic sync on init and update:**

```python
# In session_state_manager.py
manager = SessionStateManager(convo_id, sync_registry=True)
manager.init(type="build", mode="orchestrator")
# → Automatically creates conversation in registry
```

**When it syncs:**
- `init` - Creates conversation record
- Every session state update - Updates focus/objective/tags/progress
- Checkpoint - Full sync (artifacts, issues, decisions)
- Close - Final sync + mark complete + link AAR

### 2. Conversation End

**Phases that interact with registry:**

- **Phase -0.5:** Import learnings from `lessons/pending/<convo_id>.lessons.jsonl`
- **Phase 7:** Close conversation in registry, link AAR path
- **Phase 8:** Export final state to JSON

### 3. Orchestrator Workflows

**Example usage:**

```python
from conversation_registry import ConversationRegistry

registry = ConversationRegistry()

# 1. Create orchestrator conversation
registry.create('con_ORCH123', type='build', mode='orchestrator')

# 2. Spawn workers
for task in tasks:
    worker_id = create_worker_thread(task)
    registry.create(worker_id, type='build', mode='worker', parent_id='con_ORCH123')

# 3. Track worker progress
for worker_id in workers:
    registry.update(worker_id, status='complete', progress_pct=100)

# 4. Query worker status
workers = registry.get_workers('con_ORCH123')
completed = sum(1 for w in workers if w['status'] == 'complete')

# 5. Close orchestrator
registry.close('con_ORCH123', aar_path='/path/to/aar/')
```

---

## CLI Tools

### `convo-list` - List conversations

```bash
# List all conversations
n5_convo_list.py

# Filter by type
n5_convo_list.py --type build

# Filter by status
n5_convo_list.py --status active

# Show only starred
n5_convo_list.py --starred

# Show workers for orchestrator
n5_convo_list.py --parent con_ORCH123

# JSON output
n5_convo_list.py --json
```

### `convo-search` - Text search

```bash
# Search focus/objective/tags
n5_convo_search.py "authentication"

# Search with filters
n5_convo_search.py "API" --type build --status complete

# JSON output
n5_convo_search.py "database" --json
```

### `convo-show` - Show details

```bash
# Show basic info
n5_convo_show.py con_ABC123

# Show full details (artifacts, issues, learnings, decisions)
n5_convo_show.py con_ABC123 --full

# JSON output
n5_convo_show.py con_ABC123 --json
```

---

## API Reference

### ConversationRegistry Class

```python
from conversation_registry import ConversationRegistry

registry = ConversationRegistry()  # Uses default DB path

# Create conversation
registry.create(
    convo_id="con_ABC123",
    type="build",
    status="active",
    mode="standalone",
    parent_id=None,  # For workers, set to orchestrator ID
    focus="Build authentication system",
    objective="Implement JWT auth",
    tags=["auth", "security"],
    workspace_path="/path/to/workspace",
    state_file_path="/path/to/SESSION_STATE.md"
)

# Update conversation
registry.update(convo_id, progress_pct=50, status="active")

# Add artifact
registry.add_artifact(
    convo_id,
    filepath="/home/workspace/N5/scripts/auth.py",
    artifact_type="script",
    description="JWT authentication handler"
)

# Log issue (only significant issues)
registry.log_issue(
    convo_id,
    severity="blocker",  # or system_threat, learning_opportunity
    category="tool_failure",  # or logic_error, external_api, design_flaw
    message="Database connection failing",
    context="Stack trace: ..."
)

# Log decision
registry.log_decision(
    convo_id,
    decision="Use JWT instead of sessions",
    rationale="Stateless, scales better",
    alternatives="Sessions, OAuth"
)

# Import learning from lessons system
registry.import_learning(convo_id, lesson_data_dict)

# Close conversation
registry.close(convo_id, aar_path="/path/to/aar/")

# Get conversation
convo = registry.get(convo_id)
convo_full = registry.get_with_details(convo_id)

# Search conversations
results = registry.search(
    query="authentication",
    filters={"type": "build", "status": "active"},
    limit=50
)

# Get workers for orchestrator
workers = registry.get_workers(orchestrator_id)

# Get statistics
stats = registry.get_stats()
```

---

## Best Practices

### When to Log Issues

**DO log:**
- ✅ Blockers that halt progress
- ✅ System threats (data loss, security, instability)
- ✅ Learning opportunities (novel solutions to common problems)
- ✅ Repeated failures (same issue 3+ times)

**DON'T log:**
- ❌ Single tool failures that are immediately retried
- ❌ Expected errors (validation failures, user input errors)
- ❌ Minor warnings that don't affect outcomes
- ❌ Issues that are immediately resolved

### When to Log Decisions

**DO log:**
- ✅ Architecture choices (database selection, framework choice)
- ✅ Trade-off decisions (performance vs simplicity)
- ✅ Rejected alternatives (considered but not chosen)
- ✅ Design patterns selected

**DON'T log:**
- ❌ Implementation details (variable names, file locations)
- ❌ Temporary workarounds
- ❌ Standard practices (using git, writing tests)

### Artifact Types

- `script` - Executable code (.py, .sh, .js)
- `document` - Documentation, reports, notes (.md, .pdf)
- `data` - Datasets, exports, databases (.csv, .json, .db)
- `config` - Configuration files (.yaml, .json, .env)
- `command` - N5 command definitions (.md in N5/commands/)

---

## File Locations

- **Database:** `/home/workspace/N5/data/conversations.db`
- **Scripts:** `/home/workspace/N5/scripts/conversation_registry.py`
- **CLI Tools:** `/home/workspace/N5/scripts/n5_convo_*.py`
- **Commands:** Registered in `/home/workspace/Recipes/recipes.jsonl`

---

## Examples

### Example 1: Build Thread

```python
# Initialize build conversation
registry.create(
    "con_AUTH001",
    type="build",
    focus="JWT authentication system",
    tags=["auth", "security", "backend"]
)

# Track artifacts
registry.add_artifact("con_AUTH001", "/home/workspace/N5/scripts/jwt_handler.py", "script")
registry.add_artifact("con_AUTH001", "/home/workspace/Documents/auth_design.md", "document")

# Log decision
registry.log_decision(
    "con_AUTH001",
    decision="Use PyJWT library",
    rationale="Well-maintained, supports RS256",
    alternatives="python-jose, authlib"
)

# Close when complete
registry.close("con_AUTH001", aar_path="/home/workspace/N5/logs/threads/2025-10-24_auth-build")
```

### Example 2: Orchestrator with Workers

```python
# Create orchestrator
registry.create("con_ORCH001", type="build", mode="orchestrator", focus="Multi-file refactor")

# Create workers
for i, task in enumerate(tasks):
    worker_id = f"con_WORK{i:03d}"
    registry.create(
        worker_id,
        type="build",
        mode="worker",
        parent_id="con_ORCH001",
        focus=task.description
    )

# Query progress
workers = registry.get_workers("con_ORCH001")
progress = sum(w['progress_pct'] for w in workers) / len(workers)
print(f"Overall progress: {progress}%")

# Check for blockers
blocked = [w for w in workers if w['status'] == 'blocked']
if blocked:
    print(f"Blocked workers: {[w['id'] for w in blocked]}")
```

### Example 3: Finding Related Work

```bash
# Find all conversations about authentication
n5_convo_search.py "auth" --type build

# Find active build conversations
n5_convo_list.py --type build --status active

# Show full details of a past implementation
n5_convo_show.py con_AUTH001 --full
```

---

## Migration from Existing Systems

**If you have existing conversations:**

1. Conversations created after registry implementation will auto-sync
2. Historical conversations are NOT automatically backfilled
3. To backfill: Create a migration script that reads SESSION_STATE.md files and creates registry entries

**Backfill script (example):**

```python
from pathlib import Path
from conversation_registry import ConversationRegistry

registry = ConversationRegistry()
workspaces = Path("/home/.z/workspaces").glob("con_*")

for workspace in workspaces:
    convo_id = workspace.name
    state_file = workspace / "SESSION_STATE.md"
    
    if state_file.exists():
        # Parse state file and create registry entry
        # (Implementation depends on your state file format)
        pass
```

---

## Troubleshooting

### Registry sync fails during session init

**Symptom:** Warning logged but session continues

**Cause:** Database file permissions or disk space

**Fix:**
```bash
# Check database exists and is writable
ls -lh /home/workspace/N5/data/conversations.db

# Check disk space
df -h /home/workspace

# Reinitialize database
python3 /home/workspace/N5/scripts/conversation_registry.py --init
```

### Duplicate conversation IDs

**Symptom:** `create()` returns False, logs "already exists"

**Cause:** Conversation already registered (possibly from previous session)

**Fix:** Use `update()` instead of `create()`, or check if conversation exists first:

```python
convo = registry.get(convo_id)
if not convo:
    registry.create(convo_id, ...)
else:
    registry.update(convo_id, ...)
```

### Search returns no results

**Symptom:** Known conversations don't appear in search

**Cause:** Search only queries `focus`, `objective`, and `tags` fields

**Fix:** Ensure these fields are populated during conversation creation:

```python
registry.update(convo_id, focus="Clear description", tags=["tag1", "tag2"])
```

---

## Principles Applied

- **P2 (SSOT):** Registry is single source of truth for conversation metadata
- **P5 (Anti-Overwrite):** All operations are additive or update-only, no destructive actions
- **P19 (Error Handling):** All registry methods include try/except with logging
- **P18 (Verify State):** Get methods verify data before returning
- **P1 (Human-Readable):** SQLite with simple schema, CLI tools for inspection

---

## Future Enhancements

- [ ] Backfill script for historical conversations
- [ ] Web UI for browsing conversations
- [ ] Graph visualization of orchestrator→worker relationships
- [ ] Automatic tagging based on artifacts created
- [ ] Integration with git commits (link conversations to code changes)
- [ ] Slack/email notifications for blocked conversations
- [ ] Analytics dashboard (most common issues, average build time, etc.)

---

**See also:**
- file 'N5/scripts/conversation_registry.py' - Core implementation
- file 'N5/scripts/session_state_manager.py' - Integration point
- file 'N5/commands/conversation-end.md' - Conversation closure workflow
