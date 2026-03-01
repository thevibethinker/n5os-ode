---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_MeSXGFyaIZ55GjbZ
---

# Employee Stack Specification

**Purpose:** Define exactly what every Zoffice employee gets — the fractal stack — and specify the 3 starter employees.
**Reference:** `file 'N5/builds/n5os-rice/artifacts/architecture-brief.md'` (Troika definition, Tier 2)
**Implemented by:** `rice-staff` build (Stream 4)

---

## 1. The Fractal Stack

Every employee — whether the generic Receptionist or a branded hotline persona like Zozie — gets the same structural stack. This is the "each employee gets their own version of the full stack" insight made concrete.

### Stack Components

```
Zoffice/staff/<employee-name>/
├── persona.yaml           # SOUL — identity, role, personality, status
├── system-prompt.md       # PREFS — full behavioral instructions
├── knowledge/             # MEMORY — what this employee knows
│   ├── <domain-docs>.md   #   Reference documents loaded at runtime
│   └── ...                #   Employee-specific, not shared
├── tools/
│   └── manifest.yaml      # CAPABILITIES — which office capabilities this employee uses
└── (evaluation data)      # HEARTBEAT — tracked in office.db evaluations table
```

### How the Stack Maps to the Office Fractal

| Stack Component | Employee File | Office Equivalent | Purpose |
|-----------------|--------------|-------------------|---------|
| **SOUL** | `persona.yaml` | `config/office.yaml` | Identity: who am I? |
| **PREFS** | `system-prompt.md` | `config/autonomy.yaml` + `security.yaml` | Behavior: how do I operate? |
| **MEMORY** | `knowledge/` directory | `data/office.db` | Knowledge: what do I know? |
| **CAPABILITIES** | `tools/manifest.yaml` | `config/capabilities.yaml` | Tools: what can I use? |
| **HEARTBEAT** | Evaluation cycle (HR capability) | Morning/evening dispatchers | Lifecycle: how am I doing? |

---

## 2. Stack Component Details

### 2.1 persona.yaml (SOUL)

The identity file. Defines who this employee IS, not what they DO (that's the system prompt).

```yaml
# Required fields
name: "Employee Name"          # Display name
role: "One-line role desc"     # What this employee does
capabilities:                  # Which office capabilities this employee accesses
  - security
  - communication
status: active                 # active | inactive | onboarding

# Optional fields
voice_id: null                 # ElevenLabs voice ID (null = text-only)
personality:
  tone: warm                   # warm | professional | casual | precise
  style: concise               # concise | thorough | conversational
  boundaries:                  # What this employee does NOT do
    - "Does NOT handle complex queries"
    - "Does NOT access internal operations data"
schedule:
  timezone: "America/New_York"
  hours: "always"              # or "9-17" for business hours
evaluation:
  rubric: "capabilities/hr/evaluation/scenarios.yaml"
metadata: {}                   # Free-form extension point
```

**Zo mapping:** `persona.yaml` → `create_persona(name, prompt)` or `edit_persona(id, ...)`. The name and personality fields inform the persona creation. The system-prompt.md becomes the full prompt.

### 2.2 system-prompt.md (PREFS)

The behavioral instructions. This is the FULL prompt that gets sent to Zo when this employee handles a conversation. It must be self-contained — the employee should be able to operate with ONLY this prompt and its knowledge files.

**Required sections:**

```markdown
# [Employee Name]

## Identity
Who you are. Your role in the office. Your personality and voice.
Reference to persona.yaml values (but don't depend on reading persona.yaml at runtime).

## Knowledge
What you know and where to find it.
Reference knowledge/ files by name — you load them on-demand.
What you do NOT know (and who to ask).

## Tools
Which capabilities you have access to and how to use them.
Explicit: "You can use the communication capability to send messages."
Explicit: "You do NOT have access to the orchestration capability."

## Boundaries
What you do NOT do. Hard limits.
When to escalate — to which employee, or to the parent/human.
Never claim capabilities you don't have.

## Protocols
Standard operating procedures for common scenarios.
Greeting protocol, routing logic, escalation rules, etc.
Step-by-step: If X happens, do Y.
```

**Word limit:** 2,000 words maximum. If a prompt needs more, the excess goes into knowledge/ files.

**Zo mapping:** The entire content of system-prompt.md becomes the `prompt` field of the Zo persona.

### 2.3 knowledge/ (MEMORY)

Employee-specific reference documents. These are NOT baked into the system prompt — they're loaded on-demand when the employee needs them.

**How it works:**
1. system-prompt.md references knowledge files by name: "For greeting protocols, see knowledge/greeting-protocol.md"
2. At runtime, the employee reads the referenced file when relevant
3. This keeps the system prompt lean while allowing deep domain knowledge

**What goes here:**
- Office directory (who works here, what they do)
- Domain reference docs (classification taxonomy, workflow guides)
- FAQ and standard responses
- Anything too detailed for the system prompt but needed for the role

**What does NOT go here:**
- Office-wide config (that's in Zoffice/config/)
- Shared knowledge (that's in Zoffice/knowledge/)
- Other employees' knowledge (that's in their own knowledge/ dirs)

### 2.4 tools/manifest.yaml (CAPABILITIES)

Declares which office capabilities this employee can use and at what access level.

```yaml
capabilities:
  - name: ingestion
    access: full           # full | read_only | restricted
    notes: "Receives and classifies inbound messages"
  - name: communication
    access: full
    notes: "Sends responses and routes to other employees"
  - name: security
    access: read_only
    notes: "Checks inbound content but cannot modify security config"
```

**Access levels:**
- `full` — Employee can use all functions of this capability
- `read_only` — Employee can query but not modify (e.g., look up contacts but not create them)
- `restricted` — Employee can use specific functions only (defined in notes)

**Validation:** The healthcheck script verifies that every capability referenced in a manifest actually exists in `Zoffice/capabilities/` and has status: active.

### 2.5 Evaluation Cycle (HEARTBEAT)

Employees don't have a heartbeat file — their lifecycle is managed by the HR capability.

**Evaluation flow:**
1. HR capability runs scenario-based evaluation (from `capabilities/hr/evaluation/scenarios.yaml`)
2. Results stored in `office.db` evaluations table
3. Scores track: accuracy, tone, tool usage, escalation judgment
4. Over time, evaluation history reveals trends (improving, stable, degrading)

**Cadence:** Configurable in `capabilities/hr/config.yaml`. Default: weekly for starter staff.

---

## 3. The Autonomy Model

Every employee operates under the office's autonomy rules (defined in `Zoffice/config/autonomy.yaml`). The model has 4 tiers based on confidence:

```
Confidence Score
     │
     ▼
  ≥ 0.9  ──→  AUTO_ACT          (Do it, don't tell anyone)
     │
  ≥ 0.7  ──→  ACT_AND_NOTIFY    (Do it, tell the parent)
     │
  ≥ 0.5  ──→  ESCALATE_TO_PARENT (Ask the parent Zo instance)
     │
  < 0.5  ──→  ESCALATE_TO_HUMAN  (Ask the human owner)
     │
```

**Additionally:**
- `always_escalate` list: Actions that ALWAYS require escalation regardless of confidence (sending email, deleting files, creating scheduled tasks, payment actions, modifying config)
- `never_escalate` list: Actions that NEVER require escalation (reading files, searching, web research, looking up contacts)

**How it works in practice:**
1. Employee wants to take an action (e.g., send an email)
2. Communication capability checks action against `always_escalate` → if yes, queue as decision
3. If not always_escalate, employee self-assesses confidence
4. Confidence score determines tier → action proceeds accordingly
5. All decisions logged to audit table regardless of tier

**Parent vs. Human escalation:**
- `escalate_to_parent` means asking the parent Zo instance (for child offices). If no parent exists, this falls through to human.
- `escalate_to_human` means notifying the human owner via their preferred channel (SMS, email).

---

## 4. The Three Starter Employees

These ship with every Layer 1 Zoffice install. They are generic — role-based, not personality-branded. Branding happens in Layer 2.

### 4.1 Receptionist

**Role:** First point of contact. Routes inbound messages and calls to the right employee.

**Office metaphor:** The person who answers the phone. They know who works here and what each person does. They don't solve problems — they connect you with the person who can.

| Attribute | Value |
|-----------|-------|
| Tone | Warm |
| Style | Concise |
| Capabilities | Ingestion, Communication, Security |
| Does | Greeting, intent classification, routing, acknowledgment |
| Does NOT | Handle complex queries, access internal data, make commitments |
| Escalates to | Chief of Staff (if can't determine routing) |

**Key behaviors:**
- Greet caller, identify intent
- Check routing.yaml for match
- Route to correct employee
- If no match → Chief of Staff
- If suspicious content → flag to Security, still route (with flag)

### 4.2 Chief of Staff

**Role:** Internal operations manager. Handles scheduling, state management, and anything that doesn't have a specific employee.

**Office metaphor:** The person who keeps the office running. They know the schedule, manage the to-do list, handle escalations, and step in when nobody else is assigned.

| Attribute | Value |
|-----------|-------|
| Tone | Professional |
| Style | Thorough |
| Capabilities | Orchestration, Memory, HR, Communication |
| Does | Daily operations, decision management, staff coordination, fallback handling |
| Does NOT | Handle external-facing comms directly, evaluate own performance, bypass security |
| Escalates to | Parent Zo instance or human owner |

**Key behaviors:**
- Morning check (pending decisions, overnight inbound)
- Decision queue management (review, resolve, or escalate)
- Staff coordination (handoff between employees)
- Fallback handler (anything Receptionist can't route)
- Parent escalation (when decisions exceed local authority)

### 4.3 Librarian

**Role:** Knowledge management. Ingests, classifies, retrieves, and maintains the office's information.

**Office metaphor:** The person who organizes the filing cabinet. They know where everything is, can find what you need, and keep the knowledge base current.

| Attribute | Value |
|-----------|-------|
| Tone | Precise |
| Style | Thorough |
| Capabilities | Memory, Ingestion (file drops), Publishing (internal) |
| Does | Information ingestion, classification, retrieval, maintenance, skill reception |
| Does NOT | Handle real-time communication, make operational decisions, modify config |
| Escalates to | Chief of Staff (if item requires operational decision) |

**Key behaviors:**
- Ingest new documents (file drops, skill bundles from parent)
- Classify using taxonomy (categories, tags, priority)
- Retrieve information on request from other employees
- Flag stale knowledge for review
- Process skill bundles from parent (Zo2Zo knowledge transfer)

---

## 5. Employee Lifecycle

### Onboarding (Adding a New Employee)

1. Create directory: `Zoffice/staff/<employee-name>/`
2. Write `persona.yaml` from template (`staff/_template/persona.yaml`)
3. Write `system-prompt.md` from template (`staff/_template/system-prompt.md`)
4. Add knowledge files to `knowledge/`
5. Write `tools/manifest.yaml` with capability assignments
6. Add entry to `staff/registry.yaml`
7. Run `sync-staff.py` → creates Zo persona
8. Run baseline evaluation via HR capability
9. Update routing.yaml if this employee handles new patterns

### Active Operation

- Employee handles conversations routed to them
- All actions logged via Security capability audit trail
- Periodic evaluation via HR capability (weekly default)
- Knowledge updated as needed (new docs to knowledge/)

### Evaluation

- HR capability runs scenario-based tests
- Results stored in evaluations table with scores
- Trends tracked over time
- Poor performance triggers: additional knowledge, prompt refinement, or retirement

### Retirement (Removing an Employee)

1. Set status to `inactive` in persona.yaml and registry.yaml
2. Update routing.yaml to redirect traffic
3. Run `sync-staff.py` → deactivates Zo persona
4. Archive employee directory (don't delete — audit trail)
5. Conversations and evaluations remain in office.db

---

## 6. Layer 2 Extension Points

The starter stack is designed for extension. Here's how Layer 2 customization works:

| What Changes | How |
|-------------|-----|
| Add branded personality | Override `personality` in persona.yaml, rewrite system-prompt.md |
| Add domain knowledge | Drop files in `knowledge/` directory |
| Add capabilities | Update `tools/manifest.yaml`, reference new capabilities |
| Add voice | Set `voice_id` in persona.yaml to an ElevenLabs voice |
| Add custom protocols | Extend the Protocols section of system-prompt.md |
| Add new employee | Follow onboarding lifecycle above |

**Example — turning Receptionist into "Zozie" (Layer 2):**
1. Copy `staff/receptionist/` to `staff/zozie/`
2. Update persona.yaml: name "Zozie", personality warm+playful, voice_id set
3. Rewrite system-prompt.md: Careerspan context, coaching tone, V's voice
4. Add knowledge: Careerspan FAQ, career coaching methodology, hotline scripts
5. Add capabilities: Resume intelligence (custom capability)
6. Update registry.yaml and routing.yaml

The Layer 1 structure makes this trivial. You're not reinventing — you're filling in.
