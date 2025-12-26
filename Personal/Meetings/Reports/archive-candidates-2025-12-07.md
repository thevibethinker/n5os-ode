---
created: 2025-12-07
last_edited: 2025-12-07
version: 1.0
---

# Meeting Archive Automation [MG-7] — Diagnostic Report
**Date:** 2025-12-07 12:05 ET  
**Status:** Read-only analysis (v1.1)

---

## Executive Summary

This report provides a **diagnostic snapshot** of meetings currently in `_[P]` (Processed) state. As of this run, **no actual file moves occur** — MG-7 is now read-only. Archival is performed exclusively by **MG-7C** on meetings marked with `_[C]` (Complete) state.

---

## Current State Metrics

| Metric | Count |
|--------|-------|
| **Total `_[P]` meetings** | 159 |
| In Inbox (nested) | 4 |
| In main Personal/Meetings/ | 155 |
| < 7 days old (recent) | 4 |
| ≥ 7 days old (candidates) | 152 |

---

## Meetings in Inbox (Nested Under [M] Folders)

These are recent `_[P]` meetings found within Inbox `_[M]` parent folders. They are candidates for C-state marking:

1. **2025-12-04_alanmymelico_[P]** — 3 days old
2. **2025-12-04_logantheapplyai...dannytheapplyai_[P]** — 3 days old
3. **2025-12-04_mihirinvoicebutlerai_[P]** — 3 days old
4. **2025-12-03_alexcaveny...loganmycareerspancom_[P]** — 4 days old

**Recommendation:** If follow-ups (MG-5) for these meetings are complete, mark them as `_[C]` using the Meeting Mark C-State workflow.

---

## Archive Candidates (≥ 7 Days Old)

The following 152 `_[P]` meetings are 7+ days old. They should be reviewed for C-state marking and subsequent archival:

### August 2025 (3–5 months old)
- 2025-08-26_equals_product-demo-partnership-exploration_partnership_[P] — 103 days
- 2025-08-27_Amy-Quan-Vrijen_event-planning_[P] — 102 days
- 2025-08-28_David-Speigel_advisory_[P] — 101 days
- 2025-08-29_tim-he_careerspan-twill-partnership-exploration_partnership_[P] — 100 days (duplicated)
- 2025-09-02_David-Speigel_advisory_[P] — 96 days

### September 2025 (2–3 months old)
- Multiple daily standups, strategy meetings, and partnership discussions
- Ages range from 69–95 days old
- Notable: 2025-09-24_lensa_partnership-exploration-pilot_partnership_[P] — 74 days

### October 2025 (1–2 months old)
- 2025-10-14_nira-team_strategy-exploration_founder_[P] — 54 days
- 2025-10-30_Jake_Gates_and_Vrijen_Attawar_[P] — 38 days
- Multiple internal standups and networking meetings

### November 2025 (< 1 month old)
- 2025-11-17_Vrijen_Attawar_and_Paula_McMahon_[P] — 20 days
- 2025-11-24_* (Notion, team standups) — 12–13 days
- 2025-11-27_henrihumantruthsai...cerenhumantruthsai_[P] — 10 days

---

## Data Quality Notes

1. **Duplicates Detected:** Some meetings appear multiple times (e.g., 2025-08-29_tim-he, 2025-11-03_Acquisition_War_Room). May indicate:
   - Nested folders within folders
   - Backup/archive copies
   - Deduplication needed before archival

2. **Age Calculation:** Age is calculated from the `YYYY-MM-DD` prefix in folder names, assuming current date as 2025-12-07.

3. **Inbox Nesting:** The 4 nested `_[P]` meetings in Inbox are anomalies — typically, `_[P]` folders should not be inside `_[M]` parents. Consider review for correct filing.

---

## Next Steps (MG-7C Workflow)

To archive meetings:

1. **Review & Mark C-State**  
   Run `Meeting Mark C-State.prompt.md` for meetings ready for archival.
   - This renames folders from `_[P]` to `_[C]`.

2. **Automatic Archival**  
   MG-7C (`archive_completed_meetings.py`) automatically moves `_[C]` folders to:
   ```
   /home/workspace/Personal/Meetings/Archive/{YYYY}-Q{Q}/
   ```
   Where:
   - `{YYYY}` = year from folder name
   - `{Q}` = quarter (Q1=Jan–Mar, Q2=Apr–Jun, Q3=Jul–Sep, Q4=Oct–Dec)

3. **Archive Structure Example**
   - `2025-11-17_Vrijen_Attawar_and_Paula_McMahon_[C]` → `Archive/2025-Q4/`
   - `2025-08-26_equals_product-demo_[C]` → `Archive/2025-Q3/`

---

## Important Reminders

⚠️ **Hard Rule:** This prompt (MG-7) operates **read-only only**:
- ✅ **ALLOWED:** List, analyze, and report on `_[P]` meetings
- ❌ **NOT ALLOWED:** Move, rename, delete, or modify any files

**Archival is performed exclusively by MG-7C** on `_[C]` folders using a deterministic Python script.

Do not manually move `_[P]` meetings. Instead, use the C-state marking workflow:
1. Run `Meeting Mark C-State.prompt.md`
2. MG-7C handles the rest automatically

---

**Report generated:** 2025-12-07 12:05 ET  
**MG-7 Version:** 1.1 (Read-only)  
**MG-7C Status:** Archival automation ready

