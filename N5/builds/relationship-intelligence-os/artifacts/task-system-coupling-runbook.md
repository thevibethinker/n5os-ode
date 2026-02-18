---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_PfLCCUBXvNQYiH3h
---

# Task-System Coupling Runbook

## 1) Dry-run first (required)

```bash
python3 N5/task_system/promotion_task_coupling.py run \
  --dry-run \
  --promotion-events /home/workspace/N5/data/relationship_intelligence/promotion_events.jsonl \
  --deliverables /home/workspace/N5/data/relationship_intelligence/deliverable_records.jsonl \
  --report-out /home/workspace/N5/task_system/reports/task_coupling_run_report.json
```

## 2) Review run report
1. Confirm `errors = 0`
2. Validate action mix (`auto_launched`, `review_required`, `no_task`)
3. Check policy assumptions before non-dry-run execution

## 3) Rollback switch controls

```bash
# Disable coupling immediately
python3 N5/task_system/promotion_task_coupling.py toggle --state disabled

# Re-enable after validation
python3 N5/task_system/promotion_task_coupling.py toggle --state enabled
```

## 4) Production run (writes enabled)

```bash
python3 N5/task_system/promotion_task_coupling.py run \
  --promotion-events /home/workspace/N5/data/relationship_intelligence/promotion_events.jsonl \
  --deliverables /home/workspace/N5/data/relationship_intelligence/deliverable_records.jsonl \
  --report-out /home/workspace/N5/task_system/reports/task_coupling_run_report.json
```

## 5) Pilot FP/FN report

```bash
python3 N5/task_system/promotion_task_coupling.py pilot-report \
  --labels /home/workspace/N5/test_data/relationship_intelligence/task_coupling_labels.jsonl \
  --output /home/workspace/N5/task_system/reports/task_coupling_pilot_report.json
```

## 6) Idempotency + audit checks
1. `task_coupling_events.idempotency_key` is unique and upserted.
2. Verify no duplicate task creation by rerunning same event batch.
3. Confirm status sync rows exist for each processed event.
