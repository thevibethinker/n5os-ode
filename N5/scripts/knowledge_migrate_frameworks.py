#!/usr/bin/env python3
"""Knowledge Frameworks & Reasoning Patterns Migration Script.

Phase 4/5 implementation for consolidating patterns, hypotheses, and
reasoning-patterns under Personal/Knowledge/Frameworks/** and creating
compatibility stubs for Knowledge/reasoning-patterns/**.

Dry-run mode is recommended for initial runs:
- --dry-run prints planned operations only.
- Without --dry-run, operations are executed.

Sources:
- Personal/Knowledge/Legacy_Inbox/patterns/*.md
- Personal/Knowledge/Legacy_Inbox/hypotheses/*.md
- Personal/Knowledge/Legacy_Inbox/reasoning-patterns/*.md
- Knowledge/reasoning-patterns/*.md

Targets:
- Personal/Knowledge/Frameworks/Patterns/**
- Personal/Knowledge/Frameworks/Hypotheses/**
- (Future) Personal/Knowledge/Frameworks/{Strategic,Operational}/** for general frameworks
- Knowledge/reasoning-patterns/*.md converted to compatibility stubs

The script is .n5protected-aware via N5/scripts/n5_protect.check_protected.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
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
logger = logging.getLogger("knowledge_migrate_frameworks")


@dataclass
class PlannedAction:
    """Representation of a planned file operation."""

    action: str  # "copy" or "move" or "stub"
    src: str
    dest: str
    reason: str
    protected: bool = False
    protected_reason: Optional[str] = None


@dataclass
class MigrationReport:
    """Aggregate report for a migration run."""

    timestamp: str
    mode: str
    dry_run: bool
    actions_planned: int
    actions_executed: int
    actions_skipped_protected: int
    notes: List[str]


def load_paths() -> Dict[str, Path]:
    """Load knowledge paths config and resolve key roots as Paths."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")

    data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    pk = data.get("personal_knowledge", {})

    frameworks_root = WORKSPACE / pk.get("frameworks", "Personal/Knowledge/Frameworks")
    legacy_root = WORKSPACE / "Personal/Knowledge/Legacy_Inbox"
    legacy_compat_root = WORKSPACE / "Knowledge"

    return {
        "frameworks_root": frameworks_root,
        "legacy_root": legacy_root,
        "legacy_compat_root": legacy_compat_root,
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


def plan_legacy_frameworks(
    legacy_root: Path, frameworks_root: Path
) -> List[PlannedAction]:
    """Plan migrations from Legacy_Inbox patterns/hypotheses/reasoning-patterns."""

    actions: List[PlannedAction] = []

    patterns_src = legacy_root / "patterns"
    hypotheses_src = legacy_root / "hypotheses"
    legacy_reasoning_src = legacy_root / "reasoning-patterns"

    patterns_dest_root = frameworks_root / "Patterns"
    hypotheses_dest_root = frameworks_root / "Hypotheses"

    mapping = [
        (patterns_src, patterns_dest_root, "Legacy patterns → Frameworks/Patterns"),
        (hypotheses_src, hypotheses_dest_root, "Legacy hypotheses → Frameworks/Hypotheses"),
        (
            legacy_reasoning_src,
            patterns_dest_root,
            "Legacy reasoning-patterns → Frameworks/Patterns",
        ),
    ]

    for src_root, dest_root, label in mapping:
        if not src_root.exists():
            logger.info("Skipping %s; source missing: %s", label, src_root)
            continue

        for src in sorted(src_root.glob("*.md")):
            dest = dest_root / src.name
            actions.append(
                PlannedAction(
                    action="copy",
                    src=str(src),
                    dest=str(dest),
                    reason=label,
                )
            )

    return actions


def plan_reasoning_patterns_stubs(
    legacy_compat_root: Path, frameworks_root: Path
) -> List[PlannedAction]:
    """Plan migrations + stub creation for Knowledge/reasoning-patterns/*.md.

    For each pattern:
    - Copy to Frameworks/Patterns/<filename>.md
    - Replace original with a compatibility stub pointing to canonical path
    (when actually executed, not in dry-run).
    """

    actions: List[PlannedAction] = []

    compat_reasoning_root = legacy_compat_root / "reasoning-patterns"
    patterns_dest_root = frameworks_root / "Patterns"

    if not compat_reasoning_root.exists():
        logger.info("Compatibility reasoning-patterns root not found: %s", compat_reasoning_root)
        return actions

    for src in sorted(compat_reasoning_root.glob("*.md")):
        dest = patterns_dest_root / src.name
        canonical_rel = f"Personal/Knowledge/Frameworks/Patterns/{src.name}"

        # Copy action
        actions.append(
            PlannedAction(
                action="copy",
                src=str(src),
                dest=str(dest),
                reason="Compatibility reasoning-pattern → Frameworks/Patterns",
            )
        )

        # Stub action (in-place rewrite)
        actions.append(
            PlannedAction(
                action="stub",
                src=str(src),  # src == dest for stub writes
                dest=str(src),
                reason=f"Convert to compatibility stub → {canonical_rel}",
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

    today = date.today().isoformat()

    for action in actions:
        src = Path(action.src)
        dest = Path(action.dest)

        # Apply mode override: in move mode, upgrade copies to moves when safe
        effective_action = action.action
        if mode == "move" and action.action == "copy":
            effective_action = "move"

        # .n5protected checks (source for copy/move; file itself for stubs)
        check_target = dest if action.action == "stub" else dest.parent

        src_protected, src_reason = is_protected(src)
        dest_protected, dest_reason = is_protected(check_target)

        if src_protected or dest_protected:
            action.protected = True
            action.protected_reason = src_reason or dest_reason or "protected path"
            skipped_protected += 1
            logger.warning(
                "Skipping %s %s → %s due to protection: %s",
                action.action,
                src,
                dest,
                action.protected_reason,
            )
            continue

        logger.info(
            "%s %s %s → %s (%s)",
            "DRY-RUN" if dry_run else effective_action.upper(),
            action.action,
            src,
            dest,
            action.reason,
        )

        if dry_run:
            continue

        if action.action in {"copy", "move"}:
            ensure_dir(dest.parent)
            if effective_action == "copy":
                copy2(src, dest)
            elif effective_action == "move":
                move(src, dest)
            else:  # pragma: no cover - defensive
                logger.error("Unknown action type: %s", effective_action)
                continue
        elif action.action == "stub":
            # Write compatibility stub with required YAML frontmatter
            canonical_rel = f"Personal/Knowledge/Frameworks/Patterns/{src.name}"
            stub_content = (
                "---\n"
                f"created: {today}\n"
                f"last_edited: {today}\n"
                "version: 1.0\n"
                "role: compatibility_stub\n"
                f"canonical_path: {canonical_rel}\n"
                "---\n\n"
                f"This reasoning pattern now lives at `{canonical_rel}`.\n"
            )
            dest.write_text(stub_content, encoding="utf-8")
        else:  # pragma: no cover - defensive
            logger.error("Unknown action type: %s", action.action)
            continue

        executed += 1

    return executed, skipped_protected


def write_report(report_dir: Path, report: MigrationReport) -> Path:
    """Write migration report as JSON in report_dir and return its path."""

    ensure_dir(report_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = report_dir / f"frameworks_migration_report_{timestamp}.json"

    payload = asdict(report)

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote frameworks migration report → %s", out_path)
    return out_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate patterns, hypotheses, and reasoning-patterns into "
            "Personal/Knowledge/Frameworks, and convert legacy reasoning-patterns "
            "to compatibility stubs. Non-destructive by default when run with --dry-run."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and log operations without modifying any files.",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "move"],
        default="copy",
        help=(
            "When not in dry-run, choose whether to copy (preserve sources) or move "
            "(relocate) files for Legacy_Inbox sources. Default: copy."
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

    dry_run = bool(args.dry_run)

    if args.mode not in {"copy", "move"}:
        parser.error("--mode must be 'copy' or 'move'")

    try:
        paths = load_paths()
    except Exception as exc:
        logger.error("Failed to load knowledge_paths.yaml: %s", exc)
        return 1

    frameworks_root = paths["frameworks_root"].resolve()
    legacy_root = paths["legacy_root"].resolve()
    legacy_compat_root = paths["legacy_compat_root"].resolve()

    all_actions: List[PlannedAction] = []
    notes: List[str] = []

    # Legacy patterns/hypotheses/reasoning-patterns
    all_actions.extend(plan_legacy_frameworks(legacy_root, frameworks_root))

    # Compatibility reasoning-patterns stubs
    all_actions.extend(plan_reasoning_patterns_stubs(legacy_compat_root, frameworks_root))

    if not all_actions:
        logger.info("No framework-related migrations planned. Nothing to do.")
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

    if skipped_protected:
        notes.append(f"{skipped_protected} actions skipped due to .n5protected markers.")

    report = MigrationReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode=args.mode,
        dry_run=dry_run,
        actions_planned=len(all_actions),
        actions_executed=executed,
        actions_skipped_protected=skipped_protected,
        notes=notes,
    )

    report_path = write_report(args.report_dir, report)

    logger.info(
        "Frameworks migration complete. Planned=%d, Executed=%d, Protected-skipped=%d",
        len(all_actions),
        executed,
        skipped_protected,
    )
    logger.info("Report: %s", report_path)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


