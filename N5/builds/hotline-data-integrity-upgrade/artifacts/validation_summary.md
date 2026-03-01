---
created: 2026-02-24
last_edited: 2026-02-24
version: 1.0
provenance: con_fPuAgpiUmlslxLrR
---

# Validation Summary

## Outcome
- Overall validation: **PASS**
- Canonical datasets checked:
  - `Datasets/zo-hotline-calls/data.duckdb`
  - `Datasets/career-hotline-calls/data.duckdb`
  - `Datasets/vibe-pill-calls/data.duckdb`
- Excluded from canonical dashboard totals:
  - `Datasets/vapi-calls/data.duckdb`

## Key Results
- Zero-span timestamp anomaly (`ended_at = started_at` with non-zero duration) reduced to **0** in Zo and Career datasets.
- Null/blank topics reduced to **0** in Career dataset.
- No duplicate-ID/null-start/negative-duration/reversed-time regressions introduced.
- ET rollup query path is available and produces non-empty output.

## Artifact Pointers
- Machine-readable report: `artifacts/validation_report.json`
- Query set: `artifacts/validation_queries.sql`
- Dashboard rollup output: `artifacts/hotline_dashboard_rollup.json`
- Backfill reports:
  - `artifacts/hotline_backfill_report_dryrun.json`
  - `artifacts/hotline_backfill_report_apply.json`
