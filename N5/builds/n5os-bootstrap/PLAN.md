---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: build_plan
status: draft
---

# Plan: N5OS Bootstrap Skill

**Objective:** Create a distributable N5OS philosophy and infrastructure skill that any Zo instance can install, with personalization layer that adapts behavior per-instance.

**Trigger:** V wants to replicate N5OS thinking on zoputer and potentially other Zo instances, using the existing substrate sync infrastructure.

**Key Design Principle:** This is a "seed" skill — it unpacks into actual infrastructure, then stays resident for updates. Not just documentation, but executable philosophy.

---

## Open Questions

- [x] What's the minimum payload? → Going big: principles, safety, operations, personas, voice, state, pulse-lite
- [x] Personalization depth? → Config that changes behavior (autonomy levels, enabled personas, escalation targets)
- [x] Self-destruct? → No, stays for updates
- [x] Update mechanism? → Separate sync via `update.py`

---

## Architecture Overview

```
Skills/n5os-bootstrap/
├── SKILL.md                    # Usage instructions
├── scripts/
│   ├── install.py              # Main bootloader
│   ├── update.py               # Pull updates from substrate
│   ├── personalize.py          # Apply instance config
│   └── verify.py               # Health check installation
├── payload/
│   ├── principles/             # P0-P39 (full markdown files)
│   ├── safety/                 # safety.md, file-protection.md, dry-run protocols
│   ├── operations/             # Planning, debug, conversation lifecycle
│   ├── personas/               # Vibe persona definitions
│   ├── workflows/              # Persona workflows (debugger, strategist, etc.)
│   ├── voice/                  # Anti-patterns, style guide
│   ├── state/                  # SESSION_STATE templates
│   └── pulse-lite/             # Core pulse scripts (subset)
├── templates/
│   ├── CLAUDE.md.j2            # Instance CLAUDE.md template
│   ├── session-context.j2      # Session context template
│   └── rules.yaml.j2           # Zo rules derived from principles
└── config/
    ├── manifest.yaml           # What installs where
    ├── defaults.yaml           # Default personalization
    └── instances/
        ├── zoputer.yaml        # Zoputer-specific config
        └── example.yaml        # Template for new instances
```

**Installation destinations:**
- `N5/prefs/` — Safety, operations, system configs
- `Personal/Knowledge/Architecture/principles/` — Architectural principles
- `Documents/System/personas/` — Persona definitions
- `Skills/pulse/` — Pulse orchestration (lite version)
- `.claude/` — CLAUDE.md and session context

---

## Checklist

### Phase 1: Payload Curation (D1)
- ☐ Select and copy principles (P0-P39) to payload/principles/
- ☐ Select and copy safety protocols to payload/safety/
- ☐ Select and copy operational protocols to payload/operations/
- ☐ Select and copy persona definitions to payload/personas/
- ☐ Select and copy workflows to payload/workflows/
- ☐ Create voice anti-patterns doc for payload/voice/
- ☐ Create state templates for payload/state/
- ☐ Test: All payload files present and valid markdown

### Phase 2: Bootloader Core (D2)
- ☐ Create manifest.yaml mapping source → destination
- ☐ Implement install.py with manifest-driven unpacking
- ☐ Support --dry-run mode
- ☐ Support --force for overwrites
- ☐ Create verify.py for health checks
- ☐ Test: Dry-run shows correct file placements

### Phase 3: Personalization Engine (D3)
- ☐ Design personalization schema (autonomy, personas, escalation, voice)
- ☐ Create defaults.yaml with sensible defaults
- ☐ Create zoputer.yaml instance config
- ☐ Create example.yaml template
- ☐ Implement personalize.py for config application
- ☐ Create Jinja2 templates (CLAUDE.md.j2, session-context.j2)
- ☐ Test: Personalization correctly modifies behavior

### Phase 4: Update Mechanism (D4)
- ☐ Implement update.py that pulls from substrate
- ☐ Support selective updates (--principles, --safety, etc.)
- ☐ Preserve local customizations (don't overwrite personalization)
- ☐ Create update manifest tracking installed versions
- ☐ Test: Update pulls new content without breaking local changes

### Phase 5: Documentation & Integration (D5)
- ☐ Write comprehensive SKILL.md
- ☐ Add n5os-bootstrap to substrate-exports.yaml
- ☐ Test full install on fresh workspace (simulate zoputer)
- ☐ Test update flow
- ☐ Document personalization options

---

## Phase 1: Payload Curation

### Affected Files
- `Skills/n5os-bootstrap/payload/principles/*.md` - CREATE - Copy P0-P39 principle files
- `Skills/n5os-bootstrap/payload/safety/*.md` - CREATE - Safety protocols
- `Skills/n5os-bootstrap/payload/operations/*.md` - CREATE - Operational protocols
- `Skills/n5os-bootstrap/payload/personas/*.md` - CREATE - Persona definitions
- `Skills/n5os-bootstrap/payload/workflows/*.md` - CREATE - Persona workflows
- `Skills/n5os-bootstrap/payload/voice/anti-patterns.md` - CREATE - Voice anti-patterns
- `Skills/n5os-bootstrap/payload/state/SESSION_STATE.template.md` - CREATE - State template

### Changes

**1.1 Principles Payload:**
Copy from `Personal/Knowledge/Architecture/principles/`:
- architectural_principles.md (index)
- P24-P34 individual files
- P35-P39_building_fundamentals.md

**1.2 Safety Payload:**
Copy from `N5/prefs/system/`:
- safety.md
- file-protection.md
- folder-policy.md
- safety-rules.md

**1.3 Operations Payload:**
Copy from `N5/prefs/operations/`:
- planning_prompt.md
- conversation-end-v5.md
- conversation-initialization.md
- debug-logging-auto-behavior.md
- recipe-execution-guide.md
- scheduled-task-protocol.md

**1.4 Personas Payload:**
Copy from `Documents/System/personas/`:
- vibe_architect_persona.md
- vibe_builder_persona.md
- vibe_debugger_persona.md
- vibe_researcher_persona.md
- vibe_strategist_persona.md
- vibe_teacher_persona.md
- vibe_writer_persona.md
- INDEX.md

**1.5 Workflows Payload:**
Copy from `N5/prefs/workflows/`:
- debugger_workflow.md
- strategist_workflow.md
- teacher_workflow.md
- writer_workflow.md
- researcher_workflow.md

**1.6 Voice Payload:**
Create `anti-patterns.md` synthesizing voice guidance from:
- N5/data/voice_library.db export
- Known anti-patterns (corporate speak, filler, etc.)

**1.7 State Payload:**
Create `SESSION_STATE.template.md` from `.claude/session-context.md` pattern.

### Unit Tests
- `ls payload/principles/*.md | wc -l` should be ≥10
- `ls payload/safety/*.md | wc -l` should be ≥3
- `ls payload/personas/*.md | wc -l` should be ≥7
- All files should be valid markdown (no syntax errors)

---

## Phase 2: Bootloader Core

### Affected Files
- `Skills/n5os-bootstrap/config/manifest.yaml` - CREATE - Installation manifest
- `Skills/n5os-bootstrap/scripts/install.py` - CREATE - Main installer
- `Skills/n5os-bootstrap/scripts/verify.py` - CREATE - Health checker

### Changes

**2.1 Manifest Structure:**
```yaml
version: 1
name: n5os-bootstrap
description: N5OS philosophy and infrastructure bootstrap

destinations:
  principles:
    source: payload/principles/
    target: Personal/Knowledge/Architecture/principles/
    mode: merge  # don't delete existing
    
  safety:
    source: payload/safety/
    target: N5/prefs/system/
    mode: merge
    
  operations:
    source: payload/operations/
    target: N5/prefs/operations/
    mode: merge
    
  personas:
    source: payload/personas/
    target: Documents/System/personas/
    mode: merge
    
  workflows:
    source: payload/workflows/
    target: N5/prefs/workflows/
    mode: merge
    
  voice:
    source: payload/voice/
    target: N5/prefs/voice/
    mode: merge
    
  state:
    source: payload/state/
    target: .claude/templates/
    mode: merge

required_dirs:
  - N5/prefs/system
  - N5/prefs/operations
  - N5/prefs/workflows
  - N5/prefs/voice
  - Personal/Knowledge/Architecture/principles
  - Documents/System/personas
  - .claude/templates
```

**2.2 install.py Features:**
- Parse manifest.yaml
- Create required directories
- Copy files with conflict detection
- Apply personalization after copy
- Support `--dry-run`, `--force`, `--verbose`
- Log all actions to N5/logs/n5os-bootstrap.log

**2.3 verify.py Features:**
- Check all expected files exist
- Validate file contents (non-empty, valid markdown)
- Check personalization was applied
- Report health status

### Unit Tests
- `python3 install.py --dry-run` shows expected placements
- `python3 install.py --force` completes without error
- `python3 verify.py` returns exit code 0

---

## Phase 3: Personalization Engine

### Affected Files
- `Skills/n5os-bootstrap/config/defaults.yaml` - CREATE - Default config
- `Skills/n5os-bootstrap/config/instances/zoputer.yaml` - CREATE - Zoputer config
- `Skills/n5os-bootstrap/config/instances/example.yaml` - CREATE - Template
- `Skills/n5os-bootstrap/scripts/personalize.py` - CREATE - Personalization engine
- `Skills/n5os-bootstrap/templates/CLAUDE.md.j2` - CREATE - CLAUDE.md template
- `Skills/n5os-bootstrap/templates/session-context.j2` - CREATE - Session context template

### Changes

**3.1 Personalization Schema:**
```yaml
# defaults.yaml
instance:
  name: "{{INSTANCE_NAME}}"
  handle: "{{HANDLE}}.zo.computer"
  owner: "{{OWNER_NAME}}"
  role: general  # or consulting-partner, personal-assistant, etc.

autonomy:
  level: supervised  # autonomous | supervised | restricted
  requires_approval:
    - external_comms
    - file_deletion
    - scheduled_tasks
    - service_creation
  parent: null  # escalation target (e.g., va.zo.computer)
  
personas:
  enabled:
    - operator
    - builder
    - debugger
    - researcher
    - strategist
    - teacher
    - writer
    - architect
  disabled: []
  default: operator

voice:
  profile: professional  # professional | personal | formal
  primitives: local  # local | shared | none
  
safety:
  protection_level: strict  # strict | standard | relaxed
  dry_run_default: true
  
features:
  pulse: true
  state_tracking: true
  conversation_logging: true
```

**3.2 zoputer.yaml:**
```yaml
instance:
  name: zoputer
  handle: zoputer.zo.computer
  owner: V
  role: consulting-partner

autonomy:
  level: supervised
  requires_approval:
    - external_comms
    - file_deletion
    - scheduled_tasks
  parent: va.zo.computer

personas:
  enabled:
    - operator
    - builder
    - debugger
    - researcher
    - strategist
    - writer
    - architect
    - librarian
  disabled:
    - nutritionist
    - trainer
  default: operator

voice:
  profile: professional
  primitives: shared  # pull from va

safety:
  protection_level: strict
  dry_run_default: true
```

**3.3 Template Variables:**
Templates use Jinja2 syntax with variables from personalization config:
- `{{ instance.name }}`
- `{{ instance.owner }}`
- `{{ autonomy.level }}`
- `{{ personas.enabled | join(', ') }}`
- etc.

### Unit Tests
- `python3 personalize.py --config zoputer.yaml --dry-run` shows correct substitutions
- Generated CLAUDE.md contains zoputer-specific values
- Disabled personas not present in generated rules

---

## Phase 4: Update Mechanism

### Affected Files
- `Skills/n5os-bootstrap/scripts/update.py` - CREATE - Update script
- `Skills/n5os-bootstrap/config/installed.yaml` - CREATE (at runtime) - Installation state

### Changes

**4.1 update.py Features:**
- Pull latest payload from substrate (via git or API)
- Compare installed.yaml with new manifest
- Apply updates without overwriting local personalization
- Support selective updates: `--principles`, `--safety`, `--personas`, etc.
- Support `--dry-run`
- Log updates to N5/logs/n5os-bootstrap.log

**4.2 installed.yaml Structure:**
```yaml
installed_at: 2026-02-13T03:00:00Z
version: 1.0.0
personalization: zoputer.yaml
components:
  principles:
    version: 1.0.0
    files: [list of installed files]
  safety:
    version: 1.0.0
    files: [...]
  # etc.
```

**4.3 Update Strategy:**
- Payload files: overwrite with new versions
- Personalization files: preserve local changes
- Templates: regenerate from personalization config
- New components: install, prompt for personalization

### Unit Tests
- `python3 update.py --dry-run` shows what would change
- `python3 update.py` completes without error
- Local personalization preserved after update

---

## Phase 5: Documentation & Integration

### Affected Files
- `Skills/n5os-bootstrap/SKILL.md` - UPDATE - Full documentation
- `N5/config/substrate-exports.yaml` - UPDATE - Add n5os-bootstrap

### Changes

**5.1 SKILL.md Content:**
- Purpose and philosophy
- Quick start (install, personalize, verify)
- Personalization reference (all config options)
- Update workflow
- Troubleshooting
- Architecture overview

**5.2 Substrate Integration:**
Add to exports.yaml:
```yaml
exports:
  skills:
    # ... existing ...
    - n5os-bootstrap
```

### Unit Tests
- Fresh workspace install completes successfully
- `python3 verify.py` passes on fresh install
- Update from substrate works
- All expected files present and personalized

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `payload/principles/*` | D1 | ✓ |
| `payload/safety/*` | D1 | ✓ |
| `payload/operations/*` | D1 | ✓ |
| `payload/personas/*` | D1 | ✓ |
| `payload/workflows/*` | D1 | ✓ |
| `payload/voice/*` | D1 | ✓ |
| `payload/state/*` | D1 | ✓ |
| `config/manifest.yaml` | D2 | ✓ |
| `scripts/install.py` | D2 | ✓ |
| `scripts/verify.py` | D2 | ✓ |
| `config/defaults.yaml` | D3 | ✓ |
| `config/instances/*.yaml` | D3 | ✓ |
| `scripts/personalize.py` | D3 | ✓ |
| `templates/*.j2` | D3 | ✓ |
| `scripts/update.py` | D4 | ✓ |
| Update testing | D4 | ✓ |
| `SKILL.md` | D5 | ✓ |
| Substrate integration | D5 | ✓ |
| End-to-end testing | D5 | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| D1 | ~2,000 | ~15,000 | 8.5% | ✓ |
| D2 | ~2,000 | ~5,000 | 3.5% | ✓ |
| D3 | ~2,500 | ~8,000 | 5.3% | ✓ |
| D4 | ~1,500 | ~3,000 | 2.3% | ✓ |
| D5 | ~1,500 | ~5,000 | 3.3% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [ ] Wave dependencies are valid (D2-D5 depend on D1)
- [ ] `python3 N5/scripts/mece_validator.py n5os-bootstrap` passes

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | D1 | [n5os-bootstrap] D1: Payload Curation | `workers/D1-payload-curation.md` |
| 2 | D2 | [n5os-bootstrap] D2: Bootloader Core | `workers/D2-bootloader-core.md` |
| 2 | D3 | [n5os-bootstrap] D3: Personalization Engine | `workers/D3-personalization.md` |
| 3 | D4 | [n5os-bootstrap] D4: Update Mechanism | `workers/D4-update-mechanism.md` |
| 3 | D5 | [n5os-bootstrap] D5: Documentation | `workers/D5-documentation.md` |

**Wave structure:**
- Wave 1: D1 (payload must exist before anything else)
- Wave 2: D2, D3 (can run in parallel, both use payload)
- Wave 3: D4, D5 (depend on D2/D3 completion)

---

## Success Criteria

1. **Install works:** `python3 install.py --config zoputer.yaml` completes on fresh workspace
2. **Verify passes:** `python3 verify.py` returns exit 0 with all checks green
3. **Personalization applies:** Generated files contain instance-specific values
4. **Update works:** `python3 update.py` pulls new content without breaking local config
5. **Substrate syncs:** n5os-bootstrap appears in zoputer-substrate repo after push

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Payload too large for substrate | Use git-lfs or compress, test transfer |
| Personalization breaks on edge cases | Comprehensive defaults.yaml, fallback values |
| Update overwrites local changes | Strict separation: payload vs. personalization |
| Install on dirty workspace conflicts | --dry-run default, clear conflict reporting |
| Missing dependencies (Jinja2, etc.) | Bundle deps or use stdlib templates |

---

## Level Upper Review

*To be completed before build launch.*

### Counterintuitive Suggestions Received:
1. TBD

### Incorporated:
- TBD

### Rejected (with rationale):
- TBD
