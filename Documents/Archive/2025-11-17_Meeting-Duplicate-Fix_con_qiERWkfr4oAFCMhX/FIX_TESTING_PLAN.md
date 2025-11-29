# MG-1 Duplicate Folder Fix - Testing Plan

**Task:** `3ae08209-5c17-405a-bdfd-bd997d38d649`  
**Fix Applied:** 2025-11-17 23:43 UTC  
**Fix:** Added explicit `mv "$folder" "${folder}_[M]"` bash command to STEP 7

---

## Pre-Fix State

**Problem:** MG-1 was creating NEW folders with `_[M]` suffix instead of renaming, leaving original folders intact, causing duplicates on every run.

**Evidence:**
- `2025-11-17_daveyunghansgmailcom` (raw, created 21:32)
- `2025-11-17_daveyunghansgmailcom_[M]` (duplicate, created 23:00)
- Similar for ilse, Whitney, tiff, logan meetings

**Root Cause:** STEP 7 said "Rename folder" but provided NO bash command. AI interpreted this and created new folders instead of `mv` renaming.

---

## Fix Applied

**STEP 7 - Before:**
```
## STEP 7: Rename Folder with Suffix

Rename folder to add `_[M]` suffix:
- Before: `2025-11-16_Title/`
- After: `2025-11-16_Title_[M]/`

This signals manifest generation complete (visual debugging marker).
```

**STEP 7 - After:**
```
## STEP 7: Rename Folder with Suffix

**Execute this bash command to atomically rename the folder:**

\`\`\`bash
mv "$folder" "${folder}_[M]"
\`\`\`

This operation:
- Renames the folder in-place (no copy)
- Adds `_[M]` suffix to signal manifest generation complete
- Prevents duplicate processing (visual debugging marker)
- Is atomic and safe (folder either renamed or operation fails)

**Verification:** After rename, the folder path should end with `_[M]`
```

---

## Test Plan

### Test 1: Manual Verification (Immediate)
✅ Test folder created: `2025-11-17_TEST_Meeting_Fix_Verification`
- Contains: `transcript.md`, `metadata.json`
- No `manifest.json` (raw state)

**Expected:** Next MG-1 run should:
1. Find test folder
2. Generate manifest.json
3. RENAME (not copy) folder to `2025-11-17_TEST_Meeting_Fix_Verification_[M]`
4. Original folder should NOT exist anymore

### Test 2: Monitor Next Scheduled Run
**Next run:** 2025-11-18 00:00:02 UTC (7:00 PM ET today)

**Monitor:**
- Check if raw folders get renamed (not duplicated)
- Verify original folders disappear
- Count folders before/after

### Test 3: Check No Regressions
- Verify [M] folders can still be processed by downstream tasks (MG-2, MG-5, etc.)
- Verify archive task still works with [P] folders
- Check no path issues with new naming

---

## Current State Snapshot (Pre-Test)

**Raw folders (5 total):**
1. `2025-11-17_ilsetheapplyairochelmycareerspancom...`
2. `2025-11-17_daveyunghansgmailcom`
3. `2025-11-17_tiffsubstraterunattawarvgmailcom...`
4. `2025-11-17_logantheapplyaiilsetheapplyaidanny...`
5. `2025-11-17_TEST_Meeting_Fix_Verification` (test)

**Existing [M] folders:**
- `2025-11-17_daveyunghansgmailcom_[M]` (should not get another duplicate)
- `2025-11-17_ilse..._[M]` (should not get another duplicate)

---

## Success Criteria

### ✅ Primary Success:
- Test folder renamed to `..._[M]` (NOT copied)
- Original test folder NO LONGER EXISTS
- manifest.json created in renamed folder

### ✅ Secondary Success:
- No new duplicates created for existing raw folders
- All 5 raw folders either renamed OR skipped (if missing transcript)
- Zero new `_[M]` folders created alongside existing raw folders

### ✅ Tertiary Success:
- Downstream tasks (MG-2, MG-5) continue working
- No errors in logs
- No orphaned files

---

## Cleanup Actions (After Testing)

1. Remove test folder (after verification)
2. Clean up old duplicate folders:
   - Keep most recent [M] or [P] version
   - Remove raw folders that have [M] duplicates
3. Verify archive contains only final versions

---

## Rollback Plan

If fix causes issues:
1. Revert task instruction to previous version
2. Manually clean up any broken state
3. Investigate why explicit `mv` didn't work
4. Consider alternative approach (use prompt file instead of inline logic)

