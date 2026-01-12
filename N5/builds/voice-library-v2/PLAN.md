---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.4
provenance: con_TBnwuolXxSkp5t1D
status: complete
---

# Plan: Voice Library V2 (Language + Thinking)

**Slug:** `voice-library-v2`  
**Owner:** Vibe Architect  
**Status:** Complete (22/22)  
**Created:** 2026-01-12  

---

## Observed Reality (as of 2026-01-12)

**Build complete.** Evidence:
- `file 'N5/data/voice_library.db'` contains **419 approved** primitives.
- Retrieval exists: `file 'N5/scripts/retrieve_primitives.py'`.
- Batch generator exists: `file 'N5/scripts/generate_voice_review_batch.py'`.
- Writer prompt includes retrieval + novelty steps: `file 'Prompts/Generate With Voice.prompt.md'`.
- Novelty prompts doc exists: `file 'N5/prefs/communication/style-guides/novelty-injection-prompts.md'`.
- MG-2 wiring test passes for B35: `file 'N5/scripts/test_voice_pipeline.py'`.
- Meeting batch generated (8 meetings): `file 'N5/review/voice/2026-01-12_voice-primitives_batch.md'`.

**All phases complete.**

---

## Master Checklist (Top-Level)

- [x] Confirm block number for Linguistic Primitives (B35 exists)
- [x] Phase 5 (LinkedIn) complete through review sheet generation
- [ ] Optional: V approves/rejects up to **100** LinkedIn primitives (seed cap) — **superseded by reality** (419 already imported)
- [x] Import seed set into `voice_library.db` with `source = linkedin`
- [ ] (Later) Validate **final generated outputs** with Pangram (draft-level validation)

---

## Open Questions

1. **Cold start seeding:** **Resolved** — LinkedIn corpus extraction seeded the library.
2. **Block number:** **Resolved** — B35 is used and wired.
3. **Pangram usage scope:** Pangram remains best used on **full drafts**, not short primitives. However, the current DB contains `distinctiveness_score` values (min 0.7, max 1.0). The exact scoring provenance is not fully documented; treat it as an internal “v-likeness/distinctiveness” score for retrieval prioritization.

---

## Objective

Expand the Voice Library from a phrase-bank into a **cognitive-linguistic asset** that captures:

1. **Surface layer:** distinctive phrases, pivots, sentence patterns
2. **Semantic layer:** mental models / framings expressed via domain tags (no ontology)
3. **Distinctiveness layer:** a prioritization score used during retrieval

**Integration target:** Feed into the existing voice generation workflow as retrievable raw material.

---

## Alternatives Considered (Nemawashi)

### Alternative A: Formal Concept Ontology
Rejected: domain tags + retrieval cover the need with less maintenance.

### Alternative B: Frequency-Based Rarity Score
Rejected: frequency ≠ distinctiveness.

### Alternative C: Pangram-Based Distinctiveness (Scope-Limited)
Keep Pangram as the validator for **final drafts** (coherent text has enough signal). For primitives, rely on the stored `distinctiveness_score` for ranking/retrieval (and improve provenance later if needed).

### Alternative D: Temperature Manipulation for "Chaos Factor"
Rejected: not controllable in Zo.

### Alternative E: Prompt-Based Novelty Injection (Selected)
Selected: implementable via prompts + workflow steps.

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Schema columns in voice_library.db | Medium | Additive schema only; avoid removals |
| Block number (B35) | Low | Document and keep stable |

---

## Phase 1: Schema + Distinctiveness

### Checklist
- [x] 1.1 Expand `voice_library.db` schema (lean version)
- [x] 1.2 Create `compute_distinctiveness.py`
- [x] 1.3 Add throttle tracking columns
- [x] 1.4 Verify schema with tests

---

## Phase 2: Extraction + Meeting Block

### Checklist
- [x] 2.1 Create `Generate_B35.prompt.md`
- [x] 2.2 Create `extract_voice_primitives.py`
- [x] 2.3 Wire B35 into MG-2
- [x] 2.4 Generate review queue batches

---

## Phase 3: Vibe Writer Integration

### Checklist
- [x] 3.1 Create `retrieve_primitives.py`
- [x] 3.2 Update writer prompt to include primitive retrieval (Step 2.5)
- [x] 3.3 Implement throttle logic (use_count + last_used_at)
- [x] 3.4 Add post-check flow (voice_postcheck.py)

**Reality note:** current retrieval is DB-filter + keyword matching. “Full semantic search” (embeddings) is optional future work.

---

## Phase 4: Novelty Injection (Chaos Factor)

### Checklist
- [x] 4.1 Create `novelty-injection-prompts.md`
- [x] 4.2 Add novelty injection step to writer prompt (Step 7.5)
- [x] 4.3 Document usage guidelines

---

## Phase 5: LinkedIn Corpus Extraction (Parallel Workstream)

### Checklist
- [x] 5.1 Data prep: Extract comments + shares into unified corpus
- [x] 5.2 Frequency scan
- [x] 5.3 Semantic chunking
- [x] 5.4 Primitive extraction
- [x] 5.5 Synthesis + ranking
- [x] 5.6 Human review sheet generated
- [x] 5.7 Import into `voice_library.db`

---

## Dependencies (corrected)

- Pangram integration: `file 'Integrations/Pangram/pangram.py'`
- N5 semantic memory (optional future enhancement for retrieval): `file 'N5/cognition/n5_memory_client.py'`
- MG-2 spec: `file 'Prompts/Meeting Intelligence Generator.prompt.md'`

---

## Current canonical status

For the authoritative “what’s done vs not done,” see: `file 'N5/builds/voice-library-v2/STATUS.md'`.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.4 | 2026-01-12 | Aligned plan to observed reality (MVP built; Phase 2.4 backlog; corrected semantic-memory path; updated master checklist). |
| 2.3 | 2026-01-12 | Aligned plan to observed reality (MVP built; Phase 2.4 backlog; corrected semantic-memory path; updated master checklist). |
| 2.2 | 2026-01-12 | Added top-level master checklist. Locked Phase 5 decisions. |
| 2.1 | 2026-01-12 | Added Phase 5 (LinkedIn extraction). |
| 2.0 | 2026-01-12 | Complete rewrite after audit. |
| 1.0 | 2026-01-11 | Initial draft (pre-audit). |



