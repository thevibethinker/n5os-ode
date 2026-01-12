---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.0
provenance: con_wkgwgDeEtgUjiPYf
---

# Status: Voice Library V2

**Current Phase:** Phase 2 In Progress  
**Progress:** 6/9 Phase 1-2 tasks done (67%)  
**Blockers:** None  
**Next Action:** Test extraction on a real meeting transcript, then Phase 3 (Vibe Writer Integration)

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

---

## Audit Log

| Date | Event | Outcome |
|------|-------|---------|
| 2026-01-11 | Initial plan drafted | v1.0 with conceptual flaws |
| 2026-01-12 | Opus 4.5 audit | Found 4 critical issues |
| 2026-01-12 | Plan rewritten | v2.0 addresses all issues |

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
| `N5/builds/voice-library-v2/PLAN.md` | Build plan v2.0 | Complete |
| `N5/builds/voice-library-v2/STATUS.md` | This file | Active |
| `N5/data/voice_library.db` | Database (shell) | Exists, needs expansion |
| `N5/data/voice_library_schema.sql` | Schema v1.0 | Needs update |
| `Knowledge/voice-library/voice-primitives.md` | Canonical library | Shell, needs seeding |
| `N5/prefs/communication/voice-primitives-system.md` | System spec | Shell, needs update |
| `N5/review/voice/_TEMPLATE_voice-primitives_candidates.md` | Review template | Complete |



