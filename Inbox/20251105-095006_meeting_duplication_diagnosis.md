---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Meeting Duplication Diagnosis & Resolution

**Date:** 2025-11-05T03:08:14Z  
**Status:** ✅ BLEEDING STOPPED | System Stabilized

## Problem Summary
Meeting transcripts were duplicating in `/home/workspace/Personal/Meetings/Inbox` with multiple filename variations for the same meeting. The system generated 13 duplicates of "Acquisition_War_Room" alone.

### Root Cause
**Regex-based deduplication was failing** to catch filename variations:
- `Acquisition_War_Room-transcript-2025-11-03T19-48-05.399Z.transcript.md`
- `Acquisition_War_Room-transcript-2025-11-03T19-48-05-399Z.transcript.md` (dash instead of dot)
- `Acquisition_War_Room_2025-11-03T19-48-05.transcript.md` (no `-transcript-`)
- `[IMPORTED-TO-ZO] Acquisition_War_Room-transcript-2025-11-03T19-48-05_399Z.transcript.md`

The Huey queue workers were processing these "unique" filenames repeatedly because string matching couldn't understand they were semantically identical.

---

## Actions Taken

### 1. Stopped the Bleeding ✅
- **Killed Huey queue workers** (huey_consumer processes)
- **Deleted registered service** `meeting-huey-consumer` (svc__HconKDX8Q8)
- **Prevented new duplicates** from being created

### 2. Semantic Deduplication ✅
Created LLM-based deduplication system:

- **Prompt:** file 'Prompts/deduplicate-meetings.md' (tool: true)
- **Scanner:** file 'N5/scripts/deduplicate_meetings.py'
- **Executor:** file 'N5/scripts/execute_meeting_cleanup.py'

**Key Innovation:** Stop using regex patterns. Use LLM semantic understanding to identify:
- Same meeting title (underscores = dashes = spaces)
- Same timestamp (format variations are meaningless)
- Duplicate detection without brittle pattern matching

### 3. Cleanup Executed ✅
**Removed 56 duplicate files** from Inbox:
- Before: 282 files
- After: 226 files  
- Saved to: `/home/workspace/Personal/Meetings/Trash/DEDUP_CLEANUP_20251105T030814Z/`
- Log: `cleanup_log.jsonl` in trash folder

**Top Duplicate Groups:**
- Acquisition War Room: 13 → 1
- Daily team stand-up (Oct 29): 10 → 1
- Alex x Vrijen Wisdom Partners: 5 → 1
- Careerspan Sam Partnership: 5 → 1
- guz-dgac-fvk: 6 → 1
- dbn-ctum-szz: 5 → 1

---

## Current State

### System Status
✅ **Queue workers:** STOPPED  
✅ **Duplicates:** CLEANED (56 removed)  
✅ **Inbox:** 226 unique meetings  
✅ **Canonical files:** Preserved (e.g., `[IMPORTED-TO-ZO] Acquisition_War_Room_2025-11-03T19-48-05.transcript.md`)

### Semantic Normalization
The system already has `semantic_filename.py` with:
- `normalize_meeting_filename()` - Converts any variant to canonical form
- `get_meeting_id()` - Extracts unique identifier for deduplication

**However:** This normalization is NOT being applied consistently during Drive ingestion, leading to duplicate downloads.

---

## Remaining Work

### Integration Required
The LLM-based deduplication should be integrated into the pipeline:

1. **Pre-ingestion deduplication** - Run before queueing new Drive files
2. **Post-ingestion cleanup** - Run after batch downloads complete
3. **Scheduled maintenance** - Weekly cleanup task

### Drive Ingestion Fix
The file 'N5/scripts/meeting_pipeline/drive_ingestion.py' imports `semantic_filename` but may not be applying normalization before downloading. Need to ensure:

1. Check if normalized filename exists before download
2. Apply normalization immediately after download
3. Registry should use normalized meeting_id for tracking

### Monitoring
Create a health check that alerts when:
- Same meeting_id appears >1 time in Inbox
- Filename variations detected (regex vs semantic mismatch)
- Queue depth grows abnormally

---

## Files Created/Modified

### New Files
- file 'Prompts/deduplicate-meetings.md' - LLM deduplication prompt (tool)
- file 'N5/scripts/deduplicate_meetings.py' - Context preparation script
- file 'N5/scripts/execute_meeting_cleanup.py' - Cleanup executor
- file 'cleanup_plan.md' - Detailed analysis (workspace root)
- file 'meeting_duplication_diagnosis.md' - This document

### Existing Files Referenced
- file 'N5/scripts/meeting_pipeline/semantic_filename.py' - Normalization logic
- file 'N5/scripts/meeting_pipeline/drive_ingestion.py' - Drive download script
- file 'N5/prefs/ingestion/drive_meetings_v2.yaml' - Config

---

## Success Metrics

✅ **Immediate:** Bleeding stopped, 56 duplicates removed  
✅ **Short-term:** No new duplicates created (queue stopped)  
🔲 **Medium-term:** Integration into pipeline prevents future duplicates  
🔲 **Long-term:** Automated weekly deduplication + monitoring

---

## Key Learnings

### What Worked
1. **LLM semantic understanding** > regex pattern matching
2. **Stop the bleed first** - Kill processes before cleanup
3. **Dry-run validation** - Verify before executing destructive operations
4. **Audit logging** - Every move logged to JSONL

### Design Principle Applied
**"Use LLM intrinsic capabilities instead of regex"** - This is exactly the kind of task LLMs excel at:
- Understanding semantic equivalence
- Contextual grouping
- Format-agnostic comparison

The brittleness of regex for filename normalization is a perfect example of where AI adds real value.

---

## Next Steps

1. **Integrate deduplication into pipeline** - Add pre/post hooks
2. **Fix Drive ingestion** - Ensure semantic normalization before download
3. **Create monitoring** - Alert on duplicate detection
4. **Schedule maintenance** - Weekly cleanup task
5. **Document workflow** - Add to N5 operational playbooks

---

**Status:** System stabilized. Duplicates cleaned. Pipeline stopped. Ready for integration work.
