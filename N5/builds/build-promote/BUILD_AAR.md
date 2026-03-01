# After-Action Report: build-promote

## Build Overview

| Field | Value |
|-------|-------|
| Slug | `build-promote` |
| Title | Build Promote — Build-to-Skill Finalization Skill |
| Status | Complete (5/5 drops) |
| Duration | Single session (2026-02-21) |
| Execution Mode | Claude Code (Pulse orchestration) |
| Waves | 3 (W1: Analysis, W2: Promotion, W3: Integration) |

## Execution Timeline

| Wave | Drops | Duration | Notes |
|------|-------|----------|-------|
| W1 | D1.1 + D1.2 (parallel) | ~3 min | Both analysis scripts written and tested |
| W2 | D2.1 + D2.2 (parallel) | ~3 min | Promotion executor and verification suite |
| W3 | D3.1 (sequential) | ~6 min | SKILL.md + E2E test + debug pass |

## What Went Well

1. **Pulse orchestration worked smoothly** — meta.json format needed fixing (contract check expected dict waves, not list), but once corrected, the execute→deposit→advance flow was seamless.
2. **E2E validation caught real issues** — promoting `builds-audit-cleanup` and running verify on `zode-moltbook` revealed actual problems (stale pycache, SKILL.md false positives).
3. **verify.py proved its value immediately** — the debug pass used verify.py to find and fix issues in the very build that created it (self-referential validation).
4. **Lineage clustering works well** — simple prefix matching after stripping version suffixes correctly identified all 7 multi-build chains.

## What Could Be Better

1. **meta.json schema confusion** — The `init_build.py` script creates a different meta.json schema than what `build_contract_check.py` expects. Had to manually fix waves (list→dict) and add a `drops` key. Consider standardizing.
2. **verify.py self-reference complexity** — 4 rounds of refinement needed for the stale path checker to not flag its own detection logic. The final heuristic (quote counting + docstring tracking) works but is fragile.
3. **Pycache bootstrapping problem** — verify.py runs `--help` on all scripts, which creates `__pycache__`. The bytecode check then fails. Fixed by auto-cleaning after script health check, but this is a workaround.
4. **No automated test suite** — All testing was manual (--help checks, functional runs). A proper test suite would catch regressions.

## Architecture Decisions

### Why 4 scripts instead of 1?

Separation of concerns: analysis (scan/classify) is read-only and reusable independently; promotion (migrate/verify) is write-heavy and destructive. A monolith would be harder to test and debug.

### Why stdlib-only?

V's maintenance burden. No `pip install` required, no dependency drift, no virtual environments. These scripts are infrastructure — they must be rock-solid and zero-dependency.

### Why copy-then-delete instead of move?

Safety. If the copy fails, the originals are untouched. The cleanup step only runs after all copies succeed. This follows P05 (Safety, Determinism, and Anti-Overwrite).

## Pedagogical Review

### Concepts Engaged

| Concept | Drops That Exercised It | Demonstrated Level |
|---------|------------------------|-------------------|
| Build lifecycle management | D1.1, D2.1, D3.1 | Familiar |
| File system abstraction patterns | D1.2, D2.1 | Familiar |
| CLI tool design (argparse) | All drops | Practiced |
| Path adaptation / string replacement | D2.1 | Familiar |
| Self-referential system design | D2.2, D3.1 | Learning |
| Verification / testing patterns | D2.2, D3.1 | Familiar |
| Pulse orchestration | All drops | Practiced |

### Application Questions

1. If you wanted to promote a build that has scripts importing from *other* builds (cross-build dependencies), how would the path adaptation logic need to change? What new failure modes would that introduce?

2. The lineage analyzer uses simple prefix matching for clustering. What would break if two unrelated builds happened to share a prefix (e.g. `store-v2` and `store-cleanup`)? How would you make clustering more robust without over-engineering?

3. The `state/` convention separates runtime data from code. But what happens when a skill's state grows very large (GB-scale analytics)? At what point should state move to a different abstraction (database, object store), and how would you design that transition?

### Next Learning Frontier

- **Cross-build dependency resolution** — handling builds that reference each other's outputs
- **Incremental promotion** — promoting parts of a build while it's still active
- **State migration patterns** — handling schema changes in `state/` data as skills evolve
