---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_OaZwIOzCydglh4r4
---

# Internal Reports

Programmatically generated reports, telemetry, and audit artifacts.

## Structure

```
N5/reports/
├── daily/                  # Daily snapshots
│   ├── tasks/              # Morning briefing + evening accountability
│   │   └── YYYY-MM-DD.md   # One file per day, evening appends to morning
│   ├── bio/                # Bio-log entries (health, food, energy)
│   │   └── YYYY-MM-DD.md
│   └── system/             # System health, errors, service status
│       └── YYYY-MM-DD.md
│
├── weekly/                 # Weekly rollups
│   ├── tasks/              # Week in review: completed, latency, patterns
│   │   └── YYYY-WXX.md
│   └── pulse/              # Build velocity, drop success rates
│       └── YYYY-WXX.md
│
├── telemetry/              # Raw telemetry (machine-readable, append-only)
│   ├── task_events.jsonl   # Task state changes
│   ├── conversation_tags.jsonl  # Action conversation mappings
│   └── build_metrics.jsonl # Pulse build stats
│
└── audits/                 # Point-in-time audits
    ├── positions/          # Position extraction batches
    ├── content-library/    # Content library scans
    └── scheduled-tasks/    # Agent health checks
```

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Daily | `YYYY-MM-DD.md` | `2026-01-26.md` |
| Weekly | `YYYY-WXX.md` | `2026-W04.md` |
| Monthly | `YYYY-MM.md` | `2026-01.md` |
| Telemetry | `*.jsonl` | Append-only, one JSON object per line |

## Report Generators

| Report | Generator | Schedule |
|--------|-----------|----------|
| Morning briefing | `Skills/task-system/scripts/briefing.py morning` | 7am ET |
| Evening accountability | `Skills/task-system/scripts/briefing.py evening` | 9pm ET |
| Weekly task review | TBD | Sunday evening |
| Build metrics | Pulse finalize | Post-build |

## Notes

- Daily task reports: morning creates file, evening appends to same file
- Telemetry files are append-only JSONL (one JSON object per line)
- Old files in this directory (pre-2026-01-26) are legacy and may be cleaned up
