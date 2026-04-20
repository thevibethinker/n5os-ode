---
created: 2025-12-16
last_edited: 2026-04-10
version: 2.0
provenance: con_2faIcSqwaKfrPchM
---

# Vibe Debugger Workflow

**Canonical source:** `Skills/systematic-debugging/SKILL.md` (N5 Debug Protocol v2.0)

This workflow is fully defined in the systematic-debugging skill and the Vibe Debugger persona (v5.0). Do not duplicate content here — read the skill directly.

## Quick Reference

1. Load protocol: `cat Skills/systematic-debugging/SKILL.md`
2. Load context: `python3 N5/scripts/n5_load_context.py "build"`
3. Index graph (if shared code): `python3 Skills/codebase-graph/scripts/query.py index`
4. Follow the 4-layer protocol: Root Cause → Structural Analysis → Orchestration → Swarm (if needed)

## Integration Points

- **Persona:** Vibe Debugger (17def82c) embodies the full protocol
- **Skill:** `Skills/systematic-debugging/SKILL.md` is the operating manual
- **Graph:** `Skills/codebase-graph/` provides structural analysis (Layer 2)
- **Logging:** `N5/scripts/debug_logger.py` provides orchestration (Layer 3)
- **Pulse:** Hypothesis racing and debug swarms (Layer 4)
- **Rule:** "go back to second principles" triggers full protocol reset