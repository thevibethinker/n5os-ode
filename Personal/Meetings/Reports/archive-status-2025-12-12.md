---
created: 2025-12-12
last_edited: 2025-12-12
version: 1.0
---

# Meeting Archive Status Report — MG-7 Diagnostic

**Generated:** 2025-12-12 21:01:57 UTC  
**Stage:** MG-7 (Read-Only Diagnostic)  
**Status:** 🔒 Deprecated as archiver – diagnostic only

---

## Executive Summary

This is a **read-only diagnostic report** of `[P]` (Processed) meetings currently in Inbox. **No files have been moved or archived.**

The actual archival workflow is handled exclusively by **MG-7C** (C-state Archive Automation) on meetings marked with `_[C]` suffix.

---

## Inbox Status

**Total [P] (Processed) meetings:** 23

### Age Distribution

- **Less than 7 days old:** 15 meetings
- **7+ days old (archive candidates):** 8 meetings

### Archive Candidates (7+ days old)

The following 8 meetings are eligible for transition to C-state:

1. `2025-12-01_logantheapplyai_[P]` (11 days old)
2. `2025-12-02_loganmycareerspancom_[P]` (10 days old)
3. `2025-12-02_logantheapplyaiilsetheapplyaidannytheapplyairochelmycareerspancomilyamycareerspancom_logantheapplyai_ilsetheapplyai_dannytheapplyai_[P]` (10 days old)
4. `2025-12-04_logantheapplyaiilsetheapplyaidannytheapplyairochelmycareerspancomilyamycareerspancom_logantheapplyai_ilsetheapplyai_dannytheapplyai_[P]` (8 days old)
5. `2025-12-05_ericconsonantvc_[P]` (7 days old)
6. `2025-12-05_logantheapplyai_[P]` (7 days old)
7. `2025-12-05_logantheapplyaiilsetheapplyaidannytheapplyairochelmycareerspancomilyamycareerspancom_logantheapplyai_ilsetheapplyai_dannytheapplyai_[P]` (7 days old)
8. `2025-12-05_rgj-bduo-zer_[P]` (7 days old)

---

## Workflow: How to Archive [P] Meetings

MG-7 is now **read-only only**. To archive meetings:

### Step 1: Mark Meetings as C-State
Use the **"Meeting Mark C-State"** prompt or the canonical script to transition a [P] meeting to [C] state:

```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/mark_meeting_c_state.py <meeting-folder>
```

This renames the folder from `_[P]` to `_[C]`, indicating it's ready for archival.

### Step 2: Run MG-7C Archive Automation
MG-7C runs **automatically twice daily** (04:00 and 16:00 ET) or can be run manually:

```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py
```

MG-7C will:
1. Find all `_[C]` folders in Inbox
2. Extract date and determine quarter: `{YYYY}-Q{Q}`
3. Move folder to: `/home/workspace/Personal/Meetings/Archive/{YYYY}-Q{Q}/`
4. Update manifest with `status='complete'`

---

## Architecture Notes

**Why MG-7 is read-only:**
- Prevents accidental archival of partially processed meetings
- Ensures deterministic archival via dedicated MG-7C script
- Allows manual review before marking [C]

**Key invariants:**
- ✅ MG-7 lists and reports only
- ✅ MG-7C archives only on `_[C]` meetings
- ❌ Never move `_[P]` meetings directly
- ❌ Never rename without using the C-state workflow

---

## Next Steps

**For immediate archival candidates:**
Review the 8 meetings listed above. For each:
1. Verify follow-ups (MG-5) are complete
2. Run "Meeting Mark C-State" prompt
3. MG-7C will handle archival automatically

**Scheduled automation:**
- MG-7C runs at 04:00 and 16:00 ET daily
- Scans for `_[C]` meetings and archives to quarterly folders

