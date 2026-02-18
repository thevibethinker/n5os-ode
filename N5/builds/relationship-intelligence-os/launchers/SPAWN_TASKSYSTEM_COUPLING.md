---
created: 2026-02-16
last_edited: 2026-02-16
version: 1
provenance: con_7IE2POtd4gjTDQxn
---
# Spawn Worker: Task-System Coupling

## Thread Type
Separate conversation thread (parallel; gated behind core promotion outputs).

## Objective
Design and implement controlled coupling from promoted commitments/deliverables into the task system.

## Scope
1. Define coupling contract from promotion outputs to task candidates.
2. Add policy gates for `auto-launch` vs `review-required`.
3. Wire commitment/deliverable events into task queue creation.
4. Add status sync back into memory/graph context.

## Out of Scope
1. Unrestricted autonomous execution.
2. Social/external outbound actions.

## Deliverables
1. Task coupling schema and policy matrix.
2. Event-to-task mapper implementation.
3. Safety controls and rollback switch.
4. Pilot report on false positives/negatives.

## Success Criteria
1. Explicit promises become task candidates reliably.
2. Low-confidence items are held for review.
3. Task status is visible to orchestrator and downstream consumers.
