---
created: 2026-02-24
last_edited: 2026-02-24
version: 1.1
build_slug: hotline-data-integrity-upgrade
---

# Plan: Hotline Data Integrity Upgrade

## Objective

Fix hotline data integrity and reporting consistency across Zo hotline, Career coaching hotline, and Zoren hotline by:
1) repairing forward ingestion logic for timestamps/topics,
2) updating dashboard-facing queries to canonical ET rollups from canonical datasets,
3) backfilling historical rows after forward path is fixed,
4) adding validation checks to prevent recurrence.

## Open Questions

- [x] Should backfill run before forward ingestion fixes? (No: run backfill after forward fixes.)
- [x] Should we attach to an existing build? (No: new upgrade build.)
- [x] Should dashboard query updates be included in first pass? (Yes.)

## Success Criteria

- [ ] Forward ingestion writes `ended_at` correctly (not defaulting to `started_at`) in all hotline webhook/call logger paths.
- [ ] Topic defaults are normalized (`general` or service-specific normalized fallback) when classifier output is missing/empty.
- [ ] Dashboard/analytics rollups use ET date logic and canonical hotline datasets (exclude stale `vapi-calls` from primary rollups).
- [ ] Backfill updates historical rows where `ended_at = started_at` and `duration_seconds > 0`.
- [ ] Validation checks pass on all three datasets (no regressions in ID/null/negative checks; expected reduction in zero-span rows).

## Phases

### Phase 1: Forward-Fix + Query-Fix

**Drops:**
- D1.1: Forward ingestion timestamp and topic normalization
- D1.2: Dashboard queries canonical ET rollups

**Gate:** New call writes produce sane timestamps; ET rollups match expected day buckets; canonical source list is explicit in query code/docs.

### Phase 2: Backfill + Validation

**Drops:**
- D2.1: Backfill ended_at and topic defaults
- D2.2: Validation and regression checks

## Affected Files

- `Skills/zoren-hotline/scripts/hotline-webhook.ts`
- `Skills/zoren-hotline/scripts/call-logger.ts`
- `Skills/career-coaching-hotline/scripts/hotline-webhook.ts`
- `Skills/zo-hotline/scripts/hotline-webhook.ts`
- `Skills/zo-hotline/scripts/call-logger.ts`
- `Skills/zo-hotline/scripts/call_analysis_loop.py` (if ET/canonical rollup alignment requires update)
- `N5/scripts` or `Skills/*/scripts` new validation/backfill utility scripts (if needed)
- `N5/builds/hotline-data-integrity-upgrade/deposits/*.json`
- `N5/builds/hotline-data-integrity-upgrade/artifacts/*`

## Risks

- Backfill could overwrite good rows if predicate is too broad.
- Query updates could silently change historical daily counts due to UTC vs ET interpretation.
- Multiple dirty workspace changes increase risk of accidental unrelated edits.
- Large raw payload fields may make validation queries expensive if not scoped.
