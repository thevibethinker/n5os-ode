---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
---

# Journal System v1

```yaml
capability_id: journal-system-v1
name: "Journal System"
category: internal
status: active
confidence: high
last_verified: 2025-12-11
tags:
  - personal-intelligence
  - journaling
  - analytics
  - agents
entry_points:
  - type: script
    id: "N5/scripts/journal.py"
  - type: script
    id: "N5/scripts/journal_analytics.py"
  - type: script
    id: "N5/scripts/monitor_temptations.py"
  - type: agent
    id: "morning-pages-agent"
  - type: agent
    id: "evening-reflection-agent"
  - type: agent
    id: "temptation-monitor-agent"
owner: "V"
```

## What This Does

A complete personal journaling system with SQLite storage, CLI interface, and proactive agentic support. It captures structured reflection data (mood, tags, diet) and provides analytical insights.

It includes a **temptation monitoring loop** that checks in on V after he logs a temptation/urge, and **daily scheduled nudges** for morning pages and evening reflections.

## How to Use It

### CLI Interface

```bash
# New entry
python3 N5/scripts/journal.py new [type] --mood "..." --tags "..."

# Analytics
python3 N5/scripts/journal_analytics.py --days 30
```

### Agents

- **Morning Pages (8 AM):** SMS reminder.
- **Temptation Monitor (Hourly):** Checks DB for recent 'temptation' entries without follow-up. Sends SMS if >2h elapsed.
- **Evening Reflection (9 PM):** SMS reminder with context from Google Calendar.

## Architecture

- **Database:** `file 'N5/data/journal.db'` (SQLite)
- **State:** `file 'N5/data/temptation_monitor.state'` (Tracks last processed temptation ID)
- **Context:** `file 'N5/data/daily_context.md'` (Generated daily by evening agent)

## Associated Files

- `file 'N5/scripts/journal.py'` - Core CLI
- `file 'N5/scripts/journal_analytics.py'` - Reporting & Insights
- `file 'N5/scripts/monitor_temptations.py'` - Agent logic
- `file 'N5/scripts/test_temptation_logic.py'` - Verification test

