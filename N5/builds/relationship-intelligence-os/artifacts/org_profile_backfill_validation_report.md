---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_WReQi5kJBhFHraAX
---

# Org Profile Backfill Validation Report

## Primary Execution (Apply)
- Source validation JSON: `N5/builds/relationship-intelligence-os/artifacts/org-profile-backfill-validation-report.json`
- Meetings discovered: `276`
- Meetings processed in batch: `276` (single full sweep, `batch_size=300`)
- Meetings with org matches: `79`
- Unique orgs enriched: `62`
- Deltas extracted: `1,147`
- Merge outcomes:
  - `applied_high_confidence`: `511`
  - `applied_medium_confidence`: `629`
  - `conflict_flagged`: `7`
- Unresolved conflicts: `7` (`2.54%` of meetings in batch)
- Parse/runtime errors: `0` (`0.00%`)
- Semantic projections upserted: `55`

## Artifact Integrity Checks
- Canonical profiles file:
  - `N5/data/org_profiles_canonical.json` contains `62` org profile objects.
- Delta log:
  - `N5/data/org_profile_deltas.jsonl` contains `1,147` rows.
- Merge audit log:
  - `N5/data/org_profile_merge_audit.jsonl` contains `1,147` rows.
- Projection log:
  - `N5/data/org_profile_semantic_projection.jsonl` contains `55` rows.
- Semantic memory DB:
  - `brain.db` entities tagged with `metadata.projection_type='org_profile_backfill'`: `55`.

## Idempotency Validation (Re-run Sweep)
- Command pattern: re-run full corpus in 6 batches (`batch_size=50`, `batch_index=0..5`) with apply mode.
- Batch reports:
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch0.json`
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch1.json`
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch2.json`
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch3.json`
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch4.json`
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/apply_batch5.json`
- Aggregated idempotency summary:
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/idempotency_sweep_summary.json`
  - Meetings scanned across re-run: `276`
  - Deltas extracted on re-run: `0`
  - Errors: `0`
  - Result: idempotency observed (`true`).
