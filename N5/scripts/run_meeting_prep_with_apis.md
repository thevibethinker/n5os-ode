# Meeting Prep Digest - API Integration Instructions

**Created:** 2025-10-12  
**Status:** Implementation guide for Zo-based API integration

---

## Overview

The meeting prep digest script (`meeting_prep_digest.py`) currently uses mock data for Gmail and Google Calendar APIs. To integrate real data, the script needs to be called from within a Zo context that has access to `use_app_gmail` and `use_app_google_calendar` tools.

## Integration Approach

Since the scheduled task runs in a Zo context (not standalone Python), we have two options:

### Option 1: Pure Zo Scheduled Task (RECOMMENDED)
Replace the Python script call with a direct Zo instruction that:
1. Calls Google Calendar API
2. Filters meetings  
3. Calls Gmail API for each external attendee
4. Generates digest
5. Saves to file

**Pros:**
- Direct API access
- No subprocess complexity
- Simpler to maintain

**Cons:**
- Scheduled task instruction will be longer
- Logic lives in instruction, not reusable script

### Option 2: Hybrid Python + Zo Wrapper
Create a Python script that:
1. Runs in Zo context (via scheduled task)
2. Uses subprocess or JSON RPC to call Zo tools
3. Passes results to meeting_prep_digest.py

**Pros:**
- Keeps logic in reusable Python script
- Easier to test

**Cons:**
- More complex architecture
- Subprocess overhead

---

## Recommended Implementation: Pure Zo Scheduled Task

Replace the current scheduled task instruction with:

```
Generate and email daily meeting prep digest. Steps:
1. Fetch today's calendar events using Google Calendar API
2. Filter for external meetings only (exclude internal domains: mycareerspan.com, theapply.ai)
3. Exclude daily recurring meetings (patterns: "daily standup", "daily sync", etc)
4. For each external meeting:
   a. Extract V-OS tags from description ([LD-*], [!!], [A-*], etc)
   b. Skip if [OFF] or [TERM] status
   c. For each external attendee, get last 3 Gmail interactions
   d. Check for existing stakeholder profile in N5/records/meetings/
5. Generate digest in BLUF format with:
   - Chronological TOC
   - Per-meeting sections: BLUF, last 3 interactions, calendar context, prep actions
   - Tag-based prep actions (discovery → questions, critical → protect time, etc)
6. Save to N5/digests/daily-meeting-prep-{date}.md
7. Email digest to me with subject "Daily Meeting Prep — {date}"
```

---

## Alternative: Modular Python with API Stubs

Keep the current Python script structure but add API integration points:

### Gmail API Integration

```python
def get_last_3_interactions_zo(email: str) -> List[Dict[str, str]]:
    """Call Gmail API via Zo tools"""
    import json
    import subprocess
    
    # When called from Zo context, this would work:
    result = subprocess.run([
        'zo-tool', 'use_app_gmail',
        '--tool-name', 'gmail-search-messages',
        '--configured-props', json.dumps({
            "q": f"from:{email} OR to:{email}",
            "maxResults": 3
        })
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        messages = json.loads(result.stdout)
        return parse_gmail_messages(messages)
    else:
        logger.error(f"Gmail API error: {result.stderr}")
        return []
```

### Google Calendar API Integration

```python
def fetch_calendar_events_zo(target_date: datetime.date) -> List[Dict[str, Any]]:
    """Call Google Calendar API via Zo tools"""
    import json
    import subprocess
    
    # When called from Zo context, this would work:
    result = subprocess.run([
        'zo-tool', 'use_app_google_calendar',
        '--tool-name', 'google_calendar-list-events',
        '--configured-props', json.dumps({
            "calendarId": "primary",
            "timeMin": f"{target_date}T00:00:00-04:00",
            "timeMax": f"{target_date}T23:59:59-04:00",
            "timeZone": "America/New_York"
        })
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        events = json.loads(result.stdout)
        return parse_calendar_events(events)
    else:
        logger.error(f"Calendar API error: {result.stderr}")
        return []
```

---

## Decision Point

**Question for V:** Which approach do you prefer?

1. **Pure Zo task** - Replace Python script with longer scheduled task instruction
2. **Keep Python script** - Add API integration via subprocess/JSON RPC
3. **Hybrid** - Keep script for logic, but scheduled task calls APIs and passes data

---

## Current Status

- ✅ V-OS tag parsing implemented
- ✅ External meeting filtering implemented
- ✅ BLUF format generation implemented
- ✅ Stakeholder research workflow implemented
- ⏳ Gmail API integration (mock data)
- ⏳ Google Calendar API integration (mock data)
- ⏳ Scheduled task updated for v2.0.0

---

## Next Steps

1. **Decide integration approach** (see Decision Point above)
2. **Implement chosen approach**
3. **Test with real data**
4. **Update scheduled tasks** (generation + email)
5. **Monitor first runs** and adjust as needed

