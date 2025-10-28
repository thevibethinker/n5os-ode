# Phase 0: Foundation - Detailed Implementation Plan

**Objective**: Deploy minimal foundation that makes Zo think and maintain itself correctly

**Duration Estimate**: 4-6 orchestrator conversations (depending on complexity discovered)

---

## Components to Build

### 1. Core Rules Template (`/N5/templates/rules.template.md`)

**What it contains**:
```markdown
# N5OS Core Rules

## Always Applied Rules
- No hallucination - say "don't know" vs. fabricate
- 3+ clarifying questions if any doubt
- Non-technical explanations with boundary-pushing depth
- Never send messages or download files without authorization
- Load SESSION_STATE.md and update throughout conversation
- Timestamp responses (ET/EST)

## Conditional Rules
- [Component invocation] → Validate against schemas, isolate execution
- [Cross-module data flow] → Enforce tagged handoffs
- [Destructive actions] → Dry-run preview + confirmation
- [System operations] → Check for registered command first
- [Major system work] → Load planning prompt first
- [Scheduled tasks] → Follow scheduled-task-protocol.md

## Troubleshooting Protocol
When stuck:
1. Stop trying to solve directly
2. Step outside current approach
3. Ask: Missing info? Wrong order? Dependencies? Bad approach? Novel angle?
```

**Differences from Main**:
- Remove V-specific personal preferences (name, company name, etc.)
- Keep safety protocols
- Keep thinking protocols
- Generalize file paths to use N5OS standard locations

**Transport method**: Copy → redact → test on Demonstrator

---

### 2. Cleanup Schedule (`/N5/scripts/system_cleanup.py`)

**Functionality**:
```python
#!/usr/bin/env python3
"""
N5OS System Cleanup
Runs: Daily at 3 AM (configurable)
Purpose: Prune old logs, temp files, maintain disk space
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta

# Configurable thresholds
LOG_RETENTION_DAYS = 30
TEMP_RETENTION_DAYS = 7
BULLETIN_RETENTION_DAYS = 10

def cleanup_logs():
    """Remove logs older than retention period"""
    pass

def cleanup_temp():
    """Remove temp files and old conversation workspaces"""
    pass

def prune_bulletins():
    """Keep only recent bulletins"""
    pass

if __name__ == "__main__":
    cleanup_logs()
    cleanup_temp()
    prune_bulletins()
```

**Schedule registration**:
```bash
# User runs after install:
python3 /home/workspace/N5/scripts/register_cleanup_schedule.py
```

**Transport method**: Write fresh on Demonstrator (simple script)

---

### 3. Self-Description Generator (`/N5/scripts/generate_self_description.py`)

**Purpose**: Help AI understand its own setup when starting new conversations

**Functionality**:
```python
#!/usr/bin/env python3
"""
Generates /N5/data/system_description.md
- Lists installed components
- Counts files in key directories
- Shows schedule status
- Identifies customizations
"""

def scan_components():
    """Check which N5 components are installed"""
    components = {
        'session_state': Path('N5/scripts/session_state_manager.py').exists(),
        'bulletins': Path('N5/data/system_bulletins.jsonl').exists(),
        'commands': Path('N5/config/commands.jsonl').exists(),
        'orchestrator': Path('N5/scripts/build_orchestrator.py').exists(),
    }
    return components

def generate_description():
    """Create markdown summary"""
    pass

if __name__ == "__main__":
    generate_description()
```

**Output example**:
```markdown
# N5OS System Description
Generated: 2025-10-27 23:50 ET

## Installed Components
- ✅ Phase 0: Foundation (rules, cleanup, init)
- ✅ Phase 1: Infrastructure (session state, bulletins)
- ❌ Phase 2: Commands (not yet installed)
- ❌ Phase 3: Build System (not yet installed)

## Statistics
- Conversations registered: 45
- Knowledge files: 23
- Active schedules: 2
- Custom commands: 5

## Customizations
- User has modified: prefs.md, commands.jsonl
- Using default: rules.md, schemas
```

**Transport method**: Write fresh on Demonstrator

---

### 4. Config Template System (`/N5/scripts/n5_init.py`)

**Core logic**:
```python
#!/usr/bin/env python3
"""
N5OS Initialization Script
- Detects missing config files
- Generates from templates
- Prompts for customization (optional)
- Validates setup
"""

import shutil
from pathlib import Path

TEMPLATE_DIR = Path("/home/workspace/N5/templates")
CONFIG_DIR = Path("/home/workspace/N5/config")

def check_configs():
    """Return list of missing config files"""
    required = ['prefs.md', 'commands.jsonl', 'rules.md']
    missing = []
    for req in required:
        if not (CONFIG_DIR / req).exists():
            missing.append(req)
    return missing

def generate_config(template_name):
    """Copy template to config dir with optional customization"""
    template = TEMPLATE_DIR / f"{template_name}.template.md"
    config = CONFIG_DIR / template_name
    
    # Copy template
    shutil.copy(template, config)
    
    # Optional: Prompt for customization
    print(f"✓ Generated {config}")
    print(f"  Review and customize: {config}")

def validate_setup():
    """Check that system is ready"""
    checks = [
        (Path("N5/templates").exists(), "Templates directory exists"),
        (Path("N5/config").exists(), "Config directory exists"),
        (Path("N5/scripts").exists(), "Scripts directory exists"),
    ]
    
    for check, desc in checks:
        status = "✓" if check else "✗"
        print(f"{status} {desc}")

if __name__ == "__main__":
    missing = check_configs()
    if missing:
        print("Missing configs detected, generating from templates...")
        for m in missing:
            generate_config(m)
    else:
        print("✓ All configs present")
    
    validate_setup()
```

**Transport method**: Write fresh on Demonstrator

---

### 5. Directory Structure Setup

**Script**: `/N5/scripts/create_structure.py`

```python
#!/usr/bin/env python3
"""Create N5OS directory structure"""

from pathlib import Path

STRUCTURE = {
    'N5': {
        'templates': {},
        'config': {},
        'scripts': {},
        'schemas': {},
        'data': {},
        'prefs': {
            'operations': {},
            'preferences': {},
        },
    },
    'Knowledge': {
        'architectural': {},
    },
    'Lists': {},
    'Records': {
        'Temporary': {},
    },
    'Documents': {},
}

def create_tree(base, structure):
    """Recursively create directory tree"""
    for name, children in structure.items():
        path = base / name
        path.mkdir(exist_ok=True)
        if children:
            create_tree(path, children)

if __name__ == "__main__":
    base = Path("/home/workspace")
    create_tree(base, STRUCTURE)
    print("✓ Directory structure created")
```

---

## Testing Checklist

### Before Declaring Phase 0 Complete

- [ ] **Fresh Zo test**: Clone repo on Demonstrator, run init script
- [ ] **Rule loading**: AI loads rules template without error
- [ ] **Config generation**: Init script creates all config files from templates
- [ ] **Template protection**: Confirm `/config/` in .gitignore
- [ ] **Cleanup schedule**: Registers and runs without error
- [ ] **Self-description**: Generates accurate system summary
- [ ] **Documentation**: README explains setup for new users
- [ ] **Git push**: Successfully push to GitHub
- [ ] **Pull update**: Simulate update (git pull doesn't overwrite configs)

---

## Documentation Requirements

### Files to Create

1. **README.md** (root)
   - What is N5OS?
   - Quick start (5 steps)
   - Link to full docs

2. **/docs/installation.md**
   - Prerequisites (Zo account)
   - Clone repo
   - Run init script
   - Verify installation
   - Troubleshooting

3. **/docs/configuration.md**
   - Template vs. config distinction
   - How to customize
   - How to update without losing changes

4. **CHANGELOG.md**
   - Track versions
   - Breaking changes
   - Migration guides

---

## Orchestrator Thread Structure

### Thread Assignment

**Orchestrator Thread 1**: Directory structure + init script
- Build create_structure.py
- Build n5_init.py
- Test on Demonstrator

**Orchestrator Thread 2**: Rules template
- Extract from Main
- Redact V-specific elements
- Test on Demonstrator

**Orchestrator Thread 3**: Cleanup + self-description
- Build system_cleanup.py
- Build generate_self_description.py
- Register schedules
- Test on Demonstrator

**Orchestrator Thread 4**: Documentation
- README.md
- Installation guide
- Configuration guide
- Test with fresh user perspective

**Orchestrator Thread 5**: Integration testing
- Full end-to-end test
- GitHub push
- Pull and verify
- Fix any issues

---

## Success Metrics

### Quantitative
- Setup time: < 30 minutes for new user
- Init script success rate: 100%
- Config generation accuracy: 100%
- Cleanup runs without error: 100%

### Qualitative
- New user can follow docs and get working system
- AI operates correctly with rule template
- Update process preserves user customizations
- System feels "complete" even at Phase 0

---

## Handoff to Next Phase

### Prerequisites for Phase 1
- [ ] Phase 0 fully tested and documented
- [ ] Pushed to GitHub
- [ ] V confirms Demonstrator working correctly
- [ ] Lessons learned documented

### Outputs for Phase 1
- Working config system (Phase 1 can add new templates)
- Established patterns for transport (copy/redact/test)
- Documentation template for subsequent phases

---

*Created: 2025-10-27 23:47 ET*
