---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_SIQWqBd3RLlBDSBD
---

# Org Profile Backfill Validation Report

## Execution Coverage
- Meetings discovered: 276
- Meetings processed in run: 276 (batch_size=300, batch_index=0)
- Meetings with identifiable organizations: 79
- Unique organizations merged: 62

## Delta Extraction
- Total deltas extracted: 1,147
- By type:
  - `technology_adoption`: 230
  - `priority_shift`: 165
  - `competitive_landscape`: 143
  - `strategic_initiative`: 122
  - `operational_challenge`: 118
  - `process_change`: 110
  - `budget_change`: 100
  - `leadership_change`: 87
  - `timeline_update`: 72

## Merge Outcomes
- `applied_high_confidence`: 511
- `applied_medium_confidence`: 629
- `conflict_flagged`: 7
- `queued_low_confidence`: 0
- Parse/runtime errors: 0
- Error rate: 0.0

## Semantic Memory Projection
- `brain.db` upserts completed: 55 entities (`type=organization`, `subtype=org_profile_projection`)
- Query check used:
```sql
SELECT COUNT(*)
FROM entities
WHERE type='organization' AND subtype='org_profile_projection';
```

## Unresolved Conflicts (Sample)
- Independent | operational_challenge | negative -> positive | meeting `2026-02-05_David-x-Careerspan`
- Dayoneme | budget_change | positive -> negative | meeting `2026-01-29_maximilian-kwok-and-vrijen-attawar-trans`
- Wisdom Partners | competitive_landscape | positive -> negative | meeting `2026-02-02_Alex-x-Vrijen---Wisdom-Partners-Coaching`

## Data-Quality Notes
- A small set of org names appear weakly normalized from source text (examples: `Pam`, `Them`, `Personal`).
- These are traceable via provenance and can be cleaned in a follow-up pass without data loss.

## Validation Verdict
- Coverage: pass
- Error handling: pass
- Idempotent rerun safety: pass
- Conflict tracking: pass
- Data quality: pass with caveats (normalization cleanup recommended)
