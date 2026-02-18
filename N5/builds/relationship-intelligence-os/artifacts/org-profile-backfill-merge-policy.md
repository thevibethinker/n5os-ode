---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_SIQWqBd3RLlBDSBD
---

# Org Profile Merge Policy

## Canonical Model
- Canonical store is JSON object keyed by deterministic `org_id`.
- Each profile carries:
  - `delta_history` (append-only evidence records)
  - `latest_by_type` (current accepted state per delta type)
  - `signal_counts` (accepted aggregate counts)
  - `sources` (provenance pointers)
  - `unresolved_conflicts` (requires review)

## Confidence Policy
- `>= 0.75`: `applied_high_confidence`
  - Update `latest_by_type`
  - Increment `signal_counts`
  - Update profile confidence score
- `0.55 - 0.749`: `applied_medium_confidence`
  - Same merge path as high-confidence, lower trust
- `< 0.55`: `queued_low_confidence`
  - Stored in `delta_history` for traceability
  - Not used to update current state summaries

## Conflict Policy
- A conflict is raised when all are true:
  - existing accepted delta for same `delta_type` exists
  - previous and new polarities are both non-neutral
  - polarities are opposite
  - both confidence scores are `>= 0.72`
- Conflict outcome: `conflict_flagged`
  - New delta is retained in history
  - `latest_by_type` is not overwritten
  - conflict is appended to `unresolved_conflicts`

## Idempotency Policy
- Delta IDs are deterministic hash IDs from
  - organization
  - meeting
  - block type
  - delta type
  - evidence excerpt
- Duplicates are skipped via:
  - existing delta IDs in canonical profile (`applied_delta_ids`)
  - existing IDs in append-only delta log (`org_profile_deltas.jsonl`)

## Provenance Policy
- Every delta includes provenance with:
  - source file
  - processor name
  - processing timestamp
- Merge audit log records outcome by delta (`applied`, `conflict_flagged`, `queued`, `duplicate_skipped`).
