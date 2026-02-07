---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_JVzbW0S6LreS3vRW
---

# "Where's V" Revamp & Cleanup Plan

## Objective
Consolidate the fragmented "Where's V" build artifacts into a clean, essential core under `Sites/wheres-v` and prepare for a revamp.

## Checklist
- [ ] Phase 1: Environment Safety & Prep
- [ ] Phase 2: Consolidate Essential Logic
- [ ] Phase 3: Consolidate Essential Data
- [ ] Phase 4: Purge Litter (Inbox cleanup)
- [ ] Phase 5: Verification & Transition

## Phase 1: Environment Safety & Prep
- Affected Files: N/A (Directory creation)
- [ ] Create `Sites/wheres-v-staging` as the new canonical home.
- [ ] Verify `.n5protected` status.

## Phase 2: Consolidate Essential Logic
- Affected Files: `Sites/wheres-v-staging/*`
- [ ] Copy the most complete codebase from `Inbox/20251116-095237_Archives/wheres-v-archived-20251115/`.
- [ ] Strip `node_modules` and unnecessary backups from the target.
- [ ] Audit `package.json` and `zosite.json`.

## Phase 3: Consolidate Essential Data
- Affected Files: `Sites/wheres-v-staging/data/trips.jsonl`
- [ ] Identify the most recent `trips.jsonl` (from `Inbox/20251112-093605_wheresv2-data`).
- [ ] Move into `Sites/wheres-v-staging/data/`.

## Phase 4: Purge Litter
- [ ] Delete redundant Inbox folders after confirmation:
    - `Inbox/20251112-093605_wheresv2-data`
    - `Inbox/20251110-093321_wheresv-data`
    - `Inbox/20251112-093606_wheresv2`
    - `Inbox/20251112-094024_wheresv`
    - `Inbox/20251110-093321_wheresv`

## Phase 5: Verification & Transition
- [ ] Ensure the app builds/starts in the new location.
- [ ] Hand off to Architect for revamp strategy.

