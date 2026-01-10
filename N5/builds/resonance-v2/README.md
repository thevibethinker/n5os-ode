---
created: 2026-01-10
last_edited: 2026-01-10
version: 1.0
---

# Resonance System V2

Enhance Context Graph with velocity tracking, cross-pollination detection, challenge resolution, idea genealogy, and external validation signals

## Objective

Surface the dynamics of V's intellectual landscape - what's rising, converging, under challenge, evolving, and externally validated

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_schema | schema_versioning | completed | - | 1h |
| worker_velocity | velocity_tracking | completed | worker_schema | 2h |
| worker_crosspoll | cross_pollination | completed | worker_schema | 2h |
| worker_challenge | challenge_resolution | completed | worker_schema | 1.5h |
| worker_genealogy | idea_genealogy | completed | worker_schema | 2h |
| worker_validation | external_validation | completed | worker_schema | 1.5h |
| worker_integration | report_integration | pending | worker_velocity, worker_crosspoll, worker_challenge, worker_genealogy, worker_validation | 1h |

## Key Decisions

- 14-day decay threshold (week-scale, not 48-hour)
- Velocity = simple week-over-week trend, no slope math
- External validation v1 = list validators only, credibility scoring deferred
- Schema versioning for resonance_index.json migration
- Cache metrics in resonance_index.json, compute incrementally

## Relevant Files

- `N5/builds/resonance-v2/PLAN.md`
- `N5/scripts/resonance/pattern_surfacer.py`
- `N5/scripts/resonance/evolution_tracker.py`
- `N5/data/resonance_index.json`
- `N5/data/edges.db`
