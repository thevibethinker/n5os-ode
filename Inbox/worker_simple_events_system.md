---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_WoVYvJ5iACxi1PaC
type: worker_assignment
---

# Worker Assignment: Simple Events System (LLM-First)

## Context

V has an existing over-engineered events pipeline with multiple Python scripts, JSON configs, and scoring algorithms. The directive is: **Simple over easy. Use LLMs more, Python less.**

## Objective

Replace the complex Python pipeline with a single daily agent that uses LLM intelligence directly.

## The Simple Architecture

| Layer | Tool |
|-------|------|
| Discovery | Gmail search (7-day rolling window) |
| Intelligence | LLM reads emails, extracts events |
| Filtering | LLM applies V's preferences (no Python scoring) |
| Output | Email digest to V |
| Reference | Existing calendar site (keep as-is) |

## V's Must-Go Organizers (Hardcode in Agent Prompt)

- **Andrew Yeung** — runs fibe, founder breakfast events
- **FOHE / Anna Bao** — Future of Higher Education community
- **Ben Guo** — Velocity Coding, 0thernet
- **Victoria Yampelsky** — Startup Station, founder community
- **Marvin Ventures** — VC events, newsletter@marvin.vc

## V's Interests (For LLM Judgment)

- AI / ML founders and investors
- NYC tech networking
- Career / recruiting / talent
- Founder dinners and intimate gatherings
- Prefers evening events, flexible on weekends

## Event Platforms to Search

Gmail query: `(lu.ma OR partiful.com OR supermomos OR eventbrite.com OR meetup.com) newer_than:7d`

## Deliverables

### 1. Create Daily Events Agent

**Schedule:** Daily at 7:00 AM ET (before morning digest)

**Instruction (draft):**
```
Search V's Gmail (attawar.v@gmail.com) for event-related emails from the last 7 days using query: (lu.ma OR partiful.com OR supermomos OR eventbrite.com OR meetup.com) newer_than:7d

Read the email content and extract NYC events. For each event found, note:
- Title
- Date/time
- Organizer
- Location (if mentioned)
- Registration link

Then recommend which events V should attend. Use these criteria:

MUST-GO (always recommend):
- Andrew Yeung / fibe events
- FOHE / Anna Bao / Future of Higher Education
- Ben Guo / Velocity Coding / 0thernet
- Victoria Yampelsky / Startup Station
- Marvin Ventures events

HIGH INTEREST:
- AI/ML founder gatherings
- Investor mixers
- Career/recruiting/talent events
- Intimate founder dinners (<30 people)

LOWER PRIORITY:
- Large conferences (>200 people)
- Events outside NYC
- Daytime events on weekdays (V is busy)

Output format:
## 🎯 Must-Go Events
[List with links and why]

## 📅 Recommended Events
[List with links and brief reason]

## 📋 Other Events This Week
[Quick list of everything else found]

Email this to V.
```

### 2. Update Existing Calendar Site

The calendar at https://events-calendar-va.zocomputer.io should pull from `N5/data/luma_candidates.json`. 

**Keep it simple:** The site already works. Just ensure the Luma scraper (`python3 N5/scripts/luma_scraper.py --city nyc --days 30`) runs before the calendar is checked, OR accept that the calendar shows what's been scraped.

### 3. Deprecation List

Mark these as deprecated (don't delete yet, just stop using):
- `N5/scripts/event_recommender.py` — LLM does this now
- `N5/scripts/manage_allowlist.py` — preferences in agent prompt
- `N5/scripts/manage_must_go.py` — preferences in agent prompt
- `N5/scripts/get_allowlist_query.py` — hardcoded in agent
- `N5/scripts/smart_event_detector.py` — LLM does this now
- `N5/scripts/seed_event_sources.py` — one-time, not needed
- `N5/config/allowlists.json` — preferences in agent prompt
- `N5/config/event_preferences.json` — preferences in agent prompt
- Hourly "Event Source Manager" agent — not needed

### 4. Keep

- `N5/scripts/luma_scraper.py` — useful for populating calendar site
- `Sites/events-calendar-staging/` — visual reference
- The `events-calendar` user service

## Success Criteria

1. ✅ Daily agent created that emails V event recommendations
2. ✅ Agent uses LLM judgment, not Python scoring
3. ✅ Must-go organizers are respected
4. ✅ No new Python scripts created
5. ✅ Calendar site still works for visual browsing

## Notes

- The Gmail API sometimes returns truncated content. If the LLM can't extract enough info from email snippets, it may need to follow links. Test this.
- V's livelihood depends on not missing events. When in doubt, include an event rather than exclude it.
- Keep the Luma scraper running weekly to populate the calendar site with broader event data.

## Report Back

When complete, summarize:
1. Agent ID and schedule
2. What was deprecated
3. Any issues encountered
4. First test run results (if possible)

