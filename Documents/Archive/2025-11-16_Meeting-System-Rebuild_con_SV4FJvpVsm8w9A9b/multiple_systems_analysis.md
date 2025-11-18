# Meeting System Architecture - Multiple Systems Detected

**Status:** TWO PARALLEL SYSTEMS CONFIRMED ✅  
**Date:** 2025-11-16 09:28 ET  
**Conversation:** con_SV4FJvpVsm8w9A9b

---

## SYSTEM #1: JSONL Registry (Old/Legacy?)
**Database:** `N5/data/meeting_gdrive_registry.jsonl`  
**Manager:** `N5/scripts/meeting_registry_manager.py`  
**Type:** JSONL (line-delimited JSON)  
**Purpose:** Google Drive-based meeting ingestion registry

### Usage
- Tracks meetings imported from Google Drive
- Uses JSONL format (not SQLite)
- References schema: `N5/schemas/meeting_gdrive_registry.schema.json`
- Transaction log: `N5/data/meeting_registry_txlog.jsonl`

---

## SYSTEM #2: Meeting Pipeline (New/Active)
**Database:** `N5/data/meeting_pipeline.db` (216KB SQLite)  
**Related:** `N5/data/fireflies_webhooks.db` (20KB SQLite)  
**Folder:** `N5/scripts/meeting_pipeline/` (40+ scripts)  
**Purpose:** Modern meeting processing pipeline with Fireflies webhook integration

### Tables
```sql
meetings (188 total)
  - 12 complete
  - 1 detected
  - 50 failed  
  - 125 queued_for_ai ⚠️

blocks
feedback
meeting_metadata
duplicate_clusters
duplicate_members
duplicate_check_queue
fireflies_webhooks
```

### Key Scripts
- `ai_queue_executor.py` - Processes AI queue
- `queue_manager.py` - Manages processing queue
- `request_manager.py` - Creates/manages requests
- `health_scanner.py` - System health checks
- `duplicate_detector.py` - Detects duplicates
- `standardize_meeting.py` - Standardizes output
- `response_handler.py` - Handles AI responses

---

## SYSTEM #3: Empty Database
**Database:** `N5/data/meeting_registry.db` (0 bytes - empty!)  
**Status:** UNUSED OR ABANDONED  
**Note:** Referenced by `meeting_registry.py` init method but never populated

---

## The Duplication Issue

### Root Cause Chain
1. **Fireflies webhook** delivers meeting → `Personal/Meetings/Inbox/[raw transcript]`
2. **Fireflies transcript_processor.py** processes → Creates folder with `[M]` suffix in Inbox
3. **meeting_pipeline.db** adds entry with status `queued_for_ai`
4. **SEPARATELY:** Some other process (possibly manual or older system) processes meeting → `Personal/Meetings/{final_location}/`
5. **Result:** Meeting exists in BOTH locations:
   - `Personal/Meetings/Inbox/{name}_[M]/` (pending, with manifest)
   - `Personal/Meetings/{name}/` (complete, with blocks)

### Current State
**Acquisition War Room example:**
- `meeting_pipeline.db`: `queued_for_ai` status (never completed)
- `Inbox/2025-11-03_Acquisition_War_Room_[M]/`: Has manifest.json, status "pending"
- `2025-11-03_Acquisition_War_Room/`: Fully processed with 8 blocks
- **These are NOT linked in the database**

### The 125 Orphans
125 meetings with `queued_for_ai` status means:
- 125 meetings are registered in pipeline DB
- Likely already processed through OTHER means
- Database was never updated when processing completed
- Inbox folders may or may not still exist

---

## Questions for V

1. **Which system should be authoritative?**
   - JSONL registry (`meeting_gdrive_registry.jsonl`)?
   - Pipeline DB (`meeting_pipeline.db`)?
   - Both?

2. **What's the intended workflow?**
   - Fireflies webhook → Inbox → Pipeline processes → Final location?
   - Manual processing bypassing pipeline?
   - Scheduled tasks that don't update database?

3. **The `[M]` suffix folders - who should consume them?**
   - Should pipeline AI processor auto-process these?
   - Should scheduled task monitor and process?
   - Are they meant for manual review first?

4. **The 125 orphaned `queued_for_ai` records:**
   - Should we reconcile these against filesystem?
   - Mark as `complete` if processed elsewhere?
   - Or investigate why pipeline didn't process them?

---

## Immediate Action Options

### Option A: Quick Cleanup (Conservative)
1. Reconcile orphaned database records against filesystem
2. Update status for meetings that ARE processed
3. Leave systems as-is but synchronized

### Option B: Pipeline Activation (Aggressive)  
1. Activate AI queue executor to process pending [M] folders
2. Set up scheduled task to monitor Inbox
3. Make pipeline the single source of truth

### Option C: Investigation First (Recommended)
1. Trace one meeting end-to-end through both systems
2. Identify which scripts/tasks are actually running
3. Map complete workflow before making changes

---

**Next:** Waiting for V's direction on which approach and which system is authoritative.

