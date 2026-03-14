---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: meeting-system-recovery-redesign/D2.3
drop_id: D2.3
build_slug: meeting-system-recovery-redesign
---

# Skill Packaging Boundary + Export Policy

## Purpose

Define the boundary between the reusable meeting-system skill and V's private operating data, specify an allowlist export model, recommend file-based markers aligned with existing conventions, specify a bootstrap/setup contract for new environments, and describe the export tooling needed during execution.

---

## 1. Recommended Skill Slug

**Recommended slug:** `meeting-system`

**Rationale:**
- The current `meeting-ingestion` slug is accurate for the v3 pipeline but undersells the redesigned scope. The redesign adds reflection routing, knowledge elevation, archive infrastructure, and quality-gate enforcement — collectively a "meeting system," not just ingestion.
- `meeting-system-recovery` was considered but encodes the recovery context, which is a one-time event, not the durable capability.
- `meeting-system-capability` is redundant (all skills are capabilities).

**This is a recommendation, not a final decision.** V should confirm the slug before execution creates the directory.

**Migration path:** The existing `Skills/meeting-ingestion/` becomes an archive reference. The new `Skills/meeting-system/` starts from the redesigned codebase. A clean break is preferred over in-place rename because the redesign changes enough of the pipeline architecture (gate interlock, reflection routing, knowledge elevation) that continuity of the directory would be misleading.

---

## 2. Reusable Capability vs Private Operating Data

### 2.1 Boundary Principle

The skill packages **the machine** — intake contracts, normalization logic, routing rules, block-selection logic, quality gates, CLI orchestration, knowledge handoff logic, archive infrastructure, prompts, schemas, reference docs, and export tooling. The skill does NOT package **the work product** — real transcripts, manifests with participant names, generated blocks, sqlite state, HITL queues, caches, logs, or any file containing PII or operational history.

Think of it as: the skill is the factory. The meetings are the output that stays in the owner's warehouse.

### 2.2 Reusable Capability (exports with the skill)

<!-- Reusable capability boundary definition -->

| Category | Examples | Why Reusable |
|----------|----------|--------------|
| Pipeline scripts | `meeting_cli.py`, `ingest.py`, `crm_enricher.py`, `block_selector.py`, `block_generator.py`, `process.py`, `quality_gate.py`, `hitl.py`, `archive.py`, `title_normalizer.py`, `calendar_match.py` | Durable logic; no embedded PII |
| CLI and orchestration | `meeting_cli.py` tick/ingest/identify/gate/process/archive commands | Workflow entry points |
| Manifest schema | `manifest-v3.schema.json` | Contract definition; no instance data |
| Block prompt library references | References/pointers to `Prompts/Blocks/` (not the prompts themselves — those live outside the skill) | The skill documents which prompts it uses; the prompts are a separate shared resource |
| Block selection recipes | Recipe definitions inside `block_selector.py` or extracted to `references/` | Reusable intelligence selection logic |
| Quality gate checks | Gate check definitions and threshold logic | Reusable quality framework |
| HITL queue schema | Queue format definition, priority levels, escalation trigger rules | Reusable escalation framework |
| Reference documentation | `meeting-id-convention.md`, `block-picker-v2-policy.md`, `quality-harness-checks.md`, `hitl-queue-spec.md`, `quality-gate-docs.md`, `block-quality-thresholds.md`, `manifest-v3.schema.json` | Operational docs that explain the system |
| SKILL.md | Top-level skill documentation | Required by Agent Skills spec |
| Sanitized fixture examples | Example `manifest.json` with synthetic participants, example block output with synthetic content | Enables testing and onboarding without real data |
| Bootstrap/setup script | `scripts/bootstrap.py` (new, created during execution) | New-environment initialization |
| Export script | `scripts/export_skill.py` (new, created during execution) | Allowlist-driven export tool |
| Reflection pipeline scripts | New scripts for Pocket/reflection routing (created in execution) | Reusable reflection processing logic |
| Knowledge elevation scripts | New post-archive elevation/routing logic (created in execution) | Reusable downstream handoff |

### 2.3 Private Operating Data (never exports)

| Category | Examples | Why Private |
|----------|----------|-------------|
| Real transcripts | `Personal/Meetings/**/transcript.md`, `transcript.jsonl` | PII: names, conversation content |
| Real manifests | `Personal/Meetings/**/manifest.json` with real participants | PII: participant names, companies, calendar IDs |
| Generated blocks | `Personal/Meetings/**/B*.md` | Contains real meeting intelligence |
| SQLite databases | `N5/data/meeting_pipeline.db`, `N5/data/meeting_registry.db`, `N5/runtime/meeting_pipeline.db` | Operational state with PII |
| HITL queue data | `N5/review/meetings/hitl-queue.jsonl` | Contains real escalation items with participant data |
| Webhook data | Fireflies/Fathom/Recall tables in `meeting_pipeline.db` | Source system records with identifiers |
| CRM database | `Personal/Knowledge/CRM/crm.db`, `Personal/Knowledge/CRM/individuals/*.md` | Full PII |
| Source pulls | Google Drive download cache, raw Fireflies/Fathom payloads | Source system data |
| Processing logs | `N5/runtime/meeting_pipeline/*.json`, `N5/logs/` meeting-related entries | Operational history with timestamps and identifiers |
| Recovery staging | `N5/builds/meeting-system-recovery-redesign/` recovery artifacts | Build-specific, contains inventory of real meetings |
| Position candidates | `N5/data/position_candidates.jsonl` (downstream from B32 extraction) | Derived from real meetings |
| brain.db edges | `N5/cognition/brain.db` meeting_edges | Derived from real meetings |
| Archived meetings | `Personal/Meetings/Week-of-*/`, `Personal/Meetings/Archive/` | Real processed meeting corpus |
| `__pycache__/` | Any compiled Python bytecode | Build artifact, not source |

### 2.4 Boundary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Skills/meeting-system/  (EXPORTABLE)                       │
│                                                             │
│  SKILL.md                                                   │
│  scripts/                                                   │
│    meeting_cli.py, ingest.py, crm_enricher.py, ...          │
│    bootstrap.py, export_skill.py                            │
│  references/                                                │
│    manifest-v3.schema.json, quality-gate-docs.md, ...       │
│  assets/                                                    │
│    fixtures/example-manifest.json (synthetic)               │
│    fixtures/example-block-output.md (synthetic)             │
│  .n5exportable                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Workspace-private state  (NEVER EXPORTS)                   │
│                                                             │
│  Personal/Meetings/           ← real meeting corpus         │
│  N5/data/meeting_*.db         ← operational sqlite          │
│  N5/runtime/meeting_*/        ← runtime state               │
│  N5/review/meetings/          ← HITL queue                  │
│  Personal/Knowledge/CRM/      ← CRM profiles               │
│  N5/cognition/brain.db        ← knowledge graph             │
│  Prompts/Blocks/              ← shared prompt library       │
│  N5/config/drive_locations.yaml ← source integration config │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Note on Prompts/Blocks/:** The block prompt library (`Prompts/Blocks/`) is a shared workspace resource, not owned by this skill. The skill references prompts by path but does not bundle them. A bootstrap step ensures the required prompt directory exists and documents which prompts are expected (see Section 5).

---

## 3. Allowlist Export Model

### 3.1 Core Principle: Default-Deny

<!-- Allowlist export model specification -->

**Everything is private unless explicitly allowlisted.** If the export tool encounters a file not on the allowlist, it is excluded. There is no denylist. There is no "export everything except…" logic.

### 3.2 Allowlist Specification

The allowlist is defined as a file at `Skills/meeting-system/.export-allowlist` using glob patterns relative to the skill root:

```
# Skill Packaging Allowlist
# Only files matching these patterns are included in exports.
# Default-deny: unlisted files are excluded.

SKILL.md
scripts/*.py
references/*.md
references/*.json
assets/fixtures/*.json
assets/fixtures/*.md
assets/templates/*.md
```

**Explicitly excluded even if glob-matched:**
- `scripts/__pycache__/**`
- `**/*.pyc`
- `**/.DS_Store`

### 3.3 Export Behavior Rules

| Situation | Behavior |
|-----------|----------|
| File matches allowlist pattern | Include in export |
| File does NOT match any allowlist pattern | **Exclude** (default-deny) |
| File matches allowlist but also matches an exclusion | Exclude (exclusions win) |
| New file added to skill directory | Excluded until explicitly added to allowlist |
| `state/` directory if it exists | Always excluded — runtime data |
| `.n5protected` marker file | Excluded from export (it's a workspace protection marker, not skill content) |
| `.export-allowlist` itself | **Included** in export (self-documenting) |
| `.n5exportable` marker | **Included** in export (signals this skill is export-safe) |

### 3.4 Export Tool Contract

During execution, create `Skills/meeting-system/scripts/export_skill.py` with the following contract:

```
python3 Skills/meeting-system/scripts/export_skill.py --dry-run
python3 Skills/meeting-system/scripts/export_skill.py --output /path/to/export.tar.gz
python3 Skills/meeting-system/scripts/export_skill.py --output /path/to/export/ --format dir
```

**Required behaviors:**
1. Read `.export-allowlist` from skill root
2. Resolve glob patterns against the skill directory
3. Apply exclusion rules
4. In `--dry-run` mode: print the file manifest that would be exported, with sizes and checksums
5. In export mode: create a tarball or directory containing only allowlisted files
6. Log every included and excluded file to stdout
7. Exit with code 1 if `.n5exportable` marker is missing (safety gate)
8. Include a `MANIFEST.txt` in the export listing all included files with SHA-256 checksums

**The export tool does NOT:**
- Touch any files outside the skill directory
- Read or package workspace-private state
- Modify the source skill in any way
- Bundle dependencies (Python stdlib only for scripts)

---

## 4. Marker Conventions

### 4.1 Existing Markers in the Workspace

| Marker | Format | Scope | Current Usage | Count |
|--------|--------|-------|---------------|-------|
| `.n5protected` | JSON or plain text | Directory protection | Prevents delete/move without confirmation; used on `N5/`, `Sites/`, builds, sensitive paths | 30+ instances |
| `POLICY.md` | Markdown | Folder behavior override | Defines folder-specific rules that override global prefs | 6 instances |
| `.processed` | Empty sentinel | Per-meeting-folder | Historical marker from v2 system indicating processing complete | Found in zip recovery corpus |
| `manifest.json` | JSON | Per-meeting-folder | v3 primary state record with `status` field | Active in pipeline |

### 4.2 Markers for the Skill Packaging System

| Marker | Purpose | Location | Format | New or Existing |
|--------|---------|----------|--------|-----------------|
| `.n5exportable` | Signals this skill directory is safe for export | Skill root (`Skills/meeting-system/`) | JSON: `{"exportable": true, "export_version": "1.0", "created": "YYYY-MM-DD", "allowlist": ".export-allowlist"}` | **New** |
| `.export-allowlist` | Defines which files are included in exports | Skill root | Plain text, one glob pattern per line (comments with `#`) | **New** |
| `.n5protected` | Prevents accidental delete/move of the skill directory | Skill root | JSON (existing format) | **Existing convention, applied to new location** |
| `POLICY.md` | Not needed for skill directory | — | — | Not applicable (skill behavior is defined in SKILL.md, not POLICY.md) |

### 4.3 Marker Relationship to Export

| Marker | Effect on Export |
|--------|-----------------|
| `.n5exportable` present | Export tool proceeds |
| `.n5exportable` absent | Export tool refuses to run (exit 1) |
| `.n5protected` present | Excluded from export (workspace-level protection, not skill content) |
| `.export-allowlist` present | Defines export scope |
| `.export-allowlist` absent | Export tool refuses to run (no allowlist = no export) |

### 4.4 Why `.n5exportable` and Not Just the Allowlist

The allowlist defines *what* to export. The `.n5exportable` marker declares *intent* — that this skill has been reviewed and approved for export. A skill could have an allowlist file (e.g., copied from a template) but not yet be validated for distribution. The marker is the explicit green light.

This also provides a simple `find`-based discovery mechanism:
```bash
find /home/workspace/Skills -name ".n5exportable" -type f
```

---

## 5. Bootstrap / Setup Contract

### 5.1 Why Bootstrap Is Needed

The skill packages reusable logic, but that logic depends on workspace infrastructure that lives outside the skill:

- `Personal/Meetings/Inbox/` must exist for intake
- `Personal/Meetings/Archive/` (or redesigned archive target) must exist
- `Prompts/Blocks/` must contain the expected block prompts
- `N5/review/meetings/` must exist for HITL queue
- A sqlite database location must be designated for the derivative index
- Google Calendar API access must be configured
- `ZO_CLIENT_IDENTITY_TOKEN` must be set for block generation
- CRM database path must be reachable
- Drive locations config must point to transcript sources

Without bootstrap, a fresh install of the skill would fail on the first `meeting_cli.py tick` because these external dependencies don't exist.

### 5.2 Bootstrap Location Decision (DP-1)

**Decision: Bootstrap lives INSIDE the skill, with a clear separation of concerns.**

**Rationale:**
- The skill already has a `scripts/` directory. A `bootstrap.py` script there is discoverable and ships with the skill.
- Bootstrap is documentation of what the skill needs, not a system-level installer. It should travel with the capability it supports.
- External bootstrap (`N5/scripts/bootstrap/`) would create a coupling where the skill depends on an external script that may not exist in another workspace.
- The bootstrap script does NOT modify system-level N5 configuration — it only ensures the skill's expected workspace paths and dependencies exist.

**What bootstrap does:**
1. Creates required directory structure if missing:
   - `Personal/Meetings/Inbox/`
   - `Personal/Meetings/Archive/` (or redesigned target)
   - `N5/review/meetings/`
   - `N5/data/` (for derivative sqlite index)
2. Checks for required environment variables and reports missing ones:
   - `ZO_CLIENT_IDENTITY_TOKEN` (block generation)
   - Google Calendar API credentials (calendar triangulation)
3. Checks for expected prompt library at `Prompts/Blocks/` and reports if missing
4. Checks for CRM database accessibility
5. Checks for Drive locations config
6. Initializes the derivative sqlite index if it doesn't exist (empty schema only)
7. Reports a pass/fail summary with actionable instructions for each gap

**What bootstrap does NOT do:**
- Install system packages
- Configure N5 system-level services or agents
- Create scheduled agents (that's an operational decision for the workspace owner)
- Copy or generate real meeting data
- Modify files outside its documented scope

### 5.3 Bootstrap CLI Contract

```
python3 Skills/meeting-system/scripts/bootstrap.py check       # Report status only
python3 Skills/meeting-system/scripts/bootstrap.py setup       # Create missing dirs, init empty DBs
python3 Skills/meeting-system/scripts/bootstrap.py setup --dry-run  # Show what would be created
```

### 5.4 Bootstrap Output

```
Meeting System Bootstrap Check
==============================
[OK]  Personal/Meetings/Inbox/         exists
[OK]  Personal/Meetings/Archive/       exists
[OK]  N5/review/meetings/              exists
[OK]  N5/data/                         exists
[MISS] Prompts/Blocks/                 not found — block generation requires prompt library
[OK]  ZO_CLIENT_IDENTITY_TOKEN         set
[MISS] Google Calendar credentials     not configured — calendar_match will return 0.0
[OK]  CRM database                     accessible at Personal/Knowledge/CRM/crm.db
[MISS] Drive locations config          N5/config/drive_locations.yaml not found — pull command disabled

Status: 6/9 checks passed. Run 'bootstrap.py setup' to create missing directories.
Manual action needed: configure Google Calendar credentials, set up drive_locations.yaml, install prompt library.
```

### 5.5 External Dependencies Documented in SKILL.md

The skill's SKILL.md must include a "System Dependencies" section listing everything bootstrap checks for. This serves as the human-readable contract even if bootstrap.py is not run.

---

## 6. Private Operating Data Exclusions

### 6.1 Directories That Must NEVER Export

These are workspace-private paths that the skill reads from or writes to at runtime but must never be included in any export:

| Path | Contains | Why Private |
|------|----------|-------------|
| `Personal/Meetings/` (all subdirs) | Real transcripts, manifests, blocks, archives | Full PII: names, companies, conversation content |
| `N5/data/meeting_pipeline.db` | v2 operational state, webhook records | Historical PII, operational state |
| `N5/data/meeting_registry.db` | Meeting dedup index | Contains real meeting IDs with participant info |
| `N5/runtime/meeting_pipeline.db` | v3 block tracking | Operational state |
| `N5/runtime/meeting_pipeline/` | v2 transition logs | Operational history |
| `N5/review/meetings/` | HITL queue items | Contains real escalation data with participant names |
| `Personal/Knowledge/CRM/` | Contact profiles | Full PII |
| `N5/cognition/brain.db` | Knowledge graph with meeting edges | Derived from real meetings |
| `N5/data/position_candidates.jsonl` | Extracted worldview positions | Derived from real meeting content |
| `N5/config/drive_locations.yaml` | Google Drive folder IDs | Environment-specific credentials |
| `Prompts/Blocks/` | Block generation prompts | Shared resource, not owned by this skill |

### 6.2 File Patterns That Must NEVER Export (Even If Found Inside Skill Dir)

| Pattern | Reason |
|---------|--------|
| `*.db` | SQLite databases contain operational state |
| `*.jsonl` (except allowlisted fixtures) | Line-delimited logs typically contain operational data |
| `__pycache__/` | Build artifacts |
| `*.pyc` | Compiled bytecode |
| `.DS_Store` | System noise |
| `state/` | Runtime data directory (per build-promote convention) |
| Any file containing `Personal/` paths as literal data | Could leak workspace structure |

### 6.3 Sanitized Fixtures Allowed Inside the Skill

The skill MAY include synthetic example files in `assets/fixtures/` for testing and onboarding:

| Fixture | Purpose | Requirements |
|---------|---------|--------------|
| `example-manifest.json` | Demonstrates manifest v3 schema | All participant names must be synthetic ("Alice", "Bob"). All dates should be plausible but clearly fake (e.g., 2099-01-15). All company names must be synthetic ("Acme Corp"). |
| `example-block-B01.md` | Demonstrates block output format | Content must be entirely synthetic — a fictional meeting recap. |
| `example-hitl-item.json` | Demonstrates HITL queue item format | Synthetic escalation with synthetic participant data. |

**Fixture validation rule:** Any fixture file must pass a check that confirms it contains zero real workspace paths, zero real participant names from the CRM, and zero real calendar event IDs. This check should be part of the export tool's pre-flight.

---

## 7. Skill Directory Structure (Target)

```
Skills/meeting-system/
├── SKILL.md                          # Comprehensive skill documentation
├── .n5protected                      # Workspace protection (excluded from export)
├── .n5exportable                     # Export intent marker (included in export)
├── .export-allowlist                 # Allowlist for export tool (included in export)
├── scripts/
│   ├── meeting_cli.py                # Unified CLI (redesigned)
│   ├── ingest.py                     # Raw → ingested
│   ├── crm_enricher.py              # CRM participant enrichment
│   ├── calendar_match.py            # Calendar triangulation
│   ├── quality_gate.py              # Quality validation
│   ├── block_selector.py            # Smart block selection
│   ├── block_generator.py           # LLM block generation
│   ├── process.py                   # Block orchestration
│   ├── hitl.py                      # HITL queue management
│   ├── title_normalizer.py          # Title enrichment
│   ├── archive.py                   # Archive to organized folders
│   ├── validate_manifest.py         # Schema validation
│   ├── reflect.py                   # Reflection pipeline (NEW)
│   ├── elevate.py                   # Post-archive knowledge elevation (NEW)
│   ├── rebuild_index.py             # Derivative sqlite rebuild (NEW)
│   ├── bootstrap.py                 # Environment setup (NEW)
│   └── export_skill.py              # Allowlist export tool (NEW)
├── references/
│   ├── manifest-v3.schema.json      # JSON Schema for manifest
│   ├── meeting-id-convention.md     # Naming standards
│   ├── block-picker-v2-policy.md    # Block selection rules
│   ├── quality-harness-checks.md    # Quality gate spec
│   ├── hitl-queue-spec.md           # HITL queue schema
│   ├── quality-gate-docs.md         # Quality validation docs
│   ├── block-quality-thresholds.md  # Block quality scoring
│   ├── intake-contract.md           # Unified intake spec (from D2.1)
│   ├── routing-and-titling-rules.md # Classification rules (from D2.2)
│   └── reflection-pipeline.md       # Reflection processing spec (NEW)
└── assets/
    └── fixtures/
        ├── example-manifest.json     # Synthetic example manifest
        ├── example-block-B01.md      # Synthetic example block
        └── example-hitl-item.json    # Synthetic example HITL item
```

**Files NOT in the skill directory:**
- `Prompts/Blocks/` — shared prompt library, referenced by path
- `Personal/Meetings/` — operating data
- `N5/data/` — operational databases
- `N5/config/drive_locations.yaml` — environment config
- `N5/review/meetings/` — HITL queue data

---

## 8. Export Tooling Specification

### 8.1 `export_skill.py` Workflow

```
1. Check .n5exportable exists           → exit 1 if missing
2. Read .export-allowlist               → exit 1 if missing
3. Resolve glob patterns against skill directory
4. Apply exclusion rules (pycache, pyc, DS_Store, state/)
5. Run fixture validation on assets/fixtures/**
6. If --dry-run: print manifest and exit
7. If --output: create tarball or directory copy
8. Generate MANIFEST.txt with SHA-256 checksums
9. Log summary: N files included, M files excluded, total size
```

### 8.2 Fixture Validation

The export tool includes a pre-flight check that scans all files in `assets/fixtures/` for:
- Real workspace paths (e.g., `/home/workspace/Personal/`)
- Known CRM names (cross-reference against a configurable blocklist or skip if CRM unavailable)
- Real calendar event IDs
- Real Fireflies/Fathom transcript IDs

If any fixture fails validation, export halts with a clear error message identifying the offending file and content.

### 8.3 Export Versioning

Each export includes metadata in `MANIFEST.txt`:
```
Export Version: 1.0
Exported At: 2026-03-15T10:00:00Z
Skill Slug: meeting-system
Skill Version: (from SKILL.md frontmatter)
Files: 28
Total Size: 142KB
SHA-256 Checksums:
  SKILL.md  abc123...
  scripts/meeting_cli.py  def456...
  ...
```

---

## 9. Migration Path from `meeting-ingestion`

### 9.1 Relationship to Existing Skill

`Skills/meeting-ingestion/` is the current v3 skill. The redesigned `Skills/meeting-system/` supersedes it. During execution:

1. **Do NOT delete `meeting-ingestion` immediately.** It is the running production system.
2. Create `Skills/meeting-system/` as the redesigned skill.
3. Migrate salvageable scripts (identified in system-audit.md Section 8, DP-1) into the new skill with modifications.
4. Drop dead/deprecated scripts (`backfill_inbox.py`, `manifest_converter.py`, `stage.py`, `normalize_inbox.py`, `processor.py`, `inbox_poller.py`).
5. Add new scripts (`reflect.py`, `elevate.py`, `rebuild_index.py`, `bootstrap.py`, `export_skill.py`).
6. Once the new skill is validated and V approves, archive `meeting-ingestion` (do not delete — move to `Skills/.backups/meeting-ingestion.<timestamp>/`).
7. Update any scheduled agents to point to the new skill path.

### 9.2 What Carries Over

| From `meeting-ingestion` | To `meeting-system` | Changes |
|--------------------------|---------------------|---------|
| `scripts/meeting_cli.py` | `scripts/meeting_cli.py` | Gate interlock fix, reflection routing, elevation command added |
| `scripts/ingest.py` | `scripts/ingest.py` | Fathom/Pocket format support added |
| `scripts/crm_enricher.py` | `scripts/crm_enricher.py` | Minimal changes |
| `scripts/block_selector.py` | `scripts/block_selector.py` | Reflection recipe added |
| `scripts/block_generator.py` | `scripts/block_generator.py` | Minimal changes |
| `scripts/process.py` | `scripts/process.py` | Gate checkpoint enforced |
| `scripts/quality_gate.py` | `scripts/quality_gate.py` | Gate result blocks progression |
| `scripts/hitl.py` | `scripts/hitl.py` | Auto-resolution for common cases |
| `scripts/title_normalizer.py` | `scripts/title_normalizer.py` | Improved rules from D2.2 |
| `scripts/archive.py` | `scripts/archive.py` | Actually creates target directories, writes `archived` status |
| `scripts/calendar_match.py` | `scripts/calendar_match.py` | Debug/fix the 0.0 confidence issue |
| `scripts/validate_manifest.py` | `scripts/validate_manifest.py` | Minimal changes |
| `references/*` | `references/*` | Carried over + new specs from D2.1 and D2.2 |
| — | `scripts/reflect.py` | NEW: Pocket/reflection processing |
| — | `scripts/elevate.py` | NEW: Post-archive knowledge routing |
| — | `scripts/rebuild_index.py` | NEW: Derivative sqlite index rebuild |
| — | `scripts/bootstrap.py` | NEW: Environment setup |
| — | `scripts/export_skill.py` | NEW: Allowlist export |
| — | `assets/fixtures/*` | NEW: Synthetic examples |

---

## 10. Decision Point Resolutions

### DP-1: Should bootstrap live inside the skill, outside the skill, or both?

**Resolution: Inside the skill.**

The bootstrap script at `Skills/meeting-system/scripts/bootstrap.py` ships with the skill. It creates workspace directories and checks for external dependencies, but it does not modify N5 system-level config. This keeps the skill self-documenting: anyone who installs the skill gets the bootstrap tool and can run `bootstrap.py check` to see what's missing.

An external `N5/scripts/bootstrap/meetings_system_bootstrap.py` is unnecessary if the skill's own bootstrap covers the same ground. If V later wants a system-level orchestrator that bootstraps multiple skills at once, that's a separate concern — and it would call each skill's bootstrap.py, not replace it.

### DP-2: Which marker set best aligns with existing conventions while staying simple for exports?

**Resolution: Two new markers (`.n5exportable` + `.export-allowlist`), plus existing `.n5protected`.**

- `.n5protected` is already established (30+ instances) for workspace protection. Apply it to the new skill directory. It is excluded from exports because it's a workspace-level concern.
- `.n5exportable` is new but follows the `.n5*` naming family. It signals export readiness. JSON format for machine readability.
- `.export-allowlist` is new but intentionally NOT prefixed with `.n5` because it is a skill-level concern, not a workspace-level concern. It ships with the skill in exports.

The historical `.processed` sentinel (found in the zip recovery corpus) is a v2 pipeline marker. The redesigned system uses `manifest.json` status fields instead, so `.processed` is not carried forward.

### DP-3: What exact directories should be export-allowlisted vs always-private?

**Resolution: See Sections 2.2 (exportable), 2.3 (private), and 6.1 (never-export paths).**

Summary:
- **Exports:** `SKILL.md`, `scripts/*.py`, `references/*.md`, `references/*.json`, `assets/fixtures/*`, `.n5exportable`, `.export-allowlist`
- **Never exports:** Everything in `Personal/`, `N5/data/`, `N5/runtime/`, `N5/review/`, `N5/cognition/`, `N5/config/`, `Prompts/`, `Personal/Knowledge/CRM/`, plus any `state/`, `__pycache__/`, `*.pyc`, `*.db`, `.n5protected`

---

## 11. Success Criteria Verification

- [x] **Skill boundary is explicit** — Section 2 defines reusable capability vs private operating data with specific file/directory lists
- [x] **Allowlist export policy is explicit** — Section 3 defines default-deny allowlist model with `.export-allowlist` format, export tool contract, and behavior rules
- [x] **Marker conventions are explicit** — Section 4 defines `.n5exportable`, `.export-allowlist`, and their relationship to existing `.n5protected`
- [x] **Bootstrap/setup contract is explicit** — Section 5 defines `bootstrap.py` with check/setup commands, required directories, environment variables, and external dependencies
- [x] **Private operating data exclusions are explicit** — Section 6 lists every private path, file pattern, and the fixture validation rules
