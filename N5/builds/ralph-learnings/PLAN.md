---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_XeyS1O97Kcg1Aemq
---

# Ralph Learnings Implementation

## Executive Summary

Implement key learnings from the "Ralph Wiggum" AI coding technique into N5's build orchestrator system. Ralph's core insight: **progress in files, not context** — run agents in loops with automated validation ("backpressure") until specifications are met.

**What we already have that aligns with Ralph:**
- SESSION_STATE.md (progress in files ✓)
- Build orchestrator with worker briefs (specification-driven ✓)
- MECE validation (structural validation ✓)
- Build lesson ledger (cross-worker learning ✓)

**What Ralph teaches us we're missing:**
1. **Automated backpressure** — validation gates that reject invalid work before human review
2. **Struggle detection** — recognize when an agent is spinning without progress
3. **Loop infrastructure** — tooling to run agents in loops with fresh context
4. **Orchestrator integration** — wire these into the existing build flow

## Scope

### In Scope
- Backpressure validation script (tests, lint, type checks, custom validators)
- Struggle detection script (pattern recognition for spinning)
- Loop runner script (Ralph-style iteration with fresh context)
- Protocol updates to integrate these into orchestrator workflow
- Dashboard/visibility for loop status

### Out of Scope
- Persona refactoring (separate effort)
- Changes to conversation-end workflows
- New scheduled tasks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BUILD ORCHESTRATOR                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │
│  │   PLAN.md   │──▶│   Workers   │──▶│ Completions │        │
│  └─────────────┘   └──────┬──────┘   └─────────────┘        │
│                           │                                  │
│         ┌─────────────────▼─────────────────┐               │
│         │         BACKPRESSURE GATE          │               │
│         │  ┌───────┐ ┌──────┐ ┌───────────┐ │               │
│         │  │ Tests │ │ Lint │ │ Custom    │ │               │
│         │  └───────┘ └──────┘ └───────────┘ │               │
│         └─────────────────┬─────────────────┘               │
│                           │                                  │
│              ┌────────────▼────────────┐                    │
│              │   STRUGGLE DETECTOR     │                    │
│              │  • Repetition patterns  │                    │
│              │  • No-progress cycles   │                    │
│              │  • Error loops          │                    │
│              └────────────┬────────────┘                    │
│                           │                                  │
│              ┌────────────▼────────────┐                    │
│              │      LOOP RUNNER        │                    │
│              │  • Fresh context start  │                    │
│              │  • Iteration tracking   │                    │
│              │  • Auto-retry on fail   │                    │
│              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

## Workers

### Wave 1 (Parallel — No Dependencies)

#### W1.1: Backpressure Validation Script
**Scope:** Create `N5/scripts/backpressure.py` — unified validation gate

**Files owned:**
- `N5/scripts/backpressure.py` (create)
- `N5/config/backpressure_rules.yaml` (create)

**Must do:**
1. Accept a build slug or file path as input
2. Run configurable validators: pytest, ruff/flake8, mypy, custom scripts
3. Return structured result: PASS/WARN/FAIL with details
4. Support per-build config overrides via `backpressure.yaml` in build folder
5. Exit codes: 0=pass, 1=warn, 2=fail

**Must not do:**
- Modify any files (read-only validation)
- Block on missing optional validators

**Deliverable:** Working script with `--help`, tested on existing build

---

#### W1.2: Struggle Detection Script
**Scope:** Create `N5/scripts/struggle_detector.py` — detect spinning agents

**Files owned:**
- `N5/scripts/struggle_detector.py` (create)
- `N5/config/struggle_patterns.yaml` (create)

**Must do:**
1. Analyze DEBUG_LOG.jsonl for circular patterns (same error 3+ times)
2. Analyze SESSION_STATE.md for stalled progress (same % for N updates)
3. Analyze git log for revert-apply cycles
4. Return: HEALTHY/STRUGGLING/STUCK with evidence
5. Configurable thresholds via YAML

**Must not do:**
- Take corrective action (detection only)
- Require DEBUG_LOG to exist (graceful degradation)

**Deliverable:** Working script with `--help`, pattern library in YAML

---

#### W1.3: Loop Runner Script
**Scope:** Create `N5/scripts/loop_runner.py` — Ralph-style iteration

**Files owned:**
- `N5/scripts/loop_runner.py` (create)
- `N5/templates/loop_prompt.md` (create)

**Must do:**
1. Accept: prompt file, max iterations, success criteria
2. Each iteration: fresh /zo/ask call with full prompt
3. Between iterations: run backpressure validation
4. Stop conditions: backpressure passes, max iterations, struggle detected
5. Log each iteration to `N5/builds/<slug>/loop_history.jsonl`
6. Support --dry-run to show what would execute

**Must not do:**
- Run without explicit --execute flag (safety)
- Exceed 20 iterations without human confirmation

**Deliverable:** Working script with `--help`, integration with backpressure.py

---

### Wave 2 (Depends on Wave 1)

#### W2.1: Protocol Integration
**Scope:** Update orchestrator protocol and create visibility tooling

**Files owned:**
- `N5/prefs/operations/orchestrator-protocol.md` (modify)
- `N5/prefs/operations/backpressure-protocol.md` (create)
- `N5/scripts/build_dashboard.py` (create)

**Depends on:** W1.1, W1.2, W1.3

**Must do:**
1. Add backpressure gate to orchestrator protocol (when to run, how to respond)
2. Add struggle detection checkpoint to protocol
3. Document loop runner usage for stuck workers
4. Create simple CLI dashboard showing: build status, backpressure results, struggle status
5. Update BUILD.md template to include backpressure config section

**Must not do:**
- Change existing MECE or worker brief formats
- Remove any existing protocol steps

**Deliverable:** Updated protocols, working dashboard script

---

## MECE Validation

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/scripts/backpressure.py` | W1.1 | ✓ |
| `N5/config/backpressure_rules.yaml` | W1.1 | ✓ |
| `N5/scripts/struggle_detector.py` | W1.2 | ✓ |
| `N5/config/struggle_patterns.yaml` | W1.2 | ✓ |
| `N5/scripts/loop_runner.py` | W1.3 | ✓ |
| `N5/templates/loop_prompt.md` | W1.3 | ✓ |
| `N5/prefs/operations/orchestrator-protocol.md` | W2.1 | ✓ |
| `N5/prefs/operations/backpressure-protocol.md` | W2.1 | ✓ |
| `N5/scripts/build_dashboard.py` | W2.1 | ✓ |

**Overlaps:** None
**Gaps:** None

## Token Estimates

| Worker | Brief (~tokens) | File Reads (~tokens) | Total % |
|--------|-----------------|---------------------|---------|
| W1.1 | 1,500 | 2,000 (validation.py ref) | ~1.8% |
| W1.2 | 1,500 | 3,000 (debug_logger, session_state) | ~2.3% |
| W1.3 | 2,000 | 4,000 (backpressure, /zo/ask docs) | ~3.0% |
| W2.1 | 2,500 | 5,000 (all Wave 1 outputs + protocols) | ~3.8% |

All within budget (<40%).

## Success Criteria

1. `python3 N5/scripts/backpressure.py <slug>` runs and returns structured validation
2. `python3 N5/scripts/struggle_detector.py --convo-id <id>` detects known struggle patterns
3. `python3 N5/scripts/loop_runner.py --prompt <file> --dry-run` shows execution plan
4. Updated orchestrator protocol includes backpressure and struggle checkpoints
5. Dashboard shows consolidated build health view

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Loop runner could be expensive | Require --execute flag, max iterations, human confirmation at 20 |
| Backpressure too strict | Start with WARN-only mode, graduate to FAIL |
| Struggle detection false positives | Tunable thresholds, evidence required |

## Notes

- This is infrastructure work — the payoff comes from using it on future builds
- Ralph's "sit on the loop, not in it" means V monitors, doesn't micromanage
- Fresh context is key — loop_runner uses /zo/ask for clean sessions
