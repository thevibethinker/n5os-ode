---
created: 2026-05-15
last_edited: 2026-05-15
version: 1.0
provenance: con_yUBhTqBAcxEFKwof
---
# N5OS Environment — Codex Adapter

**Owner:** V (Vrijen Attawar)
**System:** N5OS on Zo Computer
**Fast map:** `file 'WORKSPACE_MAP.md'`
**Shared constitution:** `file 'AGENTS.md'`
**Shared contract:** `file 'N5/HARNESS_CONTRACT.md'`
**Session-state policy:** `file 'N5/SESSION_STATE_POLICY.md'`
**Placement authority:** `file 'POLICY.md'`

This file contains Codex-specific mechanics only. For workspace governance, routing, shared defaults, and session-state decisions, follow the shared docs above.

---

## Shared Doc Load Path

For non-trivial work, use this order:

1. `file 'WORKSPACE_MAP.md'`
2. `file 'AGENTS.md'`
3. `file 'N5/HARNESS_CONTRACT.md'`
4. `file 'N5/SESSION_STATE_POLICY.md'`
5. Specialized protocol docs only as needed

Load deeper context on demand. Do not restate the full workspace manual in this adapter.

---

## Persona Routing

Use `file 'N5/prefs/system/persona_routing_contract.md'` as the canonical routing contract.

Before substantive work:

1. Check whether the current request belongs to the active persona.
2. If another persona or playbook is clearly better, switch or explicitly route before doing the work.
3. If the needed switch tool is unavailable or deferred, state the mismatch and use the correct shared playbook/contract path rather than continuing in the wrong role.

Key invariants:

- Operator is home base.
- Maintainer is a playbook, not a persona.
- Librarian was folded into Maintainer and is not a live routing destination.
- Frontend/UI/visual work routes to Designer.
- Image generation/editing and visual assets route to Illustrator.
- Backend/scripts/data/services/infra route to Builder.
- Debugging and verification route to Debugger.

---

## Codex-Specific Extras

- Prefer `rg` / `rg --files` for repository search.
- Use `apply_patch` for manual text/code edits.
- Keep edits scoped and respect dirty worktrees; never revert changes you did not make unless V explicitly asks.
- For multi-file shared-code edits under `N5/`, `Skills/`, `Prompts/`, or `Integrations/`, run dependency graph review before editing unless the change is a trivial docs typo.
- Use `Documents/System/Maintainer-Playbook.md` for cleanup, git hygiene, ignore/protection alignment, commit cadence, and state/coherence/index checks.

---

## What This Adapter Does NOT Do

- Replace `file 'AGENTS.md'`
- Replace `file 'WORKSPACE_MAP.md'`
- Replace `file 'N5/HARNESS_CONTRACT.md'`
- Replace `file 'N5/SESSION_STATE_POLICY.md'`
- Load the whole operating manual by default
