---
created: 2026-01-29
last_edited: 2026-01-29
version: 1
type: build_plan
status: draft
---
# Plan: Careerspan Decomposer Fix

**Objective:** Fix the decomposer skill to produce consistent, schema-validated outputs including the critical `scores_complete.json` with all skill assessments.

**Trigger:** Comparison of Hardik vs Sridhar outputs revealed schema inconsistencies, missing careerspan_score for Sridhar (actually 80, not null), and different field names/types.

**Root Cause Discovered:** The `decompose.py` script doesn't extract `scores_complete.json` at all — those files were created manually in separate conversations, explaining the schema drift.

---

## Open Questions

- [x] Where is Sridhar's score? → **FOUND: 80** (embedded in "Referred 80 © Applied" line)
- [x] Why different schemas? → **Manual extraction in separate threads, no canonical schema enforced**

---

## Checklist

### Phase 1: Define Canonical Schema & Extraction Prompt
- ☐ Create `assets/canonical_schema.json` with JSON Schema definition
- ☐ Create `EXTRACTION_PROMPTS["skills_assessment"]` for scores_complete extraction
- ☐ Add careerspan_score extraction to overview prompt (look for "Referred N" pattern)
- ☐ Test: Schema validates both current outputs (after mapping)

### Phase 2: Update decompose.py
- ☐ Add skills_assessment extraction function
- ☐ Add schema validation step before writing outputs
- ☐ Add careerspan_score extraction from "Referred N ©" pattern
- ☐ Ensure all numeric fields are numeric, not strings
- ☐ Test: Run on sample doc, verify output matches schema

### Phase 3: Backfill Existing Outputs
- ☐ Normalize Hardik output to canonical schema
- ☐ Normalize Sridhar output to canonical schema
- ☐ Fix Sridhar's careerspan_score: null → 80
- ☐ Test: Both outputs pass schema validation

### Phase 4: Documentation & Quality Gates
- ☐ Update SKILL.md with canonical schema
- ☐ Update DATA-QUALITY-METHODOLOGY.md with score extraction step
- ☐ Add pre-commit schema validation to skill
- ☐ Test: End-to-end decompose produces valid output

---

## Phase 1: Define Canonical Schema & Extraction Prompt

### Affected Files
- `Skills/careerspan-decomposer/assets/canonical_schema.json` - CREATE - JSON Schema for scores_complete
- `Skills/careerspan-decomposer/scripts/decompose.py` - UPDATE - Add EXTRACTION_PROMPTS["skills_assessment"]

### Changes

**1.1 Create Canonical Schema:**

The canonical schema for `scores_complete.json` entries:

```json
{
  "skill_name": "string",           
  "category": "Responsibility|Hard Skill|Soft Skill",
  "rating": "Excellent|Good|Fair|Gap",
  "required_level": "Novice|Intermediate|Advanced|Expert",
  "required_score": 4,              
  "max_score": 5,                   
  "importance": 10,                 
  "max_importance": 10,             
  "evidence_type": "Story+profile|Profile|Resume|Gap",
  "our_take": "string",
  "support": [                      
    {
      "source": "story_id_string",
      "type": "Direct|Transferable",
      "score": "9/10",
      "rating": "Excellent"
    }
  ],
  "source_page": "page-N"           
}
```

Key decisions:
- Use `skill_name` (not `skill`) - matches JD naming
- All numeric fields are numbers (not "4/5" strings)
- `support[]` array for multiple evidence sources (not single `story_id`)
- `source_page` for provenance tracking
- `max_score` and `max_importance` always present for denominator clarity

**1.2 Update Overview Extraction:**

Add to overview prompt: Look for score in "Referred {N} ©" pattern where N is 0-100.

### Unit Tests
- `python3 -c "import jsonschema; ..."` validates schema is valid JSON Schema
- Schema can validate a sample entry from each output

---

## Phase 2: Update decompose.py

### Affected Files
- `Skills/careerspan-decomposer/scripts/decompose.py` - UPDATE - Add skills extraction

### Changes

**2.1 Add Skills Assessment Extraction Prompt:**

Create `EXTRACTION_PROMPTS["skills_assessment"]` that:
- Extracts ALL skills from the Deep Dive section
- Captures rating, required_level, importance, evidence_type
- Preserves "Our Take" narrative verbatim
- Captures support evidence with story IDs
- Notes source page for provenance

**2.2 Add Schema Validation:**

After extraction, validate output against canonical schema.
- Use `jsonschema` library
- Fail loudly if schema doesn't match
- Log warnings for any coerced values

**2.3 Fix Overview Score Extraction:**

Parse "Referred {N} ©" from OCR to get careerspan_score.
Regex pattern: `Referred\s+(\d+)\s+©`

### Unit Tests
- Extract skills from Hardik OCR, verify count matches (45)
- Extract skills from Sridhar OCR, verify count matches (33)
- careerspan_score extracted correctly (89, 80)

---

## Phase 3: Backfill Existing Outputs

### Affected Files
- `Careerspan/meta-resumes/inbox/hardik-flowfuse/scores_complete.json` - UPDATE - Normalize schema
- `Careerspan/meta-resumes/inbox/hardik-flowfuse/overview.yaml` - VERIFY - Score present
- `Careerspan/meta-resumes/inbox/sridhar-flowfuse/scores_complete.json` - UPDATE - Normalize schema
- `Careerspan/meta-resumes/inbox/sridhar-flowfuse/overview.yaml` - UPDATE - Add score: 80

### Changes

**3.1 Normalize Hardik:**
- Rename `skill` → `skill_name`
- Convert `required_score: "4/5"` → `required_score: 4, max_score: 5`
- Convert `importance: "10/10"` → `importance: 10, max_importance: 10`
- Convert `story_id` + `evidence_rating` → `support[]` array
- Add `source_page` field (can be null if unknown)

**3.2 Normalize Sridhar:**
- Already has better schema, just needs minor cleanup
- Fix `careerspan_score: null` → `80` in overview.yaml
- Add `career_trajectory: "Career Pivot"` (was in OCR)

### Unit Tests
- Both files pass schema validation
- Hardik: 45 skills, careerspan_score: 89
- Sridhar: 33 skills, careerspan_score: 80

---

## Phase 4: Documentation & Quality Gates

### Affected Files
- `Skills/careerspan-decomposer/SKILL.md` - UPDATE - Document canonical schema
- `Skills/careerspan-decomposer/references/DATA-QUALITY-METHODOLOGY.md` - UPDATE - Add score extraction
- `Skills/careerspan-decomposer/scripts/validate_output.py` - CREATE - Validation script

### Changes

**4.1 Update SKILL.md:**
- Add canonical schema documentation
- Add validation step to Quick Start

**4.2 Update Methodology:**
- Add Phase 3.5: Score Extraction (before Phase 4)
- Document the "Referred N ©" pattern for score
- Add schema validation to Phase 6

**4.3 Create Validation Script:**
```bash
python3 validate_output.py --dir <decomposed_dir>
# Returns 0 if valid, 1 if schema violations
```

### Unit Tests
- `validate_output.py` passes on both normalized outputs
- `validate_output.py` fails on pre-fix outputs (detecting the drift)

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `assets/canonical_schema.json` | D1.1 | ✓ |
| `decompose.py` (prompts + extraction) | D1.1 | ✓ |
| `decompose.py` (validation + score parsing) | D1.1 | ✓ |
| `hardik-flowfuse/scores_complete.json` | D1.2 | ✓ |
| `hardik-flowfuse/overview.yaml` | D1.2 | ✓ |
| `sridhar-flowfuse/scores_complete.json` | D1.2 | ✓ |
| `sridhar-flowfuse/overview.yaml` | D1.2 | ✓ |
| `SKILL.md` documentation | D1.3 | ✓ |
| `DATA-QUALITY-METHODOLOGY.md` | D1.3 | ✓ |
| `validate_output.py` | D1.3 | ✓ |

### Token Budget Summary

| Worker | Scope | Estimated % | Status |
|--------|-------|-------------|--------|
| D1.1 | Schema + decompose.py | ~15% | ✓ |
| D1.2 | Backfill 2 outputs | ~10% | ✓ |
| D1.3 | Docs + validation | ~10% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (D1.1 and D1.2 parallel; D1.3 after both for validation)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | D1.1 | Schema + Extraction Engine | `workers/D1.1-schema-extraction.md` |
| 1 | D1.2 | Backfill Existing Outputs | `workers/D1.2-backfill-outputs.md` |
| 2 | D2.1 | Documentation + Validation | `workers/D2.1-docs-validation.md` |

Wave 1 workers run in parallel. Wave 2 depends on Wave 1 completion.

---

## Success Criteria

1. **Schema Consistency:** Both Hardik and Sridhar pass identical schema validation
2. **Score Present:** Sridhar's `careerspan_score` is 80, Hardik's is 89
3. **Field Names Standardized:** All outputs use `skill_name`, `support[]`, numeric types
4. **Skill Counts Preserved:** Hardik: 45, Sridhar: 33 (no data loss)
5. **Decomposer Updated:** Running `decompose.py` produces schema-valid output
6. **Validation Gate:** `validate_output.py` exists and passes on both outputs

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| OCR quality varies, score not always in "Referred N" pattern | Add fallback extraction from other locations; flag if not found |
| Backfill loses data during transformation | Validate skill count and "Our Take" length before/after |
| Schema too rigid for future briefs | Use JSON Schema with `additionalProperties: true` for flexibility |

---

## Level Upper Review

*Skipped for this build — scope is well-defined fix, not architectural exploration.*

---

## Alternatives Considered

### A1: Rebuild outputs from scratch via re-extraction
**Rejected:** Would lose nuanced "Our Take" narratives that may have been manually refined

### A2: Keep both schemas, add adapter layer
**Rejected:** Complects the system; better to normalize to one canonical schema

### A3: Wait for Careerspan API (skip OCR entirely)
**Rejected:** API timing uncertain; need working system now

**Selected:** Canonical schema + backfill + validation gates
