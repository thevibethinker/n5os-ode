---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kE0s6aLxJ7hyK6fb
build_slug: n5os-ode-v2
---

# Build Plan: N5OS-Ode v2 — Meeting Ingestion + Pulse Systems

## Purpose
Add Meeting Ingestion and Pulse Build Orchestration systems to the public n5os-ode repository, enabling other Zo users to process meeting transcripts and run automated multi-worker builds.

## Open Questions
- [RESOLVED] CRM sync: **Strip entirely** (per V)
- [RESOLVED] B40-B48 internal blocks: **Create placeholders** (per V)
- [RESOLVED] Config approach: **Template files with README** (per V)

## Checklist

### Stream 1: Meeting System
- [ ] D1.1: Create `meeting_config.py` central config module
- [ ] D1.2: Update 9 meeting scripts to use config module
- [ ] D1.3: Sanitize meeting-ingestion skill (remove CRM)
- [ ] D1.4: Create B40-B48 placeholder prompts
- [ ] D1.5: Create docs/MEETING_INGESTION.md

### Stream 2: Pulse System
- [ ] D2.1: Update `pulse_common.py` with WORKSPACE env var
- [ ] D2.2: Update all Pulse scripts to use pulse_common paths
- [ ] D2.3: Create docs/PULSE.md

### Stream 3: Integration & Packaging
- [ ] D3.1: Create config templates + README
- [ ] D3.2: Update install.sh for Skills folder
- [ ] D3.3: Update main README.md
- [ ] D3.4: Validate fresh install (dry run)

## Success Criteria
1. All scripts use env-var-based paths (no hardcoded `/home/workspace`)
2. No personal data or CRM references
3. Fresh `install.sh` run creates working system
4. Meeting pull + process works on new Zo
5. Pulse build init works on new Zo

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Path changes break imports | D1.1 and D2.1 create config modules FIRST |
| Missing dependencies | Document in install.sh |
| Skill folder conflicts | Check-and-create pattern in install.sh |

---

# Drop Briefs

## Stream 1: Meeting System

### D1.1 — Create Meeting Config Module
**Type:** code_build  
**Estimated tokens:** 15% context

#### Scope
```yaml
files:
  - N5/scripts/meeting_config.py (CREATE)
responsibilities:
  - Central config module for all meeting scripts
  - Environment variable support with sensible defaults
must_not_touch:
  - Any other meeting scripts (D1.2's job)
  - Skills/meeting-ingestion/ (D1.3's job)
```

#### MUST DO
1. Create `N5/scripts/meeting_config.py` with:
   ```python
   import os
   from pathlib import Path
   
   WORKSPACE = Path(os.environ.get("ZO_WORKSPACE", "/home/workspace"))
   MEETINGS_DIR = Path(os.environ.get("MEETINGS_DIR", WORKSPACE / "Personal/Meetings"))
   STAGING_DIR = MEETINGS_DIR / "Inbox"
   LOG_DIR = WORKSPACE / "N5/logs"
   REGISTRY_DB = WORKSPACE / "N5/data/meeting_registry.db"
   TIMEZONE = os.environ.get("TIMEZONE", "UTC")
   ENABLE_SMS = os.environ.get("ENABLE_SMS_ALERTS", "false").lower() == "true"
   ```
2. Include docstring explaining each variable
3. Test import works: `python3 -c "from N5.scripts.meeting_config import *; print(WORKSPACE)"`

#### MUST NOT DO
- Modify any other files
- Add complex logic — this is pure configuration

#### EXPECTED OUTPUT
- `N5/scripts/meeting_config.py` created
- Import test passes

---

### D1.2 — Update Meeting Scripts to Use Config
**Type:** code_build  
**Estimated tokens:** 35% context

#### Scope
```yaml
files:
  - N5/scripts/meeting_registry.py
  - N5/scripts/meeting_orchestrator.py
  - N5/scripts/meeting_state_manager.py
  - N5/scripts/meeting_weekly_organizer.py
  - N5/scripts/meeting_api_integrator.py
  - N5/scripts/meeting_auto_monitor.py
  - N5/scripts/meeting_monitor.py
  - N5/scripts/meeting_transcript_watcher.py
  - N5/scripts/meeting_normalizer.py (verify only)
  - N5/scripts/meeting_manifest_generator.py (verify only)
responsibilities:
  - Replace hardcoded paths with config imports
  - Replace hardcoded timezones with config
  - Remove/disable SMS functionality (make conditional)
must_not_touch:
  - meeting_config.py (D1.1's output)
  - meeting_crm_sync.py (excluded from export)
  - meeting_gdrive_id_backfill.py (excluded)
  - Skills/meeting-ingestion/ (D1.3's job)
```

#### MUST DO
1. Add to each script: `from N5.scripts.meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS`
2. Replace all `/home/workspace` hardcoded paths
3. Replace `"America/New_York"` or similar with `TIMEZONE`
4. Wrap any SMS sending in `if ENABLE_SMS:`
5. Test each script imports successfully

#### MUST NOT DO
- Change business logic
- Remove SMS code entirely (just make conditional)
- Touch the two excluded scripts

#### EXPECTED OUTPUT
- 8 scripts updated
- 2 scripts verified (already portable)
- All scripts import without error

---

### D1.3 — Sanitize Meeting Ingestion Skill
**Type:** code_build  
**Estimated tokens:** 25% context

#### Scope
```yaml
files:
  - Skills/meeting-ingestion/SKILL.md
  - Skills/meeting-ingestion/scripts/meeting_cli.py
  - Skills/meeting-ingestion/scripts/processor.py
  - Skills/meeting-ingestion/scripts/pull.py
responsibilities:
  - Remove CRM sync entirely
  - Update paths to use config
  - Update SKILL.md to reflect changes
must_not_touch:
  - N5/scripts/meeting_*.py (D1.2's job)
  - Prompts/Blocks/ (D1.4's job)
```

#### MUST DO
1. In `processor.py`: Remove CRM sync call, add comment: `# CRM sync removed - implement your own integration`
2. In all scripts: Import from `N5.scripts.meeting_config`
3. In `SKILL.md`: Remove CRM references, update documentation
4. Remove `--skip-crm` flag (no longer needed)

#### MUST NOT DO
- Change block generation logic
- Remove the CRM sync script file (it stays in workspace, just not exported)

#### EXPECTED OUTPUT
- 4 files updated
- CRM references removed
- `python3 Skills/meeting-ingestion/scripts/meeting_cli.py --help` works

---

### D1.4 — Create B40-B48 Placeholder Prompts
**Type:** code_build  
**Estimated tokens:** 20% context

#### Scope
```yaml
files:
  - Prompts/Blocks/Generate_B40_INTERNAL_DECISIONS.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B41_TEAM_COORDINATION.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B42_INTERNAL_ACTIONS.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B43_RESOURCE_ALLOCATION.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B44_PROCESS_IMPROVEMENTS.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B45_TEAM_DYNAMICS.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B46_KNOWLEDGE_TRANSFER.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B47_OPEN_DEBATES.prompt.md (CREATE)
  - Prompts/Blocks/Generate_B48_INTERNAL_SYNTHESIS.prompt.md (CREATE)
responsibilities:
  - Create placeholder prompts following existing B01-B35 format
  - Each prompt should be functional but generic
must_not_touch:
  - Existing B01-B35 prompts
```

#### MUST DO
1. Review existing block prompts for format (read B01, B05 for pattern)
2. Create 9 placeholder prompts for internal meetings
3. Each should have: frontmatter, purpose, input format, output format
4. Make them functional (not just "TODO" stubs)

#### MUST NOT DO
- Modify existing prompts
- Make them overly complex

#### EXPECTED OUTPUT
- 9 new prompt files in Prompts/Blocks/

---

### D1.5 — Create Meeting Documentation
**Type:** documentation  
**Estimated tokens:** 15% context

#### Scope
```yaml
files:
  - docs/MEETING_INGESTION.md (CREATE)
responsibilities:
  - Document the meeting ingestion pipeline
  - Environment variables reference
  - Google Drive setup instructions
  - Block types table
must_not_touch:
  - Other docs files
```

#### MUST DO
1. Create comprehensive documentation covering:
   - Overview of the pipeline (Drive → Transcript → Blocks)
   - Environment variables table
   - Google Drive folder setup
   - Block types (B01-B27, B40-B48)
   - Troubleshooting
2. Follow existing docs/ format

#### EXPECTED OUTPUT
- `docs/MEETING_INGESTION.md` created

---

## Stream 2: Pulse System

### D2.1 — Update Pulse Common with Workspace Env Var
**Type:** code_build  
**Estimated tokens:** 15% context

#### Scope
```yaml
files:
  - Skills/pulse/scripts/pulse_common.py
responsibilities:
  - Add ZO_WORKSPACE environment variable support
  - Update all path definitions
must_not_touch:
  - Other Pulse scripts (D2.2's job)
```

#### MUST DO
1. Add at module top:
   ```python
   import os
   WORKSPACE = Path(os.environ.get("ZO_WORKSPACE", "/home/workspace"))
   ```
2. Update PATHS class to use WORKSPACE base
3. Ensure backward compatibility (default still works on Zo)
4. Test: `python3 -c "from Skills.pulse.scripts.pulse_common import PATHS; print(PATHS.workspace)"`

#### MUST NOT DO
- Change any logic
- Touch other scripts

#### EXPECTED OUTPUT
- `pulse_common.py` updated
- Import test passes

---

### D2.2 — Update All Pulse Scripts to Use pulse_common
**Type:** code_build  
**Estimated tokens:** 30% context

#### Scope
```yaml
files:
  - Skills/pulse/scripts/pulse.py
  - Skills/pulse/scripts/pulse_code_validator.py
  - Skills/pulse/scripts/pulse_learnings.py
  - Skills/pulse/scripts/pulse_llm_filter.py
  - Skills/pulse/scripts/pulse_safety.py
  - Skills/pulse/scripts/pulse_file_routing.py
  - Skills/pulse/scripts/pulse_dashboard_sync.py
  - Skills/pulse/scripts/pulse_integration_test.py
  - Skills/pulse/scripts/sentinel.py
responsibilities:
  - Replace hardcoded paths with pulse_common imports
  - Remove sys.path hacks where possible
must_not_touch:
  - pulse_common.py (D2.1's output)
  - Skills/pulse/SKILL.md (just scripts)
```

#### MUST DO
1. In each script, replace hardcoded paths with:
   ```python
   from pulse_common import PATHS, WORKSPACE
   ```
2. Remove `sys.path.insert(0, "/home/workspace")` lines
3. Replace `/home/workspace` strings with `str(PATHS.workspace)`
4. Test each script imports without error

#### MUST NOT DO
- Change business logic
- Modify pulse_common.py

#### EXPECTED OUTPUT
- 9 scripts updated
- All scripts import without error

---

### D2.3 — Create Pulse Documentation
**Type:** documentation  
**Estimated tokens:** 15% context

#### Scope
```yaml
files:
  - docs/PULSE.md (CREATE)
responsibilities:
  - Document Pulse build orchestration system
  - Terminology (Drop, Stream, Current, Deposit)
  - Getting started guide
  - Commands reference
must_not_touch:
  - Other docs files
  - Skills/pulse/SKILL.md (that's the internal skill doc)
```

#### MUST DO
1. Create documentation covering:
   - What is Pulse (build orchestration)
   - Terminology glossary
   - Quick start guide
   - Commands reference
   - Creating a build
   - Environment variables
2. Keep it user-facing (not internal implementation)

#### EXPECTED OUTPUT
- `docs/PULSE.md` created

---

## Stream 3: Integration & Packaging

### D3.1 — Create Config Templates
**Type:** code_build  
**Estimated tokens:** 10% context

#### Scope
```yaml
files:
  - N5/config/drive_locations.yaml.template (CREATE)
  - N5/config/README.md (CREATE or UPDATE)
responsibilities:
  - Template config files with placeholders
  - README explaining each config
must_not_touch:
  - Actual config files (those stay local)
```

#### MUST DO
1. Create `drive_locations.yaml.template`:
   ```yaml
   # Meeting Ingestion - Google Drive Configuration
   # Copy to drive_locations.yaml and fill in your folder IDs
   
   meeting_transcripts:
     folder_id: "YOUR_GOOGLE_DRIVE_FOLDER_ID"
     name: "Meeting Transcripts"
   ```
2. Create/update `N5/config/README.md` explaining configs

#### EXPECTED OUTPUT
- Template file created
- README explains setup

---

### D3.2 — Update Install Script
**Type:** code_build  
**Estimated tokens:** 15% context

#### Scope
```yaml
files:
  - install.sh
responsibilities:
  - Add Skills/ folder handling
  - Check-before-create pattern
  - Handle merge with existing Skills/
must_not_touch:
  - Core install logic for N5/, Prompts/, etc.
```

#### MUST DO
1. Add Skills/ to the folders being installed
2. Add check: `if [ -d "Skills" ]; then` for merge vs create
3. Add message about existing skills preservation
4. Test: `bash -n install.sh` (syntax check)

#### MUST NOT DO
- Break existing install flow
- Remove any current functionality

#### EXPECTED OUTPUT
- `install.sh` updated
- Syntax check passes

---

### D3.3 — Update Main README
**Type:** documentation  
**Estimated tokens:** 10% context

#### Scope
```yaml
files:
  - README.md
responsibilities:
  - Add Meeting Ingestion feature
  - Add Pulse feature
  - Update documentation table
must_not_touch:
  - Existing sections (just add to them)
```

#### MUST DO
1. Add Meeting Ingestion to Features Overview
2. Add Pulse to Features Overview
3. Add docs/MEETING_INGESTION.md to documentation table
4. Add docs/PULSE.md to documentation table
5. Update "What Is This?" if needed

#### EXPECTED OUTPUT
- README.md updated with new features

---

### D3.4 — Validate Fresh Install (Dry Run)
**Type:** validation  
**Estimated tokens:** 10% context

#### Scope
```yaml
files: (read-only validation)
  - All files created/modified by D1.* and D2.*
responsibilities:
  - Verify no hardcoded paths remain
  - Verify imports work
  - Verify no personal data
  - Create validation report
must_not_touch:
  - Any files (read-only)
```

#### MUST DO
1. Grep for `/home/workspace` in all modified files (should find only defaults)
2. Grep for personal identifiers (email, specific folder IDs)
3. Test key imports:
   ```bash
   python3 -c "from N5.scripts.meeting_config import *"
   python3 -c "from Skills.pulse.scripts.pulse_common import PATHS"
   ```
4. Create validation report in deposits/

#### MUST NOT DO
- Modify any files
- Actually run install.sh

#### EXPECTED OUTPUT
- Validation report confirming:
  - [ ] No hardcoded paths (except defaults)
  - [ ] No personal data
  - [ ] Imports work
  - [ ] Ready for merge to repo

---

## MECE Validation

### File Ownership Matrix

| File | Owner | 
|------|-------|
| N5/scripts/meeting_config.py | D1.1 |
| N5/scripts/meeting_registry.py | D1.2 |
| N5/scripts/meeting_orchestrator.py | D1.2 |
| N5/scripts/meeting_state_manager.py | D1.2 |
| N5/scripts/meeting_weekly_organizer.py | D1.2 |
| N5/scripts/meeting_api_integrator.py | D1.2 |
| N5/scripts/meeting_auto_monitor.py | D1.2 |
| N5/scripts/meeting_monitor.py | D1.2 |
| N5/scripts/meeting_transcript_watcher.py | D1.2 |
| N5/scripts/meeting_normalizer.py | D1.2 (verify) |
| N5/scripts/meeting_manifest_generator.py | D1.2 (verify) |
| Skills/meeting-ingestion/SKILL.md | D1.3 |
| Skills/meeting-ingestion/scripts/*.py | D1.3 |
| Prompts/Blocks/Generate_B4*.prompt.md | D1.4 |
| docs/MEETING_INGESTION.md | D1.5 |
| Skills/pulse/scripts/pulse_common.py | D2.1 |
| Skills/pulse/scripts/*.py (except common) | D2.2 |
| docs/PULSE.md | D2.3 |
| N5/config/*.template | D3.1 |
| N5/config/README.md | D3.1 |
| install.sh | D3.2 |
| README.md | D3.3 |

### Verification
- ✅ No overlaps (each file has exactly one owner)
- ✅ No gaps (all files in scope are assigned)
- ✅ Dependencies flow correctly (D1.1 before D1.2, D2.1 before D2.2)

---

## Execution Order

**Stream 1 (Meeting):** D1.1 → D1.2 → D1.3 → D1.4 → D1.5  
**Stream 2 (Pulse):** D2.1 → D2.2 → D2.3  
**Stream 3 (Integration):** D3.1 ∥ D3.2 ∥ D3.3 → D3.4

Streams 1 and 2 can run in parallel.  
Stream 3 waits for S1 and S2 to complete (D3.4 validates everything).
