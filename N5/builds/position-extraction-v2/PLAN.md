---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_vU0lAa14Y6aRjVTI
---

# PLAN: Position Extraction v2 — Capturing Wisdom, Not Just Claims

## 2026-01-03 Update: HITL Review Sheets + Amend (Overwrite) + Recompute

V decision:
- Review happens via **desktop-editable review sheets** under `N5/review/positions/`.
- Action set per candidate: **accept / amend / reject / hold**.
- **Amend = overwrite** of the insight, but must remain traceable by retaining the original extracted insight + original context fields.
- After an amend, the system must **recompute**: `reasoning`, `stakes`, `conditions` from:
  - the original source context (B32 / source excerpt / any stored extra context)
  - the newly amended insight
- The following fields remain **read-only** (not recomputed): `domain`, `classification`, `speaker`, `source_excerpt`.
- Near-dupes are acceptable for now; treat them as a later-quality problem unless they become noisy.

This adds a new Phase 4 below.

## Decisions Made

1. **Re-extraction:** Reject all 15 pending candidates. Re-run their source B32s with new LLM-based extractor.
2. **Position schema:** Expand positions.db to store structured wisdom (reasoning, stakes, conditions).
3. **Extraction approach:** Pure LLM—no Python/regex pattern matching.

4. **HITL integration point:** Introduce review-sheet-based HITL as the canonical gate before promotion.

---

## Problem Statement

Current extraction collapses wisdom into compressed claims, losing:
- **The insight** (what you see that others don't)
- **The reasoning** (why this is true/important)  
- **The stakes** (what follows from this, why it matters)
- **The conditions** (when this applies, when it doesn't)

B32 blocks already contain rich material—the extraction prompt is stripping it.

---

## Nemawashi: Alternatives Considered

### Alternative A: Richer Candidate Schema ⭐ RECOMMENDED
Add fields to capture full wisdom structure:
- `insight`: The core observation (2-3 sentences, not one)
- `reasoning`: Why this is true/important
- `stakes`: What follows, why it matters
- `conditions`: When this applies, limitations

**Pros:** Backward compatible, incremental, preserves B32 texture  
**Cons:** Requires prompt rewrite, schema expansion

### Alternative B: Two-Stage Extraction
Stage 1: Extract "wisdom blocks" (multi-paragraph)
Stage 2: Human triage + LLM-assisted refinement

**Pros:** Maximum fidelity  
**Cons:** Too heavy for routine operation; adds manual work

### Alternative C: Upstream B32 Format Change
Change B32 generation to output proto-positions directly

**Pros:** Fixes root cause  
**Cons:** Changes upstream contract; existing B32s would need migration

**Decision:** Alternative A. The B32 format is fine—the extraction prompt is the bottleneck.

---

## Positions.db Schema Expansion

### Current Schema (positions table)
```sql
id TEXT PRIMARY KEY,
domain TEXT NOT NULL,
title TEXT NOT NULL,
insight TEXT NOT NULL,        -- Currently a blob; will become structured
components TEXT,              -- JSON array of sub-insights
evidence TEXT,                -- JSON array of evidence entries
connections TEXT,             -- JSON array of related positions
stability TEXT,               -- emerging | developing | stable | foundational
confidence INTEGER,           -- 1-5 scale
formed_date TEXT,
last_refined TEXT,
source_conversations TEXT,
supersedes TEXT,
embedding BLOB,               -- deprecated (now in brain.db)
created_at TEXT,
updated_at TEXT
```

### New Fields to Add
```sql
-- Wisdom structure (the "so what")
reasoning TEXT,               -- The transferable PRINCIPLE. Why this is true in general, not just in this instance.
stakes TEXT,                  -- What follows. Why it matters. Implications for action/belief.
conditions TEXT,              -- When this applies. Boundary conditions. Where the principle breaks down.

-- Provenance clarity
original_excerpt TEXT,        -- Raw text from source (B32, conversation) - the anecdote/evidence
extraction_method TEXT,       -- 'llm_v2' | 'manual' | 'llm_v1' (legacy)
```

### Migration Approach
1. Add columns with `ALTER TABLE` (no data loss)
2. Existing 9 positions keep their current `insight` field
3. New positions from v2 extraction will populate all wisdom fields
4. Optional: Backfill existing positions with LLM pass (lower priority)

### Backward Compatibility
- Old positions: `insight` field remains valid, new fields NULL
- Display logic: If `reasoning` is NULL, show just `insight`
- Search: `insight` still indexed in brain.db; new fields are metadata

---

## Example: Principle-Grounded vs. Anecdote-Grounded

### ❌ WRONG (anecdote-grounded reasoning)
```
insight: "Habit-tracking bots work because of anthropomorphization."

reasoning: "When Rochel described ignoring app notifications but 
responding to bot texts, she showed that the human-like interaction 
was the key factor."
```
*Problem: The reasoning is tethered to Rochel's specific behavior. Not transferable.*

### ✅ RIGHT (principle-grounded reasoning)
```
insight: "The power of habit-tracking bots comes from anthropomorphization—
the sense of obligation you feel to respond to something that texts you 
like a person. The tracking logic is secondary to the social mechanism."

reasoning: "Social obligation is a more reliable behavioral driver than 
utility reminders. Humans evolved to respond to perceived social bids—
a text that feels like it came from a person activates reciprocity 
instincts that a notification cannot. This is the same mechanism that 
makes people answer phone calls but ignore voicemails."

stakes: "Products that trigger social obligation will outperform those 
that rely on utility alone. For Careerspan, this means text-based 
check-ins have structural advantage over app notifications—not because 
they're more convenient, but because they feel like a person is asking."

conditions: "Applies to users who have normalized text communication 
and haven't become cynical about bot interactions. Breaks down for 
users who see through anthropomorphization or who don't feel social 
obligation via text (e.g., younger users who treat all texts as low-priority)."

source_excerpt: "Rochel noted she ignores app notifications but feels 
compelled to respond when the bot texts her."
```

*The anecdote (Rochel) is evidence in `source_excerpt`. The reasoning is the transferable principle about social obligation and reciprocity.*

---

## Checklist

### Phase 1: Schema & Prompt Redesign
- [ ] Define new candidate schema with wisdom fields
- [ ] Rewrite `extract_positions_from_b32.md` prompt
- [ ] Add examples showing full wisdom capture
- [ ] Test on 2-3 existing B32s manually

### Phase 2: Extractor Update
- [ ] Update `b32_position_extractor.py` to handle new schema
- [ ] Update display formatting in `list-pending`
- [ ] Ensure backward compatibility with existing candidates

### Phase 3: Triage UX Improvement
- [ ] Update Position Triage prompt to show full wisdom
- [ ] Add "thin candidate" rejection reason for old-format reprocessing

### Phase 4: HITL Review Sheets + Amend + Recompute (New)
- [ ] Create review sheet generator (batch from candidates)
- [ ] Define deterministic review-sheet grammar (accept/amend/reject/hold)
- [ ] Implement ingest of review sheets → update `position_candidates.jsonl`
- [ ] Implement amend overwrite semantics with traceability fields
- [ ] Implement recompute of reasoning/stakes/conditions after amend
- [ ] Implement promote-from-reviewed flow (only promote accepted/amended)
- [ ] Add unit tests for parsing, overwrite traceability, and recompute behavior

---

## Phase 1: Schema & Prompt Redesign

### Affected Files
- `file 'N5/prompts/extract_positions_from_b32.md'` (rewrite)
- `file 'N5/data/position_candidates.jsonl'` (new schema)

### Changes

**New Candidate Schema:**
```json
{
  "insight": "2-3 sentence observation. What you see that others don't.",
  "reasoning": "The transferable PRINCIPLE. Why this is true in general—not grounded in the specific anecdote, but in underlying mechanisms that apply across contexts.",
  "stakes": "What follows from this. Why it matters. Implications for action or belief.",
  "conditions": "When this applies. Boundary conditions. Where the principle breaks down.",
  "source_excerpt": "Direct quote or paraphrase from B32 (the anecdote/evidence)",
  "speaker": "V" | "name",
  "v_stance": "endorsed" | "questioning" | "neutral",
  "domain": "hiring-market | careerspan | ai-automation | founder | worldview | epistemology",
  "classification": "V_POSITION" | "V_HYPOTHESIS" | "EXTERNAL_WISDOM"
}
```

**Key Prompt Changes:**
1. Replace "claim" with "insight" — explicitly ask for 2-3 sentences
2. Add "reasoning" field — the transferable PRINCIPLE (not anecdote-specific explanation)
3. Add "stakes" field — so what? what follows?
4. Add "conditions" field — when does this apply? where does it break?
5. Provide richer examples showing principle-grounded vs. anecdote-grounded reasoning

### Unit Tests
- Extract from Rochel B32 → should produce rich insight about "Signaling Lag"
- Extract from Davis B32 → should capture "Signal as Data" with full reasoning
- Verify no regression on SKIP classifications (QUESTION, TACTICAL, META)

---

## Phase 2: Extractor Update

### Affected Files
- `file 'N5/scripts/b32_position_extractor.py'`

### Changes
1. Update `extract_positions_llm()` to parse new schema
2. Update `cmd_list_pending()` to display multi-line wisdom
3. Add `--reprocess` flag to re-extract previously processed B32s
4. Maintain backward compatibility: old candidates still load/display

### Unit Tests
- `list-pending` shows full insight, not truncated claim
- Old candidates (with `claim` field) still display correctly
- `--reprocess` successfully re-extracts a known B32

---

## Phase 3: Triage UX Improvement

### Affected Files
- `file 'Prompts/Position Triage.prompt.md'`

### Changes
1. Update display format to show full wisdom (insight + reasoning + stakes)
2. Add rejection reason: `too_thin` for old-format candidates needing reprocessing
3. Add batch command to reprocess thin candidates

### Unit Tests
- Triage display shows readable multi-line format
- Rejection with `too_thin` triggers reprocess suggestion

---

## Phase 4: HITL Review Sheets + Amend + Recompute (New)

### Affected Files
- `file 'N5/scripts/b32_position_extractor.py'` (review sheet: generate + ingest)
- `file 'N5/data/position_candidates.jsonl'` (store amended insight + recomputed fields)
- `file 'N5/prompts/extract_positions_from_b32.md'` (ensure prompt supports recompute call)

### New/Updated Candidate Fields (Additive)
Add fields so amend can be an overwrite while remaining traceable:

```json
{
  "insight": "original extracted insight (never modified)",
  "insight_amended": "optional amended insight (overwrite surface text)",
  "insight_final": "computed at runtime: insight_amended || insight",
  "reasoning": "computed from insight_final + original context",
  "stakes": "computed from insight_final + original context",
  "conditions": "computed from insight_final + original context",

  "review": {
    "decision": "accept|amend|reject|hold",
    "reviewed_at": "ISO timestamp",
    "review_batch": "path or batch id",
    "notes": "optional"
  },

  "source_excerpt": "read-only",
  "speaker": "read-only",
  "domain": "read-only",
  "classification": "read-only"
}
```

### Review Sheet Location (Canonical)
- `file 'N5/review/positions/'`
- Batch naming convention:
  - `YYYY-MM-DD_positions-review_batch-001.md`

### Review Sheet Grammar (Deterministic)
Each candidate is a block with a fixed header and fields.

Required fields:
- `Candidate ID:`
- `Decision:` one of `accept | amend | reject | hold`

If `Decision: amend`, require:
- `Amended insight:` (multiline allowed)

Optional fields:
- `Attribution:` (`mine | inspired | other`)
- `Credit:` free text
- `Notes:`

### Recompute Behavior
If decision is `amend`:
- Set `insight_amended` and recompute `reasoning/stakes/conditions` by re-invoking the LLM extractor in a “recompute mode” using:
  - original `source_excerpt` (+ any stored original B32 context)
  - `insight_final`
The system MUST NOT change: domain/classification/speaker/source_excerpt.

### Unit Tests
- Review sheet parser:
  - Accept block parses correctly
  - Amend block requires amended insight
  - Reject/hold parse correctly
- Overwrite traceability:
  - Original `insight` remains unchanged after amend
  - `insight_amended` stored
  - `insight_final` resolves correctly
- Recompute behavior:
  - After amend, `reasoning/stakes/conditions` are regenerated
  - Read-only fields remain unchanged

---

## Success Criteria

1. **Richer extractions:** New candidates have insight (2-3 sentences), reasoning, stakes, conditions
2. **No information loss:** Full B32 context preserved in extraction
3. **Backward compatible:** Existing candidates still work
4. **Improved triage UX:** Full wisdom visible during review
5. **Reprocessing path:** Can re-extract thin candidates with new logic

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM over-extracts (too many fields, verbose) | Medium | Low | Tune prompt with max lengths, add examples |
| Schema migration breaks existing data | Low | Medium | Keep old `claim` field as fallback display |
| New extractions too slow | Low | Low | Same API call, just richer prompt |

---

## Trap Doors

**None identified.** This is additive schema change, not architectural. Can revert by restoring old prompt and ignoring new fields.

---

## Ready for Builder

When V approves this plan:
1. Hand off to Builder with Phase 1 start
2. Builder rewrites extraction prompt
3. Builder updates extractor script
4. Test on known B32s before bulk re-extraction






