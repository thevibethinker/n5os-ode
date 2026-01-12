---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.4
provenance: con_TBnwuolXxSkp5t1D
---

# Status: Voice Library V2

**Current Phase:** BUILD COMPLETE  
**Progress:** Phase 1: 4/4, Phase 2: 4/4, Phase 3: 4/4, Phase 4: 3/3, Phase 5: 7/7 — **22/22 (100%)**  
**Blockers:** None  
**Next Action:** Use in production; monitor first meeting extractions

---

## Milestone Checklist

### Planning
- [x] Initial shell created (Phase 1 v1.0)
- [x] Opus audit identified 4 critical issues
- [x] Plan rewritten (v2.0) with corrections
- [ ] V approval of plan

### Phase 1: Schema + Distinctiveness ✅ COMPLETE
- [x] 1.1 Expand schema (lean version)
- [x] 1.2 Create compute_distinctiveness.py
- [x] 1.3 Add throttle tracking columns (in schema)
- [x] 1.4 Verify schema with test inserts

### Phase 2: Extraction + Meeting Block ✅ COMPLETE
- [x] 2.1 Create B35 block prompt
- [x] 2.2 Create `extract_voice_primitives.py` for batch extraction
- [x] 2.3 Wire B35 into Meeting Intelligence Generator (MG-2)
- [x] 2.4 Pipeline validation (7/7 tests passing)

*(Note: Backfill deprioritized per V — 419 LinkedIn primitives sufficient for launch)*

### Phase 3: Vibe Writer Integration ✅ COMPLETE
- [x] 3.1 Create retrieve_primitives.py
- [x] 3.2 Update Vibe Writer prompt (Step 2.5 added)
- [x] 3.3 Implement throttle logic (24h window, use_count tracking)
- [x] 3.4 Add Pangram post-check flow (voice_postcheck.py)

### Phase 4: Novelty Injection ✅ COMPLETE
- [x] 4.1 Create novelty-injection-prompts.md (5 strategies)
- [x] 4.2 Add multi-angle generation (Step 7.5 in Vibe Writer)
- [x] 4.3 Document usage guidelines (triggers, anti-patterns, combinations)

### Phase 5: LinkedIn Corpus Extraction ✅ COMPLETE
- [x] 5.1 Data prep: Extract comments + shares into unified corpus (385 items)
- [x] 5.2 Frequency scan: Identify repeated n-grams within V's corpus
- [x] 5.3 Semantic chunking: Break each piece into semantic blocks
- [x] 5.4 Primitive extraction: Extract candidates with type classification (731 raw)
- [x] 5.5 Synthesis: Deduplicate, score, tag, rank (576 scored)
- [x] 5.6 Human review: 0.7 threshold approved by V
- [x] 5.7 Import approved primitives to voice_library.db (419 primitives imported)

---

## Overall Progress

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Schema | ✅ Complete | 4/4 (100%) |
| Phase 2: Extraction | ✅ Complete | 4/4 (100%) |
| Phase 3: Integration | ✅ Complete | 4/4 (100%) |
| Phase 4: Novelty | ✅ Complete | 3/3 (100%) |
| Phase 5: LinkedIn | ✅ Complete | 7/7 (100%) |
| **Total** | **✅ COMPLETE** | **22/22 (100%)** |

---

## Timeline

| Date | Milestone | Notes |
|------|-----------|-------|
| 2026-01-11 | Initial plan created | v1.0 shell |
| 2026-01-12 | Opus audit completed | Identified 4 critical issues |
| 2026-01-12 | Plan rewritten (v2.0) | v2.0 addresses all issues |
| 2026-01-12 | Phase 5 LinkedIn extraction | 731 raw → 576 scored → 419 imported (≥0.7 threshold) |
| 2026-01-12 | Phase 3 Vibe Writer Integration | retrieve_primitives.py + voice_postcheck.py + prompt updates |
| 2026-01-12 | Phase 4 Novelty Injection | novelty-injection-prompts.md + Step 7.5 + documentation |
| 2026-01-12 | Phase 2 Forward Pipeline | B35 wired to MG-2 + pipeline validation (7/7 tests) |
| 2026-01-12 | **BUILD COMPLETE** | Voice Library V2 operational |

---

## Audit Log

| Date | Event | Outcome |
|------|-------|---------|
| 2026-01-11 | Initial plan drafted | v1.0 with conceptual flaws |
| 2026-01-12 | Opus 4.5 audit | Found 4 critical issues |
| 2026-01-12 | Plan rewritten | v2.0 addresses all issues |
| 2026-01-12 | Phase 5 LinkedIn extraction | 731 raw → 576 scored → 419 imported (≥0.7 threshold) |
| 2026-01-12 | Phase 3 Vibe Writer Integration | retrieve_primitives.py + voice_postcheck.py + prompt update |

### Issues Found & Resolved

1. **Schema mismatch** → Acknowledged; v2.0 expands schema properly
2. **"Rarity" wrong metric** → Changed to "distinctiveness" via Pangram
3. **"Chaos factor" underspecified** → Changed to prompt-based novelty injection
4. **Concepts table overengineering** → Replaced with domain tags

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| No concepts table | Domain tags + semantic search achieves same goal with less complexity |
| Pangram for distinctiveness | Directly measures "human-like" which is our actual goal |
| Prompt-based novelty | We don't control LLM temperature; prompts are our lever |
| B35 meeting block | Integrates with existing meeting intelligence pipeline |
| 24h throttle window | Prevents overuse while allowing reasonable reuse |

---

## Files Created/Modified This Build

| File | Purpose | Status |
|------|---------|--------|
| `N5/scripts/retrieve_primitives.py` | Primitive retrieval with throttling | ✅ Complete |
| `N5/scripts/voice_postcheck.py` | Pangram post-check with injection suggestions | ✅ Complete |
| `Prompts/Generate With Voice.prompt.md` | Updated with Step 2.5 | ✅ Complete |
| `N5/prefs/communication/voice-primitives-system.md` | System spec v1.0 | ✅ Complete |

---

## Library Stats (Current)

```
Total primitives: 419 (all approved)
├── signature_phrase:    129 (31%)
├── conceptual_frame:     99 (24%)
├── syntactic_pattern:    71 (17%)
├── metaphor:             62 (15%)
├── rhetorical_device:    34 (8%)
└── analogy:              24 (6%)

Distinctiveness distribution:
├── High (≥0.9):    139
├── Medium (0.6-0.9): 280
└── Low (<0.6):       0

Top domains: career (166), tech (114), communication (103), recruiting (93)
```

---

## What's Next

**Option A: Phase 4 (Novelty Injection)**
- Create novelty injection prompts
- Lower priority since core integration is done

**Option B: Phase 2 Completion**
- Test "I'm stealing that" signal detection
- Generate first meeting-based review batches
- Validates the meeting→primitive pipeline

**Option C: Production Use**
- Start using primitives in actual content generation
- Gather feedback on quality/naturalness
- Iterate based on real usage

---

## Test Commands

```bash
# Stats
python3 N5/scripts/retrieve_primitives.py --stats

# Retrieve by topic
python3 N5/scripts/retrieve_primitives.py --topic "hiring" --count 5 --no-update

# Retrieve by type
python3 N5/scripts/retrieve_primitives.py --type metaphor --count 3 --no-update

# Post-check (requires PANGRAM_API_KEY)
python3 N5/scripts/voice_postcheck.py --text "Your draft here" --threshold 0.5
```



