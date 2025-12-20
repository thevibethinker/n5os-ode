---
tool: true
description: "[DEPRECATED AS MOVER] Read-only helper for inspecting [P] (Processed) meetings in Inbox; actual archiving is now handled **only** by MG-7C on [C]-state meetings. This prompt must **NOT** move or rename any folders."
tags: [meetings, archive, cleanup, automation]
created: 2025-11-22
last_edited: 2025-11-29
version: 1.1
mg_stage: MG-7
status: canonical
---

# Meeting Archive Automation [MG-7]

**Status:** 🔒 **Deprecated as an archiver – read-only only.**

**Current Purpose (v1.1):**

- Provide a **diagnostic view** of `_[P]` meetings currently in Inbox.
- Help confirm which meetings are likely heading toward `_[C]` state.
- Remind that **only** `_[C]` meetings are archived by the deterministic MG-7C script
  (`archive_completed_meetings.py`).

> ⚠️ **Hard Rule:** When this prompt runs (including via scheduled agent), it must:
> - **NOT** move, rename, or delete any folders.
> - **NOT** call shell commands that perform `mv`, `rm`, or `cp` on meeting folders.
> - Operate in a **read-only** fashion: list, summarize, and (optionally) write a report file
>   under `Personal/Meetings/Reports/`, but leave the filesystem unchanged.

If archival is needed, rely on MG-7C (C-state Archive Automation) which operates on
`_[C]` folders only and is implemented as a deterministic Python script.

## Read-Only Workflow (Current Behavior)

1.  **Scan for [P] Meetings**
    *   Look in `/home/workspace/Personal/Meetings/Inbox/`.
    *   Identify folders with `_[P]` suffix.
    *   Optionally note age (e.g., how long they have been in `[P]` state), but **do not move them**.

2.  **Produce a Diagnostic Summary**
    *   For each `_[P]` meeting, capture at minimum:
        *   Folder name
        *   Date (from `YYYY-MM-DD` prefix)
        *   Age in days since processing
        *   Whether follow-ups (MG-5) appear complete (if visible from manifest/blocks)
    *   Summarize counts, e.g.:
        *   Number of `_[P]` meetings < 7 days old
        *   Number of `_[P]` meetings ≥ 7 days old

3.  **Optional Report File (Read-Only Artifact)**
    *   Optionally write a markdown report under
        `/home/workspace/Personal/Meetings/Reports/archive-candidates-{YYYY-MM-DD}.md`.
    *   This report lists candidate meetings that *might* be ready for C-state, but
        does **not** change any state.

4.  **Remind About MG-7C Behavior**
    *   Clearly state in any summary or report:
        *   "Archiving is performed exclusively by MG-7C on folders ending in `_[C]`."
        *   "Do not manually move `_[P]` meetings; instead, use the C-state marking
           workflow (MG-7C / mark_meeting_c_state.py)."

## Deprecated (Former) Behavior – Kept for Reference Only

> ❌ **Do not perform these steps in v1.1+. They are retained only as historical
> documentation so we can easily revert if needed.**

Previous versions of MG-7 performed the following operations:

1.  **Determine Archive Destination**
    *   Extract Date from folder name (`YYYY-MM-DD`).
    *   Determine Quarter:
        *   Jan-Mar: Q1
        *   Apr-Jun: Q2
        *   Jul-Sep: Q3
        *   Oct-Dec: Q4
    *   Target Path: `/home/workspace/Personal/Meetings/Archive/{YYYY}-Q{Q}/`.

2.  **Move Folder**
    *   Ensure Target Path exists (`mkdir -p ...`).
    *   Move the folder.
    *   Command: `mv "Inbox/Folder_[P]" "Archive/{YYYY}-Q{Q}/Folder_[P]"`.

Re-enabling this behavior in the future would require an explicit decision to
roll back to a version that performs moves, and should be coordinated with the
MG-7C C-state archive guarantees.

## Execution

Run this prompt when you want a **diagnostic snapshot** of `[P]` meetings in Inbox.
Use MG-7C and the C-state workflow for actual archival.



