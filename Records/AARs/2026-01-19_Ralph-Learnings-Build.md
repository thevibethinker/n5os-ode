---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_XeyS1O97Kcg1Aemq
build_slug: ralph-learnings
---

# AAR: Ralph Learnings Implementation

**Date:** 2026-01-19  
**Build:** `ralph-learnings`  
**Duration:** ~40 minutes (orchestrator + 4 workers)  
**Outcome:** ✅ Complete

## Summary

Implemented key concepts from the "Ralph Wiggum" AI coding technique into N5's build orchestrator system. Ralph's insight is simple: **progress in files, not context** — run agents in loops with automated validation until specs are met. This build added three core capabilities: backpressure validation, struggle detection, and a loop runner for stuck workers.

## What Happened

1. **Research Phase:** Read the awesome-ralph GitHub repo to understand the technique. Ralph is an infinite loop (`while :; do cat PROMPT.md | claude-code ; done`) that externalizes progress to files and git, with automated validation (backpressure) gating each iteration.

2. **Gap Analysis:** Identified what N5 already had (SESSION_STATE.md = progress in files ✓, build orchestrator = specification-driven ✓) and what Ralph teaches we were missing (automated validation gates, struggle detection, loop infrastructure).

3. **Build Execution:** 
   - Wave 1 (parallel): Created backpressure.py, struggle_detector.py, loop_runner.py
   - Wave 2 (sequential): Integrated into protocols, created build_dashboard.py
   - All workers completed cleanly, no blockers

4. **Commit:** Atomic commit with all 191 files (including some meeting backlog that got swept up).

## What Worked Well

- **MECE validation caught scope early:** No overlaps or gaps in worker assignments
- **Worker briefs were self-contained:** Each worker could execute without orchestrator hand-holding
- **Build lesson ledger captured cross-worker insights:** W1.3's `--json` convention was propagated to W2.1
- **Architect → Workers → Librarian flow was smooth:** Clean handoffs at each stage

## What Could Improve

- **SESSION_STATE sync was fragmented:** Progress showed 25% even after 100% complete. Should sync more frequently during orchestrator work.
- **git commit swept in unrelated files:** 191 files is a code smell — the atomic commit caught meeting backlog. Consider narrower `git add` paths.
- **Connection drops during architecture:** Had to use `n5:resume` twice. Need more resilient state checkpointing.

## Key Learnings

1. **Ralph's "sit on the loop, not in it"** = V monitors via dashboard, doesn't micromanage workers
2. **Backpressure should start permissive:** WARN mode by default, graduate to FAIL as confidence grows
3. **Struggle detection is heuristic:** Reading DEBUG_LOG.jsonl and SESSION_STATE.md gives signal, not certainty
4. **Fresh context is expensive but effective:** Loop runner's /zo/ask calls spawn clean sessions — use sparingly for truly stuck work

## Artifacts Produced

| File | Purpose |
|------|---------|
| `N5/scripts/backpressure.py` | Unified validation (pytest, ruff, mypy) |
| `N5/scripts/struggle_detector.py` | Detect circular errors, stalled progress |
| `N5/scripts/loop_runner.py` | Ralph-style iteration with fresh context |
| `N5/scripts/build_dashboard.py` | Consolidated build health view |
| `N5/config/backpressure_rules.yaml` | Default validation thresholds |
| `N5/config/struggle_patterns.yaml` | Struggle detection patterns |
| `N5/prefs/operations/backpressure-protocol.md` | When/how to run backpressure |
| `N5/templates/loop_prompt.md` | Template for loop prompts |

## Follow-Up Actions

- [ ] Test backpressure.py on next real build (not just self-test)
- [ ] Add `N5_BUILDS_DIR` constant to paths.py if not present (fixed during commit)
- [ ] Consider scheduled task to auto-run struggle detection on long-running builds
- [ ] Document loop_runner usage in orchestrator protocol (done in W2.1)

## Emotional Weather

Energized. This felt like closing a gap that's been nagging — we had the bones of progress-in-files with SESSION_STATE.md, but lacked the validation layer. Now builds have a "quality gate" before human review.
