# N5 OS Core - Phase 0.5: System Onboarding
## REVISED SPECIFICATION

**Date**: 2025-10-28 05:30 ET  
**Worker**: WORKER_dfVR_20251028_085810  
**Thread**: con_IktUO0F8fSBLPZuo  

---

## Mission

**Configure N5 OS Core system after user completes manual prerequisites.**

NOT bio collection. NOT basic setup. This is **N5-specific system configuration only.**

---

## Order of Operations

### BEFORE Onboarding (User Does Manually)

1. ✅ Clone n5os-core to their Zo
2. ✅ Add rules in Zo settings
3. ✅ Connect apps (Gmail, Drive, Notion, Calendar)
4. ✅ Add bio in Zo settings
5. ✅ Add personas (Vibe Builder Bootstrap, Vibe Debugger Bootstrap)

### DURING Onboarding (This System)

6. **Verify prerequisites** - Check all manual steps complete
7. **Configure N5 workflows** - Which systems to enable
8. **Set automation level** - How much auto vs manual
9. **Generate user_config/** - Personalized settings
10. **Validate setup** - Test everything works
11. **Generate welcome guide** - User's personalized docs

---

## Onboarding Questions (N5-Specific Only)

### Q1: Workflow Systems
```
Which N5 workflow systems do you want to enable?

- [x] Lists (manage actions, ideas, must-contact)
- [ ] Meetings (AAR generation, follow-ups)
- [ ] Digests (daily summaries)
- [ ] Social (X/LinkedIn content)
- [ ] CRM (relationship tracking)

You can enable more later via /configure
```

**Writes to**: `user_config/preferences.json` → `workflows` section

---

### Q2: Automation Level
```
How much should N5 automate?

1. Manual - I'll trigger everything explicitly
2. Semi-Auto - Suggest automations, I approve
3. Auto - Run scheduled tasks automatically

Recommended for startups: Semi-Auto
```

**Writes to**: `user_config/preferences.json` → `automation.level`

---

### Q3: Scheduled Tasks
```
Enable these scheduled tasks? (Semi-Auto mode)

- [ ] Daily: Index rebuild (keeps Knowledge current)
- [ ] Daily: Git check (prevents accidental commits)
- [ ] Weekly: Empty files cleanup
- [ ] Weekly: List review reminder

You can modify schedule later
```

**Writes to**: `user_config/preferences.json` → `automation.tasks`  
**Generates**: Actual scheduled tasks in Zo

---

### Q4: Conversation End Behavior
```
At conversation end, should Zo:

1. Just summarize (minimal)
2. Summarize + update lists (recommended)
3. Summarize + update + trigger workflows (max automation)

Recommended: Option 2
```

**Writes to**: `user_config/preferences.json` → `conversation_end.behavior`

---

### Q5: Git Workflow
```
Git safety preferences:

- [x] Run git-check before commits (recommended)
- [ ] Auto-commit daily changes
- [ ] Require explicit approval for pushes

Safety first: Keep defaults
```

**Writes to**: `user_config/preferences.json` → `git.safety_mode`

---

### Q6: Telemetry (Optional)
```
Enable anonymous usage telemetry?

- Helps improve N5 OS Core
- Completely anonymous (no personal data)
- Stored locally only
- Can disable anytime

[Y/n]
```

**Writes to**: `user_config/telemetry_settings.json`

---

## What Gets Created: user_config/

```
n5os-core/
└── user_config/           # Created by onboarding, gitignored
    ├── preferences.json   # N5 system configuration
    ├── telemetry_settings.json
    ├── .onboarding_complete   # Timestamp + version
    └── README.md          # "This is your personal config"
```

### user_config/preferences.json
```json
{
  "version": "1.0.0",
  "created": "2025-10-28T05:30:00Z",
  "workflows": {
    "lists": true,
    "meetings": false,
    "digests": true,
    "social": false,
    "crm": false
  },
  "automation": {
    "level": "semi-auto",
    "scheduled_tasks_enabled": true,
    "tasks": ["index-rebuild", "git-check", "empty-files"]
  },
  "conversation_end": {
    "behavior": "summarize_and_update_lists",
    "auto_archive": true
  },
  "git": {
    "safety_mode": "strict",
    "auto_commit": false,
    "require_approval": true
  },
  "n5": {
    "recipes_enabled": true,
    "session_state_tracking": true,
    "persona_active": "vibe-builder"
  }
}
```

### user_config/telemetry_settings.json
```json
{
  "enabled": false,
  "anonymous_id": null,
  "events_tracked": [],
  "storage": "local_only",
  "last_event": null,
  "opt_in_date": null
}
```

### user_config/.onboarding_complete
```json
{
  "completed": "2025-10-28T05:30:45Z",
  "n5_version": "1.0.0-core",
  "onboarding_version": "0.5",
  "prerequisites_verified": true,
  "validation_passed": true,
  "user_zo_account": "username.zo.computer"
}
```

---

## Integration with Existing N5 Systems

### 1. Recipes System
**File**: `Recipes/recipes.jsonl`

Onboarding does NOT write to recipes.jsonl (that's system-level).  
User can add custom recipes later via N5 commands.

### 2. Session State Manager
**Script**: `N5/scripts/session_state_manager.py`

Onboarding uses session state to track conversation:
```python
python3 N5/scripts/session_state_manager.py init --type onboarding
```

### 3. Scheduled Tasks
**Via**: Zo's native scheduling API

If user enables scheduled tasks, create them via Zo:
```python
from zo import create_scheduled_task

if prefs["automation"]["scheduled_tasks_enabled"]:
    for task in prefs["automation"]["tasks"]:
        create_scheduled_task(
            rrule=task_schedules[task],
            instruction=task_instructions[task],
            delivery_method="email"
        )
```

### 4. Prefs System
**File**: `N5/prefs/prefs.md`

User preferences in `user_config/` OVERRIDE defaults in `N5/prefs/`.  
Scripts check `user_config/preferences.json` first, fallback to system defaults.

---

## Validation Tests (12 Required)

### Prerequisites Check
1. ✅ Zo rules configured (check settings)
2. ✅ Apps connected (Gmail, Drive, Notion exist)
3. ✅ Bio provided (check Zo settings)
4. ✅ Personas added (Vibe Builder, Vibe Debugger exist)

### Config Generation
5. ✅ `user_config/` directory created
6. ✅ `preferences.json` valid JSON + schema compliant
7. ✅ `telemetry_settings.json` exists
8. ✅ `.onboarding_complete` timestamp written

### System Integration
9. ✅ Recipes system recognizes config
10. ✅ Session state manager works
11. ✅ Scheduled tasks created (if enabled)
12. ✅ Git protection active (user_config/ gitignored)

---

## Technical Implementation

### Script 1: `n5_onboard.py`
**Purpose**: Main orchestrator

```python
#!/usr/bin/env python3
"""
N5 OS Core Onboarding Orchestrator
Configures N5 system after manual prerequisites complete.
"""
import argparse
import logging
from pathlib import Path
import json
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main(dry_run: bool = False) -> int:
    try:
        # Phase 1: Verify prerequisites
        if not verify_prerequisites():
            logger.error("Prerequisites not complete. See installation guide.")
            return 1
        
        # Phase 2: Interactive interview
        prefs = run_interview()
        
        # Phase 3: Generate user_config/
        if dry_run:
            logger.info("[DRY RUN] Would create user_config/")
            logger.info(f"Config: {json.dumps(prefs, indent=2)}")
            return 0
        
        create_user_config(prefs)
        
        # Phase 4: Setup scheduled tasks
        if prefs["automation"]["scheduled_tasks_enabled"]:
            setup_scheduled_tasks(prefs["automation"]["tasks"])
        
        # Phase 5: Validate
        if not validate_setup():
            logger.error("Validation failed")
            return 1
        
        # Phase 6: Complete
        mark_onboarding_complete()
        generate_welcome_guide(prefs)
        
        logger.info("✓ N5 OS Core onboarding complete!")
        logger.info(f"Config: /home/workspace/n5os-core/user_config/")
        return 0
        
    except Exception as e:
        logger.error(f"Onboarding failed: {e}", exc_info=True)
        return 1

def verify_prerequisites() -> bool:
    """Check all manual setup steps complete."""
    # Check Zo settings, apps, personas
    pass

def run_interview() -> dict:
    """Interactive N5 configuration interview."""
    # Q1-Q6 from spec
    pass

def create_user_config(prefs: dict) -> None:
    """Generate user_config/ directory."""
    user_config = Path("/home/workspace/n5os-core/user_config")
    user_config.mkdir(exist_ok=True)
    
    # Write preferences.json
    (user_config / "preferences.json").write_text(
        json.dumps(prefs, indent=2)
    )
    
    # Write telemetry_settings.json
    # Write README.md
    pass

def setup_scheduled_tasks(tasks: list) -> None:
    """Create scheduled tasks in Zo."""
    pass

def validate_setup() -> bool:
    """Run 12 validation tests."""
    pass

def mark_onboarding_complete() -> None:
    """Write .onboarding_complete marker."""
    pass

def generate_welcome_guide(prefs: dict) -> None:
    """Create personalized welcome guide."""
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
```

### Script 2: `prerequisite_checker.py`
Validates manual setup complete

### Script 3: `config_generator.py`
Creates user_config/ from interview answers

### Script 4: `setup_validator.py`
Runs 12 validation tests

### Script 5: `welcome_guide_generator.py`
Creates personalized docs

---

## Recipe Registration

**File**: `Recipes/onboard.md`

```markdown
---
description: Configure N5 OS Core system (run once after manual setup)
tags:
  - setup
  - system
  - onboarding
---

# N5 Onboarding

Run this AFTER completing manual prerequisites:
1. Rules configured in Zo settings
2. Apps connected (Gmail, Drive, Notion)
3. Bio provided
4. Personas added (Vibe Builder, Vibe Debugger)

## What This Does

- Configures N5 workflow systems
- Sets automation level
- Creates your user_config/
- Validates everything works
- Generates welcome guide

## Run

```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py
```

Or use dry-run to preview:
```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py --dry-run
```

Takes 10-15 minutes.
```

---

## Success Criteria

**Setup Complete When:**

1. ✅ All 12 validation tests pass
2. ✅ `user_config/` exists with valid configs
3. ✅ Scheduled tasks created (if enabled)
4. ✅ Welcome guide generated
5. ✅ `.onboarding_complete` marker written
6. ✅ User receives "Setup complete!" confirmation

---

## Deliverables

1. **5 Python scripts** (orchestrator, checker, generator, validator, guide generator)
2. **Recipe file** (`Recipes/onboard.md`)
3. **Config templates** (JSON schemas)
4. **Validation suite** (12 tests)
5. **Welcome guide template** (Jinja2)
6. **Integration tests** (with Phases 0-5)

---

## Estimated Time

**Implementation**: 10-12 hours
- Scripts: 6-8h
- Validation: 2-3h
- Integration testing: 2h
- Manual QA: 1h

---

**This is the correct spec. Focused purely on N5 configuration, no basic info collection.**

*Revised: 2025-10-28 05:30 ET*
