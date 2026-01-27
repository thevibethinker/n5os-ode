---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
type: build_plan
status: draft
provenance: con_O6kc296CDg1FW6xW
builds_on: pulse-v2
---

# Plan: Pulse v3 — Lifecycle Automation

**Objective:** Close the gaps identified in Pulse v2 by adding automated lifecycle orchestration so the full flow (task intake → interview → plan → review → build → complete) runs with minimal manual intervention.

**Trigger:** Gap analysis revealed that v2 scripts exist but aren't stitched into an autonomous pre-build pipeline.

**Key Design Principle:** Extend, don't rewrite. Wire existing scripts together via a Lifecycle Sentinel that watches task state and advances automatically.

---

## Open Questions

- [x] Should lifecycle agent be separate from build Sentinel? → **Decision: YES** — Lifecycle Agent handles pre-build; Build Sentinel handles build execution. Different cadences.
- [x] How to handle fragment routing without explicit tags? → **Decision: Explicit tagging** (`#task-slug`) for MVP; context inference is a v4 enhancement.
- [x] Where does Lifecycle Agent live? → **Decision:** Scheduled agent created when tasks exist in `queued`/`interviewing` state, self-destructs when queue empty.

---

## Alternatives Considered (Nemawashi)

### Alternative 1: Monolithic Orchestrator (Rejected)
Single script that polls everything: tasks, interviews, builds, tidying.
**Why rejected:** Complects concerns. Different stages have different polling cadences.

### Alternative 2: Event-Driven Architecture (Rejected for MVP)
File watchers or webhook triggers advance state.
**Why rejected:** Over-engineering for current scale. Polling every 3-5 min is sufficient.

### Alternative 3: Extend Build Sentinel (Rejected)
Make existing Sentinel handle pre-build lifecycle too.
**Why rejected:** Build Sentinel has specific focus (monitor Drops). Adding pre-build logic would complect its purpose.

**Selected:** New Lifecycle Agent + targeted integrations into existing scripts.

---

## Trap Doors Identified

| Trap Door | Risk Level | Mitigation |
|-----------|------------|------------|
| SMS rate limiting | MEDIUM | Batch notifications, respect quiet hours |
| Interview stuck in loop | LOW | Max 10 seeded_judge calls per task |
| Fragment router false matches | LOW | Explicit tagging for MVP |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PULSE v3 LIFECYCLE AUTOMATION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LIFECYCLE AGENT (polls every 5 min when tasks exist)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  1. Check for 'queued' tasks → Start interview                      │   │
│  │  2. Check 'interviewing' with fragments → Run seeded_judge          │   │
│  │  3. Check 'seeded' tasks → Generate plan                            │   │
│  │  4. Check 'planning' with plan → Check availability → Initiate HITL │   │
│  │  5. Check approved tasks → Start build via pulse.py                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ review_mgr   │  │ avail_check  │  │ fix_dispatch │  │ frag_router  │   │
│  │ +availability│  │ (already     │  │ wired into   │  │ explicit tag │   │
│  │  check       │  │  exists)     │  │ tidying flow │  │ support      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Checklist

### Phase 1: Lifecycle Agent + Availability Integration
- ☐ Create lifecycle_agent.py — polls task states, advances lifecycle
- ☐ Integrate availability_checker into review_manager.py
- ☐ Add `pulse.py lifecycle` command to spawn/manage agent
- ☐ Test: Task auto-advances from `queued` → `interviewing` → `seeded`

### Phase 2: Wiring Fixes + Fragment Router
- ☐ Wire fix_dispatcher.py into pulse.py tidying flow
- ☐ Add explicit tag support (#task-slug) to sms_intake.py
- ☐ Add fragment routing to existing interview responses
- ☐ Test: Tagged SMS routes to correct interview; tidying auto-fixes

### Phase 3: Integration + Documentation
- ☐ Update SKILL.md with v3 lifecycle docs
- ☐ Update pulse_v2_config.json with lifecycle settings
- ☐ Add lifecycle commands to SMS help
- ☐ Test: Full end-to-end workflow with SMS task intake

---

## Phase 1: Lifecycle Agent + Availability Integration

### Affected Files
- `N5/pulse/lifecycle_agent.py` — CREATE — Main lifecycle orchestrator
- `N5/pulse/review_manager.py` — UPDATE — Add availability check
- `Skills/pulse/scripts/pulse.py` — UPDATE — Add `lifecycle` command

### Changes

**1.1 Lifecycle Agent (`lifecycle_agent.py`):**

```python
"""
Lifecycle Agent for Pulse v3

Polls task queue and advances state automatically:
- queued → interviewing (start interview)
- interviewing → seeded (when confidence ≥ threshold)
- seeded → planning (generate plan)
- planning → plan_review (initiate HITL)
- approved → building (start build)

Self-destructs when queue is empty for 30+ minutes.
"""

def tick():
    """Single tick of lifecycle advancement."""
    tasks = queue_manager.list_tasks()
    
    for task in tasks:
        status = task["status"]
        
        if status == "queued":
            # Start interview
            interview_manager.create(task["id"])
            queue_manager.advance(task["id"], "interviewing")
            notify(f"Started interview for '{task['title']}'")
            
        elif status == "interviewing":
            # Check if seeded
            judgment = seeded_judge.evaluate(task["id"])
            if judgment["seeded"] and judgment["confidence"] >= 0.8:
                interview_manager.mark_seeded(task["id"], judgment["confidence"])
                queue_manager.advance(task["id"], "seeded")
                notify(f"Task '{task['title']}' seeded (confidence: {judgment['confidence']})")
                
        elif status == "seeded":
            # Generate plan
            result = plan_generator.generate(task["id"])
            if result["success"]:
                queue_manager.advance(task["id"], "planning")
                
        elif status == "planning":
            # Check availability then initiate review
            if availability_checker.is_available():
                review_manager.initiate(task["build_slug"])
                queue_manager.advance(task["id"], "plan_review")
            else:
                # Defer, will try next tick
                pass
                
        elif status == "approved":
            # Start build
            subprocess.run(["python3", "Skills/pulse/scripts/pulse.py", 
                          "start", task["build_slug"]])
            queue_manager.advance(task["id"], "building")
```

**1.2 Availability Integration in review_manager.py:**

Add at line ~85 (before initiate_review):
```python
# Check availability before HITL
from availability_checker import is_available, get_next_window

if not is_available():
    next_window = get_next_window()
    return {
        "success": False, 
        "deferred": True,
        "reason": "V unavailable",
        "next_window": next_window
    }
```

**1.3 Pulse.py `lifecycle` command:**

```python
# Add to subparsers
lifecycle_parser = subparsers.add_parser("lifecycle", help="Manage lifecycle agent")
lifecycle_parser.add_argument("action", choices=["start", "stop", "status", "tick"])

# Add to main()
elif args.command == "lifecycle":
    if args.action == "start":
        # Create scheduled agent
        create_lifecycle_agent()
    elif args.action == "stop":
        # Delete scheduled agent
        delete_lifecycle_agent()
    elif args.action == "status":
        show_lifecycle_status()
    elif args.action == "tick":
        # Manual single tick
        subprocess.run(["python3", "N5/pulse/lifecycle_agent.py", "tick"])
```

### Unit Tests
- Lifecycle tick: Task at `queued` → advances to `interviewing`
- Availability: `is_available()=False` → review deferred, not sent
- Pulse command: `pulse.py lifecycle tick` runs single advancement cycle

---

## Phase 2: Wiring Fixes + Fragment Router

### Affected Files
- `Skills/pulse/scripts/pulse.py` — UPDATE — Wire fix_dispatcher
- `N5/pulse/sms_intake.py` — UPDATE — Add tag parsing
- `N5/pulse/fragment_router.py` — UPDATE — Handle tagged messages

### Changes

**2.1 Wire fix_dispatcher into pulse.py:**

In `process_tidying_complete()` (around line 780), after aggregation:

```python
# After aggregating findings
aggregation_result = subprocess.run([...])

# NEW: Dispatch auto-fixes
dispatch_result = subprocess.run([
    "python3", str(WORKSPACE / "N5" / "pulse" / "tidying" / "fix_dispatcher.py"),
    "dispatch", slug, "--auto-fix-threshold", "0.9"
], capture_output=True, text=True)

if dispatch_result.returncode == 0:
    dispatch_data = json.loads(dispatch_result.stdout)
    if dispatch_data.get("fixes_dispatched", 0) > 0:
        print(f"  Auto-fixed {dispatch_data['fixes_dispatched']} issues")
```

**2.2 Tag parsing in sms_intake.py:**

```python
def parse_message(message: str) -> dict:
    """Parse SMS message for commands and tags."""
    
    # Check for explicit task tag: #task-slug
    tag_match = re.match(r'#task-(\S+)\s*(.*)', message, re.IGNORECASE)
    if tag_match:
        return {
            "type": "interview_response",
            "task_slug": tag_match.group(1),
            "content": tag_match.group(2).strip()
        }
    
    # Existing command parsing...
    if message.lower().startswith("n5 task"):
        # ... existing logic
```

**2.3 Fragment router update:**

```python
def route_fragment(message: str, channel: str) -> dict:
    """Route incoming message to correct interview."""
    
    # Priority 1: Explicit tag
    if message.startswith("#task-"):
        slug = message.split()[0].replace("#task-", "")
        return route_to_interview(slug, message, channel)
    
    # Priority 2: Single open interview
    open_interviews = get_open_interviews()
    if len(open_interviews) == 1:
        return route_to_interview(open_interviews[0], message, channel)
    
    # Priority 3: Ask for clarification
    if len(open_interviews) > 1:
        return {
            "routed": False,
            "reason": "multiple_open",
            "prompt": f"Which task? Reply with tag: {', '.join(['#task-' + i for i in open_interviews])}"
        }
    
    # No open interviews - treat as new task
    return {"routed": False, "reason": "no_open_interviews", "treat_as_new": True}
```

### Unit Tests
- Fix dispatch: Tidying finding with confidence 0.95 → auto-fix spawned
- Tag parsing: `#task-my-build this is my response` → routes to `my-build`
- Multi-interview: 2 open interviews → prompts for tag

---

## Phase 3: Integration + Documentation

### Affected Files
- `Skills/pulse/SKILL.md` — UPDATE — Add v3 lifecycle docs
- `Skills/pulse/config/pulse_v2_config.json` — UPDATE — Add lifecycle settings
- `N5/prefs/operations/pulse_v2_guidelines.md` — UPDATE — Add v3 section

### Changes

**3.1 SKILL.md additions:**

```markdown
## Pulse v3 Features

### Lifecycle Automation
Pulse v3 adds automatic lifecycle advancement:

```
queued → interviewing → seeded → planning → plan_review → building → tidying → complete
```

**Lifecycle Agent** polls every 5 minutes and advances tasks automatically:
- Starts interviews for queued tasks
- Runs seeded judgment when fragments accumulate
- Generates plans for seeded tasks
- Initiates HITL review (respecting availability)
- Starts builds on approval

**Commands:**
- `pulse.py lifecycle start` — Create lifecycle agent
- `pulse.py lifecycle stop` — Delete lifecycle agent
- `pulse.py lifecycle status` — Show agent status
- `pulse.py lifecycle tick` — Manual single tick

### Fragment Tagging
Tag SMS responses to route to specific interviews:
```
#task-my-build This is my response about the feature
```

### Auto-Fix Dispatch
Tidying findings with confidence ≥ 0.9 auto-fix. Lower confidence escalates.
```

**3.2 Config additions:**

```json
{
  "lifecycle": {
    "poll_interval_minutes": 5,
    "seeded_threshold": 0.8,
    "max_seeded_attempts": 10,
    "idle_shutdown_minutes": 30
  },
  "auto_fix": {
    "enabled": true,
    "confidence_threshold": 0.9
  }
}
```

**3.3 SMS help update:**

Add to sms_intake help response:
```
#task-<slug> <message> — Reply to specific interview
pulse lifecycle start — Start automation
pulse lifecycle stop — Stop automation
```

### Unit Tests
- SKILL.md: Contains v3 lifecycle section
- Config: lifecycle settings present and valid JSON
- SMS help: Shows tag syntax

---

## Drop Briefs

| Stream | Drop | Title | Focus |
|--------|------|-------|-------|
| 1 | D1.1 | Lifecycle Agent | Create lifecycle_agent.py with tick logic |
| 1 | D1.2 | Availability Integration | Wire availability into review_manager |
| 1 | D1.3 | Pulse Lifecycle Command | Add `pulse.py lifecycle` subcommand |
| 2 | D2.1 | Fix Dispatcher Wiring | Wire into pulse.py tidying flow |
| 2 | D2.2 | Fragment Routing | Tag parsing + router update |
| 3 | D3.1 | Documentation + Config | SKILL.md, config, guidelines |

---

## Success Criteria

1. **Lifecycle automation works:** `n5 task X` → task auto-advances through stages without manual commands
2. **Availability respected:** HITL review deferred when V unavailable
3. **Auto-fix works:** High-confidence tidying findings auto-fix
4. **Tag routing works:** `#task-slug` SMS routes correctly
5. **Documentation complete:** SKILL.md reflects v3 capabilities

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Lifecycle agent runaway | Max 10 ticks per task state; idle shutdown |
| SMS spam during automation | Batch notifications; quiet hours check |
| Conflicts with manual workflow | Lifecycle agent only touches `queued`->`plan_review`; build phase unchanged |

---

## MECE Validation

### Scope Items
1. `lifecycle_agent.py` — D1.1
2. `review_manager.py` availability integration — D1.2
3. `pulse.py` lifecycle command — D1.3
4. `pulse.py` fix_dispatcher wiring — D2.1
5. `sms_intake.py` tag parsing — D2.2
6. `fragment_router.py` routing logic — D2.2
7. `SKILL.md` updates — D3.1
8. `pulse_v2_config.json` updates — D3.1
9. `pulse_v2_guidelines.md` updates — D3.1

### Verification
- No overlaps: Each file owned by exactly one Drop
- No gaps: All identified gaps from analysis addressed
- Reasonable scope: 6 Drops across 3 streams (can complete in ~2-3 hours)

---

## Execution Plan

1. **Stream 1 (parallel):** D1.1, D1.2, D1.3 — Core lifecycle infrastructure
2. **Stream 2 (parallel, after Stream 1):** D2.1, D2.2 — Wiring fixes
3. **Stream 3 (after Stream 2):** D3.1 — Documentation

Total estimated time: 2-3 hours automated execution.
