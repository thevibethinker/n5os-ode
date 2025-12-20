---
title: Luma Register Event
description: Registers for a Luma event using Zo's Browser (human-in-the-loop)
tags: [luma, registration, events]
tool: true
---

# Luma Event Registration (Human-in-the-Loop)

This prompt handles event registration through Zo's Browser since local Playwright can't run headed browsers.

<system>
## Prerequisites
- User must be logged into Luma via Zo's Browser (Settings → Browser)
- Event must be approved in the database (status = 'approved')

## Workflow

### Step 1: Get Event Details
```bash
sqlite3 /home/workspace/N5/data/luma_events.db "SELECT id, title, url, event_datetime FROM events WHERE status = 'approved' AND registered_at IS NULL LIMIT 5"
```

### Step 2: For Each Event to Register
1. **View the registration page** using `view_webpage(url)`
2. **Extract form questions** from the page
3. **Generate draft answers** using Content Library or defaults:
   - Name: Vrijen Attawar
   - Email: vrijen@mycareerspan.com
   - Company: Careerspan
   - Role: Founder & CEO
   - LinkedIn: https://linkedin.com/in/vattawar
   - Twitter/X: https://x.com/vattawar

4. **Present draft to user for approval:**
   ```
   📝 REGISTRATION DRAFT for: [Event Title]
   
   Q: [Question 1]
   A: [Draft Answer 1]
   
   Q: [Question 2]  
   A: [Draft Answer 2]
   
   ✅ Approve and register?
   ❌ Edit answers?
   ⏭️ Skip this event?
   ```

5. **If approved:** 
   - Instruct user: "Please complete registration at [URL] with these answers"
   - Or if form is simple, attempt via `view_webpage` interaction

### Step 3: Update Database
```bash
sqlite3 /home/workspace/N5/data/luma_events.db "UPDATE events SET registered_at = datetime('now'), registration_status = 'registered' WHERE id = '[EVENT_ID]'"
```

### Step 4: Send Confirmation
```bash
python3 /home/workspace/N5/scripts/send_sms_notification.py --message "✅ Registered for: [Event Title] on [Date]"
```

### Step 5: Add to Calendar
```bash
python3 /home/workspace/N5/scripts/luma_calendar.py --event-id [EVENT_ID]
```
</system>

## Notes
- Registration requires human confirmation (no auto-submit without approval)
- All draft answers shown before any action taken
- SMS notification sent on successful registration

