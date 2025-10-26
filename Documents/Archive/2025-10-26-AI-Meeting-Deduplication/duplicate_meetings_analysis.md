# Duplicate Meeting Analysis - 2025-10-26

## Root Cause Identified

**Primary Issue:** Fireflies is uploading **multiple transcript versions** of the same meeting to Google Drive within 1-2 minutes, and the `meeting-transcript-scan` task (running every 30 minutes) is picking up all of them before any can be marked as processed.

## Evidence

### Example 1: Sam Partnership Discovery Call (2025-10-24)

**Three transcript files uploaded:**
1. `Careerspan <> Sam - Partnership Discovery Call-transcript-2025-10-24T17-32-41.785Z.docx` → gdrive_id: `1_kP2sbRDQP1bVvvoF-bPoVIFGjp-phCW`
2. `Careerspan <> Sam - Partnership Discovery Call-transcript-2025-10-24T17-33-30.497Z.docx` → gdrive_id: `19aLkFsaW2g1N9fUxdS_bZUz83jPDnG7d`
3. `Careerspan <> Sam - Partnership Discovery Call-transcript-2025-10-24T17-34-52.747Z.docx` → gdrive_id: `1_SSOZ7_pOgrDWb22fbw7I-VEqCSyBL9e`

**All created at:** 2025-10-24 19:44:58-59 UTC (scan task run)
**Time delta:** 48 seconds, 1 minute, 2 minutes from meeting end

**Result:** 3 separate meeting folders created:
- `2025-10-24_external-sam-partnership-discovery-call`
- `2025-10-24_external-sam-partnership-discovery-call_173330`
- `2025-10-24_external-sam-partnership-discovery-call_173452`

### Example 2: Alexis-Mishu Meeting (2025-10-24)

**Two transcript files uploaded:**
1. `Monthly- Vrijen - Alexis - Mishu-transcript-2025-10-24T14-34-35.642Z.docx` → gdrive_id: `15EGLPjluDOznHjsoaDFs3hgggvKM0dBG`
2. `Monthly- Vrijen - Alexis - Mishu-transcript-2025-10-24T14-37-53.429Z.docx` → gdrive_id: `1ZbsY9QYY208N2_NmDimmSXo54ff8RdBV`

**Both created at:** 2025-10-24 16:31:26 UTC (same scan)
**Time delta:** 3 minutes between transcripts

**Result:** 2 separate meeting folders created:
- `2025-10-24_external-alexis-mishu`
- `2025-10-24_external-alexis-mishu_143435`

## Why the Deduplication Logic Failed

The deduplication logic in `meeting-transcript-scan.md` checks for **existing gdrive_ids** in:
- `N5/inbox/meeting_requests/*.json`
- `N5/inbox/meeting_requests/completed/*.json`
- `N5/inbox/meeting_requests/processed/*.json`
- `N5/records/meetings/*/_metadata.json`

**But this fails when:**
- All transcript files from the same meeting appear in Google Drive **before any processing happens**
- Each has a **different gdrive_id** (Fireflies creates new files, not versions)
- The scan task sees them all at once and creates separate requests for each

## Current Scheduled Tasks Involved

### Task 1: 💾 Gdrive Meeting Pull
- **ID:** `afda82fa-7096-442a-9d65-24d831e3df4f`
- **Schedule:** Every 30 minutes
- **Action:** Executes `meeting-transcript-scan` command
- **Last updated:** 2025-10-11

### Task 2: 🧠 Meeting Transcript Processing and Analysis
- **ID:** `3bfd7d14-ffd6-4049-bd30-1bd20c0ac2ab`
- **Schedule:** Every 15 minutes
- **Action:** Processes ONE pending meeting transcript from queue
- **Last updated:** 2025-10-14

## Pattern Observed

The duplicates started appearing **around October 17, 2025** (based on file timestamps).

**Recent duplicates:**
- 2025-10-17: Laura Close (3 versions)
- 2025-10-24: Alexis-Mishu (2 versions)
- 2025-10-24: Sam Partnership Call (3 versions)
- 2025-10-24: Gabi Zo Demo (2 versions)
- 2025-10-15: Sam Partnership Sync (2 versions)
- 2025-10-15: Magic Edtech Panel (2 versions)

## Why This Happens with Fireflies

Fireflies appears to:
1. Generate initial transcript immediately after meeting ends
2. Generate improved/edited transcripts shortly after (speaker diarization, cleanup)
3. Upload each version as a **separate file** to Google Drive
4. All appear within 1-3 minutes of each other

## Recommended Solution

**Option 1: Add filename-based deduplication (Recommended)**
- Before checking gdrive_id, extract base meeting name from filename
- Check if ANY existing meeting has the same base name + date
- Skip if found, even with different gdrive_id

**Option 2: Add delay buffer**
- After detecting new transcripts, wait 5-10 minutes
- Re-scan to see if more versions appear
- Process only the **latest timestamp** version

**Option 3: Mark files in Google Drive immediately**
- Use Google Drive API to rename file with `[ZO-QUEUED]` prefix immediately upon detection
- This prevents re-detection on next scan
- Rename to `[ZO-PROCESSED]` after full processing

**Option 4: Combination approach**
- Implement Option 1 (filename matching) for safety
- Implement Option 3 (immediate marking) for real-time deduplication

## Immediate Actions Needed

1. Update `meeting-transcript-scan` command with enhanced deduplication
2. Add filename similarity matching (fuzzy match on title + date)
3. Optionally: Add immediate file renaming in Google Drive
4. Update scheduled task instruction with new deduplication requirements

## Cleanup Needed

Multiple duplicate meeting folders need to be consolidated or archived.
