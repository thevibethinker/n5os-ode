# Export to N5 OS Core
**Purpose**: Sync V's N5 changes to `n5os-core` GitHub repo for distribution
**Trigger**: Manual command `n5 export-core`
**Version**: 1.0.0

---

## Workflow Steps

### 1. Scan for Changes
Identify modified core components since last export:
- Scripts in `N5/scripts/` (select core-only)
- Prefs in `N5/prefs/`
- Schemas in `N5/schemas/`
- Knowledge in `Knowledge/architectural/`
- Commands docs in `N5/commands/`

### 2. Generify
Transform V-specific → Generic:
- `/home/workspace` → `{WORKSPACE}`
- `/home/workspace/N5` → `{N5_ROOT}`
- `V` / `va` / `Vrijen` → `{USER}`
- `Careerspan` → `{COMPANY}`
- Strip personal examples from prefs

### 3. Copy to n5os-core
```bash
# Core structure
/home/workspace/n5os-core/
├── N5/
│   ├── prefs/         # From N5/prefs/ (core only)
│   ├── scripts/       # From N5/scripts/ (4-6 core scripts)
│   ├── schemas/       # From N5/schemas/
│   └── commands/      # From N5/commands/
├── Knowledge/
│   └── architectural/ # From Knowledge/architectural/
├── Lists/
│   └── POLICY.md      # From Lists/POLICY.md
└── Documents/
    └── System/        # Core docs only
```

### 4. Git Commit & Push
```bash
cd /home/workspace/n5os-core
git add .
git commit -m "Update core from V's N5 - $(date +%Y-%m-%d)"
git push origin main
```

### 5. Update CHANGELOG
Track what changed since last export

---

## Configuration

File: `N5/config/export_core_manifest.yaml`

```yaml
version: "1.0.0"
last_export: "2025-10-27"
destination: "/home/workspace/n5os-core"
github_repo: "https://github.com/vrijenattawar/n5os-core.git"

# What to export
components:
  core_scripts:
    - N5/scripts/session_state_manager.py
    - N5/scripts/n5_index_rebuild.py
    - N5/scripts/n5_safety.py
    - N5/scripts/n5_git_check.py
  
  prefs_core:
    - N5/prefs/prefs.md
    - N5/prefs/system/*.md
    - N5/prefs/operations/*.md
    # NOT: communication, personal, formatting
  
  schemas:
    - N5/schemas/*.json
  
  knowledge:
    - Knowledge/architectural/architectural_principles.md
    - Knowledge/architectural/planning_prompt.md
    - Knowledge/architectural/principles/*.md
  
  docs:
    - Lists/POLICY.md

# Replacements for generification
replacements:
  paths:
    "/home/workspace": "{WORKSPACE}"
    "/home/workspace/N5": "{N5_ROOT}"
    "/home/workspace/N5/data": "{N5_DATA}"
  
  personal:
    "V": "{USER}"
    "va": "{USER_HANDLE}"
    "Vrijen": "{USER_NAME}"
    "Vrijen Attawar": "{USER_FULL_NAME}"
    "Careerspan": "{COMPANY}"
    "va.zo.computer": "{USER_HANDLE}.zo.computer"

# What to exclude
exclude_patterns:
  - "*/personal/*"
  - "*/communication/*"
  - "*_personal.md"
  - "*.backup.*"
  - "*/Temporary/*"
```

---

## Execution Script

See: `N5/scripts/n5_export_core.py`

---

## Safety Checks

Before export:
1. ✅ Verify n5os-core repo exists and is clean
2. ✅ No uncommitted personal changes in n5os-core
3. ✅ Backup current n5os-core state
4. ✅ Dry-run shows changes preview
5. ✅ Confirm generification (no personal data leaked)

---

## Usage

```bash
# 1. Dry run (preview changes)
python3 N5/scripts/n5_export_core.py --dry-run

# 2. Export with review
python3 N5/scripts/n5_export_core.py

# 3. Export + auto-push
python3 N5/scripts/n5_export_core.py --push

# 4. Export specific component
python3 N5/scripts/n5_export_core.py --component session_state_manager
```

---

## Post-Export

After successful export:
1. Update `last_export` timestamp in manifest
2. Log to `N5/logs/export_history.jsonl`
3. Update n5os-core CHANGELOG
4. Tag release if major changes

---

## Future Enhancements

- [ ] Auto-detect changed files (git diff since last export)
- [ ] Version bumping (semantic versioning)
- [ ] Release notes generation
- [ ] CI/CD integration (GitHub Actions)
- [ ] Multi-destination support (forks, mirrors)

---

**Last Updated**: 2025-10-27
