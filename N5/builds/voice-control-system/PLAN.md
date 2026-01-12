---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_wPcuQVQiz9f4L7Te
---

# Build Plan: Voice Control System (Modes, Moves, Retrieval, Rubric)

## Open Questions (answer in-chat, do not implement until resolved)

1. **Canonical home / naming:** Where should the new artifacts live long-term?
   - Default proposal: `N5/voice/` (new) or `Knowledge/voice/` (existing conventions unknown)
2. **Integration surface:** What is the current “Vibe Writer” entrypoint (prompt/script) we should target?
3. **Review tolerance:** You want near-zero review ongoing. What is acceptable as “minimum review”?
   - Proposal: 10-minute monthly spot-check + automatic drift detection

## Objective

Turn the LinkedIn backfill and reference blocks into a **repeatable voice control system** that:
- Preserves V’s cognitive motion (moves) and cadence (style)
- Supports **2–4 modes** and a single knob for **professionalism**
- Retrieves guidance by **rhetorical job + topic** (not just semantic similarity)
- Debrands concept nuggets while preserving motion
- Enables low-review improvement over time via a lightweight rubric

## Nemawashi: Alternatives Considered

### Alternative A (Pure RB retrieval)
- **Pros:** simple
- **Cons:** brittle; topic mismatch; hard to generalize; feels copy-pasted

### Alternative B (Moves-first system)
- **Pros:** stable; transferable; model “moves like V”
- **Cons:** requires initial extraction effort

### Alternative C (Modes-only)
- **Pros:** intuitive UX
- **Cons:** doesn’t solve reliability; modes become vague labels

**Recommendation:** **B + C** (moves-first foundation, modes as a thin layer).

## Trap Doors (irreversible / high cost)

1. **Where artifacts live** (directory and schema): moving later creates confusion and duplicates.
2. **Moves schema**: if we lock too early, we’ll have to migrate records later.

## Checklist

### Phase 1 — Define Voice Structure (parallel research + synthesis)
- ☐ Worker: derive 2–4 voice modes + professionalism modulation
- ☐ Worker: create Moves Library (maneuvers, structure, examples)
- ☐ Worker: create Debranding Playbook + sample debranded RB variants

### Phase 2 — Governance (lightweight rules + evaluation)
- ☐ Worker: Voice Constitution (Do/Don’t; anti-tropes)
- ☐ Worker: Voice-Fit Rubric + scoring sheet template

### Phase 3 — Retrieval & Integration Plan
- ☐ Worker: Retrieval Spec (topic + rhetorical job; tie-breakers)
- ☐ Worker: Wiring Plan (inspect Vibe Writer and propose minimal integration)

## Success Criteria

1. We have a **Moves Library** with ≥12 moves that are unmistakably V.
2. We have **2–4 modes** with clear deltas and a professionalism knob.
3. We have an **actionable constitution** (Do/Don’t) that prevents drift.
4. We have a **retrieval spec** that can select:
   - 1 mode
   - 1–2 moves
   - 1–2 RBs
   - 3–8 atoms
   per generation request.
5. We have a **rubric** that can be applied in ≤30 seconds.
6. We have an **integration plan** identifying exact affected prompts/scripts (no implementation yet).

## Reference Files

- `file 'N5/builds/voice-library-v2/linkedin_corpus.jsonl'`
- `file 'N5/builds/voice-library-v2/PLAN.md'`
- `file 'N5/scripts/linkedin_voice_extractor.py'`
- `file 'N5/review/voice/2026-01-12_linkedin-primitives_review.md'`
- `file 'N5/data/voice_library.db'`
- `file 'N5/data/voice_library_schema_v2.sql'`

