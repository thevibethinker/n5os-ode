---
name: sourcestack-monitor
description: >
  SourceStack API integration for ad-hoc job searches and automated daily monitoring.
  Maintains a local SQLite database of job postings with full descriptions for semantic querying.
  Supports a YAML watchlist of companies, roles, and filters that can be edited anytime.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
  created: "2026-02-09"
---

## Overview

Two-mode SourceStack integration:

1. **Ad hoc search** — Query SourceStack for jobs matching any criteria, results stored locally
2. **Daily scan** — Automated monitoring of a predefined watchlist, surfaces only new/changed jobs

All results are stored in a local SQLite database with full job descriptions for later querying.

## Setup

API key should be set as a secret in [Settings > Developers](/?t=settings&s=developers):
- Name: `SOURCESTACK_API_KEY`

Install dependencies:
```bash
pip install -r Skills/sourcestack-monitor/scripts/requirements.txt
```

## CLI Usage

```bash
cd Skills/sourcestack-monitor

# Check credit balance
python3 scripts/sourcestack.py quota

# Ad hoc search
python3 scripts/sourcestack.py search --role "product manager" --company stripe.com --limit 20
python3 scripts/sourcestack.py search --role "chief of staff" --country "United States" --limit 50

# Run daily scan (reads watchlist.yaml, stores new jobs)
python3 scripts/sourcestack.py scan
python3 scripts/sourcestack.py scan --dry-run

# Query local database
python3 scripts/sourcestack.py query --company stripe --status active
python3 scripts/sourcestack.py query --text "stakeholder management" --since 7d
python3 scripts/sourcestack.py query --new-today

# Manage watchlist
python3 scripts/sourcestack.py watchlist
python3 scripts/sourcestack.py watchlist --add-company "openai.com:OpenAI"
python3 scripts/sourcestack.py watchlist --remove-company "openai.com"
python3 scripts/sourcestack.py watchlist --add-role "staff engineer"
python3 scripts/sourcestack.py watchlist --remove-role "staff engineer"

# Delta report (what changed since last scan)
python3 scripts/sourcestack.py delta --since 1d
```

## Watchlist Configuration

Edit `assets/watchlist.yaml` to add/remove companies, roles, and default filters.
The scanner reads this file fresh each run.

## Database

SQLite database at `data/sourcestack.db`. Tables:
- `jobs` — Every job posting seen, with full description text
- `scans` — Audit trail of every scan run

## Scheduled Agent

Set up a daily scan agent that runs `scan` and emails/texts a delta report.
The scan uses `LAST_1D` filtering to minimize credit usage (~5-20 credits/day).

## Credit Budget

- `count_only=True` queries are **free**
- Daily scans with 30 companies: ~5-20 credits/day
- Ad hoc search: 1 credit per job returned
- 100k credits lasts years at daily scan rates
