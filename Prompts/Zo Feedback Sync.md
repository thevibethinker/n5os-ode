---
description: Sync new Zo feedback reports to Google Drive ZoReports folder
tags: [zo, feedback, sync, google-drive, automation]
---

# Zo Feedback Sync Recipe

**Purpose:** Upload pending feedback reports to Google Drive for Zo team review.

## Process

1. **Query new feedback** from database:
   ```bash
   python3 /home/workspace/N5/scripts/zo_report.py --list-new
   ```

2. **For each feedback item:**
   - Generate markdown report
   - Upload any attachments to Drive (folder: `1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl`)
   - Create Google Doc in ZoReports folder
   - Mark as 'sent' in database

3. **Upload attachments** (if present):
   ```python
   use_app_google_drive(
       tool_name="google_drive-upload-file",
       configured_props={
           "folderId": "1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl",
           "filePath": attachment_path,
           "mimeType": mime_type
       }
   )
   ```

4. **Create Google Doc** with feedback content:
   - Convert markdown to Google Doc format
   - Use tool: `google_drive-create-file-from-text`
   - Include links to uploaded attachments
   - Title format: `[Zo Feedback] {title} - {feedback_id}`

5. **Mark as sent**:
   ```python
   # Update database status
   UPDATE feedback SET status='sent', sent_at=NOW() WHERE id=?
   ```

6. **Report results**:
   ```
   ✓ Synced {count} feedback items to Google Drive
   - {high_count} high severity
   - {medium_count} medium severity
   - {low_count} low severity
   ```

## Database Schema

**Location:** `file 'N5/data/zo_feedback.db'`

**Tables:**
- `feedback` - Main feedback records
- `feedback_attachments` - File attachments metadata

**Key fields:**
- `status` - 'new', 'sent', 'resolved'
- `type` - 'bug', 'improvement', 'question', 'glitch'
- `severity` - 'low', 'medium', 'high'

## Error Handling

- If Drive upload fails → Log error, keep status='new', retry next sync
- If attachment missing → Log warning, upload doc without attachment
- If doc creation fails → Log error, mark item for manual review

## Notes

- This recipe is typically invoked via scheduled task (daily at 08:00 ET)
- Can be run manually: "Run Zo Feedback Sync recipe"
- Drive folder is shared with Zo team
- Attachments stored in: `file 'N5/data/zo_feedback_attachments/'`
