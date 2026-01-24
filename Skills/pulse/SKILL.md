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
4. **Escalating** via SMS when issues arise
5. **Finalizing** with safety checks, integration tests, and learning harvest

## Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | The complete orchestrated work |
| **Stream** | Parallel execution batch (like Wave) |
| **Drop** | Individual worker/task (synonym: Worker) |
| **Current** | Sequential chain within a Stream |
| **Deposit** | Worker's completion report |
| **Filter** | LLM judgment of deposit quality |
| **Dredge** | Forensics worker for dead Drops |

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

## Sentinel Setup

Pulse requires a **Sentinel** scheduled agent to monitor builds and text on meaningful events.

**Create Sentinel at build start:**
```
RRULE: FREQ=MINUTELY;INTERVAL=3;COUNT=120
Delivery: sms

Instruction:
Pulse Sentinel for build: <slug>

1. Run: python3 Skills/pulse/scripts/pulse.py status <slug>
2. Check for:
   - New completions → Text: "[PULSE] D#.# complete. Progress: X/16"
   - Dead drops (>15 min running) → Text: "[PULSE] D#.# may be dead (>15min). Reply 'retry' or 'skip'"
   - Build complete → Text: "[PULSE] Build <slug> COMPLETE" then delete yourself
3. If no changes, stay silent

Build folder: N5/builds/<slug>/
```

**Delete Sentinel when done:**
After build completes, delete the Sentinel agent to stop polling.

**Note:** Sentinel creation requires the Zo agent API (create_agent tool), which is only available in interactive/scheduled contexts — not from Python scripts. The LLM orchestrating the build must create the Sentinel.

## Pulse v2 Features

### Task Queue
- Multi-channel intake: `n5 task <description>` via SMS, email "Task: X", or chat
- Task types: code_build, research, content, analysis, hybrid
- Commands: `python3 N5/pulse/queue_manager.py add|list|prioritize|advance|next`

### Interview System
- Fragment-based async collection
- Multi-channel aggregation (SMS + email + chat)
- JSONL storage: `N5/pulse/interviews/<task-id>/fragments.jsonl`
- Seeded judgment with LLM evaluation
- Commands: `python3 N5/pulse/interview_manager.py start|add|status|seed`

### Plan Review
- Auto-sync to Google Drive: `Zo/Pulse Builds/<slug>/`
- SMS notification with shareable link
- Approval flow: "go" to build, "revise: X" for feedback
- Commands: `python3 N5/pulse/plan_sync.py sync|notify|approve`

### Tidying Swarm
- 5 hygiene Drops post-build:
  - Artifact verification
  - Dead code detection
  - Import cleanup
  - Documentation gaps
  - Test coverage check
- Auto-fix for safe issues
- Escalation for ambiguous findings

### Telemetry
- Persona + model attribution on all events
- Requirements tracking during builds
- Feedback → learnings pipeline
- Commands: `python3 N5/pulse/telemetry_manager.py log|query|export`
- Requirements: `python3 N5/pulse/requirements_tracker.py capture|list|export`

## v2 Lifecycle

```
pending → interviewing → seeded → planning → plan_review → building → tidying → complete
```

### Stage Transitions

| From | To | Trigger |
|------|----|---------|
| pending | interviewing | Task intake via any channel |
| interviewing | seeded | LLM judges ≥0.8 confidence |
| seeded | planning | `pulse.py plan <task>` |
| planning | plan_review | `plan_sync.py sync <slug>` |
| plan_review | building | V responds "go" |
| building | tidying | All Drops complete |
| tidying | complete | Health score ≥0.9 or V approves |

### v2 Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INTAKE (multi-channel)                                   │
│    - SMS: "n5 task <description>"                           │
│    - Email: Subject starts with "Task:"                     │
│    - Chat: Direct request                                   │
│    → Creates task in queue_manager.py                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. INTERVIEW (async, fragment-based)                        │
│    - Zo asks clarifying questions via same channel          │
│    - Fragments stored in interviews/<task-id>/              │
│    - LLM evaluates completeness (seeded judgment)           │
│    - Exits when confidence ≥0.8                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PLANNING (Architect creates PLAN.md)                     │
│    - Decompose into Streams/Drops                           │
│    - Generate meta.json + drop briefs                       │
│    - MECE validation on worker scopes                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PLAN REVIEW (human-in-the-loop)                          │
│    - Sync to Google Drive: Zo/Pulse Builds/<slug>/          │
│    - SMS V with review link                                 │
│    - Wait for "go" or "revise: <feedback>"                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. BUILD (automated orchestration)                          │
│    - Create git snapshot (safety)                           │
│    - Inject system learnings into briefs                    │
│    - Spawn Drops via /zo/ask                                │
│    - Tick loop: monitor, filter, escalate                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. TIDYING (automated hygiene)                              │
│    - Spawn 5 tidying Drops                                  │
│    - Auto-fix safe issues                                   │
│    - Escalate ambiguous findings                            │
│    - Calculate health score                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. FINALIZE                                                 │
│    - Verify all artifacts exist                             │
│    - Run integration tests                                  │
│    - Harvest learnings from deposits                        │
│    - SMS: Finalization result                               │
└─────────────────────────────────────────────────────────────┘
```

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
| `pulse.py` | Main orchestrator (start, tick, stop, finalize) |
| `sentinel.py` | Lightweight monitor for scheduled polling |
| `pulse_safety.py` | Pre-build checks, artifact verification, snapshots |
| `pulse_learnings.py` | Capture/propagate learnings (build + system) |
| `pulse_integration_test.py` | Post-build integration tests |

### v2 Scripts (in N5/pulse/)

| Script | Purpose |
|--------|---------|
| `queue_manager.py` | Task queue CRUD operations |
| `interview_manager.py` | Async interview orchestration |
| `plan_sync.py` | Google Drive sync + approval flow |
| `sms_intake.py` | SMS command routing |
| `telemetry_manager.py` | Event logging with attribution |
| `requirements_tracker.py` | Capture V's requirements/preferences |

## SMS Commands

Text these to control Pulse:
- `pulse stop` — Stop all builds, delete Sentinel
- `pulse done` — Mark builds complete, delete Sentinel
- `pulse pause` — Pause ticking (agent stays alive)
- `pulse resume` — Resume ticking
- `n5 task <description>` — Add task to queue (v2)

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

Two tiers:
1. **Build-local** → `N5/builds/<slug>/BUILD_LESSONS.json`
2. **System-wide** → `N5/learnings/SYSTEM_LEARNINGS.json`

```bash
# Add build learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text"

# Add system learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text" --system

# List learnings
python3 Skills/pulse/scripts/pulse_learnings.py list <slug>
python3 Skills/pulse/scripts/pulse_learnings.py list-system

# Promote build learning to system
python3 Skills/pulse/scripts/pulse_learnings.py promote <slug> <index>

# Inject system learnings into briefs
python3 Skills/pulse/scripts/pulse_learnings.py inject <slug>

# Harvest learnings from deposits
python3 Skills/pulse/scripts/pulse_learnings.py harvest <slug>
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

- `file 'Skills/pulse-interview/SKILL.md'` — Pre-build interview skill
- `file 'N5/learnings/SYSTEM_LEARNINGS.json'` — System-wide learnings
- `file 'N5/config/pulse_control.json'` — Sentinel control state
- `file 'Documents/System/Build-Orchestrator-System.md'` — Legacy manual system
- `file 'N5/pulse/'` — v2 scripts directory
