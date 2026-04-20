---
name: pulse
description: |
  Automated build orchestration system. Spawns headless Zo workers (Drops) in parallel Waves,
  monitors health, validates Deposits via LLM judgment, handles dead Drops, and escalates via SMS.
  Supports sequential Streams within Waves. Replaces manual Build Orchestrator for unattended execution.
---

# Pulse: Automated Build Orchestration

## Overview

Pulse orchestrates complex builds by:
1. **Spawning Drops** (workers) via `/zo/ask` API (or generating launchers for manual Drops)
2. **Monitoring** for deposits, timeouts, failures
3. **Filtering** deposits via LLM judgment
4. **Checkpoint verification** at strategic quality gates
5. **Escalating** via email/SMS when issues arise
6. **Finalizing** with safety checks, integration tests, and learning harvest

## Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | The complete orchestrated work |
| **Wave** | Parallel execution round — a hard barrier; Wave N+1 cannot start until all blocking Drops in Wave N are complete |
| **Stream** | Sequential workflow within a Wave — Drops in a Stream run in order (D1.1 → D1.2 → D1.3) |
| **Drop** | Individual worker/task — one conversation's worth of context |
| **Checkpoint** | Strategic quality gate verifying cross-Drop consistency |
| **Deposit** | Worker's completion report (JSON in `deposits/`) |
| **Filter** | LLM judgment of deposit quality |
| **Dredge** | Forensics worker for dead Drops |
| **Launcher** | Generated markdown file for manual Drops with paste-ready prompt |
| **Jettison** | Connected-but-independent build spawned as tangent off-ramp |
| **Lineage** | Parent-child relationship graph between builds |

### Execution Model

```
Wave 1 (barrier)
├── Stream 1: D1.1 → D1.2 → D1.3  (sequential)
├── Stream 2: D2.1 → D2.2         (sequential, parallel to Stream 1)
└── Stream 3: D3.1                (parallel to Streams 1 & 2)

    ↓ (all blocking Drops in Wave 1 must complete)

Wave 2 (barrier)
├── Stream 1: D1.4 → D1.5
└── Stream 2: D2.3
```

- **Waves are hard barriers**: No Drop from Wave 2 spawns until all blocking Drops in Wave 1 are complete.
- **Streams are sequential**: Within a stream, D1.2 waits for D1.1 to complete.
- **Streams run in parallel**: D1.1 and D2.1 can run simultaneously (same Wave, different Streams).

## Quick Start

```bash
# Contract gate (required before start)
python3 N5/scripts/build_contract_check.py <slug>

# Validate plan before starting (recommended)
python3 Skills/pulse/scripts/pulse.py validate <slug>

# Check build status
python3 Skills/pulse/scripts/pulse.py status <slug>

# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start <slug>

# Manual tick (for testing)
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Ring the deposit bell after a Drop writes its deposit
python3 Skills/pulse/scripts/pulse.py ring <slug> <drop_id>

# Stop gracefully
python3 Skills/pulse/scripts/pulse.py stop <slug>

# Resume stopped build
python3 Skills/pulse/scripts/pulse.py resume <slug>

# Post-build finalization
python3 Skills/pulse/scripts/pulse.py finalize <slug>

# Launch a manual Drop (prints launcher content)
python3 Skills/pulse/scripts/pulse.py launch <slug> <drop_id>

# Retry a failed Drop (reset + update brief)
python3 Skills/pulse/scripts/pulse.py retry <slug> <drop_id> --reason "Why it failed"

# Create jettison (off-ramp build)
pulse jettison "<task>" [--from <parent>] [--type <type>]

# View build lineage DAG
pulse lineage [<slug>] [--format tree|json]
```

## Required Contract Gate

Before starting any Pulse build, both checks must pass:

```bash
python3 N5/scripts/build_contract_check.py <slug>
python3 Skills/pulse/scripts/pulse.py validate <slug>
```

If either command fails, do not run `start` yet. Fix missing artifacts first (`PLAN.md`, `meta.json`, and drop briefs in `drops/`).

## Plan Validation

**Principle (from Theo):** Plans are context vehicles, not spec documents. An incomplete plan means the model will guess, and guessing compounds errors across Drops.

Before starting any build, validate the plan is complete:

```bash
python3 Skills/pulse/scripts/pulse.py validate <slug>
```

The validator checks for:
- **Unfilled placeholders** (`{{PLACEHOLDER}}`, `TODO:`, etc.)
- **Missing required sections** (Objective, Open Questions, Phase 1, Success Criteria)
- **Empty sections** (headers without content)
- **Missing Scenarios** — Drop briefs without a `## Scenarios` section get warnings
- **Spec completeness** — Drops with `spawn_mode: auto` but `spec_completeness: partial|ambiguous` get warnings
- **Missing `drop_type`** — new-style briefs should say whether the Drop is `code`, `debug`, `research`, etc.
- **Missing `quality_contract`** — `drop_type: code` briefs should declare the local check loop
- **Missing `debug_contract`** — `drop_type: debug` briefs should declare target, symptom, and debugging evidence requirements
- **Warnings** (unchecked open questions, stale plans >14 days)

A build should NOT start until validation passes. The `start` command does NOT enforce this automatically — you must run `validate` first.

**Pre-build workflow (mandatory):**
1. Run spec-writing skill to extract scenarios from intent (`Skills/spec-writing/SKILL.md`)
2. Run pulse-interview to decompose into Streams/Drops
3. Architect creates plan with scenarios distributed into Drop briefs
4. Optionally write holdout scenarios in `holdout_scenarios/`
5. Validate plan
6. Start build

## Design Context Integration (teach-impeccable)

For builds with frontend/design work, the validator checks for `.impeccable.md` in the target project directory. This is a **soft gate** — it recommends but does not block.

**How it works:**
1. `validate` scans Drop titles and briefs for design/frontend keywords (ui, layout, styling, component, aesthetic, etc.)
2. If design work is detected, it looks for `Sites/` path references in the plan and briefs
3. It checks whether `.impeccable.md` exists in the referenced project directory
4. Reports a recommendation in the `🎨 Design Context` section of the validation output

**If `.impeccable.md` is missing:**
Run `/teach-impeccable` on the target project before briefing design Drops. This captures brand personality, aesthetic direction, and design principles in a persistent file that can be injected into Drop briefs.

**If `.impeccable.md` exists:**
Inject its content into design-related Drop briefs as shared context so all workers have the same aesthetic guardrails.

**Not a blocker:** Builds can proceed without design context. The recommendation surfaces during `validate` so you can make an informed choice.

## Visual References via Google Stitch

For builds with design Drops, generate visual reference mockups using Google Stitch. These serve as a "visual brief" — workers get a screenshot alongside the text brief so everyone builds toward the same aesthetic.

**Requires:** `STITCH_API_KEY` in environment, `Skills/google-stitch/` installed.

**Commands:**
```bash
# Check which design Drops have/lack visual references
python3 Skills/pulse/scripts/stitch_brief.py check <slug>

# Preview prompts without calling API
python3 Skills/pulse/scripts/stitch_brief.py generate <slug> --dry-run

# Generate reference mockups for all design Drops
python3 Skills/pulse/scripts/stitch_brief.py generate <slug>

# Generate for a specific Drop only
python3 Skills/pulse/scripts/stitch_brief.py generate <slug> --drop D7

# List existing references
python3 Skills/pulse/scripts/stitch_brief.py list <slug>
```

**How it works:**
1. Finds `.impeccable.md` for the build's target project (required — run `/teach-impeccable` first)
2. Identifies design-related Drops by keyword matching on titles and briefs
3. Composes a Stitch prompt for each Drop: objective + design principles from `.impeccable.md`
4. Creates a Stitch project, sets up a design system from the `.impeccable.md` context
5. Generates screens and saves screenshots to `N5/builds/<slug>/context/<drop_id>-reference.png`

**Validator integration (soft gate):**
When `.impeccable.md` exists and design Drops are detected, `validate` also checks for Stitch references. If missing, it surfaces a recommendation with the generate command.

**Recommended workflow:**
1. Run `/teach-impeccable` → `.impeccable.md`
2. Write plan + Drop briefs
3. `stitch_brief.py generate <slug> --dry-run` → review prompts
4. `stitch_brief.py generate <slug>` → generate mockups
5. Review mockups, re-generate any that miss the mark
6. `pulse.py validate <slug>` → confirm design context + references
7. Start build — workers reference both text brief and visual mockup

## Optional Graph Review For Shared Refactors

If your workspace also includes a dependency-graph toolchain, use it before Drops that modify shared code in `N5/`, `Skills/`, `Prompts/`, or `Integrations/`.

Recommended sequence when available:

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <target>
```

If the review is `HIGH`, also run:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps <target>
```

Use the result to narrow scope or split the work into staged Drops before editing a shared hub. If the graph tool is not installed in your export, skip this step rather than assuming those commands exist.

## Debug Swarm Protocol

Debug swarms use the N5 Debug Protocol (`Skills/systematic-debugging/SKILL.md`) as their operating methodology. Every debug Drop runs Layers 1-3 of the protocol independently.

### When to Use Debug Swarms

- Multiple tests/components failing after a refactor
- Bug has 2+ plausible root causes (hypothesis racing)
- System-wide issue affecting multiple components
- Circular fix detection fired and parallel approaches are needed

### Debug Drop Brief Template

Each debug Drop brief MUST include:

```markdown
## Debug Protocol
- Target: <specific file or component>
- Symptom: <what's broken>
- Phase 1 pre-screen: Run `query.py review <target>` before investigating
- Protocol: Follow N5 Debug Protocol Layers 1-3 (Skills/systematic-debugging/SKILL.md)

## Hypothesis
<specific theory this Drop is testing>

## Scenarios
Given: <system state>
When: <the fix is applied>
Then: <expected behavior>
Verify: <how to confirm>
```

### Hypothesis Racing for Debugging

When multiple theories compete, enable racing in `meta.json`:

```json
{
  "first_wins": true,
  "hypothesis_group": ["D1.1", "D1.2", "D1.3"]
}
```

Each Drop includes a `verdict` in its deposit: `confirmed`, `rejected`, or `inconclusive`.

### Swarm Synthesis

After all debug Drops complete, the orchestrator:
1. Collects verdicts from all Drops
2. Checks for cross-Drop pattern convergence (did multiple Drops find the same upstream cause?)
3. Runs `query.py rdeps` on the confirmed fix target for blast-radius validation
4. Synthesizes a unified fix plan before implementation

## Retry Failed Drops

**Principle (from Theo):** If output is bad, don't keep appending corrections. Revert and restart with corrected input.

When a Drop fails or produces bad output:

```bash
# Reset Drop and optionally explain why
python3 Skills/pulse/scripts/pulse.py retry <slug> <drop_id> --reason "Missed the auth requirements"
```

The retry command:
1. Archives the old deposit (preserves history)
2. Resets Drop status to `pending`
3. Appends retry context to the brief (if `--reason` provided)
4. Increments retry counter

This gives the model a clean slate with better context rather than compounding errors by appending fix requests to a polluted history.

## Manual Drops & Launchers

Some Drops need human oversight — close prompting control, high-risk changes, or work requiring V's judgment.

### spawn_mode Options

| Mode | Behavior | Use When |
|------|----------|----------|
| `auto` (default) | Pulse spawns via `/zo/ask` headless | Standard automated execution |
| `manual` | Pulse generates launcher, waits for V to execute | High-risk, requires judgment, voice-sensitive |

### Automatic Recommendation

If a Drop's `spawn_mode` is not explicitly set, Pulse analyzes the brief and recommends:
- **Manual** if brief contains: "preferences", "voice protocol", "HITL", "requires V review", "Careerspan voice", "ask V", "judgment", "sensitive"
- **Auto** otherwise

The recommendation is stored as `spawn_recommendation` and applied if no explicit mode is set.

### Manual Drop Workflow

1. **Tick detects ready Drop with `spawn_mode: manual`**
2. **Launcher generated** at `N5/builds/<slug>/launchers/<drop_id>.md`
3. **Status set to `awaiting_manual`**
4. **STATUS.md updated** with:
   ```
   ## Awaiting Manual (1)
   - [ ] D1.2 → run: `python3 Skills/pulse/scripts/pulse.py launch <slug> D1.2`
   ```
5. **V runs the launch command** (or opens launcher file directly)
6. **V pastes prompt into new thread**, executes, writes deposit
7. **Next tick detects deposit**, runs Filter, advances

### Launcher File Format

```markdown
# Launcher: my-build / D1.2

## Paste into a new thread

```text
Load and execute: file 'N5/builds/my-build/drops/D1.2-voice-sensitive-task.md'

When complete, write deposit to:
file 'N5/builds/my-build/deposits/D1.2.json'
```

## After you finish

- Confirm the deposit exists at the path above.
- Then run:
  - `python3 Skills/pulse/scripts/pulse.py ring my-build D1.2`
  - (or run periodic tick via your scheduler of choice)
```

## blocking Field (Non-Blocking Drops)

By default, all Drops are **blocking** — the next Wave cannot start until they complete.

Set `blocking: false` on a Drop to make it **non-blocking**:
- The Drop still runs and is tracked
- But it does NOT hold up Wave advancement
- Useful for: logging, notifications, optional enrichment, async cleanup

```json
{
  "drops": {
    "D1.1": { "name": "Core work", "wave": "W1", "blocking": true },
    "D1.2": { "name": "Send notification", "wave": "W1", "blocking": false }
  }
}
```

Wave 2 can start once D1.1 completes, even if D1.2 is still running.

**STATUS.md** explicitly surfaces non-blocking Drops so nothing is silently left behind.

## meta.json Structure (v3)

```json
{
  "schema_version": 3,
  "slug": "my-build",
  "title": "Build Title",
  "build_type": "code_build",
  "status": "pending",
  "model": "anthropic:claude-sonnet-4-20250514",
  "launch_mode": "orchestrated|manual|jettison",
  "delegate_only": false,
  "first_wins": false,
  "hypothesis_group": [],
  "broadcasts": [],
  "task_pool": {
    "enabled": false,
    "tasks": [],
    "max_concurrent_claims": 4,
    "worker_drops": []
  },
  
  "waves": {
    "W1": ["D1.1", "D1.2", "D2.1"],
    "W2": ["D1.3", "D2.2"]
  },
  "active_wave": "W1",
  
  "drops": {
    "D1.1": {
      "name": "Task name",
      "stream": 1,
      "order": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "blocking": true,
      "status": "pending"
    },
    "D1.2": {
      "name": "Voice-sensitive task",
      "stream": 1,
      "order": 2,
      "spawn_mode": "manual",
      "blocking": true,
      "status": "pending"
    }
  },
  
  "lineage": {
    "parent_type": "build|jettison|conversation|null",
    "parent_ref": "slug or convo_id",
    "parent_conversation": "convo_id",
    "moment": "description",
    "branched_at": "ISO timestamp"
  }
}
```

### Legacy Compatibility

Builds with `currents` or `current_stream`/`total_streams` (schema v1/v2) still work:
- Pulse normalizes them in-memory
- No migration required for old builds
- New builds should use `waves` schema

## Build Folder Structure

```
N5/builds/<slug>/
├── meta.json           # Build state (status, drops, waves)
├── STATUS.md           # Human-readable progress dashboard
├── BUILD_LESSONS.json  # Build-specific learnings
├── INTEGRATION_TESTS.json  # Test definitions
├── INTEGRATION_RESULTS.json  # Test results
├── FINALIZATION.json   # Post-build report
├── drops/              # Drop briefs
│   ├── D1.1-task-a.md
│   ├── D1.2-voice-task.md
│   └── D2.1-combine.md
├── deposits/           # Completion reports
│   ├── D1.1.json
│   ├── D1.1_filter.json
│   └── D1.1_forensics.json  (if dead)
├── launchers/          # Manual drop launchers (auto-generated)
│   └── D1.2.md
├── holdout_scenarios/  # Hidden acceptance scenarios (not visible to workers)
│   └── D1.1_holdouts.yaml
├── context/            # Pyramid summary context files (for large builds)
│   ├── overview.md
│   └── D1.1-context.md
└── artifacts/          # Build outputs
```

## Jettison Launch Mode

Jettisons are **off-ramp builds** — when you hit a tangent worth pursuing without derailing your current thread.

### When to Use

- Debugging issue surfaces mid-build that needs isolated investigation
- Interesting idea emerges that deserves its own exploration
- Current task has a prerequisite that should be handled separately
- You want to branch off without losing the parent context

### Command Syntax

```bash
# Basic jettison
pulse jettison "fix the rate limiting issue"

# Explicit parent build
pulse jettison "debug the API" --from adhd-todo-research

# Explicit type (overrides auto-detection)
pulse jettison "explore gamification approaches" --type research

# Custom moment description
pulse jettison "handle auth edge case" --moment "Discovered during D1.2 execution"
```

### Type Auto-Detection

| Keywords | Detected Type |
|----------|---------------|
| fix, bug, debug, error, refactor | `code_build` |
| research, explore, investigate, analyze | `research` |
| draft, write, content, blog, email | `content` |
| plan, design, architect, strategy | `planning` |
| (default) | `code_build` |

## Tick Runner (No Sentinel Dependency)

Pulse does not require a Sentinel agent. Orchestration runs directly via `start`, `tick`, and `status`.

### Recommended Operation

```bash
# Start one build
python3 Skills/pulse/scripts/pulse.py start <slug>

# Run periodic ticks from scheduler/cron if desired
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Inspect progress
python3 Skills/pulse/scripts/pulse.py status <slug>
```

### Optional Scheduler Pattern

If you want unattended progression, schedule:

```bash
python3 Skills/pulse/scripts/pulse.py tick <slug>
```

every 3-5 minutes using your own scheduler.

### Recovery Behavior

Pulse recovery is handled in the orchestration loop:

- dead/failed drops are assessed during tick cycles
- retry counts are tracked in `meta.json`
- recovery actions are logged to `N5/builds/<slug>/RECOVERY_LOG.jsonl`

## Learnings System

Shipped by default:
1. **Build-local** → `N5/builds/<slug>/BUILD_LESSONS.json`

Optional for richer installs:
2. **System-wide** → `N5/learnings/SYSTEM_LEARNINGS.json`

```bash
# Add build learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text"

# List learnings
python3 Skills/pulse/scripts/pulse_learnings.py list <slug>

# Harvest learnings from deposits
python3 Skills/pulse/scripts/pulse_learnings.py harvest <slug>
```

If you create `N5/learnings/SYSTEM_LEARNINGS.json` in your workspace, you can also use the optional `--system`, `list-system`, `promote`, and `inject` flows.

## Forward Broadcast

Drops can share findings with subsequent Drops via the `broadcast` field in deposits.

### How It Works

1. Drop includes `broadcast` string in deposit JSON
2. Pulse collects all broadcasts from completed Drops
3. New Drops receive a "## Broadcasts from Prior Drops" section in their brief

### Deposit Schema

```json
{
  "drop_id": "D1.1",
  "status": "complete",
  "broadcast": "Auth tokens expire after 30 min—don't cache beyond that",
  ...
}
```

### Injected Format

```markdown
## Broadcasts from Prior Drops

These findings were shared by earlier Drops in this build:

- **D1.1:** Auth tokens expire after 30 min—don't cache beyond that
```

### Best Practices

- Keep broadcasts short (~500 chars max)
- Broadcast discoveries that affect other Drops
- Don't broadcast obvious things already in briefs

## Hypothesis Racing

For debugging or exploration builds where you want to test multiple theories in parallel.

### Enabling

In `meta.json`:

```json
{
  "first_wins": true,
  "hypothesis_group": ["D1.1", "D1.2", "D1.3"]  // optional
}
```

### Verdict Field

Racing Drops include `verdict` in their deposit:

```json
{
  "drop_id": "D1.2",
  "status": "complete",
  "verdict": "confirmed",
  "summary": "Theory confirmed: rate limit is client-side"
}
```

Valid verdicts: `confirmed`, `rejected`, `inconclusive`

### Behavior

- When a Drop deposits `verdict: "confirmed"`, other Drops in the race are marked `superseded`
- Superseded Drops are not spawned (if pending) or ignored (if running)
- Wave can advance once winner confirms — superseded Drops don't block

### Use Cases

- Debugging with multiple theories
- A/B testing approaches
- Finding the first working solution among alternatives

## Delegate-Only Mode

Prevents the orchestrator from directly editing code, keeping all work in Drops.

### Enabling

In `meta.json`:

```json
{
  "delegate_only": true
}
```

### Constraints

When enabled, the orchestrator:
- **MAY**: Run pulse.py commands, read files, create/modify briefs, retry Drops
- **MUST NOT**: Edit source files, run application code, "fix" issues directly

### Why Use It

- Clear provenance (every change has a Drop source)
- Prevents long-build confusion
- Better audit trail

See `file 'Skills/pulse/references/delegate-only-mode.md'` for full details.

## Task Pool (Dynamic Claiming)

For builds with many similar tasks, Drops can claim work from a shared pool.

### Enabling

In `meta.json`:

```json
{
  "task_pool": {
    "enabled": true,
    "tasks": [
      {"id": "T001", "type": "enrich", "target": "file1.json", "status": "pending"},
      {"id": "T002", "type": "enrich", "target": "file2.json", "status": "pending"}
    ],
    "max_concurrent_claims": 4,
    "worker_drops": ["D1.1", "D1.2", "D1.3", "D1.4"]
  }
}
```

### Task States

- `pending` — Available for claiming
- `claimed` — Assigned to a Drop
- `complete` — Finished successfully
- `failed` — Failed, may be re-claimable

### Claiming

Pool workers claim tasks atomically (file-locked to prevent races):

```python
task = claim_task(slug, drop_id)
if task is None:
    # Pool exhausted, exit
```

### Use Cases

- Processing batches of similar items
- Parallelizing uniform work without pre-planning assignments
- Variable-duration tasks where fast Drops should grab more work

## Integration Tests

```bash
# Generate tests from artifacts
python3 Skills/pulse/scripts/pulse_integration_test.py generate <slug>

# Run tests
python3 Skills/pulse/scripts/pulse_integration_test.py run <slug>

# Add custom test
python3 Skills/pulse/scripts/pulse_integration_test.py add <slug> \
  --type file_exists \
  --name "Check output" \
  --config '{"path": "Sites/mysite/dist/index.html"}'
```

Test types: `file_exists`, `file_contains`, `command`, `http`, `service_running`

## Safety Layer

```bash
# Pre-build checks
python3 Skills/pulse/scripts/pulse_safety.py pre-check <slug>

# Verify artifacts after build
python3 Skills/pulse/scripts/pulse_safety.py verify <slug>

# Create git snapshot
python3 Skills/pulse/scripts/pulse_safety.py snapshot <slug>

# Restore from snapshot
python3 Skills/pulse/scripts/pulse_safety.py restore <slug>
```

## Scripts

| Script | Purpose |
|--------|---------|
| `pulse.py` | Main orchestrator (start, tick, stop, finalize, launch) |
| `pulse_common.py` | Shared paths, config, parsing utilities |
| `pulse_safety.py` | Pre-build checks, artifact verification, snapshots |
| `pulse_learnings.py` | Capture/propagate learnings (build + system) |
| `pulse_integration_test.py` | Post-build integration tests |
| `stitch_brief.py` | Generate Stitch visual references for design Drops |

## Related Files

- `file 'Skills/spec-writing/SKILL.md'` — Pre-build scenario extraction skill
- `file 'Skills/spec-writing/references/scenario-patterns.md'` — Common scenario patterns by build type
- `file 'Skills/pulse/references/holdout-scenarios-template.md'` — Holdout scenario convention
- `file 'Skills/pulse/references/pyramid-summary-template.md'` — Multi-resolution context files
- `BUILD_LESSONS.json` inside each build folder — Build-local learnings file

## Learning-Engaged Build Mode

When `build_mode: "learning"` in meta.json (the default):

### Orchestrator Responsibilities

1. **Generate Learning Landscape** — During planning, read `N5/config/understanding_bank.json` and analyze plan concepts against V's levels. Flag Decision Points and tag Drops.

2. **Present Decision Points** — Before launching Drops that involve flagged decisions:
   - Present the question in plain language
   - Offer 2-3 options with tradeoffs explained at V's level
   - Include a recommendation with reasoning
   - Support multi-round Socratic dialogue if V wants to explore
   - Log resolved decisions to `DECISIONS.md` in the build folder

3. **Spawn Learning Drops** — When V says "I want to deep dive into X":
   - Create an L-prefix Drop brief using `references/learning-drop-template.md`
   - The Learning Drop is always manual spawn
   - It never blocks the build — other Drops continue
   - When V completes the Learning Drop, integrate conclusions into subsequent briefs

4. **Generate Wave Reviews** — At wave boundaries:
   - Summarize what was accomplished
   - List concepts V was exposed to
   - Ask ONE Socratic question testing the most important concept
   - V can opt to deep dive (spawns Learning Drop) or continue

5. **Default Manual Spawn** — Pedagogical Drops use `spawn_mode: manual`. V opens them in new threads. Mechanical Drops (tagged in Learning Landscape) can be auto-spawned with V's approval.

### Rush Mode Override

V can override learning mode at any scope:
- **Per-Drop:** "Run D1.2 headless"
- **Per-Wave:** "Auto-spawn wave 2"
- **Per-Build:** `build_mode: "rush"` in meta.json, or V says "rush mode"

Rush mode reverts to Pulse v2 behavior: auto-spawn, no Decision Points, no Wave Reviews.

### Understanding Bank Integration

- **Read at plan time:** Architect reads `N5/config/understanding_bank.json` to calibrate Learning Landscape
- **Update at build close:** Pedagogical AAR updates concept levels based on V's demonstrated understanding
- **Updated by Learning Drops:** L-prefix deposits include `understanding_update` assessments
