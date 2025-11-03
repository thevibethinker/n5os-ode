---
description: Refresh the productivity dashboard by fetching sent emails from Gmail and updating the database with proper word counting (excluding quoted replies and signatures)
tags: [productivity, gmail, dashboard, automation]
tool: true
---

# Refresh Productivity Dashboard

## Workflow

1. **Fetch Sent Emails**: Query Gmail for emails sent today using `in:sent after:YYYY-MM-DD`
2. **Parse Word Counts**: Count only words YOU wrote (exclude quoted replies, signatures, thread history)
3. **Calculate Metrics**:
   - Email count (total sent emails)
   - Word count (original words only)
   - RPI (Response Productivity Index) = emails + (words / 100)
4. **Update Dashboard**: POST data to `/api/refresh` endpoint
5. **Confirm Update**: Display updated metrics

## Word Counting Rules

**INCLUDE:**
- Your original message text

**EXCLUDE:**
- Lines starting with `>`  (quoted replies)
- Content after "On [date], [person] wrote:"
- Email headers (From:, Sent:, To:, Subject:)
- Signature blocks (V-OS Tags, {TWIN}, {CATG}, etc.)
- "Best," and standard closings
- "Sent via Superhuman" footers
- "---" divider lines

## Implementation

Use the Gmail API tool to fetch sent emails, then send the email data to:
- **POST** `http://localhost:3000/api/refresh`
- **Body**: `{"emails": [{"subject": "...", "payload": "..."}]}`

The dashboard endpoint will:
1. Parse each email's payload
2. Count words excluding quoted/signature content
3. Update the SQLite database
4. Return stats summary

## Dashboard Location

https://productivity-dashboard-va.zocomputer.io
