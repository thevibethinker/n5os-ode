# N5 OS Core - Phase 0.1 Orchestrator Brief

**Project**: N5 OS (Cesc v0.1)  
**Phase**: 0.1 - Directory Structure + Init Script  
**Planning Thread**: con_HuaTrPlhVJRg9c9m (on Main: va.zo.computer)  
**Target Environment**: vademonstrator.zo.computer  
**GitHub Repo**: https://github.com/vattawar/zo-n5os-core

---

## Your Mission (Phase 0.1)

Build the **foundation structure** and **initialization script** for N5 OS Core.

**Time Estimate**: 1-2 hours  
**Complexity**: Low (pure setup, no complex logic)

---

## Context Documents

**LOAD THESE FIRST**:
1. Planning thread conversation workspace: `/home/.z/workspaces/con_HuaTrPlhVJRg9c9m/`
   - `n5os_core_spec.md` - Complete specification
   - `phase0_detailed_plan.md` - Your implementation guide
   - `demonstrator_empty_structure.md` - File structure reference

---

## What You're Building (Phase 0.1)

### 1. Directory Structure

Create on **vademonstrator.zo.computer**:

```
/home/workspace/
├── N5/
│   ├── templates/          # Config templates (from GitHub)
│   ├── config/             # Generated user configs (git ignored)
│   ├── scripts/            # System scripts
│   ├── data/               # System data
│   └── schemas/            # (Phase 2)
├── docs/                   # User documentation
└── .gitignore             # Ignore /N5/config/
```

### 2. Initialization Script (`/N5/scripts/n5_init.py`)

**Purpose**: Detects missing user configs and generates them from templates

**Logic**:
```python
def check_config(template_name):
    template = TEMPLATE_DIR / f"{template_name}.template.md"
    config = CONFIG_DIR / f"{template_name}.md"
    
    if not config.exists():
        if not template.exists():
            raise FileNotFoundError(f"Template missing: {template}")
        
        print(f"Generating {config.name} from template...")
        config.write_text(template.read_text())
        print(f"✓ Created {config}")
    else:
        print(f"✓ Config exists: {config}")

def main():
    # Ensure dirs exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check each config type
    check_config("rules")
    check_config("prefs")
    
    print("\n✓ N5 initialization complete")
```

**Requirements**:
- Python 3.12
- `pathlib` for paths
- Logging with timestamps
- Helpful error messages
- Exit codes (0 = success, 1 = error)

### 3. .gitignore

```
# User-generated configs (never commit)
/N5/config/

# System data
/N5/data/

# Python
__pycache__/
*.pyc

# Logs
*.log

# OS
.DS_Store
```

---

## Success Criteria

- [ ] Directory structure created on vademonstrator
- [ ] `n5_init.py` script written and tested
- [ ] `.gitignore` configured correctly
- [ ] Running `python3 N5/scripts/n5_init.py` succeeds (even with no templates yet)
- [ ] Script creates `/N5/config/` directory
- [ ] Script logs helpful messages
- [ ] Documentation written in `/docs/phase0_setup.md`

---

## Testing Checklist

```bash
# On vademonstrator.zo.computer
cd /home/workspace

# Test 1: Script runs without templates (should create dirs, log info)
python3 N5/scripts/n5_init.py

# Test 2: Verify structure
ls -la N5/
ls -la N5/config/
ls -la N5/templates/
ls -la N5/scripts/

# Test 3: Check .gitignore
cat .gitignore

# Test 4: Verify config/ is ignored
git status  # (if initialized - we'll do this in Phase 0.2)
```

---

## Principles to Apply

- **P7 (Dry-Run)**: Include `--dry-run` flag
- **P11 (Failure Modes)**: Log clear errors if templates missing
- **P15 (Complete Before Claiming)**: Test all paths before saying "done"
- **P18 (Verify State)**: Check that dirs exist after creation
- **P19 (Error Handling)**: Try/except with informative messages

---

## What Comes Next

**Phase 0.2**: Extract rules template from Main → transport to vademonstrator

You're just building the **container** now. Content comes next.

---

## Non-Goals (Don't Do These)

- ❌ Don't create templates yet (Phase 0.2)
- ❌ Don't implement rules or schedules (Phase 0.2-0.3)
- ❌ Don't set up GitHub integration yet (Phase 0.4)
- ❌ Don't build config UI or complex logic

---

## How to Execute

1. **Switch to vademonstrator.zo.computer** in your browser
2. **Create directory structure** with mkdir commands
3. **Write n5_init.py** using `create_or_rewrite_file`
4. **Write .gitignore** using `create_or_rewrite_file`
5. **Test the script** with `run_bash_command`
6. **Document** what you built in `/docs/phase0_setup.md`
7. **Report back** to V with test results

---

## Questions Before Starting?

If anything is unclear, ask V in the planning thread (con_HuaTrPlhVJRg9c9m) before proceeding.

Otherwise: **Load the spec, load the detailed plan, and execute Phase 0.1.**

---

**Status**: Ready to Execute  
**Assigned to**: Orchestrator Thread 1  
**Created**: 2025-10-28 00:16 ET

---

## Quick Reference

| Key | Value |
|-----|-------|
| Main System | va.zo.computer |
| Demonstrator | vademonstrator.zo.computer |
| Planning Thread | con_HuaTrPlhVJRg9c9m (on Main) |
| GitHub Repo | vattawar/zo-n5os-core |
| Phase | 0.1 |
| Duration | 1-2 hours |
