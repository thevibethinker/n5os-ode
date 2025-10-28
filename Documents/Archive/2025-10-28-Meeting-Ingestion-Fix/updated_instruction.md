# Updated Instruction for "💾 Gdrive Meeting Pull"

Execute the meeting transcript scan with AI-powered deduplication, then mark processed transcripts on Google Drive.

**STEP 1: Check for any pending LLM requests**
Run: `python3 /home/workspace/N5/scripts/helpers/llm_request_handler.py`

If pending requests exist, handle them first before continuing.

**STEP 2: Run deduplication scan**
Execute: `python3 /home/workspace/N5/scripts/meeting_ai_deduplicator.py`

This script:
- Scans Google Drive for new meeting transcripts
- Deduplicates based on gdrive_id (using JSONL state file)
- Downloads transcripts to N5/inbox/transcripts/
- Creates request JSONs in N5/inbox/meeting_requests/processed/
- Logs results to /home/workspace/N5/inbox/meeting_requests/processing.log

**STEP 3: Mark successfully processed meetings on Google Drive**
Run: `python3 /home/workspace/N5/scripts/gdrive_processed_marker.py`

This identifies meetings that have been fully processed but whose Google Drive files haven't been renamed yet.

For each meeting found, use Google Drive API to rename the file with [ZO-PROCESSED] prefix:
- Read output from: `/tmp/gdrive_marking_needed.json`
- For each meeting with `gdrive_id`, call use_app_google_drive with tool_name='google_drive-update-file'
- Set configured_props: `{"fileId": "<gdrive_id>", "updateMask": "name", "requestBody": {"name": "[ZO-PROCESSED] <original_filename>"}}`
- Log successful renames

**Success Criteria:**
- Deduplication scan completes without errors
- New transcripts downloaded (if any)
- All completed meetings marked on Google Drive (if any)
- Logs updated with scan results

**Error Handling:**
- If Step 1 fails: Skip to Step 2 (LLM handler is optional)
- If Step 2 fails: Log error, do not proceed to Step 3
- If Step 3 fails: Log warning (non-critical, will retry next run)
