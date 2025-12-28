---
created: 2025-12-27
last_edited: 2025-12-27
version: 3.0
type: build_plan
status: approved
provenance: con_fCxNsgBS9Vw33X2k
supersedes: PLAN.md
---

# Plan v3: Position Tracking System (Simplified)

**Decision:** Build extraction → existing `positions.db`, not parallel markdown system.

**Rationale:** 
- `positions.py` already provides CRUD, semantic search, overlap detection
- 9 positions already exist in positions.db
- No need for duplicate storage layer
- Reduces estimated effort from ~12h to ~4h

---

## What Exists (N=4)

| Artifact | Purpose | Status |
|----------|---------|--------|
| `N5/scripts/positions.py` | Full CRUD for positions.db | ✅ Working |
| `N5/data/positions.db` | 9 positions with semantic embeddings | ✅ Has data |
| `Prompts/Position Seed Interview.prompt.md` | Interview to extract cornerstone positions | ✅ Exists |
| `Prompts/Close Conversation Type B.prompt.md` | Extracts positions from conversations | ✅ Exists |

---

## Simplified Phase Plan

### Phase -1: Seed Positions (Optional)
**Status:** Already partially done (9 positions exist)
- [ ] Run seed interview if V wants to add more cornerstones
- [ ] Or skip — 9 positions is a reasonable starting point

**Decision needed:** Run interview or proceed with existing 9?

---

### Phase 0: B32 Enhancement
**Status:** Nice-to-have, not blocking
- [ ] Add speaker/v_stance fields to B32 generation prompt
- [ ] Can defer — extraction can infer from context (76% yield without it)

**Recommendation:** Defer to post-MVP

---

### Phase 1: B32 → Candidate Extraction
**New Approach:** Extract to staging JSONL, then triage to positions.py

**Create:**
- `N5/scripts/b32_position_extractor.py` — scans B32 files, outputs candidates
- `N5/data/position_candidates.jsonl` — staging area for triage

**Flow:**
```
B32 files → extractor.py → candidates.jsonl → [triage] → positions.py add
```

**Candidate JSONL schema (staging only):**
```json
{
  "id": "cand_20251227_001",
  "claim": "The scarcest resource in hiring is attention",
  "speaker": "V",
  "v_stance": "endorsed",
  "source_meeting": "2025-09-16_Fohe-partnership-pilot",
  "source_excerpt": "...",
  "extracted_at": "2025-12-27T21:00:00Z",
  "domain_suggestion": "hiring-market",
  "status": "pending"
}
```

**Checklist:**
- [ ] Create `b32_position_extractor.py`
- [ ] Create extraction prompt (`N5/prompts/extract_positions_from_b32.md`)
- [ ] Test on 5 B32 files, verify output
- [ ] Quality gate: <30% noise

**Estimated effort:** 1.5 hours

---

### Phase 2: SKIP
~~Directory structure~~ — Not needed. positions.db is the store.

---

### Phase 3: Triage Interface
**New Approach:** Triage prompt that calls `positions.py add` for approved candidates

**Create:**
- `Prompts/Position Triage.prompt.md` — review candidates, approve/reject

**Triage actions:**
- **Approve** → `python3 positions.py add --id <slug> --domain <domain> --title "<claim>" --statement "<full statement>" --stability emerging --confidence 3`
- **Extend** (if similar exists) → `python3 positions.py extend <existing_id> --evidence "<source>"`
- **Reject** → Mark as rejected in candidates.jsonl

**Checklist:**
- [ ] Create triage prompt
- [ ] Test approve flow → verify position appears in `positions.py list`
- [ ] Test extend flow → verify evidence added
- [ ] Test reject flow → verify candidate marked rejected

**Estimated effort:** 1 hour

---

### Phase 4: Deduplication Enhancement
**Enhancement to existing positions.py:**
- [ ] Improve `check-overlap` to run automatically before add
- [ ] If high overlap (>0.8), suggest extend instead of add

**Estimated effort:** 30 min

---

### ⏸️ CHECKPOINT

After Phase 3, use for 2 weeks. Track:
- Is extraction quality good?
- Is triage sustainable?
- Do we need more automation?

---

### Phase 5+ (Post-Checkpoint)
- Tension detection (compare positions semantically)
- Daily agent for automated triage notification
- Integration with Thought Provoker ending

---

## Execution Order

1. **Phase 1** — Build extractor (1.5h)
2. **Phase 3** — Build triage (1h)
3. **Phase 4** — Dedup enhancement (30min)
4. **Test** — Run extraction on 20 B32s, triage candidates
5. **Checkpoint** — Use for 2 weeks

**Total estimated effort: ~3-4 hours**

---

## Files to Create

| File | Purpose |
|------|---------|
| `N5/scripts/b32_position_extractor.py` | Extract candidates from B32s |
| `N5/prompts/extract_positions_from_b32.md` | LLM prompt for extraction |
| `N5/data/position_candidates.jsonl` | Staging area for candidates |
| `Prompts/Position Triage.prompt.md` | Interactive triage interface |

---

## Success Criteria

1. **Extraction works:** 20 B32s → candidates with <30% noise
2. **Triage works:** Approve candidate → position in positions.db
3. **Dedup works:** Similar positions detected, suggest extend
4. **Habit forms:** Triage is fast enough to be sustainable (<5 min for 10 candidates)

---

## Integration Points

| Existing System | Integration |
|-----------------|-------------|
| `positions.py add` | Triage approval action |
| `positions.py extend` | Triage extend action |
| `positions.py check-overlap` | Pre-add deduplication |
| `positions.py search` | Query existing positions |
| `brain.db` | Already integrated via `migrate_positions_to_brain.py` |

