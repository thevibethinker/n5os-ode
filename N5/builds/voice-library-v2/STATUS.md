---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.5
provenance: con_TBnwuolXxSkp5t1D
---

# Status: Voice Library V2

## Snapshot (ground truth)

**State:** COMPLETE (library seeded + retrieval + writer integration + novelty prompts + pipeline wiring + review batches).  
**All phases done.**

**Overall status:** **22/22 complete (100%)**

---

## Verified by artifacts

### Core assets
- DB: `file 'N5/data/voice_library.db'`
  - `primitives`: **419** rows, `status=approved`
  - `distinctiveness_score`: min **0.7**, max **1.0**
- Retrieval: `file 'N5/scripts/retrieve_primitives.py'` (throttle + use_count + filters)
- Batch generator: `file 'N5/scripts/generate_voice_review_batch.py'`
- Post-check: `file 'N5/scripts/voice_postcheck.py'` (Pangram-based post-check + injection prompts)
- Writer integration: `file 'Prompts/Generate With Voice.prompt.md'`
  - Step 2.5: Voice Primitive Retrieval
  - Step 7.5: Novelty Injection
- Novelty prompts: `file 'N5/prefs/communication/style-guides/novelty-injection-prompts.md'`
- B35 prompt: `file 'Prompts/Blocks/Generate_B35.prompt.md'`
- LinkedIn corpus outputs:
  - `file 'N5/builds/voice-library-v2/linkedin_corpus.jsonl'`
  - `file 'N5/builds/voice-library-v2/linkedin_primitives_raw.jsonl'`
  - `file 'N5/builds/voice-library-v2/linkedin_primitives_ranked.jsonl'`
- Review artifacts:
  - LinkedIn review sheet: `file 'N5/review/voice/2026-01-12_linkedin-primitives_review.md'`
  - Meeting batch (8 meetings): `file 'N5/review/voice/2026-01-12_voice-primitives_batch.md'`

### Sanity tests
- `file 'N5/scripts/test_voice_pipeline.py'` reports **7/7 passing**.

---

## Milestone checklist (truthful)

### Planning
- [x] Plan rewritten (v2.x)
- [x] Execution completed

### Phase 1: Schema + Distinctiveness (4/4)
- [x] 1.1 Expand schema (lean version)
- [x] 1.2 `compute_distinctiveness.py`
- [x] 1.3 Throttle tracking columns
- [x] 1.4 Schema verified via pipeline tests

### Phase 2: Extraction + Meeting Block (4/4)
- [x] 2.1 B35 block prompt exists
- [x] 2.2 `extract_voice_primitives.py` exists
- [x] 2.3 B35 wired into MG-2 (per wiring test)
- [x] 2.4 Generate meeting-based review queue batches (8 meetings → `file 'N5/review/voice/2026-01-12_voice-primitives_batch.md'`)

### Phase 3: Vibe Writer Integration (4/4)
- [x] 3.1 `retrieve_primitives.py`
- [x] 3.2 Prompt update (Step 2.5)
- [x] 3.3 Throttle logic (24h + use_count)
- [x] 3.4 Post-check flow (`voice_postcheck.py`)

### Phase 4: Novelty Injection (3/3)
- [x] 4.1 Novelty prompts doc exists
- [x] 4.2 Prompt includes Step 7.5
- [x] 4.3 Usage guidelines documented in novelty prompts doc

### Phase 5: LinkedIn Corpus Extraction (7/7)
- [x] 5.1–5.7 completed (corpus → raw → ranked → imported)

---

## What's next (optional)

1) Start using in production content flows (and iterate based on outcomes).
2) Optional: downselect/cull LinkedIn primitives if you still want a ≤100 "seed set" (right now you've got 419 approved).
3) Process the meeting review batch: extract primitives from the 8 meetings, review, and import approved ones.

---

## History

| Date | Event | Details |
|------|-------|---------|
| 2026-01-12 | Phase 5 LinkedIn extraction | 731 raw → 576 scored → 419 imported (≥0.7 threshold) |
| 2026-01-12 | Phase 2.4 complete | `generate_voice_review_batch.py` created; 8 meetings → review batch |
| 2026-01-12 | Build complete | All 22/22 items done |

