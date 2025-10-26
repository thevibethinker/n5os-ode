# Google Drive Rename Strategy Implementation

**Date:** 2025-10-10  
**Status:** ✅ Implemented  
**Architecture Version:** 3.0

---

## 🎯 Summary

Implemented **Google Drive filename-based state tracking** for meeting transcript processing. Files are renamed after processing to prevent re-detection and provide visual confirmation.

---

## 🔄 What Changed

### **Before (v2.0):**
- Local state tracking (processed_meetings.jsonl)
- Risk of sync issues between local and cloud
- No visual confirmation in Google Drive

### **After (v3.0):**
- Google Drive filenames are source of truth
- Files with `[ZO-PROCESSED]` prefix = already processed
- Visual confirmation when browsing Drive
- Idempotent detection (safe to re-run)

---

## 📝 Updated Components

### 1. **Scheduled Task: Detection**
**Task ID:** `afda82fa-7096-442a-9d65-24d831e3df4f`  
**Name:** "Process New Meeting Transcripts in FULL Mode"

**New Behavior:**
```markdown
1. List files in Google Drive Transcripts folder
2. Filter OUT files starting with "[ZO-PROCESSED]"
3. Download only unprocessed transcripts
4. Create request files for processing
```

**Key Implementation:**
- Uses `use_app_google_drive` with `tool_name='google_drive-list-files'`
- Filters filenames client-side (skips `[ZO-PROCESSED]` prefix)
- Downloads only new transcripts

### 2. **Command: meeting-process**
**File:** `file 'N5/commands/meeting-process.md'`

**New Step Added (Step 8):**
```markdown
After successful processing, rename Google Drive file:
- Add [ZO-PROCESSED] prefix to original filename
- Uses: use_app_google_drive with tool_name='google_drive-update-file'
- Example: "Meeting.docx" → "[ZO-PROCESSED] Meeting.docx"
```

**Purpose:**
- Prevents re-detection on next scan
- Visual confirmation in Drive
- Single source of truth for state

### 3. **Documentation: meeting-processing-flow.md**
**File:** `file 'N5/docs/meeting-processing-flow.md'`

**Updates:**
- Version bumped to 3.0
- Core Principle updated to mention rename strategy
- Phase 2 processing includes rename step (step f)
- Last Updated: 2025-10-10

### 4. **New Command Documentation**
**File:** `file 'N5/commands/meeting-detect.md'`

**Created:** Full documentation for the detection command
- Explains rename strategy
- Details workflow steps
- Includes error handling
- Request file format documented

### 5. **Helper Script**
**File:** `file 'N5/scripts/gdrive_meeting_detector.py'`

**Created:** Python utility for filtering unprocessed files
- `parse_transcript_filename()` - extracts meeting metadata
- `filter_unprocessed()` - skips [ZO-PROCESSED] files
- `create_processing_request()` - generates request JSON

---

## 🎬 Naming Convention

### **Processed Files:**
```
[ZO-PROCESSED] Daily team stand-up-transcript-2025-10-03.docx
[ZO-PROCESSED] Logan x Vrijen Resync #2 - Oct 10.docx
[ZO-PROCESSED] Alex x Vrijen Chat[GRANOLA VERSION].docx
```

### **Unprocessed Files:**
```
Daily team stand-up-transcript-2025-10-10.docx
Ilse Midday Chat[GRANOLA VERSION].docx
spv-hmya-oeh-transcript-2025-10-10T17-51-00.314Z.docx
```

---

## 🔄 Complete Flow (v3.0)

### **Detection Phase (Every 30 min)**
```
1. Scan Google Drive → List all files
2. Filter → Skip files with [ZO-PROCESSED] prefix
3. Download → Unprocessed transcripts to N5/inbox/transcripts/
4. Classify → Determine stakeholder type
5. Queue → Create request files in N5/inbox/meeting_requests/
```

### **Processing Phase (Every 10 min)**
```
1. List pending requests → N5/inbox/meeting_requests/*.json
2. Select oldest → FIFO order maintained
3. Process → Extract intelligence blocks (ONE transcript)
4. Save → Blocks to N5/records/meetings/{meeting-id}/
5. Mark done → Move request to processed/
6. Rename → Add [ZO-PROCESSED] prefix in Google Drive ⭐ NEW
7. Stop → Next run processes next transcript
```

---

## ✅ Benefits

1. **Single Source of Truth**
   - Google Drive folder shows processing state
   - No need for local log files

2. **Visual Confirmation**
   - See at a glance what's been processed
   - Easy to verify system status

3. **Idempotent**
   - Safe to re-run detection
   - Won't duplicate processing

4. **Crash-Safe**
   - Rename happens AFTER processing succeeds
   - If processing fails, file stays unprocessed

5. **No Sync Issues**
   - Don't need to maintain local state
   - Cloud is authoritative

---

## 🧪 Testing Strategy

### **Test 1: First Detection Run**
**Scenario:** 98 old transcripts + 2 new transcripts  
**Expected:**
- Assumes 98 older ones are processed (per your instruction)
- Detects 2 most recent as unprocessed
- Downloads and queues 2 requests

### **Test 2: Rename After Processing**
**Scenario:** Process one transcript successfully  
**Expected:**
- Blocks saved to N5/records/meetings/
- Request moved to processed/
- Google Drive file renamed with [ZO-PROCESSED] prefix

### **Test 3: Re-Detection After Rename**
**Scenario:** Run detection again after processing  
**Expected:**
- Previously processed file is skipped (has [ZO-PROCESSED])
- Only truly new files are detected
- No duplicate processing

### **Test 4: Error Handling**
**Scenario:** Rename fails (network issue)  
**Expected:**
- Processing still completes locally
- Warning logged
- File can be manually renamed later
- Detection might re-detect it (handled by checking local records)

---

## 📊 State Tracking Comparison

| Aspect | Old (v2.0) | New (v3.0) |
|--------|-----------|-----------|
| Source of truth | Local JSONL | Google Drive filename |
| Visual confirmation | No | Yes (in Drive) |
| Sync risk | Yes | No |
| Idempotent | Requires careful log management | Yes (automatic) |
| Recovery | Manual log editing | Re-run detection |
| Human readable | No (need to open log) | Yes (browse Drive) |

---

## 🚀 Next Steps

### **Immediate (Next Run):**
1. Detection task runs in ~14 minutes (next scheduled)
2. Will scan Drive with new rename-aware logic
3. Should detect 2 most recent transcripts (if unprocessed)
4. Create request files

### **After First Processing:**
1. Processing task runs every 10 minutes
2. Processes oldest queued transcript
3. Renames in Google Drive with [ZO-PROCESSED] prefix
4. Next detection run will skip renamed file

### **Verification:**
1. Check Google Drive folder after processing
2. Verify files have [ZO-PROCESSED] prefix
3. Confirm next detection doesn't re-queue them

---

## 📚 Related Documentation

- `file 'N5/docs/meeting-processing-flow.md'` - Complete workflow (v3.0)
- `file 'N5/commands/meeting-process.md'` - Processing command with rename step
- `file 'N5/commands/meeting-detect.md'` - Detection command documentation
- `file 'N5/scripts/gdrive_meeting_detector.py'` - Helper utilities

---

## 🎉 Implementation Complete

**Architecture Version:** 3.0 (Google Drive Rename State Tracking)  
**Status:** ✅ Ready for next scheduled run  
**Next Detection:** ~14 minutes (00:14:51 UTC)  
**Next Processing:** ~4 minutes (23:54:19 UTC)

---

**Implemented:** 2025-10-10T23:56:00Z  
**Tested:** Pending (will verify on next run)  
**Documented:** ✅ Complete
