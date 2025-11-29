---
tool: true
description: "Transitions meetings from [M] (Manifest) state to [P] (Processed) state when all required intelligence blocks and artifacts are complete."
tags: [meetings, transition, automation, state-machine]
created: 2025-11-22
version: 1.0
mg_stage: MG-6
status: canonical
---

# Meeting State Transition [MG-6]

**Purpose:** Promote meetings from `_[M]` to `_[P]` when processing is complete.

## Workflow

1.  **Scan for [M] Meetings**
    *   Look in `/home/workspace/Personal/Meetings/Inbox/`.
    *   Identify folders with `_[M]` suffix.

2.  **Check Completion Criteria**
    *   Read `manifest.json` in the folder.
    *   **Required Blocks:**
        *   `blocks_generated.stakeholder_intelligence` == true (or B01/B08 exist)
        *   `blocks_generated.brief` == true (or B02/Brief exist)
    *   **Required Artifacts:**
        *   `FOLLOW_UP_EMAIL.md` (if applicable/requested)
        *   `metadata.json` (should exist)

3.  **Transition to [P] State**
    *   If criteria met:
        *   Update `manifest.json`: Set `"status": "processed"`, `"last_updated_by": "MG-6_Prompt"`.
        *   **Renaming:** Rename folder from `..._[M]` to `..._[P]`.
        *   Command: `mv "Folder_[M]" "Folder_[P]"`
    *   If criteria NOT met:
        *   Skip.

## Execution

Run this prompt to check and transition eligible meetings.


