---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: drop_brief
build_slug: n5os-bootstrap
drop_id: D5
wave: 3
depends_on: [D2, D3]
status: pending
---

# D5: Documentation & Integration

**Build:** n5os-bootstrap
**Wave:** 3 (depends on D2, D3 — parallel with D4)
**Title:** [n5os-bootstrap] D5: Documentation & Integration

---

## Objective

Create comprehensive documentation and integrate n5os-bootstrap into the substrate export system. This makes the skill discoverable, usable, and distributable.

---

## Scope

### Files to Create/Update

```
Skills/n5os-bootstrap/
└── SKILL.md                   # Comprehensive skill documentation

N5/config/
└── substrate-exports.yaml     # UPDATE - Add n5os-bootstrap to exports
```

### Must NOT Touch

- `Skills/n5os-bootstrap/payload/` (D1's scope)
- `Skills/n5os-bootstrap/config/manifest.yaml` (D2's scope)
- `Skills/n5os-bootstrap/scripts/install.py` (D2's scope)
- `Skills/n5os-bootstrap/scripts/verify.py` (D2's scope)
- `Skills/n5os-bootstrap/config/defaults.yaml` (D3's scope)
- `Skills/n5os-bootstrap/config/instances/` (D3's scope)
- `Skills/n5os-bootstrap/scripts/personalize.py` (D3's scope)
- `Skills/n5os-bootstrap/templates/` (D3's scope)
- `Skills/n5os-bootstrap/scripts/update.py` (D4's scope)

---

## MUST DO

### 1. Create SKILL.md

Full documentation following the Agent Skills spec. Must include:

```markdown
---
name: n5os-bootstrap
description: >
  Bootstrap N5OS philosophy and infrastructure on any Zo instance.
  Installs architectural principles, safety protocols, operational workflows,
  and persona definitions with per-instance personalization.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: 1.0.0
  category: system
  tags: [infrastructure, philosophy, bootstrap, personalization]
---

# N5OS Bootstrap

A distributable operating system substrate for Zo instances. Installs the N5OS
philosophy, safety systems, and operational protocols that power va.zo.computer.

## What This Does

N5OS Bootstrap is a "seed" skill that unpacks into actual infrastructure:

- **Principles** — 15+ architectural principles (P24-P39) that guide system behavior
- **Safety** — Protection protocols, dry-run defaults, file protection rules
- **Operations** — Planning prompts, conversation lifecycle, debug workflows
- **Personas** — 8 specialized personas (Builder, Debugger, Strategist, etc.)
- **Workflows** — Execution patterns for each persona
- **Voice** — Anti-patterns and style guidance

## Quick Start

### 1. Install

```bash
# Fresh install with defaults
python3 Skills/n5os-bootstrap/scripts/install.py

# Install with specific instance config
python3 Skills/n5os-bootstrap/scripts/install.py \
  --config Skills/n5os-bootstrap/config/instances/zoputer.yaml

# Preview what will be installed
python3 Skills/n5os-bootstrap/scripts/install.py --dry-run
```

### 2. Personalize

Create your own instance config:

```bash
# Copy the example
cp Skills/n5os-bootstrap/config/instances/example.yaml \
   Skills/n5os-bootstrap/config/instances/my-instance.yaml

# Edit with your values
# Then apply:
python3 Skills/n5os-bootstrap/scripts/personalize.py \
  Skills/n5os-bootstrap/config/instances/my-instance.yaml
```

### 3. Verify

```bash
python3 Skills/n5os-bootstrap/scripts/verify.py
```

### 4. Update

```bash
# Check for updates
python3 Skills/n5os-bootstrap/scripts/update.py --dry-run

# Apply updates
python3 Skills/n5os-bootstrap/scripts/update.py
```

## Personalization Reference

### Instance Configuration

| Field | Type | Description |
|-------|------|-------------|
| `instance.name` | string | Instance identifier (e.g., "zoputer") |
| `instance.handle` | string | Full handle (e.g., "zoputer.zo.computer") |
| `instance.owner` | string | Owner name (e.g., "V") |
| `instance.role` | enum | `general`, `consulting-partner`, `personal-assistant` |

### Autonomy Levels

| Level | Behavior |
|-------|----------|
| `autonomous` | Full autonomy, minimal approval required |
| `supervised` | Requires approval for specified actions |
| `restricted` | Most actions require explicit approval |

### Requires Approval Options

- `external_comms` — Sending emails, SMS, external API calls
- `file_deletion` — Deleting files or directories
- `scheduled_tasks` — Creating scheduled agents
- `service_creation` — Registering new services

### Persona Configuration

```yaml
personas:
  enabled:
    - operator      # Default conversational mode
    - builder       # Code and system building
    - debugger      # Systematic debugging
    - researcher    # Multi-source research
    - strategist    # Decision frameworks
    - teacher       # Scaffolded explanation
    - writer        # Voice-aware writing
    - architect     # Build planning
  disabled:
    - nutritionist  # Optional personas
    - trainer
  default: operator
```

### Voice Profiles

| Profile | Description |
|---------|-------------|
| `professional` | Clear, direct, business-appropriate |
| `personal` | Warmer, more conversational |
| `formal` | Precise, documentation-style |

### Safety Levels

| Level | Behavior |
|-------|----------|
| `strict` | All protections active, dry-run default |
| `standard` | Core protections, optional dry-run |
| `relaxed` | Minimal protections (not recommended) |

## Directory Structure

After installation, N5OS content is distributed to:

```
/home/workspace/
├── Personal/Knowledge/Architecture/principles/  # Architectural principles
├── N5/prefs/
│   ├── system/           # Safety protocols
│   ├── operations/       # Operational protocols
│   ├── workflows/        # Persona workflows
│   └── voice/            # Voice guidance
├── Documents/System/personas/  # Persona definitions
└── .claude/
    ├── CLAUDE.md         # Generated from personalization
    └── session-context.md # Generated from personalization
```

## Philosophy

N5OS is built on several core ideas:

1. **Single Source of Truth (P02)** — Each fact lives in exactly one place
2. **Safety & Determinism (P05)** — Dry-run first, explicit consent for side-effects
3. **Minimal Context (P08)** — Load only what's needed
4. **Complete Before Claiming (P15)** — Honest progress reporting
5. **Accuracy Over Sophistication (P16)** — Conservative facts over speculation

See `Personal/Knowledge/Architecture/principles/` for the full principle set.

## Updating

N5OS Bootstrap stays installed for updates. When va publishes new principles
or protocols, run:

```bash
python3 Skills/n5os-bootstrap/scripts/update.py
```

This pulls new payload content without touching your personalization config.

### Selective Updates

```bash
# Update only principles
python3 Skills/n5os-bootstrap/scripts/update.py --component principles

# Update only safety protocols
python3 Skills/n5os-bootstrap/scripts/update.py --component safety
```

## Troubleshooting

### Verification Fails

Run verbose verification to see what's missing:

```bash
python3 Skills/n5os-bootstrap/scripts/verify.py --verbose
```

Common issues:
- Missing directories (run install again)
- Unreplaced placeholders (run personalize again)
- Corrupt files (run update with --force)

### Conflicts During Install

If files already exist:

```bash
# Preview conflicts
python3 Skills/n5os-bootstrap/scripts/install.py --dry-run

# Force overwrite
python3 Skills/n5os-bootstrap/scripts/install.py --force
```

### Reset to Defaults

```bash
# Re-install with force
python3 Skills/n5os-bootstrap/scripts/install.py --force

# Re-personalize
python3 Skills/n5os-bootstrap/scripts/personalize.py \
  Skills/n5os-bootstrap/config/instances/your-config.yaml
```

## For Instance Maintainers

### Creating a New Instance Config

1. Copy `config/instances/example.yaml`
2. Replace placeholder values
3. Adjust autonomy and persona settings
4. Run install with your config
5. Commit your config to your repo

### Escalation Setup

For child instances (like zoputer → va):

```yaml
autonomy:
  level: supervised
  parent: va.zo.computer  # Escalation target
```

This enables human-escalation skill to route decisions to the parent instance.

## Version History

- **1.0.0** — Initial release with full payload, personalization, and update system

---

*Generated by n5os-bootstrap | va.zo.computer*
```

### 2. Update substrate-exports.yaml

Add n5os-bootstrap to the exports list:

```yaml
# Add to exports.skills section:
skills:
  # ... existing skills ...
  - n5os-bootstrap
```

### 3. End-to-End Testing

Before marking complete, verify:

1. **Fresh install test:**
   ```bash
   # In a test workspace
   python3 Skills/n5os-bootstrap/scripts/install.py \
     --config Skills/n5os-bootstrap/config/instances/example.yaml \
     --verbose
   ```

2. **Verify test:**
   ```bash
   python3 Skills/n5os-bootstrap/scripts/verify.py --verbose
   # Should show all checks pass
   ```

3. **Personalization test:**
   ```bash
   # Check generated files have correct values
   grep "my-zo" .claude/CLAUDE.md
   grep "Owner" .claude/CLAUDE.md
   ```

4. **Update test (dry-run):**
   ```bash
   python3 Skills/n5os-bootstrap/scripts/update.py --dry-run
   # Should show "Already up to date" or list available updates
   ```

---

## MUST NOT DO

- Do NOT create or modify scripts — D2 and D4 handle those
- Do NOT create config files — D3 handles those
- Do NOT modify payload — D1 handles that
- Do NOT include va-specific personal information in docs
- Do NOT include persona UUIDs (those are instance-specific)

---

## Expected Output

### Deposit Structure

```yaml
drop_id: D5
status: complete
files_created:
  - Skills/n5os-bootstrap/SKILL.md
files_modified:
  - N5/config/substrate-exports.yaml
total_files: 2
test_results:
  fresh_install: "Completes without error"
  verify: "All checks pass"
  personalization: "Generated files contain correct values"
  update_dry_run: "Shows correct status"
  skill_readable: "SKILL.md renders correctly"
```

### Verification Commands

```bash
# Check SKILL.md exists and is valid
head -50 Skills/n5os-bootstrap/SKILL.md

# Check substrate exports updated
grep "n5os-bootstrap" N5/config/substrate-exports.yaml

# Full test cycle
python3 Skills/n5os-bootstrap/scripts/install.py --force --verbose && \
python3 Skills/n5os-bootstrap/scripts/verify.py --verbose
```

---

## Context Files to Read

1. `file 'Skills/pulse/SKILL.md'` — Example of good SKILL.md structure
2. `file 'N5/config/substrate-exports.yaml'` — Current exports structure
3. `file 'N5/builds/n5os-bootstrap/PLAN.md'` — Full build plan

---

## Build Lesson Ledger

Check ledger: `python3 Skills/pulse/scripts/pulse_learnings.py read n5os-bootstrap`
Log lessons: `python3 Skills/pulse/scripts/pulse_learnings.py add n5os-bootstrap "lesson" --source D5`
