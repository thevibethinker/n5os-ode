# `meeting-prep-digest`

Generate daily meeting intelligence digest with attendee research and email context.

## Usage

```bash
# Generate digest for today
meeting-prep-digest

# Generate for specific date
meeting-prep-digest --date 2025-10-10

# Preview without saving
meeting-prep-digest --dry-run
```

## Description

Automated daily meeting prep that scans your calendar, filters for external meetings, researches attendees, and surfaces relevant context. Runs every morning at 06:00 ET to prep you for the day ahead.

**What it does:**

1. **Calendar Scan** - Fetches today's meetings from Google Calendar
2. **Smart Filtering** - Excludes internal meetings and internal 1:1s
3. **Email Context** - Scans Gmail for past interactions (90 days → all-time)
4. **Light Research** - LinkedIn, company sites, recent news
5. **Auto-Detection** - Identifies whether attendee is person/company/org
6. **Context Injection** - Parses meeting titles for relevant framing

**Exclusions:**
- Internal events (all attendees @mycareerspan.com or @theapply.ai)
- Internal 1:1s (2 attendees, both internal)
- All-day events
- Declined meetings

## Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--date` | str | today | Target date (YYYY-MM-DD or "today") |
| `--dry-run` | flag | False | Preview without generating file |

## What Gets Generated

**Output File:** `N5/digests/daily-meeting-prep-YYYY-MM-DD.md`

**Content Structure:**
- Meeting-by-meeting breakdown
- Email history summary (max 3 bullets per person)
- Quick research (LinkedIn, company info, recent activity)
- Auto-injected context from meeting titles
- Clarification prompts for unclear attendees
- Summary stats and action items

## Examples

```bash
# Standard daily run (scheduled at 06:00 ET)
meeting-prep-digest

# Generate for tomorrow
meeting-prep-digest --date 2025-10-10

# Test without saving
meeting-prep-digest --date today --dry-run
```

## Related Commands

- `knowledge-ingest` - Ingest research results into knowledge base
- `research-prompt-generator` - Generate deep research prompts

## Implementation

**Script:** `N5/scripts/meeting_prep_digest.py`  
**Scheduled:** Daily at 06:00 ET via Zo scheduled tasks

## Notes

- Gmail scan starts at 90 days, extends to all-time if needed
- Light research is sufficient for meeting prep (not deep research)
- Unclear attendee names are flagged with clarification prompts
- Entity type auto-detected using email domain + LLM analysis
