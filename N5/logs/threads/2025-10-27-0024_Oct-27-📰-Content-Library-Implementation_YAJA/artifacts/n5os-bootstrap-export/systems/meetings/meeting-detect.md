# Meeting Detection Command

**Purpose:** Scan Google Drive for new meeting transcripts and queue them for processing.

**Usage:** `command 'meeting-detect'`

---

## What This Command Does

1. **Scans Google Drive** Fireflies/Transcripts folder (ID: `1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV`)
2. **Filters unprocessed** - Skips files starting with `[ZO-PROCESSED]`
3. **Downloads new transcripts** to `N5/inbox/transcripts/`
4. **Creates request files** in `N5/inbox/meeting_requests/`
5. **Ready for processing** - Files queued for `command 'meeting-process'`

---

## State Tracking Method

**Google Drive filenames are the source of truth:**

```
UNPROCESSED: "Daily team stand-up-transcript-2025-10-03.docx"
PROCESSED:   "[ZO-PROCESSED] Daily team stand-up-transcript-2025-10-03.docx"
```

**Benefits:**
- ✅ No local state files needed
- ✅ Visual confirmation in Drive
- ✅ Idempotent (safe to re-run)
- ✅ Crash-safe (rename happens after processing)

---

## Workflow Steps

### 1. List All Files in Transcripts Folder

```python
# Zo calls: use_app_google_drive
tool: "google_drive-list-files"
folderId: "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"
fields: "files(id,name,mimeType,modifiedTime,webViewLink)"
trashed: false
```

### 2. Filter Unprocessed Files

```python
unprocessed = [
    f for f in files 
    if not f['name'].startswith('[ZO-PROCESSED]')
]
```

**Note:** ALL files in the folder are transcripts—no additional name/extension filtering needed.

### 3. For Each Unprocessed File

a. **Download from Google Drive**
   - Use `google_drive-download-file-by-id`
   - Save to `N5/inbox/transcripts/{meeting_id}.txt`

b. **Parse filename** to extract:
   - Meeting ID (date + participants)
   - Participants list
   - Date

c. **Classify stakeholder type** (if classifier available)
   - Internal vs External
   - Use email domains from transcript

d. **Create request file**
   - `N5/inbox/meeting_requests/{meeting_id}_request.json`
   - Contains: meeting_id, gdrive_id, participants, date, status

### 4. Report Results

```
✅ Detected: 3 new transcripts
📥 Downloaded: 3 files
📋 Queued: 3 processing requests
```

---

## Request File Format

```json
{
  "meeting_id": "2025-10-10_internal-strategy",
  "participants": "Logan x Vrijen",
  "date": "2025-10-10",
  "gdrive_id": "1WHiMtOeJBRrRj8R6bikHCBWv3aawMKD77nUkXB7bKRQ",
  "gdrive_link": "https://docs.google.com/document/d/...",
  "original_filename": "Logan x Vrijen Resync #2 - Oct 10",
  "created_at": "2025-10-10T19:50:00Z",
  "status": "pending"
}
```

---

## When Processing Completes

**After `command 'meeting-process'` succeeds:**

1. Rename file in Google Drive: add `[ZO-PROCESSED]` prefix
2. Move request to `N5/inbox/meeting_requests/completed/`
3. Meeting intelligence saved to `N5/records/meetings/{meeting_id}/`

---

## Error Handling

**If download fails:**
- Skip file
- Log error
- Continue with other files

**If classification fails:**
- Use fallback classification ("unknown")
- Still create request file
- Processing can handle it

---

## Integration with Scheduled Tasks

**Scheduled Task:** "Process New Meeting Transcripts in FULL Mode"  
**ID:** `afda82fa-7096-442a-9d65-24d831e3df4f`  
**Frequency:** Every 30 minutes

**What it does:**
```
command 'meeting-detect'
```

That's it! Simple invocation that:
1. Scans Drive
2. Downloads new transcripts
3. Queues them for processing

---

## Manual Usage

**Check for new transcripts right now:**
```
command 'meeting-detect'
```

**Then check queue:**
```bash
ls N5/inbox/meeting_requests/*.json
```

**Process oldest immediately:**
```
command 'meeting-process'
```

---

## Related Commands

- `command 'meeting-process'` - Process one queued transcript
- `command 'meeting-approve'` - Approve processed meeting for publishing

---

**Last Updated:** 2025-10-10  
**Version:** 3.0 (Google Drive Rename Strategy)
