---
created: 2026-03-02
last_edited: 2026-03-02
version: 1.0
provenance: con_pLLTlqfVu4hKeKhT
---

# Phase 0 Rollback

## When to Roll Back
- Invalid or incomplete discovery response
- Localization mismatch on critical runtime assumptions
- Safety policy conflict not resolvable in current loop

## Rollback Procedure
1. Mark Phase 0 as failed in checklist.
2. Freeze progression to Phase 1.
3. Record blockers and unresolved assumptions.
4. Issue revised discovery packet with narrowed scope.

## Notes
- Phase 0 is discovery-only; no production payload apply occurs.
