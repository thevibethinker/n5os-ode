---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 4: Preflight & Skeleton (Phases 0–1 Implementation)

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W4-PREFLIGHT-SKELETON  
**Estimated Time:** 45–75 minutes  
**Dependencies:**
- Worker 1–3 complete (`PHASE1_current_state_map.md`, `PHASE2_target_architecture.md`, `PHASE3_migration_plan.md`).

---

## Mission
Implement Phase 0–1 of the migration plan: preflight protections + creation of the target `Personal/Knowledge/**` directory skeleton and SSOT README files, without moving any existing content.

---

## Context

The design work has established `Personal/Knowledge/` as the SSOT for elevated knowledge and defined the target topology. Before any migrations, we must:

1. Protect critical roots using `.n5protected` so later scripts cannot accidentally damage them.
2. Ensure the **full target directory skeleton** exists for `Personal/Knowledge/**` (Wisdom, Intelligence, ContentLibrary, Canon, CRM, Architecture, Logs, Archive, Legacy_Inbox subtrees).
3. Place small README files to document SSOT semantics at key roots.

This worker creates the infrastructure for safe, structured migrations in Workers 5–8.

---

## Dependencies

- `Records/Personal/knowledge-system/PHASE2_target_architecture.md` (v1.1) and `PHASE3_migration_plan.md` (v1.1) available and read.
- `N5/prefs/paths/knowledge_paths.yaml` present (version 1) with updated paths.

---

## Deliverables

1. `.n5protected` files at:
   - `Personal/Knowledge/`
   - `Personal/Meetings/`
   - `Knowledge/`
   - `N5/`
   - `Records/Personal/knowledge-system/`
2. Created directory skeletons (even if empty) for:
   - `Personal/Knowledge/Wisdom/{Self,World,Systems}/`
   - `Personal/Knowledge/Intelligence/{Self,World/Market,Systems,Relationships}/`
   - `Personal/Knowledge/ContentLibrary/content/`
   - `Personal/Knowledge/Canon/{Company,V/SocialContent,Products,Stakeholders}/`
   - `Personal/Knowledge/CRM/{db,individuals,organizations,events,views}/`
   - `Personal/Knowledge/Architecture/{principles,ingestion_standards,planning_prompts,case_studies,specs}/`
   - `Personal/Knowledge/Logs/`
   - `Personal/Knowledge/Archive/{Pre_2025,Legacy_Knowledge_Tree,Company_Snapshots}/`
   - `Personal/Knowledge/Legacy_Inbox/{intelligence,schemas,crm,market_intelligence,stable,semi_stable}/`
3. README files:
   - `Personal/Knowledge/README.md` – declares SSOT role.
   - `Personal/Meetings/README.md` – declares meeting SSOT role (if not already present).
   - `Records/Personal/knowledge-system/README.md` – clarifies design/migration-only role.
   - `Knowledge/README.md` – marks compatibility shell status and points to `Personal/Knowledge/`.
4. A small helper script (e.g. `N5/scripts/knowledge_preflight.py`) that can be re-run safely to validate skeleton presence and `.n5protected` markers.

---

## Requirements

- **Language:** Python 3.12.
- **Idempotent:** Running the script multiple times should not break anything.
- **Non-destructive:** No moves, deletions, or content modifications.
- **Safety:** Use existing `N5/scripts/n5_protect.py` semantics for `.n5protected` file format.
- **Config-aware:** Use `N5/prefs/paths/knowledge_paths.yaml` where applicable instead of hardcoding roots.

---

## Implementation Guide

1. **Preflight Script Skeleton**

Create `N5/scripts/knowledge_preflight.py` with roughly this structure:

```python
import argparse
from pathlib import Path
import yaml

ROOT = Path("/home/workspace")
PATHS_YAML = ROOT / "N5/prefs/paths/knowledge_paths.yaml"


def load_paths():
    data = yaml.safe_load(PATHS_YAML.read_text())
    return data["personal_knowledge"], data["meetings"], data["records"], data["system"], data["compatibility_shell"]


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_readme(path: Path, content: str):
    ensure_dir(path)
    readme = path / "README.md"
    if not readme.exists():
        readme.write_text(content)


def ensure_n5protected(path: Path, reason: str):
    marker = path / ".n5protected"
    if not marker.exists():
        marker.write_text(f"reason: {reason}\n")


def main(check_only: bool = False):
    pk_paths, meetings_cfg, records_cfg, system_cfg, compat_cfg = load_paths()
    # Resolve roots
    pk_root = ROOT / pk_paths["root"]
    meetings_root = ROOT / meetings_cfg["root"]
    records_root = ROOT / records_cfg["knowledge_system"]
    n5_root = ROOT / system_cfg["n5_root"]
    legacy_knowledge_root = ROOT / compat_cfg["legacy_knowledge_root"]

    # 1) Ensure dirs
    #   - Build all required skeleton directories using ensure_dir()

    # 2) Ensure .n5protected markers
    #   - Personal/Knowledge, Personal/Meetings, Knowledge, N5, Records/Personal/knowledge-system

    # 3) Ensure README files with short, clear content

    # In check_only mode, just report what would be created.


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    main(check_only=args.check_only)
```

2. **Directory Skeleton Creation**

- Use `ensure_dir()` to create all target subdirectories from the Deliverables section.
- Use the paths config for roots; append subpaths explicitly (e.g. `pk_root / "Wisdom" / "Self"`).

3. **README Content (Short & Clear)**

Suggested minimal content:

- `Personal/Knowledge/README.md`:
  > This directory is the **single source of truth (SSOT)** for elevated knowledge (Wisdom + Intelligence) and curated content. All durable knowledge should eventually live here.

- `Personal/Meetings/README.md`:
  > This directory is the **SSOT for meeting intelligence**: per-meeting transcripts, blocks, and derived artifacts that remain tied to a specific meeting.

- `Records/Personal/knowledge-system/README.md`:
  > This directory stores **design, migration plans, and reasoning traces** for the knowledge system. It is not a knowledge SSOT.

- `Knowledge/README.md`:
  > This directory is a **compatibility shell only**. The canonical knowledge home is `Personal/Knowledge/`. New knowledge should not be authored here.

4. **.n5protected Markers**

- Use a simple YAML-like content in each `.n5protected` file, e.g.:

  ```text
  reason: SSOT root – structural changes require explicit confirmation
  scope: subtree
  ```

- Do **not** enforce enforcement logic here; rely on `n5_protect.py` in later scripts.

---

## Testing

1. Run the script in check-only mode:

```bash
cd /home/workspace
python3 N5/scripts/knowledge_preflight.py --check-only
```

- Confirm the script prints which directories and files it would create.

2. Run in normal mode:

```bash
cd /home/workspace
python3 N5/scripts/knowledge_preflight.py
```

3. Validate:

- `.n5protected` files exist at the specified roots.
- `ls -R Personal/Knowledge` shows the expected skeleton.
- README files exist with the intended content.

---

## Report Back

When complete, report to the orchestrator with:

1. Confirmation that `N5/scripts/knowledge_preflight.py` exists and runs in both `--check-only` and normal modes without errors.
2. Confirmation that `.n5protected` markers and README files were created as specified.
3. A brief summary of any deviations from the brief (if needed).

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  

