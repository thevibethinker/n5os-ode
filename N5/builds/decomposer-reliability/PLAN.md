---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.0
type: build_plan
status: ready
provenance: con_VrZWyEvkDHZu2bES
---

# Plan: Careerspan Decomposer Reliability

**Objective:** Eliminate hallucinations in careerspan-decomposer by implementing evidence-locked extraction with fail-fast validation.

**Trigger:** V reported hallucinations: story details mixed up, "Our Take" paraphrased instead of verbatim, company names swapped (Amex/KeyGen), incorrect story references. Current implementation has no provenance verification.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [x] What payload shape will the endpoint provide? **Assumption: structured JSON with verbatim our_take, skill assessments, story IDs. Design for this target state; maintain backward compatibility with OCR mode.**
- [x] Preferred failure behavior? **Fail fast, stop processing, create FAILED manifest with specific errors, don't emit partial outputs.**

---

## Alternatives Considered (Nemawashi)

### Alternative A: Patch existing prompts (rejected)
- Add stronger "verbatim" language to prompts
- **Why rejected:** Prompts already ask for verbatim; problem is architectural (no verification). Prompt tuning won't prevent LLM from paraphrasing or mixing details.

### Alternative B: Chunk-based extraction with substring verification (selected)
- Process skills individually or in small batches
- Verify every `our_take` is a substring of source
- Fail if verification fails
- **Why selected:** Addresses root cause (no provenance checking), aligns with fail-fast requirement, works with both OCR and structured input modes.

### Alternative C: Full rewrite for structured-only input (deferred)
- Eliminate LLM extraction entirely; just copy/map fields from structured payload
- **Why deferred:** Endpoint payload shape not finalized. We need OCR backward compatibility. Phase 2 can optimize for structured-only once endpoint is stable.

---

## Trap Doors Identified

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Schema changes to allow null | Medium | Downstream meta-resume generator may depend on non-null values. **Mitigation:** Don't change schema; emit empty string or fail instead of null. |
| Fail-fast stops all output | Low risk | Can be made configurable later with `--strict` flag. Start strict. |
| Validation against source text | Low risk | Whitespace normalization may cause false negatives. **Mitigation:** Use fuzzy substring match with 95% threshold. |

---

## Checklist

<!-- Concise one-liners. ☐ = pending, ☑ = complete. Zo updates as it executes. -->

### Phase 1: Provenance Verification Layer
- ☐ Create `verify.py` script for evidence-locked validation
- ☐ Implement substring matching with whitespace normalization
- ☐ Add story ID validation against known story list
- ☐ Integrate into validation pipeline
- ☐ Test: Run against existing hardik-flowfuse output + source doc

### Phase 2: Fail-Fast Extraction with Chunking
- ☐ Refactor `decompose.py` to extract skills in batches (5-10 at a time)
- ☐ Add provenance check after each batch
- ☐ Implement FAILED manifest generation on any check failure
- ☐ Add `--strict` flag (default: true) to control fail-fast behavior
- ☐ Test: Intentionally corrupt input and verify it fails correctly

### Phase 3: Structured Input Mode
- ☐ Add JSON input mode to `decompose.py` (alongside existing doc mode)
- ☐ For structured input: copy verbatim fields directly, skip LLM extraction for those fields
- ☐ Validate incoming JSON against expected schema before processing
- ☐ Test: Create sample structured payload and run end-to-end

---

## Phase 1: Provenance Verification Layer

### Affected Files
- `Skills/careerspan-decomposer/scripts/verify.py` - CREATE - New provenance verification module
- `Skills/careerspan-decomposer/scripts/validate.py` - UPDATE - Integrate provenance checks
- `Skills/careerspan-decomposer/SKILL.md` - UPDATE - Document verification behavior

### Changes

**1.1 Create verify.py:**
New module with these functions:
- `normalize_text(text: str) -> str`: Lowercase, collapse whitespace, strip punctuation for fuzzy matching
- `substring_match(needle: str, haystack: str, threshold: float = 0.95) -> tuple[bool, float]`: Check if needle appears in haystack with similarity threshold
- `verify_our_take(our_take: str, source_doc: str) -> VerificationResult`: Returns pass/fail + confidence + location if found
- `verify_story_ids(story_ids: list[str], known_stories: list[str]) -> VerificationResult`: Check all referenced stories exist
- `verify_skill_provenance(skill: dict, source_doc: str, known_stories: list[str]) -> VerificationResult`: Full provenance check for one skill

**1.2 Update validate.py:**
- Import verify module
- Add `--source` flag to accept source document path
- After schema validation, run provenance verification on each skill's `our_take`
- Report provenance failures with specific details (which skill, what text wasn't found)
- Exit non-zero if any provenance check fails

**1.3 Update SKILL.md:**
- Document new `--source` flag for validate.py
- Add section on provenance verification and what it checks

### Unit Tests
- `verify_our_take` finds exact substring: Pass
- `verify_our_take` finds substring with minor whitespace differences: Pass
- `verify_our_take` rejects paraphrased text: Fail (as expected)
- `verify_story_ids` accepts valid IDs: Pass
- `verify_story_ids` rejects unknown IDs: Fail (as expected)

---

## Phase 2: Fail-Fast Extraction with Chunking

### Affected Files
- `Skills/careerspan-decomposer/scripts/decompose.py` - UPDATE - Chunked extraction + fail-fast
- `Skills/careerspan-decomposer/assets/FAILED_TEMPLATE.md` - CREATE - Template for failure reports

### Changes

**2.1 Refactor skills_assessment extraction:**
Current: One LLM call extracts all 30-50 skills at once.
New approach:
1. First LLM call: Identify all skill section anchors (skill names + approximate locations)
2. For each batch of 5-10 skills:
   - Extract structured data
   - Immediately verify `our_take` against source
   - If any verification fails: stop, don't continue to next batch
3. After all batches: run full validation

**2.2 Implement FAILED manifest:**
When extraction fails:
- Do NOT write scores_complete.json, scores_complete.csv, or other output files
- Write `FAILED.md` with:
  - Timestamp
  - Which phase failed
  - Specific errors (which skills, what checks failed)
  - Source doc path (for debugging)
  - Instruction: "Review source document and re-run, or escalate to V"
- Write `manifest.yaml` with `status: failed` and error details

**2.3 Add --strict flag:**
- `--strict` (default: true): Fail on first provenance error
- `--strict=false`: Log warnings but continue (for debugging only)

### Unit Tests
- Batch extraction produces same skills as one-shot (correctness)
- Provenance failure in batch 2 stops processing, doesn't write outputs
- FAILED.md contains actionable error details
- `--strict=false` allows completion with warnings

---

## Phase 3: Structured Input Mode

### Affected Files
- `Skills/careerspan-decomposer/scripts/decompose.py` - UPDATE - Add JSON input mode
- `Skills/careerspan-decomposer/assets/input_schema.json` - CREATE - Schema for structured input
- `Skills/careerspan-decomposer/SKILL.md` - UPDATE - Document JSON input mode

### Changes

**3.1 Add JSON input mode:**
New flag: `--input-json <path>` as alternative to `--doc`
When JSON input provided:
- Validate against `input_schema.json`
- For fields that are verbatim (our_take, skill_name, story_id): COPY directly, no LLM
- For fields that need synthesis (summary, elevator_pitch): Use LLM
- Still run provenance verification (JSON input should contain source text for verification)

**3.2 Create input_schema.json:**
Expected structure:
```json
{
  "candidate": { "name": "...", "current_title": "..." },
  "job": { "title": "...", "company": "...", "requirements": [...] },
  "stories": [
    { "id": "...", "text": "...", "company": "...", "role": "..." }
  ],
  "assessments": [
    {
      "skill_name": "...",
      "our_take": "...",
      "rating": "...",
      "supporting_story_ids": ["..."]
    }
  ],
  "source_text": "..." // Full source for provenance verification
}
```

**3.3 Update SKILL.md:**
- Document both input modes (doc vs JSON)
- Recommend JSON mode when available (more reliable)
- Document input_schema.json requirements

### Unit Tests
- JSON input with valid schema produces correct outputs
- JSON input with missing required field fails fast with clear error
- JSON input with invalid our_take (not in source_text) fails provenance check
- Mixed mode: JSON provides some fields, LLM fills gaps

---

## MECE Validation

This is a **single-worker build** (sequential phases, one person executing). MECE validation not required.

---

## Success Criteria

1. **Provenance verified:** Every `our_take` in output is a verifiable substring of source document
2. **Fail-fast working:** Corrupted input produces FAILED.md, not partial outputs
3. **No regressions:** Existing valid outputs (if any) still pass validation
4. **Structured input ready:** JSON input mode works end-to-end
5. **V can trust outputs:** When decomposition succeeds, the data is reliable

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Substring matching too strict (false negatives on valid text) | Use fuzzy matching with 95% threshold; log near-misses for tuning |
| Chunked extraction slower than one-shot | Acceptable tradeoff for reliability; can parallelize batches if needed |
| Endpoint payload shape changes | input_schema.json is versioned; update schema when endpoint stabilizes |
| LLM still hallucinates in synthesis fields | Synthesis fields (summary, elevator_pitch) are clearly marked as LLM-generated, not claimed as verbatim |

---

## Level Upper Review

<!-- Skipped for this build - straightforward reliability engineering, not strategic/creative work -->

Not invoked. This is a reliability/correctness build with clear requirements.

---

## Execution Notes

**Estimated effort:** 2-3 hours
**Dependencies:** None (self-contained skill)
**Rollback:** Keep current decompose.py as decompose_v1.py if needed

Ready for Builder.
