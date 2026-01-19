---
tool: true
description: "Scans Personal/Meetings/Inbox for unprocessed meeting folders (no _[M] or _[P] suffix), generates manifest.json, and transitions them to [M] state."
tags: [meetings, ingestion, manifest, automation]
created: 2025-11-22
version: 2.0
mg_stage: MG-1
status: canonical
last_edited: 2026-01-17
---

# Meeting Manifest Generation Workflow [MG-1]

**Purpose:** Ingest raw meeting folders into the N5 meeting pipeline by validating contents, creating a manifest, and applying the `_[M]` suffix.

## Workflow

1.  **Scan for Unprocessed Meetings**
    *   Look in `/home/workspace/Personal/Meetings/Inbox/`.
    *   Identify folders that do **NOT** have `_[M]` or `_[P]` suffix.
    *   Ignore `_quarantine` or hidden files.

2.  **Process Each Folder**

    ### ⛔ GUARD RAILS (Check BEFORE any processing)
    
    **SKIP and move to `_quarantine` if ANY of these are true:**
    
    1. **Test/Fake Name Detection:** Folder name contains (case-insensitive):
       - `Test`, `Sample`, `Simulated`, `Demo`, `Workflow`, `Raw-Meeting`, `Brand-New-Raw`, `Unprocessed`
       - Exception: Names like `therapy_test` or `product_demo_with_client` where the word is part of real meeting context are OK — use judgment
    
    2. **Stub Transcript Detection:** Combined transcript content is < 500 bytes
       - Real meetings have substantial content; stubs like `{"text": "This is a test"}` are ~50 bytes
    
    3. **Placeholder Content Detection:** Transcript contains ANY of these phrases:
       - "This is a test transcript"
       - "test transcript for MG"
       - "Meeting content here"
       - "Sample meeting content"
       - "Placeholder"
    
    **When quarantining:** Move to `_quarantine/{folder_name}_failed_guard_{reason}`
    
    ---

    *   **Validation:** Check for `transcript.jsonl`.
        *   If `transcript.jsonl` exists: Proceed.
        *   If `transcript.md` or `transcript.txt` exists but no jsonl: Convert to `transcript.jsonl` (content: `{"text": "..."}`).
        *   If no transcript found: Log warning and skip (or move to `_quarantine`).
    *   **Global Duplicate Check:**
        *   Before processing, check if this meeting already exists in any `Week-of-YYYY-MM-DD` folder under `/home/workspace/Personal/Meetings/`.
        *   Compare base folder names (ignoring case and common suffixes like `gmailcom`).
        *   If a duplicate is found in a Week-of folder:
            *   Log: "Meeting already exists in {Week-of-folder}. Moving to quarantine."
            *   Move the folder to `/home/workspace/Personal/Meetings/Inbox/_quarantine/{folder_name}_duplicate_already_archived`.
            *   Skip to next folder.
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
# Find raw folders in Inbox only (exclude [M], [P], quarantine)
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d \
  -not -name "*_[M]" \
  -not -name "*_[P]" \
  -not -name "_quarantine" \
  -not -name "Inbox"
```

---

## ➡️ Next Step (Optional)

After MG-1 completes, you may want to run **MG-2** to generate intelligence blocks:

> **Run next stage?** `@Meeting Block Generation`
>
> MG-2 generates intelligence blocks (B01-B35) from the transcript for each newly processed `_[M]` meeting.





