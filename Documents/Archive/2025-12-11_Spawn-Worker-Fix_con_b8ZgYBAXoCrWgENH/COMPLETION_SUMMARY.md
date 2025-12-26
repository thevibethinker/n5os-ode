---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Spawn Worker & Build Orchestrator Improvements

## Summary

Fixed the spawn_worker.py "Not specified" parent context bug and created an improved v2 architecture.

## Root Cause Analysis

The original script failed to extract parent context because:

1. **Field name mismatch**: SESSION_STATE uses `**Type:**` but script looked for `**Primary Type:**`
2. **Placeholder handling**: `TBD` values weren't filtered, resulting in "Not specified"
3. **Progress field ignored**: The richest context was in `**Progress:**` but wasn't extracted
4. **No fallback**: When SESSION_STATE was sparse, no intelligent inference happened

## Changes Made

### 1. spawn_worker.py (v2.0)

**New file:** `file 'N5/scripts/spawn_worker.py'`
**Backup:** `file 'N5/scripts/spawn_worker_v1_backup.py'`

**Key improvements:**
- **LLM-first design**: `--context` JSON argument lets LLM provide all context directly
- **Multi-source field extraction**: Tries multiple field names (Type, Primary Type, Conversation Type, etc.)
- **Progress field extraction**: Extracts the Progress field which often has the best context
- **Placeholder filtering**: Recognizes TBD, N/A, unknown as placeholders
- **`--generate-ids` mode**: Returns JSON with IDs/paths for LLM to write files manually
- **Recent artifacts list**: Shows what files were created in parent workspace
- **Dry-run support**: Preview output without writing

**Usage modes:**
```bash
# LLM-provided context (recommended)
python3 spawn_worker.py --parent con_XXX --context '{"instruction": "...", ...}'

# Legacy mode (parses SESSION_STATE)
python3 spawn_worker.py --parent con_XXX --instruction "..."

# ID generation only
python3 spawn_worker.py --parent con_XXX --generate-ids
```

### 2. build_orchestrator_v2.py

**New file:** `file 'N5/scripts/build_orchestrator_v2.py'`

**Key improvements:**
- **SQLite storage**: Proper database instead of JSONL
- **spawn_worker integration**: Uses spawn_worker.py for actual thread spawning
- **Project/worker management**: Create, list, status, complete commands
- **Dependency tracking**: Only spawns workers whose dependencies are complete
- **Status reports**: Generate markdown status reports
- **Worker update scanning**: Scans parent workspace for worker updates

### 3. Updated Prompt

**Updated file:** `file 'Prompts/Spawn Worker.prompt.md'`

Documents v2.0 features including --context, --generate-ids, and build orchestrator integration.

## Test Results

### Before (v1):
```
## Parent Context

**What parent is working on:**  
Not specified

**Parent objective:**  
Not specified
```

### After (v2):
```
## Parent Context

**What parent is working on:**  
[From Progress] Complete: Database, CLI, 5 adaptive conversational reflection prompts (morning pages, evening, weekly, gratitude, temptation)

**Parent objective:**  
_Not specified_

**Parent status:**  
active (Build)

**Parent conversation type:**  
Build
```

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `N5/scripts/spawn_worker.py` | Rewritten | v2.0 with LLM-first design |
| `N5/scripts/spawn_worker_v1_backup.py` | Created | Backup of original |
| `N5/scripts/build_orchestrator_v2.py` | Created | SQLite-backed orchestrator |
| `Prompts/Spawn Worker.prompt.md` | Updated | Documents v2.0 features |

## Recommendations for Further Improvement

1. **SESSION_STATE template**: Update session_state_manager.py to better prompt for Focus/Objective values during init
2. **Auto-context extraction**: Consider an `n5_extract_context.py` that uses LLM to summarize conversation state
3. **Worker heartbeat**: Add periodic status writes from workers to detect stuck workers
4. **Build dashboard**: Create a web UI for monitoring multi-worker projects

---

*Completed: 2025-12-10 22:49 ET*

