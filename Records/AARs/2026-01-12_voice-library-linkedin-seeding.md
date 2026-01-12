---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_wPcuQVQiz9f4L7Te
type: after-action-report
build_slug: voice-library-v2
---

# After-Action Report: Voice Library V2 — LinkedIn Seeding

**Conversation ID:** con_wPcuQVQiz9f4L7Te  
**Duration:** ~4 hours  
**Outcome:** ✓ Success — 419 voice primitives imported to voice_library.db

---

## Summary

Seeded Voice Library V2 with V's authentic voice primitives extracted from LinkedIn corpus (comments and shares). Built a complete extraction pipeline using LLM-based semantic analysis for distinctiveness scoring, domain tagging, and pattern classification.

## What Was Built

### Pipeline: `N5/scripts/linkedin_voice_extractor.py`

5-step extraction pipeline:
1. **prep** — Extract LinkedIn data from DuckDB, compute n-gram frequency
2. **chunk** — Semantic chunking + primitive extraction via batched `/zo/ask` calls
3. **synth** — LLM-based scoring for distinctiveness, domain tags, pattern_reversal detection
4. **review** — Generate grouped HITL review sheet
5. **import** — Bulk import to voice_library.db with threshold filtering

### Corpus Flow

```
LinkedIn DuckDB → 385 items (comments ≥100 chars + shares with commentary)
                      ↓
              731 raw primitives (semantic chunking)
                      ↓
              576 scored primitives (LLM synthesis)
                      ↓
              419 imported (≥0.7 distinctiveness threshold)
```

### Primitive Distribution in voice_library.db

| Type | Count | Avg Distinctiveness |
|------|-------|---------------------|
| signature_phrase | 129 | 0.83 |
| conceptual_frame | 99 | 0.84 |
| syntactic_pattern | 71 | 0.80 |
| metaphor | 62 | 0.84 |
| rhetorical_device | 34 | 0.81 |
| analogy | 24 | 0.88 |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| LLM-based scoring over heuristics | V explicitly rejected regex/keyword approach — semantic understanding required |
| No Pangram during seeding | Reserve API budget for validating generated outputs, not ground truth |
| 0.7 distinctiveness threshold | Filters generic engagement phrases while retaining V-specific voice |
| Domain tags as JSON array | Flexible multi-tagging without separate concepts table |
| pattern_reversal as tag | Track "Not-X-but-Y" inversions without meta-pattern overhead |

## Lessons Learned

1. **LLM > Heuristics for semantic work** — Initial attempt with regex/keyword matching was wrong approach. V caught this immediately. Semantic classification requires semantic intelligence.

2. **Statistical grounding still valuable** — N-gram frequency within corpus provides reality check for LLM extraction ("V actually uses this 14 times")

3. **Threshold-based approval efficient** — Rather than manual checkbox review of 576 items, distinctiveness threshold (0.7) enabled bulk approval while filtering noise.

## What Went Wrong

- **Initial synthesis used regex** — Built keyword-based stoplist and pattern detection. V rejected this approach ("God damn it. I want you to use large language models"). Had to rewrite synthesis step to use `/zo/ask` for LLM-based scoring.

- **Connection drops** — Multiple `n5 resume` cycles required. Pipeline was robust enough to checkpoint progress.

## Artifacts

| File | Purpose |
|------|---------|
| `N5/scripts/linkedin_voice_extractor.py` | Complete extraction pipeline |
| `N5/data/voice_library.db` | 419 primitives seeded |
| `N5/builds/voice-library-v2/linkedin_corpus.jsonl` | Source corpus (385 items) |
| `N5/builds/voice-library-v2/linkedin_frequency.json` | N-gram frequency data |
| `N5/builds/voice-library-v2/linkedin_primitives_raw.jsonl` | Raw extraction (731) |
| `N5/builds/voice-library-v2/linkedin_primitives_ranked.jsonl` | Scored + ranked (576) |
| `N5/builds/voice-library-v2/PLAN.md` | Updated with Phase 5 spec |
| `N5/builds/voice-library-v2/STATUS.md` | Phase 5 complete (7/7) |

## Next Steps

Voice Library V2 Phase 5 (LinkedIn seeding) is complete. Remaining phases:

- **Phase 3:** Vibe Writer integration — `retrieve_primitives.py`, throttle logic, Pangram post-check
- **Phase 4:** Novelty injection — prompt-based generation variety
- **Phases 2.3-2.4:** Meeting extraction — "I'm stealing that" signal detection, review queue

## Top 5 Primitives (by distinctiveness)

1. "self-advocacy skill gap" (signature_phrase, 1.0)
2. "interviews as F train on St. Paddy's Day" (analogy, 1.0)
3. "networking bachmanity" (signature_phrase, 1.0)
4. "career companion" (metaphor, 1.0)
5. "marginal cost of fraud is approaching $0" (signature_phrase, 1.0)

---

*Filed: 2026-01-12 02:18 ET*

