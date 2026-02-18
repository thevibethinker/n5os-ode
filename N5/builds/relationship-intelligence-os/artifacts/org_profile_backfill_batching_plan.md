---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_WReQi5kJBhFHraAX
---

# Org Profile Backfill Batching Plan

## Batch Unit
- Primary unit: one `manifest.json` meeting folder under `Personal/Meetings/`.
- Eligible data per meeting: `manifest.json` + `B08_STAKEHOLDER_INTELLIGENCE.md` (fallback `B03_STAKEHOLDER_INTELLIGENCE.md`).

## Default Partitioning
- `batch_size=50` meetings.
- `batch_index=0..N-1` where `N = ceil(total_meetings / batch_size)`.

## Execution Envelope
1. Dry-run first per batch:
   - `python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py --batch-size 50 --batch-index <i> --dry-run`
2. Validate metrics:
   - Coverage should be non-zero.
   - Error rate should stay low and conflicts should be inspectable.
3. Apply batch:
   - `python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py --batch-size 50 --batch-index <i>`

## Suggested Rollout
1. Pilot: batches `0` and `1`.
2. Mid-wave: parallelize remaining batches in 2-4 workers.
3. Final pass: rerun all batch indexes in apply mode (idempotency check; should report mostly `deltas_skipped_existing`).

## Outputs Per Batch
- JSON validation artifact:
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/org-backfill-*.json`
- Rolling pointer:
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/latest_run.json`
