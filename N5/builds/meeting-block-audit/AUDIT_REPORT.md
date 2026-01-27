---
created: 2026-01-26
provenance: meeting-block-audit
---

# Meeting Intelligence Block Quality Audit Report

## Executive Summary

A critical quality degradation was identified in the meeting intelligence block generation system. Of 20 scanned meetings, 18 have severely degraded blocks with missing frontmatter, block names, IDs, and provenance. The root cause was the creation of a new processor that bypassed the canonical prompt system, using hardcoded inline prompts instead of the proven `Prompts/Blocks/` files.

## Root Cause Analysis

**Timeline of Events:**
- **2026-01-26 21:10:55 UTC**: Skills/meeting-ingestion/SKILL.md created  
- **2026-01-26 23:21:00 UTC**: processor.py created with inline BLOCK_DEFINITIONS
- **2026-01-26 (unknown time)**: 13 legacy meeting prompts deleted from system
- **Never**: Skill was never committed to git

**Root Cause**: The new `Skills/meeting-ingestion/scripts/processor.py` was written from scratch with hardcoded BLOCK_DEFINITIONS, completely bypassing the proven canonical prompt system in `Prompts/Blocks/`. While 37 canonical prompt files exist and are actively used by other scripts (`worker_generate_blocks.py`, `generate_blocks.py`), the new processor implemented a parallel system with inferior prompts.

**Contributing Factors:**
- No cross-reference between new skill and existing prompt loading logic
- Skill development bypassed existing infrastructure
- No testing to verify prompt quality before deployment

## Impact Assessment

| Category | Count |
|----------|-------|
| Meetings with degraded blocks | 18 |
| Meetings with good blocks | 1 |
| Meetings with no blocks | 1 |
| Total blocks affected | 198 |

### Affected Meetings (Priority Order)

**External/Business Critical:**
1. **2026-01-19_Careerspan-corridorx-scoping** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
2. **2026-01-20_Futurefit-x-careerspan** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded  
3. **2026-01-19_David-x-careerspan** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
4. **Vrijen Attawar - Zoom with RBV (Dan and Gus)** — B01, B02, B03, B05, B08, B25, B26, B28 degraded

**External/Personal:** 
5. **2026-01-19_Chat-with-ben-zo-cofounder-vrijen-attawar** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
6. **2026-01-21_Zain-x-vrijen-attawar** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
7. **2026-01-20_Trinayaan-hariharan-x-vrijen-attawar** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded

**Internal/Team Meetings:**
8. **2026-01-19_Trio-standup-1** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
9. **2026-01-20_Trio-standup** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded
10. **2026-01-21_Grind-oclock** — B01, B03, B05, B06, B07, B14, B21, B25, B26, B32 degraded

**Good Quality Reference:**
- **2026-01-23_Anna-bao** — Properly formatted blocks with frontmatter and provenance

## Fix Applied

**Changes Made to `Skills/meeting-ingestion/scripts/processor.py`:**
- Added `load_prompt_file()` function to load canonical prompts from `Prompts/Blocks/`
- Modified `generate_block()` to try canonical prompts first with transcript and context injection
- Preserved fallback to inline BLOCK_DEFINITIONS for blocks without prompt files
- 37 lines changed across 2 functions

**Verification Results:**
- 13 canonical prompt files successfully loaded: B01, B02, B03, B04, B05, B06, B07, B08, B10, B13, B21, B25, B26
- 1 fallback block (B28_STRATEGIC_INTELLIGENCE) uses inline definition as expected
- No prompt file exists for B28, confirming fallback logic works correctly

## Recommendations

**Immediate Priority (External/Business Critical):**
1. **Regenerate Careerspan business meetings** — corridorx scoping, Futurefit partnership, David consultation
2. **Regenerate RBV investor meeting** — Dan and Gus zoom session

**High Priority (External Contacts):**
3. **Regenerate Ben Zo cofounder meeting** — Important strategic conversation 
4. **Regenerate partner meetings** — Zain and Trinayaan sessions

**Medium Priority (Internal Operations):**
5. **Regenerate team standups** — Trio standup meetings from Jan 19-20
6. **Consider regenerating** other internal meetings based on available time

**Optional/Low Priority:**
- Internal grind sessions and informal meetings can remain as-is if resources are constrained
- Meetings older than one week can be left with existing blocks

## Prevention

**Immediate Actions:**
1. **Commit `Skills/meeting-ingestion/` to git** — Ensure version control tracking
2. **Add integration test** — Verify prompt files are being loaded and used correctly
3. **Document prompt system** — Update skill documentation to reference canonical prompt usage

**Process Improvements:**
1. **Skill review checklist** — Verify new skills use existing infrastructure before deployment
2. **Prompt quality gates** — Test block output quality before replacing existing systems
3. **Infrastructure discovery** — Standard practice to grep for existing implementations before creating new ones
4. **Cross-reference validation** — Automated checks to ensure new code leverages existing proven components

**Technical Debt:**
1. **Consolidate prompt systems** — Single canonical approach for all block generation
2. **Prompt versioning** — Track changes to prompt files for quality regression detection
3. **Block quality metrics** — Automated scoring of generated block quality