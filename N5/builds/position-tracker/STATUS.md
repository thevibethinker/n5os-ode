---
created: 2025-12-26
last_edited: 2025-12-27
build_slug: position-tracker
provenance: con_fCxNsgBS9Vw33X2k
---

# Build Status: Position Tracking System (v3 Simplified)

## Quick Status

| Metric | Value |
|--------|-------|
| **Overall Progress** | 75% (MVP ready for use) |
| **Current Phase** | Checkpoint |
| **Blocked?** | No |
| **Plan File** | `N5/builds/position-tracker/PLAN_V3_SIMPLIFIED.md` |

## Phase Progress

- [x] Plan drafted (v1)
- [x] Level Upper review
- [x] Strategic analysis (v2)
- [x] Option A selected: Use existing positions.db
- [x] **Plan v3 finalized (simplified)**
- [x] **Phase 1: B32 Extractor** ✅
- [x] **Phase 3: Triage Prompt** ✅
- [x] Quality gate passed (15 candidates from 5 files, <30% noise)
- [ ] ⏸️ **CHECKPOINT**: Use for 2 weeks
- [ ] Phase 4: Dedup enhancement (post-checkpoint)
- [ ] Phase 5+: Tension detection, daily agent (if needed)

## Artifacts Created

| File | Purpose |
|------|---------|
| `N5/builds/position-tracker/PLAN_V3_SIMPLIFIED.md` | Simplified plan using positions.db |
| `N5/scripts/b32_position_extractor.py` | Extracts candidates from B32 blocks |
| `N5/prompts/extract_positions_from_b32.md` | LLM prompt for extraction |
| `N5/data/position_candidates.jsonl` | Staging area for triage |
| `N5/data/b32_processed.jsonl` | Tracks processed B32 files |
| `Prompts/Position Triage.prompt.md` | Interactive triage interface |

## How to Use

### Extract candidates from B32s
```bash
# Scan recent B32 files
python3 N5/scripts/b32_position_extractor.py scan --limit 10

# Or extract from specific file
python3 N5/scripts/b32_position_extractor.py extract <path/to/B32.md>
```

### Triage candidates
```bash
# See pending candidates
python3 N5/scripts/b32_position_extractor.py list-pending

# Approve: add to positions.db
python3 N5/scripts/positions.py add --domain <domain> --title "<title>" --insight "<claim>" --stability emerging

# Mark candidate as approved/rejected
python3 N5/scripts/b32_position_extractor.py mark <cand_id> approved
python3 N5/scripts/b32_position_extractor.py mark <cand_id> rejected
```

### Query positions
```bash
python3 N5/scripts/positions.py list
python3 N5/scripts/positions.py search "query"
```

## Activity Log

| Timestamp | Event |
|-----------|-------|
| 2025-12-26 | Build initialized |
| 2025-12-26 | Architect drafted plan v1 |
| 2025-12-26 | Level Upper review completed |
| 2025-12-27 | Strategic analysis: B32 extraction test (76% yield) |
| 2025-12-27 | **Decision: Option A (use existing positions.db)** |
| 2025-12-27 | Plan v3 simplified created |
| 2025-12-27 | Phase 1 built: b32_position_extractor.py |
| 2025-12-27 | Phase 3 built: Position Triage prompt |
| 2025-12-27 | Quality gate passed: 15 candidates from 5 B32s |
| 2025-12-27 | **MVP COMPLETE - entering checkpoint** |

## Checkpoint Criteria

Use system for 2 weeks, then assess:
- [ ] Is extraction quality good?
- [ ] Is triage sustainable?
- [ ] Do we need deduplication enhancement?
- [ ] Do we need tension detection?
- [ ] Do we need daily agent automation?

## Notes

Simplified from original 12-hour plan to ~3 hour implementation by leveraging existing `positions.py` infrastructure.



---

## Graduation Status

| Field | Value |
|-------|-------|
| **Graduated** | ✅ Yes |
| **Graduation Date** | 2026-01-09 |
| **Capability Doc** | `N5/capabilities/internal/position-tracker.md` |

This build has been graduated to the capability registry. The capability doc is now the source of truth for "what this does."

## GRADUATED

- **Date:** 2026-01-09
- **Capability Doc:** `N5/capabilities/internal/position-tracker.md`
- **Provenance:** con_JS1OqPU9pbYCCCjI
