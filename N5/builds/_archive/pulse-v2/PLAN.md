---
created: 2026-01-24
last_edited: 2026-01-24
version: 2.2
type: build_plan
status: draft
provenance: con_pf8ZLEBtIiuNJzIs
incorporates:
  - con_T0QGg2ryaDjCTxVj (Pulse Genesis + Dashboard)
  - con_plquQK5mpVEUO74p (prompt-to-skill, 42% complete)
---

# Plan: Pulse v2 — Research/Content Orchestration with Interview Gates

**Objective:** Evolve Pulse from code-build-only to a general-purpose orchestration system supporting research, content, and analysis tasks — with human-in-the-loop interview gates, plan review, calendar-aware availability, post-build tidying swarm, and integrated teaching moments via VibeTeacher.

**Trigger:** V's realization that Pulse's orchestration primitives (queue → gate → parallel execution → synthesis) apply beyond code builds to research and content workflows.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Existing Work Incorporated

This plan builds on completed work from two parallel conversations:

### From con_T0QGg2ryaDjCTxVj (COMPLETE)
| Component | Status | Action |
|-----------|--------|--------|
| `pulse.py` | ✅ Exists | EXTEND |
| `sentinel.py` | ✅ Exists | EXTEND |
| `pulse_safety.py` | ✅ Exists | USE AS-IS |
| `pulse_learnings.py` | ✅ Exists | USE AS-IS |
| `pulse_dashboard_sync.py` | ✅ Exists | USE AS-IS |
| `pulse_integration_test.py` | ✅ Exists | EXTEND |
| Dashboard (build-tracker) | ✅ Live | USE AS-IS |
| SMS commands | ✅ Working | EXTEND |

**Known Gap:** Filter not wired into tick loop → **This plan addresses**

### From con_plquQK5mpVEUO74p (42% COMPLETE)
| Component | Status | Action |
|-----------|--------|--------|
| `pulse_code_validator.py` | ✅ Exists | WIRE INTO TICK |
| `pulse_llm_filter.py` | ✅ Exists | WIRE INTO TICK |
| `N5/scripts/lessons.py` | ✅ Exists | USE AS-IS |
| `N5/lib/close/` | ✅ Exists | USE AS-IS |
| `Skills/thread-close/` | ⚠️ Scaffolded | NOT IN SCOPE |
| `Skills/drop-close/` | ⚠️ Scaffolded | NOT IN SCOPE |
| `Skills/build-close/` | ⚠️ Scaffolded | NOT IN SCOPE |

**Recommendation:** Resume `prompt-to-skill` build after Pulse v2 core is stable.

---

## Open Questions

- [x] Deep work block convention → **Decision: `[DW]` prefix in calendar event title**
- [x] Response routing for interview → **Decision: Context inference with `#task-<slug>` override**
- [x] Google Drive folder location → **Decision: `Zo/Pulse Builds/<slug>/` in My Drive**
- [x] Skill name → **Decision: Pulse v2 (evolution of existing skill)**

---

## Alternatives Considered (Nemawashi)

### Alternative 1: Separate Skill (Rejected)
Create a new skill for research/content, keeping Pulse for code builds only.
**Why rejected:** Core orchestration primitives are identical. Would cause divergence.

### Alternative 2: Interview in Thread (Rejected)
Run interviews in the SMS/chat thread directly without separate storage.
**Why rejected:** Context window pollution, no multi-channel aggregation.

### Alternative 3: Google Docs for Everything (Rejected)
Store interview responses, plans, AND results all in Google Docs.
**Why rejected:** Over-reliance on external system. Local-first with Drive as outpost is cleaner.

---

## Trap Doors Identified

| Trap Door | Risk Level | Mitigation |
|-----------|------------|------------|
| Interview storage schema | HIGH | Design schema carefully; migration later is painful |
| Google Drive folder structure | MEDIUM | Mirror local structure exactly |
| Persona prompt modifications | MEDIUM | Additive changes only |
| Task queue schema | HIGH | Include extensibility fields; version the schema |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PULSE v2 PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐   ┌─────────┐   ┌───────────┐   ┌─────────┐   ┌────────────┐  │
│  │ INTAKE  │──▶│ QUEUED  │──▶│ INTERVIEW │──▶│ SEEDED  │──▶│  PLAN GEN  │  │
│  │ SMS/    │   │ Task    │   │ Fragment  │   │ LLM     │   │ Decompose  │  │
│  │ Email   │   │ Queue   │   │ Storage   │   │ Judges  │   │ to Drops   │  │
│  └─────────┘   └─────────┘   └───────────┘   └─────────┘   └────────────┘  │
│                                    │                             │         │
│                              [HITL Gate]                         ▼         │
│                              Availability              ┌────────────────┐  │
│                              Aware                     │  PLAN REVIEW   │  │
│                               +                        │ Google Doc +   │  │
│                            🎓 VIBE                     │ SMS Link       │  │
│                            TEACHER                     │ [HITL Gate]    │  │
│                                                        │ + 🎓 TEACHING  │  │
│                                                        └────────────────┘  │
│                                                                  │         │
│       ┌──────────────────────────────────────────────────────────┘         │
│       ▼                                                                    │
│  ┌─────────┐   ┌─────────────┐   ┌──────────┐   ┌──────────┐              │
│  │  BUILD  │──▶│   TIDYING   │──▶│ DELIVERY │──▶│ FEEDBACK │              │
│  │ Pulse   │   │   SWARM     │   │ Artifact │   │ Learning │              │
│  │ Drops   │   │ 5 Hygiene   │   │ + SMS    │   │ Extract  │              │
│  │ +FILTER │   │ Drops       │   │          │   │ + 🎓 VIBE│              │
│  └─────────┘   └─────────────┘   └──────────┘   └──────────┘              │
│       │              │                                                     │
│  [code_validator]  [Auto-fix                    [FINAL REVIEW]             │
│  [llm_filter]       or Escalate]                🎓 Comprehensive           │
│                                                  Teaching Summary          │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Checklist

### Phase 1: Foundation + Validator Wiring
- ☐ Create task queue schema and storage
- ☐ Create interview storage schema and handlers
- ☐ Add Pulse v2 config with default_build_model variable
- ☐ **WIRE `pulse_code_validator.py` into tick loop**
- ☐ **WIRE `pulse_llm_filter.py` into tick loop**
- ☐ Test: Deposit with stub code → REJECTED by validator

### Phase 2: Interview & Availability
- ☐ Build multi-channel intake handlers (SMS, email)
- ☐ Build interview fragment aggregator
- ☐ Build availability checker (calendar + deep work blocks)
- ☐ Build seeded-judgment evaluator
- ☐ Test: Interview fragments aggregate; seeded judgment works

### Phase 3: Plan Pipeline + Google Drive
- ☐ Build plan generator (interview → decomposed plan)
- ☐ Build Google Drive outpost manager
- ☐ Build HITL review flow (SMS + approval handling)
- ☐ Extend pulse.py with plan-review stage
- ☐ Test: Plan uploads to Drive; SMS contains shareable link

### Phase 4: Tidying Swarm
- ☐ Create 5 hygiene Drop templates
- ☐ Build findings aggregator
- ☐ Build auto-fix vs escalate logic
- ☐ Integrate tidying stage into pulse.py lifecycle
- ☐ Test: Tidying swarm runs post-build; findings aggregated

### Phase 5: Telemetry & Personas
- ☐ Add model/persona tracking to telemetry
- ☐ Create requirements tracking module
- ☐ Update personas with requirements tracking behavior
- ☐ Build feedback-to-learning extractor
- ☐ Test: Errors log persona + model

### Phase 6: VibeTeacher Integration
- ☐ Create VibeTeacher persona (or update existing Teacher)
- ☐ Build teaching moment generator
- ☐ Build technical glossary system
- ☐ Integrate VibeTeacher at HITL gates
- ☐ Build final review synthesis
- ☐ Test: Teaching moments generated at plan review; final summary includes glossary

---

## Pre-Phase: Standalone Validator Fix (D0.1)

**Ship immediately before main build starts.**

This is the critical gap identified in con_plquQK5mpVEUO74p — validators exist but aren't wired into the tick loop.

### Affected Files
- `Skills/pulse/scripts/pulse.py` - UPDATE - Wire validators

### Changes
Wire `pulse_code_validator.py` and `pulse_llm_filter.py` into tick loop (see Phase 1 code block for implementation).

### Success Criteria
- Deposit with stub code (`pass`, `TODO`, `NotImplementedError`) → REJECTED
- Deposit with hallucinated import → REJECTED  
- Lesson logged for each rejection

### Execution
This can run NOW as a single-Drop fix. No dependencies on rest of build.

```bash
# After D0.1 completes, verify:
python3 Skills/pulse/scripts/pulse.py tick <test-slug>
# Should reject deposits with stubs
```

---

## Phase 1: Foundation + Validator Wiring

### Affected Files
- `Skills/pulse/config/pulse_v2_config.json` - CREATE
- `N5/pulse/queue/task_queue.json` - CREATE
- `N5/pulse/queue_manager.py` - CREATE
- `N5/pulse/interview_manager.py` - CREATE
- `Skills/pulse/scripts/pulse.py` - UPDATE - **Wire validators into tick**

### Changes

**1.1 Pulse v2 Configuration:**
```json
{
  "version": "2.0",
  "default_build_model": "claude-opus-4-20250514",
  "task_types": ["code_build", "research", "content", "analysis", "hybrid"],
  "interview": {
    "seeded_threshold": 0.8,
    "max_fragments": 50,
    "channels": ["sms", "email", "chat"]
  },
  "availability": {
    "deep_work_marker": "[DW]",
    "check_calendar": true
  },
  "validation": {
    "code_validator_enabled": true,
    "llm_filter_enabled": true,
    "auto_reject_on_critical": true
  },
  "tidying_swarm": {
    "enabled": true,
    "auto_fix_threshold": 0.9
  },
  "google_drive": {
    "outpost_folder": "Zo/Pulse Builds",
    "email": "attawar.v@gmail.com"
  },
  "vibe_teacher": {
    "enabled": true,
    "activation_points": ["interview_complete", "plan_review", "feedback", "build_complete"],
    "glossary_path": "N5/pulse/teaching/glossary.json"
  }
}
```

**1.2 Task Queue Schema & Manager:**
- `add_task()`, `list_tasks()`, `prioritize()`, `advance()`, `get_next()`
- Task states: `queued → interviewing → seeded → planning → plan_review → building → tidying → complete`

**1.3 Interview Storage (JSONL):**
```
N5/pulse/interviews/<task-id>.jsonl
```

Each line is a fragment:
```jsonl
{"timestamp": "2026-01-24T15:00:00Z", "channel": "sms", "content": "...", "processed": false}
{"timestamp": "2026-01-24T15:05:00Z", "channel": "email", "content": "...", "processed": false}
```

Synthesis stored separately:
```
N5/pulse/interviews/<task-id>_synthesis.json
N5/pulse/interviews/<task-id>_judgment.json
```

**1.4 CRITICAL: Wire Validators into Tick Loop:**

Update `pulse.py` tick logic (around line where deposits are checked):

```python
# BEFORE (current - auto-passes):
if deposit_exists and not filtered:
    # mark as filtered and continue
    
# AFTER (with validation):
if deposit_exists and not filtered:
    # 1. Run mechanical validation
    code_result = subprocess.run([
        "python3", "Skills/pulse/scripts/pulse_code_validator.py",
        "check", slug, drop_id
    ], capture_output=True, text=True)
    code_data = json.loads(code_result.stdout)
    
    if code_data.get("critical_count", 0) > 0:
        mark_deposit_failed(slug, drop_id, "code_validation", code_data)
        log_lesson("stub_code", f"Drop {drop_id} failed code validation", slug, drop_id)
        continue
    
    # 2. Run LLM validation
    llm_result = subprocess.run([
        "python3", "Skills/pulse/scripts/pulse_llm_filter.py",
        "validate", slug, drop_id
    ], capture_output=True, text=True)
    llm_data = json.loads(llm_result.stdout)
    
    if not llm_data.get("pass", False):
        mark_deposit_failed(slug, drop_id, "llm_validation", llm_data)
        log_lesson("llm_hallucination", f"Drop {drop_id} failed LLM filter: {llm_data.get('reason')}", slug, drop_id)
        continue
    
    # 3. Mark as filtered (passed both)
    mark_deposit_filtered(slug, drop_id)
```

### Unit Tests
- Queue: Add task → list shows task → prioritize moves to front
- Interview: Create → add fragments → synthesize produces output
- **Validator wiring: Deposit with `pass` stub → rejected with lesson logged**
- **LLM filter wiring: Deposit with fake import → rejected**

---

## Phase 2: Interview & Availability

### Affected Files
- `N5/pulse/sms_intake.py` - CREATE
- `N5/pulse/email_intake.py` - CREATE
- `N5/pulse/classifier.py` - CREATE
- `N5/pulse/fragment_router.py` - CREATE
- `N5/pulse/availability/calendar_checker.py` - CREATE
- `N5/pulse/seeded_judge.py` - CREATE

### Changes

**2.1 Multi-Channel Intake:**
SMS commands:
- `n5 task <description>` → add task to queue
- `n5 tasks` → list pending tasks
- `n5 prioritize <slug>` → bump task priority

**2.2 Fragment Router:**
1. Check explicit tag: `#task-<slug>` → route to that interview
2. One open interview → route there
3. Multiple open → ask for clarification
4. None open → treat as new task

**2.3 Availability Checker:**
- `is_available()` → no meeting, no `[DW]` event, not quiet hours
- `next_available_window()` → when V is next free
- Uses Google Calendar API

**2.4 Seeded Judgment:**
- Synthesizes fragments
- Evaluates completeness
- Returns `{seeded: bool, confidence: float, missing: []}`

**2.5 Fallback: Manual Availability**
If Calendar API fails or is not connected:
- `is_available()` defaults to `True` during configured hours (9am-6pm ET)
- SMS prompt: "Calendar unavailable. Are you free to review? Reply 'yes' or 'later'"
- Manual override always available: `n5 available` / `n5 busy`

### Unit Tests
- Intake: SMS "write blog about AI" → task created as "content"
- Router: Message with `#task-xyz` → routes to interview xyz
- Availability: Calendar with `[DW]` → is_available() = False

---

## Phase 3: Plan Pipeline + Google Drive

### Affected Files
- `N5/pulse/plan_generator.py` - CREATE
- `N5/pulse/decomposer.py` - CREATE
- `N5/pulse/outpost_manager.py` - CREATE
- `N5/pulse/review_manager.py` - CREATE
- `Skills/pulse/scripts/pulse.py` - UPDATE - Add plan-review stage

### Changes

**3.1 Plan Generator:**
Decomposition strategies by type:
- `research`: Parallel angles → synthesis
- `content`: Outline → draft → edit → finalize
- `analysis`: Gather → analyze → visualize → summarize
- `code_build`: Standard Pulse decomposition

**3.2 Google Drive Outpost:**
- `ensure_folder(slug)` → create `Zo/Pulse Builds/<slug>/`
- `upload_plan(slug, content)` → upload as Google Doc
- `get_shareable_link(slug)` → return link
- Uses `use_app_google_drive`

**3.3 HITL Review Flow:**
1. Upload plan to Drive
2. SMS: "Plan ready for '<task>': [link]. Reply 'go' or 'revise: [feedback]'"
3. On `go`: advance to build
4. On `revise: X`: regenerate plan

**3.4 Pulse.py Plan-Review Stage:**
New lifecycle:
```
pending → interviewing → seeded → planning → plan_review → building → tidying → complete
```

**3.5 Fallback: Local-Only Mode**
If Google Drive API fails:
- Plan saved locally to `N5/builds/<slug>/PLAN.md` (already happens)
- SMS includes plan summary (first 500 chars) + "Full plan at local path: ..."
- Flag in meta.json: `"drive_sync_failed": true`
- Retry sync on next tick or manual: `pulse.py sync-drive <slug>`

### Unit Tests
- Generator: type="research" → parallel research Drops
- Outpost: Upload → folder exists in Drive → link shareable
- Review: "go" response → status advances

---

## Phase 4: Tidying Swarm

### Affected Files
- `Skills/pulse/drops/tidying/*.md` - CREATE - 5 templates
- `N5/pulse/findings_aggregator.py` - CREATE
- `N5/pulse/fix_dispatcher.py` - CREATE
- `Skills/pulse/scripts/pulse.py` - UPDATE - Add tidying stage

### Changes

**4.1 Five Hygiene Drop Templates:**

| Drop | Checks | Auto-Fix? |
|------|--------|-----------|
| `integration_test.md` | Cross-component behavior | No (report) |
| `reference_check.md` | Broken imports, dead paths | Yes (simple) |
| `stub_scan.md` | TODOs, NotImplementedError | No (escalate) |
| `dedup.md` | Duplicate code/files | Partial |
| `cleanup.md` | Debug statements, dead code | Yes (safe) |

**4.2 Findings Aggregator:**
- Collects all 5 deposits
- Categorizes: critical/warning/info
- Computes health score

**4.3 Fix Dispatcher:**
```python
if finding.auto_fixable and finding.confidence >= 0.9:
    spawn_fix_drop(finding)
else:
    add_to_escalation(finding)
```

**4.4 Tidying Stage:**
After BUILD:
1. Spawn 5 tidying Drops (parallel)
2. Aggregate findings
3. Dispatch fixes or escalate
4. Advance to DELIVERY

### Unit Tests
- Stub scanner: File with TODO → found in findings
- Aggregator: 5 deposits → health score computed
- Dispatcher: Auto-fixable finding → fix Drop spawned

---

## Phase 5: Telemetry & Personas

### Affected Files
- `N5/pulse/telemetry_manager.py` - CREATE
- `N5/pulse/requirements_tracker.py` - CREATE
- `N5/pulse/feedback_extractor.py` - CREATE
- Persona prompts - UPDATE (via `edit_persona`)

### Changes

**5.1 Telemetry Manager:**
Auto-enriches events with:
- `persona_id`, `persona_name`
- `model_name`, `used_default_model`
- `conversation_id`, `build_slug`

**5.2 Requirements Tracker:**
- Captures "I want...", "always...", "never..." statements
- Exports to REQUIREMENTS.md per build

**5.3 Persona Updates:**
Add to Operator, Builder, Debugger, Architect:
```
When in build context:
- Monitor for requirement/preference/decision statements
- Log via requirements_tracker.py
- On errors, log telemetry with persona + model
```

### Unit Tests
- Telemetry: Log error → includes persona + model
- Requirements: "I want X" → stored as requirement
- Personas: Updated prompts contain tracking behavior

---

## Phase 6: VibeTeacher Integration

### Affected Files
- `N5/pulse/teaching/vibe_teacher.py` - CREATE - Core teaching engine
- `N5/pulse/teaching/glossary.json` - CREATE - Technical glossary storage
- `N5/pulse/teaching/moment_generator.py` - CREATE - Teaching moment logic
- `N5/pulse/teaching/final_review.py` - CREATE - End-of-build synthesis
- Persona: VibeTeacher - CREATE or UPDATE existing Teacher persona

### Changes

**6.1 VibeTeacher Persona:**

Create or extend Teacher persona with build-specific capabilities:

```markdown
## VibeTeacher (Build Context)

Activates at HITL gates during Pulse builds to:

1. **Explain what just happened** — Summarize technical actions in accessible terms
2. **Fill terminology gaps** — When V uses imprecise language, provide the precise term
3. **Surface teaching moments** — Opportunities to learn concepts relevant to this build
4. **Sense-check** — Verify V's modifications make semantic sense before proceeding

### Activation Points
- Interview complete → Explain what info was gathered and why it matters
- Plan review → Explain architectural decisions, terminology in the plan
- Feedback collection → Translate V's feedback into precise technical framing
- Build complete → Comprehensive summary + glossary of terms learned

### Tone
- Conversational, not condescending
- Build understanding, don't just define
- Use analogies when helpful
- Respect V's existing knowledge, push boundaries incrementally
```

**6.2 Teaching Moment Generator:**

`moment_generator.py`:
```python
def generate_moment(context: dict) -> TeachingMoment:
    """
    Analyzes context (recent actions, V's language, build state)
    Returns teaching moment with:
    - concept: What to teach
    - v_said: What V said that triggered this
    - precise_term: The technical term
    - explanation: Accessible explanation
    - example: Concrete example from this build
    - absorbed: False (default - V must acknowledge)
    """
```

**6.3 Technical Glossary:**

`glossary.json` structure:
```json
{
  "version": "1.0",
  "terms": {
    "idempotent": {
      "definition": "An operation that produces the same result no matter how many times you run it",
      "v_context": "You mentioned 'making sure it doesn't duplicate' — the technical term is idempotent",
      "build_slug": "pulse-v2",
      "learned_at": "2026-01-24T16:30:00Z",
      "absorbed": true
    }
  },
  "pending_review": [
    {
      "term": "MECE",
      "definition": "Mutually Exclusive, Collectively Exhaustive — a way to divide work so nothing overlaps and nothing is missed",
      "build_slug": "pulse-v2",
      "absorbed": false
    }
  ]
}
```

**6.4 HITL Gate Integration:**

At each HITL gate, before presenting to V:

```python
def hitl_gate_with_teaching(gate_type: str, content: dict, build_slug: str):
    # 1. Generate teaching moment for this gate
    moment = generate_teaching_moment(gate_type, content, build_slug)
    
    # 2. Check for terminology opportunities
    glossary_additions = scan_for_new_terms(content, build_slug)
    
    # 3. Compose message
    message = compose_hitl_message(content)
    
    if moment:
        message += f"\n\n🎓 **Teaching moment:** {moment.explanation}"
        message += f"\n_You said: \"{moment.v_said}\" → Technical term: **{moment.precise_term}**_"
    
    if glossary_additions:
        message += f"\n\n📚 **New terms:** {', '.join([t['term'] for t in glossary_additions])}"
    
    # 4. Send via SMS/notification
    send_hitl_notification(message)
    
    # 5. Store pending teaching moments
    store_pending_moments(moments, glossary_additions, build_slug)
```

**6.5 Final Review Synthesis:**

`final_review.py` — runs at build complete:

```python
def generate_final_review(build_slug: str) -> FinalReview:
    """
    Produces comprehensive teaching summary:
    
    1. Build recap (what was accomplished, in accessible terms)
    2. Architectural decisions explained (why things were structured this way)
    3. Glossary of terms encountered (with V's original language → precise term)
    4. Teaching moments delivered (list with absorbed status)
    5. "What V said vs. how to say it next time" — concrete vocabulary upgrades
    6. Concepts for further exploration (optional reading/learning)
    """
    
    # Gather all teaching moments from build
    moments = load_build_moments(build_slug)
    
    # Gather glossary terms added during build
    terms = load_build_glossary_terms(build_slug)
    
    # Generate synthesis
    return FinalReview(
        build_recap=generate_recap(build_slug),
        decisions_explained=explain_decisions(build_slug),
        glossary=terms,
        teaching_moments=moments,
        vocabulary_upgrades=extract_vocabulary_upgrades(moments),
        further_exploration=suggest_further_learning(build_slug)
    )
```

**6.6 Absorption Tracking:**

Teaching moments have `absorbed: false` by default. V acknowledges via:
- SMS: "got it" / "absorbed" / "👍" after receiving a moment
- Checkbox in final review document
- Explicit: "I understand X now"

Unabsorbed moments persist and may resurface in future builds if relevant concepts recur.

**6.7 Output Formats:**

Teaching moments can output to:
- SMS (inline with HITL notification)
- Build's `TEACHING.md` file (accumulated)
- Final review Google Doc (at build end)
- Glossary JSON (persistent)

### Unit Tests
- Moment generator: V says "the thing that runs over and over" → suggests "loop" or "iteration"
- Glossary: New term added → appears in pending_review with absorbed=false
- Final review: Build with 3 moments → synthesis includes all 3 with vocabulary upgrades
- Absorption: V replies "got it" → moment.absorbed = true

---

## Drop Briefs

| Stream | Drop | Title | Focus |
|--------|------|-------|-------|
| 0 | D0.1 | Validator Wiring Fix | SHIP FIRST - Wire validators into tick loop |
| 1 | D1.1 | Queue + Config | Task queue schema + Pulse v2 config |
| 1 | D1.2 | Interview Storage | JSONL fragment storage and synthesis |
| 2 | D2.1 | Multi-Channel Intake | SMS/email handlers + classifier |
| 2 | D2.2 | Availability + Seeded Judge | Calendar checker (+ manual fallback) + seeded evaluation |
| 3 | D3.1 | Plan Generator | Interview → plan decomposition |
| 3 | D3.2 | Google Drive Outpost | Drive folder + doc upload (+ local fallback) |
| 3 | D3.3 | Review Flow + Pulse.py Stages | HITL review + lifecycle update |
| 4 | D4.1 | Tidying Drop Templates | 5 hygiene templates |
| 4 | D4.2 | Tidying Orchestration | Aggregator + dispatcher + pulse.py |
| 5 | D5.1 | Telemetry + Requirements | Tracking modules |
| 5 | D5.2 | Feedback Extractor | Learning extraction |
| 5 | D5.3 | Persona Updates + Docs | Persona modifications + SKILL.md |
| 6 | D6.1 | VibeTeacher Core | Persona + moment generator + glossary |
| 6 | D6.2 | VibeTeacher Integration | HITL hooks + final review + absorption |
| 6 | D6.3 | Architectural Principles Update | Update N5/prefs/ with learnings from this build |

---

## Success Criteria

1. **Validators wired**: Deposit with stub → REJECTED with lesson logged
2. **Task intake works**: SMS "n5 task X" creates queued task
3. **Interview completes**: Fragments aggregate; LLM judges seeded
4. **Plan review works**: Google Doc created, shareable link in SMS
5. **Tidying swarm runs**: 5 Drops execute, findings aggregated
6. **Telemetry captured**: Errors log persona + model
7. **VibeTeacher activates**: Teaching moment generated at plan review gate
8. **Glossary populated**: New terms added during build with absorbed=false
9. **Final review generated**: Comprehensive summary with vocabulary upgrades

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Google Drive API limits | Batch operations, cache folder IDs |
| Calendar API auth | Use existing connected account |
| Validator false positives | Tunable thresholds in config |
| Tidying swarm timeout | 15 min per Drop, parallel execution |
| Teaching moments annoying/too frequent | Config toggle, only surface high-value moments |
| Glossary bloat | Periodic review, merge similar terms |

---

## Dependencies on Paused Build

The `prompt-to-skill` build (42% complete) created infrastructure this build uses:
- `pulse_code_validator.py` ← we wire this
- `pulse_llm_filter.py` ← we wire this
- `N5/scripts/lessons.py` ← we use this
- `N5/lib/close/` ← not in scope but exists

**After Pulse v2:** Resume `prompt-to-skill` with `python3 Skills/pulse/scripts/pulse.py resume prompt-to-skill`

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. **Radical simplicity** — Consider shipping validator wiring alone first
2. **Flatten directory structure** — 10 new directories may be over-engineering
3. **SMS inline summary** — Don't force Drive click for simple plans
4. **JSONL for fragments** — Single file vs directory of JSON files
5. **Fallback paths** — What if Drive/Calendar APIs fail?
6. **Phase split** — Ship v2.0a (foundation) before v2.0b (full pipeline)

### Incorporated:
- ✅ **Validator wiring as D0.1** — Ships first as standalone fix before main build
- ✅ **Flattened directory** — `N5/pulse/` with descriptive filenames, not 10 subdirs
- ✅ **SMS inline + Drive link** — Plan summary in SMS, full doc in Drive
- ✅ **JSONL fragments** — `N5/pulse/interviews/<task-id>.jsonl` instead of fragments/
- ✅ **Fallback paths** — Local-only mode if Drive fails; manual availability if Calendar fails
- ✅ **D6.3 added** — Update architectural principles in `N5/prefs/` post-build

### Rejected (with rationale):
- ❌ **Phase split** — V has capacity now; comprehensive build enables the "background work while waiting" future state faster

---

## Architectural Principles

**Skills, not prompts:** All deliverables are executable skills in `Skills/` or reusable modules in `N5/`. No new prompts in `Prompts/` — that pattern is deprecated.

**Flat over nested:** Prefer `N5/pulse/queue_manager.py` over `N5/pulse/queue/queue_manager.py` unless genuine organizational benefit.

**Local-first with outposts:** Source of truth is workspace. Google Drive is a shareable outpost, not primary storage.

**Graceful degradation:** Every external integration (Drive, Calendar, SMS) has a local fallback path.