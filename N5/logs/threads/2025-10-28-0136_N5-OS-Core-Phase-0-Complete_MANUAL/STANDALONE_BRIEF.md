# N5 OS Core - Phase 0.1 Build Instructions

**Project**: N5 OS (Cesc v0.1)  
**GitHub**: https://github.com/vattawar/zo-n5os-core  
**License**: MIT  
**This Document**: Self-contained instructions for Phase 0.1

**Persona**: Load Vibe Builder Bootstrap v2.0 (if available) for optimal execution

---

## Mission: Build Foundation Structure

Create the directory skeleton and initialization system for N5 OS Core.

**Time**: 1-2 hours  
**Environment**: vademonstrator.zo.computer

---

## What to Build

### 1. Directory Structure

```bash
/home/workspace/
├── N5/
│   ├── templates/          # Config templates (will come from GitHub)
│   ├── config/             # User-generated configs (git ignored)
│   ├── scripts/            # System scripts
│   └── data/               # System data (bulletins, db, etc.)
├── docs/                   # Documentation
│   └── phase0_setup.md     # What you built
└── .gitignore             # Git ignore rules
```

### 2. Initialization Script: `/N5/scripts/n5_init.py`

**Purpose**: Generate user configs from templates on first run

**Full Implementation**:

```python
#!/usr/bin/env python3
"""
N5 OS Initialization Script
Generates user configs from templates if they don't exist
"""
import argparse
import logging
from pathlib import Path

# Paths
WORKSPACE = Path("/home/workspace")
N5_DIR = WORKSPACE / "N5"
TEMPLATE_DIR = N5_DIR / "templates"
CONFIG_DIR = N5_DIR / "config"
DATA_DIR = N5_DIR / "data"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def ensure_directories():
    """Create required directories if they don't exist"""
    dirs = [N5_DIR, TEMPLATE_DIR, CONFIG_DIR, DATA_DIR]
    for d in dirs:
        if not d.exists():
            logger.info(f"Creating directory: {d}")
            d.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"✓ Directory exists: {d}")


def check_config(template_name: str, dry_run: bool = False) -> bool:
    """
    Check if config exists; if not, generate from template
    
    Args:
        template_name: Name without extension (e.g., 'rules')
        dry_run: If True, only report what would happen
        
    Returns:
        True if config exists or was created, False on error
    """
    template = TEMPLATE_DIR / f"{template_name}.template.md"
    config = CONFIG_DIR / f"{template_name}.md"
    
    if config.exists():
        logger.info(f"✓ Config exists: {config}")
        return True
    
    if not template.exists():
        logger.warning(f"⚠ Template missing: {template}")
        logger.warning(f"  Config will be generated once template is available")
        return True  # Not an error, just not ready yet
    
    if dry_run:
        logger.info(f"[DRY RUN] Would generate {config.name} from {template.name}")
        return True
    
    try:
        logger.info(f"Generating {config.name} from template...")
        content = template.read_text()
        config.write_text(content)
        logger.info(f"✓ Created {config}")
        return True
    except Exception as e:
        logger.error(f"Failed to create {config}: {e}")
        return False


def main(dry_run: bool = False) -> int:
    """
    Main initialization logic
    
    Returns:
        0 on success, 1 on error
    """
    try:
        logger.info("=== N5 OS Initialization ===")
        
        # Ensure directory structure
        ensure_directories()
        
        # Check/generate configs
        configs = ["rules", "prefs"]
        success = True
        
        for cfg in configs:
            if not check_config(cfg, dry_run=dry_run):
                success = False
        
        if success:
            logger.info("\n✓ N5 initialization complete")
            return 0
        else:
            logger.error("\n✗ Initialization completed with errors")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error during initialization: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize N5 OS configuration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
```

### 3. Git Ignore: `/.gitignore`

```gitignore
# User-generated configs (never commit - users customize these)
/N5/config/

# System data (user-specific)
/N5/data/

# Python
__pycache__/
*.pyc
*.pyo

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# User workspaces (don't commit user's personal files)
/Knowledge/
/Lists/
/Records/
/Documents/
```

### 4. Documentation: `/docs/phase0_setup.md`

```markdown
# Phase 0 Setup Documentation

**Phase**: 0.1 - Foundation Structure  
**Date**: 2025-10-28  
**Status**: Complete

---

## What Was Built

### Directory Structure
- `/N5/` - Core system directory
  - `/templates/` - Config templates (from GitHub)
  - `/config/` - User configs (git ignored)
  - `/scripts/` - System scripts
  - `/data/` - System data

### Initialization Script
- `/N5/scripts/n5_init.py` - Generates configs from templates
- Supports `--dry-run` flag
- Creates directories automatically
- Logs all actions with timestamps

### Git Configuration
- `.gitignore` prevents committing user-specific files
- Templates are tracked, configs are not

---

## How to Use

### First Time Setup
```bash
# Run initialization
python3 /home/workspace/N5/scripts/n5_init.py

# Check what was created
ls -la /home/workspace/N5/config/
```

### Dry Run (Preview)
```bash
python3 /home/workspace/N5/scripts/n5_init.py --dry-run
```

---

## Testing Performed

- [x] Script creates directories
- [x] Script handles missing templates gracefully
- [x] Dry-run mode works
- [x] Error handling logs helpful messages
- [x] .gitignore configured correctly

---

## Next Steps

Phase 0.2 will create the actual template files and transport them from Main system.
```

---

## Execution Steps

### Step 1: Create Directories
```bash
cd /home/workspace
mkdir -p N5/templates N5/config N5/scripts N5/data docs
```

### Step 2: Create n5_init.py
Use `create_or_rewrite_file` tool with the Python code above.

### Step 3: Create .gitignore
Use `create_or_rewrite_file` tool with the gitignore content above.

### Step 4: Create Documentation
Use `create_or_rewrite_file` tool with the docs/phase0_setup.md content above.

### Step 5: Test
```bash
# Test 1: Dry run
python3 N5/scripts/n5_init.py --dry-run

# Test 2: Real run
python3 N5/scripts/n5_init.py

# Test 3: Verify structure
ls -la N5/
ls -la N5/config/
ls -la N5/templates/

# Test 4: Run again (should be idempotent)
python3 N5/scripts/n5_init.py
```

---

## Success Criteria

- [ ] All directories created
- [ ] n5_init.py runs without errors
- [ ] Script is idempotent (can run multiple times safely)
- [ ] Dry-run mode works
- [ ] .gitignore exists
- [ ] Documentation complete
- [ ] All tests pass

---

## Principles Applied

- **P7 (Dry-Run)**: `--dry-run` flag implemented
- **P11 (Failure Modes)**: Graceful handling of missing templates
- **P15 (Complete Before Claiming)**: All tests must pass
- **P18 (Verify State)**: Checks directory existence
- **P19 (Error Handling)**: Try/except with logging

---

## What This Enables

Phase 0.1 creates the **container**. Subsequent phases will fill it:
- **Phase 0.2**: Rules template
- **Phase 0.3**: Scheduled tasks (cleanup, self-description)
- **Phase 0.4**: GitHub integration

---

**Status**: Ready to Build  
**Created**: 2025-10-28 00:20 ET
