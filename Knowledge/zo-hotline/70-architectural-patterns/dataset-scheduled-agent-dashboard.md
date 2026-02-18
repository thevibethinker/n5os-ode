---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Dataset Scheduled Agent Dashboard Pattern

## What It Is

- Scheduled agent pulls fresh data into Zo Datasets
- Dashboard page in zo.space visualizes current state
- Creates always-current data view without manual updates

## When to Use

- Business metrics need daily refresh
- External APIs provide regular data updates
- Team needs shared visibility into changing data
- Reports must stay current automatically

## Minimal Build Recipe

- Create dataset with `datapackage.json` structure
- Agent runs daily: `create_agent("FREQ=DAILY", "Refresh dataset from API")`
- Agent fetches data, updates `data.duckdb`
- Dashboard page reads dataset: `update_space_route("/dashboard", "page", code)`
- Use DuckDB queries for charts and tables
- Set page public if team needs access

## Example Prompts

- "Build daily sales dashboard that auto-updates from our CRM API"
- "Create team performance tracker that refreshes every morning"

## Common Failure Modes

- API rate limits kill scheduled updates
- Dataset grows too large without cleanup
- Dashboard loads slowly with complex queries