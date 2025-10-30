# System Bulletins

**Purpose:** Automated changelog providing AI transparency into recent system evolution

**Version:** 1.0 | **Created:** 2025-10-27

---

## Overview

The System Bulletins system automatically tracks and documents significant changes to the workspace, providing AI visibility into recent system evolution. This helps prevent context gaps when encountering system irregularities or missed changes.

### Key Benefits

1. **Transparency:** AI always aware of recent architectural changes
2. **Context:** Explains "why does this exist?" when encountering new patterns
3. **Completeness:** Catches changes that may have been missed during system-wide updates
4. **Efficiency:** Auto-loaded in session state = no manual tracking

---

## Components

### 1. Bulletin Generator

**Script:** `file 'N5/scripts/bulletin_generator.py'`  
**Frequency:** Every 2 hours (scheduled task)  
**Function:** Scans git commits + conversations.db for significant changes

#### Change Detection Methods

**Git Commits:**
- Scans git log since last run (or 10 days on first run)
- Applies significance filters based on file patterns
- Groups changes by commit

**Conversations Database:**
- Queries learnings table for captured insights
- Queries artifacts table for created outputs
- Links changes to specific conversations

#### Significance Criteria

```
HIGH Priority:
- N5/scripts/*.py (core scripts)
- Knowledge/architectural/principles/*.md (principle changes)
- N5/prefs/*.md (preference updates)
- N5/schemas/*.json (schema changes)
- Recipes/recipes.jsonl (command registry)

MEDIUM Priority:
- N5/orchestration/*.md (workflow changes)
- Documents/System/**/*.md (system docs)
- Recipes/*.md (recipe changes)
- Knowledge/**/*.md (knowledge updates)

LOW Priority:
- All other N5/** and Documents/** changes
- Filtered unless conversation has explicit learnings/artifacts
```

### 2. Bulletin Storage

**File:** `file 'N5/data/system_bulletins.jsonl'`  
**Format:** JSONL (one JSON object per line)  
**TTL:** 10 days (auto-pruned)

#### Entry Schema

```json
{
  "timestamp": "2025-10-27T03:59:39+00:00",
  "bulletin_id": "bul_abc123def456",
  "change_type": "architecture|workflow_changed|learning_captured|artifact_created|breaking_change|documentation",
  "scope": "N5/scripts, Knowledge/architectural",
  "summary": "Brief one-line description",
  "details": "Full commit message or learning description",
  "conversation_id": "con_xyz789" (optional),
  "files_affected": ["path/to/file1", "path/to/file2"],
  "git_commit": "abc123de" (optional),
  "significance": "high|medium|low"
}
```

### 3. Session State Integration

**Function:** `SessionStateManager.load_system_bulletins()`  
**When:** Auto-loaded on session state initialization  
**Output:** Markdown-formatted summary of last 10 days

#### Loading Behavior

- **Always loaded:** Every conversation gets bulletins in context
- **Format:** Grouped by significance (high/medium)
- **Size:** ~50-100 lines markdown = minimal context cost
- **Value:** High - explains irregularities when encountered

---

## Usage

### Manual Generation

```bash
# Dry run (preview changes)
python3 /home/workspace/N5/scripts/bulletin_generator.py --dry-run

# Real run
python3 /home/workspace/N5/scripts/bulletin_generator.py
```

### View Bulletins

```bash
# Count entries
wc -l /home/workspace/N5/data/system_bulletins.jsonl

# View recent high-priority changes
jq 'select(.significance == "high")' /home/workspace/N5/data/system_bulletins.jsonl | head -5

# View all from specific date
jq 'select(.timestamp | startswith("2025-10-27"))' /home/workspace/N5/data/system_bulletins.jsonl
```

### Check State

```bash
# View last run timestamp and count
cat /home/workspace/N5/data/.bulletin_state.json
```

---

## Scheduled Task

**Task ID:** Retrieved via `list_scheduled_tasks`  
**Schedule:** Every 2 hours  
**Command:** `python3 /home/workspace/N5/scripts/bulletin_generator.py`

### Rationale: 2-Hour Frequency

- **Coverage:** Captures changes quickly without lag
- **Efficiency:** Doesn't scan too many conversations at once
- **Bounded:** 2hr × 12/day × 10 days = 120 runs max
- **Balance:** Can do significant coding in 2 hours

---

## Maintenance

### First Run Behavior

- **Backfills:** Scans last 10 days of git commits + conversations
- **Creates:** Initial bulletin file with all significant changes
- **Sets:** State file with last run timestamp

### Incremental Processing

- **Scans:** Only changes since last run timestamp
- **Appends:** New bulletins to file
- **Prunes:** Entries older than 10 days
- **Updates:** State file with new timestamp

### Manual Intervention

If bulletins need rebuild:
1. Delete state file: `rm /home/workspace/N5/data/.bulletin_state.json`
2. Delete bulletins: `rm /home/workspace/N5/data/system_bulletins.jsonl`
3. Run script: `python3 /home/workspace/N5/scripts/bulletin_generator.py`

---

## Integration Points

### 1. Session State Manager

**File:** `file 'N5/scripts/session_state_manager.py'`  
**Function:** `load_system_bulletins()` called during init with `--load-system` flag  
**Output:** Logs bulletin summary to stdout for AI context

### 2. System Rules

**Rule:** Auto-load bulletins in session state init  
**Location:** User rules → ALWAYS APPLIED  
**Effect:** Every conversation starts with bulletin context

### 3. Conversation Registry

**Source:** Queries `file 'N5/data/conversations.db'` for learnings and artifacts  
**Tables:** learnings, artifacts  
**Filters:** status='active', timestamp>last_run

---

## Principles Applied

- **P2 (SSOT):** Bulletins stored in single jsonl file
- **P7 (Dry-Run):** Script supports --dry-run flag
- **P11 (Failure Modes):** Error handling with logging
- **P15 (Complete):** Verifies writes, state updates
- **P18 (Verify State):** Checks file existence, counts
- **P19 (Error Handling):** Try/except with context logging
- **P20 (Modular):** Clean separation of concerns

---

## Future Enhancements

### Potential Additions

1. **Bulletin Search:** CLI tool to query bulletins by date/type/significance
2. **Bulletin Digest:** Weekly summary email of major changes
3. **Cross-Reference:** Link bulletins to specific principle violations or learnings
4. **Trend Detection:** Flag patterns (e.g., same file changed 5x in 2 days)
5. **Integration Hooks:** Notify on breaking changes via webhook

### Not Planned

- **Real-time monitoring:** 2-hour batch processing is sufficient
- **Full git history:** 10-day window handles recent evolution
- **External APIs:** Self-contained system only

---

## Troubleshooting

### No Bulletins Generated

**Check:**
1. Git commits in last period: `git log --since="2 hours ago"`
2. Database has learnings: `sqlite3 N5/data/conversations.db "SELECT COUNT(*) FROM learnings WHERE status='active'"`
3. Files match significance patterns

### Bulletins Not Loading

**Check:**
1. File exists: `ls -l N5/data/system_bulletins.jsonl`
2. Valid JSON: `head -1 N5/data/system_bulletins.jsonl | jq .`
3. Session state init ran: Check logs for "System Bulletins Summary"

### Old Entries Not Pruned

**Check:**
1. TTL calculation: Entries should be removed after 10 days
2. Run manually: `python3 N5/scripts/bulletin_generator.py`
3. Verify count decreased

---

## References

- `file 'N5/scripts/bulletin_generator.py'` - Generator script
- `file 'N5/scripts/session_state_manager.py'` - Session integration
- `file 'N5/data/system_bulletins.jsonl'` - Bulletin storage
- `file 'N5/data/.bulletin_state.json'` - State tracking
- `file 'N5/data/conversations.db'` - Source database

---

**Last Updated:** 2025-10-27 00:00 ET  
**Status:** Active, running every 2 hours
