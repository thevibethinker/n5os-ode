---
tool: true
description: "Moves [P] (Processed) meetings from Inbox to the permanent Archive organized by Year and Quarter."
tags: [meetings, archive, cleanup, automation]
created: 2025-11-22
version: 1.0
mg_stage: MG-7
status: canonical
---

# Meeting Archive Automation [MG-7]

**Purpose:** Move fully processed `_[P]` meetings out of Inbox into long-term storage.

## Workflow

1.  **Scan for [P] Meetings**
    *   Look in `/home/workspace/Personal/Meetings/Inbox/`.
    *   Identify folders with `_[P]` suffix.
    *   **Age Check:** Optional (e.g., archive immediately or wait 24h). Current policy: Archive immediately if [P].

2.  **Determine Archive Destination**
    *   Extract Date from folder name (`YYYY-MM-DD`).
    *   Determine Quarter:
        *   Jan-Mar: Q1
        *   Apr-Jun: Q2
        *   Jul-Sep: Q3
        *   Oct-Dec: Q4
    *   Target Path: `/home/workspace/Personal/Meetings/Archive/{YYYY}-Q{Q}/`

3.  **Move Folder**
    *   Ensure Target Path exists (`mkdir -p ...`).
    *   Move the folder.
    *   Command: `mv "Inbox/Folder_[P]" "Archive/{YYYY}-Q{Q}/Folder_[P]"`

## Execution

Run this prompt to clean up the Inbox.


