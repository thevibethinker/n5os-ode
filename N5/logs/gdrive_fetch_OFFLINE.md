---
created: 2025-11-04
status: OFFLINE
priority: HIGH
---

# Google Drive Fetch - OFFLINE FOR REPAIR

## Status
**Google Drive meeting fetch is OFFLINE** as of 2025-11-04 14:45 EST

## Problem
Google Drive download process was fetching **Word documents (.docx)** and renaming them to `.transcript.md` **without converting to text**. This created 147 corrupted "transcripts" that were actually ZIP archives.

## What Happened
1. Scheduled task fetched files from Google Drive folder `1J...`
2. Files downloaded as binary Word docs
3. Files renamed with `.transcript.md` extension
4. Database marked them as ready to process
5. AI processor failed when trying to read binary data

## Files Affected
- 147 corrupted files deleted from `/home/workspace/Personal/Meetings/Inbox/`
- Files had underscores in names (e.g., `Acquisition_War_Room-transcript...`)
- Valid files (with spaces) remained intact

## Paused Tasks
- Task ID: `8b833bb3-6c45-4a1a-afa9-900831c77bc5` - "Meeting Pipeline - Detection & Queueing" (created Nov 3)
- Task ID: `414fe0e2-e7ce-40fa-b46e-ae5644772177` - "Meeting Transcripts Processing" (created Nov 4 - DUPLICATE)

## Root Cause: Duplicate Tasks
**Task 2 was created TODAY** (2025-11-04 13:09:33), likely as a fix attempt. This created:
- **Race conditions**: Both tasks downloading same files simultaneously
- **Duplicate downloads**: Same file fetched multiple times with naming variations
- **Database conflicts**: Both inserting same meeting_id

This explains the filename encoding variations (`-` vs `.` vs `_` in timestamps) - files were downloaded 48+ times in 24 hours by competing tasks.

**When re-enabling: Create ONE task only, not two.**

## Repair Needed
1. **Fix download logic**: Use Google Drive export/convert API to get text, not binary
2. **Add validation**: Check file type before adding to queue
3. **Test with 1 file**: Verify text extraction works
4. **Re-enable tasks**: Only after validation passes

## Current State
- **233 valid transcripts** queued for processing (local files)
- **10 meetings** already processed and complete
- **Processing continues** with local files (unaffected by Drive issues)

## Scripts to Fix
- `/home/workspace/N5/scripts/meeting_pipeline/gdrive_fetcher_v2.py.BROKEN` (already marked broken)
- Scheduled task instruction for task `8b833bb3...` needs rewrite

## Next Steps
1. V decides: Should we implement proper text extraction or use a different source?
2. Test extraction with 1 file before re-enabling
3. Add file type validation to prevent this again
