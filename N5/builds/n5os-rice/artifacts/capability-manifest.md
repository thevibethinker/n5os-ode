---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_MeSXGFyaIZ55GjbZ
---

# Capability Infrastructure Manifest

**Purpose:** Define the 8 capability infrastructure layers, map them to Zo primitives, audit current maturity, and identify gaps.
**Reference:** `file 'N5/builds/n5os-rice/artifacts/architecture-brief.md'` (Troika definition, Tier 3)
**Implemented by:** `rice-capabilities` build (Stream 3)

---

## Overview

Capabilities are the shared infrastructure modules of a Zoffice. They are the office plumbing — employees use them, but no single employee owns them. Each capability is a self-contained unit in `Zoffice/capabilities/<name>/` with its own config, handlers, and API surface.

**The 8 Capabilities:**

| # | Capability | Office Metaphor | One-Liner |
|---|-----------|----------------|-----------|
| 1 | **Security** | The locks, cameras, and guard at the door | Validates inbound content, filters PII, logs everything |
| 2 | **Memory** | The filing cabinet and Rolodex | Stores and retrieves contacts, conversations, decisions |
| 3 | **Ingestion** | The mailroom | Receives and classifies inbound from all channels |
| 4 | **Communication** | The phone system and outbox | Sends messages, manages approval gates, templates |
| 5 | **Orchestration** | The daily schedule and workflow clipboard | Dispatches recurring tasks, manages multi-step workflows |
| 6 | **Zo2Zo** | The interoffice mail and parent company hotline | Communicates with other Zo instances (parent, children) |
| 7 | **Publishing** | The print shop and website | Manages content pipelines and public-facing pages |
| 8 | **HR** | The personnel office | Evaluates employees, manages onboarding and handoffs |

**Architectural rule:** Capabilities are independent. They communicate through defined interfaces, not direct imports. All capabilities write to the shared audit table.

---

## Capability 1: Security

> The locks, cameras, and guard at the door.

### Definition

Security is the **always-on** capability that protects the office. It validates every piece of inbound content, detects adversarial attempts, filters PII, and maintains an immutable audit trail. Security cannot be disabled once installed (architectural decision D7).

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| Rules (conditional) | Could map security policies to Zo rules |
| DuckDB | `office.db` audit table — immutable event log |
| Python scripts | Inbound gate, PII filter, audit writer |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Audit logging | **Partial** — scattered across multiple .jsonl files and DuckDB tables | `N5/logs/`, `N5/data/` various |
| Adversarial detection | **Partial** — rule-based detection in some persona prompts | Persona system prompts |
| PII filtering | **None** — no centralized PII detection | - |
| Hash verification | **None** — no tamper detection on audit entries | - |
| Content classification | **Partial** — ad-hoc in persona routing and email rules | Rules, persona prompts |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| Audit logging | **Minimal** — basic zo-to-zo communication log | `Documents/System/zo-to-zo-communication-log.jsonl` |
| Content sanitization | **Partial** — sanitizer layer for inbound content from clients | `Integrations/zoputer-sync/sanitizer.py` |
| Everything else | **None** | - |

### Known Gaps

1. **No centralized audit trail** — va has 669+ scripts but audit logging is per-script, not centralized
2. **No hash verification** — existing logs can be modified without detection
3. **No PII filter** — PII can flow through the system undetected
4. **No inbound gate** — adversarial detection is persona-by-persona, not centralized
5. **zoputer sanitizer exists but is narrow** — only covers zo-to-zo, not all inbound

### Target State (Layer 1)

- Centralized inbound gate (adversarial detection + PII filter)
- Immutable audit table in office.db with SHA-256 hash verification
- Configurable sensitivity via `security/config.yaml`
- All other capabilities write to audit via Security's logging interface

---

## Capability 2: Memory

> The filing cabinet and Rolodex.

### Definition

Memory is the office's persistent storage. It provides CRUD operations for contacts, conversations, and decisions via a shared DuckDB database (`office.db`). All employees access memory through helper functions — no raw SQL outside this capability.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| DuckDB | `office.db` — 5 tables (audit, contacts, decisions, conversations, evaluations) |
| Python scripts | db_helpers.py, contact_manager.py, conversation_logger.py, decision_queue.py |
| File system | `Zoffice/knowledge/` for document-based knowledge (separate from DB) |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Contact management | **Functional** — CRM in n5_core.db `people` table | `N5/data/n5_core.db`, `Personal/Knowledge/CRM/` |
| Conversation logging | **Partial** — session context files, some meeting logs | `.claude/session-context.md`, `Personal/Meetings/` |
| Decision tracking | **Minimal** — B03_DECISIONS.md (manual markdown file) | `/home/workspace/B03_DECISIONS.md` |
| Semantic memory | **Functional** — indexed knowledge files for retrieval | `N5/cognition/`, `N5/scripts/n5_load_context.py` |
| Knowledge base | **Functional** — Content Library, Architecture docs, CRM | `Knowledge/`, `Personal/Knowledge/` |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| All components | **None** — zoputer has no structured memory system | - |

### Known Gaps

1. **CRM exists but is va-specific** — tied to V's personal contacts, not genericizable
2. **Decision queue is a markdown file** — no structured CRUD, no status tracking
3. **Conversation logging is fragmented** — session context, meeting files, export logs
4. **No unified data model** — contacts in one DB, meetings in another, decisions in a .md file
5. **Semantic memory is powerful but va-specific** — `n5_load_context.py` + pageindex work well but are hardcoded to va's workspace structure

### Target State (Layer 1)

- Single `office.db` with unified schema (5 tables)
- Python helper module for all CRUD operations
- Contact manager with lookup by phone/email/name
- Decision queue with create/resolve/expire lifecycle
- Conversation logger for all channels

---

## Capability 3: Ingestion

> The mailroom.

### Definition

Ingestion receives and classifies inbound content from all channels — email, voice, SMS, webhooks, and Zo2Zo messages. It assigns a UUID, timestamp, and classification to every piece of inbound, then routes it to the appropriate employee.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| Gmail app tools | Email ingestion (read, classify, route) |
| SMS (send_sms_to_user) | SMS channel — inbound from contacts |
| Webhooks (zo.space API routes) | VAPI voice webhooks, generic webhook receivers |
| Zo2Zo API (/zo/ask) | Authenticated inbound from trusted Zo instances |
| Zo rules | Tag-based routing conditions |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Email ingestion | **Functional** — Gmail tools + tag-based routing (JD, RESUME, UPDATE) | Rules, Careerspan skills |
| Voice ingestion | **Functional** — VAPI webhooks for Zozie and Zoren hotlines | `Skills/career-coaching-hotline/`, `Skills/zoren-hotline/` |
| SMS routing | **Functional** — n5 command routing for SMS | Rules (SMS command handler) |
| Webhook receivers | **Partial** — ad-hoc webhook handlers for various services | Various skills |
| Zo2Zo inbound | **Functional** — teaching protocol and zoputer_client.py | `Documents/System/zo-to-zo-teaching-protocol.md` |
| Content classification | **Partial** — email tags, persona routing, but no unified classifier | Scattered across rules and skills |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| Zo2Zo inbound | **Partial** — receives from va via teaching protocol | Documented in teaching protocol |
| Everything else | **None** | - |

### Known Gaps

1. **No unified handler framework** — each channel is a separate bespoke implementation
2. **No classification standard** — email uses tags, voice uses VAPI intents, SMS uses keywords
3. **No UUID/timestamp assignment** — inbound items aren't uniformly identified
4. **va ingestion works but is V-specific** — Careerspan tags, V's hotline personas
5. **No channel-agnostic abstraction** — can't add a new channel without building from scratch

### Target State (Layer 1)

- Base handler class that all channel handlers extend
- 4 channel handlers: email (tag-based), voice (VAPI), webhook (generic), Zo2Zo (authenticated)
- Unified classifier (type, urgency, topic)
- Every inbound item gets UUID, timestamp, classification, routing decision

---

## Capability 4: Communication

> The phone system and outbox.

### Definition

Communication manages all outbound from the office. When an employee wants to send a message, it goes through Communication — which selects the best channel, formats the message, and either sends immediately or queues for approval based on the autonomy model.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| send_sms_to_user | SMS outbound channel |
| send_email_to_user | Email outbound to owner |
| use_app_gmail | Email outbound on behalf of owner |
| send_telegram_message | Telegram outbound (if connected) |
| Zo personas | Employee identity determines communication style |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Email sending | **Functional** — Gmail tools, Writer persona for voice | Rules, Writer persona |
| SMS sending | **Functional** — various agents and notifications | Scheduled agents, rules |
| Approval gates | **Partial** — rules require consent for emails, but no formal gate | Rules ("never send without authorization") |
| Templates | **None** — each communication is composed ad-hoc | - |
| Rate limiting | **None** — no deduplication or rate limits on outbound | - |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| All components | **None** — zoputer sends via va for now | Teaching protocol |

### Known Gaps

1. **No formal approval gate** — va uses rules ("ask V first") but no structured gate
2. **No template system** — every email/SMS is composed from scratch
3. **No rate limiting or deduplication** — could theoretically send duplicate messages
4. **No multi-channel dispatch logic** — channel selection is manual or hardcoded
5. **Communication and ingestion are not symmetric** — ingestion has some structure, communication has very little

### Target State (Layer 1)

- Multi-channel dispatch (employee → channel selection)
- Autonomy-aware approval gate (checks confidence vs. thresholds)
- Markdown template system with variable substitution
- Rate limiter and deduplication
- Outbound audit logging

---

## Capability 5: Orchestration

> The daily schedule and workflow clipboard.

### Definition

Orchestration manages recurring tasks and multi-step workflows. It defines what the office does on a schedule (morning check, evening close, health check) and provides a workflow engine for multi-step processes.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| Scheduled agents (create_agent) | Dispatchers — recurring task execution |
| Zo rules | Conditional triggers for workflow steps |
| Python scripts | Dispatcher logic, workflow engine |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Morning dispatcher | **Functional** — runs data pipelines, generates briefing | Agent: Morning Operations Dispatcher |
| Evening dispatcher | **Functional** — accountability check-in | Agent: Evening Accountability Check-In |
| Health checkpoints | **Functional** — 5x daily health checks | Agent: Health Checkpoint Dispatcher |
| Weekly maintenance | **Functional** — system health, CRM enrichment, performance dash | Multiple weekly agents |
| Workflow engine | **None** — no formal multi-step workflow system | - |
| Task system | **Partial** — `Skills/task-system/` exists | `Skills/task-system/` |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| All components | **None** — zoputer has no scheduled agents | - |

### Known Gaps

1. **va has 17 scheduled agents but they're V-specific** — not generalizable dispatchers
2. **No workflow engine** — multi-step processes are scripted linearly, not as state machines
3. **Agent sprawl** — 17 agents with some overlap and some disabled
4. **No dispatcher framework** — each agent has its own instruction format
5. **No workflow recovery** — if a multi-step process fails mid-way, no checkpoint/resume

### Target State (Layer 1)

- YAML-defined dispatcher framework (scheduled routines)
- Morning, evening, and healthcheck dispatcher templates
- Workflow engine skeleton (state machine for multi-step processes)
- Creates Zo scheduled agents from YAML definitions

---

## Capability 6: Zo2Zo

> The interoffice mail and parent company hotline.

### Definition

Zo2Zo enables communication between Zo Computer instances. The parent instance can teach skills, delegate work, and escalate decisions. Child instances can report back, ask questions, and receive knowledge. Trust is verified before any exchange.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| /zo/ask API | Parent-to-child and child-to-parent communication |
| Zo access tokens | Authentication between instances |
| File system | Skill bundles, knowledge packages |

### What Exists Today (va → zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| Teaching protocol | **Functional** — structured va→zoputer teaching sessions | `Documents/System/zo-to-zo-teaching-protocol.md` |
| Trust model | **Partial** — implicit trust (va trusts zoputer, manually configured) | Teaching protocol docs |
| Skill transfer | **Partial** — base64 file transfer for deterministic installs | Teaching protocol |
| Communication logging | **Functional** — structured log of all va↔zoputer exchanges | `Documents/System/zo-to-zo-communication-log.jsonl` |
| Sanitization | **Functional** — outbound content sanitized before sending to clients | `Integrations/zoputer-sync/sanitizer.py` |
| Audit system | **Functional** — dual-sided audit for va↔zoputer | `Skills/audit-system/` |
| Parent escalation | **None** — no formal "ask my parent" protocol | - |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| Receiving from va | **Partial** — can receive teaching sessions | Teaching protocol |
| Sending to clients | **Partial** — sanitized output to client instances | Sanitizer layer |
| Trust registry | **None** — no formal list of trusted instances | - |

### Known Gaps

1. **No formal trust registry** — trust is implicit (manually configured per-session)
2. **No parent escalation protocol** — zoputer can't say "I don't know, ask va"
3. **No skill receiver** — zoputer gets skills via teaching, not via automated delivery
4. **Trust is va-specific** — no generic "verify this Zo instance is trusted" mechanism
5. **No standardized skill bundle format** — teaching protocol is conversational, not packaged

### Target State (Layer 1)

- YAML-based trust registry (loaded from security.yaml)
- Parent link protocol (child → parent escalation with context)
- Skill receiver (accept packaged skill bundles from parent)
- Inbound trust verification (validate API key + instance identity)

---

## Capability 7: Publishing

> The print shop and website.

### Definition

Publishing manages content pipelines and public-facing output. It handles the flow from draft → review → approval → publish, and provides helpers for creating zo.space pages.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| zo.space routes (update_space_route) | Public-facing pages and APIs |
| zo.space assets (update_space_asset) | Static files for pages |
| File system | Content drafts, templates |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| zo.space pages | **Functional** — multiple pages deployed | zo.space routes |
| Sites system | **Functional** — full sites hosting with staging/prod | `Sites/`, site services |
| Content library | **Functional** — curated knowledge artifacts | `Knowledge/content-library/` |
| Content ingestion | **Functional** — `content_ingest.py` for article/link intake | `N5/scripts/content_ingest.py` |
| Newsletter generation | **Functional** — FOHE newsletter build | `N5/builds/fohe-newsletter-q1-2026/` |
| Approval gate | **None** — no formal review/approve step before publishing | - |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| zo.space | **Available** — zoputer has zo.space capability | Zo platform |
| Everything else | **None** | - |

### Known Gaps

1. **No formal content pipeline** — publishing on va is ad-hoc (write it, deploy it)
2. **No approval gate** — V reviews everything manually, no structured approval flow
3. **No template system for zo.space pages** — each page is built from scratch
4. **Content library is va-specific** — not structured for office-level content management
5. **No content versioning** — published content isn't tracked as versions

### Target State (Layer 1)

- Content pipeline skeleton (draft → review → approved → published)
- zo.space page framework (landing page, contact page, report templates)
- Mandatory review gate (configurable: always-on by default)
- Integration with Security for content audit

---

## Capability 8: HR

> The personnel office.

### Definition

HR manages employee lifecycle — evaluation, onboarding, handoffs, and the file-to-persona sync. It provides the framework for assessing how well employees are performing and managing the human side of the office.

### Zo Primitives Used

| Primitive | How It's Used |
|-----------|---------------|
| Zo personas (list, create, edit) | Syncing file definitions to runtime personas |
| DuckDB | `office.db` evaluations table |
| Python scripts | Evaluation runner, sync script, handoff protocol |

### What Exists Today (va)

| Component | Status | Location |
|-----------|--------|----------|
| Persona management | **Functional** — 13 personas with routing contract | Zo personas, `Documents/System/personas/INDEX.md` |
| Persona routing | **Functional** — rule-based auto-activation | Rules, `persona_routing_contract.md` |
| Persona creation template | **Functional** — standardized template | `Documents/System/personas/persona_creation_template.md` |
| Performance evaluation | **None** — no scenario-based evaluation of persona quality | - |
| Handoff protocol | **Partial** — persona routing handles activation but no structured context transfer | Persona routing contract |
| File-to-persona sync | **None** — personas are created manually in Zo UI | - |

### What Exists Today (zoputer)

| Component | Status | Location |
|-----------|--------|----------|
| Personas | **Minimal** — basic persona setup via teaching | Teaching protocol |
| Everything else | **None** | - |

### Known Gaps

1. **No performance evaluation** — va personas aren't tested against scenarios
2. **No file-to-persona sync** — persona creation is manual (Zo UI), not file-driven
3. **No handoff protocol** — when one persona activates, no structured context transfer
4. **No onboarding protocol** — adding a new persona is ad-hoc
5. **Persona definitions are scattered** — YAML prompts in Zo platform, reference docs in Documents/System/personas/
6. **No evaluation rubric** — no standardized way to assess if a persona is performing well

### Target State (Layer 1)

- Scenario-based evaluation rubric (predefined test scenarios per employee)
- Structured handoff protocol (conversation summary, caller profile, pending actions)
- File-to-persona sync script (staff/ directory → Zo personas, idempotent)
- Onboarding protocol (validate schema, create persona, register, baseline eval)
- Staff registry sync (detect new/changed/removed employees)

---

## Maturity Summary

| Capability | va Maturity | zoputer Maturity | Biggest Gap |
|-----------|-------------|-----------------|------------|
| **Security** | Partial (scattered logging, some detection) | Minimal (sanitizer only) | No centralized audit, no PII filter |
| **Memory** | Functional (CRM, semantic memory) | None | No unified data model, manual decisions |
| **Ingestion** | Functional (email, voice, SMS, Zo2Zo) | Minimal (Zo2Zo receive) | No unified handler framework |
| **Communication** | Functional (multi-channel, Writer persona) | None | No approval gate, no templates |
| **Orchestration** | Functional (17 scheduled agents) | None | No workflow engine, agent sprawl |
| **Zo2Zo** | Functional (teaching protocol, audit) | Partial (receiving) | No trust registry, no parent escalation |
| **Publishing** | Functional (zo.space, sites, content library) | Available (zo.space) | No content pipeline, no approval gate |
| **HR** | Partial (persona mgmt, routing) | Minimal | No evaluation, no sync, no handoff |

### Key Takeaway

va has working versions of most capabilities, but they're **V-specific implementations, not generic infrastructure**. The gap is not "does this capability exist?" — it's "is this capability structured as reusable, configurable plumbing that any Zoffice can use?"

The answer is consistently: the functionality exists, but the infrastructure does not. Rice builds the infrastructure.
