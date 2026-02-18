---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: drop_brief
build_slug: n5os-bootstrap
drop_id: D3
wave: 2
depends_on: [D1]
status: pending
---

# D3: Personalization Engine

**Build:** n5os-bootstrap
**Wave:** 2 (depends on D1, parallel with D2)
**Title:** [n5os-bootstrap] D3: Personalization Engine

---

## Objective

Create the personalization system that adapts N5OS infrastructure to specific instances. This is what makes zoputer behave differently from va while sharing the same philosophy.

---

## Scope

### Files to Create

```
Skills/n5os-bootstrap/
├── config/
│   ├── defaults.yaml              # Default personalization
│   └── instances/
│       ├── zoputer.yaml           # Zoputer-specific config
│       └── example.yaml           # Template for new instances
├── scripts/
│   └── personalize.py             # Personalization engine
└── templates/
    ├── CLAUDE.md.j2               # CLAUDE.md template
    └── session-context.j2         # Session context template
```

### Must NOT Touch

- `Skills/n5os-bootstrap/payload/` (D1's scope)
- `Skills/n5os-bootstrap/config/manifest.yaml` (D2's scope)
- `Skills/n5os-bootstrap/scripts/install.py` (D2's scope)
- `Skills/n5os-bootstrap/scripts/verify.py` (D2's scope)
- `Skills/n5os-bootstrap/scripts/update.py` (D4's scope)
- `Skills/n5os-bootstrap/SKILL.md` (D5's scope)

---

## MUST DO

### 1. Create defaults.yaml

```yaml
# Default personalization for N5OS Bootstrap
# Override any values in instance-specific configs

instance:
  name: "my-zo"
  handle: "my-zo.zo.computer"
  owner: "Owner"
  role: general  # general | consulting-partner | personal-assistant

autonomy:
  level: supervised  # autonomous | supervised | restricted
  requires_approval:
    - external_comms
    - file_deletion
    - scheduled_tasks
    - service_creation
  parent: null  # escalation target handle (e.g., va.zo.computer)
  
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
  
paths:
  prefs: N5/prefs
  knowledge: Personal/Knowledge
  personas: Documents/System/personas
  logs: N5/logs
```

### 2. Create instances/zoputer.yaml

```yaml
# Zoputer instance configuration
# Inherits from defaults.yaml, overrides specific values

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
  primitives: shared  # pull from va's library

safety:
  protection_level: strict
  dry_run_default: true
```

### 3. Create instances/example.yaml

```yaml
# Example instance configuration
# Copy this file and modify for new instances

instance:
  name: "{{INSTANCE_NAME}}"           # e.g., "my-assistant"
  handle: "{{HANDLE}}.zo.computer"    # e.g., "my-assistant.zo.computer"
  owner: "{{OWNER_NAME}}"             # e.g., "Alice"
  role: general                       # general | consulting-partner | personal-assistant

autonomy:
  level: supervised                   # autonomous | supervised | restricted
  requires_approval:
    - external_comms
    - file_deletion
    - scheduled_tasks
    - service_creation
  parent: null                        # e.g., "va.zo.computer" for escalation

personas:
  enabled:                            # List of personas to enable
    - operator
    - builder
    - debugger
  disabled: []                        # List of personas to disable
  default: operator                   # Default persona on conversation start

voice:
  profile: professional               # professional | personal | formal
  primitives: local                   # local | shared | none

safety:
  protection_level: strict            # strict | standard | relaxed
  dry_run_default: true

features:
  pulse: true
  state_tracking: true
  conversation_logging: true
```

### 4. Create personalize.py

**Features:**
- Load instance config (merging with defaults)
- Process Jinja2 templates
- Replace placeholders in installed files
- Generate CLAUDE.md and session-context.md

**CLI Interface:**
```bash
python3 personalize.py CONFIG [OPTIONS]

Arguments:
  CONFIG            Path to instance config (e.g., instances/zoputer.yaml)

Options:
  --dry-run         Show what would be generated without writing
  --output-dir DIR  Write generated files to DIR instead of destinations
  --verbose         Show detailed progress
  --help            Show this help
```

**Pseudocode:**
```python
def main():
    args = parse_args()
    
    # Load and merge configs
    defaults = load_yaml(SKILL_ROOT / 'config/defaults.yaml')
    instance = load_yaml(args.config)
    config = deep_merge(defaults, instance)
    
    # Setup Jinja2 environment
    env = jinja2.Environment(
        loader=FileSystemLoader(SKILL_ROOT / 'templates'),
        undefined=jinja2.StrictUndefined
    )
    
    # Generate CLAUDE.md
    template = env.get_template('CLAUDE.md.j2')
    claude_md = template.render(**config)
    write_file('.claude/CLAUDE.md', claude_md, dry_run=args.dry_run)
    
    # Generate session-context.md
    template = env.get_template('session-context.j2')
    session_ctx = template.render(**config)
    write_file('.claude/session-context.md', session_ctx, dry_run=args.dry_run)
    
    # Replace placeholders in installed files
    for md_file in find_installed_files():
        content = md_file.read_text()
        content = content.replace('{{WORKSPACE}}', '/home/workspace')
        content = content.replace('{{INSTANCE}}', config['instance']['name'])
        content = content.replace('{{OWNER}}', config['instance']['owner'])
        # ... more replacements
        write_file(md_file, content, dry_run=args.dry_run)
    
    print(f"Personalization complete for {config['instance']['name']}")
```

### 5. Create templates/CLAUDE.md.j2

A Jinja2 template that generates the instance's CLAUDE.md file. Should include:

- Instance identification
- Active personas (from config)
- Autonomy rules (from config)
- Safety rules (from config)
- Escalation targets (from config)
- Core principles summary

**Template structure:**
```jinja2
# {{ instance.name | title }} Environment — Claude Code Integration

**Owner:** {{ instance.owner }}
**Instance:** {{ instance.handle }}
**Role:** {{ instance.role }}
{% if autonomy.parent %}
**Parent Instance:** {{ autonomy.parent }}
{% endif %}

---

## Autonomy Level: {{ autonomy.level | title }}

{% if autonomy.level == 'supervised' %}
This instance operates under supervision. The following actions require explicit approval:
{% for action in autonomy.requires_approval %}
- {{ action | replace('_', ' ') | title }}
{% endfor %}
{% endif %}

---

## Active Personas

{% for persona in personas.enabled %}
- {{ persona | title }}
{% endfor %}

Default: {{ personas.default | title }}

---

## Safety Configuration

- Protection Level: {{ safety.protection_level | title }}
- Dry-Run Default: {{ safety.dry_run_default }}

---

## Core Principles

This instance runs N5OS philosophy. Key principles:

- **P02:** Single Source of Truth
- **P05:** Safety, Determinism, Anti-Overwrite
- **P08:** Minimal Context, Maximal Clarity
- **P15:** Complete Before Claiming Complete
- **P16:** Accuracy Over Sophistication

See `Personal/Knowledge/Architecture/principles/` for full reference.

---

*Generated by n5os-bootstrap v1.0*
```

### 6. Create templates/session-context.j2

Template for session initialization:

```jinja2
# Session Context

**Instance:** {{ instance.name }}
**Started:** [TIMESTAMP]

## Environment

This is {{ instance.owner }}'s {{ instance.role }} instance running N5OS.

## Autonomy

Level: {{ autonomy.level }}
{% if autonomy.parent %}
Escalation Target: {{ autonomy.parent }}
{% endif %}

## Active Personas

{% for persona in personas.enabled %}
- {{ persona }}
{% endfor %}

---

## Progress This Session

[Session progress will be tracked here]

## Decisions Made

[Decisions will be logged here]

## Next Steps

[Next steps will be recorded here]
```

---

## MUST NOT DO

- Do NOT modify install.py or manifest.yaml — D2's scope
- Do NOT create update.py — D4's scope
- Do NOT modify payload files — D1's scope
- Do NOT use dependencies beyond Python stdlib and Jinja2 (Jinja2 is pre-installed)
- Do NOT include va-specific personal data in templates

---

## Expected Output

### Deposit Structure

```yaml
drop_id: D3
status: complete
files_created:
  - Skills/n5os-bootstrap/config/defaults.yaml
  - Skills/n5os-bootstrap/config/instances/zoputer.yaml
  - Skills/n5os-bootstrap/config/instances/example.yaml
  - Skills/n5os-bootstrap/scripts/personalize.py
  - Skills/n5os-bootstrap/templates/CLAUDE.md.j2
  - Skills/n5os-bootstrap/templates/session-context.j2
total_files: 6
test_results:
  dry_run: "Shows generated CLAUDE.md content for zoputer"
  personalize: "Generates correct files with zoputer values"
```

### Verification Commands

```bash
# Test dry run
python3 Skills/n5os-bootstrap/scripts/personalize.py \
  Skills/n5os-bootstrap/config/instances/zoputer.yaml --dry-run

# Verify generated content
grep "zoputer" .claude/CLAUDE.md  # Should find instance name
grep "supervised" .claude/CLAUDE.md  # Should find autonomy level
```

---

## Context Files to Read

1. `file 'CLAUDE.md'` — Current va CLAUDE.md for reference
2. `file '.claude/session-context.md'` — Current session context pattern
3. `file 'N5/builds/n5os-bootstrap/PLAN.md'` — Full plan context

---

## Build Lesson Ledger

Check ledger: `python3 Skills/pulse/scripts/pulse_learnings.py read n5os-bootstrap`
Log lessons: `python3 Skills/pulse/scripts/pulse_learnings.py add n5os-bootstrap "lesson" --source D3`
