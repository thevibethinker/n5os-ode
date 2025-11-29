# Complete Meeting Processing Chain Diagnosis

**Date:** 2025-11-18 00:13 UTC  
**Status:** ✅ System Working As Designed

---

## Executive Summary

**Issues Found & Fixed:**
1. ✅ Duplicate folder creation (MG-1 bug) - **FIXED**
2. ✅ Malformed `_[M]]` suffix (bash escaping) - **FIXED**

**Working As Designed:**
3. ✅ [M] folders waiting for transition - **INTENTIONAL BEHAVIOR**

---

## Complete Processing Chain

### 1. Fireflies Webhook → Raw Folder
**Component:** `fireflies-webhook` service (port 8420)  
**Frequency:** Real-time (on webhook receive)  
**Action:** Creates raw folder with `transcript.jsonl` + `metadata.json`

**Status:** ✅ Working

---

### 2. Raw → [M]: Manifest Generation
**Task:** MG-1 (`3ae08209-5c17-405a-bdfd-bd997d38d649`)  
**Schedule:** 10x daily (hours 0,15-23)  
**Action:** 
- Scans for raw folders (no suffix, no manifest)
- Generates `manifest.json` with selected blocks
- Renames folder with `_[M]` suffix

**Bug Found:** Was creating NEW folders instead of renaming  
**Fix Applied:** Added explicit `mv "$folder" "${folder}_[M]"` command  
**Status:** ✅ FIXED

---

### 3. [M]: Block Generation
**Task:** MG-2 (`cd8d3155-b898-4c65-afc0-d867a2974ae7`)  
**Schedule:** Every 30 minutes  
**Action:**
- Finds [M] folders with `status="pending"` blocks
- Generates up to 4 blocks per run
- Updates manifest with `status="generated"`

**Status:** ✅ Working

---

### 4. [M] → [P]: Transition Check
**Task:** MG-6 (`7b4458d3-317c-4575-a2f1-5f4ab04d40b5`)  
**Schedule:** 4x daily (1, 13, 17, 21 UTC)  
**Action:**
- Scans [M] folders
- Checks if ALL blocks complete (pending_count == 0)
- Renames `_[M]` → `_[P]`

**Current Behavior:** 9 [M] folders with complete blocks awaiting next run  
**Status:** ✅ INTENTIONAL - Batches transitions 4x daily

---

### 5. [P]: Archive
**Task:** MG-7 (`a30a74ba-328d-40ff-b195-ea8e324f7237`)  
**Schedule:** 4x daily (1, 13, 17, 21 UTC)  
**Action:**
- Finds [P] folders in Inbox
- Moves to `/Personal/Meetings/Archive/YYYY-QX/`
- Strips suffix in archive (clean folder name)

**Status:** ✅ Working (22 meetings archived)

---

## Parallel Workflows

**MG-3: Blurbs** (every 30min)  
**MG-4: Warm Intros** (every 30min)  
**MG-5: Follow-up Emails** (every 30min)

These run on [M] folders as blocks complete.

---

## Bug #2: Malformed Suffix `_[M]]`

**Root Cause:** Unescaped brackets in bash parameter expansion  
**Location:** `Prompts/meeting-block-generator.prompt.md` line 206  
**Bug:** `new_folder="${folder%_[M]}_[P]"` (treats `[M]` as glob)  
**Fix:** `new_folder="${folder%_\[M\]}_[P]"` (escapes brackets)  
**Status:** ✅ FIXED

---

## Current System State

**Inbox:**
- 2 RAW folders (awaiting MG-1 next run)
- 9 [M] folders (awaiting MG-6 next run at 01:00 UTC)
- 0 [P] folders (all archived)
- 1 TEST folder (for validation)

**Archive:**
- 22 meetings properly archived

**Pipeline Health:** ✅ HEALTHY
- No duplicates
- No orphans
- No malformed suffixes
- Transitions working as designed

---

## Timing Design

**Why 4x daily for transitions?**
- Batches processing for efficiency
- Reduces race conditions
- Allows time for block generation to complete
- Prevents constant file system churn

**Expected wait times:**
- Raw → [M]: Max 1 hour (MG-1 runs hourly during active hours)
- [M] blocks complete → [P]: Max 6 hours (MG-6 runs 4x daily)
- [P] → Archive: Max 6 hours (MG-7 runs 4x daily)

---

## Validation Complete

✅ All bugs identified and fixed  
✅ System behavior understood and documented  
✅ No changes needed to intentional design  
✅ Next MG-6 run will process waiting [M] folders

