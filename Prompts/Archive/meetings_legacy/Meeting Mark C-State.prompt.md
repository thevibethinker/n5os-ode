---
tool: true
description: "Mark a processed meeting as C-state by renaming its Inbox folder, ready for MG-7C archive."
tags: [meetings, state, archive, automation]
created: 2025-11-23
last_edited: 2025-11-23
version: 1.0
mg_stage: MG-7C
status: canonical
role: helper
---

# Meeting Mark C-State

You are wiring into the N5 meeting pipeline to mark meetings as **C-state** (completed follow-ups, ready for archive).

## Behavior

When invoked, follow this behavior:

1. **Identify the target meeting**
   - The user will provide either:
     - A full meeting ID prefix (e.g. `2025-11-20_laurensalitangmailcom`), or
     - A clear reference to a specific meeting folder name.
   - Resolve ambiguity by asking the user to confirm the exact prefix if needed.

2. **Call the helper CLI**
   - Once the prefix is determined, call the Python helper:

   ```bash
   python3 /home/workspace/N5/scripts/meeting_pipeline/mark_meeting_c_state.py <prefix>
   ```

   Examples:

   ```bash
   python3 /home/workspace/N5/scripts/meeting_pipeline/mark_meeting_c_state.py 2025-11-20_laurensalitangmailcom
   ```

3. **Semantics and constraints**
   - Only operate on folders in `/home/workspace/Personal/Meetings/Inbox/`.
   - If the folder ends with `_[P]`, rename to `_[C]`.
   - If it already ends with `_[C]`, report that it is already in C-state.
   - If no matching folder is found or more than one match exists, report the error and ask the user to clarify.
   - Do **not** modify any files besides the folder name.

4. **Report back**
   - After the CLI completes, summarize:
     - Original folder name
     - New folder name (if changed)
     - Any warnings or errors from the script
   - Remind that MG-7C will archive C-state meetings on its next run (04:00 or 16:00 ET) or can be run manually via:

   ```bash
   python3 /home/workspace/N5/scripts/meeting_pipeline/archive_completed_meetings.py
   ```

Use this prompt whenever the user asks to mark a meeting as C-state, move a processed meeting into the "ready for archive" bucket, or explicitly mentions updating a meeting's suffix from `[P]` to `[C]`.

