---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_SIQWqBd3RLlBDSBD
---

# Org Profile Backfill Execution Script + Batching Plan

## Script
- Path: `/home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py`
- Supports:
  - `--dry-run` (no writes)
  - `--batch-size` + `--batch-index` (deterministic slices)
  - `--project-semantic-memory` (upsert into `brain.db` entities)
  - `--strict` (fail fast on parse errors)

## Deterministic Batch Selection
- Meetings are discovered and sorted lexicographically.
- Batch window:
  - `start = batch_index * batch_size`
  - `end = start + batch_size`
  - selected meetings = `meeting_dirs[start:end]`

## Recommended Plan For Current Corpus
- Discovery count observed: 276 meeting directories with relevant blocks.
- Recommended execution plan:
  1. Batch 0: `--batch-size 100 --batch-index 0`
  2. Batch 1: `--batch-size 100 --batch-index 1`
  3. Batch 2: `--batch-size 100 --batch-index 2`
- Reason: keeps each write unit small enough for reruns/recovery, while finishing in three passes.

## Commands
```bash
# 1) Safety check (no writes)
python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 100 --batch-index 0 --dry-run

# 2) Execute one batch with semantic projection
python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 100 --batch-index 0 --project-semantic-memory

# 3) Execute all batches sequentially
for i in 0 1 2; do
  python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
    --batch-size 100 --batch-index "$i" --project-semantic-memory
 done
```

## Produced Stores
- Canonical org profiles: `/home/workspace/N5/data/org_profiles_canonical.json`
- Delta log: `/home/workspace/N5/data/org_profile_deltas.jsonl`
- Merge audit log: `/home/workspace/N5/data/org_profile_merge_audit.jsonl`
- Semantic projection feed: `/home/workspace/N5/data/org_profile_semantic_projection.jsonl`
- Run validation report: `/home/workspace/N5/builds/relationship-intelligence-os/artifacts/org-profile-backfill-validation-report.json`
