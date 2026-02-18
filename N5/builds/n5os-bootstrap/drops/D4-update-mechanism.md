---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: drop_brief
build_slug: n5os-bootstrap
drop_id: D4
wave: 3
depends_on: [D2, D3]
status: pending
---

# D4: Update Mechanism

**Build:** n5os-bootstrap
**Wave:** 3 (depends on D2, D3)
**Title:** [n5os-bootstrap] D4: Update Mechanism

---

## Objective

Create the update system that pulls new N5OS content from the substrate without breaking local personalization. This enables ongoing evolution — zoputer can receive principle updates, new operational protocols, and enhanced safety rules from va without manual intervention.

---

## Scope

### Files to Create

```
Skills/n5os-bootstrap/
└── scripts/
    └── update.py              # Update script
```

### Files Created at Runtime

```
Skills/n5os-bootstrap/
└── config/
    └── installed.yaml         # Installation state (created on first install)
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
- `Skills/n5os-bootstrap/SKILL.md` (D5's scope)

---

## MUST DO

### 1. Create update.py

**Features:**
- Pull latest payload from substrate (GitHub or direct fetch)
- Compare installed.yaml with incoming versions
- Update payload files without touching personalization
- Support selective updates (--principles, --safety, etc.)
- Re-run personalize.py after update to regenerate templates
- Log all updates

**CLI Interface:**
```bash
python3 update.py [OPTIONS]

Options:
  --source URL       Source URL or path for updates (default: substrate)
  --component NAME   Only update specific component (principles, safety, etc.)
  --dry-run          Show what would be updated without making changes
  --force            Update even if versions match
  --skip-personalize Skip re-personalization after update
  --verbose          Show detailed progress
  --help             Show this help
```

**Exit Codes:**
- 0: Success (updates applied or already up-to-date)
- 1: Error (network failure, invalid source, etc.)
- 2: Partial update (some components failed)

**Update Strategy:**

```
┌─────────────────────────────────────────────────────────────┐
│                     UPDATE FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. Fetch manifest from source                              │
│   2. Compare versions with installed.yaml                    │
│   3. For each outdated component:                            │
│      a. Download new payload files                           │
│      b. Replace payload/ directory content                   │
│      c. Re-run install.py for that component                 │
│   4. Re-run personalize.py with existing config              │
│   5. Update installed.yaml with new versions                 │
│   6. Run verify.py to confirm health                         │
│                                                              │
│   NEVER TOUCH:                                               │
│   - config/instances/*.yaml (user personalization)           │
│   - Generated files in .claude/ (re-generate instead)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Pseudocode:**
```python
def main():
    args = parse_args()
    
    # Load current installation state
    installed = load_installed_yaml()
    if not installed:
        print("Not installed. Run install.py first.")
        return 1
    
    # Fetch remote manifest
    remote_manifest = fetch_manifest(args.source)
    
    # Determine what needs updating
    updates = []
    for component, config in remote_manifest['destinations'].items():
        if args.component and args.component != component:
            continue
        
        local_version = installed['components'].get(component, {}).get('version', '0.0.0')
        remote_version = config.get('version', '1.0.0')
        
        if version_gt(remote_version, local_version) or args.force:
            updates.append({
                'component': component,
                'from_version': local_version,
                'to_version': remote_version,
                'config': config
            })
    
    if not updates:
        print("Already up to date.")
        return 0
    
    # Show what will be updated
    print(f"Updates available: {len(updates)} components")
    for u in updates:
        print(f"  - {u['component']}: {u['from_version']} → {u['to_version']}")
    
    if args.dry_run:
        return 0
    
    # Apply updates
    for update in updates:
        apply_update(update, dry_run=args.dry_run)
        installed['components'][update['component']]['version'] = update['to_version']
    
    # Save updated installation state
    save_installed_yaml(installed)
    
    # Re-personalize
    if not args.skip_personalize:
        config_file = installed.get('personalization')
        if config_file:
            run_personalize(config_file)
    
    # Verify
    verify_result = run_verify()
    if verify_result != 0:
        print("Warning: Verification failed after update")
        return 2
    
    print(f"Updated {len(updates)} components successfully")
    return 0

def fetch_manifest(source):
    """Fetch manifest from substrate or local path."""
    if source.startswith('http'):
        # Fetch from GitHub raw content
        response = urllib.request.urlopen(source)
        return yaml.safe_load(response.read())
    else:
        # Local path
        return load_yaml(Path(source) / 'config' / 'manifest.yaml')

def apply_update(update, dry_run=False):
    """Download and apply a component update."""
    component = update['component']
    config = update['config']
    
    # Fetch new payload files
    source_url = f"{SUBSTRATE_URL}/payload/{component}/"
    target_dir = SKILL_ROOT / 'payload' / component
    
    # Download files (implementation depends on substrate structure)
    download_directory(source_url, target_dir, dry_run=dry_run)
    
    # Re-run install for this component only
    install_component(component, config, dry_run=dry_run)
```

### 2. Define installed.yaml Schema

This file is created by install.py after first installation and updated by update.py:

```yaml
# Auto-generated by n5os-bootstrap install/update
# Do not edit manually

installed_at: "2026-02-13T03:00:00Z"
updated_at: "2026-02-13T03:00:00Z"
version: "1.0.0"
personalization: "instances/zoputer.yaml"

components:
  principles:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - Personal/Knowledge/Architecture/principles/architectural_principles.md
      - Personal/Knowledge/Architecture/principles/P24-simulation-over-doing.md
      # ... etc
      
  safety:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - N5/prefs/system/safety.md
      - N5/prefs/system/file-protection.md
      # ... etc
      
  operations:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - N5/prefs/operations/planning_prompt.md
      # ... etc
      
  personas:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - Documents/System/personas/INDEX.md
      # ... etc
      
  workflows:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - N5/prefs/workflows/debugger_workflow.md
      # ... etc
      
  voice:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - N5/prefs/voice/anti-patterns.md
      
  state:
    version: "1.0.0"
    installed_at: "2026-02-13T03:00:00Z"
    files:
      - .claude/templates/SESSION_STATE.template.md
```

### 3. Substrate Integration

The update mechanism needs to know where to fetch updates from. Default substrate URL:

```python
SUBSTRATE_URL = "https://raw.githubusercontent.com/vrijenattawar/zoputer-substrate/main/Skills/n5os-bootstrap"
```

This requires:
- n5os-bootstrap being pushed to the substrate repo (D5 handles this)
- Manifest includes version numbers for each component
- Update script can fetch individual files or directories

---

## MUST NOT DO

- Do NOT modify personalization configs — user owns those
- Do NOT delete local customizations
- Do NOT update if install hasn't been run
- Do NOT use external dependencies beyond Python stdlib + PyYAML
- Do NOT implement substrate push logic — that's a separate concern

---

## Expected Output

### Deposit Structure

```yaml
drop_id: D4
status: complete
files_created:
  - Skills/n5os-bootstrap/scripts/update.py
total_files: 1
test_results:
  dry_run: "Shows available updates"
  update: "Updates payload and re-personalizes"
  selective: "--component principles updates only principles"
```

### Verification Commands

```bash
# Test dry run
python3 Skills/n5os-bootstrap/scripts/update.py --dry-run

# Test selective update
python3 Skills/n5os-bootstrap/scripts/update.py --component principles --dry-run

# Test full update (on test workspace)
python3 Skills/n5os-bootstrap/scripts/update.py --verbose
```

---

## Context Files to Read

1. `file 'Skills/n5os-bootstrap/scripts/install.py'` — Understand install flow (D2 output)
2. `file 'Skills/n5os-bootstrap/scripts/personalize.py'` — Understand personalization (D3 output)
3. `file 'Skills/n5os-bootstrap/config/manifest.yaml'` — Component structure (D2 output)

---

## Build Lesson Ledger

Check ledger: `python3 Skills/pulse/scripts/pulse_learnings.py read n5os-bootstrap`
Log lessons: `python3 Skills/pulse/scripts/pulse_learnings.py add n5os-bootstrap "lesson" --source D4`
