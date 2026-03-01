---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: n5os-rice-architecture
type: build_plan
status: complete
---

# Rice Core — Zoffice Skeleton, Config Schemas & Database

**Build slug:** `rice-core`
**One-liner:** Create the Zoffice/ directory structure, config schemas, DuckDB schema, and zoffice-setup installer — the skeleton that everything else builds on.

## Objective

Build the foundational layer of the Zoffice product (Layer 1). This creates:
1. The complete `Zoffice/` directory tree on zoputer
2. All 5 config YAML files with validated schemas (office.yaml, autonomy.yaml, capabilities.yaml, routing.yaml, security.yaml)
3. The office.db DuckDB database with 5 core tables (audit, contacts, decisions, conversations, evaluations)
4. MANIFEST.json for office identity/versioning
5. The `zoffice-setup` installer skill (the equivalent of n5os-bootstrap but for Layer 1)
6. Utility scripts: setup.py, healthcheck.py, rotate-keys.py, export-audit.py

This build creates NO capabilities, NO staff, NO routing logic — just the empty, well-structured office with plumbing ready to receive those components from the other Rice builds.

## Dependencies

- **Prerequisite:** Layer 0 (n5os-bootstrap) must be installed on target instance
- **Downstream:** rice-capabilities, rice-staff, and rice-integration all depend on this build completing first
- **No dependency on:** Any existing va infrastructure. This is greenfield on zoputer.

## Decisions (ALL FINAL)

| Decision | Status | Detail |
|----------|--------|--------|
| Top-level dir | FINAL | `Zoffice/` at `/home/workspace/Zoffice/` |
| Config format | FINAL | YAML for all config (consistent with N5OS) |
| Database | FINAL | Single DuckDB (`Zoffice/data/office.db`) |
| Installer location | FINAL | `Skills/zoffice-setup/` (mirrors n5os-bootstrap pattern) |
| Staff source of truth | FINAL | File-based definitions; Zo personas are runtime sync targets |
| Directory structure | FINAL | As specified in zoffice-architecture-v1.md |

## Success Criteria

1. `Zoffice/` directory tree matches architecture spec exactly (all dirs exist, READMEs in place)
2. All 5 config YAML files are syntactically valid and contain sensible defaults
3. `office.db` is created with all 5 tables, schema matches spec, indexes present
4. MANIFEST.json accurately describes the install
5. `python3 Skills/zoffice-setup/scripts/install.py --dry-run` succeeds
6. `python3 Skills/zoffice-setup/scripts/healthcheck.py` reports all green
7. Running install.py on a clean Zo creates the full skeleton idempotently (run twice = same result)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Directory naming collision with existing Zo structure | `Zoffice/` is unique, won't collide with N5/, Personal/, Sites/, Skills/ |
| Config schemas too rigid for future needs | All YAML files include extensible `metadata` or `custom` fields |
| DuckDB file locking in multi-process | Single writer pattern; reads are concurrent-safe |
| Install script idempotency bugs | healthcheck.py validates post-install state; install uses CREATE IF NOT EXISTS |
| Schema migration as product evolves | MANIFEST.json tracks version; future builds add migration scripts |

---

## Checklist

### Phase 1: Directory Skeleton & Config Schemas
- [x] Create full Zoffice/ directory tree (all dirs, READMEs)
- [x] Write office.yaml with zoputer defaults
- [x] Write autonomy.yaml with 4-tier thresholds
- [x] Write capabilities.yaml with all 8 capabilities (status: pending until rice-capabilities installs them)
- [x] Write routing.yaml with empty route table (populated by rice-integration)
- [x] Write security.yaml with strict defaults
- [x] Write MANIFEST.json
- [x] Test: All files parse cleanly (`python3 -c "import yaml; yaml.safe_load(open('...'))"`)

### Phase 2: Database Schema
- [x] Create office.db with DuckDB
- [x] Define audit table with hash verification
- [x] Define contacts table with profile JSON
- [x] Define decisions table with status workflow
- [x] Define conversations table with channel tracking
- [x] Define evaluations table with scenario scores
- [x] Add indexes on timestamp, employee, channel, status
- [x] Test: Insert sample row in each table, verify schema

### Phase 3: Installer Skill & Utility Scripts
- [x] Create Skills/zoffice-setup/ with SKILL.md
- [x] Write scripts/install.py (creates skeleton, configs, DB)
- [x] Write scripts/healthcheck.py (validates all components)
- [x] Write Zoffice/scripts/setup.py (first-run customization)
- [x] Write Zoffice/scripts/export-audit.py (audit trail export)
- [x] Write Zoffice/scripts/rotate-keys.py (placeholder for key rotation)
- [x] Support --dry-run on install.py
- [x] Test: install.py --dry-run shows planned actions without side-effects
- [x] Test: install.py creates everything; healthcheck.py passes

---

## Phase 1: Directory Skeleton & Config Schemas

### Affected Files

- `Zoffice/` - CREATE - Root directory for the entire office
- `Zoffice/MANIFEST.json` - CREATE - Office identity, version, install metadata
- `Zoffice/config/office.yaml` - CREATE - Office identity config
- `Zoffice/config/autonomy.yaml` - CREATE - Decision threshold config
- `Zoffice/config/capabilities.yaml` - CREATE - Active capabilities config
- `Zoffice/config/routing.yaml` - CREATE - Channel→employee routing config
- `Zoffice/config/security.yaml` - CREATE - Security and trust config
- `Zoffice/capabilities/` - CREATE - Directory tree for all 8 capabilities (empty, populated by rice-capabilities)
- `Zoffice/staff/` - CREATE - Directory tree for staff (empty, populated by rice-staff)
- `Zoffice/staff/registry.yaml` - CREATE - Empty staff registry
- `Zoffice/data/` - CREATE - Data directory with subdirs
- `Zoffice/knowledge/` - CREATE - Knowledge base directory tree
- `Zoffice/scripts/` - CREATE - Utility scripts directory

### Changes

**1.1 Create Directory Tree:**

The full Zoffice/ directory tree as specified in architecture doc:
```
Zoffice/
├── config/
├── capabilities/
│   ├── ingestion/
│   │   ├── handlers/
│   │   └── README.md
│   ├── communication/
│   │   ├── channels/
│   │   ├── templates/
│   │   └── README.md
│   ├── publishing/
│   │   ├── pipelines/
│   │   └── README.md
│   ├── orchestration/
│   │   ├── scheduler/
│   │   ├── workflows/
│   │   └── README.md
│   ├── zo2zo/
│   │   ├── trust/
│   │   ├── protocols/
│   │   └── README.md
│   ├── security/
│   │   ├── gates/
│   │   ├── audit/
│   │   └── README.md
│   ├── hr/
│   │   ├── evaluation/
│   │   ├── development/
│   │   └── README.md
│   └── memory/
│       └── README.md
├── staff/
│   ├── registry.yaml
│   ├── receptionist/
│   │   ├── knowledge/
│   │   └── tools/
│   ├── chief-of-staff/
│   │   ├── knowledge/
│   │   └── tools/
│   └── librarian/
│       ├── knowledge/
│       └── tools/
├── data/
│   ├── contacts/
│   ├── conversations/
│   └── decisions/
├── knowledge/
│   ├── about-owner/
│   ├── products/
│   ├── clients/
│   └── domain/
└── scripts/
```

Each capability README.md contains a brief description of the capability, its status (pending), and what rice-capabilities will install there.

**1.2 Write MANIFEST.json:**

```json
{
  "product": "Zoffice",
  "version": "1.0.0",
  "layer": 1,
  "requires_layer_0": "n5os-bootstrap >= 1.0",
  "installed_at": null,
  "installed_by": null,
  "instance": {
    "name": null,
    "handle": null,
    "owner": null,
    "parent": null
  },
  "capabilities_installed": [],
  "staff_installed": [],
  "schema_version": "1.0"
}
```

Populated at install time by install.py using values from office.yaml.

**1.3 Write office.yaml:**

```yaml
# Zoffice Identity Configuration
# This file defines WHO this office is.

office:
  name: "Zoffice"               # Display name (customized at install)
  handle: null                   # zo.computer handle (set at install)
  owner: null                    # Owner name (set at install)
  domain: null                   # Primary domain (optional)
  parent: null                   # Parent Zo instance (e.g., va.zo.computer)
  version: "1.0.0"
  installed_at: null             # ISO timestamp, set by installer

# Extend with custom fields as needed
custom: {}
```

**1.4 Write autonomy.yaml:**

```yaml
# Zoffice Autonomy Configuration
# Controls decision-making thresholds for all employees.

thresholds:
  auto_act: 0.9            # Above: act without notification
  act_and_notify: 0.7      # Between: act but notify parent
  escalate_to_parent: 0.5  # Between: ask parent AI
  escalate_to_human: 0.3   # Below: ask human owner

# Actions that ALWAYS require escalation regardless of confidence
always_escalate:
  - send_email
  - delete_file
  - create_scheduled_task
  - register_service
  - payment_action
  - modify_config

# Actions that NEVER require escalation
never_escalate:
  - read_file
  - search
  - web_research
  - list_files
  - lookup_contact

custom: {}
```

**1.5 Write capabilities.yaml:**

```yaml
# Zoffice Capabilities Configuration
# Tracks which capabilities are installed and active.
# Status values: active, pending, disabled

capabilities:
  ingestion:
    status: pending
    channels: []
  communication:
    status: pending
    channels: []
  publishing:
    status: pending
    platforms: []
  orchestration:
    status: pending
    dispatchers: []
  zo2zo:
    status: pending
    parent: null
  security:
    status: pending    # Activated by rice-capabilities (cannot be disabled once active)
    level: strict
  hr:
    status: pending
    evaluation_cadence: weekly
  memory:
    status: pending
    db: Zoffice/data/office.db

custom: {}
```

**1.6 Write routing.yaml:**

```yaml
# Zoffice Routing Configuration
# Maps inbound channels + intent patterns to employees.
# Populated by rice-integration build.

routes:
  voice:
    default: receptionist
    patterns: []
  email:
    default: chief-of-staff
    patterns: []
  sms:
    default: receptionist
    patterns: []
  zo2zo:
    default: receptionist
    patterns: []
  webhook:
    default: chief-of-staff
    patterns: []

# Fallback when no pattern matches and default employee is unavailable
fallback: receptionist

custom: {}
```

**1.7 Write security.yaml:**

```yaml
# Zoffice Security Configuration
# Controls security gates, trust, and audit behavior.

security:
  level: strict   # strict | standard | permissive

  gates:
    inbound:
      enabled: true
      adversarial_detection: true
      pii_filter: true
    outbound:
      enabled: true
      content_review: true

  trust:
    # Trusted Zo instances (can make authenticated requests)
    trusted_instances: []
    # Trusted domains (inbound email/webhook)
    trusted_domains: []

  audit:
    enabled: true
    retention_days: 365
    hash_verification: true

  api_keys:
    # Reference to env vars, never store actual keys here
    parent_key_env: null
    zo2zo_key_env: null

custom: {}
```

### Unit Tests
- All YAML files load without errors: `python3 -c "import yaml; yaml.safe_load(open('Zoffice/config/office.yaml'))"`
- MANIFEST.json is valid JSON
- All directories exist per spec
- staff/registry.yaml is valid YAML (empty list)

---

## Phase 2: Database Schema

### Affected Files
- `Zoffice/data/office.db` - CREATE - Central DuckDB database

### Changes

**2.1 Create office.db with all 5 tables:**

```sql
-- Core audit trail — immutable record of every office action
CREATE TABLE IF NOT EXISTS audit (
  id VARCHAR PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  capability VARCHAR NOT NULL,
  employee VARCHAR,
  action VARCHAR NOT NULL,
  channel VARCHAR,
  counterparty VARCHAR,
  content_hash VARCHAR,
  metadata JSON,
  parent_event_id VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_employee ON audit(employee);
CREATE INDEX IF NOT EXISTS idx_audit_capability ON audit(capability);
CREATE INDEX IF NOT EXISTS idx_audit_channel ON audit(channel);

-- Contact registry — CRM-like storage
CREATE TABLE IF NOT EXISTS contacts (
  id VARCHAR PRIMARY KEY,
  name VARCHAR,
  email VARCHAR,
  phone VARCHAR,
  organization VARCHAR,
  relationship VARCHAR,
  first_contact TIMESTAMP,
  last_contact TIMESTAMP,
  interaction_count INTEGER DEFAULT 0,
  profile JSON,
  tags VARCHAR[]
);

CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_relationship ON contacts(relationship);

-- Decision queue — pending/resolved decision tracking
CREATE TABLE IF NOT EXISTS decisions (
  id VARCHAR PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  origin_employee VARCHAR,
  summary TEXT NOT NULL,
  full_context JSON,
  options JSON,
  recommendation VARCHAR,
  status VARCHAR DEFAULT 'pending',
  resolved_at TIMESTAMP,
  resolution TEXT,
  resolved_by VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at);

-- Conversation log — every interaction tracked
CREATE TABLE IF NOT EXISTS conversations (
  id VARCHAR PRIMARY KEY,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  channel VARCHAR,
  employee VARCHAR,
  counterparty_id VARCHAR,
  summary TEXT,
  duration_seconds INTEGER,
  satisfaction DOUBLE,
  metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel);
CREATE INDEX IF NOT EXISTS idx_conversations_employee ON conversations(employee);
CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at);

-- Staff performance evaluations
CREATE TABLE IF NOT EXISTS evaluations (
  id VARCHAR PRIMARY KEY,
  employee VARCHAR NOT NULL,
  evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  scenario_scores JSON,
  overall_score DOUBLE,
  strengths TEXT,
  improvements TEXT,
  evaluator VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_evaluations_employee ON evaluations(employee);
CREATE INDEX IF NOT EXISTS idx_evaluations_date ON evaluations(evaluated_at);
```

**2.2 Validation:**
After creation, run a schema check that verifies all 5 tables exist with expected columns and indexes.

### Unit Tests
- `duckdb.connect('Zoffice/data/office.db').execute("SELECT table_name FROM information_schema.tables")` returns 5 tables
- INSERT + SELECT on each table succeeds
- Indexes exist (query information_schema)

---

## Phase 3: Installer Skill & Utility Scripts

### Affected Files
- `Skills/zoffice-setup/SKILL.md` - CREATE - Skill documentation
- `Skills/zoffice-setup/scripts/install.py` - CREATE - Main installer
- `Skills/zoffice-setup/scripts/healthcheck.py` - CREATE - Health validator
- `Skills/zoffice-setup/config/defaults.yaml` - CREATE - Default values for fresh install
- `Zoffice/scripts/setup.py` - CREATE - First-run customization wizard
- `Zoffice/scripts/export-audit.py` - CREATE - Audit trail export utility
- `Zoffice/scripts/rotate-keys.py` - CREATE - Key rotation placeholder

### Changes

**3.1 Create Skills/zoffice-setup/SKILL.md:**

Mirrors the n5os-bootstrap SKILL.md pattern:
- What: Installs the Zoffice (Layer 1) on a Zo Computer
- How: `python3 Skills/zoffice-setup/scripts/install.py --config <config.yaml>`
- Requires: Layer 0 (n5os-bootstrap) already installed
- Supports: `--dry-run` for preview mode

**3.2 Create scripts/install.py:**

The installer does (in order):
1. Verify Layer 0 is present (check for N5/prefs/ existence)
2. Read config file (or use defaults.yaml)
3. Create Zoffice/ directory tree
4. Write config YAML files with values from config
5. Write MANIFEST.json
6. Create office.db with schema
7. Write staff/registry.yaml (empty)
8. Create capability README.md files
9. Run healthcheck

All operations are idempotent (mkdir -p, CREATE IF NOT EXISTS, etc.).
`--dry-run` mode prints every action without executing.

**3.3 Create scripts/healthcheck.py:**

Checks:
- Zoffice/ directory tree completeness
- All 5 config YAML files parse cleanly
- MANIFEST.json is valid
- office.db exists and has all 5 tables
- staff/registry.yaml exists
- Reports pass/fail with specific details

**3.4 Create defaults.yaml:**

```yaml
# Default configuration for a fresh Zoffice install
# Override by passing --config <your-config.yaml>

office:
  name: "My Zoffice"
  owner: null      # MUST be set at install time
  parent: null     # Optional: parent Zo instance

autonomy:
  preset: supervised  # supervised | autonomous | custom
  # supervised = escalate_to_human: 0.5, escalate_to_parent: 0.7
  # autonomous = escalate_to_human: 0.3, auto_act: 0.7

security:
  level: strict

capabilities:
  # All 8 activated by default; rice-capabilities populates handlers
  activate_all: true
```

**3.5 Utility Scripts:**

- `setup.py` — Interactive first-run: prompts for office name, owner, parent instance, domain. Writes values into office.yaml and MANIFEST.json. Intended for the "clean install" user path.
- `export-audit.py` — Exports audit table to CSV/JSON for compliance reporting. Supports `--format csv|json`, `--since <date>`, `--employee <name>`.
- `rotate-keys.py` — Placeholder that reads security.yaml, lists key env vars, and prints rotation instructions. Actual rotation is manual (deliberate safety choice per P05).

### Unit Tests
- `install.py --dry-run` exits 0 and prints planned actions
- `install.py` creates full skeleton; `healthcheck.py` exits 0
- Running `install.py` twice produces identical state (idempotent)
- `healthcheck.py` on empty dir exits 1 with clear error messages
- `export-audit.py --format json` on empty DB returns empty array (no crash)

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| Zoffice/ directory tree | W1.1 | Planned |
| Config YAML schemas (5 files) | W1.1 | Planned |
| MANIFEST.json | W1.1 | Planned |
| office.db schema (5 tables) | W1.2 | Planned |
| Skills/zoffice-setup/ | W2.1 | Planned |
| install.py + healthcheck.py | W2.1 | Planned |
| Utility scripts (setup, export, rotate) | W2.1 | Planned |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~2,500 | ~5,000 | 3.8% | OK |
| W1.2 | ~1,500 | ~3,000 | 2.3% | OK |
| W2.1 | ~3,000 | ~8,000 | 5.5% | OK |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (W2 depends on W1)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Directory Skeleton & Config Schemas | `workers/W1.1-skeleton-configs.md` |
| 1 | W1.2 | DuckDB Schema | `workers/W1.2-database-schema.md` |
| 2 | W2.1 | Installer Skill & Utility Scripts | `workers/W2.1-installer-utilities.md` |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** minimal
**Rationale:** This is foundational scaffolding — directory creation, config files, DB schema. The concepts (YAML config, DuckDB, installer scripts) are well within V's working vocabulary. No novel architectural decisions remain.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| DuckDB schema design | Practitioner | Data | Low (V uses DuckDB daily) |
| YAML config schemas | Practitioner | Config | Low (standard pattern) |
| Idempotent installers | Familiar | DevOps | Medium (good pattern to internalize) |
| Product packaging | Exploring | Product | Medium (thinking in "installable" terms) |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Include schema migration support in v1? | Yes (versioned) / No (manual) | Low | W1.2 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | mechanical | Directory creation and config file writing |
| W1.2 | mechanical | SQL DDL, straightforward schema |
| W2.1 | pedagogical | Installer design patterns, idempotency |
