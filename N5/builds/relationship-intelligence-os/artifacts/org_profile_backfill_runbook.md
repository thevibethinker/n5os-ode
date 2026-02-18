---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_WReQi5kJBhFHraAX
---

# Org Profile Backfill Runbook (Re-runnable)

## Preconditions
1. Confirm databases exist:
   - `N5/data/n5_core.db`
   - `N5/cognition/brain.db`
2. Confirm meetings corpus exists:
   - `Personal/Meetings/`

## Command Interface
- Script:
  - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py`

### Pilot Dry-Run
```bash
python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 50 \
  --batch-index 0 \
  --dry-run
```

### Apply Batch
```bash
python3 N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py \
  --batch-size 50 \
  --batch-index 0
```

### Full Sweep (Sequential)
```bash
python3 - <<'PY'
import json, math, subprocess
from pathlib import Path

meetings = sorted(Path("/home/workspace/Personal/Meetings").rglob("manifest.json"))
batch_size = 50
batch_count = math.ceil(len(meetings) / batch_size)
for idx in range(batch_count):
    cmd = [
        "python3",
        "/home/workspace/N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill.py",
        "--batch-size", str(batch_size),
        "--batch-index", str(idx),
    ]
    print("Running", " ".join(cmd))
    subprocess.run(cmd, check=True)
PY
```

## Validation Artifacts
1. Latest run summary:
   - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/latest_run.json`
2. Historical run snapshots:
   - `N5/builds/relationship-intelligence-os/artifacts/org_profile_backfill_output/org-backfill-*.json`

## Re-run Safety
1. Re-running same batch is safe (delta key dedupe).
2. Expected re-run behavior:
   - `deltas_skipped_existing` increases.
   - `deltas_accepted` trends toward 0 unless source content changed.
