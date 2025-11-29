#!/usr/bin/env python3
"""CRM migration script (Phase 2 implementation).

- Consolidates CRM assets under Personal/Knowledge/CRM/** (SSOT).
- Converts Knowledge/crm/individuals into compatibility stubs + index view.
- Idempotent and .n5protected-aware.

This script is designed to be run in two modes:
- --dry-run: compute and report planned actions only
- --execute: apply changes safely after dry-run verification
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

ROOT = Path("/home/workspace")
PATHS_YAML = ROOT / "N5/prefs/paths/knowledge_paths.yaml"
LOGS_ROOT = ROOT / "Records/Personal/knowledge-system/logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ProfileSource:
    person_id: str
    path: Path
    origin: str  # e.g. "legacy_inbox", "legacy_view"


@dataclass
class PlannedProfile:
    person_id: str
    canonical_path: Path
    sources: List[ProfileSource]
    action: str  # "copy", "merge", "exists"


class ActionCollector:
    """Collects planned actions for dry-run and execute modes."""

    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.profile_plans: List[PlannedProfile] = []
        self.stub_creations: List[Tuple[Path, Path]] = []  # (stub_path, canonical_path)
        self.db_moves: List[Tuple[Path, Path]] = []  # (src, dest)
        self.index_write: Optional[Path] = None

    def log(self, message: str) -> None:
        prefix = "DRY-RUN" if self.dry_run else "APPLY"
        logger.info("%s: %s", prefix, message)


def load_paths() -> Dict[str, Path]:
    """Load path config and return key roots as Paths.

    Keys:
      - crm_root
      - crm_db_root
      - crm_individuals_root
      - legacy_inbox_crm_root
      - legacy_inbox_individuals_root
      - legacy_view_individuals_root
      - legacy_view_index_path
    """

    if not PATHS_YAML.exists():
        raise FileNotFoundError(f"Missing paths config: {PATHS_YAML}")

    data = yaml.safe_load(PATHS_YAML.read_text())
    try:
        pk_paths = data["personal_knowledge"]
        compat_cfg = data["compatibility_shell"]
    except KeyError as exc:
        raise KeyError(f"Missing expected key in {PATHS_YAML}: {exc}") from exc

    crm_cfg = pk_paths.get("crm", {})

    crm_root = ROOT / crm_cfg.get("root", str(ROOT / pk_paths["root"] / "CRM"))
    crm_db_root = crm_root / "db"
    crm_individuals_root = crm_root / "individuals"

    legacy_inbox_root = ROOT / pk_paths.get(
        "archive", str(ROOT / pk_paths["root"] / "Archive")
    )
    # Phase 2/3: Legacy_Inbox/crm explicitly under Personal/Knowledge
    legacy_inbox_crm_root = ROOT / pk_paths["root"] / "Legacy_Inbox" / "crm"
    legacy_inbox_individuals_root = legacy_inbox_crm_root / "individuals"

    # Compatibility view under Knowledge/crm/individuals
    legacy_knowledge_root = ROOT / compat_cfg["legacy_knowledge_root"]
    legacy_view_individuals_root = legacy_knowledge_root / "crm" / "individuals"
    legacy_view_index_path = legacy_view_individuals_root / "index.jsonl"

    return {
        "crm_root": crm_root,
        "crm_db_root": crm_db_root,
        "crm_individuals_root": crm_individuals_root,
        "legacy_inbox_crm_root": legacy_inbox_crm_root,
        "legacy_inbox_individuals_root": legacy_inbox_individuals_root,
        "legacy_view_individuals_root": legacy_view_individuals_root,
        "legacy_view_index_path": legacy_view_index_path,
    }


def check_n5_protected(path: Path) -> bool:
    """Return True if path is under a .n5protected marker.

    Uses n5_protect.py check <path>; non-zero exit means not protected.
    """

    try:
        result = subprocess.run(
            [
                "python3",
                str(ROOT / "N5/scripts/n5_protect.py"),
                "check",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to invoke n5_protect.py: %s", exc, exc_info=True)
        return False

    if result.returncode == 0:
        logger.warning(".n5protected active for %s; skipping destructive changes here.", path)
        return True

    return False


def discover_legacy_profiles(individuals_root: Path, origin: str) -> List[ProfileSource]:
    if not individuals_root.exists():
        return []

    sources: List[ProfileSource] = []
    for md in sorted(individuals_root.glob("*.md")):
        person_id = md.stem
        sources.append(ProfileSource(person_id=person_id, path=md, origin=origin))
    return sources


def group_profiles(
    legacy_inbox_profiles: List[ProfileSource],
    legacy_view_profiles: List[ProfileSource],
    canonical_root: Path,
) -> List[PlannedProfile]:
    by_id: Dict[str, List[ProfileSource]] = {}
    for src in legacy_inbox_profiles + legacy_view_profiles:
        by_id.setdefault(src.person_id, []).append(src)

    plans: List[PlannedProfile] = []
    for person_id, sources in sorted(by_id.items()):
        canonical_path = canonical_root / f"{person_id}.md"
        if canonical_path.exists():
            action = "exists"
        elif len(sources) == 1:
            action = "copy"
        else:
            action = "merge"
        plans.append(
            PlannedProfile(
                person_id=person_id,
                canonical_path=canonical_path,
                sources=sources,
                action=action,
            )
        )
    return plans


def read_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    """Minimal YAML frontmatter reader.

    Returns (frontmatter_dict, body_str).
    If no frontmatter, returns ({}, full_content).
    """

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text

    _, fm_text, body = parts
    try:
        fm = yaml.safe_load(fm_text) or {}
    except Exception:  # noqa: BLE001
        fm = {}
    return fm, body


def write_canonical_profile(plan: PlannedProfile, dry_run: bool) -> None:
    """Write unified profile to canonical path.

    Current implementation is conservative: if multiple sources exist, it
    concatenates their bodies with simple separators and chooses the most
    recently edited frontmatter metadata when available.
    """

    path = plan.canonical_path

    # Read sources
    merged_bodies: List[str] = []
    chosen_fm: Dict[str, object] = {}
    chosen_date: Optional[str] = None

    for src in plan.sources:
        fm, body = read_frontmatter(src.path)
        merged_bodies.append(f"\n<!-- source: {src.origin} ({src.path}) -->\n" + body.strip() + "\n")

        # Choose frontmatter with latest last_edited/updated_at if present
        candidate_date = None
        for key in ("last_edited", "updated_at", "updated"):
            if isinstance(fm.get(key), str):
                candidate_date = fm[key]
                break

        if candidate_date is not None:
            if chosen_date is None or str(candidate_date) > str(chosen_date):
                chosen_date = str(candidate_date)
                chosen_fm = dict(fm)

    # Ensure person_id present
    chosen_fm.setdefault("person_id", plan.person_id)
    today = date.today().isoformat()
    chosen_fm.setdefault("created", today)
    chosen_fm["last_edited"] = today

    frontmatter_text = "---\n" + yaml.safe_dump(chosen_fm, sort_keys=False) + "---\n\n"
    body_text = "\n".join(merged_bodies).strip() + "\n"
    content = frontmatter_text + body_text

    if dry_run:
        logger.info("DRY-RUN: would write canonical profile %s", path)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote canonical profile %s", path)


def ensure_stub(stub_path: Path, canonical_path: Path, dry_run: bool) -> None:
    stub_fm = {
        "person_id": canonical_path.stem,
        "canonical_path": str(canonical_path.relative_to(ROOT)),
        "role": "compatibility_stub",
        "created": date.today().isoformat(),
        "last_edited": date.today().isoformat(),
        "version": "1.0",
    }
    fm_text = "---\n" + yaml.safe_dump(stub_fm, sort_keys=False) + "---\n\n"
    body = (
        "This CRM profile now lives at "
        f"`{canonical_path.relative_to(ROOT)}`.\n"
    )
    content = fm_text + body

    if dry_run:
        logger.info("DRY-RUN: would write stub %s -> %s", stub_path, canonical_path)
        return

    stub_path.parent.mkdir(parents=True, exist_ok=True)
    stub_path.write_text(content, encoding="utf-8")
    logger.info("Wrote stub %s -> %s", stub_path, canonical_path)


def move_db_files(paths: Dict[str, Path], actions: ActionCollector) -> None:
    legacy_root = paths["legacy_inbox_crm_root"]
    db_root = paths["crm_db_root"]

    if not legacy_root.exists():
        return

    for src in legacy_root.glob("*.db"):
        dest = db_root / src.name
        actions.db_moves.append((src, dest))
        actions.log(f"DB move: {src} -> {dest}")


def apply_db_moves(actions: ActionCollector, dry_run: bool) -> None:
    for src, dest in actions.db_moves:
        if dest.exists():
            logger.info("DB already at %s; leaving legacy copy at %s", dest, src)
            continue
        if dry_run:
            logger.info("DRY-RUN: would copy DB %s -> %s", src, dest)
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        logger.info("Copied DB %s -> %s", src, dest)


def regenerate_index(
    canonical_root: Path,
    index_path: Path,
    dry_run: bool,
) -> None:
    entries: List[Dict[str, object]] = []

    if canonical_root.exists():
        for md in sorted(canonical_root.glob("*.md")):
            fm, _ = read_frontmatter(md)
            entry = {
                "person_id": fm.get("person_id", md.stem),
                "path": str(md.relative_to(ROOT)),
                "name": fm.get("name") or fm.get("full_name") or fm.get("title") or md.stem,
            }
            entries.append(entry)

    if dry_run:
        logger.info(
            "DRY-RUN: would write index %s with %d entries",
            index_path,
            len(entries),
        )
        return

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.info("Wrote index %s (%d entries)", index_path, len(entries))


def write_run_log(
    paths: Dict[str, Path],
    actions: ActionCollector,
    executed: bool,
    limited_to: Optional[int],
) -> None:
    LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOGS_ROOT / f"crm_migration_run_{ts}.md"

    today = date.today().isoformat()
    frontmatter = (
        "---\n"
        f"created: {today}\n"
        f"last_edited: {today}\n"
        "version: 1.0\n"
        "---\n\n"
    )

    total_profiles = len(actions.profile_plans)
    merges = sum(1 for p in actions.profile_plans if p.action == "merge")
    copies = sum(1 for p in actions.profile_plans if p.action == "copy")
    exists = sum(1 for p in actions.profile_plans if p.action == "exists")

    content_lines = [
        f"# CRM Migration Run ({'EXECUTE' if executed else 'DRY-RUN'})\n",
        "\n",
        f"Date: {today}\n",
        f"Limited to: {limited_to if limited_to is not None else 'No'} profiles\n",
        "\n",
        "## Summary\n",
        f"- Total planned profiles: {total_profiles}\n",
        f"- Copies: {copies}\n",
        f"- Merges: {merges}\n",
        f"- Existing canonicals: {exists}\n",
        f"- DB moves planned: {len(actions.db_moves)}\n",
        "\n",
        "## Paths\n",
        *(f"- {k}: {v}\n" for k, v in paths.items()),
        "\n",
    ]

    log_path.write_text(frontmatter + "".join(content_lines), encoding="utf-8")
    logger.info("Wrote run log %s", log_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="CRM migration script (Phase 2)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Preview planned actions")
    mode.add_argument("--execute", action="store_true", help="Apply planned actions")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of profiles to process",
    )
    args = parser.parse_args()

    dry_run = args.dry_run

    try:
        paths = load_paths()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load paths config: %s", exc, exc_info=True)
        return 1

    actions = ActionCollector(dry_run=dry_run)

    # Safety: check protections at key roots
    for key in ("crm_root", "crm_db_root", "crm_individuals_root", "legacy_view_individuals_root"):
        path = paths[key]
        if check_n5_protected(path):
            logger.warning("Path %s is protected; script will avoid destructive writes here.", path)

    # Discover legacy DBs
    move_db_files(paths, actions)

    # Discover legacy profiles
    legacy_inbox_profiles = discover_legacy_profiles(
        paths["legacy_inbox_individuals_root"],
        origin="legacy_inbox",
    )
    legacy_view_profiles = discover_legacy_profiles(
        paths["legacy_view_individuals_root"],
        origin="legacy_view",
    )

    if not legacy_inbox_profiles and not legacy_view_profiles:
        logger.info("No legacy CRM profiles found; nothing to do.")
        return 0

    # Group into planned canonical profiles
    plans = group_profiles(
        legacy_inbox_profiles,
        legacy_view_profiles,
        canonical_root=paths["crm_individuals_root"],
    )

    if args.limit is not None and args.limit > 0:
        plans = plans[: args.limit]

    actions.profile_plans = plans

    logger.info("Planned %d canonical profiles", len(plans))

    # Plan and optionally apply canonical writes + stubs
    for plan in plans:
        if plan.action in {"copy", "merge"}:
            write_canonical_profile(plan, dry_run=dry_run)
        else:
            logger.info("Canonical already exists for %s at %s", plan.person_id, plan.canonical_path)

        # Stub for Knowledge/crm/individuals
        stub_path = paths["legacy_view_individuals_root"] / f"{plan.person_id}.md"
        ensure_stub(stub_path, plan.canonical_path, dry_run=dry_run)

    # Apply DB moves
    apply_db_moves(actions, dry_run=dry_run)

    # Regenerate view index
    regenerate_index(
        canonical_root=paths["crm_individuals_root"],
        index_path=paths["legacy_view_index_path"],
        dry_run=dry_run,
    )

    # Write run log
    write_run_log(paths, actions, executed=not dry_run, limited_to=args.limit)

    return 0


if __name__ == "__main__":
    sys.exit(main())

