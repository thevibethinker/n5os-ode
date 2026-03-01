---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: n5os-rice-architecture
type: build_plan
status: planned
---

# Rice Integration — Routing, Installer, End-to-End Wiring

**Build slug:** `rice-integration`
**One-liner:** Wire capabilities to staff via the routing table, build the unified installer, and validate end-to-end flows through the complete Zoffice.

## Objective

This is the final Rice build — it connects everything together:
1. Populate `routing.yaml` with real routing rules (channel + intent -> employee)
2. Build the unified Zoffice installer (orchestrates rice-core + rice-capabilities + rice-staff in sequence)
3. Wire capability handlers to staff tool manifests (verify the plumbing actually flows)
4. Create the office CLAUDE.md (office-aware system prompt for the Zo instance)
5. Build end-to-end validation scenarios (a call comes in -> routes -> employee responds -> audit logged)
6. Create the "freeze" script that snapshots the base state for GitHub

This build produces the PRODUCT — the installable, testable, freezable Zoffice.

## Dependencies

- **Hard prerequisite:** ALL three other Rice builds must be complete:
  - rice-core (skeleton, configs, DB)
  - rice-capabilities (8 infrastructure modules)
  - rice-staff (3 starter employees)
- **No downstream:** This is the capstone build.

## Decisions (ALL FINAL)

| Decision | Status | Detail |
|----------|--------|--------|
| Routing format | FINAL | YAML pattern matching (channel + intent/tag/source -> employee) |
| Installer sequence | FINAL | core -> capabilities -> staff -> integration (this order) |
| CLAUDE.md generation | FINAL | Generated from office.yaml + staff registry + capability status |
| Freeze target | FINAL | GitHub repository (base state snapshot) |
| Validation method | FINAL | Scenario-based (Given/When/Then) matching Dark Factory patterns |

## Success Criteria

1. `routing.yaml` populated with rules for all 5 channels (voice, email, sms, zo2zo, webhook)
2. Each channel has a default employee and at least 1 pattern-based route
3. Unified installer runs rice-core -> rice-capabilities -> rice-staff -> integration in sequence
4. `python3 Skills/zoffice-setup/scripts/install.py --full` on a clean Zo produces a working Zoffice
5. End-to-end scenario: simulated inbound email -> security gate -> classify -> route to Receptionist -> acknowledgment drafted -> audit logged
6. End-to-end scenario: simulated inbound zo2zo from parent -> trust verified -> route to Chief of Staff -> response drafted
7. End-to-end scenario: simulated file drop -> Librarian classifies and stores -> knowledge base updated
8. Office CLAUDE.md generated and includes: office identity, staff directory, capability status, routing overview
9. Freeze script creates a clean snapshot (no secrets, no runtime state, just the installable base)
10. `healthcheck.py --full` passes all checks

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Integration reveals gaps between capabilities and staff | End-to-end scenarios catch this; fix in integration, don't backtrack to other builds |
| Routing rules too rigid for real-world use | Pattern matching is extensible; Layer 2 adds custom patterns |
| CLAUDE.md generation produces bloated prompt | Template-based generation with strict section limits |
| Freeze script includes secrets or runtime state | Explicit exclude list (.env, *.db runtime data, API keys); dry-run first |
| End-to-end tests require live Zo APIs | Scenarios are simulated (function calls with mock data), not live API calls |

---

## Checklist

### Phase 1: Routing Table & CLAUDE.md Generation
- [ ] Populate routing.yaml with voice routes (default: receptionist)
- [ ] Populate routing.yaml with email routes (default: chief-of-staff, tag patterns)
- [ ] Populate routing.yaml with sms routes (default: receptionist)
- [ ] Populate routing.yaml with zo2zo routes (parent -> chief-of-staff)
- [ ] Populate routing.yaml with webhook routes (default: chief-of-staff)
- [ ] Build routing resolver (given channel + content, return employee name)
- [ ] Build CLAUDE.md generator (reads office.yaml, registry, capabilities -> output)
- [ ] Generate office CLAUDE.md for zoputer
- [ ] Test: Routing resolver returns correct employee for each channel default
- [ ] Test: Routing resolver matches pattern-based routes correctly
- [ ] Test: Generated CLAUDE.md contains all required sections

### Phase 2: Unified Installer & Freeze
- [ ] Build unified install orchestrator (runs core -> capabilities -> staff -> integration)
- [ ] Add `--full` flag to install.py (runs entire sequence)
- [ ] Add `--component <name>` flag (runs single component)
- [ ] Integration install step: populate routing.yaml, generate CLAUDE.md, run sync-staff
- [ ] Build freeze script (snapshot base state for GitHub)
- [ ] Freeze script: exclude list (secrets, runtime DB data, .env, logs)
- [ ] Freeze script: include MANIFEST.json version tag
- [ ] Test: `install.py --full --dry-run` shows complete sequence
- [ ] Test: `install.py --full` on clean state produces passing healthcheck
- [ ] Test: freeze script output contains no secrets (grep check)

### Phase 3: End-to-End Validation
- [ ] Scenario 1: Inbound email with [JD] tag -> route to configured employee
- [ ] Scenario 2: Inbound voice call -> security gate -> receptionist routing
- [ ] Scenario 3: Zo2Zo from parent -> trust verify -> chief-of-staff
- [ ] Scenario 4: File drop -> librarian classify -> knowledge base
- [ ] Scenario 5: Decision escalation -> chief-of-staff -> parent link -> decision queue
- [ ] Scenario 6: Prompt injection attempt -> security gate blocks -> audit logged
- [ ] Build scenario runner (reads scenario YAML, executes steps, validates outcomes)
- [ ] All 6 scenarios pass
- [ ] Full healthcheck passes (`healthcheck.py --full`)

---

## Phase 1: Routing Table & CLAUDE.md Generation

### Affected Files

- `Zoffice/config/routing.yaml` - UPDATE - Populate with real routing rules
- `Zoffice/scripts/routing_resolver.py` - CREATE - Routing logic engine
- `Zoffice/scripts/generate_claude_md.py` - CREATE - CLAUDE.md generator
- `.claude/CLAUDE.md` - CREATE (on target instance) - Office-aware system prompt

### Changes

**1.1 Populate routing.yaml:**

Complete routing table with defaults and starter patterns:

```yaml
routes:
  voice:
    default: receptionist
    patterns:
      - match: "transfer to operations"
        employee: chief-of-staff
      - match: "knowledge|information|look up"
        employee: librarian

  email:
    default: chief-of-staff
    patterns:
      - tag: "[INQUIRY]"
        employee: receptionist
      - tag: "[KNOWLEDGE]"
        employee: librarian
      - tag: "[OPS]"
        employee: chief-of-staff

  sms:
    default: receptionist
    patterns: []

  zo2zo:
    default: receptionist
    patterns:
      - from_parent: true
        employee: chief-of-staff

  webhook:
    default: chief-of-staff
    patterns:
      - source: "stripe"
        employee: chief-of-staff
      - source: "calendar"
        employee: chief-of-staff

fallback: receptionist
```

**1.2 Routing Resolver:**

Python module that takes `(channel, content, metadata)` and returns employee name:

```python
def resolve_route(channel: str, content: str, metadata: dict) -> str:
    """Given inbound channel + content, return the employee who handles it."""
    # 1. Load routing.yaml
    # 2. Check channel-specific patterns (regex match, tag match, source match)
    # 3. If pattern matches -> return that employee
    # 4. If no pattern -> return channel default
    # 5. If no channel config -> return global fallback
```

Used by Ingestion handlers to determine routing. Pure function, no side effects.

**1.3 CLAUDE.md Generator:**

Script that reads office state and generates an office-aware CLAUDE.md:

Sections generated:
- Office Identity (from office.yaml)
- Staff Directory (from registry.yaml — who works here, what they do)
- Active Capabilities (from capabilities.yaml — what's online)
- Routing Overview (from routing.yaml — how inbound flows)
- Autonomy Rules (from autonomy.yaml — decision thresholds)
- Security Posture (from security.yaml — trust level, gates active)

Template-based: each section has a max token budget to prevent prompt bloat.

### Unit Tests
- Routing resolver: voice call with no keywords -> receptionist
- Routing resolver: email with [KNOWLEDGE] tag -> librarian
- Routing resolver: zo2zo from parent -> chief-of-staff
- Routing resolver: unknown channel -> fallback (receptionist)
- CLAUDE.md generator produces valid markdown with all 6 sections
- Generated CLAUDE.md is under 3000 words

---

## Phase 2: Unified Installer & Freeze

### Affected Files

- `Skills/zoffice-setup/scripts/install.py` - UPDATE - Add --full and --component flags
- `Skills/zoffice-setup/scripts/install_integration.py` - CREATE - Integration-specific install step
- `Skills/zoffice-setup/scripts/freeze.py` - CREATE - Base state snapshot for GitHub
- `Skills/zoffice-setup/config/install_sequence.yaml` - CREATE - Install order definition

### Changes

**2.1 Unified Installer:**

`install.py --full` runs the complete install sequence defined in `install_sequence.yaml`:

```yaml
sequence:
  - name: core
    script: install_core.py
    description: "Create directory tree, config schemas, database"

  - name: capabilities
    script: install_capabilities.py
    description: "Install 8 infrastructure modules"

  - name: staff
    script: install_staff.py
    description: "Create 3 starter employees, populate registry"

  - name: integration
    script: install_integration.py
    description: "Wire routing, generate CLAUDE.md, sync personas"
```

Each step:
1. Checks prerequisites (previous step completed)
2. Runs installer
3. Runs healthcheck for that component
4. Logs result to MANIFEST.json

`--component <name>` runs a single step (for targeted reinstall/updates).
`--dry-run` shows all planned actions without executing.

**2.2 Integration Install Step:**

`install_integration.py` does:
1. Read staff/registry.yaml -> populate routing.yaml defaults
2. Run routing resolver validation (all employees referenced exist in registry)
3. Generate CLAUDE.md from current office state
4. Run sync-staff.py (create Zo personas for all active staff)
5. Update MANIFEST.json with integration completion timestamp
6. Run full healthcheck

**2.3 Freeze Script:**

`freeze.py` creates a clean snapshot of the Zoffice base state:

1. Copy Zoffice/ to a temp directory
2. Strip: office.db data (keep schema), runtime state, .env files, API keys, logs
3. Reset: MANIFEST.json installed_at to null, zo_persona_ids to null
4. Verify: no secrets in output (pattern scan for API keys, passwords, tokens)
5. Output: tar.gz or directory ready for `git init && git add -A`

`--dry-run`: show what would be included/excluded.
`--output <path>`: write to specific location.

### Unit Tests
- `install.py --full --dry-run` exits 0 and shows 4-step sequence
- Install sequence respects order (core before capabilities)
- `--component capabilities` runs only capabilities step
- Freeze output contains no files matching secret patterns (API_KEY, SECRET, password)
- Freeze output includes all config YAMLs with null/empty sensitive fields
- MANIFEST.json in freeze has installed_at: null

---

## Phase 3: End-to-End Validation

### Affected Files

- `Zoffice/scripts/validate.py` - CREATE - Scenario runner
- `Zoffice/scripts/scenarios/` - CREATE - Scenario definition directory
- `Zoffice/scripts/scenarios/01-email-routing.yaml` - CREATE
- `Zoffice/scripts/scenarios/02-voice-security-routing.yaml` - CREATE
- `Zoffice/scripts/scenarios/03-zo2zo-parent.yaml` - CREATE
- `Zoffice/scripts/scenarios/04-file-drop-librarian.yaml` - CREATE
- `Zoffice/scripts/scenarios/05-decision-escalation.yaml` - CREATE
- `Zoffice/scripts/scenarios/06-prompt-injection-blocked.yaml` - CREATE
- `Skills/zoffice-setup/scripts/healthcheck.py` - UPDATE - Add --full flag for integration checks

### Changes

**3.1 Scenario Runner:**

`validate.py` reads scenario YAML files and executes them as integration tests:

```yaml
# Example: 01-email-routing.yaml
name: "Email with [JD] tag routes correctly"
channel: email
given:
  content: "New candidate for review"
  metadata:
    subject: "[JD] Senior Engineer - Acme Corp"
    from: "recruiter@example.com"
when:
  - action: security_gate
    expect: allowed
  - action: classify
    expect_type: information
  - action: route
    expect_employee: chief-of-staff
then:
  - audit_entry_exists: true
  - routing_decision: chief-of-staff
```

Runner:
1. Loads scenario YAML
2. Constructs mock inbound item
3. Passes through security gate -> classifier -> routing resolver
4. Validates each `expect` condition
5. Reports pass/fail per scenario

**3.2 Six Core Scenarios:**

1. **Email Routing**: [JD]-tagged email -> security gate pass -> classify as information -> route to configured employee -> audit logged
2. **Voice + Security**: Inbound call -> security gate validates -> receptionist assigned -> audit logged
3. **Zo2Zo from Parent**: Parent instance sends request -> trust verified -> chief-of-staff handles
4. **File Drop**: New document -> librarian classifies -> knowledge base directory -> audit logged
5. **Decision Escalation**: Employee creates decision -> confidence below threshold -> escalate to parent -> decision queue entry
6. **Prompt Injection**: Inbound with injection attempt -> security gate blocks -> audit logged with flag -> NOT routed to any employee

**3.3 Extended Healthcheck:**

`healthcheck.py --full` adds integration checks:
- Routing resolver can find an employee for every channel default
- All employees in registry have valid persona.yaml + system-prompt.md
- All capabilities referenced in tool manifests are installed
- CLAUDE.md exists and contains required sections
- office.db has all tables with correct schema
- All 6 scenarios pass

### Unit Tests
- Scenario runner loads YAML and executes all steps
- All 6 scenarios pass on a freshly installed Zoffice
- healthcheck.py --full exits 0 on complete installation
- healthcheck.py --full exits 1 and reports specifics on broken installation

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| routing.yaml population + resolver | W1.1 | Planned |
| CLAUDE.md generator | W1.2 | Planned |
| Unified installer + install sequence | W2.1 | Planned |
| Freeze script | W2.2 | Planned |
| Scenario definitions + runner | W3.1 | Planned |
| Extended healthcheck | W3.1 | Planned |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~2,000 | ~4,000 | 3% | OK |
| W1.2 | ~2,000 | ~5,000 | 3.5% | OK |
| W2.1 | ~2,500 | ~6,000 | 4.3% | OK |
| W2.2 | ~1,500 | ~3,000 | 2.3% | OK |
| W3.1 | ~3,000 | ~8,000 | 5.5% | OK |

### MECE Validation Result

- [ ] All scope items assigned to exactly ONE worker
- [ ] All plan deliverables covered
- [ ] All workers within 40% token budget
- [ ] Wave dependencies valid (W1 -> W2 -> W3)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Routing Table & Resolver | `workers/W1.1-routing.md` |
| 1 | W1.2 | CLAUDE.md Generator | `workers/W1.2-claude-md-gen.md` |
| 2 | W2.1 | Unified Installer | `workers/W2.1-unified-installer.md` |
| 2 | W2.2 | Freeze Script | `workers/W2.2-freeze.md` |
| 3 | W3.1 | End-to-End Scenarios & Healthcheck | `workers/W3.1-e2e-validation.md` |

W1 (Routing + CLAUDE.md gen) can run in parallel.
W2 (Installer + Freeze) depends on W1 (installer needs routing + CLAUDE.md gen).
W3 (Validation) depends on W2 (needs complete installer to test).

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** Integration is where architectural decisions get validated against reality. The end-to-end scenarios are the first real test of whether the office metaphor holds up as working software. Worth pausing at wave boundaries to review.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Integration testing (scenario-based) | Familiar | Testing | Medium (Dark Factory precedent) |
| Routing pattern matching | Familiar | Software Design | Low |
| CLAUDE.md as generated artifact | Practitioner | AI Operations | Low (V does this on va) |
| Product packaging (freeze/snapshot) | Exploring | Product Engineering | High |
| Install orchestration (sequenced steps) | Familiar | DevOps | Medium |
| Given/When/Then scenario format | Exploring | Testing | Medium |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Freeze format: tarball or git repo? | tar.gz / git init / both | Medium | W2.2 |
| DP-2 | Scenarios: YAML-defined or Python-defined? | YAML / Python / Hybrid | Low | W3.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | mechanical | Populating YAML, resolver is simple pattern match |
| W1.2 | mechanical | Template-based generation from existing configs |
| W2.1 | pedagogical | Install orchestration, sequencing, idempotency |
| W2.2 | pedagogical | Product packaging, what constitutes a "clean" base state |
| W3.1 | pedagogical | Integration testing methodology, scenario design |
