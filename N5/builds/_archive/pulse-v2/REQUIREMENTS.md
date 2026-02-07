---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.3
provenance: con_pf8ZLEBtIiuNJzIs
turn_count: 19
---

# Pulse v2 Requirements

Accumulated requirements from V during conversation con_pf8ZLEBtIiuNJzIs.

---

## Functional Requirements

### Task Queue
- [ ] Persistent task queue for varied work types (research, content, analysis, hybrid)
- [ ] Multi-channel intake: SMS, email, chat
- [ ] FIFO default ordering with priority bumping support
- [ ] Task classification on intake (type detection)

### Interview Gate
- [ ] Fragment-tolerant interview collection (responses stored separately from conversation thread)
- [ ] Multi-channel response aggregation (SMS, email → same interview storage)
- [ ] Stays open indefinitely until seeded (or explicit override like "just go")
- [ ] LLM judges completeness ("seeded?") from stored fragments
- [ ] Clean context window for interview analysis (no thread pollution)

### Availability Awareness
- [ ] Calendar-aware gating (no meetings, no deep work blocks)
- [ ] Deep work block detection (convention TBD: `[DW]` in title, specific color, etc.)
- [ ] Proactive check if V can unblock the interview

### Plan Generation & Review
- [ ] Plan generated after interview seeding
- [ ] HITL gate: SMS notification when plan ready for review
- [ ] Google Docs for plan delivery (shareable links, not SMS body)
- [ ] Designated Google Drive folder mirroring local build structure
- [ ] Metadata file in Drive folder linking back to local build
- [ ] Approval syntax: `approve`, `go`, `revise: [feedback]`

### Execution
- [ ] Pulse-style execution (headless Zos, Drops, Streams)
- [ ] Pulse monitoring (Sentinel, SMS escalation)
- [ ] Iteration continues until terminal (same as Pulse)
- [ ] Delivery same as Pulse

### Tidying Swarm (Post-Build)
- [ ] Dedicated swarm that runs after main build, before delivery
- [ ] Parallelizable hygiene tasks as separate Drops:
  - **Integration Testing Drop** — run integration tests, verify cross-component behavior
  - **Reference Checker Drop** — find broken imports, dead references, invalid paths
  - **Stub Scanner Drop** — detect TODO comments, placeholder code, unimplemented functions
  - **Deduplication Drop** — find duplicate code, redundant files, copy-paste patterns
  - **Cleanup Drop** — remove debug statements, console.logs, commented-out code
- [ ] Each Drop produces findings report
- [ ] Orchestrator aggregates findings, decides: fix automatically vs. escalate
- [ ] Can spawn fix Drops for auto-resolvable issues
- [ ] Escalate ambiguous issues via SMS before proceeding to delivery

### Feedback Loop
- [ ] Feedback capture after delivery
- [ ] Self-improvement learning extraction
- [ ] Pattern detection from completed builds

---

## Technical Requirements

### Model/Persona Telemetry
- [ ] Track persona ID and persona name in all telemetry
- [ ] Track model used (e.g., `claude-sonnet-4-20250514`)
- [ ] Default build model as configurable variable (current: `claude-opus-4-20250514`)
- [ ] Flag: `used_default` (boolean) — did we use the default build model?
- [ ] Log which model was used when errors/confusion occur

### Requirements Tracking
- [ ] Requirements/preferences/decisions tracking embedded at persona level
- [ ] Active in: Operator, Builder, Debugger, Architect, and relevant personas
- [ ] Activated when building (not for casual chat)
- [ ] Auto-updated every 2-3 turns or on significant statement
- [ ] REQUIREMENTS.md structure: Functional, Technical, Preferences, Decisions Made

### Interview Storage Layer
- [ ] Separate storage from conversation thread
- [ ] Independent analyzer reads stored responses
- [ ] Clean context for interview synthesis
- [ ] Supports async input (I reply now, analysis happens later)

### VibeTeacher Integration
- [ ] VibeTeacher persona activates at each HITL choke point during builds
- [ ] Teaching moments generated at: plan review, feedback collection, any approval gate
- [ ] Final comprehensive review at conversation end
- [ ] Teachable moment documents stored separately (not in conversation thread)
- [ ] Each teachable moment has frontmatter with `absorbed: false` default
- [ ] V manually marks `absorbed: true` after reviewing/internalizing
- [ ] VibeTeacher tracks absorbed vs. pending (doesn't auto-assume learning)
- [ ] Accumulated vocabulary/concepts build V's technical glossary over time
- [ ] Teaching forces system to articulate reasoning (secondary sense-check)

### Google Drive Outpost
- [ ] Designated folder in Google Drive (e.g., `Zo/Pulse Builds/`)
- [ ] Mirror local build folder structure: `Pulse Builds/<slug>/PLAN.md`
- [ ] Metadata file linking Drive folder ↔ local build
- [ ] Shareable link generation for plan review SMS

### Progress Indicators
- [ ] Build mode: build dashboard (existing)
- [ ] Conversation mode: auto-generated to-do list updated as requirements accumulate
- [ ] Honest progress reporting (X/Y done, Z%)

---

## Preferences

### Approval Syntax
- `approve` / `go` → proceed to build
- `revise: [feedback]` → iterate on plan
- `just go` / `override` → skip interview, proceed with partial info

### Queue Management
- FIFO default
- Priority bumping: `prioritize <task-slug>`

### Deep Work Marker (TBD)
- Convention needed: `[DW]` in event title? Specific calendar? Color?

---

## Decisions Made

| Turn | Decision |
|------|----------|
| 4 | Interview responses stored separately from conversation thread (fragment tolerance) |
| 6 | Multi-channel input aggregates to single interview storage |
| 8 | Plan delivery via Google Docs with shareable link, not SMS body |
| 10 | Plan review HITL gate added before build execution |
| 12 | Self-improvement telemetry includes persona + model + default_model flag |
| 12 | Google Drive outpost mirrors local build folder structure |
| 14 | Requirements tracking embedded at persona level (Operator, Builder, Debugger, etc.) |
| 14 | Model tracking uses configurable variable, not hardcoded model name |
| 15 | Tidying Swarm added as post-build stage with parallelized hygiene Drops |
| 16 | Incorporate existing work from con_T0QGg2ryaDjCTxVj (Pulse Genesis) |
| 17 | Incorporate existing work from con_plquQK5mpVEUO74p (prompt-to-skill) — wire validators into tick loop |
| 18 | VibeTeacher activates at HITL choke points, not randomly |
| 19 | Teachable moments require explicit absorption acknowledgment (no auto-assume) |

---

## Open Questions

- [ ] Deep work block convention (how to mark in calendar)?
- [ ] Response routing: explicit tag vs. context inference vs. prompt on ambiguity?
- [ ] Google Drive folder location: `Zo/Pulse Builds/` or different path?
- [ ] Skill name: Pulse v2 (evolution) or separate skill for research/content variant?

---

## Incorporated Work

### From con_T0QGg2ryaDjCTxVj (Pulse Genesis + Dashboard)
**Status:** COMPLETE — All core Pulse infrastructure exists and works.

Reused as-is:
- `pulse.py`, `sentinel.py`, `pulse_safety.py`
- `pulse_learnings.py`, `pulse_dashboard_sync.py`
- Dashboard at build-tracker-va.zocomputer.io
- SMS commands (pulse stop/done/pause/resume)

### From con_plquQK5mpVEUO74p (prompt-to-skill)
**Status:** 42% complete — Paused for Pulse upgrades.

Key deliverables we wire into Pulse v2:
- `pulse_code_validator.py` — EXISTS, needs wiring into tick loop
- `pulse_llm_filter.py` — EXISTS, needs wiring into tick loop
- `N5/scripts/lessons.py` — EXISTS, use as-is

Not in scope (resume later):
- Close skills (thread-close, drop-close, build-close)
- `N5/lib/close/` shared library

**Resume after Pulse v2:** `python3 Skills/pulse/scripts/pulse.py resume prompt-to-skill`

---

## Late Additions (Turn 21)

### Plan Review Output Format
- **Zo-native links preferred**: Use `file 'path'` syntax instead of Google Docs links when V is in Zo
- **High-level + drill-down**: Summary at top, clickable links to specific files/briefs below
- **Google Docs optional**: Only upload to Drive if V explicitly requests or is reviewing via SMS/mobile
- This simplifies the plan review HITL gate — local-first, Drive as fallback

### Decision: Zo Links > Google Docs
- V is always on a laptop logged into Zo
- Zo links open directly in workspace
- Reduces external dependency
- Drive remains available for sharing externally
