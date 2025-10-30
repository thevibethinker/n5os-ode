# Meeting Prep Digest v2.0 - Reference Guide

**Version:** 2.0.0  
**Status:** Production (API integration pending)  
**Last Updated:** 2025-10-30  
**Related:** `file 'N5/scripts/run_meeting_prep_with_apis.md'`

---

## Overview

The Meeting Prep Digest is a daily automated report that provides BLUF-style briefings for external meetings. It integrates calendar data, email history, stakeholder intelligence, and V-OS tag context to deliver actionable prep guidance.

---

## Purpose

**What it does:**
- Fetches today's calendar events from Google Calendar
- Filters for external meetings (excludes internal domains)
- Retrieves last 3 Gmail interactions per external attendee
- Analyzes V-OS tags for meeting context
- Generates BLUF prep briefing for each meeting
- Emails digest to V at configured time (default: 8am ET)

**Why it exists:**
- Eliminates manual meeting prep research
- Surfaces stakeholder context automatically
- Ensures critical meetings get proper prep
- Integrates calendar intelligence with CRM data

---

## Architecture

### Components

1. **meeting_prep_digest.py** - Core script (Python)
   - Location: `N5/scripts/meeting_prep_digest.py`
   - Inputs: Google Calendar, Gmail APIs (via Zo)
   - Output: Markdown digest file

2. **Scheduled Task** - Automation
   - Frequency: Daily at 8:00am ET
   - Triggers: meeting_prep_digest.py execution
   - Delivers: Email to V with digest

3. **V-OS Tag System** - Meeting classification
   - Location: `file 'Documents/System/guides/calendar-tagging-system.md'`
   - Format: Square brackets in calendar descriptions
   - Examples: `[LD-Discovery]`, `[!!]`, `[A-Partner]`

4. **Stakeholder Profiles** - CRM integration
   - Location: `Knowledge/crm/individuals/`
   - Format: Markdown profiles with structured data
   - Auto-linked in digest when available

---

## Meeting Filtering Logic

### Included Meetings

✅ **Include if:**
- Has external attendees (non-internal domains)
- Scheduled for target date
- Not marked with exclusion tags

### Excluded Meetings

❌ **Exclude if:**
- All attendees are internal (@mycareerspan.com, @theapply.ai)
- Daily recurring patterns ("daily standup", "daily sync")
- Marked with `[OFF]` or `[TERM]` status tags
- Declined or tentative on calendar

### External Domain Detection

**Internal domains (excluded):**
- mycareerspan.com
- theapply.ai

**Everything else is external.**

---

## V-OS Tag Integration

### Tag Categories

| Tag Pattern | Category | Digest Action |
|------------|----------|---------------|
| `[LD-*]` | Lifecycle (Discovery/Nurture/Close/Expansion) | Context in BLUF, discovery questions |
| `[A-*]` | Audience (Founder/CXO/Manager/IC) | Tailor communication style |
| `[!!]` | Critical Priority | Highlight, protect time |
| `[T-*]` | Topic (Product/Tech/Partnerships) | Pull relevant context |
| `[OFF]` | Inactive | Skip meeting |
| `[TERM]` | Terminated | Skip meeting |

### Tag-Based Prep Actions

**Discovery stage** (`[LD-Discovery]`):
- Focus on listening and questions
- Prepare open-ended discovery questions
- Avoid premature pitching

**Critical meetings** (`[!!]`):
- Flag as high-priority
- Suggest protecting 15min buffer before/after
- Double-check materials

**Partner meetings** (`[A-Partner]`):
- Pull partnership context
- Review mutual value prop
- Check previous commitments

---

## Digest Format

### Structure

```markdown
# Daily Meeting Prep — YYYY-MM-DD

## Table of Contents
- [09:00 AM] Meeting Title (Attendees)
- [02:00 PM] Meeting Title (Attendees)

---

## [Time] Meeting Title

### BLUF (Bottom Line Up Front)
[One-sentence meeting purpose and recommended approach]

### Last 3 Interactions
**[Person Name]** ([email])
1. [Date] - [Subject line] - [1-sentence summary]
2. [Date] - [Subject line] - [1-sentence summary]
3. [Date] - [Subject line] - [1-sentence summary]

### Calendar Context
- **Tags**: [V-OS tags from description]
- **Duration**: [Length]
- **Location**: [Virtual/Physical]
- **Description**: [First 200 chars]

### Prep Actions
- [ ] [Tag-driven action 1]
- [ ] [Tag-driven action 2]
- [ ] Review stakeholder profile: [link if exists]

---
```

### Example Output

```markdown
# Daily Meeting Prep — 2025-10-30

## Table of Contents
- [02:00 PM] Ash @ Sam Partnership Discussion (Ash Straughn)

---

## [02:00 PM] Ash @ Sam Partnership Discussion

### BLUF
Partnership discussion with Sam co-founder about sourcing integration. Focus on listening mode (discovery stage), avoid premature commitment on timelines.

### Last 3 Interactions
**Ash Straughn** (ash@example.com)
1. Oct 24 - "Great meeting you!" - Follow-up from rooftop event, expressed interest in partnership
2. Oct 25 - "Sam platform overview" - Shared deck on their recruiting platform
3. Oct 28 - "Sync on integration" - Proposed this meeting to discuss technical integration

### Calendar Context
- **Tags**: [LD-Discovery], [A-Founder], [T-Partnerships]
- **Duration**: 60 minutes
- **Location**: Zoom
- **Description**: Discuss Careerspan x Sam integration opportunities. Focus on sourcing vs distribution specialization.

### Prep Actions
- [ ] Review Sam's platform capabilities (deck from Oct 25)
- [ ] Prepare discovery questions on their sourcing process
- [ ] Avoid committing to implementation timelines (discovery mode)
- [ ] Review stakeholder profile: Knowledge/crm/individuals/ash-straughn.md

---
```

---

## API Integration Status

### Current State (v2.0)

**Implemented:**
- ✅ V-OS tag parsing
- ✅ External meeting filtering
- ✅ BLUF format generation
- ✅ Stakeholder profile linking
- ✅ Mock data processing

**Pending:**
- ⏳ Gmail API integration (using mock data)
- ⏳ Google Calendar API integration (using mock data)
- ⏳ Real scheduled task deployment

### Integration Approach

**Method:** Pure Zo scheduled task (recommended)

The script runs in Zo context with direct access to:
- `use_app_google_calendar` - Fetch calendar events
- `use_app_gmail` - Search email history
- `send_email_to_user` - Deliver digest

**See:** `file 'N5/scripts/run_meeting_prep_with_apis.md'` for implementation details

---

## Configuration

### Scheduled Task Settings

**Frequency:** Daily  
**Time:** 8:00 AM ET  
**RRULE:** `FREQ=DAILY;BYHOUR=8;BYMINUTE=0`  

**Instruction:**
```
Generate and email daily meeting prep digest for today's meetings using meeting_prep_digest.py. Include Google Calendar events and Gmail history for external attendees.
```

### Customization Options

**In meeting_prep_digest.py:**
```python
# Internal domains (skip these attendees)
INTERNAL_DOMAINS = ["mycareerspan.com", "theapply.ai"]

# Daily recurring patterns (exclude these)
DAILY_RECURRING_PATTERNS = [
    "daily standup", 
    "daily sync", 
    "daily check-in"
]

# Output location
OUTPUT_DIR = Path("/home/workspace/N5/digests")

# Stakeholder profiles
PROFILES_DIR = Path("/home/workspace/Knowledge/crm/individuals")
```

---

## Usage

### Manual Execution

```bash
cd /home/workspace
python3 N5/scripts/meeting_prep_digest.py --date 2025-10-30
```

### Scheduled Execution

Runs automatically at 8am ET daily via scheduled task.

### Testing

```bash
# Dry run with mock data
python3 N5/scripts/meeting_prep_digest.py --date 2025-10-30 --mock

# Test specific date
python3 N5/scripts/meeting_prep_digest.py --date 2025-11-15
```

---

## Maintenance

### Adding New Tag Types

1. Update `file 'Documents/System/guides/calendar-tagging-system.md'`
2. Add parsing logic in `meeting_prep_digest.py`
3. Define prep actions for new tag in this reference

### Updating Internal Domains

Edit `INTERNAL_DOMAINS` in meeting_prep_digest.py

### Modifying Digest Format

Edit template sections in `meeting_prep_digest.py`:
- `generate_bluf()`
- `format_interactions()`
- `generate_prep_actions()`

---

## Troubleshooting

### No digest received

**Check:**
1. Scheduled task is active (`list_scheduled_tasks`)
2. Script ran without errors (check logs)
3. Email delivery succeeded

### Missing meetings

**Possible causes:**
- Meeting has no external attendees
- Marked with `[OFF]` or `[TERM]`
- Daily recurring pattern matched

### Incorrect stakeholder links

**Fix:**
- Verify profile exists in `Knowledge/crm/individuals/`
- Check filename matches attendee email pattern
- Profile filename should be `firstname-lastname.md`

---

## Future Enhancements

**Planned:**
- [ ] Gmail API integration (replace mock data)
- [ ] Google Calendar API integration (replace mock data)
- [ ] Meeting notes auto-population after meeting
- [ ] Historical meeting pattern detection
- [ ] Smart prep time allocation based on priority

**Considered:**
- Integration with meeting transcript system
- Auto-generated follow-up email drafts
- Stakeholder profile auto-enrichment from interactions

---

**Document Status:** Complete  
**Next Review:** After API integration deployment  
**Owner:** Vibe Operator + Vibe Builder
