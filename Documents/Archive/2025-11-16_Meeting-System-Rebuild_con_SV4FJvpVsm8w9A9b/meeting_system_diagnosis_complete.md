# Meeting System Duplication - Complete Diagnosis

**Status:** ROOT CAUSE IDENTIFIED ✅  
**Date:** 2025-11-16 09:25 ET  
**Conversation:** con_SV4FJvpVsm8w9A9b

---

## The Problem

Meetings appearing in BOTH locations:
- `Personal/Meetings/{meeting_name}/` (processed, complete)
- `Personal/Meetings/Inbox/{meeting_name}_[M]/` (inbox, pending)

**Example:** Acquisition War Room meeting exists in both places

---

## Root Cause: THREE-PART SYSTEM COLLISION

### Part 1: Firefly Webhook (NEW - Added Nov 15)
**Service:** `fireflies-webhook` (port 8420)  
**What it does:**
- Receives webhook from Fireflies when transcription completes
- Fetches transcript via Fireflies API
- Creates folder in `Personal/Meetings/Inbox/` with format: `YYYY-MM-DD_name_[M]`
- Contains: `transcript.md` + `manifest.json` (blocks marked "pending")

**Problem:** NO DUPLICATE DETECTION
- Doesn't check if meeting already exists
- Doesn't query database
- Doesn't check filesystem
- Just blindly creates new folder

### Part 2: Old Meeting Pipeline (PRE-NOV 15)
**Database:** `N5/data/meeting_pipeline.db` table `meetings`  
**Status:** 125 meetings stuck in status `queued_for_ai` 
**What happened:**
- Old system ingested meetings (Nov 4 for Acquisition War Room)
- Set status to `queued_for_ai`
- Saved raw `.transcript.md` files to Inbox
- These were eventually processed → moved to `Personal/Meetings/`
- **But:** Database still shows `queued_for_ai` status (orphaned records)

### Part 3: Scheduled Tasks (Added Nov 16 - TODAY)
**Three agents running aggressively:**

1. **`🧠 Generate meeting intelligence manifest`** (Every 15 min)
   - Scans for folders WITHOUT `_[M]` suffix
   - Creates manifest.json
   - Renames folder to add `_[M]` suffix

2. **`Meeting Block Generation Process`** (Every 30 min)
   - Finds folders with `_[M]` suffix
   - Generates ONE block at a time
   - Updates manifest status to "complete" for that block
   - When all blocks done, renames to `_[P]` (processed)

3. **`Finalize Meeting Intelligence and Relocation`** (Every 60 min)
   - Finds folders with `_[P]` suffix
   - Moves to `Personal/Meetings/` (removes suffix)
   - Marks as complete

---

## Why Duplicates Happened

**Timeline:**
1. **Nov 3:** Meeting occurs
2. **Nov 4:** OLD system ingests, processes, moves to `Personal/Meetings/2025-11-03_Acquisition_War_Room/` ✅
3. **Nov 15:** Firefly webhook configured (you mentioned this was set up "yesterday")
4. **Nov 16 14:18:** Firefly RETRANSMITS webhook for old meeting
   - Firefly doesn't know this meeting was already processed
   - Webhook creates NEW folder: `Inbox/2025-11-03_Acquisition_War_Room_[M]/`
   - Now there are TWO copies of the meeting

**The scheduled tasks are working correctly!** They're doing their job processing the duplicate that Firefly created.

---

## Database Evidence

```sql
-- 188 total meetings in database
SELECT COUNT(*), status FROM meetings GROUP BY status;

12   complete       -- Successfully processed
1    detected       -- Just detected, not yet queued
50   failed         -- Processing failures
125  queued_for_ai  -- STUCK (old system orphans)
```

**That's 125 orphaned meetings** that were processed but never had their database status updated!

---

## Current State

**4 meetings in Inbox with [M] suffix:**
- `2025-10-23_Daily_team_stand-up_[M]`
- `2025-10-24_Monthly-Vrijen-Alexis-Mishu_[M]`
- `2025-11-03_Acquisition_War_Room_[M]` ← DUPLICATE
- `2025-11-03_Nafisa Poonawala and Vrijen Attawar_[M]`

These are being processed by the scheduled tasks right now (running every 15-30 min).

---

## What's Working

✅ **Firefly webhook** - Successfully receives and fetches transcripts  
✅ **Scheduled tasks** - Correctly process [M] folders → generate blocks → move to final location  
✅ **Block generation** - Produces quality intelligence blocks

---

## What's NOT Working

❌ **Firefly duplicate detection** - Retransmits old meetings  
❌ **Database reconciliation** - 125 orphaned `queued_for_ai` records  
❌ **System handoff** - Old vs new system not coordinated  
❌ **Firefly webhook timing** - Set up AFTER meetings already occurred, causing retransmission

---

## The Fix

### IMMEDIATE (P0) - Stop Further Duplicates

1. **Add duplicate detection to Firefly webhook**
   Edit: `N5/services/fireflies_webhook/transcript_processor.py`
   
   Before creating folder, check:
   ```python
   # Check filesystem
   existing = Path(f"/home/workspace/Personal/Meetings").glob(f"*{meeting_date}*{participant_names}*")
   if any(existing):
       logger.info(f"Meeting already exists, skipping: {meeting_id}")
       return None
   
   # Check database
   cursor.execute("SELECT meeting_id FROM meetings WHERE meeting_id LIKE ?", (f"%{meeting_id}%",))
   if cursor.fetchone():
       logger.info(f"Meeting in database, skipping: {meeting_id}")
       return None
   ```

2. **Clean up current duplicates**
   - Manually remove the 4 duplicate [M] folders from Inbox
   - OR: Let scheduled tasks finish processing them (they'll overwrite the originals)

### SHORT-TERM (P1) - Clean Database

3. **Reconcile orphaned database records**
   ```python
   # Mark orphans as complete if folder exists in Personal/Meetings
   for orphan in orphans_queued_for_ai:
       if folder_exists(orphan.meeting_id):
           update_status(orphan.meeting_id, "complete")
       elif folder_in_inbox(orphan.meeting_id):
           update_status(orphan.meeting_id, "processing")
       else:
           update_status(orphan.meeting_id, "failed", "No folder found")
   ```

### MEDIUM-TERM (P2) - Unify Systems

4. **Deprecate old meeting pipeline**
   - Remove old ingestion paths
   - Use Firefly webhook as single source of truth
   - Migrate remaining `queued_for_ai` meetings

5. **Add database tracking to scheduled tasks**
   - Update database when creating manifest
   - Update when generating blocks
   - Update when finalizing/relocating

---

## Firefly Configuration Issue

The webhook was configured AFTER meetings already occurred. Firefly's behavior:
- When webhook is first set up, it may retransmit recent meetings
- This caused it to send webhooks for meetings from Nov 3 (13 days ago)

**Solutions:**
1. **Ignore old meetings:** Add time filter (only process meetings from last 24-48 hours)
2. **Firefly dashboard:** Check if there's a "backfill" setting causing retransmission
3. **Webhook filtering:** Add timestamp check in webhook receiver

---

## Recommendations for V

### Option A: Quick Fix (Recommended)
1. Add duplicate detection to Firefly webhook (5 min fix)
2. Let scheduled tasks finish processing current 4 [M] folders
3. Monitor for next 24 hours

### Option B: Clean Slate
1. Stop Firefly webhook temporarily
2. Clean up all [M] folders manually
3. Reconcile database orphans
4. Add duplicate detection
5. Restart Firefly webhook

### Option C: Full Rebuild
1. Pause all meeting processing
2. Audit complete system state
3. Build unified meeting ingestion pipeline
4. Migrate historical data properly
5. Cut over to new system

---

## System Health

**Good news:**
- Scheduled tasks ARE working
- Block generation IS working
- Firefly webhook IS receiving data

**Bad news:**
- 125 orphaned database records
- Duplicate detection missing
- Old/new system not reconciled
- Firefly retransmitting old meetings

---

## Next Steps

**Waiting for V's decision:**
1. Which fix approach? (A, B, or C)
2. Should we pause scheduled tasks while fixing?
3. What to do with current 4 [M] folders? (let process or delete?)
4. Check Firefly dashboard for backfill settings?

---

## Files Needing Changes

### Must Fix
- `N5/services/fireflies_webhook/transcript_processor.py` - Add duplicate detection

### Should Fix
- Create script: `N5/scripts/meeting_pipeline/reconcile_database.py` - Fix orphans
- Create script: `N5/scripts/meeting_pipeline/cleanup_duplicates.py` - Manual cleanup

### Nice to Have
- `N5/services/fireflies_webhook/webhook_receiver.py` - Add timestamp filter
- Scheduled task instructions - Add database updates

