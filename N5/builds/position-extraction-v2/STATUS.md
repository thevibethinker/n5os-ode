---
created: 2025-12-27
last_edited: 2026-01-03
version: 2.1
provenance: con_vU0lAa14Y6aRjVTI
---

# Position Extraction v2: Build Status

## Overall: 🚧 IN PROGRESS

Earlier status marked this build as complete, but Phase 4 (HITL review sheets + amend + recompute + reviewed-only promotion) was added later and is now being implemented.

## Phase Summary

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Schema Expansion | ✅ | `reasoning`, `stakes`, `conditions` fields added |
| Prompt Rewrite | ✅ | Principle-grounded extraction prompt |
| Re-extraction | ⚠️ | Prior claims existed; current pipeline is candidate-first and promotion is gated by HITL |
| Brain Integration | ⚠️ | Exists, but promotion + indexing is now downstream of review sheets |
| Tension Detection | ✅ | `tension_detector.py` present; tension scan runs |
| Phase 4: HITL Review Sheets | 🚧 | review sheet generate/ingest + amend overwrite + recompute wisdom |

## Current State (as of 2026-01-03)

### positions.db
- Total positions: (see `python3 N5/scripts/positions.py stats`)
- Note: bulk promotion is intentionally gated behind review sheets going forward.

### brain.db
- Semantic search exists; future indexing should follow reviewed-only promotion.

### Scheduled Agents
- Daily extraction exists; Phase 4 introduces desktop review sheets as the canonical HITL gate.

## Test Results

- Phase 4 unit tests: `pytest N5/tests/test_position_review_sheets.py` (passes)

## Next Steps

1. Generate review sheet: `python3 N5/scripts/b32_position_extractor.py review-sheet-generate --status pending --limit 10`
2. Edit the sheet on desktop (accept/amend/reject/hold)
3. Ingest decisions: `python3 N5/scripts/b32_position_extractor.py review-sheet-ingest <sheet.md>`
4. Promote reviewed: `python3 N5/scripts/b32_position_extractor.py promote-reviewed`



