---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Meeting Archive Automation

Automated system for moving completed [R] meetings from Inbox to permanent Archive with database tracking.

## Overview

**Purpose:** Process [R]-marked meetings that have completed all workflow blocks and move them to versioned archive directories while maintaining a pipeline database registry.

**Execution Model:** Daily automated task (4:00 AM ET) + manual execution via script

**Status:** ✅ Deployed and tested

---

## Components

### 1. Archive Script
**File:** `/home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py`

**Functionality:**
- Finds next [R] meeting in Inbox ready for archival
- Validates manifest.json with all blocks marked "completed"
- Cleans nested duplicate folders (2025-* pattern within meeting)
- Registers meeting in pipeline database
- Moves meeting to Archive/[YEAR]-Q[N]/ with cleaned name (removes _[R] suffix)

**Execution:**
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py
```

**Output:**
- Timestamped logs with status indicators (✓/✗/✅/→)
- Meeting moved from Inbox to Archive on success
- Graceful exit if no [R] meetings ready

### 2. Database Integration
**File:** `/home/workspace/N5/scripts/meeting_pipeline/add_to_database.py`

**Purpose:** Registers archived meetings in the pipeline tracking system

**Integration Points:**
- Called by archive script automatically
- Extracts meeting_id from folder name (removes _[R] suffix)
- Detects meeting type (INTERNAL/EXTERNAL) from manifest classification
- Finds transcript via fallback chain: transcript.md → transcript.jsonl → first block file
- Records meeting status as "complete"

---

## Directory Structure

### Inbox Location
```
/home/workspace/Personal/Meetings/Inbox/
├── 2025-10-30_meeting-name_[R]/           ← Ready for archive
│   ├── manifest.json                      ← Must have all blocks completed
│   ├── transcript.md (or .jsonl)
│   ├── B01_DETAILED_RECAP.md
│   ├── B02_COMMITMENTS.md
│   └── ... [additional blocks]
└── [other meetings]
```

### Archive Structure
```
/home/workspace/Personal/Meetings/Archive/
├── 2025-Q1/
├── 2025-Q2/
├── 2025-Q3/
├── 2025-Q4/
│   ├── 2025-10-30_meeting-name/            ← Cleaned name (no _[R])
│   ├── 2025-11-16_another-meeting/
│   └── ...
└── ...
```

**Quarter Calculation:**
- Q1: January (01-03)
- Q2: April (04-06)
- Q3: July (07-09)
- Q4: October (10-12)

---

## Validation Requirements

### Manifest Completion Check
All blocks in `manifest.json` must have `"status": "completed"`:

```json
{
  "blocks": [
    {
      "block_id": "B01_DETAILED_RECAP",
      "status": "completed"      ← REQUIRED
    },
    // ... all other blocks must also be "completed"
  ]
}
```

If any block has status != "completed", the meeting is skipped.

### File Requirements
- ✅ manifest.json must exist
- ✅ Transcript must exist (transcript.md, transcript.jsonl, or B*.md file)
- ✅ At least one block file (B*.md) for fallback

### Folder Naming
- Must start with YYYY-MM-DD date
- Must end with `_[R]` suffix
- Example: `2025-11-16_danielscrappy-poetcom_[R]`

---

## Scheduled Task Configuration

**Task Name:** 📅 Meeting Pipeline Processing

**Schedule:** Daily at 4:00 AM ET

**RRULE:** `FREQ=DAILY;BYHOUR=4;BYMINUTE=0`

**Next Run:** 2025-11-17T04:00:56-05:00

**Delivery:** Email report to user

**Frequency:** Once daily (automated)

---

## Execution Flow

### Single Meeting Processing

```
START
  ↓
[Find next [R] meeting in Inbox]
  ├─ No meetings → Log "✓ No [R] meetings ready" → EXIT (0)
  ├─ Found meeting → Continue
  ↓
[Validate manifest.json]
  ├─ Missing/unparseable → Log error → EXIT (0)
  ├─ Any pending blocks → Log error → EXIT (0)
  ├─ All completed → Continue
  ↓
[Clean nested duplicates]
  ├─ Find 2025-* subdirectories
  ├─ Delete each with rm -rf
  ├─ Log each deletion → Continue
  ↓
[Register in database]
  ├─ Extract meeting_id
  ├─ Find transcript (priority order)
  ├─ Detect meeting_type from manifest
  ├─ Call add_to_database.py
  ├─ Exit code != 0 → Log error → EXIT (0)
  ├─ Success → Continue
  ↓
[Calculate archive path]
  ├─ Parse YYYY-MM-DD from folder name
  ├─ Calculate quarter (Q1-Q4)
  ├─ Path: Archive/YYYY-Q[N]/
  ↓
[Create archive directory]
  ├─ mkdir -p [archive_dir]
  ├─ Continue
  ↓
[Move meeting]
  ├─ Remove _[R] suffix from name
  ├─ mv [meeting_path] [archive_path]/[cleaned_name]
  ├─ Failure → Log error → EXIT (1)
  ├─ Success → Log "✅ Archived: ..."
  ↓
EXIT (0) ✅
```

### Scheduled Daily Execution

The task runs at 4:00 AM ET and:
1. Processes ONE meeting per execution
2. Continues to next day if successful
3. Retries same meeting if failures occur
4. Sends email report of actions taken

---

## Error Handling & Recovery

### Error Scenarios

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| No [R] meetings ready | Log info, exit cleanly | No action needed |
| manifest.json missing | Skip meeting, log error | Add manifest.json to meeting |
| Blocks incomplete | Skip meeting, log error | Mark remaining blocks completed |
| Database registration fails | Skip meeting, log error | Fix database or script, retry |
| Move operation fails | Log error, exit error code | Check filesystem permissions, retry |
| Nested duplicates found | Delete each, log deletion | Continue processing |

### User Actions on Error

1. **Check logs:** Review email report for error details
2. **Identify issue:** See error messages for specific cause
3. **Fix upstream:** Add missing files, complete blocks, fix database
4. **Manual retry:** Run script manually or wait for next scheduled run
5. **Report issue:** Contact system if script errors indicate bugs

---

## Testing & Validation

### Manual Execution Test
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py
```

Expected output:
```
[HH:MM:SS] → Processing: [meeting_name]
[HH:MM:SS] ✓ Registered in database: [meeting_name]
[HH:MM:SS] ✅ Archived: [meeting_name] → Archive/YYYY-Q[N]/[cleaned_name]
```

### Validation Steps
1. ✅ Check meeting moved from Inbox to Archive
2. ✅ Verify folder name has _[R] suffix removed
3. ✅ Confirm meeting in correct quarter directory
4. ✅ Query database to verify registration
5. ✅ Inspect logs for timestamp and status indicators

---

## Database Registry

### Schema
```sql
CREATE TABLE meetings (
  meeting_id TEXT PRIMARY KEY,
  transcript_path TEXT,
  meeting_type TEXT,
  status TEXT,
  detected_at TEXT,
  completed_at TEXT,
  notes TEXT
);
```

### Query Examples
```bash
# List archived meetings
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT meeting_id, status, completed_at FROM meetings WHERE status='complete' ORDER BY completed_at DESC LIMIT 10"

# Check specific meeting
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT * FROM meetings WHERE meeting_id='2025-10-30_dbn-ctum-szz'"
```

---

## Maintenance

### Weekly Review
- Monitor email reports for recurring errors
- Check database for registration success rate
- Verify no meetings "stuck" with pending blocks
- Confirm archive directories growing appropriately

### Monthly Deep Review
- Check for stale [R] meetings not being archived
- Verify quarter calculations are correct
- Audit database integrity (orphaned records, duplicates)
- Review script performance and error rate

### Troubleshooting
- **Meetings not archiving:** Check manifest.json for completed blocks
- **Database errors:** Run `add_to_database.py` manually with `--help`
- **Archive path wrong:** Verify date parsing in script
- **Duplicate cleanup failing:** Check nested folder permissions

---

## Related Files

- **Script:** `file 'N5/scripts/meeting_pipeline/archive_completed_meetings.py'`
- **Database Script:** `file 'N5/scripts/meeting_pipeline/add_to_database.py'`
- **Meeting Storage:** `file 'Personal/Meetings/'`
- **Archive Structure:** `/home/workspace/Personal/Meetings/Archive/`
- **Scheduled Task:** 📅 Meeting Pipeline Processing (Daily 4:00 AM ET)

---

## Success Metrics

✅ **Deployed Successfully**
- 2 initial [R] meetings processed and archived
- Database registration working correctly
- Scheduled task configured for daily execution
- All error handling paths tested
- Clean logs with proper timestamps

---

