---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# Meeting Archive Workflow Documentation

**Scheduled Task ID:** `6c3bbe50-295d-4e7c-8cd6-4ee3456f26f9` (Latest - ACTIVE)  
**Alternative ID:** `177d8f70-4ec1-4038-98d2-c90b63de7320` (Older - can be deleted)  
**Schedule:** Hourly at :45 minutes (e.g., 12:45 ET, 1:45 ET, 2:45 ET)  
**Model:** Claude Haiku (gpt-5-mini for efficiency)  
**Delivery:** Email summary after each run

---

## Overview

Automated scheduled task to move completed [R] meetings from Inbox to permanent Archive location with database tracking.

**Key Features:**
- ✅ Runs every hour at :45 minutes
- ✅ Processes ONE meeting per run (sorted alphabetically)
- ✅ Validates manifest completion before archiving
- ✅ Registers in database for tracking
- ✅ Automatically calculates archive quarter (2025-Q1, Q2, Q3, Q4)
- ✅ Cleans nested duplicate folders
- ✅ Removes `_[R]` suffix when moving to archive
- ✅ Emails completion summary

---

## Workflow Steps (As Executed by Agent)

### 1. **Find [R] Meeting Ready for Archive**
```bash
ls -d /home/workspace/Personal/Meetings/Inbox/*_\[R\] 2>/dev/null | sort | head -1
```
- Returns FIRST [R] meeting (alphabetically sorted)
- If empty: exits cleanly with log message

### 2. **Validate Manifest Completion**
- Reads `manifest.json` from meeting folder
- Checks that ALL blocks have `"status": "completed"`
- If any pending: logs error and skips meeting (doesn't archive)

### 3. **Clean Nested Duplicates** (If Present)
```bash
find [meeting_path] -mindepth 1 -maxdepth 1 -type d -name "2025-*"
```
- Removes any nested duplicate folders
- Logs each cleanup action

### 4. **Register in Database**
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/add_to_database.py \
  [meeting_id] \
  --transcript [first_md_file] \
  --type internal \
  --status complete \
  --notes "Auto-archived from [R] state"
```
- Registers meeting in central database
- Exits if script fails (non-zero exit code)

### 5. **Calculate Archive Location**
- Extracts date from folder name: `YYYY-MM-DD`
- Calculates quarter from month:
  - Jan-Mar (01-03) = Q1
  - Apr-Jun (04-06) = Q2
  - Jul-Sep (07-09) = Q3
  - Oct-Dec (10-12) = Q4
- Archive path: `/home/workspace/Personal/Meetings/Archive/[YEAR]-Q[N]/`

### 6. **Move Meeting to Archive**
- Removes `_[R]` suffix from folder name
- Example: `2025-10-30_dbn-ctum-szz_[R]` → `2025-10-30_dbn-ctum-szz`
- Moves folder to archive with clean name
- Original [R] folder removed from Inbox

### 7. **Email Summary**
- Reports completion status
- Includes meeting name and archive location
- Lists any errors encountered

---

## File Structure

```
Personal/Meetings/
├── Inbox/
│   ├── 2025-10-30_dbn-ctum-szz_[R]/          ← Ready to archive
│   │   ├── manifest.json
│   │   ├── B01_DETAILED_RECAP.md
│   │   ├── B02_COMMITMENTS.md
│   │   └── ... (other blocks)
│   └── 2025-11-10_other-meeting_[R]/
│       └── (similar structure)
│
└── Archive/
    ├── 2025-Q1/
    │   ├── 2025-01-15_meeting-name/
    │   └── 2025-02-20_another-meeting/
    ├── 2025-Q2/
    │   └── ...
    ├── 2025-Q3/
    │   └── ...
    └── 2025-Q4/
        ├── 2025-10-23_Daily_team_stand-up/
        ├── 2025-10-24_Monthly-Vrijen-Alexis-Mishu/
        ├── 2025-10-30_dbn-ctum-szz/           ← Archived (name cleaned)
        └── ...
```

---

## Success Criteria

A successful archival run meets ALL of these conditions:

1. **No nested duplicates remain** in original location
2. **Database entry created** successfully (script exit code = 0)
3. **Meeting folder moved** to correct `Archive/YEAR-QN/` directory
4. **Original [R] folder removed** from Inbox
5. **Cleaned folder name** (without `_[R]` suffix) appears in Archive
6. **Email summary sent** with completion details

---

## Error Handling

| Error Condition | Action | Result |
|---|---|---|
| No [R] meetings found | Exit cleanly | No error logged (normal state) |
| manifest.json missing | Skip meeting | Logged, task continues |
| manifest.json unparseable | Skip meeting | Logged, task continues |
| Block has pending status | Skip meeting | Logged (don't archive incomplete) |
| Database script fails | Skip meeting | Logged with exit code |
| Filesystem move fails | Exit task | Logged, investigation required |

---

## Testing Results (Pre-Deployment)

✅ **All validation checks passed:**

- Manifest validation: All 8 blocks marked "completed"
- Nested duplicates: None found (clean state)
- Archive path calculation: Correct (2025-Q4)
- Folder name cleaning: Properly removes `_[R]` suffix
- Database registration: Successful update
- Archive directory: Exists and ready
- Dry run preview: Move command correct

---

## Database Integration

**Database Location:** `/home/workspace/N5/data/meeting_pipeline.db`

**Script:** `/home/workspace/N5/scripts/meeting_pipeline/add_to_database.py`

**Fields Updated:**
- `meeting_id` — Unique identifier (folder name without `_[R]`)
- `status` — Set to "complete"
- `completed_at` — ISO timestamp of archive operation
- `notes` — "Auto-archived from [R] state"

---

## Scheduled Task Details

**ID (ACTIVE):** `6c3bbe50-295d-4e7c-8cd6-4ee3456f26f9`

**ID (OLD - can delete):** `177d8f70-4ec1-4038-98d2-c90b63de7320`

**RRULE:**
```
FREQ=HOURLY;BYMINUTE=45
```

**Next Runs:**
- 2025-11-16 20:45 ET (initial)
- 2025-11-16 21:45 ET
- 2025-11-16 22:45 ET
- (continues hourly)

**Model:** `anthropic:claude-haiku-4-5-20251001` (Haiku for efficiency)

**Delivery Method:** Email (summary to your inbox)

---

## Usage Notes

### Starting the Workflow

The task runs **automatically every hour at :45 minutes**. No manual intervention needed.

### Current [R] Meetings in Inbox

```bash
ls -d /home/workspace/Personal/Meetings/Inbox/*_\[R\] | sort
```

Currently: 2 [R] meetings ready for archival (will be processed hourly)

### View Archives

```bash
ls -d /home/workspace/Personal/Meetings/Archive/2025-Q*/ | xargs -I{} sh -c 'echo "=== {} ===" && ls -1 {}'
```

### Database Query

```sql
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT meeting_id, status, completed_at FROM meetings WHERE status='complete' ORDER BY completed_at DESC LIMIT 10;"
```

---

## Notes for Future Maintenance

1. **Task runs every hour** — Very frequent, designed to keep [R] queue clear
2. **One meeting per run** — Prevents resource contention, ensures deterministic execution
3. **Silent on empty queue** — No error when no [R] meetings exist (normal state)
4. **Database-backed** — All archives tracked in central database for reporting
5. **Email summaries** — Each run emails completion details to tracking inbox

---

## Related Files

- `file 'Personal/Meetings/'` — Meeting storage structure
- `file 'N5/scripts/meeting_pipeline/add_to_database.py'` — Database registration script
- `file 'N5/data/meeting_pipeline.db'` — Central database

