---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
name: Planning System v1 – Architect-Owned Build Planning
category: internal
status: active
---

# Planning System v1 – Architect-Owned Build Planning

## Summary

Planning System v1 makes **AI-executable build plans mandatory for major system work**, upgrading the architectural layer with:

- **Architect as plan owner** – Vibe Architect v3.0 is the mandatory checkpoint for major builds
- **Standardized plan files** – Every major build has `N5/builds/<slug>/PLAN.md` using a common template
- **Auto-initialized build workspaces** – `init_build.py` scaffolds `PLAN.md`, `STATUS.md`, and `.n5protected`
- **Builder plan gating** – Vibe Builder v3.1 refuses to execute major work without a plan file
- **Level Upper integration (experimental)** – Counterintuitive review step for bigger builds

This capability operationalizes Ben Guo's Velocity Coding planning discipline inside N5 so that plans are **for Zo to execute**, not for humans to read.

## Scope

Included:
- All **major builds** (refactors >50 lines, schema changes, multi-file work, new systems/features, persona/prompt design)
- Architect, Builder, Level Upper, and Operator persona behavior for builds
- Plan template, build init script, and planning guide

Excluded:
- Minor one-off edits (<50 lines, single file) where planning is optional
- Non-build conversational threads

## Key Components

- `N5/scripts/init_build.py` – Build workspace initializer
- `N5/templates/build/plan_template.md` – Canonical plan structure
- `N5/templates/build/status_template.md` – Status tracking template
- `N5/docs/BUILD_PLANNING_GUIDE.md` – Build planning quick reference
- `N5/builds/<slug>/PLAN.md` – Per-build plan files
- `N5/builds/<slug>/STATUS.md` – Per-build status files
- `N5/prefs/system/persona_routing_contract.md` §7.1 – Build Planning Protocol

## Personas Involved

- **Vibe Architect v3.0** – Owns plan creation, Nemawashi (2–3 alternatives), trap-door identification, Level Upper integration, and handoff to Builder.
- **Vibe Builder v3.1** – Enforces plan gating (refuses major work without `PLAN.md`), executes phases, and updates checklists.
- **Vibe Level Upper v2.1** – Provides a counterintuitive lens on plans (experimental).
- **Vibe Operator v2.1** – Detects major builds and routes to Architect.

## Triggers

- V or Zo requests: "build X capability", "build [system/feature]", or any major system change.
- Operator detects **"major"** change and invokes Architect + `init_build.py`.

## Success Criteria

- 100% of major builds have a populated `PLAN.md` before any implementation begins.
- Builder never starts major work without a plan file present.
- Plans are structured so Zo can execute them step-by-step without human clarification.
- Planning overhead for minor fixes remains low (no forced planning for simple changes).

## Risks & Mitigations

- **Risk:** Over-planning for simple work → **Mitigation:** Clear "major" definition and escape hatch for <50-line single-file changes.
- **Risk:** Level Upper adds too much friction → **Mitigation:** Time-boxed, optional for small/medium builds, treated as experimental.
- **Risk:** Personas drift from contract → **Mitigation:** Routing contract §7.1 kept as canonical source; periodic review.

## Related

- `file 'N5/docs/BUILD_PLANNING_GUIDE.md'`
- `file 'N5/builds/planning-system-v1/PLAN.md'`
- `file 'N5/builds/planning-system-v1/BUILD_COMPLETE.md'`
- Ben Guo – Velocity Coding / plan-code-changes prompt.
