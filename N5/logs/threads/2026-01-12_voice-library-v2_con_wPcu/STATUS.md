---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.1
provenance: con_wPcuQVQiz9f4L7Te
---

# Status: Voice Library V2

**Current Phase:** Phase 5 LinkedIn Extraction (6/7 done)  
**Progress:** Phase 1-2: 6/9 (67%), Phase 5: 6/7 (86%)  
**Blockers:** None — awaiting V's review of primitives  
**Next Action:** V reviews `N5/review/voice/2026-01-12_linkedin-primitives_review.md`, then import approved

---

## Milestone Checklist

### Planning
- [x] Initial shell created (Phase 1 v1.0)
- [x] Opus audit identified 4 critical issues
- [x] Plan rewritten (v2.0) with corrections
- [ ] V approval of plan

### Phase 1: Schema + Distinctiveness
- [x] 1.1 Expand schema (lean version)
- [x] 1.2 Create compute_distinctiveness.py
- [x] 1.3 Add throttle tracking columns (in schema)
- [x] 1.4 Verify schema with test inserts

### Phase 2: Extraction + Meeting Block
- [x] 2.1 Create B35 block prompt
- [x] 2.2 Create `extract_voice_primitives.py` for batch extraction
- [ ] 2.3 Integrate "I'm stealing that" signal detection (in code, needs testing)
- [ ] 2.4 Generate review queue batches (manual step required)

### Phase 3: Vibe Writer Integration
- [ ] 3.1 Create retrieve_primitives.py
- [ ] 3.2 Update Vibe Writer prompt
- [ ] 3.3 Implement throttle logic
- [ ] 3.4 Add Pangram post-check flow

### Phase 4: Novelty Injection
- [ ] 4.1 Create novelty-injection-prompts.md
- [ ] 4.2 Add multi-angle generation
- [ ] 4.3 Document usage guidelines

### Phase 5: LinkedIn Corpus Extraction (Parallel Workstream)
- [x] 5.1 Data prep: Extract comments + shares into unified corpus (385 items)
- [x] 5.2 Frequency scan: Identify repeated n-grams within V's corpus
- [x] 5.3 Semantic chunking: Break each piece into semantic blocks
- [x] 5.4 Primitive extraction: Extract candidates with type classification (731 raw)
- [x] 5.5 Synthesis: Deduplicate, score, tag, rank (150 high-quality candidates)
- [x] 5.6 Human review: Review sheet generated, grouped by type
- [ ] 5.7 Import approved primitives to voice_library.db (awaiting V approvals)

---

## Audit Log

| Date | Event | Outcome |
|------|-------|---------|
| 2026-01-11 | Initial plan drafted | v1.0 with conceptual flaws |
| 2026-01-12 | Opus 4.5 audit | Found 4 critical issues |
| 2026-01-12 | Plan rewritten | v2.0 addresses all issues |
| 2026-01-12 | Phase 5 LinkedIn extraction | 731 raw → 150 ranked primitives ready for review |

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

---

## Files Created This Session

| File | Purpose | Status |
|------|---------|--------|
| `N5/builds/voice-library-v2/PLAN.md` | Build plan v2.2 | Complete |
| `N5/builds/voice-library-v2/STATUS.md` | This file | Active |
| `N5/data/voice_library.db` | Database (shell) | Exists, needs expansion |
| `N5/data/voice_library_schema.sql` | Schema v1.0 | Needs update |
| `Knowledge/voice-library/voice-primitives.md` | Canonical library | Shell, needs seeding |
| `N5/prefs/communication/voice-primitives-system.md` | System spec | Shell, needs update |
| `N5/review/voice/_TEMPLATE_voice-primitives_candidates.md` | Review template | Complete |
| `N5/scripts/linkedin_voice_extractor.py` | LinkedIn extraction pipeline | Complete |
| `N5/builds/voice-library-v2/linkedin_corpus.jsonl` | Extracted corpus (385 items) | Complete |
| `N5/builds/voice-library-v2/linkedin_frequency.json` | N-gram frequency data | Complete |
| `N5/builds/voice-library-v2/linkedin_primitives_raw.jsonl` | Raw primitives (731) | Complete |
| `N5/builds/voice-library-v2/linkedin_primitives_ranked.jsonl` | Ranked primitives (150) | Complete |
| `N5/review/voice/2026-01-12_linkedin-primitives_review.md` | Human review queue | Pending V review |




