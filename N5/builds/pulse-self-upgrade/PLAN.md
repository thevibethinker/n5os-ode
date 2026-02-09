---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_BjZjM1PHgM7UO3tZ
---

# Build Plan: Pulse Self-Upgrade

## Objective

Use Pulse v1 to upgrade itself with 4 new capabilities derived from Claude Agent Teams analysis:
1. Forward Broadcast — inter-Drop information propagation
2. Hypothesis Racing — first-wins parallel debugging
3. Delegate-Only Mode — orchestrator coordination discipline
4. Dynamic Task Claiming — shared task pool for workers

**Build Slug:** `pulse-self-upgrade`
**Build Type:** `code_build`
**Risk Level:** Medium (modifying the orchestration system mid-flight)

## Safety Measures

1. **Git snapshot before start** — `pulse_safety.py snapshot pulse-self-upgrade`
2. **Delegate-only mode for orchestrator** — orchestrator reviews deposits but does NOT directly edit pulse.py
3. **Each Drop tests its own changes** before depositing
4. **W2 integration tests** verify all features work together

## Phase 1

Wave 1 builds all 4 features in parallel (D1.1-D4.1). Wave 2 integrates and documents (D1.2, D2.2).

## Features to Build

| ID | Feature | Effort | Value | Dependencies |
|----|---------|--------|-------|--------------|
| F1 | Forward Broadcast | 2h | High | None |
| F2 | Hypothesis Racing | 2h | Medium | None |
| F3 | Delegate-Only Mode | 30m | Medium | None |
| F4 | Dynamic Task Claiming | 4-6h | Medium | None |

## Wave Structure

```
Wave 1 (parallel feature builds)
├── Stream 1: D1.1 (Forward Broadcast)
├── Stream 2: D2.1 (Hypothesis Racing)
├── Stream 3: D3.1 (Delegate-Only Mode - docs only)
└── Stream 4: D4.1 (Dynamic Task Claiming)

    ↓ (all W1 Drops must complete)

Wave 2 (integration & docs)
├── Stream 1: D1.2 (Integration Tests)
└── Stream 2: D2.2 (SKILL.md Comprehensive Update)
```

## Success Criteria

- [ ] Forward Broadcast: Deposits with `broadcast` field are injected into subsequent Drop briefs
- [ ] Hypothesis Racing: `first_wins: true` builds correctly stop remaining Drops when one confirms
- [ ] Delegate-Only Mode: SKILL.md documents the discipline; no code changes needed
- [ ] Dynamic Task Claiming: Drops can self-assign from `task_pool` atomically
- [ ] All integration tests pass
- [ ] SKILL.md updated with all new features

## Open Questions

- [x] Should broadcasts persist across Waves or reset? → Persist across entire build
- [x] How to handle task pool exhaustion? → Drop exits normally when pool empty
- [x] First-wins timeout? → No timeout; manual intervention if all fail

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Bug in Pulse breaks the build mid-flight | Git snapshot; can restore and finish manually |
| Features conflict during integration | W2 dedicated to integration testing |
| Self-referential confusion | Delegate-only discipline; orchestrator doesn't touch code |

## Estimated Duration

- W1: ~2-3 hours (parallel)
- W2: ~1-2 hours (integration)
- **Total:** 3-5 hours elapsed (assuming no major blockers)
