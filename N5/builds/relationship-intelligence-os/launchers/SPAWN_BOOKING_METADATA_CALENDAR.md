---
created: 2026-02-16
last_edited: 2026-02-16
version: 1
provenance: con_7IE2POtd4gjTDQxn
---
# Spawn Worker: Booking Metadata + Calendar Skill

## Thread Type
Separate conversation thread (parallel to Pulse core).

## Objective
Build a booking metadata intake and calendar booking flow that captures structured intent for downstream meeting promotion/routing.

## Scope
1. Parse natural-language booking requests into structured metadata:
- `meeting_intent`
- `strategic_importance`
- `expected_outputs`
- `relationship_goal`
- `promotion_bias`
2. Integrate with calendar creation flow.
3. Persist metadata with meeting identity so ingestion can consume it.

## Out of Scope
1. Full task-system execution.
2. Semantic memory promotion implementation.

## Deliverables
1. Spec for booking metadata schema.
2. Parser implementation and validation cases.
3. Calendar integration wiring with examples.
4. Short runbook for usage.

## Success Criteria
1. NL booking messages produce valid structured metadata.
2. Metadata lands in a retrievable location linked to meeting IDs.
3. End-to-end booking test passes with at least 3 representative intents.
