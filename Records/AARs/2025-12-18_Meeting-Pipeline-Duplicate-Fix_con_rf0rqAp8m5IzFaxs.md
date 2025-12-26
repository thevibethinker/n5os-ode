---
created: 2025-12-18
last_edited: 2025-12-18
version: 1
provenance: con_UvE3epNbKjbL4Ss9
---
# AAR: MG-5/MG-6 Pipeline Fix - [M]→[P] State Transition Restoration

## Summary

Fixed the meeting pipeline to restore correct state transitions. MG-5 (Follow-Up Email Generation) was not running because the Weekly Organizer moved [M] meetings to Week-of folders before they reached [P] state.

## Problem Statement

**Root Cause:** Weekly Organizer was moving both `[M]` AND `[P]` folders:
```python
# BEFORE (broken)
if "_[M]" in item.name or "_[P]" in item.name:
    all_meetings.append(("inbox", item))
```

**Intended Pipeline:**
```
[Raw] → MG-1 → [M] → MG-2 (blocks) → MG-6 → [P] → MG-5 (follow-up email) → Weekly Organizer → Week-of/
```

**Broken Pipeline:**
```
[M] → Weekly Organizer → Week-of/ (MG-5 never runs)
```

## Resolution

### 1. Fixed Weekly Organizer (`N5/scripts/meeting_weekly_organizer.py`)

Changed line 167-180 to ONLY move `[P]` folders:
```python
# AFTER (fixed)
if "_[P]" in item.name:
    # [P] folders are fully processed and ready to move
    all_meetings.append(("inbox", item))
elif "_[M]" in item.name:
    # [M] folders need more processing - do NOT move yet
    print(f"  Skipping [M] folder (awaiting MG-6 → [P] transition): {item.name}")
```

### 2. Created MG-6 Scheduled Task

- **Purpose:** Transition [M] → [P] after block generation
- **Schedule:** Hourly at :45 (9am-8pm ET)
- **Script:** `N5/scripts/meeting_pipeline/m_to_p_transition.py`

### 3. Created Backfill Script

- **Location:** `N5/scripts/maintenance/backfill_followup_emails.py`
- **Purpose:** Identify meetings in Week-of folders needing FOLLOW_UP_EMAIL.md
- **Result:** Found 12 meetings needing backfill

## Pipeline Schedule (Corrected)

| Task | Time | Purpose |
|------|------|---------|
| MG-1 | :15 (8-20h) | Generate manifest for raw meetings |
| MG-2 | :15 (8-20h) | Generate intelligence blocks |
| **MG-6** | :45 (9-20h) | **[M] → [P] transition (NEW)** |
| MG-3 | :30 | Generate blurbs |
| MG-4 | :30 | Warm intro drafts |
| MG-5 | :45 (9,12,15,18) | Follow-up email generation |
| Weekly Organizer | :30 (3,9,15,21) | Move [P] to Week-of/ |

## Impact

- **Fixed:** MG-5 will now find [P] meetings in Inbox
- **Fixed:** Weekly Organizer respects pipeline state
- **Identified:** 12 historical meetings need manual backfill

## Backfill Status

Run `python3 N5/scripts/maintenance/backfill_followup_emails.py` to see meetings needing follow-up email generation.

## Lessons Learned

1. **State-based gating is critical** - moving meetings before pipeline completion breaks downstream tasks
2. **Keep [M] flag load-bearing** - the suffix system enables proper sequencing
3. **MG-6 was essential** - the [M]→[P] transition wasn't optional, it gates MG-5

## Artifacts

- Modified: `N5/scripts/meeting_weekly_organizer.py`
- Created: MG-6 scheduled task (ID in task list)
- Created: `N5/scripts/maintenance/backfill_followup_emails.py`
- Parent thread: con_rf0rqAp8m5IzFaxs

---
*Worker: WORKER_Faxs_20251218_140028*

