---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_WReQi5kJBhFHraAX
---

# Org Profile Backfill Merge Policy

## Non-Destructive Canonical Strategy
- Canonical merge target: `org_profile_canonical` table in `N5/data/n5_core.db`.
- Raw extraction target: `org_profile_observations` table in `N5/data/n5_core.db`.
- Existing `organizations` table is not overwritten by this backfill.

## Idempotency
- Observation identity key: `delta_key = sha1(meeting_id + org_slug + stakeholder_digest)`.
- `org_profile_observations.delta_key` is a primary key.
- Re-runs skip existing keys and preserve prior merges.

## Confidence Handling
- Minimum confidence gate: `0.58` default (`--min-confidence` configurable).
- Candidate confidence precedence:
  1. `manifest.crm_enrichment.participant_matches.company` (highest)
  2. explicit organization field/table in stakeholder block
  3. inline mention heuristic (lowest)
- Canonical confidence update: weighted running average by merged observation count.

## Conflict Handling
- Backfill does not hard-delete or replace prior profile facts.
- Conflicts are flagged to validation output when:
  - many organizations are detected in one meeting (review signal),
  - extraction fails for a meeting.
- Conflicts are surfaced as unresolved review items in run JSON.

## Semantic Memory Projection
- Projection target: `org_memory_profiles` table in `N5/cognition/brain.db`.
- Projection is compact summary + structured payload for retrieval.
- Projection upserts by `org_slug` and tracks `source_version` per run.
