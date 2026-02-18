---
created: 2026-02-11
last_edited: 2026-02-11
version: 1.0
provenance: con_i1iw8n1WM8ldPi9L
---

# Build Plan: SkillRL Integration

## Objective

Implement the "recursive skill-augmented" pattern from SkillRL research using a compressed architecture that leverages existing infrastructure.

## Background

SkillRL (arXiv:2602.08234) demonstrates that LLM agents improve significantly when they:
1. Distill experiences into reusable skills (not just store raw trajectories)
2. Adaptively retrieve both general and task-specific heuristics
3. Recursively evolve the skill library based on validation results

**Our insight:** We already have 80% of this infrastructure:
- `BUILD_LESSONS.json` = experience store
- `Skills/` = skill library (SkillBank)
- `build-close` / `thread-close` = distillation trigger points
- `DEBUG_LOG.jsonl` = failure signal for evolution

**Gap:** No automated experience → skill promotion, no evolution loop.

## Architecture

```
Experience Capture (EXISTING)          Skill Extraction (NEW: D1.1)
┌─────────────────────────────┐       ┌─────────────────────────────┐
│ BUILD_LESSONS.json          │──────▶│ skill_extractor.py          │
│ thread-close learnings      │       │ - Classify scope            │
│ DEBUG_LOG.jsonl             │       │ - Check similarity          │
└─────────────────────────────┘       │ - Generate candidates       │
                                      └──────────────┬──────────────┘
                                                     │
                                                     ▼
                                      ┌─────────────────────────────┐
                                      │ N5/review/skills/           │
                                      │ YYYY-MM-DD_candidates.md    │
                                      └──────────────┬──────────────┘
                                                     │
                                              V reviews (HITL)
                                                     │
                                                     ▼
Skill Library (EXISTING)              Evolution Loop (NEW: D1.2)
┌─────────────────────────────┐       ┌─────────────────────────────┐
│ Skills/                     │◀──────│ skill_evolution.py          │
│ - Enhanced frontmatter      │       │ - Usage tracking            │
│ - scope/provenance fields   │       │ - Staleness detection       │
│ - usage_count tracking      │       │ - Failure pattern analysis  │
└─────────────────────────────┘       │ - Weekly digest agent       │
                                      └─────────────────────────────┘
```

## Phase 1: Core Implementation

### Wave 1 (Parallel)

| Drop | Name | Stream | Blocking |
|------|------|--------|----------|
| D1.1 | Skill Extractor Script + Close Integration | 1 | Yes |
| D1.2 | Evolution Agent + SKILL.md Frontmatter | 2 | Yes |

Both Drops can run in parallel — no dependencies between them.

## Open Questions

- [x] Where to store skill candidates? → `N5/review/skills/`
- [x] How to track usage? → Convention-based: Zo calls `skill_usage.py record`
- [x] How aggressive on staleness? → 60 days unused = stale candidate
- [x] Deprecation flow? → Move to `Skills/_archived/`

## Success Criteria

1. **Extraction works:** BUILD_LESSONS → skill candidates automatically
2. **Deduplication works:** Similar skills detected, flagged as refinements
3. **Evolution runs:** Weekly digest surfaces stale/unhealthy skills
4. **HITL preserved:** V approves all skill additions/removals
5. **Minimal footprint:** 2 new scripts, 1 spec doc, 1 scheduled agent

## Risks

| Risk | Mitigation |
|------|------------|
| Noisy candidates overwhelm V | Confidence threshold filters low-quality |
| Usage tracking not called | It's a convention; Zo's rules remind to track |
| Evolution agent too verbose | Digest is summary, not exhaustive |

## Timeline

Estimated: 4-6 hours total (2-3 hours per Drop)

## Related Files

- `file 'Skills/pulse/SKILL.md'` — Pulse orchestration
- `file 'Skills/build-close/SKILL.md'` — Build close flow
- `file 'Skills/thread-close/SKILL.md'` — Thread close flow
- `file 'N5/prefs/operations/debug-logging-auto-behavior.md'` — DEBUG_LOG discipline
