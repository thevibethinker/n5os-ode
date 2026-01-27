---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_Tq9eOqW4T0rTnKvb
---

# Meeting Ingestion Skill - Debug Review

## Issues Found & Fixed

### 1. ❌→✅ Import Path Bug in Skill Scripts
**Problem:** `pull.py` and `processor.py` used `from N5.scripts.meeting_config import ...` which doesn't work when N5/scripts is added to sys.path.

**Fix:** Changed to `from meeting_config import ...`

**Files Fixed:**
- `Skills/meeting-ingestion/scripts/pull.py`
- `Skills/meeting-ingestion/scripts/processor.py`

### 2. ❌→✅ Import Path Bug in N5/scripts
**Problem:** 8 files in `N5/scripts/` used `from N5.scripts.X import Y` pattern, which breaks when scripts are imported via sys.path manipulation.

**Fix:** Changed all to use relative imports `from X import Y`

**Files Fixed:**
- `N5/scripts/meeting_registry.py`
- `N5/scripts/meeting_orchestrator.py`
- `N5/scripts/meeting_api_integrator.py`
- `N5/scripts/meeting_auto_monitor.py`
- `N5/scripts/meeting_monitor.py`
- `N5/scripts/meeting_state_manager.py`
- `N5/scripts/meeting_transcript_watcher.py`
- `N5/scripts/meeting_weekly_organizer.py`

### 3. ✅ FIXED: pull.py Zo API Schema Issue
**Problem:** `pull.py` used `/zo/ask` with a complex `output_format` schema containing nested arrays of objects. The Zo API doesn't support this schema complexity.

**Fix Applied:** Rewrote `call_zo_api()` to not use `output_format`. Instead:
1. Prompt asks Zo to return data in a specific text format
2. New `parse_file_list_from_text()` function parses multiple response formats (list, JSON, table)
3. Robust fallback parsing handles various Zo response styles

**Current Status:** FIXED - API calls work, parsing is robust

**Note on Performance:** Drive operations via `/zo/ask` take 2-5 minutes because they spawn a full Zo session. This is expected behavior. The unified agent will handle this gracefully since agents have longer timeouts than interactive commands.

## Test Results (Post-Fix)

| Command | Status | Notes |
|---------|--------|-------|
| `meeting_cli.py status` | ✅ PASS | Shows registry and staging queue correctly |
| `meeting_cli.py pull --dry-run` | ✅ PASS | Works but slow (~2-5 min for Drive operations) |
| `meeting_cli.py process --dry-run` | ✅ PASS | Correctly identifies meetings and manifests blocks |
| `meeting_cli.py archive --dry-run` | ✅ PASS | Correctly scans and categorizes meetings |
| Text parsing (all formats) | ✅ PASS | Parses list, JSON, and table formats |

## Recommendations

1. **Immediate:** The unified agent will work for `process` and `archive` commands, but `pull` will fail. The agent should be updated to handle pull failures gracefully OR pull should be redesigned.

2. **Short-term:** Redesign `pull.py` to either:
   - Not use structured output (parse text)
   - Be an agent-only command (not script-callable)
   - Use direct Google Drive API via service account

3. **Architecture Note:** The `/zo/ask` API is designed for simple structured outputs (scalars, enums). Complex nested data should be returned as text or files, not structured JSON.
