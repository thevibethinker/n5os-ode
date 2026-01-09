# R-Block Framework: Claude Code Instructions

## Quick Start

From your terminal with Claude Code:

```bash
# See what workers are ready to run
python3 N5/scripts/build_orchestrator_v2.py ready --project r-block-framework

# Spawn a worker (Claude Code will read the assignment and execute)
claude "Execute the worker assignment in N5/builds/r-block-framework/workers/w01_foundation.md"

# Or run multiple in parallel (in separate terminals)
claude "Execute the worker assignment in N5/builds/r-block-framework/workers/w01_foundation.md" &
claude "Execute the worker assignment in N5/builds/r-block-framework/workers/w02_edge_infra.md" &
```

## Current Ready Workers

These have no dependencies and can run now:

1. **w01_foundation** — Base R-block template (est. 2 hrs)
2. **w02_edge_infra** — JSONL edge storage + query script (est. 1 hr)

## Workflow

1. **Check ready workers:**
   ```bash
   python3 N5/scripts/build_orchestrator_v2.py ready --project r-block-framework
   ```

2. **Spawn worker(s):**
   ```bash
   claude "Execute the worker assignment in N5/builds/r-block-framework/workers/<worker_id>.md"
   ```

3. **Worker marks itself complete** (last line of each assignment):
   ```bash
   python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker <worker_id>
   ```

4. **Check status / see what's unlocked:**
   ```bash
   python3 N5/scripts/build_orchestrator_v2.py status --project r-block-framework
   python3 N5/scripts/build_orchestrator_v2.py ready --project r-block-framework
   ```

## Dependency Graph

```
Layer 0 (parallel):
  w01_foundation ──┬──> w03_r04_pilot ──┬──> w04-w12 (R-blocks, parallel) ──> w14_orchestrator
  w02_edge_infra ──┴──> w13_rix ────────┘
```

## All Workers

| ID | Component | Dependencies | Status |
|----|-----------|--------------|--------|
| w01_foundation | Base Template | — | pending |
| w02_edge_infra | Edge Infrastructure | — | pending |
| w03_r04_pilot | R04 Market | w01 | pending |
| w04_r01 | R01 Personal | w01, w03 | pending |
| w05_r02 | R02 Learning | w01, w03 | pending |
| w06_r03 | R03 Strategic | w01, w03 | pending |
| w07_r05 | R05 Product | w01, w03 | pending |
| w08_r06 | R06 Synthesis | w01, w03 | pending |
| w09_r07 | R07 Prediction | w01, w03 | pending |
| w10_r08 | R08 Venture | w01, w03 | pending |
| w11_r09 | R09 Content | w01, w03 | pending |
| w12_r00 | R00 Emergent | w01, w03 | pending |
| w13_rix | RIX Integration | w01, w02, w03 | pending |
| w14_orchestrator | Process Reflection | w04-w13 | pending |

## Worker Assignment Files

Each worker has a self-contained assignment at:
```
N5/builds/r-block-framework/workers/<worker_id>.md
```

These files contain:
- Full context for the task
- Specific deliverables
- Completion criteria checklist
- Command to mark complete

