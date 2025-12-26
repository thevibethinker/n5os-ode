---
created: 2025-11-16
last_edited: 2025-11-16
version: 2.0
---

# Granola Zapier Webhook Setup

## Webhook URL

Use this URL in your Zapier webhook configuration:

**`https://zapier-webhook-va.zocomputer.io/webhook/zapier/granola`**

## Overview

This webhook receives JSON payloads from Zapier (triggered by Granola) and automatically saves meeting data to the processing pipeline at `/home/workspace/Personal/Meetings/Inbox/`.

## File Locations

- **Webhook receiver**: `/home/workspace/webhook-receiver/server.js`
- **Webhook logs**: `/home/workspace/webhook-receiver/webhook-logs.jsonl`
- **Meeting intake**: `/home/workspace/Personal/Meetings/Inbox/`
- **Meeting processing docs**: `/home/workspace/N5/prefs/operations/meetings-folder-structure.md`

## Expected JSON Payload Structure

The webhook expects the following fields from Zapier/Granola:

```json
{
  "transcript": "Full meeting transcript text",
  "meeting_title": "Title of the meeting note",
  "enhanced_notes": "AI-enhanced summary and notes",
  "meeting_time": "2025-11-16T10:00:00Z",
  "calendar_title": "Original calendar event name",
  "attendees": ["Attendee 1", "Attendee 2"],
  "creator_name": "Name of person who shared the note",
  "creator_email": "Email of creator",
  "granola_link": "https://link-to-granola-note",
  "meeting_id": "unique-meeting-id"
}
```

### Required Fields
- `transcript`
- `meeting_title`
- `meeting_time`

### Optional Fields
All other fields are optional and will use sensible defaults if not provided.

## Output Format

The webhook creates **folder structures** in the meeting processing pipeline with the following naming pattern:

```
YYYY-MM-DD_sanitized_meeting_name/
```

Example:
```
2025-11-16_test_calendar_event/
  ├── transcript.md
  └── _metadata.json
```

### Folder Contents

#### 1. `transcript.md`
Contains the meeting transcript with essential metadata at the top:

```markdown
Meeting Title: Test Meeting

Calendar Event ID: test_123

Attendee Emails: person1@example.com, person2@example.com

Creator Email: v@careerspan.com

Enhanced Notes:
These are enhanced AI notes from Granola

Transcript:

[Speaker 1]: Welcome to the meeting...
[Speaker 2]: Thanks for having me...
```

#### 2. `_metadata.json`
Contains full meeting metadata:

```json
{
  "meeting_id": "test_123",
  "meeting_title": "Test Meeting",
  "calendar_title": "Test Calendar Event",
  "meeting_time": "2025-11-16T10:00:00Z",
  "meeting_date": "2025-11-16",
  "attendees": ["person1@example.com", "person2@example.com"],
  "creator_name": "Vrijen Attawar",
  "creator_email": "v@careerspan.com",
  "granola_link": "https://granola.test/link",
  "enhanced_notes": "These are enhanced AI notes",
  "source": "granola_zapier",
  "ingested_at": "2025-11-16T15:02:21.620Z",
  "folder_name": "2025-11-16_test_calendar_event",
  "transcript_path": "/home/workspace/Personal/Meetings/Inbox/2025-11-16_test_calendar_event/transcript.md"
}
```

## Testing the Webhook

### Quick Test Command

```bash
curl -X POST https://zapier-webhook-va.zocomputer.io/webhook/zapier/granola \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Test meeting transcript",
    "meeting_title": "Test Meeting",
    "meeting_time": "2025-11-16T10:00:00Z",
    "calendar_title": "Test Calendar Event",
    "attendees": ["Vrijen Attawar", "Test Participant"],
    "creator_name": "Vrijen Attawar",
    "creator_email": "v@careerspan.com",
    "granola_link": "https://granola.test/link",
    "meeting_id": "test_123",
    "enhanced_notes": "These are enhanced AI notes"
  }'
```

### Health Check

Check if the webhook service is running:
```bash
curl https://zapier-webhook-va.zocomputer.io/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-16T15:02:21.620Z"
}
```

### View Recent Webhooks

```bash
curl https://zapier-webhook-va.zocomputer.io/logs
```

### View Recent Meetings

```bash
curl https://zapier-webhook-va.zocomputer.io/meetings
```

This will return a list of recently created meeting folders in `/home/workspace/Personal/Meetings/Inbox/`.

## Troubleshooting

### Issue: Webhook returns 404

**Solution**: The service may need to be restarted to pick up the new endpoint.
```bash
# From /home/workspace/webhook-receiver/
pkill -f "node server.js"
nohup node server.js > /dev/null 2>&1 &
```

### Issue: Folders not appearing in Personal/Meetings/Inbox/

**Solution**: Check the webhook logs for errors:
```bash
tail -f /home/workspace/webhook-receiver/webhook-logs.jsonl
```

### Issue: Invalid meeting_time format

**Solution**: Ensure the `meeting_time` field is in ISO 8601 format (e.g., `2025-11-16T10:00:00Z`).

## Integration with Meeting Processing Pipeline

Folders created in `Personal/Meetings/Inbox/` are automatically picked up by your scheduled meeting processing tasks. These tasks:
1. Scan for new meeting folders in Inbox
2. Run meeting intelligence analysis
3. Generate action items and summaries
4. Move processed meetings to `/home/workspace/Personal/Meetings/` with enriched metadata
5. Create normalized meeting intelligence blocks (B01, B02, B26, etc.)

For more details on the meeting processing pipeline, see:
- `/home/workspace/N5/prefs/operations/meetings-folder-structure.md`
- Your scheduled tasks in the Zo Computer dashboard

[^1]: /home/workspace/N5/prefs/operations/meetings-folder-structure.md


