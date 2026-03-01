---
created: 2026-02-21
last_edited: 2026-02-21
version: 1
provenance: con_MeSXGFyaIZ55GjbZ
---
# N5OS-Rice Architecture Brief — The Troika Model

**Purpose:** Canonical definition of the Troika Architecture that underpins the Zoffice product.
**Audience:** All Rice stream builds, future Zoffice implementers, V for review.
**SSOT for:** Troika tiers, layer model, terminology, "what carries over" mapping.

---

## 1. The Core Insight

> "The same pattern applies at every level: the office has its version, AND each individual employee gets their own version of the full stack."

N5OS on va is a powerful personal operating system. But it's a single-tenant system — everything is V's. The Troika Architecture transforms this into a **replicable product** by recognizing that the system is actually three nested abstractions, each with the same structural pattern.

---

## 2. The Troika: Three Tiers

```
┌─────────────────────────────────────────────┐
│                  THE OFFICE                  │
│  (The whole Zo instance as a unified entity) │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  EMPLOYEE A  │  │  EMPLOYEE B  │  ...    │
│  │             │  │             │          │
│  │  ┌────────┐ │  │  ┌────────┐ │          │
│  │  │ Cap. 1 │ │  │  │ Cap. 2 │ │          │
│  │  │ Cap. 3 │ │  │  │ Cap. 4 │ │          │
│  │  └────────┘ │  │  └────────┘ │          │
│  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────┘
```

### Tier 1: The Office

The office is the entire Zo Computer instance viewed as a single entity — a virtual business with identity, policies, memory, and staff.

| Aspect | What It Means | Zo Primitive |
|--------|---------------|-------------|
| **Identity** | Who is this office? Name, handle, owner, domain | `Zoffice/config/office.yaml` + MANIFEST.json |
| **Policy** | What are the rules? Autonomy thresholds, security posture | `Zoffice/config/autonomy.yaml`, `security.yaml` |
| **Memory** | What does the office remember? Contacts, conversations, decisions | `Zoffice/data/office.db` (DuckDB) |
| **Staff Directory** | Who works here? | `Zoffice/staff/registry.yaml` |
| **Capabilities** | What can this office do? | `Zoffice/config/capabilities.yaml` |
| **Routing** | How does work flow to the right person? | `Zoffice/config/routing.yaml` |
| **Audit Trail** | What happened and when? | `office.db` audit table with hash verification |

**Office = N5 prefs at the organizational level.**

### Tier 2: The Employee

An employee is a Zo persona with its own complete stack — identity, knowledge, tools, and behavioral rules. Employees are defined as files on disk and synced to Zo personas at runtime.

| Aspect | What It Means | Zo Primitive |
|--------|---------------|-------------|
| **Identity (SOUL)** | Who am I? Role, personality, voice | `staff/<name>/persona.yaml` → Zo persona |
| **Knowledge (MEMORY)** | What do I know? Domain expertise, reference docs | `staff/<name>/knowledge/` directory |
| **Behavior (PREFS)** | How do I operate? System prompt, protocols | `staff/<name>/system-prompt.md` → persona prompt |
| **Tools (CAPABILITIES)** | What can I use? Which office capabilities | `staff/<name>/tools/manifest.yaml` |
| **Evaluation (HEARTBEAT)** | How am I doing? Performance assessment | HR capability → `evaluations` table |

**Employee = A fully self-contained AI agent with bounded authority.**

### Tier 3: The Capability

A capability is an infrastructure module that provides a specific function to the office. Employees USE capabilities; they don't own them. Capabilities are shared office plumbing.

| Aspect | What It Means | Zo Primitive |
|--------|---------------|-------------|
| **Function** | What does this do? | Python modules in `capabilities/<name>/` |
| **Configuration** | How is it tuned? | `capabilities/<name>/config.yaml` |
| **Interface** | How do employees call it? | Documented API in `capabilities/<name>/README.md` |
| **Audit** | Does it log its actions? | All capabilities write to the shared audit table |

**Capability = Office infrastructure that any authorized employee can call.**

---

## 3. The Fractal Pattern

V's insight is that the **same structural pattern** repeats at each tier:

| Component | Office Version | Employee Version |
|-----------|---------------|-----------------|
| **SOUL** (identity) | `office.yaml` — who is this office | `persona.yaml` — who is this employee |
| **MEMORY** (knowledge) | `office.db` — organizational memory | `knowledge/` — employee-specific knowledge |
| **PREFS** (behavior) | `autonomy.yaml` + `security.yaml` — office policies | `system-prompt.md` — employee behavior rules |
| **HEARTBEAT** (lifecycle) | Morning/evening dispatchers — office rhythm | Evaluation cycle — employee assessment |
| **CAPABILITIES** (tools) | `capabilities.yaml` — what the office can do | `tools/manifest.yaml` — what this employee can use |
| **ROUTING** (flow) | `routing.yaml` — how work reaches employees | Escalation rules in system prompt — how this employee routes internally |

This is not metaphor — it's the actual file structure. The office literally has a `persona.yaml` equivalent (office.yaml), and each employee literally has their own version.

---

## 4. The Layered Product Model

The Zoffice is built in layers, each adding to the previous:

### Layer 0: n5os-bootstrap (The Operating System)

**What it is:** A raw Zo Computer with the N5 operational machinery installed — prefs, scripts, config, and the behavioral infrastructure that makes Zo useful.

**What's included:**
- N5/prefs/ (37 architectural principles, 27 operational protocols)
- N5/scripts/ (669+ automation scripts)
- N5/config/ (port registry, anchors, canonical locations)
- CLAUDE.md (system prompt for the Zo instance)
- Skills/ (deployed automation workflows)

**Who has it:** va (V's primary Zo). Partially replicated on zoputer via teaching protocol.

**Maturity:** Production. va has been running on Layer 0 since October 2025.

### Layer 1: Zoffice Base Install (The Product)

**What it is:** The office skeleton, config schemas, database, 8 capabilities, 3 starter employees, routing, and a unified installer. This is what Rice builds.

**What's included:**
- `Zoffice/` directory tree (the entire office structure)
- 5 config YAML files (office, autonomy, capabilities, routing, security)
- `office.db` DuckDB with 5 tables (audit, contacts, decisions, conversations, evaluations)
- 8 capability modules (Security, Memory, Ingestion, Communication, Orchestration, Zo2Zo, Publishing, HR)
- 3 starter employees (Receptionist, Chief of Staff, Librarian)
- Routing resolver and CLAUDE.md generator
- Installer skill (`Skills/zoffice-setup/`)

**Who has it:** Nobody yet. Rice builds this.

**Maturity:** Planned. Architecture defined (this document), implementation planned (rice-core through rice-integration).

### Layer 2: Instance Customization (The Deployment)

**What it is:** Per-client configuration that turns the generic Zoffice into a specific business. Branded employees, custom knowledge, domain capabilities.

**What's included (examples from va):**
- Branded employees: Zozie (career coach hotline), Zoren (vibe thinker hotline), Zoseph (general operations)
- Custom knowledge: Careerspan pipeline docs, V's CRM, position system
- Domain capabilities: Resume intelligence, hiring POV generation, meeting processing
- Custom routing: Careerspan email tags, VAPI hotline integration

**Who has it:** va has Layer 2 elements, but they're not organized as Zoffice yet — they're scattered across the N5OS flat structure.

**Maturity:** Exists in fragments. Rice doesn't build Layer 2 — it creates the Layer 1 foundation that Layer 2 customizes.

---

## 5. What Carries Over (va → Zoffice Mapping)

This table maps what exists on va today to its Zoffice equivalent. This is NOT a copy operation — it's a principled adaptation. The va version is V-specific; the Zoffice version is generic.

| va Concept | va Implementation | Zoffice Equivalent | Notes |
|-----------|-------------------|-------------------|-------|
| **Personas** | 13 Zo personas (Operator, Builder, Architect, etc.) | `Zoffice/staff/` file-based employees | va personas are V-specific. Zoffice has generic starter staff. |
| **Persona routing** | Rules in persona_routing_contract.md | `Zoffice/config/routing.yaml` + resolver | Same concept, different implementation (YAML patterns vs. rule-based). |
| **N5 prefs** | 37 principles in N5/prefs/ | `Zoffice/config/autonomy.yaml` + `security.yaml` | Prefs are V's governance. Autonomy.yaml is the generic equivalent. |
| **SOUL.md** | `Zo/SOUL.md` — Zo's identity anchor | `Zoffice/config/office.yaml` + per-employee `persona.yaml` | Office has identity; each employee has identity. |
| **Scheduled agents** | 17 Zo agents (dispatchers, health checks, syncs) | Orchestration capability (`capabilities/orchestration/`) | va agents are V-specific. Orchestration provides the framework. |
| **N5/scripts/** | 669+ Python scripts | Capability handler scripts | Scripts become capability implementations. |
| **Content Library** | `Knowledge/content-library/` | Publishing capability + `Zoffice/knowledge/` | Content management becomes a formal capability. |
| **CRM** | `Personal/Knowledge/CRM/` + n5_core.db | Memory capability + `office.db` contacts table | CRM becomes memory infrastructure. |
| **Meeting processing** | Inbox → Personal/Meetings/ pipeline | Ingestion capability (meeting handler) | Meeting intake becomes a channel in ingestion. |
| **Voice hotlines** | VAPI webhooks (Zozie, Zoren) | Ingestion capability (voice handler) + Layer 2 employee | Hotline architecture carries over; branding is Layer 2. |
| **Email integration** | Gmail app tools + tag routing | Ingestion capability (email handler) | Email routing by tags carries over directly. |
| **Zo2Zo communication** | Teaching protocol + zoputer_client.py | Zo2Zo capability | Parent-child trust model carries over. |
| **Audit/logging** | N5/logs/ + various .jsonl files | Security capability (audit writer) + `office.db` audit table | Scattered logging becomes centralized audit with hash verification. |
| **Decision queue** | B03_DECISIONS.md + ad-hoc patterns | Memory capability (decision queue) + `office.db` decisions table | Informal patterns become structured infrastructure. |

---

## 6. Key Architectural Decisions (ALL FINAL)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Troika model (Office → Employee → Capability)** | Mirrors V's insight about fractal patterns. Clean separation of concerns. |
| D2 | **File-based employee definitions, Zo personas as runtime sync** | Files are version-controllable, diffable, and portable. Personas are runtime. |
| D3 | **Single DuckDB for all office data** | Simple, embedded, no external dependencies. Good enough for single-instance. |
| D4 | **8 capabilities, not fewer** | Each maps to a distinct office function. Merging (e.g., Ingestion+Communication) would complect (P32). |
| D5 | **3 starter employees (Receptionist, Chief of Staff, Librarian)** | Minimum viable office. Covers: front door, operations, knowledge. |
| D6 | **4-tier autonomy model** | Graduated trust: auto_act → act_and_notify → escalate_to_parent → escalate_to_human. |
| D7 | **Security capability cannot be disabled** | Non-negotiable. Audit trail and adversarial detection are always on. |
| D8 | **Layer 0/1/2 separation** | Clean product boundaries. Layer 0 = OS. Layer 1 = product. Layer 2 = customization. |
| D9 | **Generic starter staff, branded staff is Layer 2** | Product should be useful out of the box, but personality is per-deployment. |
| D10 | **YAML config over code config** | Human-readable, LLM-readable, consistent with N5OS patterns. |

---

## 7. Glossary

| Term | Definition |
|------|-----------|
| **Troika** | The 3-tier architecture model: Office → Employee → Capability |
| **Office** | A complete Zo Computer instance operating as a virtual business |
| **Employee** | A Zo persona with its own identity, knowledge, tools, and behavioral rules |
| **Capability** | An infrastructure module that provides a specific function (shared plumbing) |
| **Layer 0** | n5os-bootstrap — the raw operating system machinery |
| **Layer 1** | Zoffice base install — the product skeleton Rice builds |
| **Layer 2** | Instance customization — per-client branding, knowledge, capabilities |
| **Autonomy threshold** | Confidence score that determines whether an employee can act independently |
| **Fractal stack** | The repeating pattern where Office and Employee both have SOUL/MEMORY/PREFS/HEARTBEAT/CAPABILITIES |
| **Dark Factory** | An office running with zero human intervention (aspirational goal, not Rice scope) |
| **Rice** | The build program that creates Layer 1 (named for the Japanese concept of polishing/refining) |
| **Routing** | The system that maps inbound messages to the right employee |
| **Zo2Zo** | Communication between Zo Computer instances (parent ↔ child) |

---

## 8. Principles Applied

| Principle | How It Applies |
|-----------|---------------|
| **P02 (SSOT)** | This document is the single source for Troika architecture. Stream 2-4 plans reference, don't duplicate. |
| **P05 (Anti-Overwrite)** | Employee definitions are files on disk — version-controllable, diffable. |
| **P08 (Minimal Context)** | Each employee's system-prompt.md is self-contained. No loading 37 prefs. |
| **P16 (Accuracy)** | "What Carries Over" table is based on actual workspace audit, not aspiration. |
| **P20 (Modular Components)** | Capabilities are independent modules. Employees compose them via manifests. |
| **P32 (Simple Over Easy)** | 8 distinct capabilities > 4 overloaded ones. More concepts, less complecting. |
| **P35 (Version, Don't Overwrite)** | MANIFEST.json tracks versions. Config changes are versioned. |
| **P36 (Make State Visible)** | registry.yaml, capabilities.yaml, and office.db make all state inspectable. |
| **P38 (Isolate by Default)** | Employees don't share state except through capability interfaces. |
| **P39 (Audit Everything)** | Every capability writes to the audit table. Hash verification for tamper detection. |
