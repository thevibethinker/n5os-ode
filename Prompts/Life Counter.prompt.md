---
title: Life Counter
description: Quick habit and life event tracking - GitHub for Life
tool: true
created: 2025-12-28
last_edited: 2025-12-28
version: 2.0
provenance: con_TwWTxz0rcZU4UqIx
tags:
  - habits
  - tracking
  - wellness
  - life
---

# Life Counter

Quick habit and life event tracking system. Parse natural language and execute the appropriate command.

## Quick Commands

| Input | Action |
|-------|--------|
| `+1 meds` | `python3 N5/scripts/life_counter.py increment meds` |
| `+1 weed` | `python3 N5/scripts/life_counter.py increment weed` |
| `+1 workout` | `python3 N5/scripts/life_counter.py increment workout` |
| `life list` | `python3 N5/scripts/life_counter.py list` |
| `life today` | `python3 N5/scripts/life_counter.py today` |

## Views

| Command | What it shows |
|---------|---------------|
| `ledger` | Bad habits with clean streak (days since last) |
| `scoreboard` | Good habits with current/best streaks |
| `stats` | Summary statistics for period |

```bash
python3 N5/scripts/life_counter.py ledger
python3 N5/scripts/life_counter.py scoreboard
python3 N5/scripts/life_counter.py stats --days 30
```

## Accountability

Daily check for missed good habits:
```bash
python3 N5/scripts/life_accountability.py daily
python3 N5/scripts/life_accountability.py check meds
python3 N5/scripts/life_accountability.py status
```

## Patterns & Correlations

Analyze habits vs outcomes:
```bash
python3 N5/scripts/life_patterns.py correlate workout sleep
python3 N5/scripts/life_patterns.py correlate weed sleep
python3 N5/scripts/life_patterns.py weekly workout
python3 N5/scripts/life_patterns.py report
```

## Visualization

GitHub-style contribution graphs:
```bash
python3 N5/scripts/life_viz.py graph workout --weeks 12
python3 N5/scripts/life_viz.py heatmap
python3 N5/scripts/life_viz.py streak meds
```

## Add New Categories

```bash
python3 N5/scripts/life_counter.py add-category coffee "Coffee" --sentiment neutral
python3 N5/scripts/life_counter.py add-category reading "Reading" --sentiment good
```

## Implementation

- Database: `N5/data/wellness.db` (tables: `life_categories`, `life_logs`)
- CLI: `N5/scripts/life_counter.py`
- Viz: `N5/scripts/life_viz.py`
- Accountability: `N5/scripts/life_accountability.py`
- Patterns: `N5/scripts/life_patterns.py`
- Fitbit bridge: `N5/scripts/fitbit_life_bridge.py`

Always confirm the log with the output from the script.


