---
created: 2026-06-10
last_edited: 2026-06-10
version: 1.0
provenance: con_sQ03t9FFBWIVZTXO
---

# MECE Worker Framework

Use this framework when decomposing Pulse builds into Drops.

## Goal

Drops should be mutually exclusive and collectively exhaustive enough that workers can execute independently without hidden overlap or missing integration work.

## Decomposition Rules

1. Split by ownership boundary first: module, surface, data contract, workflow, or artifact.
2. Keep each Drop independently testable.
3. Name shared files and interfaces explicitly in every affected brief.
4. Put integration, reconciliation, and final validation in their own Drops when multiple workers touch related behavior.
5. Avoid two parallel Drops writing the same source file unless one is explicitly sequencing after the other.

## Drop Brief Checklist

- Objective is one sentence.
- Inputs and authoritative files are listed.
- Non-goals are explicit.
- Success criteria include executable checks or concrete review criteria.
- Dependencies on other Drops are named.
- Collision risks are named.
- Deposit path and required fields are specified.

## Red Flags

- "Clean up everything" as a worker task.
- Broad component ownership without file boundaries.
- Parallel Drops editing the same contract or schema.
- No integration Drop after multiple implementation Drops.
- Success criteria that require the orchestrator to guess what "good" means.
