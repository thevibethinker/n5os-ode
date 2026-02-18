---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_LhnxuEVVapCNdXle
---

# Pulse v2 Operational Guidelines

## Task Intake

- SMS: `n5 task <description>`
- Email: Subject "Task: <description>"
- Chat: Direct description (classified automatically)

## Interview Protocol

- Fragments accumulate in JSONL (`N5/pulse/interview/fragments.jsonl`)
- Multi-channel aggregation (SMS, email, chat)
- Context inference for routing (explicit `#task-<slug>` override)
- Seeded judgment at 0.8 confidence threshold

## Plan Review

- Google Drive sync to `Zo/Pulse Builds/<slug>/`
- SMS with inline summary + Drive link
- Approval: "go", "approve", "👍"
- Revision: "revise: <feedback>"

## Build Execution

- Standard Pulse Drop spawning via `/zo/ask`
- Manual override via `spawn_mode: "manual"` in Drop frontmatter
- Validators wired: code_validator + llm_filter
- Deposits rejected on validation failure

## Validation

- **Code Validator**: Syntax/lint checks (60s timeout)
- **LLM Filter**: Semantic validation against brief (120s timeout)
- Auto-pass on validator error (fail-open)
- Auto-reject on critical issues

## Tidying

- 5 hygiene Drops post-build:
  - `integration_test`
  - `reference_check`
  - `stub_scan`
  - `dedup`
  - `cleanup`
- Auto-fix threshold: 0.9 confidence
- Escalation for ambiguous findings

## Teaching

- LLM-native learning mode (orchestrator handles teaching natively)
- Understanding bank tracks concept mastery (`N5/config/understanding_bank.json`)
- "teach" command for review
- "absorbed: <term>" to mark learned

## Monitoring

- Sentinel agent polls every 3 min during active builds
- Dead Drop threshold: 15 min (900s) without heartbeat
- SMS escalation on failure, completion, or dead Drop

## Configuration

All settings in `Skills/pulse/config/pulse_v2_config.json`:
- Default build model: `anthropic:claude-opus-4-5-20251101`
- Seeded threshold: 0.8
- Quiet hours: 22:00-07:00 ET

## Pulse v3 Additions

### Lifecycle Automation
- Lifecycle agent polls every 5 min when tasks exist in queue
- Auto-advances: queued → interviewing → seeded → planning → plan_review
- Respects availability before HITL gates
- Self-destructs after 30 min of empty queue

### Fragment Tagging
- SMS responses route via `#task-<slug>` prefix
- Single open interview: auto-routes without tag
- Multiple open: prompts for tag

### Auto-Fix
- Tidying findings with confidence ≥ 0.9 auto-fix
- Lower confidence escalates to V
- Configurable threshold in config

### Commands Reference
| Command | Purpose |
|---------|---------|
| `pulse.py lifecycle start` | Create lifecycle agent |
| `pulse.py lifecycle stop` | Delete lifecycle agent |
| `pulse.py lifecycle status` | Show queue state |
| `pulse.py lifecycle tick` | Manual advancement |
| `#task-<slug> <message>` | Route SMS to interview |
