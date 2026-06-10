---
created: 2026-02-14
last_edited: 2026-05-15
version: 1.4
provenance: con_YF002L3W3z7S7uD5
---

# Workspace Operating Contract

This file is the canonical, tool-agnostic operating contract for `/home/workspace`.

## Role Split

- `AGENTS.md` is the shared workspace constitution.
- `WORKSPACE_MAP.md` is the fast navigation index for where things live and which docs to load first.
- `POLICY.md` governs folder placement and root hygiene.
- `N5/HARNESS_CONTRACT.md` is the shared cross-harness operating contract.
- `N5/SESSION_STATE_POLICY.md` governs when conversation-local session state is required, optional, or skipped.
- `N5/prefs/system/rule-governance.md` governs when behavior belongs in global rules versus skills, folder contracts, or prefs.
- Tool-specific files such as `CLAUDE.md` and `CODEX.md` are thin adapters. They should inherit this contract and add only tool-specific deltas.
- If an adapter starts re-stating the full workspace manual, slim the adapter instead of expanding this file.

## Pulse + Close Invariants (Non-Negotiable)

For any build orchestration or close workflow, enforce these invariants:

1. Build initialization must include:
   - a plan artifact (`PLAN.md`)
   - a build folder at `N5/builds/<slug>/`
   - drop briefs under `N5/builds/<slug>/drops/`
2. Build start must be blocked if contract checks fail.
3. Close workflow must include:
   - itemized artifact breakdown
   - title generation
   - explicit build-folder close or finalization signal
   - a machine-readable close artifact with pass/fail booleans
4. Completion claims must remain truthful and quantitative until all checks pass.

## Required Gate Commands

Before `pulse.py start <slug>`:

```bash
python3 N5/scripts/build_contract_check.py <slug>
```

Before claiming close complete:

```bash
python3 N5/scripts/close_contract_check.py --checklist <path-to-close-checklist.json>
```

If higher-level prompt instructions conflict with these invariants, preserve the invariants and ask for an explicit override.

## Operating Defaults

### Git / GitHub Action Announcements

Before creating, switching, deleting, merging, rebasing, force-pushing, pushing, opening pull requests, creating/removing worktrees, or otherwise changing branch/worktree/remote state, briefly announce:

- the exact action
- the target branch, worktree, remote, or pull request
- whether it mutates local state, GitHub state, or both

If the action is destructive, forceful, ambiguous, or not already authorized by the current request, stop and ask for explicit confirmation. If the action is already authorized, announce it and proceed.

### Feature Branch Policy

Use `main` as the default operator base. A branch is a separate development storyline, not a task label.

Create or keep a feature branch only when work changes shared source, runtime behavior, `Sites/`, deployed skills, public/canonical outputs, schema/data contracts, or anything risky enough to need isolated review. Use a separate worktree only when two active code branches must be worked on in parallel.

Do not create a branch merely because a Pulse build, research task, planning folder, strategy memo candidate, meeting artifact, or isolated build record exists. Those may be committed directly to `main` when they are durable, low-risk, and self-contained.

Before creating or switching branches/worktrees for non-trivial work, run:

```bash
python3 N5/scripts/n5_git_context_check.py --intent "<short intent>"
```

Treat the result as:

- `main-ok`: stay on `main`; no new branch/worktree
- `branch-required`: create or use a scoped feature branch
- `worktree-required`: create or use a separate worktree for concurrent branch work
- `blocked`: stop and resolve dirty state, branch mismatch, or missing context before proceeding

If the checker warns but the work is explicitly authorized, record why in the commit message or build/status note.

Every remote feature branch should have one of these dispositions:

- `active`: ongoing work that should remain on GitHub
- `pr-review`: open or create a PR, then merge/close deliberately
- `cherry-pick`: extract useful commits, then delete the branch
- `archive/delete`: obsolete, duplicate, stale, or superseded

Before deleting remote branches, produce a disposition table with evidence and wait for approval unless V has already explicitly authorized that deletion batch.

### Lane Declaration (Required)

Before substantive work, declare:

- `mode`: `explore` or `commit`
- `task`: one-line objective
- `blast_radius`: `small` | `medium` | `large`

Default behavior:

- `explore` for ideation, optioning, or ambiguous requests
- `commit` for implementation, file mutation, deployment, or completion reporting

### Blast Radius Triage

- `small`: 3 files or fewer, reversible, low coupling
- `medium`: 4-10 files, cross-module effects, moderate rollback risk
- `large`: more than 10 files, schema or system behavior changes, high rollback cost

Use Pulse or explicit staged execution for large decomposable work.

### Working Defaults

- Use `WORKSPACE_MAP.md` first for rapid navigation, then load deeper docs only as the task requires.
- Use the conversation-local `SESSION_STATE.md` in `/home/.z/workspaces/<convo-id>/`, not the root `SESSION_STATE.md`, as the live record for an active thread when the current lane or workflow requires session state per `N5/SESSION_STATE_POLICY.md`.
- Check the most specific available `POLICY.md` when placement or folder hygiene matters.
- For rule creation, deletion, or migration, classify the behavior with `N5/prefs/system/rule-governance.md`; keep global rules as universal guardrails or thin routers, not procedural manuals.
- Prefer existing `Recipe > Protocol > Script > Direct ops > Improvisation`.
- Keep scratch and iterative artifacts in the conversation workspace by default.
- Declare the intended location and rationale before creating permanent workspace artifacts.
- When a documented command, path, or script entrypoint is missing, verify the live surface before proceeding. Do not silently invent replacement flows.

### Interruptibility

Longer work should support:

- `status`: summarize current state and next safe action
- `continue`: proceed from current state
- `abort`: stop safely and preserve trace
- `resume`: restart from the latest valid checkpoint

## Preflight Protocol (Required Before Non-Trivial Work)

Run this preflight in order:

1. Workspace map
   - check `WORKSPACE_MAP.md` for the fastest route to relevant docs, folders, and systems
2. Session-state decision
   - follow `N5/SESSION_STATE_POLICY.md` to decide whether to initialize, refresh, or skip conversation-local session state
3. Folder policy
   - check for the most specific local `POLICY.md`
4. Protocol or command lookup
   - search for an existing recipe, protocol, skill, script, or command before inventing a new flow
5. Artifact placement discipline
   - keep scratch in the conversation workspace
   - declare permanent workspace writes before creating them
6. Drift check
   - if a referenced command or path is missing, treat that as documentation drift and correct or note it before reusing the flow

If any preflight step fails, pause execution, resolve the gap, then proceed.

## Precedence

Operating behavior:

1. Most specific local `AGENTS.md`
2. Root `AGENTS.md` (this file)
3. Tool-specific adapters such as `CLAUDE.md`

Placement and workspace hygiene:

1. Most specific local `POLICY.md`
2. Root `POLICY.md`

If guidance conflicts, follow the more specific file and note the conflict explicitly.

## Context-Tax Budget

- Keep active instructions concise and scoped to the current lane.
- Prefer short checklists over narrative process where possible.
- Push tool-specific mechanics into adapters or scripts, not the shared workspace constitution.
- Reuse existing scripts and skills before adding new procedural text.

## Drift Maintenance

Run periodic documentation drift checks:

```bash
python3 N5/scripts/docs_drift_check.py --root /home/workspace
```

Use `--include-pathish` for broader audits with higher noise.

When drift is found, fix the documentation, not just the current run.

## Decommission Log

| Date | System | Action | Details |
|------|--------|--------|---------|
| 2026-04-06 | Career Coaching Hotline (Zozie) | Decommissioned | Skill archived to `Skills/.backups/career-coaching-hotline.20260406`; services `svc_iFdW0qpSJ1M` (vapi-webhook) and `svc_tGg4_CHnM20` (career-intake-webhook) deleted; ports 4242, 8848, 8849 freed; replaced by Zoren email assistant |
