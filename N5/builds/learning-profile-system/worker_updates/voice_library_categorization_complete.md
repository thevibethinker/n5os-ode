---
created: 2026-01-13
provenance: con_WDVrJL9R2FhuBypw
worker: voice_library_categorization
status: complete
---

# Worker Status: Voice Library Categorization Design

**Status:** ✅ Complete  
**Deliverable:** `file 'N5/builds/learning-profile-system/VOICE_LIBRARY_SPEC.md'`  
**Completed:** 2026-01-13 21:25 ET

---

## Summary

Designed a **function-based categorization schema** for V's Voice Library. Categories derived from actual corpus analysis, not generic taxonomies.

### Key Decisions

1. **7 Primary Categories** (mutually exclusive):
   - `OPEN` — Hooks attention
   - `PIVOT` — Shifts direction
   - `FRAME` — Recontextualizes
   - `STRIKE` — Quotable truths
   - `RALLY` — Calls to action
   - `CLOSE` — Lands the point
   - `BRIDGE` — Transitions

2. **7 Secondary Tags** (additive):
   - `analogy`, `metaphor`, `contrarian`, `warm`, `technical`, `humor`, `self-aware`

3. **Backward Compatible** — Extends existing `voice_library.db` schema without breaking current queries

4. **Auto-Approve Gate** — Distinctiveness ≥0.8 auto-approves; lower scores queue for HITL

### Capture Format Defined

```json
{
  "text": "...",
  "source_type": "conversation",
  "source_id": "con_...",
  "context_before": "...",
  "context_after": "...",
  "capture_signal": "distinctive_framing",
  "timestamp": "..."
}
```

### Open Questions — RESOLVED

1. ✅ Category granularity — 7 confirmed sufficient (functional, not formal)
2. ✅ Auto-approve threshold — 0.8 confirmed
3. ✅ Source priority — conversations weighted at 0.75 vs LinkedIn at 1.0
4. ✅ Decay policy — implemented (retrieval/selection tracking + archival path)

---

## Next Steps for Parent

1. **Review updated spec** — `file 'N5/builds/learning-profile-system/VOICE_LIBRARY_SPEC.md'` (v1.1)
2. **Implement schema migration** (Phase 1) — add columns, bulk-classify existing 419 primitives
3. **Wire conversation-close hook** to capture pipeline
4. **Update retrieve_primitives.py** with effective_score calculation

---

## Artifacts

- `file 'N5/builds/learning-profile-system/VOICE_LIBRARY_SPEC.md'` — Full spec (design only, no implementation)


