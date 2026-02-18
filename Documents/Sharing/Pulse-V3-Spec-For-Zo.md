---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_0vQ33jnKrHMMVhFF
---

# Pulse V3: Automated Build Orchestration for Zo

**Author:** V (Vrijen Attawar) via Zo  
**Context:** User-built capability extending Zo's agentic capabilities  
**Inspiration:** The "Gastown" concept of AI agents spawning and coordinating other agents

---

## What is Pulse?

Pulse is a **build orchestration system** that automates complex, multi-step work by spawning headless Zo workers (called "Drops") via the `/zo/ask` API, monitoring their progress, validating their output, and coordinating their execution across parallel and sequential tracks.

Think of it as a **foreman** that breaks down a large project into independent tasks, assigns each to a specialist worker, monitors their progress, quality-checks their deliverables, and escalates issues when human attention is needed.

---

## Core Capabilities

### 1. **Automated Worker Spawning**
- Decomposes work into parallel **Streams** and sequential **Currents**
- Spawns workers via `/zo/ask` API (headless conversations)
- Each worker receives a self-contained brief with all context needed
- Workers write structured "Deposits" (completion reports) to a shared build folder

### 2. **LLM-Based Quality Validation (Filter)**
- Every Deposit is validated by an LLM "Filter" that checks:
  - Did artifacts get created?
  - Were success criteria met?
  - Any scope creep or anti-patterns?
- Verdicts: PASS / WARN / FAIL
- Failed Drops trigger SMS escalation

### 3. **Health Monitoring & Dead Drop Detection**
- Sentinel polls every 3 minutes
- Workers running >15 minutes without output are marked "dead"
- Automatic forensics worker spawns to diagnose failures
- SMS alerts for dead workers with recovery options

### 4. **SMS-Based Human-in-the-Loop**
- Build start/complete notifications
- Failure escalations with actionable context
- V can respond via SMS: `pulse stop`, `pulse pause`, `pulse resume`
- Plan review approval: respond "go" or "revise: feedback"

### 5. **Learnings System (Two-Tier)**
- **Build-local learnings**: Lessons specific to current build
- **System-wide learnings**: Patterns that apply to all future builds
- Learnings auto-inject into worker briefs
- Harvested from completed Deposits at finalization

### 6. **Post-Build Hygiene (Tidying Swarm)**
- 5 automated hygiene checks after build completes:
  1. Integration tests
  2. Reference validation
  3. Stub/placeholder scan
  4. Duplicate code detection
  5. General cleanup
- High-confidence issues (≥0.9) auto-fix
- Lower-confidence issues escalate for review

### 7. **LLM-Native Learning Mode (Technical Vocabulary)**
- Orchestrator LLM natively identifies learning opportunities during HITL checkpoints
- Maintains an **Understanding Bank** tracking concepts V has encountered with mastery levels
- SMS commands: `teach` (get pending concepts), `absorbed: <term>` (mark as learned)
- Non-blocking: learning tracked asynchronously via `N5/config/understanding_bank.json`

---

## V3-Specific Features (Lifecycle Automation)

### Full Lifecycle State Machine
```
queued → interviewing → seeded → planning → plan_review → building → tidying → complete
```

The Lifecycle Agent advances tasks through states automatically:
- **Interviewing**: Async fragment collection from SMS/email/chat
- **Seeded**: LLM judges interview completeness (threshold: 0.8 confidence)
- **Planning**: Architect decomposes into Streams/Drops
- **Plan Review**: Respects V's calendar and quiet hours before pinging
- **Building**: Parallel/sequential worker execution
- **Tidying**: Automated hygiene pass
- **Complete**: Learnings harvested, finalization report generated

### Availability-Aware Reviews
- Checks Google Calendar for conflicts
- Respects quiet hours (default: 10pm-7am ET)
- Detects `[DW]` (Deep Work) markers
- Defers HITL checkpoints to available windows

### Multi-Channel Task Intake
- SMS: `n5 task <description>`
- Email: Subject starts with "Task:"
- Chat: Direct request

### Fragment Tagging
For multiple concurrent interviews:
```
#task-my-build This is my response about the feature requirements
```

---

## LLM-Native Learning Mode (Technical Vocabulary)

The learning system helps V build precise technical vocabulary through the natural flow of build work. The orchestrator LLM handles teaching natively — no separate regex-based scripts.

### How It Works

1. **Detection**: At HITL checkpoints (plan reviews, feedback, interviews), the orchestrator LLM identifies opportunities to surface precise technical terminology
2. **Teaching Moment**: When detected, generates a teaching moment with:
   - What V said (the imprecise phrase)
   - The precise term
   - Why it matters
   - A concrete example
3. **Storage**: Concepts tracked in `N5/config/understanding_bank.json` with mastery levels
4. **Review**: V can review via SMS (`teach`) or in finalization summary
5. **Absorption**: When V demonstrates understanding, mark as absorbed (`absorbed: MECE`)

### Activation Points

| Checkpoint | Trigger |
|------------|---------|
| `interview_complete` | After seeded judgment confirms enough context |
| `plan_review` | When V reviews the generated plan |
| `feedback` | When V provides feedback on work |
| `build_complete` | In finalization summary |

### Imprecision Patterns Detected

| V Says | Precise Term | Teaching |
|--------|--------------|----------|
| "non-overlapping tasks" | **MECE decomposition** | Mutually Exclusive, Collectively Exhaustive |
| "all at once" / "all-or-nothing" | **atomic operation** | Completes entirely or fails entirely |
| "run twice safely" | **idempotent operation** | Same result no matter how many times applied |
| "pause for review" | **checkpoint** | Designated point for human validation |
| "split into parts" | **decomposition** | Breaking complex problems into smaller pieces |
| "independent tasks" | **parallelizable** | Tasks that can run simultaneously |

### Understanding Bank Tracking

`N5/config/understanding_bank.json` tracks:
```json
{
  "term": "MECE",
  "definition": "Mutually Exclusive, Collectively Exhaustive...",
  "v_description": "like those sort of non-overlapping worker assignments",
  "precise_term": "MECE decomposition",
  "first_encountered": "2026-01-24",
  "level": "solid",
  "last_engaged": "2026-01-24T23:02:59",
  "usage_count": 12
}
```

### SMS Commands

- **`teach`** — Get summary of pending concepts from understanding bank
- **`absorbed: <term>`** — Mark term as learned (e.g., `absorbed: MECE`)

### Build Finalization Integration

At build complete, the finalization SMS includes:
```
[PULSE] my-build FINALIZED ✅ Artifacts verified, tests passed.
📚 Teaching: MECE, atomic, checkpoint +2 more
Reply 'teach' for details.
```

### Why This Matters

The learning system transforms builds from pure execution into learning opportunities. V gradually builds technical vocabulary through real work context, not abstract study. The understanding bank becomes a personalized reference of terms V has encountered and absorbed.

---

## Architecture

### Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | Complete orchestrated project |
| **Stream** | Parallel execution batch |
| **Current** | Sequential chain within a Stream |
| **Drop** | Individual worker task |
| **Deposit** | Worker's completion report |
| **Filter** | LLM judge of Deposit quality |
| **Dredge** | Forensics worker for dead Drops |
| **Sentinel** | Scheduled agent that monitors builds |

### Build Folder Structure
```
N5/builds/<slug>/
├── meta.json              # Build state, Drop registry
├── STATUS.md              # Human-readable dashboard
├── BUILD_LESSONS.json     # Build-specific learnings
├── INTEGRATION_TESTS.json # Test definitions
├── FINALIZATION.json      # Post-build report
├── drops/                 # Worker briefs
│   ├── D1.1-schema.md
│   └── D2.1-frontend.md
├── deposits/              # Completion reports
│   ├── D1.1.json
│   └── D1.1_filter.json
└── artifacts/             # Build outputs
```

### Drop Brief Structure
```yaml
---
drop_id: D1.1
build_slug: my-build
stream: 1
depends_on: []
spawn_mode: auto  # auto = headless | manual = V pastes into thread
thread_title: "[my-build] D1.1: Create Schema"
---

# Drop Brief: Create Schema

**Mission:** Define the database schema for user management.

**Output:** `schema.sql`, `types.ts`

## Context
<Everything needed - Drops have NO orchestrator context>

## Requirements
<Detailed specs>

## Success Criteria
- [ ] schema.sql exists with 5 tables
- [ ] types.ts exports User, Session, Token types
- [ ] Soft-delete pattern used

## On Completion
Write deposit to `N5/builds/my-build/deposits/D1.1.json`
```

---

## Key Design Principles

### 1. **Workers Are Context-Free**
Each Drop receives a completely self-contained brief. Workers cannot access orchestrator context, conversation history, or other workers' state. This enables true parallel execution and makes debugging isolated.

### 2. **Documents Are The Orchestrator's Brain**
The build folder (`N5/builds/<slug>/`) IS the orchestrator's persistent memory. Everything is file-based: state, briefs, deposits, learnings. This enables:
- Human readability
- Git versioning
- Recovery from failures
- Cross-session continuity

### 3. **LLM Judgment Over Mechanical Checks**
The Filter uses LLM judgment, not just file existence checks. It can read artifacts, understand intent, and make nuanced PASS/WARN/FAIL decisions.

### 4. **SMS as Primary Escalation Channel**
Critical events go to SMS because it's:
- Attention-grabbing
- Works when not at computer
- Enables quick responses
- Supports structured commands

### 5. **Availability Awareness**
Pulse respects human rhythms—calendar integration, quiet hours, deep work markers. It won't ping for review during meetings or at midnight.

---

## Zo Primitives Used

| Zo Capability | How Pulse Uses It |
|---------------|-------------------|
| `/zo/ask` API | Spawns headless worker conversations |
| `send_sms_to_user` | Escalations and notifications |
| `use_app_google_calendar` | Availability checking |
| `use_app_google_drive` | Plan sync for external review |
| Scheduled Agents | Sentinel polling every 3 minutes |
| File system | Build folder as persistent state |
| `create_agent` / `delete_agent` | Sentinel lifecycle |

---

## Example Workflow

1. **Intake**: V texts `n5 task Build user auth system`
2. **Interview**: Pulse asks clarifying questions via SMS
3. **Seeding**: LLM judges when enough context gathered (≥0.8)
4. **Planning**: Architect creates PLAN.md with 3 Streams, 8 Drops
5. **Review**: Pulse syncs to Drive, texts V with link, waits for "go"
6. **Building**: 
   - Stream 1: D1.1 (schema), D1.2 (types) run in parallel
   - Stream 2: D2.1 (API) waits for Stream 1
   - Sentinel monitors, Filters validate, SMS on failures
7. **Tidying**: 5 hygiene Drops scan for issues, auto-fix safe ones
8. **Finalize**: Artifacts verified, tests run, learnings harvested
9. **Complete**: V receives "Build COMPLETE" SMS

---

## Configuration

`Skills/pulse/config/pulse_v2_config.json`:
```json
{
  "version": "3.0",
  "default_build_model": "anthropic:claude-opus-4-5-20251101",
  "interview": {
    "seeded_threshold": 0.8,
    "channels": ["sms", "email", "chat"]
  },
  "availability": {
    "check_calendar": true,
    "quiet_hours": {"start": "22:00", "end": "07:00"},
    "deep_work_marker": "[DW]"
  },
  "validation": {
    "llm_filter_enabled": true,
    "code_validator_enabled": true,
    "auto_pass_on_validator_error": true
  },
  "thresholds": {
    "dead_threshold_seconds": 900,
    "poll_interval_seconds": 180
  },
  "tidying_swarm": {
    "enabled": true,
    "auto_fix_threshold": 0.9
  },
  "lifecycle": {
    "enabled": true,
    "poll_interval_minutes": 5,
    "idle_shutdown_minutes": 30
  }
}
```

---

## Why This Matters

Pulse demonstrates that Zo users can build sophisticated orchestration on top of Zo's primitives:

1. **The `/zo/ask` API enables agent-spawning-agents** — a single conversation can orchestrate dozens of parallel workers
2. **SMS + scheduled agents enable async supervision** — no need to stay in the chat session
3. **File-based state is durable and human-readable** — builds survive disconnections, can be debugged by inspection
4. **LLM judgment is the right tool for validation** — mechanical checks miss intent; LLM Filters understand context

This is "Gastown" realized: a small crew of AI agents self-organizing to complete complex work, with human oversight at key decision points.

---

## Commands Reference

```bash
# Build lifecycle
python3 Skills/pulse/scripts/pulse.py start <slug>
python3 Skills/pulse/scripts/pulse.py status <slug>
python3 Skills/pulse/scripts/pulse.py stop <slug>
python3 Skills/pulse/scripts/pulse.py finalize <slug>

# V3 lifecycle management
python3 Skills/pulse/scripts/pulse.py lifecycle start
python3 Skills/pulse/scripts/pulse.py lifecycle tick --dry-run

# SMS commands
pulse stop      # Stop all builds
pulse pause     # Pause ticking
pulse resume    # Resume
n5 task <desc>  # Add task to queue
```

---

*Built by V on Zo. January 2026.*
