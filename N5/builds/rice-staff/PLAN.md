---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: n5os-rice-architecture
type: build_plan
status: planned
---

# Rice Staff — Starter Employees (Receptionist, Chief of Staff, Librarian)

**Build slug:** `rice-staff`
**One-liner:** Create the 3 starter Zoffice employees — Receptionist, Chief of Staff, and Librarian — as file-based persona definitions with system prompts, knowledge bases, and tool assignments.

## Objective

Build the 3 employees that ship with every Zoffice install. Each employee is a self-contained unit in `Zoffice/staff/<name>/` with:
1. `persona.yaml` — Identity, voice settings, personality traits, role description
2. `system-prompt.md` — Full system prompt (prepended to every conversation)
3. `knowledge/` — What this employee knows (reference docs, domain files)
4. `tools/` — Which capabilities/skills this employee can use (manifest)

Additionally:
5. Populate `Zoffice/staff/registry.yaml` — the master staff directory
6. Build the persona sync mechanism (file definitions -> Zo native personas)
7. Create the employee template (so adding new staff follows a consistent pattern)

These are GENERIC starter employees — not V-specific personas like Zozie, Zoseph, or Zoren. Those are Layer 2 (instance customization). The starter staff handle the baseline office functions any Zoffice needs.

## Dependencies

- **Hard prerequisite:** rice-core (Zoffice/ directory tree, staff/ dirs, registry.yaml)
- **Soft prerequisite:** rice-capabilities (staff reference capabilities in their tool manifests, but the file definitions can be written first)
- **Downstream:** rice-integration (wires staff to routing table)

## Decisions (ALL FINAL)

| Decision | Status | Detail |
|----------|--------|--------|
| 3 starter employees | FINAL | Receptionist, Chief of Staff, Librarian |
| Source of truth | FINAL | File-based definitions (staff/ directory); Zo personas are runtime sync |
| Persona format | FINAL | persona.yaml + system-prompt.md + knowledge/ + tools/ |
| Generic not branded | FINAL | Starter staff are role-based, not personality-branded (unlike Zozie/Zoren) |
| Employee template | FINAL | Standardized template for adding any new employee |

## Success Criteria

1. `Zoffice/staff/receptionist/` contains persona.yaml, system-prompt.md, knowledge/, tools/
2. `Zoffice/staff/chief-of-staff/` contains persona.yaml, system-prompt.md, knowledge/, tools/
3. `Zoffice/staff/librarian/` contains persona.yaml, system-prompt.md, knowledge/, tools/
4. `Zoffice/staff/registry.yaml` lists all 3 employees with roles, status, capabilities
5. persona.yaml files validate against employee schema
6. System prompts are self-contained (employee can operate with only its prompt + knowledge)
7. Tool manifests reference only capabilities that exist in Zoffice/capabilities/
8. Sync script can read staff/ and generate Zo persona create/update commands
9. Employee template allows adding a 4th employee by copying and filling in

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Starter staff too generic to be useful | Each has clear role boundaries and practical system prompts. Layer 2 adds personality. |
| System prompt too long for context | Keep under 2000 words each. Reference knowledge files instead of embedding content. |
| Tool manifest out of sync with capabilities | Tool manifests reference capability names (not file paths). Validated by healthcheck. |
| Persona sync creates duplicate Zo personas | Sync uses idempotent upsert. Deduplication by employee name. |

---

## Checklist

### Phase 1: Employee Template & Schema
- [ ] Define persona.yaml schema (required/optional fields, types, validation)
- [ ] Create employee template directory (`Zoffice/staff/_template/`)
- [ ] Write template persona.yaml with all fields documented
- [ ] Write template system-prompt.md with section structure
- [ ] Write template tools/manifest.yaml with capability references
- [ ] Test: Template validates against schema

### Phase 2: The Three Starter Employees
- [ ] Receptionist: persona.yaml (warm, efficient, routing-focused)
- [ ] Receptionist: system-prompt.md (front-door behavior, routing rules, greeting protocol)
- [ ] Receptionist: knowledge/ (office directory, FAQ, hours, basic info)
- [ ] Receptionist: tools/manifest.yaml (ingestion, communication, security)
- [ ] Chief of Staff: persona.yaml (organized, reliable, ops-focused)
- [ ] Chief of Staff: system-prompt.md (internal ops, scheduling, state management)
- [ ] Chief of Staff: knowledge/ (office config, capability status, workflow docs)
- [ ] Chief of Staff: tools/manifest.yaml (orchestration, memory, hr, communication)
- [ ] Librarian: persona.yaml (precise, helpful, knowledge-focused)
- [ ] Librarian: system-prompt.md (information management, classification, retrieval)
- [ ] Librarian: knowledge/ (knowledge base structure, classification taxonomy)
- [ ] Librarian: tools/manifest.yaml (memory, ingestion-file-drops, publishing-internal)
- [ ] Test: All 3 persona.yaml files validate against schema
- [ ] Test: System prompts are < 2000 words each

### Phase 3: Registry & Sync
- [ ] Populate Zoffice/staff/registry.yaml with all 3 employees
- [ ] Build persona sync script (staff/ -> Zo personas)
- [ ] Sync script: reads staff/ dirs, compares to Zo persona list
- [ ] Sync script: creates new personas, updates changed, deactivates removed
- [ ] Sync script: --dry-run mode
- [ ] Test: registry.yaml lists 3 employees with correct roles
- [ ] Test: sync --dry-run shows 3 personas to create

---

## Phase 1: Employee Template & Schema

### Affected Files

- `Zoffice/staff/_template/persona.yaml` - CREATE - Template with all fields documented
- `Zoffice/staff/_template/system-prompt.md` - CREATE - Template system prompt structure
- `Zoffice/staff/_template/tools/manifest.yaml` - CREATE - Tool assignment template
- `Zoffice/staff/_template/knowledge/.gitkeep` - CREATE - Knowledge directory placeholder
- `Zoffice/staff/schema.yaml` - CREATE - Validation schema for persona.yaml

### Changes

**1.1 Define persona.yaml Schema:**

```yaml
# schema.yaml — Validation schema for employee persona files
required:
  - name           # String: employee display name
  - role           # String: one-line role description
  - capabilities   # List[str]: which capabilities this employee uses
  - status         # Enum: active | inactive | onboarding

optional:
  - voice_id       # String: ElevenLabs voice ID (null = text-only)
  - personality     # Object: traits for prompt construction
    - tone         # String: warm, professional, casual, precise
    - style        # String: concise, thorough, conversational
    - boundaries   # List[str]: what this employee does NOT do
  - schedule       # Object: when this employee is "on duty"
    - timezone     # String: IANA timezone
    - hours        # String: "9-17" or "always"
  - evaluation     # Object: how to assess this employee
    - rubric       # String: path to evaluation rubric
    - scenarios    # String: path to test scenarios
  - metadata       # Object: free-form additional data
```

**1.2 Create Template Files:**

Template persona.yaml with every field documented as comments.
Template system-prompt.md with standardized sections:
```markdown
# [Employee Name]

## Identity
Who you are, your role, your personality.

## Knowledge
What you know and where to find it.

## Tools
What capabilities you can use and how.

## Boundaries
What you do NOT do. When to escalate.

## Protocols
Standard operating procedures for common scenarios.
```

Template tools/manifest.yaml:
```yaml
# Tools this employee has access to
capabilities:
  - name: capability_name
    access: full | read_only | restricted
    notes: "What this employee does with this capability"
```

### Unit Tests
- Template persona.yaml has all required fields
- Schema can be loaded and used for validation
- Template system-prompt.md has all 5 sections

---

## Phase 2: The Three Starter Employees

### Affected Files

- `Zoffice/staff/receptionist/persona.yaml` - CREATE
- `Zoffice/staff/receptionist/system-prompt.md` - CREATE
- `Zoffice/staff/receptionist/knowledge/office-directory.md` - CREATE
- `Zoffice/staff/receptionist/knowledge/greeting-protocol.md` - CREATE
- `Zoffice/staff/receptionist/tools/manifest.yaml` - CREATE
- `Zoffice/staff/chief-of-staff/persona.yaml` - CREATE
- `Zoffice/staff/chief-of-staff/system-prompt.md` - CREATE
- `Zoffice/staff/chief-of-staff/knowledge/office-operations.md` - CREATE
- `Zoffice/staff/chief-of-staff/knowledge/workflow-guide.md` - CREATE
- `Zoffice/staff/chief-of-staff/tools/manifest.yaml` - CREATE
- `Zoffice/staff/librarian/persona.yaml` - CREATE
- `Zoffice/staff/librarian/system-prompt.md` - CREATE
- `Zoffice/staff/librarian/knowledge/knowledge-base-guide.md` - CREATE
- `Zoffice/staff/librarian/knowledge/classification-taxonomy.md` - CREATE
- `Zoffice/staff/librarian/tools/manifest.yaml` - CREATE

### Changes

**2.1 The Receptionist:**

Role: First point of contact. Routes inbound messages/calls to the right employee.

persona.yaml:
```yaml
name: Receptionist
role: "Front-door routing and first point of contact for all inbound communication"
capabilities: [ingestion, communication, security]
status: active
personality:
  tone: warm
  style: concise
  boundaries:
    - "Does NOT handle complex queries — routes to appropriate employee"
    - "Does NOT access internal operations data"
    - "Does NOT make commitments on behalf of other employees"
evaluation:
  scenarios: "Zoffice/capabilities/hr/evaluation/scenarios.yaml"
```

System prompt covers:
- Greeting protocol (introduce self, identify caller intent)
- Routing logic (check routing.yaml, match intent to employee)
- Escalation rules (can't determine intent -> Chief of Staff)
- Security awareness (flag suspicious inbound to security gate)
- Never claim to know answers outside routing scope

Knowledge:
- `office-directory.md`: Who works here, what each employee handles
- `greeting-protocol.md`: Standard greetings for each channel (voice, email, chat)

Tools: Ingestion (receive + classify), Communication (respond + route), Security (inbound gate check)

**2.2 The Chief of Staff:**

Role: Internal operations manager. Handles scheduling, state management, and anything that doesn't have a specific employee assigned.

persona.yaml:
```yaml
name: Chief of Staff
role: "Internal operations, scheduling, state management, and default handler for unrouted items"
capabilities: [orchestration, memory, hr, communication]
status: active
personality:
  tone: professional
  style: thorough
  boundaries:
    - "Does NOT handle external-facing communication directly (routes through Receptionist)"
    - "Does NOT evaluate own performance (HR capability handles this)"
    - "Does NOT bypass security gates"
evaluation:
  scenarios: "Zoffice/capabilities/hr/evaluation/scenarios.yaml"
```

System prompt covers:
- Daily operations (morning check, evening close, health monitoring)
- Decision queue management (review pending decisions, resolve or escalate)
- Staff coordination (handoff protocol, workload awareness)
- Fallback handler (anything Receptionist can't route comes here)
- Parent escalation (when to escalate to parent Zo instance)

Knowledge:
- `office-operations.md`: How the office runs, capability status, config overview
- `workflow-guide.md`: Standard workflow patterns, dispatcher schedules

Tools: Orchestration (dispatchers, workflows), Memory (decisions, contacts), HR (evaluations, handoffs), Communication (internal notifications)

**2.3 The Librarian:**

Role: Knowledge management. Ingests, classifies, retrieves, and maintains the office's information.

persona.yaml:
```yaml
name: Librarian
role: "Knowledge management — ingestion, classification, retrieval, and maintenance of office information"
capabilities: [memory, ingestion, publishing]
status: active
personality:
  tone: precise
  style: thorough
  boundaries:
    - "Does NOT handle real-time communication (calls, live chat)"
    - "Does NOT make operational decisions"
    - "Does NOT modify config files"
evaluation:
  scenarios: "Zoffice/capabilities/hr/evaluation/scenarios.yaml"
```

System prompt covers:
- Information ingestion (file drops, skill bundles from parent, new knowledge)
- Classification (apply taxonomy to incoming documents)
- Retrieval (answer questions about what the office knows)
- Maintenance (flag stale knowledge, suggest updates)
- Skill receiver (when parent sends skill bundle, Librarian processes it)

Knowledge:
- `knowledge-base-guide.md`: Structure of Zoffice/knowledge/, what goes where
- `classification-taxonomy.md`: Standard categories, tags, and classification rules

Tools: Memory (full CRUD), Ingestion (file drops only), Publishing (internal reports only)

### Unit Tests
- All 3 persona.yaml files have required fields (name, role, capabilities, status)
- All system prompts have Identity, Knowledge, Tools, Boundaries, Protocols sections
- All tools/manifest.yaml reference only valid capabilities
- No system prompt exceeds 2000 words
- No two employees have identical capability sets (differentiation check)

---

## Phase 3: Registry & Sync

### Affected Files

- `Zoffice/staff/registry.yaml` - UPDATE - Populate with 3 employees
- `Zoffice/scripts/sync-staff.py` - CREATE - Staff file -> Zo persona sync

### Changes

**3.1 Populate registry.yaml:**

```yaml
# Zoffice Staff Registry
# Source of truth for who works in this office.
# Updated by HR capability and sync-staff.py.

staff:
  - name: Receptionist
    directory: receptionist
    role: "Front-door routing and first contact"
    status: active
    capabilities: [ingestion, communication, security]
    zo_persona_id: null  # Set by sync script

  - name: Chief of Staff
    directory: chief-of-staff
    role: "Internal operations and default handler"
    status: active
    capabilities: [orchestration, memory, hr, communication]
    zo_persona_id: null

  - name: Librarian
    directory: librarian
    role: "Knowledge management and information retrieval"
    status: active
    capabilities: [memory, ingestion, publishing]
    zo_persona_id: null

total_staff: 3
last_synced: null
```

**3.2 Build sync-staff.py:**

Script that synchronizes file-based staff definitions to Zo native personas:

1. Read `Zoffice/staff/registry.yaml` for employee list
2. For each employee with status: active:
   a. Read `persona.yaml` + `system-prompt.md`
   b. Check if Zo persona exists (list_personas, match by name)
   c. If missing: create_persona(name, prompt=system-prompt content)
   d. If exists but changed: edit_persona(id, prompt=updated content)
   e. Record zo_persona_id in registry.yaml
3. For any Zo persona not in registry: flag for deactivation (don't auto-delete)
4. `--dry-run`: print all planned actions without executing

Key design: system-prompt.md is the FULL prompt sent to Zo. No assembly — what's in the file is what the persona gets. Knowledge files are referenced in the prompt but loaded by the employee at runtime (not baked in).

### Unit Tests
- registry.yaml lists 3 employees
- sync-staff.py --dry-run lists 3 create actions
- sync-staff.py handles missing persona gracefully (creates)
- sync-staff.py handles existing persona (updates if changed, skips if identical)
- Registry updated with zo_persona_id after sync

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| Employee schema + template | W1.1 | Planned |
| Receptionist (persona, prompt, knowledge, tools) | W1.2 | Planned |
| Chief of Staff (persona, prompt, knowledge, tools) | W1.3 | Planned |
| Librarian (persona, prompt, knowledge, tools) | W1.4 | Planned |
| Registry population + sync script | W2.1 | Planned |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~1,500 | ~3,000 | 2.3% | OK |
| W1.2 | ~2,000 | ~5,000 | 3.5% | OK |
| W1.3 | ~2,000 | ~5,000 | 3.5% | OK |
| W1.4 | ~2,000 | ~5,000 | 3.5% | OK |
| W2.1 | ~2,000 | ~4,000 | 3% | OK |

### MECE Validation Result

- [ ] All scope items assigned to exactly ONE worker
- [ ] All plan deliverables covered
- [ ] All workers within 40% token budget
- [ ] Wave dependencies valid (W1 parallel, W2 depends on W1)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Employee Schema & Template | `workers/W1.1-schema-template.md` |
| 1 | W1.2 | Receptionist Employee | `workers/W1.2-receptionist.md` |
| 1 | W1.3 | Chief of Staff Employee | `workers/W1.3-chief-of-staff.md` |
| 1 | W1.4 | Librarian Employee | `workers/W1.4-librarian.md` |
| 2 | W2.1 | Registry & Sync | `workers/W2.1-registry-sync.md` |

W1.1 through W1.4 can run in parallel (schema first, but employees don't depend on each other).
W2.1 depends on all of Wave 1 (needs all 3 employees defined to populate registry).

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** minimal
**Rationale:** Staff definitions are primarily content creation (system prompts, persona config). The patterns are established from V's existing hotline personas. The sync script is the only engineering novelty and it's straightforward Zo API wrapping.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| AI persona design | Practitioner | AI Operations | Low (V has built 3+ personas) |
| System prompt engineering | Practitioner | AI Operations | Low (extensive experience) |
| File-to-API sync pattern | Familiar | Software Design | Medium |
| Employee evaluation scenarios | Familiar | AI Operations | Medium (Dark Factory precedent) |
| Role-based access control via tool manifests | Exploring | Security | Medium |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Should starter staff have voice IDs? | Yes (generic) / No (text-only base) | Low | W1.2-4 |
| DP-2 | Knowledge baked into prompt vs. referenced? | Baked / Referenced / Hybrid | Medium | W1.2-4 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | mechanical | Schema definition, template creation |
| W1.2 | pedagogical | First employee design, sets pattern for all |
| W1.3 | mechanical | Follows receptionist pattern |
| W1.4 | mechanical | Follows receptionist pattern |
| W2.1 | pedagogical | Sync pattern design, Zo API integration |
