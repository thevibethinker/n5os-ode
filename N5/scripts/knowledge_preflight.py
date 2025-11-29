#!/usr/bin/env python3
"""Knowledge system preflight: protections + directory skeleton + SSOT READMEs.

Phase 0–1 implementation for Personal/Knowledge/**.

- Idempotent and non-destructive
- Config-aware via N5/prefs/paths/knowledge_paths.yaml
- Re-runnable with --check-only to preview planned actions
"""

import argparse
import json
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Tuple

import yaml


ROOT = Path("/home/workspace")
PATHS_YAML = ROOT / "N5/prefs/paths/knowledge_paths.yaml"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


class ActionLog:
    """Collect actions for either check-only or apply mode."""

    def __init__(self, check_only: bool) -> None:
        self.check_only = check_only
        self.actions: List[str] = []

    def add(self, message: str) -> None:
        self.actions.append(message)
        prefix = "DRY-RUN" if self.check_only else "APPLY"
        logger.info("%s: %s", prefix, message)

    def summary(self) -> None:
        if not self.actions:
            logger.info("No changes needed; all protections and skeleton already in place.")
        else:
            logger.info("Planned/applied %d actions.", len(self.actions))


def load_paths() -> Tuple[dict, dict, dict, dict, dict]:
    if not PATHS_YAML.exists():
        raise FileNotFoundError(f"Missing paths config: {PATHS_YAML}")

    data = yaml.safe_load(PATHS_YAML.read_text())
    try:
        pk_paths = data["personal_knowledge"]
        meetings_cfg = data["meetings"]
        records_cfg = data["records"]
        system_cfg = data["system"]
        compat_cfg = data["compatibility_shell"]
    except KeyError as exc:
        raise KeyError(f"Missing expected key in {PATHS_YAML}: {exc}") from exc

    return pk_paths, meetings_cfg, records_cfg, system_cfg, compat_cfg


def ensure_dir(path: Path, action_log: ActionLog) -> None:
    if path.exists():
        return
    action_log.add(f"mkdir -p {path}")
    if not action_log.check_only:
        path.mkdir(parents=True, exist_ok=True)


def ensure_readme(path: Path, content: str, action_log: ActionLog) -> None:
    """Create README.md with YAML frontmatter if missing.

    README creation is intentionally one-shot; subsequent runs do not overwrite.
    """

    ensure_dir(path, action_log)
    readme = path / "README.md"
    if readme.exists():
        return

    today = date.today().isoformat()
    frontmatter = "---\n" f"created: {today}\n" f"last_edited: {today}\n" "version: 1.0\n" "---\n\n"
    full_content = frontmatter + content.strip() + "\n"

    action_log.add(f"create README {readme}")
    if not action_log.check_only:
        readme.write_text(full_content)


def ensure_n5protected(path: Path, reason: str, action_log: ActionLog, scope: str = "subtree") -> None:
    """Ensure a .n5protected marker exists with n5_protect-compatible JSON format."""

    ensure_dir(path, action_log)
    marker = path / ".n5protected"
    if marker.exists():
        return

    marker_data = {
        "protected": True,
        "reason": reason,
        "scope": scope,
        "created": datetime.now(timezone.utc).isoformat(),
        "created_by": "knowledge_preflight",
        "script": "knowledge_preflight.py",
    }

    action_log.add(f"create .n5protected {marker}")
    if not action_log.check_only:
        marker.write_text(json.dumps(marker_data, indent=2) + "\n")


def build_skeleton_dirs(pk_paths: dict) -> List[Path]:
    """Return list of directories that must exist under Personal/Knowledge/**."""

    dirs: List[Path] = []

    pk_root = ROOT / pk_paths["root"]

    # Wisdom
    wisdom_root = ROOT / pk_paths.get("wisdom", str(pk_root / "Wisdom"))
    for leaf in ("Self", "World", "Systems"):
        dirs.append(wisdom_root / leaf)

    # Intelligence
    intelligence_root = ROOT / pk_paths.get("intelligence", str(pk_root / "Intelligence"))
    for leaf in ("Self", "World", "Systems", "Relationships"):
        dirs.append(intelligence_root / leaf)
    # World/Market subtree
    world_root = ROOT / pk_paths.get("intelligence_world", str(intelligence_root / "World"))
    dirs.append(world_root)
    dirs.append(world_root / "Market")

    # ContentLibrary/content
    content_library_root = ROOT / pk_paths.get("content_library", str(pk_root / "ContentLibrary"))
    dirs.append(content_library_root)
    dirs.append(content_library_root / "content")

    # Canon
    canon_root = ROOT / pk_paths.get("canon", str(pk_root / "Canon"))
    for sub in ("Company", "V", "Products", "Stakeholders"):
        dirs.append(canon_root / sub)
    # V/SocialContent subtree
    dirs.append(canon_root / "V" / "SocialContent")

    # CRM
    crm_cfg = pk_paths.get("crm", {})
    crm_root = ROOT / crm_cfg.get("root", str(pk_root / "CRM"))
    dirs.append(crm_root)
    dirs.append(crm_root / "db")
    dirs.append(crm_root / "individuals")
    dirs.append(crm_root / "organizations")
    dirs.append(crm_root / "views")
    dirs.append(crm_root / "events")

    # Architecture
    arch_root = pk_root / "Architecture"
    for sub in ("principles", "ingestion_standards", "planning_prompts", "case_studies", "specs"):
        dirs.append(arch_root / sub)

    # Logs
    dirs.append(pk_root / "Logs")

    # Archive
    archive_root = ROOT / pk_paths.get("archive", str(pk_root / "Archive"))
    for sub in ("Pre_2025", "Legacy_Knowledge_Tree", "Company_Snapshots"):
        dirs.append(archive_root / sub)

    # Legacy_Inbox
    legacy_inbox_root = pk_root / "Legacy_Inbox"
    for sub in (
        "intelligence",
        "schemas",
        "crm",
        "market_intelligence",
        "stable",
        "semi_stable",
    ):
        dirs.append(legacy_inbox_root / sub)

    # Deduplicate while preserving order
    seen = set()
    unique_dirs: List[Path] = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            unique_dirs.append(d)
    return unique_dirs


PK_README = """This directory is the **single source of truth (SSOT)** for elevated knowledge (Wisdom + Intelligence), curated content, frameworks, canon, and CRM. All durable knowledge should eventually live here.
"""

MEETINGS_README = """This directory is the **SSOT for meeting intelligence**: per-meeting transcripts, blocks, and derived artifacts that remain tied to a specific meeting.
"""

RECORDS_KNOWLEDGE_SYSTEM_README = """This directory stores **design, migration plans, and reasoning traces** for the knowledge system. It is not a knowledge SSOT.
"""

LEGACY_KNOWLEDGE_README = """This directory is a **compatibility shell only**. The canonical knowledge home is `Personal/Knowledge/`. New knowledge should not be authored here.
"""


def main(check_only: bool = False) -> int:
    try:
        pk_paths, meetings_cfg, records_cfg, system_cfg, compat_cfg = load_paths()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load paths config: %s", exc, exc_info=True)
        return 1

    action_log = ActionLog(check_only=check_only)

    # Resolve roots from config
    pk_root = ROOT / pk_paths["root"]
    meetings_root = ROOT / meetings_cfg["root"]
    records_root = ROOT / records_cfg["knowledge_system"]
    n5_root = ROOT / system_cfg["n5_root"]
    legacy_knowledge_root = ROOT / compat_cfg["legacy_knowledge_root"]

    # 1) Ensure directory skeleton under Personal/Knowledge/**
    skeleton_dirs = build_skeleton_dirs(pk_paths)
    for d in skeleton_dirs:
        ensure_dir(d, action_log)

    # 2) Ensure .n5protected markers for core SSOT/critical roots
    ensure_n5protected(
        pk_root,
        reason="SSOT knowledge root – structural changes require explicit confirmation",
        action_log=action_log,
    )
    ensure_n5protected(
        meetings_root,
        reason="SSOT meeting root – structural changes require explicit confirmation",
        action_log=action_log,
    )
    ensure_n5protected(
        legacy_knowledge_root,
        reason="Legacy compatibility shell – destructive changes must be explicit",
        action_log=action_log,
    )
    ensure_n5protected(
        n5_root,
        reason="System root – N5 scripts and services live here",
        action_log=action_log,
    )
    ensure_n5protected(
        records_root,
        reason="Knowledge-system design and migration records root",
        action_log=action_log,
    )

    # 3) Ensure README files at key roots
    ensure_readme(pk_root, PK_README, action_log)
    ensure_readme(meetings_root, MEETINGS_README, action_log)
    ensure_readme(records_root, RECORDS_KNOWLEDGE_SYSTEM_README, action_log)
    ensure_readme(legacy_knowledge_root, LEGACY_KNOWLEDGE_README, action_log)

    action_log.summary()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge system preflight: protections + skeleton + READMEs")
    parser.add_argument("--check-only", action="store_true", help="Dry-run mode; report actions without modifying the filesystem")
    args = parser.parse_args()

    sys.exit(main(check_only=args.check_only))

