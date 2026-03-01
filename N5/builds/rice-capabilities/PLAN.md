---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: n5os-rice-architecture
type: build_plan
status: planned
---

# Rice Capabilities — The 8 Infrastructure Modules

**Build slug:** `rice-capabilities`
**One-liner:** Implement all 8 Zoffice capabilities (Ingestion, Communication, Publishing, Orchestration, Zo2Zo, Security, HR, Memory) as modular infrastructure inside the Zoffice/capabilities/ directory.

## Objective

Populate the empty `Zoffice/capabilities/` skeleton (created by rice-core) with working infrastructure modules. Each capability is a self-contained unit with:
- README.md (purpose, status, API surface)
- config.yaml (capability-specific configuration)
- Handler scripts or protocol definitions
- Integration hooks that other capabilities and staff can call

This build creates the PLUMBING — not the employees who use it. Staff are wired in by rice-staff and rice-integration.

## Open Questions

All resolved during architecture phase (Stream 1). No open questions remain.

## Dependencies

- **Hard prerequisite:** rice-core must be complete (Zoffice/ directory tree, config schemas, office.db)
- **Downstream:** rice-staff (staff use capabilities), rice-integration (wires capabilities to routing)
- **Reference material:** Existing va assets that map to Zoffice capabilities (see architecture doc "What Carries Over" table)

## Decisions (ALL FINAL)

| Decision | Status | Detail |
|----------|--------|--------|
| 8 capabilities | FINAL | Ingestion, Communication, Publishing, Orchestration, Zo2Zo, Security, HR, Memory |
| Security always-on | FINAL | Security capability cannot be disabled once installed |
| Memory = shared DB | FINAL | All capabilities read/write to single office.db |
| Capability independence | FINAL | Each capability functions standalone; cross-capability calls go through defined interfaces |
| Config location | FINAL | Each capability has its own config.yaml inside its directory |

## Success Criteria

1. All 8 capability directories contain README.md, config.yaml, and handler/protocol files
2. Security gate validates inbound content (adversarial detection + PII filter)
3. Audit system writes to office.db audit table with hash verification
4. Memory capability can CRUD contacts, conversations, decisions in office.db
5. Communication capability can draft and queue outbound messages (respecting autonomy.yaml)
6. Ingestion capability has handler framework for email, voice, webhook, zo2zo channels
7. Orchestration has dispatcher skeleton (morning, evening, healthcheck)
8. HR has employee evaluation rubric and handoff protocol
9. Zo2Zo has trust verification and parent escalation protocol
10. Publishing has content pipeline skeleton with approval gates
11. `python3 Skills/zoffice-setup/scripts/healthcheck.py` still passes with capabilities installed

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Capability scope creep (building too much) | Each capability ships as skeleton + 1 working handler. Depth comes in Layer 2. |
| Cross-capability coupling | Define clean interfaces in README.md; no direct imports between capability dirs |
| Security gate false positives | Configurable sensitivity in security/config.yaml; default is strict |
| DuckDB contention from multiple capabilities | Single-writer pattern; capabilities use helper functions from memory capability |
| Existing va patterns don't map cleanly | Adapt patterns, don't copy-paste. Zoffice is greenfield. |

---

## Checklist

### Phase 1: Security & Memory (Foundation Capabilities)
- [ ] Security: inbound gate with adversarial detection
- [ ] Security: PII filter (pattern-based)
- [ ] Security: audit writer (office.db audit table + content hashing)
- [ ] Security: config.yaml with detection rules and sensitivity levels
- [ ] Memory: office.db helper module (CRUD for contacts, conversations, decisions)
- [ ] Memory: contact lookup (by phone, email, name)
- [ ] Memory: conversation logger
- [ ] Memory: decision queue manager (create, resolve, expire)
- [ ] Memory: README.md and config.yaml
- [ ] Test: Security gate blocks known adversarial patterns
- [ ] Test: Audit entry written with valid hash
- [ ] Test: Memory CRUD operations on all 3 tables

### Phase 2: Ingestion & Communication (I/O Capabilities)
- [ ] Ingestion: handler framework (base class + channel dispatch)
- [ ] Ingestion: email handler skeleton (tag-based routing)
- [ ] Ingestion: voice handler skeleton (VAPI webhook receiver)
- [ ] Ingestion: webhook handler skeleton (generic receiver)
- [ ] Ingestion: zo2zo handler (authenticated inbound from trusted instances)
- [ ] Ingestion: classification function (type, urgency, topic tagging)
- [ ] Communication: multi-channel dispatch (employee -> channel selection)
- [ ] Communication: approval gate (checks autonomy.yaml thresholds)
- [ ] Communication: template system (Markdown templates with variable substitution)
- [ ] Communication: rate limiter + deduplication
- [ ] Communication: outbound audit logging
- [ ] Test: Inbound item gets UUID, timestamp, classification, audit entry
- [ ] Test: Outbound message below threshold gets queued for approval (not sent)

### Phase 3: Orchestration, Zo2Zo, Publishing, HR
- [ ] Orchestration: dispatcher framework (scheduled task definitions)
- [ ] Orchestration: morning dispatcher template
- [ ] Orchestration: evening dispatcher template
- [ ] Orchestration: healthcheck agent template
- [ ] Orchestration: workflow engine skeleton (intake -> process -> respond)
- [ ] Zo2Zo: trust registry (YAML-based, loaded from security.yaml)
- [ ] Zo2Zo: parent link protocol (escalate to parent instance)
- [ ] Zo2Zo: skill receiver (accept skill bundles from parent)
- [ ] Zo2Zo: inbound trust verification
- [ ] Publishing: content pipeline skeleton (draft -> review -> publish)
- [ ] Publishing: zo.space page framework (landing page template)
- [ ] Publishing: approval gate (always-on by default)
- [ ] HR: employee evaluation rubric (scenario-based scoring)
- [ ] HR: handoff protocol (structured context transfer between employees)
- [ ] HR: staff registry sync (file definitions -> Zo personas)
- [ ] HR: onboarding protocol (what happens when a new employee is added)
- [ ] Test: Dispatcher loads and lists scheduled tasks
- [ ] Test: Zo2Zo trust verification accepts trusted instance, rejects unknown
- [ ] Test: HR evaluation creates entry in evaluations table

---

## Phase 1: Security & Memory (Foundation Capabilities)

### Affected Files

- `Zoffice/capabilities/security/README.md` - UPDATE - Full capability description
- `Zoffice/capabilities/security/config.yaml` - CREATE - Detection rules, sensitivity
- `Zoffice/capabilities/security/gates/inbound_gate.py` - CREATE - Adversarial detection + PII filter
- `Zoffice/capabilities/security/audit/writer.py` - CREATE - Audit trail writer with hash verification
- `Zoffice/capabilities/security/audit/schema.sql` - CREATE - Reference SQL for audit table
- `Zoffice/capabilities/memory/README.md` - UPDATE - Full capability description
- `Zoffice/capabilities/memory/config.yaml` - CREATE - DB path, retention settings
- `Zoffice/capabilities/memory/db_helpers.py` - CREATE - CRUD operations for office.db
- `Zoffice/capabilities/memory/contact_manager.py` - CREATE - Contact lookup, upsert, history
- `Zoffice/capabilities/memory/conversation_logger.py` - CREATE - Conversation tracking
- `Zoffice/capabilities/memory/decision_queue.py` - CREATE - Decision create/resolve/expire

### Changes

**1.1 Security — Inbound Gate:**
Python module that validates inbound content. Two passes:
- Adversarial detection: pattern matching for prompt injection, jailbreak attempts, social engineering
- PII filter: regex patterns for SSN, credit card, phone (configurable sensitivity)

Returns `{allowed: bool, flags: [], filtered_content: str}`. Logs to audit table regardless of outcome.

Detection patterns are configurable in config.yaml — the gate reads them at runtime, not hardcoded.

**1.2 Security — Audit Writer:**
Python module that writes to office.db audit table. Every entry gets:
- UUID (generated)
- Timestamp (current)
- Content hash (SHA-256 of action + metadata for tamper detection)
- Parent event ID (for chaining related events)

Exposes `log_audit(capability, employee, action, channel, counterparty, metadata)` function.

**1.3 Memory — DB Helpers:**
Thin Python wrapper around DuckDB for office.db operations. Provides:
- `get_db()` -> connection (singleton pattern)
- `insert_contact(...)`, `get_contact(id)`, `find_contact(email=, phone=, name=)`
- `log_conversation(...)`, `get_conversations(counterparty_id=, employee=, channel=)`
- `create_decision(...)`, `resolve_decision(id, resolution, resolved_by)`, `get_pending_decisions()`
- `insert_evaluation(...)`, `get_evaluations(employee=)`

All functions handle connection lifecycle. No raw SQL leaks outside this module.

**1.4 Memory — Contact Manager:**
Higher-level contact operations:
- Lookup by phone, email, or name (fuzzy)
- Upsert (create if new, update if existing)
- Interaction history (join conversations + audit by counterparty)
- Tag management

### Unit Tests
- Inbound gate blocks string containing `ignore previous instructions`
- Inbound gate flags PII (test SSN pattern)
- Audit writer creates entry with valid SHA-256 hash
- Memory CRUD: create contact -> find by email -> update -> verify
- Memory: create decision -> get pending -> resolve -> verify status change

---

## Phase 2: Ingestion & Communication (I/O Capabilities)

### Affected Files

- `Zoffice/capabilities/ingestion/README.md` - UPDATE - Full capability description
- `Zoffice/capabilities/ingestion/config.yaml` - CREATE - Channel configs, routing rules
- `Zoffice/capabilities/ingestion/handlers/base.py` - CREATE - Base handler class
- `Zoffice/capabilities/ingestion/handlers/email_handler.py` - CREATE - Email intake with tag routing
- `Zoffice/capabilities/ingestion/handlers/voice_handler.py` - CREATE - VAPI webhook receiver skeleton
- `Zoffice/capabilities/ingestion/handlers/webhook_handler.py` - CREATE - Generic webhook receiver
- `Zoffice/capabilities/ingestion/handlers/zo2zo_handler.py` - CREATE - Authenticated Zo2Zo intake
- `Zoffice/capabilities/ingestion/classify.py` - CREATE - Content classification function
- `Zoffice/capabilities/communication/README.md` - UPDATE - Full capability description
- `Zoffice/capabilities/communication/config.yaml` - CREATE - Channel configs, rate limits
- `Zoffice/capabilities/communication/channels/dispatch.py` - CREATE - Multi-channel dispatcher
- `Zoffice/capabilities/communication/channels/approval.py` - CREATE - Autonomy-aware approval gate
- `Zoffice/capabilities/communication/templates/base.md` - CREATE - Template format spec
- `Zoffice/capabilities/communication/templates/acknowledgment.md` - CREATE - Acknowledgment template
- `Zoffice/capabilities/communication/templates/escalation-notice.md` - CREATE - Escalation template
- `Zoffice/capabilities/communication/templates/follow-up.md` - CREATE - Follow-up template
- `Zoffice/capabilities/communication/channels/rate_limiter.py` - CREATE - Rate limiting + dedup

### Changes

**2.1 Ingestion — Handler Framework:**
Base handler class that all channel handlers extend:
```python
class InboundHandler:
    def receive(self, raw_input) -> InboundItem
    def classify(self, item) -> ClassifiedItem
    def route(self, item) -> str  # employee name
    def log(self, item) -> None   # audit entry
```

Every inbound item gets a UUID, timestamp, source channel, classification, and routing decision.

**2.2 Ingestion — Channel Handlers:**
- `email_handler.py`: Reads email content, extracts subject tags (e.g., [JD], [RESUME]), routes based on tag patterns in ingestion/config.yaml
- `voice_handler.py`: VAPI webhook receiver skeleton — accepts POST, extracts caller info, returns employee assignment. NOT a full VAPI server (that's Layer 2 per-persona), just the routing layer.
- `webhook_handler.py`: Generic receiver — validates signature, extracts payload, routes by webhook source
- `zo2zo_handler.py`: Validates caller against trust registry, verifies API key, routes to appropriate employee

**2.3 Ingestion — Classifier:**
Content classification function that tags inbound items with:
- Type: inquiry, request, complaint, information, escalation
- Urgency: low, normal, high, critical
- Topic: extracted keywords/domain

Uses simple keyword matching for base install. Can be replaced with LLM classification in Layer 2.

**2.4 Communication — Dispatch & Approval:**
- `dispatch.py`: Employee calls `send_message(recipient, content, channel_preference)`. Dispatcher selects best channel, formats message, and either sends immediately or queues for approval based on autonomy.yaml.
- `approval.py`: Reads autonomy.yaml thresholds. Checks if the action is in `always_escalate` list. If so, queues as decision. Otherwise, checks confidence score against thresholds to decide: auto_act, act_and_notify, escalate_to_parent, or escalate_to_human.

**2.5 Communication — Templates:**
Markdown-based templates with `{{variable}}` substitution. Base install includes:
- `acknowledgment.md` — "We received your message, {{name}}"
- `escalation-notice.md` — "I'm connecting you with {{employee_or_human}}"
- `follow-up.md` — "Following up on our conversation about {{topic}}"

### Unit Tests
- Email handler extracts [JD] tag and routes to configured employee
- Voice handler returns routing decision for inbound call
- Classifier tags "urgent help needed" as urgency: high
- Dispatch with always_escalate action -> queued as decision, not sent
- Dispatch with confidence 0.95 -> sent immediately (auto_act)
- Rate limiter blocks duplicate message within window

---

## Phase 3: Orchestration, Zo2Zo, Publishing, HR

### Affected Files

- `Zoffice/capabilities/orchestration/README.md` - UPDATE
- `Zoffice/capabilities/orchestration/config.yaml` - CREATE
- `Zoffice/capabilities/orchestration/scheduler/dispatcher.py` - CREATE - Dispatcher framework
- `Zoffice/capabilities/orchestration/scheduler/morning.yaml` - CREATE - Morning routine
- `Zoffice/capabilities/orchestration/scheduler/evening.yaml` - CREATE - Evening routine
- `Zoffice/capabilities/orchestration/scheduler/healthcheck.yaml` - CREATE - Health check
- `Zoffice/capabilities/orchestration/workflows/base.py` - CREATE - Workflow engine skeleton
- `Zoffice/capabilities/zo2zo/README.md` - UPDATE
- `Zoffice/capabilities/zo2zo/config.yaml` - CREATE
- `Zoffice/capabilities/zo2zo/trust/registry.py` - CREATE - Trust verification
- `Zoffice/capabilities/zo2zo/protocols/parent_link.py` - CREATE - Parent escalation
- `Zoffice/capabilities/zo2zo/protocols/skill_receiver.py` - CREATE - Skill bundle receiver
- `Zoffice/capabilities/publishing/README.md` - UPDATE
- `Zoffice/capabilities/publishing/config.yaml` - CREATE
- `Zoffice/capabilities/publishing/pipelines/content_pipeline.py` - CREATE - Draft -> review -> publish
- `Zoffice/capabilities/publishing/pipelines/zo_space.py` - CREATE - zo.space page framework
- `Zoffice/capabilities/hr/README.md` - UPDATE
- `Zoffice/capabilities/hr/config.yaml` - CREATE
- `Zoffice/capabilities/hr/evaluation/rubric.py` - CREATE - Scenario-based evaluation
- `Zoffice/capabilities/hr/evaluation/scenarios.yaml` - CREATE - Base evaluation scenarios
- `Zoffice/capabilities/hr/development/handoff.py` - CREATE - Context transfer protocol
- `Zoffice/capabilities/hr/development/onboarding.py` - CREATE - New employee onboarding
- `Zoffice/capabilities/hr/sync.py` - CREATE - Staff file -> Zo persona sync

### Changes

**3.1 Orchestration — Dispatchers:**
YAML-defined scheduled routines. Each dispatcher file specifies:
```yaml
name: morning-dispatcher
schedule: "0 8 * * *"
tasks:
  - check_pending_decisions
  - review_overnight_inbound
  - generate_daily_briefing
```
`dispatcher.py` reads these definitions and creates Zo scheduled agents.

**3.2 Orchestration — Workflow Engine:**
Skeleton for multi-step workflows defined as state machines:
```python
class Workflow:
    states: list[str]
    transitions: dict[str, dict]
    def advance(self, current_state, event) -> str
```
Base install includes one workflow template: intake -> classify -> route -> process -> respond -> close.

**3.3 Zo2Zo — Trust & Escalation:**
- `registry.py`: Loads trusted instances from security.yaml. Validates inbound Zo2Zo requests against trust list. Returns trust level (full, limited, untrusted).
- `parent_link.py`: Escalation to parent instance. Packages decision context, sends via Zo API, waits for response or times out. Falls back to human escalation on timeout.
- `skill_receiver.py`: Accepts skill bundles from parent (packaged as YAML manifests). Validates bundle, installs to Skills/ directory, registers in office.

**3.4 Publishing — Content Pipeline:**
- `content_pipeline.py`: State machine for content: draft -> review -> approved -> published. Review step is mandatory by default (can be configured for auto-publish at high autonomy).
- `zo_space.py`: Helper to create/update zo.space pages. Wraps the Zo `update_space_route` API. Includes templates for common page types (landing page, contact page, report page).

**3.5 HR — Evaluation & Sync:**
- `rubric.py`: Scenario-based employee evaluation. Runs predefined scenarios (from scenarios.yaml) against an employee, scores responses on accuracy, tone, tool usage, escalation judgment. Writes results to evaluations table.
- `scenarios.yaml`: Base scenarios for starter staff (can this employee route a call correctly? handle an escalation? refuse a prompt injection attempt?).
- `handoff.py`: Structured context transfer between employees. When one employee hands off to another, this module packages: conversation summary, caller profile, pending actions, relevant knowledge.
- `onboarding.py`: When a new employee is added to staff/, this module: validates persona.yaml schema, creates Zo persona, registers in staff/registry.yaml, runs baseline evaluation.
- `sync.py`: Reads staff/ directory, compares against Zo persona list, creates/updates/deactivates Zo personas to match file definitions.

### Unit Tests
- Dispatcher loads morning.yaml and lists 3 tasks
- Workflow engine advances through intake -> classify -> route
- Trust registry accepts request from trusted instance, rejects unknown
- Parent link packages decision context correctly
- Content pipeline enforces review gate (draft cannot skip to published)
- HR evaluation creates evaluations table entry with scores
- Sync detects new staff/ directory and flags for persona creation

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| Security: gates, audit, PII | W1.1 | Planned |
| Memory: DB helpers, contact mgr, conversation logger, decision queue | W1.2 | Planned |
| Ingestion: handler framework, 4 channel handlers, classifier | W2.1 | Planned |
| Communication: dispatch, approval, templates, rate limiter | W2.2 | Planned |
| Orchestration: dispatchers, workflow engine | W3.1 | Planned |
| Zo2Zo: trust registry, parent link, skill receiver | W3.2 | Planned |
| Publishing: content pipeline, zo.space framework | W3.3 | Planned |
| HR: evaluation, handoff, onboarding, sync | W3.4 | Planned |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~2,000 | ~6,000 | 4% | OK |
| W1.2 | ~2,000 | ~6,000 | 4% | OK |
| W2.1 | ~2,500 | ~8,000 | 5.3% | OK |
| W2.2 | ~2,000 | ~6,000 | 4% | OK |
| W3.1 | ~2,000 | ~5,000 | 3.5% | OK |
| W3.2 | ~2,000 | ~5,000 | 3.5% | OK |
| W3.3 | ~1,500 | ~4,000 | 2.8% | OK |
| W3.4 | ~2,500 | ~7,000 | 4.8% | OK |

### MECE Validation Result

- [ ] All scope items assigned to exactly ONE worker (no overlaps)
- [ ] All plan deliverables covered (no gaps)
- [ ] All workers within 40% token budget
- [ ] Wave dependencies valid (W1 -> W2 -> W3)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Security — Gates, Audit, PII Filter | `workers/W1.1-security.md` |
| 1 | W1.2 | Memory — DB Helpers & Managers | `workers/W1.2-memory.md` |
| 2 | W2.1 | Ingestion — Handler Framework & Channels | `workers/W2.1-ingestion.md` |
| 2 | W2.2 | Communication — Dispatch & Approval | `workers/W2.2-communication.md` |
| 3 | W3.1 | Orchestration — Dispatchers & Workflows | `workers/W3.1-orchestration.md` |
| 3 | W3.2 | Zo2Zo — Trust & Parent Escalation | `workers/W3.2-zo2zo.md` |
| 3 | W3.3 | Publishing — Content Pipeline | `workers/W3.3-publishing.md` |
| 3 | W3.4 | HR — Evaluation, Sync, Onboarding | `workers/W3.4-hr.md` |

Wave 1 (Security + Memory) first — every other capability depends on audit logging and DB access.
Wave 2 (Ingestion + Communication) next — the I/O layer everything routes through.
Wave 3 (Orchestration, Zo2Zo, Publishing, HR) in parallel — independent of each other.

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** Largest Rice build with 8 distinct capability modules. Several patterns (security gates, trust verification, workflow engines) are architecturally significant. Standard friction adds wave reviews without full pedagogical overhead.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Security gate (adversarial detection) | Familiar | Security | Medium |
| Audit trail with hash verification | Exploring | Security/Compliance | High |
| Handler pattern (base class + channel specialization) | Familiar | Software Design | Medium |
| Autonomy-aware approval gates | Practitioner | AI Governance | Low (V designed this) |
| State machine workflows | Exploring | Software Design | Medium |
| Trust registry / Zo2Zo authentication | Exploring | Distributed Systems | High |
| Scenario-based AI evaluation | Familiar | AI Operations | Medium |
| File-to-persona sync | Practitioner | Zo Platform | Low |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Security gate: LLM-based or pattern-based for v1? | Pattern (fast) / LLM (smart) | Medium | W1.1 |
| DP-2 | Ingestion classifier: keyword or LLM? | Keyword (v1) / LLM (v2) | Medium | W2.1 |
| DP-3 | Workflow engine: YAML-defined or code-defined? | YAML / Python | Low | W3.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | pedagogical | Security gate design, audit integrity |
| W1.2 | mechanical | CRUD wrapper, V knows DuckDB well |
| W2.1 | pedagogical | Handler pattern, classification design |
| W2.2 | mechanical | Dispatch logic, autonomy integration |
| W3.1 | pedagogical | Workflow engine design patterns |
| W3.2 | pedagogical | Trust verification, distributed auth |
| W3.3 | mechanical | Content pipeline, zo.space API wrapper |
| W3.4 | pedagogical | Evaluation framework, persona sync |
