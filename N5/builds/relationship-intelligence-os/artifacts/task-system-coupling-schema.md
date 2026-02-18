---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_PfLCCUBXvNQYiH3h
---

# Task-System Coupling Schema + Policy Matrix

## Coupling Contract (Promotion Output -> Task Candidate)

### Required event fields
1. `event_id` (or `promotion_id`)
2. `source_meeting_id` (or `meeting_id`)
3. `candidate_type`
4. `tier`
5. `score`
6. `status`
7. `confidence.overall` (or numeric `confidence`)

### Optional enrichers
1. `candidate_id` for deliverable lookups
2. `score_breakdown.commitment_clarity`
3. `hard_override.reason` or `hard_overrides[]`
4. `provenance.idempotency_key` (falls back to `event_id`)

## Policy Matrix

| Signal | Decision | Output |
|---|---|---|
| rollback switch disabled | `blocked` | no task action |
| status in deny list (`duplicate`, `blocked`, `archived`) | `no_task` | no task action |
| tier `C` | `no_task` | no task action |
| confidence < `min_confidence` | `review_required` | staged task |
| tier `A` + hard override OR high score+clarity | `auto_launch` | real task in registry |
| score >= `review_min_score` | `review_required` | staged task |
| otherwise | `no_task` | no task action |

Policy source: `file 'N5/config/task_coupling_policy.json'`.

## Output Surfaces
1. Task registry row (auto-launch): `N5/task_system/tasks.db` (`tasks`, `task_events`)
2. Staging row (review-required): `N5/task_system/tasks.db` (`staged_tasks`)
3. Coupling audit row: `N5/task_system/task_coupling.db` (`task_coupling_events`)
4. Status sync row for memory/graph consumers: `N5/task_system/task_coupling.db` (`task_coupling_status_sync`)

## Rollback Switch
1. Canonical switch file: `file 'N5/config/task_coupling_switch.json'`
2. `enabled: false` hard-blocks coupling decisions at policy gate.
