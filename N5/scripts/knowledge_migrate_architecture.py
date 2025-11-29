#!/usr/bin/env python3
"""Knowledge Architecture Migration Script.

Phase 4/5 implementation for consolidating architecture-related docs under
Personal/Knowledge/Architecture/**.

Dry-run mode is recommended for initial runs:
- --dry-run prints planned operations only.
- Without --dry-run, operations are executed (copy by default).

Sources:
- Personal/Knowledge/Legacy_Inbox/systems/**
- Personal/Knowledge/Legacy_Inbox/infrastructure/**
- Personal/Knowledge/Specs/*.md
- Inbox/20251028-132904_n5os-core/Knowledge/architectural/**

Targets:
- Personal/Knowledge/Architecture/specs/systems/**
- Personal/Knowledge/Architecture/specs/infrastructure/**
- Personal/Knowledge/Architecture/** (for specs/principles)
- Personal/Knowledge/Archive/Legacy_Knowledge_Tree/Knowledge/architectural/** (archive copy)

The script is .n5protected-aware via N5/scripts/n5_protect.check_protected.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

WORKSPACE = Path("/home/workspace").resolve()
CONFIG_PATH = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"

# Ensure N5 scripts dir is importable for n5_protect
SCRIPTS_DIR = WORKSPACE / "N5" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:  # type: ignore[import]
    from n5_protect import check_protected as _check_protected
except Exception:  # pragma: no cover - defensive fallback
    _check_protected = None  # type: ignore[assignment]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("knowledge_migrate_architecture")


@dataclass
class PlannedAction:
    """Representation of a planned file operation."""

    action: str  # "copy" or "move"
    src: str
    dest: str
    reason: str
    protected: bool = False
    protected_reason: Optional[str] = None


@dataclass
class AmbiguousSpec:
    path: str
    reason: str


@dataclass
class MigrationReport:
    """Aggregate report for a migration run."""

    timestamp: str
    mode: str
    dry_run: bool
    actions_planned: int
    actions_executed: int
    actions_skipped_protected: int
    ambiguous_specs: List[AmbiguousSpec]
    notes: List[str]


def load_paths() -> Dict[str, Path]:
    """Load knowledge paths config and resolve key roots as Paths."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")

    data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    pk = data.get("personal_knowledge", {})
    compat = data.get("compatibility_shell", {})

    pk_root = WORKSPACE / pk.get("root", "Personal/Knowledge")

    architecture_root = WORKSPACE / pk.get("architecture", "Personal/Knowledge/Architecture")
    wisdom_root = WORKSPACE / pk.get("wisdom", "Personal/Knowledge/Wisdom")

    legacy_root = pk_root / "Legacy_Inbox"
    archive_legacy_root = WORKSPACE / compat.get(
        "legacy_knowledge_archive",
        "Personal/Knowledge/Archive/Legacy_Knowledge_Tree/Knowledge",
    )

    return {
        "pk_root": pk_root,
        "architecture_root": architecture_root,
        "wisdom_root": wisdom_root,
        "legacy_root": legacy_root,
        "archive_legacy_root": archive_legacy_root,
    }


def is_protected(path: Path) -> Tuple[bool, Optional[str]]:
    """Return (True, reason) if path (or parents) is protected via .n5protected.

    If n5_protect is unavailable, treat as unprotected but log a warning once.
    """

    global _check_protected  # type: ignore[global-variable-not-assigned]

    if _check_protected is None:
        logger.warning(
            "n5_protect.check_protected unavailable; skipping .n5protected checks."
        )
        return False, None

    try:
        marker = _check_protected(path)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(".n5protected check failed for %s: %s", path, exc)
        return False, None

    if marker:
        return True, str(marker.get("reason", "protected"))
    return False, None


def ensure_dir(path: Path) -> None:
    """Create directory (and parents) if needed."""

    path.mkdir(parents=True, exist_ok=True)


def classify_spec(path: Path, content: str) -> Tuple[str, float, str]:
    """Classify a spec as architecture vs wisdom vs ambiguous.

    Returns (label, confidence, reason).
    label in {"architecture", "wisdom", "ambiguous"}.
    """

    text = content.lower()
    fname = path.name.lower()

    arch_score = 0
    wisdom_score = 0
    reasons: List[str] = []

    # Strong indicators
    if "architectural principles" in text:
        arch_score += 3
        reasons.append("contains 'architectural principles'")
    if "architecture" in text or "architectural" in text:
        arch_score += 2
        reasons.append("mentions 'architecture/architectural'")
    if "n5os" in text:
        arch_score += 1
        reasons.append("mentions 'N5OS'")

    if "wisdom" in text:
        wisdom_score += 2
        reasons.append("mentions 'Wisdom'")
    if "belief" in text or "beliefs" in text or "philosophy" in text:
        wisdom_score += 1
        reasons.append("mentions beliefs/philosophy")

    # Filename-based hints
    if "principles" in fname and "architect" in text:
        arch_score += 1
        reasons.append("file about principles + architecture")

    if arch_score == 0 and wisdom_score == 0:
        return "ambiguous", 0.0, "no strong architecture/wisdom indicators found"

    if arch_score >= wisdom_score + 1:
        conf = min(1.0, 0.5 + 0.1 * arch_score)
        return "architecture", conf, f"arch_score={arch_score}, wisdom_score={wisdom_score}; " + ", ".join(reasons)

    if wisdom_score >= arch_score + 1:
        conf = min(1.0, 0.5 + 0.1 * wisdom_score)
        return "wisdom", conf, f"arch_score={arch_score}, wisdom_score={wisdom_score}; " + ", ".join(reasons)

    return "ambiguous", 0.0, (
        f"scores too close (arch={arch_score}, wisdom={wisdom_score}); "
        + ", ".join(reasons)
    )


def plan_legacy_systems(
    legacy_root: Path, architecture_root: Path
) -> List[PlannedAction]:
    """Plan moves/copies from Legacy_Inbox/systems and infrastructure."""

    actions: List[PlannedAction] = []

    systems_src = legacy_root / "systems"
    infra_src = legacy_root / "infrastructure"

    systems_dest_root = architecture_root / "specs" / "systems"
    infra_dest_root = architecture_root / "specs" / "infrastructure"

    for src_root, dest_root, label in [
        (systems_src, systems_dest_root, "legacy systems → Architecture/specs/systems"),
        (infra_src, infra_dest_root, "legacy infrastructure → Architecture/specs/infrastructure"),
    ]:
        if not src_root.exists():
            logger.info("Skipping %s; source missing: %s", label, src_root)
            continue

        for src in src_root.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(src_root)
            dest = dest_root / rel
            actions.append(
                PlannedAction(
                    action="copy",
                    src=str(src),
                    dest=str(dest),
                    reason=label,
                )
            )

    return actions


def plan_specs_directory(
    specs_root: Path, architecture_root: Path, wisdom_root: Path
) -> Tuple[List[PlannedAction], List[AmbiguousSpec]]:
    """Plan migrations for Personal/Knowledge/Specs/*.md."""

    actions: List[PlannedAction] = []
    ambiguous: List[AmbiguousSpec] = []

    if not specs_root.exists():
        logger.info("Specs root not found: %s", specs_root)
        return actions, ambiguous

    for src in sorted(specs_root.glob("*.md")):
        text = src.read_text(encoding="utf-8")
        label, confidence, reason = classify_spec(src, text)

        if label == "ambiguous" or confidence < 0.6:
            ambiguous.append(
                AmbiguousSpec(
                    path=str(src),
                    reason=f"{label} (confidence={confidence:.2f}): {reason}",
                )
            )
            logger.warning("Ambiguous spec, leaving in place: %s (%s)", src, reason)
            continue

        if label == "architecture":
            # Heuristic: principles-related specs go under Architecture/principles
            target_subdir = "principles" if "principles" in src.name.lower() else "specs"
            dest = architecture_root / target_subdir / src.name
            actions.append(
                PlannedAction(
                    action="copy",
                    src=str(src),
                    dest=str(dest),
                    reason=f"Specs → Architecture/{target_subdir} (label={label}, confidence={confidence:.2f})",
                )
            )
        elif label == "wisdom":
            # Default Wisdom landing for system-level specs
            wisdom_systems = wisdom_root / "Systems"
            dest = wisdom_systems / src.name
            actions.append(
                PlannedAction(
                    action="copy",
                    src=str(src),
                    dest=str(dest),
                    reason=f"Specs → Wisdom/Systems (label={label}, confidence={confidence:.2f})",
                )
            )

    return actions, ambiguous


def plan_n5os_architectural(
    n5os_arch_root: Path,
    architecture_root: Path,
    archive_legacy_root: Path,
) -> List[PlannedAction]:
    """Plan migrations for Inbox/20251028-132904_n5os-core/Knowledge/architectural/**.

    - Live copies go into Architecture/{principles,planning_prompts}/**.
    - Archive copies mirror original structure under legacy_knowledge_archive/architectural/**.
    """

    actions: List[PlannedAction] = []

    if not n5os_arch_root.exists():
        logger.info("N5OS architectural source missing: %s", n5os_arch_root)
        return actions

    archive_arch_root = archive_legacy_root / "architectural"

    for src in n5os_arch_root.rglob("*"):
        if not src.is_file():
            continue

        rel = src.relative_to(n5os_arch_root)

        # Live architecture mapping
        if rel.parts[0] == "principles":
            live_dest = architecture_root / "principles" / Path(*rel.parts[1:])
        elif src.name == "starter_planning_prompt.md":
            live_dest = architecture_root / "planning_prompts" / src.name
        elif "principles" in src.name.lower():
            live_dest = architecture_root / "principles" / src.name
        else:
            live_dest = architecture_root / "specs" / "n5os-core" / rel

        actions.append(
            PlannedAction(
                action="copy",
                src=str(src),
                dest=str(live_dest),
                reason="N5OS architectural → Architecture (live)",
            )
        )

        # Archive copy mirrors original tree under .../architectural/**
        archive_dest = archive_arch_root / rel
        actions.append(
            PlannedAction(
                action="copy",
                src=str(src),
                dest=str(archive_dest),
                reason="N5OS architectural → legacy archive (mirror)",
            )
        )

    return actions


def execute_actions(
    actions: List[PlannedAction],
    *,
    dry_run: bool,
    mode: str,
) -> Tuple[int, int]:
    """Execute planned actions, respecting .n5protected.

    Returns (executed_count, skipped_protected_count).
    """

    from shutil import copy2, move

    executed = 0
    skipped_protected = 0

    for action in actions:
        src = Path(action.src)
        dest = Path(action.dest)

        # Apply mode override: in move mode, upgrade copies to moves when safe
        effective_action = action.action
        if mode == "move" and action.action == "copy":
            effective_action = "move"

        # .n5protected checks on both source and destination roots
        src_protected, src_reason = is_protected(src)
        dest_protected, dest_reason = is_protected(dest.parent)

        if src_protected or dest_protected:
            action.protected = True
            action.protected_reason = src_reason or dest_reason or "protected path"
            skipped_protected += 1
            logger.warning(
                "Skipping %s → %s due to protection: %s",
                src,
                dest,
                action.protected_reason,
            )
            continue

        logger.info(
            "%s %s → %s (%s)",
            "DRY-RUN" if dry_run else effective_action.upper(),
            src,
            dest,
            action.reason,
        )

        if dry_run:
            continue

        ensure_dir(dest.parent)

        if effective_action == "copy":
            copy2(src, dest)
        elif effective_action == "move":
            move(src, dest)
        else:  # pragma: no cover - defensive
            logger.error("Unknown action type: %s", effective_action)
            continue

        executed += 1

    return executed, skipped_protected


def write_report(report_dir: Path, report: MigrationReport) -> Path:
    """Write migration report as JSON in report_dir and return its path."""

    ensure_dir(report_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = report_dir / f"architecture_migration_report_{timestamp}.json"

    payload = asdict(report)
    # Convert dataclasses in lists to dicts manually
    payload["ambiguous_specs"] = [asdict(a) for a in report.ambiguous_specs]

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote architecture migration report → %s", out_path)
    return out_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate legacy architecture docs into Personal/Knowledge/Architecture, "
            "with optional archive copies. Non-destructive by default."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and log operations without modifying any files (default).",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "move"],
        default="copy",
        help=(
            "When not in dry-run, choose whether to copy (preserve sources) or move "
            "(relocate) files. Default: copy."
        ),
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=WORKSPACE / "Personal/Knowledge/Logs",
        help="Directory to write JSON migration report (default: Personal/Knowledge/Logs)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Respect explicit dry-run flag (recommended for initial runs)
    dry_run = bool(args.dry_run)

    if args.mode not in {"copy", "move"}:
        parser.error("--mode must be 'copy' or 'move'")

    try:
        paths = load_paths()
    except Exception as exc:
        logger.error("Failed to load knowledge_paths.yaml: %s", exc)
        return 1

    architecture_root = paths["architecture_root"].resolve()
    wisdom_root = paths["wisdom_root"].resolve()
    legacy_root = paths["legacy_root"].resolve()
    archive_legacy_root = paths["archive_legacy_root"].resolve()

    specs_root = WORKSPACE / "Personal/Knowledge/Specs"
    n5os_arch_root = WORKSPACE / "Inbox/20251028-132904_n5os-core/Knowledge/architectural"

    all_actions: List[PlannedAction] = []
    ambiguous_specs: List[AmbiguousSpec] = []
    notes: List[str] = []

    # Legacy systems + infrastructure
    all_actions.extend(plan_legacy_systems(legacy_root, architecture_root))

    # Specs classification
    specs_actions, ambiguous = plan_specs_directory(specs_root, architecture_root, wisdom_root)
    all_actions.extend(specs_actions)
    ambiguous_specs.extend(ambiguous)

    # N5OS architectural tree
    all_actions.extend(
        plan_n5os_architectural(n5os_arch_root, architecture_root, archive_legacy_root)
    )

    if not all_actions and not ambiguous_specs:
        logger.info("No architecture-related migrations planned. Nothing to do.")
        return 0

    logger.info(
        "Planned %d file operations (%s mode). Dry-run=%s",
        len(all_actions),
        args.mode,
        dry_run,
    )

    executed, skipped_protected = execute_actions(
        all_actions,
        dry_run=dry_run,
        mode=args.mode,
    )

    if ambiguous_specs:
        notes.append(
            f"{len(ambiguous_specs)} specs left in-place for manual classification (see ambiguous_specs)."
        )

    if skipped_protected:
        notes.append(f"{skipped_protected} actions skipped due to .n5protected markers.")

    report = MigrationReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode=args.mode,
        dry_run=dry_run,
        actions_planned=len(all_actions),
        actions_executed=executed,
        actions_skipped_protected=skipped_protected,
        ambiguous_specs=ambiguous_specs,
        notes=notes,
    )

    report_path = write_report(args.report_dir, report)

    logger.info(
        "Architecture migration complete. Planned=%d, Executed=%d, Protected-skipped=%d, Ambiguous-specs=%d",
        len(all_actions),
        executed,
        skipped_protected,
        len(ambiguous_specs),
    )
    logger.info("Report: %s", report_path)

    # Non-zero exit only if something went wrong structurally
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


