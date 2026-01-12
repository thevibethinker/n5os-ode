---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.2
provenance: con_wPcuQVQiz9f4L7Te
status: planning (Phase 5 execution authorized)
---

# Plan: Voice Library V2 (Language + Thinking)

**Slug:** `voice-library-v2`  
**Owner:** Vibe Architect  
**Status:** Planning (Reviewed + Phase 5 execution authorized)  
**Created:** 2026-01-12  

---

## Master Checklist (Top-Level)

- [ ] Confirm block number for Linguistic Primitives (avoid B-number conflicts)
- [ ] Phase 5 (LinkedIn) complete through review sheet generation
- [ ] V approves/rejects up to **100** LinkedIn primitives (seed set cap)
- [ ] Import approved seed set into `voice_library.db` with `source = linkedin`
- [ ] (Later) Validate **final generated outputs** with Pangram (not primitives)

---

## Open Questions

1. **Cold start seeding:** Should we seed from LinkedIn posts (already planned for transformation pairs) or start with manual curation of known V-phrases? **RESOLVED:** LinkedIn corpus extraction (Phase 5, parallel workstream). No manual seeding—let it emerge organically.
2. **Block number:** What number for the new Linguistic Primitives block? B35? Check for conflicts.
3. **Pangram usage scope:** **Resolved for Phase 5** — no Pangram during seeding; reserve Pangram for validating final generated outputs.

---

## Objective

Expand the Voice Library from a phrase-bank into a **cognitive-linguistic asset** that captures:

1. **Surface layer:** V's distinctive phrases, pivots, sentence patterns
2. **Semantic layer:** The mental models and framings those phrases express (via domain tags, not formal ontology)
3. **Distinctiveness layer:** Statistical measure of how "V" vs "generic" each primitive is

**Integration target:** Feed into the existing Voice Transformation System (v3.0) as retrievable raw material during content generation.

---

## Alternatives Considered (Nemawashi)

### Alternative A: Formal Concept Ontology
- Create `concepts` table with UUID primary keys
- Many-to-many links between primitives and concepts
- **Rejected:** Overengineers the problem. Domain tags + semantic search achieve the same goal with less complexity. Concepts would require ongoing maintenance and add query complexity.

### Alternative B: Frequency-Based Rarity Score
- Build n-gram frequency baseline from V's corpus
- Compare each phrase's frequency to baseline
- **Rejected:** Measures "how often V says this" not "how distinctively V says this." A frequently-used phrase can still be highly distinctive. A rare phrase might just be obscure jargon.

### Alternative C: Pangram-Based Distinctiveness (Scope-Limited)
- Pangram is excellent for validating **final generated drafts** (a coherent passage)
- Pangram is **not reliable/meaningful** on short primitives/snippets (too little signal)
- **Decision:** Do **not** call Pangram during Phase 5 extraction/seeding. Leave `distinctiveness_score = NULL` for LinkedIn-seeded primitives; score later only when testing full outputs.

### Alternative D: Temperature Manipulation for "Chaos Factor"
- Adjust LLM temperature at inference for creative segments
- **Rejected:** We don't control temperature in Zo. Not implementable.

### Alternative E: Prompt-Based Novelty Injection (SELECTED)
- Multi-angle generation with constraints
- Forced primitive injection ("You MUST use this analogy")
- Constraint prompting ("Explain using household object metaphors")
- **Selected:** Achievable via prompting. No infrastructure changes needed.

### Alternative F: Pure LLM Ranking vs Light Hybrid Ranking (SELECTED)
- **Pure LLM:** Ask LLM to pick “most V-like” primitives from raw candidates.
  - Pro: fast, semantically rich.
  - Con: can overfit expectations and elevate “clever sounding” but non-V patterns.
- **Light Hybrid (selected):** Use light stats (frequency within V corpus + de-dup) + LLM “sounds-like-V” rating as a *re-ranker*.
  - Pro: grounded (repetition matters) while still capturing voice.
  - Con: slightly more moving parts.

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Schema columns in voice_library.db | Medium | Can add columns; removing is harder. Keep schema minimal. |
| Block number (B35) | Low | Once blocks exist with that number, changing causes confusion. Verify no conflicts before assigning. |
| Distinctiveness algorithm | High | Can recompute scores anytime. Not a trap door. |

---

## Phase 1: Schema Simplification + Distinctiveness

### Checklist
- [ ] 1.1 Expand `voice_library.db` schema (lean version)
- [ ] 1.2 Create `compute_distinctiveness.py` using Pangram
- [ ] 1.3 Add throttle tracking columns
- [ ] 1.4 Verify schema with test inserts

### Affected Files
- `N5/data/voice_library.db`
- `N5/data/voice_library_schema.sql`
- `N5/scripts/compute_distinctiveness.py` (new)

### Changes

**Schema expansion (LEAN — no concepts table):**

```sql
-- Add to primitives table
ALTER TABLE primitives ADD COLUMN distinctiveness_score REAL DEFAULT 0.0;
  -- Range: 0.0 (generic/AI-like) to 1.0 (distinctive/human-like)
  -- Computed via: 1.0 - pangram_fraction_ai

ALTER TABLE primitives ADD COLUMN novelty_flagged INTEGER DEFAULT 0;
  -- 1 if explicit capture signal present ("I'm stealing that")

ALTER TABLE primitives ADD COLUMN domains_json TEXT;
  -- JSON array of domain tags: ["career", "incentives", "ethics", "optionality"]
  -- Replaces formal concepts table

ALTER TABLE primitives ADD COLUMN last_used_at TEXT;
  -- ISO timestamp of last retrieval for throttling

ALTER TABLE primitives ADD COLUMN use_count INTEGER DEFAULT 0;
  -- Total times retrieved for content generation

-- Index for retrieval
CREATE INDEX IF NOT EXISTS idx_primitives_distinctiveness ON primitives(distinctiveness_score);
```

**`compute_distinctiveness.py`:**

```python
"""
Compute distinctiveness scores for voice primitives using Pangram.

Usage:
  python3 compute_distinctiveness.py --all          # Score all unscored primitives
  python3 compute_distinctiveness.py --id VP-001    # Score specific primitive
  python3 compute_distinctiveness.py --threshold 0.6 --list  # List high-distinctiveness
"""
# Calls Pangram API for each primitive's exact_text
# Updates distinctiveness_score = 1.0 - fraction_ai
# Respects rate limits with sleep between calls
```

### Unit Tests
- Insert test primitive → verify default distinctiveness_score = 0.0
- Run compute_distinctiveness on test → verify score updated
- Verify domains_json stores/retrieves as valid JSON array

---

## Phase 2: Extraction + Meeting Block

### Checklist
- [ ] 2.1 Create B35 (Linguistic Primitives) block prompt
- [ ] 2.2 Create `extract_voice_primitives.py` for batch extraction
- [ ] 2.3 Integrate "I'm stealing that" signal detection
- [ ] 2.4 Generate review queue batches

### Affected Files
- `Prompts/Blocks/Generate_B35.prompt.md` (new)
- `N5/scripts/extract_voice_primitives.py` (new)
- `N5/review/voice/YYYY-MM-DD_voice-primitives_candidates_batch-NNN.md` (generated)

### Changes

**B35 Block Prompt (Linguistic Primitives):**

Extracts from transcript:
- **Analogies:** "X is like Y because Z"
- **Metaphors:** Conceptual framings ("talent as optionality", "career as portfolio")
- **Distinctive phrases:** Sentence patterns that sound like V
- **Capture signals:** "I'm stealing that", "That's a great way to put it"
- **Comparisons:** "The difference between X and Y is..."

Output format: JSONL with fields matching primitives schema.

**`extract_voice_primitives.py`:**

```python
"""
Extract voice primitive candidates from meeting transcripts.

Usage:
  python3 extract_voice_primitives.py --meeting "2026-01-10_Client-Call"
  python3 extract_voice_primitives.py --all-unprocessed
  python3 extract_voice_primitives.py --since 2026-01-01

Process:
1. Load transcript
2. Run B35 block extraction (via LLM)
3. Score each candidate with Pangram (distinctiveness)
4. Flag explicit capture signals (novelty_flagged = 1)
5. Write to review queue sorted by: novelty_flagged DESC, distinctiveness_score DESC
"""
```

### Unit Tests
- Extract from sample transcript → verify JSONL output format
- Verify "I'm stealing that" detection sets novelty_flagged = 1
- Verify review queue sorting (high novelty/distinctiveness first)

---

## Phase 3: Vibe Writer Integration

### Checklist
- [ ] 3.1 Create `retrieve_primitives.py` for semantic search
- [ ] 3.2 Update Vibe Writer prompt to include primitive retrieval
- [ ] 3.3 Implement throttle logic (no reuse within 500 words)
- [ ] 3.4 Add Pangram post-check with primitive injection fallback

### Affected Files
- `N5/scripts/retrieve_primitives.py` (new)
- `N5/prefs/communication/voice-primitives-system.md` (update)
- `Prompts/Generate With Voice.prompt.md` (update)

### Changes

**`retrieve_primitives.py`:**

```python
"""
Retrieve relevant voice primitives for content generation.

Usage:
  python3 retrieve_primitives.py --topic "talent optionality" --count 10
  python3 retrieve_primitives.py --domains career,incentives --min-distinctiveness 0.6

Process:
1. Embed query topic using N5 semantic memory
2. Search primitives by semantic similarity
3. Filter by domains (if specified)
4. Filter by distinctiveness_score >= threshold (default 0.5)
5. Exclude recently used (last_used_at within throttle window)
6. Return top N primitives
7. Update last_used_at and use_count for returned primitives
"""
```

**Retrieval Contract (update to voice-primitives-system.md):**

- Default retrieval: **5-10 primitives** per 1,000-2,000 word piece
- Distinctiveness threshold: **≥ 0.6** (only distinctive primitives)
- Throttle: Same primitive not reused within **500 words** or **2 pieces** (whichever is longer)
- Diversity: Prefer primitives from different domain tags

**Pangram Post-Check Flow:**

```
1. Generate draft using Vibe Writer + retrieved primitives
2. Run Pangram on draft
3. If fraction_ai > 0.5:
   a. Identify highest-AI-scoring windows (paragraphs)
   b. Retrieve HIGH distinctiveness primitives (≥ 0.8) not yet used
   c. Prompt: "Rewrite this paragraph incorporating: [primitive]"
   d. Re-check with Pangram
   e. Max 2 iterations per window
```

### Unit Tests
- Retrieve primitives → verify throttle excludes recently used
- Verify distinctiveness filter works (returns only ≥ threshold)
- Verify use_count increments on retrieval

---

## Phase 4: Novelty Injection (Chaos Factor)

### Checklist
- [ ] 4.1 Create `novelty_injection_prompts.md` with constraint templates
- [ ] 4.2 Add multi-angle generation option to Vibe Writer
- [ ] 4.3 Document when to use novelty injection

### Affected Files
- `N5/prefs/communication/style-guides/novelty-injection-prompts.md` (new)
- `Prompts/Generate With Voice.prompt.md` (update)

### Changes

**Novelty Injection Strategies (prompt-based, no temperature control needed):**

1. **Forced Primitive Injection:**
   > "You MUST incorporate this analogy somewhere in the piece: '[primitive]'"

2. **Constraint Prompting:**
   > "Explain this concept using only metaphors from [domain: cooking/sports/construction]"

3. **Multi-Angle Generation:**
   > "Generate 3 versions of this opening paragraph with different framings. I'll pick the best."

4. **Socratic Iteration:**
   > "This draft feels generic. Rewrite paragraph 2 with a more surprising angle. What would make a reader stop scrolling?"

5. **Inversion Prompt:**
   > "Write the contrarian take on this. What would someone who disagrees say, and why might they be right?"

**When to use:**
- Pangram score > 0.6 after first pass
- Content feels "correct but boring"
- Topic is crowded/saturated (many people writing about it)
- Explicitly requested ("make this spicier")

### Unit Tests
- Verify novelty injection prompts are syntactically valid
- Manual test: generate with/without novelty injection, compare Pangram scores

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Schema supports all required fields | ✓ | Migration runs without error |
| Distinctiveness scores computed | ✓ | All approved primitives have score > 0 |
| Extraction captures "I'm stealing that" | ✓ | Test transcript with signal → novelty_flagged = 1 |
| Retrieval respects throttle | ✓ | Same primitive not returned within window |
| **Pangram post-check reduces AI score** | **≤50% AI** | Only 100% AI gets noticed; ~50% is acceptable and realistic |
| End-to-end: draft generation uses primitives | ✓ | Manual verification of primitive presence in output |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pangram API rate limits | Medium | Blocks bulk scoring | Batch with delays; cache scores |
| Extraction noise (too many false positives) | High | Overwhelms review queue | High distinctiveness threshold for auto-queue; human review required |
| Primitives feel forced in output | Medium | Damages voice authenticity | Throttle aggressively; only high-distinctiveness; test with Pangram |
| Cold start (empty library) | Medium | No primitives to retrieve | LinkedIn corpus backfill (Phase 5); organic accumulation from meetings |

---

## Dependencies

- **Pangram API:** Required for distinctiveness scoring. Already integrated at `Integrations/Pangram/pangram.py`.
- **N5 Semantic Memory:** Required for primitive retrieval. Already available via `N5/scripts/n5_memory_client.py`.
- **Meeting Intelligence Pipeline:** B35 block integrates with existing block generation system.
- **Voice Transformation System v3.0:** Already exists. Voice Library feeds into it, doesn't replace it.

---

## Estimated Effort

| Phase | Complexity | Estimate |
|-------|------------|----------|
| Phase 1: Schema + Distinctiveness | Low | 1-2 hours |
| Phase 2: Extraction + Block | Medium | 3-4 hours |
| Phase 3: Vibe Writer Integration | Medium | 2-3 hours |
| Phase 4: Novelty Injection | Low | 1 hour |
| Phase 5: LinkedIn Corpus Extraction | Medium | 2-3 hours (parallel) |
| **Total** | | **9-13 hours** |

---

## Phase 5: LinkedIn Corpus Extraction (Parallel Workstream)

**Context:** V has ingested a LinkedIn database (`Datasets/linkedin-full-pre-jan-10/data.duckdb`) containing authentic posts and comments. This is a rich source of "known-good" voice primitives.

**Corpus:**
- **Comments:** 689 total (~300 usable at ≥100 chars)
- **Shares (posts with commentary):** 130 total (~80-100 with substantial commentary)
- **Messages:** 15,101 — **excluded** (too contextual/personal)

### Checklist
- [ ] 5.1 Data prep: Extract comments + shares into unified corpus
- [ ] 5.2 Frequency scan: Identify repeated n-grams within V's corpus
- [ ] 5.3 Semantic chunking: Break each piece into semantic blocks (complete thoughts)
- [ ] 5.4 Primitive extraction: Extract candidates with type classification
- [ ] 5.5 Synthesis: Deduplicate, find meta-patterns, rank
- [ ] 5.6 Human review: Present to V for approval
- [ ] 5.7 Import approved primitives to voice_library.db

### Affected Files
- `N5/scripts/linkedin_voice_extractor.py` (new — main pipeline)
- `N5/builds/voice-library-v2/linkedin_corpus.jsonl` (extracted corpus)
- `N5/builds/voice-library-v2/linkedin_frequency.json` (n-gram frequency data)
- `N5/builds/voice-library-v2/linkedin_primitives_raw.jsonl` (extracted candidates)
- `N5/builds/voice-library-v2/linkedin_primitives_ranked.jsonl` (after synthesis)
- `N5/review/voice/YYYY-MM-DD_linkedin-primitives_review.md` (human review queue)

### Phase 5 Execution Specs (V confirmed)

- **Distinctive-only:** ignore generic but useful engagement openers (e.g., "couldn't agree more").
- **Grouping:** review sheet must be grouped by **primitive type**.
- **Tagging:** candidates can be tagged by **domain** (e.g., hiring, job-search, career coaching, recruiting, product).
- **Not-X-but-Y handling:** treat these as **linguistic atoms (specific phrasings)**, not tracked as a meta-pattern.
- **Pattern reversal:** add tag `pattern_reversal` when a primitive is a reversal/subversion of a common template (still stored as an atom).

### Approach: Light Hybrid (Statistical Grounding + LLM Extraction)

**Why hybrid over pure LLM:**
- Statistical pass provides reality check ("V actually uses this 14 times")
- Prevents LLM from hallucinating patterns it expects to find
- Light statistical = just frequency counts within V's corpus

**Pipeline:**

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Data Prep                                          │
│  - Pull comments (≥100 chars) + shares with commentary      │
│  - Light frequency scan: what n-grams does V repeat?        │
│  - Output: ~350-400 pieces + frequency hit list             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Semantic Chunking + Extraction (batched LLM)       │
│  - Process 15-20 pieces per LLM call via /zo/ask            │
│  - For each: chunk into semantic blocks → extract primitives│
│  - Capture: primitive, type, extractable form, context      │
│  - Output: ~500-1000 raw primitive candidates               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Synthesis                                          │
│  - Deduplicate (same primitive, different instances)        │
│  - Find meta-patterns ("V does this reframe a lot")         │
│  - Rank by frequency × quality                              │
│  - Output: ~100-150 ranked unique primitives                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Human Review                                       │
│  - Present to V in batches                                  │
│  - Approve / reject / refine                                │
│  - Output: 30-50 high-confidence primitives → voice_library │
└─────────────────────────────────────────────────────────────┘
```

### Primitive Types to Extract

| Type | Example | Detection Signal |
|------|---------|------------------|
| **Signature phrase** | "the talent cliff" | Frequency (V repeats it) |
| **Syntactic pattern** | Em-dash pivot ("X—but actually Y") | Structural |
| **Conceptual frame** | "it's not about X—it's about Y" | LLM classification |
| **Metaphor/analogy** | "career as portfolio" | LLM classification |
| **Rhetorical device** | Rhetorical questions, inversions | LLM classification |

### Key Insight
LinkedIn comments especially valuable:
- Short-form, punchy
- Written quickly (less polished = more authentic)
- Often contain reactive analogies
- High signal-to-noise for distinctive V-isms

### Integration
- Outputs feed into `voice_library.db`
- Source = "linkedin" (vs "meeting" for B35 extractions)
- `distinctiveness_score` = **NULL** for Phase 5 (populated later when validating full generated outputs)

### Review Contract (Phase 5)

- Goal: seed set of **≤100** primitives that “sound like V” (linguistic signature prioritized)
- Review UI: **Approve / Reject** + optional notes column (notes are non-blocking)

### Unit Tests
- Data prep extracts correct count from DuckDB
- Frequency scan identifies repeated phrases
- Chunking produces valid semantic blocks
- Extraction outputs valid JSONL with required fields
- Synthesis reduces duplicates
- Review sheet groups by type + includes domain tags + includes pattern_reversal tag when relevant

---

## Handoff

When plan is approved:
1. Switch to Builder persona: `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`
2. Execute Phase 1 first
3. Verify schema before proceeding to Phase 2
4. Human review gate after Phase 2 extraction before Phase 3 integration

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.2 | 2026-01-12 | Added top-level master checklist. Locked Phase 5 decisions: no Pangram for seeding, seed cap 100, approve/reject review, optimize “sounds like V”. |
| 2.1 | 2026-01-12 | Added Phase 5 (LinkedIn extraction). Updated success criteria to ≤50% AI. Resolved cold start question. |
| 2.0 | 2026-01-12 | Complete rewrite after Opus audit. Removed concepts table, changed rarity→distinctiveness, added Pangram scoring, added novelty injection strategies, added trap door analysis, added alternatives considered. |
| 1.0 | 2026-01-11 | Initial draft (pre-audit). Had conceptual flaws. |





