# Meeting Duplication Issue - Root Cause Analysis

**Conversation:** con_SV4FJvpVsm8w9A9b  
**Date:** 2025-11-16  
**Issue:** Duplicate meetings appearing in both Inbox/ and processed location

---

## Problem Summary

Meetings are duplicated between:
- `/home/workspace/Personal/Meetings/Inbox/` (with `[M]` suffix)
- `/home/workspace/Personal/Meetings/` (processed location, no suffix)

**Example:**
- `Personal/Meetings/2025-11-03_Acquisition_War_Room/` (processed, Nov 15)
- `Personal/Meetings/Inbox/2025-11-03_Acquisition_War_Room_[M]/` (inbox, Nov 16)

---

## System Architecture Discovery

### Two Parallel Ingestion Systems

#### 1. **OLD SYSTEM** (Deprecated but still active)
**Entry Point:** Unknown manual/legacy scripts  
**Database:** `N5/data/meeting_pipeline.db`  
**Status Field:** `queued_for_ai`  
**File Location:** Saves raw `.transcript.md` files to `Personal/Meetings/Inbox/`  
**Example:** `Acquisition War Room-transcript-2025-11-03T19-48-05.399Z.transcript.md`

```sql
-- Old system database entry
meeting_id: "Acquisition War Room-transcript-2025-11-03T19-48-05.399Z"
transcript_path: "/home/workspace/Personal/Meetings/Inbox/Acquisition War Room-transcript-2025-11-03T19-48-05.399Z.transcript.md"
status: "queued_for_ai"
detected_at: "2025-11-04T19:46:44.423130"
```

**Problem:** This entry has status `queued_for_ai` but the transcript file no longer exists.

#### 2. **NEW SYSTEM** (Firefly Webhook - Yesterday's Setup)
**Entry Point:** Firefly webhook → `fireflies-webhook` service (port 8420)  
**Database:** Same `meeting_pipeline.db`, table `fireflies_webhooks`  
**Processing:** `TranscriptProcessor` fetches from Fireflies API  
**File Location:** Creates folder structure in `Personal/Meetings/Inbox/`  
**Folder Pattern:** `YYYY-MM-DD_participant-names_[M]` (note the `[M]` marker)  
**Contents:** `transcript.md` + `manifest.json`

```json
// Example Inbox/[M] folder
{
  "meeting_id": "2025-11-03_Acquisition_War_Room",
  "generated_at": "2025-11-16T14:16:19-05:00",
  "blocks": [ /* all status: "pending" */ ]
}
```

---

## The Duplication Flow

### Timeline: Acquisition War Room Meeting

1. **Nov 3:** Meeting occurs
2. **Nov 4 19:46:** OLD SYSTEM ingests, creates entry in database
   - Status: `queued_for_ai`
   - File: Raw `.transcript.md` file (now missing)
3. **Nov 15 23:08:** Meeting PROCESSED (blocks generated)
   - Location: `Personal/Meetings/2025-11-03_Acquisition_War_Room/`
   - Contains: 7 intelligence blocks (B01, B02, B05, B08, B21, B26, B27)
4. **Nov 16 14:16:** NEW SYSTEM (Firefly webhook) receives duplicate
   - Webhook received: `8dc1c922-b86c-4ba8-b8bd-590a9838459a`
   - Transcript fetched from Fireflies API
   - Creates: `Inbox/2025-11-03_Acquisition_War_Room_[M]/`
   - manifest.json shows all blocks as "pending"

---

## Root Causes Identified

### 1. **No Deduplication Logic**
The Firefly webhook system (`transcript_processor.py`) has ZERO duplicate detection:
- Doesn't check if meeting already exists
- Doesn't query database for existing meetings
- Doesn't check filesystem for duplicate folders

### 2. **No Connection Between Systems**
- Old system uses database field `status: queued_for_ai`
- New system uses separate `fireflies_webhooks` table
- No reconciliation between the two tracking systems

### 3. **Firefly Retransmission**
Firefly is retransmitting meetings that were already processed:
- Original ingestion: Nov 4 (via old system)
- Webhook received: Nov 16 (12 days later)
- This suggests Firefly webhook was configured AFTER meetings already occurred

### 4. **Missing Queue Processor**
The `[M]` suffix indicates "Marked for processing", but:
- No active service consuming these
- No scheduled task processing Inbox/[M] folders
- Meetings sit in Inbox indefinitely with "pending" status

---

## System Components Analysis

### Active Services (User Services)
- `fireflies-webhook` (port 8420): Receives webhooks ✅ ACTIVE
- `fireflies-poller` (port 8421): Polls for pending webhooks ✅ ACTIVE

### Missing/Inactive Services
- **Meeting Inbox Processor:** Should consume `[M]` folders and trigger AI processing
- **Deduplication Service:** Should prevent duplicate ingestion
- **Old System Cleanup:** Should mark old entries as obsolete

### Database Tables
```sql
meetings               -- Old system tracking
fireflies_webhooks     -- New webhook tracking
blocks                 -- Block generation tracking
meeting_metadata       -- GDrive metadata (separate system?)
duplicate_clusters     -- Duplicate detection (not actively used?)
```

---

## Why [M] Folders Exist

The `[M]` suffix appears to be a marker meaning "Manifest created, pending AI processing":
- Folder contains `transcript.md` + `manifest.json`
- manifest.json lists required blocks with status "pending"
- System expects something to process these and generate blocks

**But:** No service is currently watching for/processing these folders.

---

## Recommendations

### Immediate Fix (P0)
1. **Add deduplication to Firefly webhook processor**
   - Check database for existing meeting_id before creating folder
   - Check filesystem for existing meeting folder
   - Skip if already processed

2. **Activate or create Inbox processor service**
   - Watch for `Inbox/*_[M]/` folders
   - Generate intelligence blocks per manifest
   - Move to processed location when complete

3. **Clean up orphaned database entries**
   - Mark old `queued_for_ai` entries as obsolete if processed elsewhere
   - Reconcile between old and new tracking systems

### Medium-term (P1)
4. **Unify tracking systems**
   - Deprecate old `meetings` table structure
   - Use `fireflies_webhooks` as source of truth
   - Add migration path for existing data

5. **Implement duplicate detection service**
   - Use existing `duplicate_clusters` table
   - Active monitoring for duplicates
   - Automated reconciliation

### Long-term (P2)
6. **System documentation**
   - Document complete meeting ingestion flow
   - Clarify old vs new system responsibilities
   - Migration timeline for full cutover

---

## Files to Review

### Key Scripts
- `N5/services/fireflies_webhook/transcript_processor.py` - Add deduplication
- `N5/scripts/queue_all_inbox_meetings.py` - Understand old queue system
- `N5/scripts/meeting_pipeline/ai_queue_executor.py` - AI processing system

### Key Databases
- `N5/data/meeting_pipeline.db` - Meeting tracking
- Check for multiple databases or fragmented state

### Key Folders
- `Personal/Meetings/Inbox/` - Staging area
- `Personal/Meetings/` - Processed meetings
- `N5/inbox/ai_requests/` - AI command queue

---

## Questions for V

1. **Is the Firefly webhook replacing the old system completely?**
   - If yes: Need to deprecate old ingestion path
   - If no: Need to coordinate between them

2. **What should happen when webhook arrives for existing meeting?**
   - Skip entirely?
   - Update with new data?
   - Flag as duplicate for review?

3. **Should [M] folders be processed automatically?**
   - If yes: Need to activate/create service
   - If no: What's the manual workflow?

4. **Is there a scheduled task that should be processing these?**
   - Check `list_scheduled_tasks` for meeting-related agents

---

## Next Steps

**Waiting for V's direction on:**
1. Desired behavior for duplicates
2. Whether to auto-process [M] folders
3. Priority: Quick fix vs complete redesign

