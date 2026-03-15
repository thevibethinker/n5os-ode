---
name: pulse
description: |
  Automated build orchestration system. Spawns headless Zo workers (Drops) in parallel Streams,
  monitors health, validates Deposits via LLM judgment, handles dead Drops, and escalates via SMS.
  Supports sequential Currents within Streams. Replaces manual Build Orchestrator for unattended execution.
---

# Pulse: Automated Build Orchestration

## Overview

Pulse orchestrates complex builds by:
1. **Spawning Drops** (workers) via `/zo/ask` API
2. **Monitoring** for deposits, timeouts, failures
3. **Filtering** deposits via LLM judgment
4. **Checkpoint verification** at strategic quality gates
5. **Escalating** via email/SMS when issues arise
6. **Finalizing** with safety checks, integration tests, and learning harvest

## Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | The complete orchestrated work |
| **Stream** | Parallel execution batch (like Wave) |
| **Drop** | Individual worker/task (synonym: Worker) |
| **Current** | Sequential chain within a Stream |
| **Checkpoint** | Strategic quality gate verifying cross-Drop consistency |
| **Deposit** | Worker's completion report |
| **Filter** | LLM judgment of deposit quality |
| **Dredge** | Forensics worker for dead Drops |
| **Jettison** | Connected-but-independent build spawned as tangent off-ramp |
| **Lineage** | Parent-child relationship graph between builds |
| **Launch Mode** | How a build was spawned: orchestrated, manual, or jettison |

## Quick Start

```bash
# Check build status
python3 Skills/pulse/scripts/pulse.py status <slug>

# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start <slug>

# Manual tick (for testing)
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Stop gracefully
python3 Skills/pulse/scripts/pulse.py stop <slug>

# Resume stopped build
python3 Skills/pulse/scripts/pulse.py resume <slug>

# Post-build finalization
python3 Skills/pulse/scripts/pulse.py finalize <slug>
```

## Scope of the Public Export

This export ships the stable Pulse orchestration core:

- `start`
- `status`
- `tick`
- `stop`
- `resume`
- `finalize`

The broader jettison, lineage, lifecycle, queue, and interview systems are not included in this public repo. Treat this export as the core unattended build runner rather than the full internal Pulse environment.

## Sentinel Setup

Pulse requires a **Sentinel** scheduled agent to monitor builds and report via email (preferred) or SMS.

### Email Sentinel (Recommended)

Email provides richer updates and allows detailed replies.

**Create Email Sentinel at build start:**
```
RRULE: FREQ=MINUTELY;INTERVAL=5;COUNT=100
Delivery: email

Instruction:
Pulse Sentinel for build: <slug>

1. Run: python3 Skills/pulse/scripts/pulse.py status <slug> --json
2. Parse the status and compose an email update.

EMAIL FORMAT:
Subject: [PULSE] <slug> - <status_summary>

Body:
## Build: <slug>
**Status:** <stream X of Y> | **Progress:** <completed>/<total> Drops (<pct>%)

### Stream Status
| Stream | Status | Drops |
|--------|--------|-------|
| S1 | complete | D1.1 ✓, D1.2 ✓ |
| S2 | running | D2.1 ✓, D2.2 ⏳ (8 min) |
| S3 | pending | - |

### Recent Activity (since last email)
- D2.1 completed: "Implemented webhook handler" 
- D2.2 started 8 minutes ago

### Concerns
- ⚠️ D2.2 running >15 min → may be stuck
- ⚠️ D1.2 deposit has WARN: "Consider extracting to skill"

### Reply Commands
Reply to this email with any of:
- `status` — Get detailed status
- `retry D2.2` — Retry a stuck/failed Drop
- `skip D2.2` — Skip a Drop and continue
- `pause` — Pause the build
- `resume` — Resume paused build
- `stop` — Stop the build entirely
- `<other instructions>` — Free-form guidance

---
Build folder: N5/builds/<slug>/
Orchestrator: <conversation_id>

3. ONLY send email if:
   - New completions since last check
   - Drop running >15 min (potential dead drop)
   - Build complete
   - Stream advanced
   - Any FAIL verdict from Filter
   
4. If build complete: Send final summary email, then delete yourself.

5. If no meaningful changes, stay silent (don't spam).
```

### SMS Sentinel (Fallback)

Use SMS for brief, urgent alerts when email isn't being checked.

```
RRULE: FREQ=MINUTELY;INTERVAL=3;COUNT=120
Delivery: sms

Instruction:
Pulse SMS Sentinel for build: <slug>

1. Run: python3 Skills/pulse/scripts/pulse.py status <slug>
2. ONLY text if:
   - Drop FAILED → "[PULSE] ❌ D#.# FAILED: <reason>. Reply 'retry' or 'skip'"
   - Drop dead (>15 min) → "[PULSE] ⚠️ D#.# may be dead. Reply 'retry' or 'skip'"
   - Build complete → "[PULSE] ✅ <slug> COMPLETE"
3. For routine progress, stay silent (email handles that).
```

### Dual Sentinel (Email + SMS)

For critical builds, run both:
- Email Sentinel: Every 5 min, detailed updates
- SMS Sentinel: Every 3 min, urgent alerts only (failures, dead drops)

### Email Reply Processing

When V replies to a Sentinel email, the reply is processed as a conversation with Zo. The Sentinel instruction should include:

```
If this is a reply to a previous Sentinel email, parse the command:
- "status" → Run full status and reply
- "retry D#.#" → Mark drop for retry, run: python3 Skills/pulse/scripts/pulse.py retry <slug> D#.#
- "skip D#.#" → Skip drop: python3 Skills/pulse/scripts/pulse.py skip <slug> D#.#
- "pause" → python3 Skills/pulse/scripts/pulse.py pause <slug>
- "resume" → python3 Skills/pulse/scripts/pulse.py resume <slug>
- "stop" → python3 Skills/pulse/scripts/pulse.py stop <slug>
- Free-form text → Log as guidance to N5/builds/<slug>/guidance.md and acknowledge
```

### Delete Sentinel When Done

After build completes, the Sentinel should delete itself. If it doesn't, manually delete via:
- SMS: `pulse done` or `pulse stop`
- Chat: Delete the scheduled agent

**Note:** Sentinel creation requires the Zo agent API (create_agent tool), which is only available in interactive/scheduled contexts — not from Python scripts. The LLM orchestrating the build must create the Sentinel.

## Build Folder Structure

```
N5/builds/<slug>/
├── meta.json           # Build state (status, drops, streams)
├── STATUS.md           # Human-readable progress dashboard
├── BUILD_LESSONS.json  # Build-specific learnings
├── INTEGRATION_TESTS.json  # Test definitions
├── INTEGRATION_RESULTS.json  # Test results
├── FINALIZATION.json   # Post-build report
├── drops/              # Drop briefs (D1.1-name.md)
│   ├── D1.1-task-a.md
│   ├── D1.2-task-b.md
│   └── D2.1-combine.md
├── deposits/           # Completion reports
│   ├── D1.1.json
│   ├── D1.1_filter.json
│   └── D1.1_forensics.json  (if dead)
└── artifacts/          # Build outputs
```

## Scripts

| Script | Purpose |
|--------|---------|
| `pulse.py` | Main orchestrator (start, status, stop, resume, tick, finalize) |
| `pulse_safety.py` | Pre-build checks, artifact verification, snapshots |
| `pulse_learnings.py` | Build-local learning capture and reporting |
| `pulse_llm_filter.py` | Deposit quality filtering |
| `pulse_code_validator.py` | Code-oriented validation helpers |
| `pulse_file_routing.py` | Artifact routing helpers |
| `pulse_common.py` | Shared path and utility helpers |

## SMS Commands

Text these to control Pulse:
- `pulse stop` — Stop all builds, delete Sentinel
- `pulse done` — Mark builds complete, delete Sentinel
- `pulse pause` — Pause ticking (agent stays alive)
- `pulse resume` — Resume ticking

## meta.json Structure

```json
{
  "slug": "my-build",
  "title": "Build Title",
  "build_type": "code_build",
  "status": "pending",
  "total_streams": 2,
  "current_stream": 1,
  "model": "anthropic:claude-sonnet-4-20250514",
  "launch_mode": "orchestrated|manual|jettison",
  "lineage": {
    "parent_type": "build|jettison|conversation|null",
    "parent_ref": "slug or convo_id",
    "parent_conversation": "convo_id",
    "moment": "description",
    "branched_at": "ISO timestamp"
  },
  "drops": {
    "D1.1": {
      "name": "Task name",
      "stream": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "status": "pending"
    }
  },
  "currents": {}
}
```

### spawn_mode Options

| Mode | Behavior | Use When |
|------|----------|----------|
| `auto` (default) | Pulse spawns via `/zo/ask` headless | Most Drops - standard automated execution |
| `manual` | Pulse marks as "awaiting_manual", V pastes brief into new thread | High-risk work, requires human judgment, complex debugging |

When a Drop has `spawn_mode: "manual"`:
1. Pulse prints `[SPAWN] D1.1 is waiting for manual spawn`
2. Status changes to `awaiting_manual`
3. V opens new thread, pastes brief, executes
4. V writes deposit manually
5. Next tick detects deposit, runs Filter

**Mix and match:** Some Drops auto, some manual. Useful for builds where setup is automated but core logic needs human oversight.

## Learnings System

Pulse ships build-local learnings via `N5/builds/<slug>/BUILD_LESSONS.json`.

```bash
# Add build learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text"

# List learnings
python3 Skills/pulse/scripts/pulse_learnings.py list <slug>
```

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

## Related Files

- `file 'Skills/pulse/scripts/pulse.py'` — Main Pulse CLI
- `file 'Skills/pulse/scripts/pulse_safety.py'` — Pre-build and verification checks
- `file 'Skills/pulse/scripts/pulse_learnings.py'` — Learning capture helpers
- `file 'Skills/pulse/references/drop-brief-template.md'` — Drop brief shape
