---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_PfLCCUBXvNQYiH3h
---

# Task-System Coupling Pilot Report

## Inputs
1. Promotion events fixture: `file 'N5/test_data/relationship_intelligence/task_coupling_promotion_events.jsonl'`
2. Deliverables fixture: `file 'N5/test_data/relationship_intelligence/task_coupling_deliverable_records.jsonl'`
3. Labels fixture: `file 'N5/test_data/relationship_intelligence/task_coupling_labels.jsonl'`

## Dry-Run Execution Summary
1. Events processed: 3
2. Auto-launch candidates: 1
3. Review-required candidates: 1
4. No-task candidates: 1
5. Errors: 0

Source: `file 'N5/task_system/reports/task_coupling_run_report.json'`

## Pilot Quality Metrics (Labeled)
1. Compared decisions: 3
2. False positives: 0
3. False negatives: 0

Source: `file 'N5/task_system/reports/task_coupling_pilot_report.json'`

## Notes
1. This pilot used dry-run mode to avoid production task mutations.
2. FP/FN are label-dependent and should be recalculated on real production review outcomes.
