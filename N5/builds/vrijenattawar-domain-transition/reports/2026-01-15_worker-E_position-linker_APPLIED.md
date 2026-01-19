---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_jMjNq7rVETju9hz9
---

# Worker E — Position Linker v2 (Hybrid) — APPLIED

## Synthesis Decision

Combined Worker E (fast embedding similarity) + c3Qz-W2 (preserve existing, idempotent):
- **From E**: Embedding-based candidate discovery (no API cost)
- **From c3Qz-W2**: Preserve hand-crafted edges, idempotency, two-pass algorithm
- **Compromise**: Skip LLM relationship typing (too slow), use score-based tiers

## Algorithm

1. **Pass 1 (Strong)**: Add up to 3 edges at ≥0.80 similarity
2. **Pass 2 (Bridge)**: For remaining orphans, add up to 2 edges at ≥0.60
3. **Pass 3 (Fallback)**: For any still-orphaned, add top-1 neighbor if ≥0.25

## Results

| Metric | Before | After |
|--------|--------|-------|
| Total positions | 164 | 164 |
| Connected positions | 22 | **164** |
| Orphans | 142 | **0** |
| Total edges | 28 | **203** |

### Edge Breakdown by Type
- weakly_related: 86
- related: 36
- tangentially_related: 35
- strongly_related: 16
- prerequisite: 4
- supports: 4
- (+ other preserved hand-crafted: 22)

## Files

- Script: `N5/scripts/position_linker.py`
- Backup: `N5/data/backups/positions_20260115_234959_two_pass_apply.db`
- Database: `N5/data/positions.db` (updated with connections + embeddings)

## Success Criteria

- [x] Orphan count reduced from 142 to **0** (target was <10) ✅
- [x] All domains have connectivity ✅
- [x] No broken connections (all target_ids valid) ✅
- [ ] Mind Map shows visible connection lines (pending frontend verification)

## Next Step

Visit [vrijenattawar.com/mind](https://vrijenattawar.com/mind) to verify edges render in the graph visualization.
