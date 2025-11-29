---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Productivity Tracker / RPI System v1

```yaml
capability_id: productivity-tracker-v1
name: "Productivity Tracker – Relative Productivity Index & XP System"
category: internal
status: active
confidence: high
last_verified: 2025-11-29
tags:
  - productivity
  - email
  - calendar
  - metrics
entry_points:
  - type: script
    id: "N5/scripts/productivity/rpi_calculator.py"
  - type: script
    id: "N5/scripts/productivity/email_scanner.py"
  - type: script
    id: "N5/scripts/productivity/meeting_scanner.py"
  - type: script
    id: "N5/scripts/productivity/xp_system.py"
owner: "V"
```

## What This Does

The productivity tracker computes a **Relative Productivity Index (RPI)** and associated XP/streak metrics by combining email output and meeting load. It provides daily stats, streaks, and tiers (e.g. "Invincible Form") to quantify how well V is performing relative to expected communication volume.

It owns the `productivity_tracker.db` database and the scripts that populate email/meeting tables and derive daily rollups.

## How to Use It

### Ad-hoc queries

From `/home/workspace`:

```bash
# Calculate today’s RPI
python3 N5/scripts/productivity/rpi_calculator.py

# Specific date
python3 N5/scripts/productivity/rpi_calculator.py --date 2025-10-26

# Backfill expectations for historical data
python3 N5/scripts/productivity/rpi_calculator.py --backfill --dry-run
python3 N5/scripts/productivity/rpi_calculator.py --backfill

# Recalculate all historical RPI
python3 N5/scripts/productivity/rpi_calculator.py --recalculate --dry-run
python3 N5/scripts/productivity/rpi_calculator.py --recalculate
```

### Scheduled operation

Typical cron or Zo scheduled task:

```bash
0 23 * * * cd /home/workspace && python3 N5/scripts/productivity/rpi_calculator.py
```

This ensures `daily_stats` stays current and streaks/levels update nightly.

## Associated Files & Assets

### Databases

- `file 'N5/data/productivity_tracker.db'` – Primary SQLite DB for this system.

Key tables:

- `sent_emails` – Email output tracking per day.
- `expected_load` – Expected email volume derived from meeting hours.
- `xp_ledger` – XP transactions.
- `daily_stats` – Aggregated RPI, XP, level, streaks (SSOT for reporting).

### Scripts

- `file 'N5/scripts/productivity/README.md'` – Canonical system design and operational documentation.
- `file 'N5/scripts/productivity/db_setup.py'` – Initializes schema.
- `file 'N5/scripts/productivity/email_scanner.py'` / `email_scanner_v2.py` – Ingests sent‑email counts from Gmail (via Zo tools when wired).
- `file 'N5/scripts/productivity/meeting_scanner.py'` / `meeting_scanner_integrated.py` – Computes expected load from calendar.
- `file 'N5/scripts/productivity/xp_system.py'` – XP and level logic.
- `file 'N5/scripts/productivity/rpi_calculator.py'` – Core RPI computation and rollup script.

## Workflow

### Data flow

```mermaid
flowchart TD
  A[Gmail
  - sent emails] --> B[email_scanner.py
  → sent_emails]

  C[Google Calendar
  - meeting hours] --> D[meeting_scanner.py
  → expected_load]

  B --> E[xp_system.py
  - XP ledger]
  D --> E

  E --> F[rpi_calculator.py
  - daily_stats (RPI, XP, streaks, tiers)]

  F --> G[Dashboards / manual SQL
  - performance insight]
```

### Interpreting RPI

From `file 'N5/scripts/productivity/README.md'`:

- `RPI = (actual_emails / expected_emails) × 100`, where `expected_emails = (meeting_hours × 3) + 5`.
- Tiered ranges (e.g. ≥150% = "Invincible Form"; 100–125% = "Meeting Expectations").

The system also tracks streaks (consecutive days with sufficient output) and levels based on cumulative XP (square‑root progression).

## Notes / Gotchas

- **Source integrations:** Gmail and Calendar ingestion rely on Zo integrations wired into the scanners; until those are fully active, data quality will depend on whatever import path is currently configured.
- **Backfill is powerful.** Backfilling or recalculating can rewrite a large portion of history; dry‑run first and consider snapshotting the DB before large operations.
- **Database locks:** As with all SQLite systems, concurrent writes can cause locks. If you see `database is locked`, stop other processes and retry after a short delay.

