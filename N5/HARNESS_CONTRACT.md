---
created: 2026-04-23
last_edited: 2026-04-23
version: 1.0
provenance: con_jL5x88AR1IB8Mvab
---

# N5 Harness Contract

This file is the shared operating contract for Zo, Claude Code, and Codex.

Use it as the cross-harness source of truth for how to work inside this workspace.

## Design Goal
Preserve capability. Reduce always-on context.

The system should keep the same operational quality while loading only the guidance relevant to the current lane.

## Shared Load Order
For non-trivial work, load in this order:

1. `WORKSPACE_MAP.md` — fast routing
2. `AGENTS.md` — shared workspace constitution
3. `N5/SESSION_STATE_POLICY.md` — decide whether session state is required
4. Specialized protocol, skill, or local project docs only if the task needs them

Do not load the full manual by default.

## Lane Model
Declare the current lane before substantive work:
- `explore` — ideation, optioning, ambiguous research, lightweight reasoning
- `commit` — implementation, file mutation, deployment, close claims, irreversible changes

Also declare blast radius:
- `small` — 3 files or fewer, reversible, low coupling
- `medium` — 4-10 files, cross-module effects
- `large` — more than 10 files or higher rollback cost

## Shared Defaults
- Prefer the smallest doc set that safely fits the task
- Use workspace docs as source of truth, not the global rule layer
- Prefer existing `Recipe > Protocol > Script > Direct ops > Improvisation`
- Keep scratch in the conversation workspace by default
- Declare permanent artifact placement before writing workspace files
- Verify missing commands or docs before inventing replacement flows
- For multi-file shared-code work in `N5/`, `Skills/`, `Prompts/`, or `Integrations/`, run dependency review before edits

## Required Invariants

### Safety and honesty
- Do not hallucinate
- Do not externally send, publish, or commit on behalf of V without explicit permission
- Report progress honestly; do not claim complete before checks pass

### Placement and hygiene
- Follow `POLICY.md` and the most specific local `POLICY.md`
- Treat `Sites/` as canonical for site-shaped projects
- Route research working artifacts to `Research/`
- Follow canonical meeting storage under `Personal/Meetings/`
- Use `Documents/System/Maintainer-Playbook.md` for cleanup, git hygiene, ignore/protection alignment, and commit-boundary decisions

### Build and close invariants
- Preserve Pulse and close contract checks
- Do not bypass build/close invariants just because docs are being slimmed
- Use the appropriate skill/protocol when entering build, close, or drop workflows
- Run Maintainer checkpoints after plan/init, after meaningful build waves, and during close/finalization when the worktree has materially changed

## When to Load Specialized Guidance

### Build / orchestration
Load `Skills/pulse/SKILL.md`

### Cleanup / git / commit hygiene
Load `Documents/System/Maintainer-Playbook.md`

### Repeated bugs / second-principles debugging
Load `Skills/systematic-debugging/SKILL.md`

### Debug logging
If `DEBUG_LOG.jsonl` exists, load `N5/prefs/operations/debug-logging-auto-behavior.md`

### Sites / web apps
Load local site docs and staging conventions under `Sites/`

### Research
Use `N5/scripts/research_router.py` and work under `Research/`

### Agent management
Use conflict-gate workflow before create/reactivate/delete/significant edits

## Adapter Rule
Harness adapters should stay thin.

They may add:
- harness-specific mechanics
- harness-specific session tooling
- harness-specific shortcuts

They should not duplicate:
- workspace constitution
- map/index content
- session-state policy
- large operational manuals

## Migration Intent
This contract intentionally relocates high-frequency guidance out of always-on prompt space and into shared docs. If behavior appears to drift, fix the shared docs or adapters rather than re-expanding the global rule layer.
