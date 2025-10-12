# Meeting Transcript Scan

## Purpose
Scan Google Drive for NEW meeting transcripts, download them, classify stakeholders, and create processing requests with proper deduplication.

## Naming Convention
- **Internal meetings**: `YYYY-MM-DD_internal-team`
- **External meetings**: `YYYY-MM-DD_external-{name/org}`

Examples:
- `2025-10-10_internal-team` (Daily team stand-up)
- `2025-10-09_external-alex-wisdom-partners` (Alex x Vrijen coaching)
- `2025-09-23_external-stephanie` (Stephanie x Vrijen)

## State Tracking Strategy
Files WITH `[ZO-PROCESSED]` prefix = already processed (skip)
Files WITHOUT `[ZO-PROCESSED]` prefix = new/unprocessed (download & queue)

## Workflow

### 1. List Files from Google Drive
- Folder: `Fireflies/Transcripts` (ID: `1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV`)
- Tool: `use_app_google_drive` with `google_drive-list-files`
- Fields: `files(id,name,mimeType,modifiedTime,webViewLink)`
- Filter: `trashed=false`

### 2. Filter for Unprocessed Transcripts
- **Skip**: Any filename starting with `[ZO-PROCESSED]`
- **Keep**: Files containing "transcript" OR ending in `.docx`

### 3. Check for Duplicates (CRITICAL)
Before processing ANY file, check if it already exists:

#### a. Load Existing gdrive_ids
Scan these locations for existing `gdrive_id` values:
- `N5/inbox/meeting_requests/*.json`
- `N5/inbox/meeting_requests/completed/*.json`
- `N5/inbox/meeting_requests/processed/*.json`
- `N5/records/meetings/*/_metadata.json`

#### b. Skip Already Queued/Processed
If `gdrive_id` exists in any of above locations, **SKIP** the file entirely.

### 4. Process Each New File

For EACH unprocessed file NOT in existing queue:

#### a. Download to Transcript Directory
- Path: `N5/inbox/transcripts/{meeting-id}.txt`
- Tool: `use_app_google_drive` with `google_drive-download-file`
- Convert: Use `pandoc` to convert `.docx` to plain text

#### b. Parse Filename
Extract:
- **Date**: `YYYY-MM-DD` from timestamp in filename
- **Participants**: Parse from filename before "-transcript-"
- **Time**: `HH:MM:SS` (optional, for disambiguation)

#### c. Classify Stakeholder Type

**Internal Meeting if ANY:**
- Filename contains: "daily team stand-up", "co-founder", "extended cof", "bi-weekly extended"
- Transcript emails only contain: `@mycareerspan.com`, `@theapply.ai`

**External Meeting otherwise**

**Extract External Participant:**
- Remove: "x Vrijen", "and Vrijen Attawar", "+ Logan Currie"
- Remove: "transcript", "-transcript-"
- Slugify: Convert to lowercase, replace spaces/special chars with `-`
- Example: "Alex x Vrijen - Wisdom Partners Coaching" → "alex-wisdom-partners-coaching"

#### d. Generate Meeting ID

**Format:**
- Internal: `{date}_internal-team`
- External: `{date}_external-{participant-slug}`

**Handle Multiple Meetings on Same Day:**
- If meeting_id already exists in queue, append time: `{base-id}_{HHMMSS}`
- Example: `2025-09-22_external-giovanna-ventola_164313`

#### e. Create Request File

Path: `N5/inbox/meeting_requests/{meeting_id}_request.json`

```json
{
  "meeting_id": "YYYY-MM-DD_internal-team",
  "classification": "internal",
  "participants": "Daily team stand-up",
  "date": "YYYY-MM-DD",
  "gdrive_id": "1abc...",
  "gdrive_link": "https://docs.google.com/...",
  "original_filename": "...-transcript-....docx",
  "created_at": "2025-10-11T03:45:00.000000Z",
  "status": "pending"
}
```

For external meetings, add:
```json
{
  "external_participant": "alex-wisdom-partners-coaching"
}
```

### 5. Report Results
```
✅ Detected {N} new transcripts | 📥 Downloaded {N} files | 📋 Queued {N} requests | ⏭️ Skipped {N} duplicates
```

## Error Handling
- If download fails: Log error, continue with others
- If all files already processed: Exit gracefully with "No new transcripts to process"
- If classification uncertain: Default to `external-unknown`

## CRITICAL NOTES
1. **Do NOT rename files** - that happens AFTER processing via `meeting-process`
2. **This only DETECTS and DOWNLOADS** - processing happens separately
3. **Always check for duplicates** before creating new requests
4. **Use consistent naming** per convention above

## Dependencies
- Google Drive API access
- `pandoc` for document conversion
- Existing queue/processed meeting tracking

## Related Commands
- `meeting-process` - Process pending requests
- `meeting-request-standardizer` - Standardize existing queue
