---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: ready
provenance: con_bU6QDWx22wZGHG1Z
---

# Plan: N5OS Ode UX Hardening

**Objective:** Transform N5OS Ode install from a confusing multi-step process into a bulletproof, single-command experience with version control, rollback, progress tracking, and modular architecture.

**Trigger:** Real-world testing revealed friction points — files landing in subdirectories, no progress feedback, no way to recover from failed installs, monolithic bootloader.

---

## Open Questions

- [x] Should personas be in separate YAML files or markdown? → **Markdown** (readable, editable)
- [x] How to handle `create_persona` API? → Bootloader still creates them, but reads from modular files
- [x] Rollback: delete everything or restore backup? → **Backup-based** (safer)

---

## Checklist

### Phase 1: Foundation (Quick Install + Version + Progress)
- ☐ Create `VERSION` file with semantic version
- ☐ Create `quick-install.sh` — single curl command
- ☐ Create `SETUP_PROGRESS.md` — tracks discrete milestones
- ☐ Update `install.sh` to initialize progress file
- ☐ Test: `curl | bash` works on fresh workspace

### Phase 2: Modular Personas + Order of Operations
- ☐ Create `N5/personas/` directory with 6 persona files
- ☐ Create `INSTALL_ORDER.md` — canonical sequence
- ☐ Update BOOTLOADER to read personas from files
- ☐ Reduce BOOTLOADER from 1000+ lines to ~300
- ☐ Test: Bootloader creates personas from modular files

### Phase 3: Rollback + Idempotency
- ☐ Create `scripts/backup.py` — snapshot before install
- ☐ Create `scripts/rollback.py` — restore from backup
- ☐ Add idempotency checks to all creation steps
- ☐ Update BOOTLOADER with explicit skip messages
- ☐ Test: Run bootloader twice, no duplicates

### Phase 4: Version Migration + Validation
- ☐ Create `scripts/migrate.py` — version upgrade logic
- ☐ Create `scripts/validate_install.py` — post-install health check
- ☐ Add version check at bootloader start
- ☐ Test: Upgrade from v1.0 to v1.1

---

## Phase 1: Foundation (Quick Install + Version + Progress)

### Affected Files
- `VERSION` - CREATE - Semantic version string
- `quick-install.sh` - CREATE - One-liner install script
- `SETUP_PROGRESS.md` - CREATE - Progress tracking template
- `install.sh` - UPDATE - Initialize progress file
- `README.md` - UPDATE - Add curl install instructions

### Changes

**1.1 VERSION file:**
```
1.2.0
```
Simple text file, read by scripts for version checking.

**1.2 quick-install.sh:**
```bash
#!/bin/bash
# N5OS Ode Quick Installer
# Usage: curl -sL https://raw.githubusercontent.com/vrijenattawar/n5os-ode/main/quick-install.sh | bash

set -e
cd /home/workspace

echo "🚀 N5OS Ode Quick Install"
echo "========================="

# Clone to temp location
git clone --depth 1 https://github.com/vrijenattawar/n5os-ode.git .n5os-ode-temp

# Run the real installer
cd .n5os-ode-temp
bash install.sh

echo ""
echo "✅ Files installed to workspace root"
echo ""
echo "Next: Open a new Zo conversation and run:"
echo "  @BOOTLOADER.prompt.md"
```

**1.3 SETUP_PROGRESS.md:**
```markdown
# N5OS Ode Setup Progress

Track your installation progress. Each step updates automatically.

## Milestones

| Step | Status | Completed |
|------|--------|-----------|
| 1. Files Installed | ⬜ Pending | — |
| 2. Personas Created | ⬜ Pending | — |
| 3. Rules Installed | ⬜ Pending | — |
| 4. Folders Created | ⬜ Pending | — |
| 5. Databases Initialized | ⬜ Pending | — |
| 6. Git Configured | ⬜ Pending | — |
| 7. Personalized | ⬜ Pending | — |

## Current Step

**Next Action:** Run `@BOOTLOADER.prompt.md`

## Version

Installed: [VERSION]
```

**1.4 Update install.sh:**
- After moving files, create `SETUP_PROGRESS.md` from template
- Mark "Files Installed" as ✅ Complete
- Update "Next Action" to point to BOOTLOADER

### Unit Tests
- `curl -sL ... | bash` on fresh workspace → files at root
- `SETUP_PROGRESS.md` exists with Step 1 marked complete
- `VERSION` file readable

---

## Phase 2: Modular Personas + Order of Operations

### Affected Files
- `N5/personas/operator.md` - CREATE - Ode Operator persona
- `N5/personas/builder.md` - CREATE - Ode Builder persona
- `N5/personas/researcher.md` - CREATE - Ode Researcher persona
- `N5/personas/writer.md` - CREATE - Ode Writer persona
- `N5/personas/strategist.md` - CREATE - Ode Strategist persona
- `N5/personas/debugger.md` - CREATE - Ode Debugger persona
- `INSTALL_ORDER.md` - CREATE - Canonical install sequence
- `BOOTLOADER.prompt.md` - UPDATE - Read from modular files

### Changes

**2.1 Persona file format (example: operator.md):**
```yaml
---
name: Ode Operator
version: "1.0"
domain: Navigation, routing, execution, state management
---

## Core Identity

You are the home persona for N5OS Ode...
[rest of persona prompt]
```

**2.2 INSTALL_ORDER.md:**
```markdown
# N5OS Ode Installation Order

Follow these steps IN ORDER for a complete installation.

## Order of Operations

### 1. Quick Install (Terminal)
```bash
curl -sL https://raw.githubusercontent.com/vrijenattawar/n5os-ode/main/quick-install.sh | bash
```
✅ Installs files to workspace root

### 2. Run Bootloader (Zo Conversation)
```
@BOOTLOADER.prompt.md
```
✅ Creates personas, rules, folders, databases

### 3. Personalize (Zo Conversation)
```
@PERSONALIZE.prompt.md
```
✅ Configures your name, timezone, preferences

### 4. Verify (Zo Conversation)
```
@VALIDATE.prompt.md
```
✅ Confirms everything is working

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for common issues.
```

**2.3 Slim BOOTLOADER:**
- Remove inline persona prompts (900+ lines)
- Add: "Read persona from `N5/personas/{name}.md`"
- Add: "Create persona using content from file"
- Keep: Rules, folder creation, DB init inline (they're short)

### Unit Tests
- Each persona file is valid markdown with YAML frontmatter
- BOOTLOADER creates all 6 personas from files
- BOOTLOADER is <400 lines

---

## Phase 3: Rollback + Idempotency

### Affected Files
- `N5/scripts/backup.py` - CREATE - Pre-install snapshot
- `N5/scripts/rollback.py` - CREATE - Restore from snapshot
- `BOOTLOADER.prompt.md` - UPDATE - Add idempotency checks

### Changes

**3.1 backup.py:**
```python
# Creates .n5os-backup-{timestamp}/ with:
# - N5/ (if exists)
# - Prompts/ (if exists)
# - Knowledge/ (if exists)
# - prefs backup
# Stores manifest of what was backed up
```

**3.2 rollback.py:**
```python
# Lists available backups
# Restores selected backup
# Removes N5OS Ode files added since backup
```

**3.3 Idempotency in BOOTLOADER:**
```
Before creating persona "Ode Operator":
  1. Check if persona with name "Ode Operator" exists
  2. If exists: Print "⏭ Skipping Ode Operator (already exists)"
  3. If not: Create persona, print "✅ Created Ode Operator"
```

Same pattern for rules, folders, files.

### Unit Tests
- Run bootloader twice → no duplicate personas
- Run bootloader twice → no errors
- backup.py creates valid backup
- rollback.py restores correctly

---

## Phase 4: Version Migration + Validation

### Affected Files
- `N5/scripts/migrate.py` - CREATE - Version upgrade handler
- `N5/scripts/validate_install.py` - CREATE - Health check
- `VALIDATE.prompt.md` - CREATE - User-facing validation prompt
- `BOOTLOADER.prompt.md` - UPDATE - Version check at start

### Changes

**4.1 migrate.py:**
```python
# Reads current VERSION from installed system
# Reads target VERSION from repo
# Applies migrations:
#   1.0 → 1.1: Add conversations.db
#   1.1 → 1.2: Add modular personas
# Updates VERSION file
```

**4.2 validate_install.py:**
```python
# Checks:
# - All 6 personas exist
# - All 6 rules exist
# - Required folders exist
# - Required files exist
# - DBs initialized
# - VERSION matches expected
# Returns: PASS/FAIL with details
```

**4.3 VALIDATE.prompt.md:**
```markdown
Run validation to confirm N5OS Ode is properly installed.

Execute: python3 N5/scripts/validate_install.py

Report results and suggest fixes for any failures.
```

**4.4 Version check in BOOTLOADER:**
```
At start of BOOTLOADER:
1. Read VERSION file
2. Compare to expected version
3. If mismatch: "⚠️ Version mismatch. Run migration first."
4. If match: Continue with install
```

### Unit Tests
- validate_install.py reports PASS on good install
- validate_install.py reports FAIL with specifics on bad install
- migrate.py upgrades 1.1 → 1.2 correctly

---

## Worker Briefs

| Wave | Worker | Title | Scope |
|------|--------|-------|-------|
| 1 | W1.1 | Foundation | VERSION, quick-install.sh, SETUP_PROGRESS.md, install.sh update |
| 1 | W1.2 | Modular Personas | N5/personas/*.md (6 files), INSTALL_ORDER.md |
| 2 | W2.1 | Rollback + Idempotency | backup.py, rollback.py, BOOTLOADER idempotency |
| 2 | W2.2 | Version + Validation | migrate.py, validate_install.py, VALIDATE.prompt.md, BOOTLOADER version check |

Wave 2 depends on Wave 1 (needs modular structure in place).

---

## Success Criteria

1. **One-liner install works:** `curl -sL ... | bash` → files at workspace root
2. **Progress is visible:** SETUP_PROGRESS.md shows clear milestones
3. **Order is clear:** INSTALL_ORDER.md provides unambiguous sequence
4. **Idempotent:** Running bootloader twice causes no issues
5. **Rollback works:** Can restore to pre-install state
6. **Version tracked:** VERSION file exists, checked on boot
7. **Bootloader slim:** <400 lines (down from 1000+)
8. **Validation exists:** User can verify install succeeded

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Persona files not found | BOOTLOADER checks file exists, provides clear error |
| Backup too large | Exclude node_modules, .git, large binaries |
| Migration breaks existing setup | Backup required before migration |
| curl blocked by firewall | Document manual install alternative |

---

## Level Upper Review

### Incorporated:
- Single command install (quick-install.sh)
- Progress indicator (SETUP_PROGRESS.md with discrete milestones)
- Version file
- Modular personas (separate files)
- Rollback mechanism
- Idempotency checks

### Rejected:
- Full programmatic bootloader (keeping LLM-based for semantic flexibility)
- Batched rule creation (API doesn't support it cleanly)

---

## Trap Doors (Irreversible Decisions)

⚠️ **Persona file format:** Once users have custom personas, changing format is breaking
→ Use standard YAML frontmatter + markdown body (widely compatible)

⚠️ **VERSION scheme:** Once released, can't change versioning approach
→ Use semantic versioning (X.Y.Z) from start

