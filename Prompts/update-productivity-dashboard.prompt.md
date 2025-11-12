---
description: Fetch real Gmail and Calendar data, update productivity dashboard with correct RPI calculation
tags: [productivity, automation, gmail, calendar, rpi, dashboard]
tool: true
created: 2025-11-06
last_edited: 2025-11-06
version: 1.0
---

# Update Productivity Dashboard

Fetch today's sent email count from BOTH Gmail accounts, calculate meeting hours from calendar, then update the productivity database with real data.

## Critical Requirements

**NEVER use fallback or fake data. If APIs fail, report error and exit.**

## Steps

### 1. Fetch Gmail Data from BOTH Accounts

Query **attawar.v@gmail.com**:
```
use_app_gmail(
  tool_name="gmail-find-email",
  configured_props={
    "q": "in:sent after:{TODAY}",
    "maxResults": 500,
    "metadataOnly": true,
    "withTextPayload": false
  },
  email="attawar.v@gmail.com"
)
```

Query **vrijen@mycareerspan.com**:
```
use_app_gmail(
  tool_name="gmail-find-email",
  configured_props={
    "q": "in:sent after:{TODAY}",
    "maxResults": 500,
    "metadataOnly": true,
    "withTextPayload": false
  },
  email="vrijen@mycareerspan.com"
)
```

Count emails from both accounts: `total_emails = len(personal_emails) + len(business_emails)`

### 2. Fetch Calendar Meeting Hours

Query Google Calendar for today's events:
```
use_app_google_calendar(
  tool_name="google_calendar-list-events",
  configured_props={
    "calendarId": "primary",
    "timeMin": "{TODAY}T00:00:00-05:00",
    "timeMax": "{TODAY}T23:59:59-05:00",
    "singleEvents": true,
    "maxResults": 100
  },
  email="attawar.v@gmail.com"
)
```

Calculate meeting hours:
- Parse each event's `start.dateTime` and `end.dateTime`
- Skip all-day events (those with only `start.date` instead of `start.dateTime`)
- Sum duration in hours: `(end - start).total_seconds() / 3600`

### 3. Update Database with Real Data

Call the sync script with real data:
```bash
python3 /home/workspace/Sites/productivity-dashboard/sync_gmail_v2.py \
  --emails {TOTAL_EMAILS} \
  --meetings {MEETING_HOURS}
```

### 4. Verify Update

Check database:
```bash
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT date, emails_sent, meeting_hours, expected_emails, rpi FROM daily_stats WHERE date = date('now')"
```

Log the result with timestamp.

## Error Handling

- If Gmail API fails → Exit with error, DO NOT use fake data
- If Calendar API fails → Exit with error, DO NOT use fake data
- If database update fails → Report error with details

## Output Format

Log structured JSON:
```json
{
  "date": "YYYY-MM-DD",
  "emails_sent": N,
  "meeting_hours": X.X,
  "expected_emails": Y.Y,
  "rpi": Z.Z,
  "status": "success"
}
```
