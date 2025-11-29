---
created: 2025-11-17
last_edited: 2025-11-23
version: 1.1
---

# Meeting Archive Automation (MG-7C)

Automated system for moving completed **[C] meetings** from Inbox to permanent Archive with database tracking.

## Overview

**Purpose:** Process `[C]`-marked meetings that have completed all follow-up actions and move them to versioned archive directories while maintaining a pipeline database registry.

**Execution Model:** Automated task every 12 hours + manual execution via script.

**Status:** ✅ Deployed and tested (C-state variant)

---

## Components

### 1. Archive Script
**File:** `/home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py`

**Functionality (MG-7C):**
- Scans Inbox for meetings whose folder names end with `_[C]`.
- For each `[C]` meeting in the Inbox run:
  - Validates `manifest.json` with existing completion rules.
  - Cleans nested duplicate folders (2025-* pattern within meeting).
  - Registers the meeting in the pipeline database (`meeting_pipeline.db`, `meetings` table) with `status="complete"`.
  - Calculates the archive quarter from the YYYY-MM-DD prefix.
  - **Strips the `_[C]` suffix** and moves the meeting into `Archive/{YEAR}-Q{Q}/{clean_name}`.
- Processes **all** `[C]` meetings found in the Inbox during a single execution.

**Execution:**
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py
```

**Output:**
- Timestamped logs with status indicators (✓/✗/✅/→).
- Each successfully processed meeting moved from Inbox to Archive.
- Graceful exit if no `[C]` meetings are ready.

---

## Directory Structure

### Inbox Location
```
/home/workspace/Personal/Meetings/Inbox/
├── 2025-11-20_meeting-name_[C]/           ← Ready for archive (follow-ups completed)
│   ├── manifest.json
│   ├── transcript.md (or .jsonl)
│   ├── B01_DETAILED_RECAP.md
│   ├── B02_COMMITMENTS.md
│   └── ...
└── [other meetings]
```

### Archive Structure
```
/home/workspace/Personal/Meetings/Archive/
├── 2025-Q3/
├── 2025-Q4/
│   ├── 2025-11-20_meeting-name/           ← Cleaned name (no suffix)
│   ├── 2025-11-21_another-meeting/
│   └── ...
└── ...
```

**Quarter Calculation:**
- Q1: January (01-03)
- Q2: April (04-06)
- Q3: July (07-09)
- Q4: October (10-12)

---

## Scheduled Task Configuration (MG-7C)

**Task Name:** ⇱ 🧠 Meeting Archive Automation [MG-7C]

**Schedule:** Every 12 hours at 04:00 and 16:00 (ET).

**RRULE:** `FREQ=DAILY;BYHOUR=4,16;BYMINUTE=0`

**Frequency:** Twice daily (automated), processing all `_[C]` meetings each run.

---

## Execution Flow (Per Run)

```
START
  ↓
[Scan Inbox for folders ending in `_[C]`]
  ├─ None found → Log "No [C] meetings ready" → EXIT (0)
  ├─ One or more found → Process all of them
  ↓
For each `[C]` meeting:
  ↓
[Validate manifest.json]
  ├─ Missing/unparseable → Log error, skip meeting
  ├─ Blocks fail completion rules → Log error, skip meeting
  ├─ Valid → Continue
  ↓
[Clean nested duplicates]
  ├─ Find 2025-* subdirectories
  ├─ Delete each with rm -rf
  ├─ Log each deletion → Continue
  ↓
[Register in database]
  ├─ Extract meeting_id by stripping `_[C]`
  ├─ Find transcript (priority: transcript.md → transcript.jsonl → first B*.md)
  ├─ Detect meeting_type from manifest classification
  ├─ Call add_to_database.py with status="complete"
  ├─ On failure → Log error, skip meeting
  ↓
[Calculate archive path]
  ├─ Parse YYYY-MM-DD from folder name
  ├─ Calculate quarter (Q1-Q4)
  ├─ Path: Archive/YYYY-Q[N]/
  ↓
[Move meeting]
  ├─ Remove `_[C]` suffix from name
  ├─ If destination exists, merge contents then remove source folder
  ├─ Else, mv source folder to destination
  ├─ Log "✅ Archived" on success or error on failure
  ↓
After last `[C]` meeting:
  ↓
[Log completion summary and EXIT (0)]
```

---

## Database Registry

Archived meetings are recorded in `/home/workspace/N5/data/meeting_pipeline.db` in the `meetings` table:

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

MG-7C uses `status="complete"` when registering C-state archives.

---


