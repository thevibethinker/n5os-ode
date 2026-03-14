---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_SIQWqBd3RLlBDSBD
---

# Org Profile Backfill Runbook (Re-runnable)

## Preconditions
1. Verify source paths exist:
```bash
test -d /home/workspace/Personal/Meetings
test -f /home/workspace/N5/cognition/brain.db
```
2. Verify script is executable:
```bash
python3 -m py_compile /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py
```

## Step 1: Dry Run
```bash
python3 /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 100 \
  --batch-index 0 \
  --dry-run
```

## Step 2: Apply Batch
```bash
python3 /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 100 \
  --batch-index 0 \
  --project-semantic-memory
```

## Step 3: Complete Remaining Batches
```bash
for i in 1 2; do
  python3 /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
    --batch-size 100 \
    --batch-index "$i" \
    --project-semantic-memory
 done
```

## Step 4: Verify Outputs
```bash
ls -lh \
  /home/workspace/N5/data/org_profiles_canonical.json \
  /home/workspace/N5/data/org_profile_deltas.jsonl \
  /home/workspace/N5/data/org_profile_merge_audit.jsonl \
  /home/workspace/N5/data/org_profile_semantic_projection.jsonl \
  /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org-profile-backfill-validation-report.json

sqlite3 /home/workspace/N5/cognition/brain.db \
  "SELECT COUNT(*) FROM entities WHERE type='organization' AND subtype='org_profile_projection';"
```

## Recovery / Re-run
- Re-running the same batch is safe:
  - deterministic delta IDs prevent duplicate writes
  - canonical merge is idempotent by `applied_delta_ids`
  - append logs skip known IDs
- For strict fail-fast mode:
```bash
python3 /home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 100 --batch-index 0 --strict --project-semantic-memory
```
