---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
tool: true
description: Semantically deduplicate meeting files using LLM understanding instead of regex. Analyzes filenames to identify duplicates and provides cleanup plan.
tags:
  - meetings
  - deduplication
  - cleanup
  - semantic-analysis
  - pipeline
---

# Meeting Deduplication Prompt

## Purpose
Use LLM semantic understanding to identify duplicate meeting files that regex-based approaches miss. Filenames may have variations in timestamp formatting, special characters, or suffixes but represent the same meeting.

## Context
Meeting files come from various sources (Granola, Fireflies, manual imports) and may have:
- Different timestamp formats: `.399Z`, `-399Z`, `_399Z`, `T19-48-05`, `T19_48_05`
- Different separators: dashes, underscores, spaces
- Suffix variations: `-transcript`, `_transcript`, none
- Prefixed markers: `[IMPORTED-TO-ZO]`
- Multiple file extensions: `.transcript.md`, `.md`

Regex fails because it can't understand semantic equivalence. You can.

## Task
Given a list of meeting filenames, identify duplicates and provide a cleanup plan.

### Input Format
Provide either:
1. A directory path to scan
2. A list of filenames

### Analysis Steps

1. **Parse Each Filename Semantically**
   - Extract meeting title/name
   - Extract date/timestamp
   - Identify source system markers
   - Note any special prefixes/suffixes

2. **Group by Meeting Identity**
   - Same meeting = same title + same date/timestamp (ignore format differences)
   - Example: All these are the SAME meeting:
     - `Acquisition_War_Room-transcript-2025-11-03T19-48-05.399Z.transcript.md`
     - `Acquisition_War_Room-transcript-2025-11-03T19-48-05-399Z.transcript.md`
     - `Acquisition_War_Room_2025-11-03T19-48-05.transcript.md`
     - `[IMPORTED-TO-ZO] Acquisition_War_Room-transcript-2025-11-03T19-48-05_399Z.transcript.md`

3. **Select Canonical Version**
   For each duplicate group, choose ONE file to keep based on:
   - **Preference order:**
     1. Shortest filename (least noise)
     2. Standard ISO timestamp format
     3. No special characters in timestamp
     4. Has `[IMPORTED-TO-ZO]` prefix (already processed)
     5. If tied, keep alphabetically first

4. **Generate Cleanup Plan**
   Output format:
   ```
   ## Meeting: [Title]
   Date: [Date]
   Duplicates Found: [count]
   
   **KEEP:** [canonical filename]
   
   **DELETE:**
   - [duplicate 1]
   - [duplicate 2]
   - [duplicate 3]
   
   ---
   ```

### Output Requirements

1. **Summary Stats**
   - Total files analyzed
   - Total unique meetings
   - Total duplicates found
   - Total files to delete

2. **Detailed Groupings**
   - One section per duplicate group
   - Clear KEEP vs DELETE designation
   - Rationale for canonical selection

3. **Executable Cleanup Script**
   - Generate Python script that:
     - Moves duplicates to Trash with timestamp
     - Logs all moves to file
     - Includes dry-run mode
     - Verifies canonical file exists before deleting duplicates

### Safety Checks

Before recommending deletions:
1. Verify all files in group have same content (if accessible)
2. Ensure canonical file is readable
3. Never delete if only one file exists
4. Flag suspicious cases (very different timestamps, different file sizes)

## Example Usage

```bash
# Scan Inbox directory
python3 /home/workspace/N5/scripts/deduplicate_meetings.py \
  --scan /home/workspace/Personal/Meetings/Inbox \
  --output /home/workspace/cleanup_plan.md \
  --dry-run
```

## Integration Points

This prompt should be used:
1. **Before batch processing** - Clean Inbox before queueing
2. **After Drive ingestion** - Dedupe newly downloaded files  
3. **On-demand** - Manual cleanup when duplicates suspected
4. **Scheduled** - Weekly cleanup task

## Success Criteria

- Zero false positives (never group different meetings)
- Catch all semantic duplicates (high recall)
- Preserve most canonical filename
- Generate safe, auditable cleanup scripts
- Complete in <30 seconds for typical Inbox (~50 files)

## Notes

- This is SEMANTIC deduplication - you understand context
- Timestamp format variations are MEANINGLESS differences
- Title normalization: underscores = dashes = spaces
- You can read file metadata if needed to verify
- When in doubt, flag for manual review (don't delete)
