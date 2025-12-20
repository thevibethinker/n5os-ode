---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
title: Luma Event Digest
description: >
  Generate and review Luma event recommendations for NYC.
  Scrapes events, scores them, and presents top picks for approval.
tags:
  - events
  - networking
  - luma
  - automation
tool: true
---

# Luma Event Digest

Generate personalized event recommendations from Luma.

## Workflow

1. **Scrape** - Fetch latest NYC events from lu.ma/nyc
2. **Score** - Rank events by relevance (AI, founders, networking, timing)
3. **Filter** - Apply booking rules (max 3/week, prefer 2-3 weeks out)
4. **Present** - Show top 5 recommendations with approval actions

## Usage

```bash
# Full workflow: scrape + score + digest
cd /home/workspace
python3 N5/scripts/luma_scraper.py --city nyc --days 21
python3 N5/scripts/luma_scorer.py --city nyc
python3 N5/scripts/luma_digest.py --preview --city nyc --num 5
```

## Approval Actions

When V approves events, run:
```bash
# Approve an event (by event ID from digest)
python3 -c "
from N5.scripts.luma_calendar import mark_event_approved
result = mark_event_approved('EVENT_ID_HERE')
print(result)
"
```

## Related Files

- Config: `N5/config/luma_scoring.json`
- Database: `N5/data/luma_events.db`
- Digests: `N5/digests/luma-event-digest-*.md`

