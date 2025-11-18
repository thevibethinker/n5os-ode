---
created: 2025-11-05
last_edited: 2025-11-08
version: 1.1
tool: true
description: Download meeting transcripts from Google Drive, convert to markdown, apply semantic normalization, and register in the meeting system
tags:
  - meetings
  - drive
  - ingestion
  - automation
---
# Drive Meeting Ingestion

Process meeting transcripts from Google Drive queue download convert normalize and register.

## Workflow

1. Load config: Read Drive folder ID from file 'N5/config/drive_locations.yaml' (meetings.transcripts_inbox)
2. Check registry: Use file 'N5/scripts/meeting_registry_manager.py' to check processed files
3. For each item up to batch_size:
   - **DUPLICATE DETECTION**: Check if already processed
     * Run: python3 N5/scripts/meeting_registry_manager.py check --gdrive-id <file_id>
     * If exit code 0 (found): Skip with log message "Already processed: <filename>"
     * If exit code 1 (not found): Continue with download
   - Download from Drive using use_app_google_drive
   - Target folder ID from config file (canonical: 1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV)
   - Ignore any prefixes in the file name that indicate it has been processed
   - Convert to markdown if needed: pandoc -f docx -t markdown
   - **VALIDATE CONVERSION:** Check file size with stat -c%s. If 0 bytes:
     * Log error with filename
     * Mark in registry with failed flag
     * Send SMS notification about failed conversion
     * Skip remaining steps (do NOT move to Inbox)
     * Continue to next file
   - Apply semantic normalization: python3 N5/scripts/normalize_transcript.py
   - Write to Personal/Meetings/Inbox/
   - Update registry: python3 N5/scripts/meeting_registry_manager.py add --gdrive-id --meeting-id --folder-name <folder> --converted --conversion-method pandoc
   - Remove from queue (if queued)
4. Report results

## Tools

- file 'N5/config/drive_locations.yaml' - Canonical Drive folder IDs
- file 'N5/scripts/meeting_registry_manager.py' - Schema-validated registry ops
- file 'N5/scripts/normalize_transcript.py' - Speaker turn normalization
- file 'N5/schemas/meeting_gdrive_registry.schema.json' - Validation schema

## Email

vrijen@mycareerspan.com

