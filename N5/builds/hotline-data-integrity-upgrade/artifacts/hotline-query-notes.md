---
created: 2026-02-24
last_edited: 2026-02-24
version: 1.0
provenance: con_fPuAgpiUmlslxLrR
---

# Hotline Query Notes

## Canonical Sources
- `Datasets/zo-hotline-calls/data.duckdb`
- `Datasets/career-hotline-calls/data.duckdb`
- `Datasets/vibe-pill-calls/data.duckdb`

## Excluded Source
- `Datasets/vapi-calls/data.duckdb` (stale archival dataset, not used for default dashboard totals)

## Timezone Contract
- Default day bucket = ET via `CAST(started_at - INTERVAL 5 HOUR AS DATE)` for current period.
- UTC day rollups may still be useful for forensic checks, but not for default dashboard totals.

## Intended Consumer
- Any dashboard/report code that needs consolidated hotline metrics should use
  `N5/scripts/hotline_dashboard_rollup.py` or equivalent SQL in this artifact.
