---
created: 2025-12-27
last_edited: 2025-12-28
version: 2.0
provenance: con_vU0lAa14Y6aRjVTI
---

# Position Extraction v2: Build Status

## Overall: ✅ COMPLETE

All phases executed successfully.

## Phase Summary

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Schema Expansion | ✅ | `reasoning`, `stakes`, `conditions` fields added |
| Prompt Rewrite | ✅ | Principle-grounded extraction prompt |
| Re-extraction | ✅ | 96 positions promoted (v2 quality) |
| Brain Integration | ✅ | 106 positions indexed, semantic search working |
| Tension Detection | ✅ | `tension_detector.py`, 2 tensions tracked |
| Weekly Triage Agent | ✅ | Daily extraction + weekly SMS notification |

## Current State

### positions.db
- Total positions: 106
- v2 positions: 97
- Original: 9
- Domains: careerspan (31), hiring-market (30), worldview (26), ai-automation (22), founder (4), epistemology (2)

### brain.db
- Position vectors: 106 (3072D, correct embedding model)
- Semantic search: Working

### _tensions.jsonl
- Total tensions: 2
- Unresolved: 2

### Scheduled Agents
1. **Daily B32 Position Extraction** (5:00 AM)
   - Extracts from new B32s
   - Runs tension scan
   - Silent unless errors

2. **Weekly Position Triage Summary** (Sunday 6:00 PM)
   - SMS notification with candidate count
   - Triggers manual triage session

## Test Results

**Semantic Query Test:**
- Query: "What do I think about recruiting and hiring?"
- Result: 5 relevant positions returned
- Score range: 0.59-0.70

**Tension Detection Test:**
- Found: AI compression vs information standstill tension
- Working as expected

## Files Created/Modified

- `N5/scripts/b32_position_extractor.py` (modified)
- `N5/scripts/tension_detector.py` (created)
- `N5/scripts/positions.py` (modified)
- `N5/prompts/extract_positions_from_b32.md` (rewritten)
- `N5/data/positions.db` (schema expanded)
- `Knowledge/positions/_tensions.jsonl` (created)

## Next Steps (User-Driven)

1. Weekly triage sessions via `@Position Triage`
2. Resolve detected tensions
3. Promote working positions → cornerstone
4. Query positions: "What do I think about X?"


