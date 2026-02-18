---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_7IE2POtd4gjTDQxn
---

# Relationship Intelligence OS - Execution Plan

## Objective
Ship a unified intelligence pipeline that converts meetings into durable, high-signal memory and action scaffolding across:
- semantic memory (`brain.db`)
- relationship graph (people/org/idea/commitment edges)
- CRM/profile projections
- deliverables intelligence (dedupe, reuse, launcher prompts)

## Success Criteria
1. Post-`tick` promotion stage exists and is idempotent.
2. Promotion gate applies meeting-level + item-level scoring and assigns Tier A/B/C.
3. CRM people + org summaries are projected into semantic memory without replacing CRM as canonical source.
4. Graph edges are written for relationship evolution, mutuals, intro paths, commitments, and org intelligence.
5. Deliverables database tracks promises/requests and prevents duplicate work via similarity routing.
6. Downstream consumers can use promoted data for email/blurb generation and deliverable launcher prompts.
7. System runs with low manual load: auto-promote A, queue B digest, archive C.

## Core Design Decisions (Locked)
1. Canonical source: CRM/profile stores remain source of truth; semantic memory stores compact retrieval representation + deltas.
2. Block policy:
- Always blocks: recap, commitments/actions, decisions, stakeholder intelligence, metadata.
- Conditional blocks: generated only when downstream consumer exists or trigger condition is met.
3. Promotion policy:
- Tier A (75-100): auto-promote.
- Tier B (50-74): review digest.
- Tier C (<50): archive only.
- Hard overrides auto-promote explicit promises, intros, and named deliverables.
4. Writer policy: single promotion writer path to `brain.db` + graph to avoid split-brain writes.

## Scoring Rubric (0-100)
1. Strategic importance: 0-20
2. Relationship delta strength: 0-20
3. Commitment clarity (owner/date/scope): 0-20
4. Evidence quality: 0-15
5. Novelty vs existing memory: 0-15
6. Execution value: 0-10

## Data Products
1. `relationship_delta`
- person/org deltas, relationship trend, confidence, evidence, provenance.
2. `org_delta`
- org priorities, constraints, buying process shifts, strategic signals.
3. `deliverable_record`
- client-scoped deliverable metadata, status, due owner, source context.
4. `intro_opportunity`
- mutual paths, intro intent, confidence, recommended action.
5. `promotion_event`
- typed memory candidate, score, tier, dedupe result, write status.

## Workstream Partitioning
### In this Pulse build (code + pipeline core)
1. Promotion gating + scoring engine.
2. B08/B03/B02_B05/B32/B33 extraction into typed deltas.
3. CRM profile projection to semantic memory.
4. Graph edge write integration.
5. Deliverables intelligence DB + similarity router.
6. Downstream consumer contracts for email/blurb/launcher.

### Separate spawn-worker conversations (parallel but distinct)
1. Booking metadata + calendar capture skill (Zo app integration heavy).
2. Task-system auto-launch/fulfillment coupling (policy-heavy; phase after promotion stabilizes).
3. Org-profile enrichment at scale backfill (bulk run + monitoring wave).

## Wave Plan
### Wave 1 - Contracts + Gate
- Define schemas for promotion events, relationship/org deltas, deliverables.
- Implement scorer + tiering + hard override logic.
- Add idempotency keys and dry-run audit mode.

### Wave 2 - Memory + Graph
- Add CRM/person projection into memory entities + summary blocks.
- Build relationship/org delta extractors from selected blocks.
- Integrate graph writer for people/org/idea/commitment edges.

### Wave 3 - Deliverables Intelligence
- Implement deliverables DB with client scoping and lifecycle states.
- Add similarity router (`reuse|adapt|new`) against prior deliverables and conversation references.
- Emit launcher prompt bundles for new/adapt routes.

### Wave 4 - Consumers + Rollout
- Wire downstream consumers (email/blurb/launcher prefill).
- Run pilot on recent meetings, calibrate thresholds.
- Enable production mode with digest queue and observability metrics.

## Pulse Drop Map
- D1.1: Data contracts and storage schema
- D1.2: Promotion scorer and gating engine
- D1.3: Pipeline hook integration (post-`tick` promotion writer)
- D2.1: CRM profile projection (people/org)
- D2.2: Relationship and org delta extraction
- D2.3: Graph writer integration + edge taxonomy
- D3.1: Deliverables DB + client ID model + similarity routing
- D3.2: Downstream consumer interfaces (email/blurb/launcher)
- D4.1: Pilot, threshold tuning, and operational runbook

## Launch Order
1. Build contract check
```bash
python3 N5/scripts/build_contract_check.py relationship-intelligence-os
```
2. Start Pulse
```bash
python3 Skills/pulse/scripts/pulse.py start relationship-intelligence-os
```
3. Monitor until Wave 4 complete, then finalize
```bash
python3 Skills/pulse/scripts/pulse.py finalize relationship-intelligence-os
```

## Risks and Controls
1. Over-promotion noise -> strict scoring + hard evidence requirement.
2. Duplicate/conflicting memory writes -> single writer path + idempotency.
3. Graph drift/edge spam -> edge confidence threshold + limited relation vocab.
4. Deliverable explosion -> similarity router + client-level dedupe + status lifecycle.

## Out of Scope for this Build
1. Full autonomous task execution from commitments.
2. Full calendar booking assistant UI/skill deployment.
3. Social posting or external messaging automations.
