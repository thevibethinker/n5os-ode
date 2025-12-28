---
created: 2025-12-26
last_edited: 2025-12-26
version: 2
type: build_plan
status: approved
provenance: con_XI9x9PheQIwZQ84j
level_upper_review: complete
---
# Plan: Position Tracking System (Worldview Knowledge Graph)

**Objective:** Build a system to track V's intellectual positions over time, observing crystallization from raw ideas → working positions → cornerstone beliefs. Includes attribution (V vs. external wisdom), tension detection, and daily triage ritual.

**Why This Matters:** 
- Positions compound over time — tracking them builds cumulative intellectual capital
- Contradictions surface growth opportunities and content fodder
- Semantic memory becomes richer with structured position data
- V can query "What do I think about X?" and get grounded answers

---

## Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| Review cadence | **Daily** — prevent backlog accumulation |
| External wisdom handling | **Same system** with `speaker` tag distinguishing V vs. others |
| Tension resolution | **Flag AND track** — surface for resolution, keep record |
| Position retirement | **Archive old version** — maintain full traceability |
| Review ritual | **All options** — vary based on situation (themed, contradiction-first, frequency, Socratic) |

---

## Position Lifecycle Model

```
                    ┌─────────────┐
                    │  RAW_IDEA   │  (extracted from B32, attributed)
                    └──────┬──────┘
                           │ auto-extraction
                           ▼
                    ┌─────────────┐
              ┌─────│  CANDIDATE  │─────┐
              │     └──────┬──────┘     │
         V rejects         │        V approves
              │            │            │
              ▼            │            ▼
        ┌──────────┐       │     ┌─────────────┐
        │ REJECTED │       │     │   WORKING   │
        └──────────┘       │     └──────┬──────┘
                           │            │
                           │       V promotes (high confidence)
                           │            │
                           │            ▼
                           │     ┌─────────────┐
                           │     │ CORNERSTONE │
                           │     └─────────────┘
                           │
                           │  position evolves/replaced
                           │            │
                           │            ▼
                           │     ┌─────────────┐
                           └────▶│ SUPERSEDED  │ (archived, linked to successor)
                                 └─────────────┘
```

---

## Data Schemas

### Position Candidate (JSONL entry)
```json
{
  "id": "cand_20251226_001",
  "claim": "Recruiters will evolve into agent managers",
  "speaker": "V",
  "v_stance": "endorsed",
  "source_meeting": "2025-12-09_Mckinsey-Alumni-Founders",
  "source_excerpt": "The recruiter of the future won't source...",
  "extracted_at": "2025-12-26T20:00:00Z",
  "topic_suggestion": "careerspan/recruiting/future",
  "status": "pending",
  "crystallization_signals": {
    "repetition_count": 1,
    "explicit_endorsement": true,
    "defense_count": 0
  }
}
```

### Position File (Markdown frontmatter)
```yaml
---
id: pos_20251226_001
topic: careerspan/recruiting/future
claim: "Recruiters will evolve into agent managers coordinating AI systems"
status: working  # candidate | working | cornerstone | superseded
confidence: 0.7  # 0.0-1.0
speaker: V  # V | person name for external wisdom
v_stance: endorsed  # endorsed | questioning | neutral | disagreed
sources:
  - meeting: 2025-12-09_Mckinsey-Alumni-Founders
    date: 2025-12-09
    excerpt: "The recruiter of the future..."
  - meeting: 2025-11-15_Logan-Strategy
    date: 2025-11-15
    excerpt: "We discussed how..."
crystallization:
  repetition_count: 3
  defense_count: 1
  first_appeared: 2025-10-15
  last_reinforced: 2025-12-09
evolution:
  - date: 2025-10-15
    note: "Initial formation during strategy session"
  - date: 2025-12-09
    note: "Strengthened after McKinsey Alumni discussion"
tensions:
  - position_id: pos_20251201_003
    nature: "contradicts"
    resolution_status: unresolved
supersedes: null  # or pos_id of older version
superseded_by: null  # set when this position is retired
created: 2025-10-15
last_edited: 2025-12-26
version: 2.1
provenance: con_XI9x9PheQIwZQ84j
---
```

---

## Level Upper Review

### Counterintuitive Questions Applied:

1. **"What if we did the opposite?"** — Instead of bottom-up extraction, start with V's known positions and find evidence. V's worldview isn't a blank slate.

2. **"What breaks at 10x scale?"** — Triage fatigue (20+ daily candidates), tension explosion (O(n²)), topic sprawl, deduplication complexity.

3. **"Laziest solution that works?"** — Skip Phases 5-6. Extract, triage, store as markdown. Query manually via grep/conversation.

4. **"Senior engineer criticism?"** — No versioning/diff, JSONL mutation for dedup, expensive LLM extraction, no rollback plan, schema lock-in.

5. **"Assumptions that might be wrong?"** — B32s contain worldview positions (vs tactical), daily triage habit sticks, positions are discrete claims, speaker attribution is recoverable.

### Incorporated (V-Approved):

1. ✅ **Phase -1: Seed Positions** — Before extraction, V provides 5-10 known cornerstone positions. These anchor the system and validate extraction quality.

2. ✅ **Topic Hierarchy** — Positions use hierarchical topics (e.g., `careerspan/recruiting/future`). Added to Phase 2 directory structure.

3. ✅ **Lazy MVP Checkpoint** — After Phase 3, STOP. Use system for 2 weeks before proceeding to Phase 5-6. Only build tension detection when pain is felt.

4. ✅ **Extraction Quality Gate** — Phase 1 includes manual review of 5 meetings. If >30% noise, tune prompt before scaling.

5. ✅ **Triage Habit Bootstrap** — First 2 weeks, embed in Thought Provoker session end. Don't create standalone habit until pattern established.

### Rejected (with rationale):

1. **Skip brain integration entirely** — Rejected because semantic query ("What do I think about X?") is a core value prop. But deferred via Lazy MVP checkpoint.

2. **Start with interview instead of extraction** — Partially rejected. Seed positions are good, but extraction still needed to find positions V doesn't consciously track.

---

## Phase Checklist

### Phase -1: Seed Positions ⭐ NEW
- [ ] Create `Prompts/Position Seed Interview.prompt.md`
- [ ] V provides 5-10 cornerstone positions via structured interview
- [ ] Create initial position files for each in `Knowledge/positions/`
- [ ] These become "anchor" positions for extraction comparison
- [ ] Validates frontmatter schema before automated extraction

### Phase 0: B32 Enhancement
- [ ] Add speaker attribution field to B32 generation prompt
- [ ] Add v_stance field (endorsed/questioning/neutral/disagreed)
- [ ] Test on 3 sample meetings
- [ ] Backfill is NOT required (new format going forward)

### Phase 1: Extraction Pipeline
- [ ] Create `position_extractor.py` to scan B32s for position candidates
- [ ] Create `N5/prompts/extraction/extract_positions.md`
- [ ] Output to `N5/data/position_candidates.jsonl` (append-only)
- [ ] Include deduplication logic (same claim across meetings)
- [ ] Track crystallization signals (repetition, endorsement)
- [ ] **Quality Gate:** Manual review of 5 meetings before scaling
- [ ] If >30% noise, tune prompt before proceeding
- [ ] Test: extract from 10 recent meetings, verify output format

### Phase 2: Directory Structure
- [ ] Create `Knowledge/positions/` directory
- [ ] Create **hierarchical** topic subdirectories (e.g., `careerspan/recruiting/future/`)
- [ ] Initial topics from thought_patterns.json themes
- [ ] Create `Knowledge/positions/_archive/` for superseded positions
- [ ] Create `Knowledge/positions/_tensions.jsonl` for tension tracking
- [ ] Add `.n5protected` to prevent accidental deletion

### Phase 3: Review Interface (Position Triage)
- [ ] Create `Prompts/Position Triage.prompt.md`
- [ ] Support Mode A: Themed batches
- [ ] Support Mode B: Contradiction-first
- [ ] Support Mode C: Frequency surfacing
- [ ] Support Mode D: Socratic integration (for Thought Provoker)
- [ ] Approval action: create position file from candidate
- [ ] Rejection action: mark candidate as rejected
- [ ] **Habit Bootstrap:** First 2 weeks, embed at end of Thought Provoker session
- [ ] Test: triage 10 candidates, verify file creation

---

## ⏸️ LAZY MVP CHECKPOINT

**After Phase 3, STOP and use for 2 weeks.**

Track:
- [ ] How often does V query positions manually?
- [ ] How painful is lack of tension detection?
- [ ] Is daily triage sustainable?
- [ ] Are candidates high-quality or noisy?

**Decision Gate:** Proceed to Phase 4-7 only if:
- Manual querying proves inadequate (>3x/week wanting semantic search)
- Tension detection is clearly needed (missing contradictions)
- System has 30+ positions (enough to benefit from automation)

---

### Phase 4: Position File Management (POST-CHECKPOINT)
- [ ] Create `position_manager.py` for CRUD operations
- [ ] `create`: candidate → position file
- [ ] `promote`: working → cornerstone
- [ ] `supersede`: archive old, link to new
- [ ] `add_source`: add new evidence to existing position
- [ ] `add_tension`: link two contradictory positions
- [ ] Test: full lifecycle of one position

### Phase 5: Brain Integration (POST-CHECKPOINT)
- [ ] Extend brain.db schema for position-specific fields
- [ ] Create `position_indexer.py` to index position files
- [ ] Add `type: position` tag for filtering
- [ ] Add `status` field for lifecycle stage
- [ ] Enable semantic query: "What do I think about X?"
- [ ] Test: index 5 positions, verify semantic retrieval

### Phase 6: Tension Detection (POST-CHECKPOINT)
- [ ] Create `tension_detector.py` to find contradictions
- [ ] Compare new candidates against existing positions
- [ ] Compare existing positions against each other (batch)
- [ ] Output to `_tensions.jsonl` with resolution_status
- [ ] Surface unresolved tensions in daily triage
- [ ] Test: detect tension between 2 known contradictory positions

### Phase 7: Daily Agent (POST-CHECKPOINT)
- [ ] Create scheduled task for daily position triage
- [ ] Morning: run extraction on yesterday's meetings
- [ ] Surface candidate count + tension count
- [ ] SMS notification: "You have X new position candidates to review"
- [ ] Link to triage interface
- [ ] Test: simulate 3 days of operation

---

## Phase Details

### Phase -1: Seed Positions ⭐ NEW

**Affected Files:**
- `Prompts/Position Seed Interview.prompt.md` (create)
- `Knowledge/positions/` (create initial files)

**Changes:**
- Structured interview prompt asks V for 5-10 cornerstone positions
- For each: claim, confidence, key sources (from memory), topic
- Creates position files with status=cornerstone
- These anchors validate schema and seed the system

**Unit Tests:**
- Interview produces 5+ positions
- Position files have valid frontmatter
- Topics are hierarchical

**Why This Matters:**
- Prevents cold-start problem
- V's known positions become comparison anchors
- Validates extraction quality (new candidates should relate to anchors)

---

### Phase 0: B32 Enhancement

**Affected Files:**
- `Prompts/Blocks/Generate_B32.prompt.md` (modify)

**Changes:**
- Add instruction to include speaker name for each idea
- Add instruction to note V's stance (endorsed/questioning/neutral/disagreed)
- Update output format to include attribution fields

**Unit Tests:**
- Generate B32 for 1 meeting with multiple speakers
- Verify speaker attribution is present
- Verify v_stance is captured

---

### Phase 1: Extraction Pipeline

**Affected Files:**
- `N5/scripts/position_extractor.py` (create)
- `N5/data/position_candidates.jsonl` (create)
- `N5/prompts/extraction/extract_positions.md` (create)

**Changes:**
- Script walks B32 files, extracts position candidates
- LLM-assisted extraction using prompt template
- Deduplication: if same claim exists, increment repetition_count
- Crystallization signal tracking
- Quality gate before scaling

**Unit Tests:**
- Extract from B32 with 3 ideas → 3 candidates in JSONL
- Extract same idea from 2 meetings → 1 candidate with repetition_count=2
- Verify JSONL schema compliance
- Quality gate: <30% noise on 5-meeting sample

---

### Phase 2: Directory Structure

**Affected Files:**
- `Knowledge/positions/` (create directory tree)
- `Knowledge/positions/_archive/` (create)
- `Knowledge/positions/_tensions.jsonl` (create)
- `Knowledge/positions/.n5protected` (create)

**Changes:**
- Initialize hierarchical directory structure
- Create initial topic folders based on existing themes:
  - `careerspan/` (recruiting, product, gtm)
  - `ai/` (agents, automation, future-of-work)
  - `founder/` (strategy, operations, personal)
  - `worldview/` (career, society, technology)
- Seed with protection marker

**Unit Tests:**
- Verify directories exist with hierarchy
- Verify .n5protected present
- Verify _tensions.jsonl is valid empty JSONL

---

### Phase 3: Review Interface

**Affected Files:**
- `Prompts/Position Triage.prompt.md` (create)
- `N5/scripts/position_triage_helper.py` (create)

**Changes:**
- Prompt reads from position_candidates.jsonl
- Offers 4 review modes (themed, contradiction, frequency, Socratic)
- Helper script for batch operations (approve N, reject N)
- Approved candidates → create position file
- **Habit bootstrap:** integrates with Thought Provoker ending

**Unit Tests:**
- Load 10 pending candidates
- Approve 3 → verify 3 position files created
- Reject 2 → verify status=rejected in JSONL
- Remaining 5 still pending

---

## Success Criteria

### MVP (Phases -1 through 3):
1. **Seed positions exist:** 5-10 cornerstone positions documented
2. **Extraction works:** Running extractor on 20 meetings yields candidates with proper attribution
3. **Quality is acceptable:** <30% noise in extraction output
4. **Triage is fast:** V can approve/reject 10 candidates in under 5 minutes
5. **Habit forms:** Daily triage embedded in Thought Provoker for 2 weeks

### Full System (Phases 4-7, post-checkpoint):
6. **Positions are queryable:** "What do I think about recruiting?" returns relevant positions
7. **Tensions surface:** Contradictory positions are flagged automatically
8. **Evolution is tracked:** Promoting/superseding positions maintains full history
9. **Scale test:** System handles 100+ positions without degradation

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| B32 format change breaks existing meetings | Low | Medium | New format forward-only, old meetings still work |
| Over-extraction creates noise | Medium | Medium | Conservative extraction prompt + HITL filter + **Quality Gate** |
| Tension detection false positives | Medium | Low | Surface for review, don't auto-resolve |
| Daily triage becomes burden | Medium | High | Batch operations, smart prioritization, **habit bootstrap** |
| Brain.db schema migration issues | Low | High | Backup before migration, test on copy, **Lazy MVP gate** |
| Topic sprawl at scale | Medium | Medium | **Hierarchical topics from start** |
| Extraction prompt produces garbage | Medium | High | **Quality gate: review 5 meetings before scale** |

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Position file format (frontmatter schema) | Medium | Migration possible but tedious |
| Brain.db schema extension | Medium | Can add fields, harder to remove |
| Directory structure | High | Easy to reorganize |
| JSONL staging format | High | Append-only, easy to reprocess |
| Topic hierarchy | High | Can restructure folders |

**Recommendation:** Phases -1 through 3 are fully reversible. Pause at checkpoint before Phase 5 (brain integration).

---

## Dependency Graph

```
Phase -1 (Seed) ──────────────────────────────────┐
       │                                          │
       ▼                                          │
Phase 0 (B32 Enhancement) ◄── can parallel ──────►│
       │                                          │
       ▼                                          │
Phase 1 (Extraction) ◄─── benefits from seed ─────┘
       │
       ▼
Phase 2 (Directory) ◄── independent, can parallel with 1
       │
       ▼
Phase 3 (Triage) ◄── depends on 1 + 2
       │
       ▼
   ⏸️ CHECKPOINT (2 weeks)
       │
       ▼
Phase 4 (Manager) ◄── depends on 2
       │
       ▼
Phase 5 (Brain) ◄── depends on 4
       │
       ▼
Phase 6 (Tensions) ◄── depends on 5
       │
       ▼
Phase 7 (Agent) ◄── depends on 1, 3, 6
```

---

## Estimated Effort

### MVP (Phases -1 through 3):
- Phase -1: 1 hour (interview + file creation)
- Phase 0: 30 min
- Phase 1: 2 hours (includes quality gate)
- Phase 2: 30 min (hierarchical structure)
- Phase 3: 2 hours
- **MVP Total: ~6 hours**

### Post-Checkpoint (Phases 4-7):
- Phase 4: 1.5 hours
- Phase 5: 2 hours
- Phase 6: 1.5 hours
- Phase 7: 1 hour
- **Post-Checkpoint Total: ~6 hours**

### **Full System Total: ~12 hours**

---

## Handoff Notes for Orchestrator Thread

**Start with Phase -1** (Seed Positions) — this grounds the system in V's known worldview and validates the schema before any automation runs.

**Parallelization opportunity:** Phase 0 and Phase -1 can run in parallel. Phase 2 can run in parallel with Phase 1.

**Critical checkpoint:** After Phase 3, use the system for 2 weeks before deciding to proceed. This prevents over-engineering.

**Key files to create:**
1. `Prompts/Position Seed Interview.prompt.md`
2. `Prompts/Blocks/Generate_B32.prompt.md` (modify)
3. `N5/scripts/position_extractor.py`
4. `Knowledge/positions/` (directory tree)
5. `Prompts/Position Triage.prompt.md`

**Orchestration pattern:** Builder executes each phase. After each phase, verify checklist items before proceeding. At checkpoint, V decides whether to continue.

