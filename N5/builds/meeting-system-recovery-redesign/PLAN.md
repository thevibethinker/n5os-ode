---
created: 2026-03-10
last_edited: 2026-03-10
version: 1
provenance: con_9zO5lFoCncknWVxk
build_slug: meeting-system-recovery-redesign
build_type: system-redesign
---
# PLAN: Meeting System Recovery + Redesign

## Context

The live meeting corpus under `Personal/Meetings/` appears to have been wiped or materially degraded. V provided a backup archive at `file '/home/.z/chat-uploads/Zo Meetings copy-e49d20a9b948.zip'` and wants that zip used as the historical recovery source.

The current meeting system also needs structural redesign, not just restore:
- historical meetings from prior sources should be brought into one normalized fold
- future sources now include Fireflies, Fathom, and Pocket
- Pocket should default to **reflection** unless initial evaluation suggests a meeting signal such as multiple speakers
- inbound items should land in `Personal/Meetings/Inbox/` in a ready-to-process state, or be converted immediately into that state on landing
- after full processing, state should explicitly indicate the meeting is ready to move/archive
- meeting titling needs stronger rules
- the downstream meeting → wisdom/knowledge pipeline needs repair and refinement
- sqlite backups should be updated to reflect the recovered state once restoration is executed

V explicitly asked for a **redesign-optimized** plan, but with **prepare/inspect only** right now. No live restore or code execution should occur until V approves execution.

## Objective

Prepare an execution-ready Pulse build that:
1. recovers the historical meeting corpus from the provided zip
2. reconciles filesystem state and sqlite backup state
3. redesigns the intake contract to normalize Fireflies, Fathom, and Pocket into a single pipeline
4. improves block selection, meeting/reflection routing, title generation, and move-ready state handling
5. repairs the meeting-to-wisdom/knowledge pipeline
6. produces a staged execution plan for V review before any mutation

## Confirmed Decisions

- Recovery source for historical state: provided zip archive
- Optimization preference: system redesign first, not just fastest restore
- Current phase: inspect + plan + prepare only
- Pocket default classification: reflection unless initial evaluation detects meeting signal (e.g. multiple speakers)
- Success criteria: all of the following — historical restore, missing-date boundaries, unified intake contract, improved titling/classification, repaired knowledge pipeline
- External-source backfill (Fireflies/Fathom) should be normalized into the redesigned system, not dumped directly into the old flow
- The reusable system capability should be created as a skill within this same build
- Skill packaging should use an allowlist export model plus simple file-based sentinel conventions
- Real meeting data, sqlite state, source pulls, caches, and logs remain outside the exported skill

## Non-Goals for This Planning Pass

- No restoration into `Personal/Meetings/`
- No mutation of the live meeting pipeline DB
- No external-source bulk pull
- No agent start
- No service restarts

## Open Questions / Trap Doors

- Execution target shape: restore exactly to historical zip layout first, or restore directly into the current canonical layout under `Personal/Meetings/` while preserving lineage?
- SQLite recovery method: filesystem-derived rebuild vs. selective import into existing schema
- Knowledge destination contract: which current knowledge store is authoritative for post-meeting elevation?
- Final exported skill slug and bootstrap companion naming: `meeting-system-recovery`, `meeting-system-capability`, or similar?

## Phase 1

Phase 1 is the non-mutating discovery wave. Its purpose is to establish the factual baseline before redesign or restoration work proceeds.

### Phase 1 goals
- inventory the zip recovery corpus and map restore classes
- audit the current meeting pipeline, filesystem assumptions, and sqlite/state dependencies
- audit the downstream knowledge/wisdom pipeline so redesign decisions improve end-to-end behavior rather than just restoring storage

### Phase 1 outputs
- `N5/builds/meeting-system-recovery-redesign/artifacts/restore-map.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/system-audit.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/knowledge-audit.md`

### Phase 1 exit condition
Phase 1 is complete only when the build has enough evidence to design:
1. the canonical intake contract,
2. the routing/title/move-ready rules,
3. the skill/export/bootstrap boundary,
4. the final execution sequence.

## Build Strategy

### Wave 1 — Forensics + Contract Discovery (parallel)
- D1.1 — Zip corpus inventory and restore mapping
- D1.2 — Current pipeline/code/state audit
- D1.3 — Knowledge pipeline audit

### Wave 2 — Redesign Spec + Skill Boundary (parallel after Wave 1)
- D2.1 — Unified intake contract for Fireflies/Fathom/Pocket
- D2.2 — Classification/title/state rules spec
- D2.3 — Skill packaging boundary, bootstrap contract, and export policy

### Wave 3 — Execution Plan + Build-to-Skill Delivery (sequential synthesis)
- D3.1 — Phased execution plan with safety gates, rollback, sqlite update plan, and skill-creation sequencing

## Execution Principles

- **P35 Version, Don’t Overwrite:** treat zip and existing sqlite DBs as immutable inputs
- **P36 Make State Visible:** every stage declares inputs, outputs, and state transitions
- **P37 Design as Pipelines:** intake → normalize → identify → process → mark move-ready → archive → elevate
- **P38 Isolate & Parallelize:** independent drops for forensics, intake redesign, knowledge audit, and skill-boundary design
- **P39 Audit Everything:** every proposed mutation gets provenance and rollback notes before execution

## Expected Deliverables

- `N5/builds/meeting-system-recovery-redesign/artifacts/restore-map.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/system-audit.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/knowledge-audit.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/intake-contract.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/routing-and-titling-rules.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/skill-packaging-and-export-policy.md`
- `N5/builds/meeting-system-recovery-redesign/artifacts/execution-plan.md`
- `Skills/meeting-system-recovery/` (or final approved slug) as a build output during execution
- `N5/scripts/bootstrap/meetings_system_bootstrap.py` or equivalent bootstrap/setup asset if the build concludes that workspace initialization should live outside the skill

## Success Criteria

- [ ] Zip corpus is inventoried with date coverage and restore classes
- [ ] Current system breakpoints are documented with evidence
- [ ] Unified intake contract covers Fireflies, Fathom, and Pocket
- [ ] Pocket routing rule is codified in the redesign
- [ ] Meeting/reflection routing, block selection, title rules, and move-ready state are specified
- [ ] Knowledge pipeline failure points and redesign are documented
- [ ] Skill boundary between reusable capability and private operating data is specified
- [ ] Allowlist export policy and file-marker conventions are specified
- [ ] Bootstrap/setup contract for new environments is specified
- [ ] SQLite backup update strategy is specified
- [ ] Execution plan is ready for V approval
