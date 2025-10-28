# Meeting Ingestion System - Root Cause & Fix

## Problem Identified

The meeting ingestion workflow has been broken since Oct 26, 2025 because:

1. **`meeting_transcript_scan.py` is hardcoded to use mock Google Drive data** (line 216)
2. The script never actually calls the Google Drive API
3. 5 new transcripts from Oct 27 are sitting unprocessed on Google Drive:
   - Gabi x Vrijen Onboarding
   - David x Careerspan
   - Lisa Noble x Vrijen
   - Ilya Meets Careerspan
   - Meet - kob-icsy-peo

## Evidence

```
$ cat /home/workspace/N5/records/Temporary/meeting_transcript_scan_run_20251026_000712.json
{
  "timestamp": "2025-10-26T00:07:12.254780+00:00",
  "drive_list_success": false,
  "error": "Google Drive integration unavailable: use_app_google_drive calls failing"
}
```

## The Fix

The scheduled task **"💾 Gdrive Meeting Pull"** needs to be completely rewritten to:

1. **Use the Google Drive API directly** via `use_app_google_drive` tool
2. List files from folder ID: `1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV`
3. Skip files with `[ZO-PROCESSED]` prefix
4. Download new transcripts
5. Create request JSONs
6. Mark completed meetings on Google Drive

The current Python script approach isn't working because it can't access `use_app_google_drive` (that's a Zo tool, not available in standalone Python scripts).

## Recommendation

**Rewrite the scheduled task instruction to do the work directly** (without calling the broken Python script), or **fix the Python script to actually call Google Drive APIs** using a method that works.
