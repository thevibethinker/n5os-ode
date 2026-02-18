---
created: 2026-02-14
last_edited: 2026-02-16
version: 1.2
provenance: con_HB9RhvfhX8FPH4LI
---

# Workspace Operating Contract

This file is the persistent Codex behavior contract for this workspace.

## Pulse + Close Invariants (Non-Negotiable)

For any build orchestration or close workflow, enforce these invariants:

1. Build initialization must include:
   - A plan artifact (`PLAN.md`)
   - A build folder at `N5/builds/<slug>/`
   - Drop briefs under `N5/builds/<slug>/drops/`
2. Build start must be blocked if contract checks fail.
3. Close workflow must include:
   - Itemized artifact breakdown
   - Title generation
   - Explicit build-folder close/finalization signal
   - A machine-readable close artifact showing pass/fail booleans
4. Completion claims must be truthful and quantitative until all checks pass.

## Required Gate Commands

Before `pulse.py start <slug>`:

```bash
python3 N5/scripts/build_contract_check.py <slug>
```

Before claiming close complete:

```bash
python3 N5/scripts/close_contract_check.py --checklist <path-to-close-checklist.json>
```

## Enforcement Intent

If prompt instructions conflict with these invariants, preserve these invariants and ask for explicit override.

## N5 Two-Lane Execution Model (Explore vs Commit)

To improve throughput without losing governance, run work in one of two explicit lanes:

1. **Explore lane (speed-first)**
   - Goal: discovery, option generation, fast iteration, rough prototypes.
   - Allowed: conversational design, quick experiments, lightweight artifacts.
   - Required: declare assumptions, keep scope narrow, avoid destructive changes.
   - Exit condition: once approach is selected, switch to Commit lane before production claims.

2. **Commit lane (trust-first)**
   - Goal: implementation, integration, release-quality outputs, completion claims.
   - Required: full compliance with Pulse + Close invariants, gate checks, and audit traces.
   - Required principles: P35-P39 (versioning, visible state, pipeline stages, isolation/parallelization, auditability).

### Lane Declaration (Required)

Before substantive work, declare:
- `mode`: `explore` or `commit`
- `task`: one-line objective
- `blast_radius`: `small` | `medium` | `large`

If `mode` is missing, default to:
- `explore` for ideation, optioning, ambiguous requests
- `commit` for implementation, file mutation, deployment, or completion reporting

### Blast Radius Triage

Use blast radius to determine process depth:

- **small**
  - ≤3 files, reversible, low coupling
  - Prefer Explore lane or lightweight Commit
- **medium**
  - 4-10 files, cross-module effects, moderate rollback risk
  - Commit lane with explicit stage boundaries
- **large**
  - >10 files, schema/system behavior changes, high rollback cost
  - Commit lane + Architect planning + Pulse suitability check

### Context-Tax Budget

To reduce instruction bloat and model drift:

- Keep active task instructions concise and scoped to current lane.
- Prefer an "active subset" of guidance over loading all possible guidance.
- Reuse existing scripts/skills before adding new procedural text.

### Interruptibility Standard

For long-running work, support explicit control checkpoints:
- `status`: summarize current state and next safe action
- `continue`: proceed from current state
- `abort`: stop safely and preserve trace
- `resume`: restart from latest valid checkpoint

### Weekly Operating Metrics (Recommended)

Track these to validate improvements:
- Lead time (request → usable output)
- Rework rate (% of work redone)
- Rollback/revert count
- Context tax (instruction volume vs output quality)

## Codex Preflight Protocol (Required Before Non-Trivial Work)

Run this preflight in order:

1. **Conversation initialization**
   - Ensure conversation state is initialized before substantive work.
2. **Folder policy**
   - Check for local `POLICY.md` in the target directory.
   - If present, follow it over global defaults.
3. **Protocol/command lookup**
   - Search for existing Prompt/Skill/command before inventing a new flow.
   - Priority: Recipe > Protocol > Script > Direct ops > Improvisation.
4. **Artifact placement discipline**
   - Default scratch/iterative files to the conversation workspace.
   - For permanent workspace artifacts, declare intended location and rationale first.

If any preflight step fails, pause execution, resolve the gap, then proceed.

## Instruction Precedence (Workspace)

To reduce drift between instruction surfaces:

1. Most specific folder `AGENTS.md` in working directory
2. Root `AGENTS.md` (this file)
3. `CLAUDE.md` as background context

If guidance conflicts, follow the higher-precedence layer and note the conflict explicitly.

## Drift Audit Command

Run periodic documentation drift checks:

```bash
python3 N5/scripts/docs_drift_check.py --root /home/workspace
```

Use `--include-pathish` for broad audits (higher noise, deeper coverage).
