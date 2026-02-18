---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: drop_brief
build_slug: n5os-bootstrap
drop_id: D2
wave: 2
depends_on: [D1]
status: pending
---

# D2: Bootloader Core

**Build:** n5os-bootstrap
**Wave:** 2 (depends on D1)
**Title:** [n5os-bootstrap] D2: Bootloader Core

---

## Objective

Create the core installation scripts that unpack payload content into the target workspace structure. This is the "bootloader" — the executable that transforms the skill into actual infrastructure.

---

## Scope

### Files to Create

```
Skills/n5os-bootstrap/
├── config/
│   └── manifest.yaml         # Installation manifest
├── scripts/
│   ├── install.py            # Main bootloader
│   └── verify.py             # Health check
```

### Must NOT Touch

- `Skills/n5os-bootstrap/payload/` (D1's scope, read-only for D2)
- `Skills/n5os-bootstrap/config/defaults.yaml` (D3's scope)
- `Skills/n5os-bootstrap/config/instances/` (D3's scope)
- `Skills/n5os-bootstrap/templates/` (D3's scope)
- `Skills/n5os-bootstrap/scripts/personalize.py` (D3's scope)
- `Skills/n5os-bootstrap/scripts/update.py` (D4's scope)
- `Skills/n5os-bootstrap/SKILL.md` (D5's scope)

---

## MUST DO

### 1. Create manifest.yaml

```yaml
version: 1
name: n5os-bootstrap
description: N5OS philosophy and infrastructure bootstrap

destinations:
  principles:
    source: payload/principles/
    target: Personal/Knowledge/Architecture/principles/
    mode: merge
    
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
  - N5/logs
```

### 2. Create install.py

**Features:**
- Parse manifest.yaml
- Create required directories
- Copy payload files to destinations
- Handle conflicts (skip, overwrite, or abort based on flags)
- Call personalize.py if config provided
- Log all actions

**CLI Interface:**
```bash
python3 install.py [OPTIONS]

Options:
  --config PATH      Instance config file (e.g., instances/zoputer.yaml)
  --dry-run          Show what would be installed without making changes
  --force            Overwrite existing files without prompting
  --verbose          Show detailed progress
  --skip-personalize Skip personalization step
  --help             Show this help
```

**Exit Codes:**
- 0: Success
- 1: Error (missing files, permission denied, etc.)
- 2: Conflicts detected (use --force to override)

**Pseudocode:**
```python
def main():
    args = parse_args()
    manifest = load_manifest()
    
    # Create required directories
    for dir in manifest['required_dirs']:
        ensure_dir(dir, dry_run=args.dry_run)
    
    # Process each destination
    conflicts = []
    for name, dest_config in manifest['destinations'].items():
        source_dir = SKILL_ROOT / dest_config['source']
        target_dir = Path(dest_config['target'])
        
        for source_file in source_dir.glob('**/*.md'):
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            if target_file.exists() and not args.force:
                conflicts.append(target_file)
                continue
            
            copy_file(source_file, target_file, dry_run=args.dry_run)
    
    if conflicts and not args.force:
        print(f"Conflicts: {len(conflicts)} files exist. Use --force to overwrite.")
        return 2
    
    # Run personalization if config provided
    if args.config and not args.skip_personalize:
        run_personalize(args.config, dry_run=args.dry_run)
    
    # Log installation
    log_install(manifest, args)
    
    return 0
```

### 3. Create verify.py

**Features:**
- Check all expected files exist based on manifest
- Validate files are non-empty
- Check for placeholder markers that should have been replaced
- Report health status

**CLI Interface:**
```bash
python3 verify.py [OPTIONS]

Options:
  --verbose    Show all checks, not just failures
  --help       Show this help
```

**Exit Codes:**
- 0: All checks passed
- 1: Some checks failed

**Output Format:**
```
N5OS Bootstrap Health Check
===========================
✓ principles/architectural_principles.md exists
✓ principles/P24-simulation-over-doing.md exists
...
✗ safety/safety.md missing
✗ Found unreplaced placeholder: {{WORKSPACE}}

Summary: 35/38 checks passed
Status: UNHEALTHY
```

---

## MUST NOT DO

- Do NOT create personalization logic — that's D3
- Do NOT create update logic — that's D4
- Do NOT modify payload files — D1 already created them
- Do NOT implement template rendering — D3 handles that
- Do NOT use external dependencies (stick to Python stdlib)

---

## Expected Output

### Deposit Structure

```yaml
drop_id: D2
status: complete
files_created:
  - Skills/n5os-bootstrap/config/manifest.yaml
  - Skills/n5os-bootstrap/scripts/install.py
  - Skills/n5os-bootstrap/scripts/verify.py
total_files: 3
test_results:
  dry_run: "Shows 38 files would be installed"
  force_install: "Completes without error"
  verify: "All checks pass on fresh install"
```

### Verification Commands

```bash
# Test dry run
python3 Skills/n5os-bootstrap/scripts/install.py --dry-run

# Test install (on test workspace)
python3 Skills/n5os-bootstrap/scripts/install.py --force --verbose

# Verify installation
python3 Skills/n5os-bootstrap/scripts/verify.py --verbose
```

---

## Context Files to Read

1. `file 'Skills/n5os-bootstrap/config/manifest.yaml'` — After creating, verify structure
2. `file 'N5/builds/n5os-bootstrap/PLAN.md'` — Full plan context

---

## Build Lesson Ledger

Check ledger: `python3 Skills/pulse/scripts/pulse_learnings.py read n5os-bootstrap`
Log lessons: `python3 Skills/pulse/scripts/pulse_learnings.py add n5os-bootstrap "lesson" --source D2`
