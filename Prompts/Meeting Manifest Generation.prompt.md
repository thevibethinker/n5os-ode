---
tool: true
description: "Scans Personal/Meetings/Inbox for unprocessed meeting folders (no _[M] or _[P] suffix), generates manifest.json, and transitions them to [M] state."
tags: [meetings, ingestion, manifest, automation]
created: 2025-11-22
version: 1.0
mg_stage: MG-1
status: canonical
---

# Meeting Manifest Generation Workflow [MG-1]

**Purpose:** Ingest raw meeting folders into the N5 meeting pipeline by validating contents, creating a manifest, and applying the `_[M]` suffix.

## Workflow

1.  **Scan for Unprocessed Meetings**
    *   Look in `/home/workspace/Personal/Meetings/Inbox/`.
    *   Identify folders that do **NOT** have `_[M]` or `_[P]` suffix.
    *   Ignore `_quarantine` or hidden files.

2.  **Process Each Folder**
    *   **Validation:** Check for `transcript.jsonl`.
        *   If `transcript.jsonl` exists: Proceed.
        *   If `transcript.md` or `transcript.txt` exists but no jsonl: Convert to `transcript.jsonl` (content: `{"text": "..."}`).
        *   If no transcript found: Log warning and skip (or move to `_quarantine`).
    *   **Generate Manifest:**
        *   Create `manifest.json` in the folder.
        *   Content:
            ```json
            {
              "manifest_version": "1.0",
              "generated_at": "{current_iso_timestamp}",
              "meeting_folder": "{folder_name}",
              "meeting_date": "{extract_from_name_or_today}",
              "status": "manifest_generated",
              "blocks_generated": {
                "stakeholder_intelligence": false,
                "brief": false,
                "transcript_processed": true
              },
              "last_updated_by": "MG-1_Prompt"
            }
            ```
    *   **Transition to [M] State:**
        *   **Renaming:** Rename the folder by appending `_[M]`.
        *   Command: `mv "Folder Name" "Folder Name_[M]"`
        *   **Safety Check:** Ensure "Folder Name_[M]" does not already exist. If it does, verify contents and merge or alert.

## Execution

Run this prompt to process all pending raw meetings.

**Example Command:**
```bash
# Find raw folders (exclude [M], [P], quarantine)
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -not -name "*_[M]" -not -name "*_[P]" -not -name "_quarantine" -not -name "Inbox"
```


