#!/usr/bin/env python3
"""Canon & Content Library import script (Worker 8).

Scans legacy knowledge locations and classifies files into:
- Canon (Company + V/SocialContent)
- ContentLibrary references
- (Optionally) Archive

Writes a manifest JSONL log for executed imports.

Usage:
    python3 N5/scripts/knowledge_import_canon_contentlibrary.py --dry-run
    python3 N5/scripts/knowledge_import_canon_contentlibrary.py --execute
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Root of the workspace
ROOT = Path("/home/workspace").resolve()

# Source locations
STABLE_COMPANY_DIR = ROOT / "Personal/Knowledge/Legacy_Inbox/stable/company"
SEMI_STABLE_DIR = ROOT / "Personal/Knowledge/Legacy_Inbox/semi_stable"
SOCIAL_CONTENT_DIR = ROOT / "Personal/Knowledge/Legacy_Inbox/personal-brand/social-content"
ARTICLES_DIR = ROOT / "Documents/Knowledge/Articles"

# Target locations
CANON_BASE = ROOT / "Personal/Knowledge/Canon"
CANON_COMPANY_DIR = CANON_BASE / "Company"
CANON_COMPANY_SNAPSHOTS_DIR = CANON_COMPANY_DIR / "Snapshots"
CANON_V_SOCIAL_DIR = CANON_BASE / "V" / "SocialContent"
CONTENT_LIBRARY_DIR = ROOT / "Personal/Knowledge/ContentLibrary/content"

# Manifest
MANIFEST_PATH = ROOT / "Records/Personal/knowledge-system/canon_content_import_manifest.jsonl"


@dataclass
class ImportDecision:
    source: Path
    target: Path
    classification: str  # canon | content_library | archive | skip
    grade: str
    domain: str
    stability: str
    reason: Optional[str] = None
    status: str = "planned"  # planned | copied | skipped_existing | skipped_error


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )


def iter_candidate_files() -> List[Path]:
    """Return a sorted list of candidate files from the configured sources."""
    candidates: List[Path] = []

    def add_dir(dir_path: Path) -> None:
        if not dir_path.exists():
            logging.debug("Source directory missing, skipping: %s", dir_path)
            return
        for path in dir_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt"}:
                continue
            candidates.append(path)

    add_dir(STABLE_COMPANY_DIR)
    add_dir(SEMI_STABLE_DIR)
    add_dir(SOCIAL_CONTENT_DIR)
    add_dir(ARTICLES_DIR)

    # Sort for deterministic behaviour
    return sorted(candidates, key=lambda p: str(p))


def classify_file(path: Path) -> Optional[ImportDecision]:
    """Classify a file into canon/content_library/archive/skip and choose a target.

    Heuristics:
    - stable/company → Canon/Company (durable)
    - semi_stable/* (non-README) → Canon/Company/Snapshots (time_bound)
    - personal-brand/social-content/** → Canon/V/SocialContent (time_bound)
    - Documents/Knowledge/Articles/** → ContentLibrary/content (time_bound)
    - README.md in any source → skip
    """
    # Global skips
    if path.name.lower() == "readme.md":
        return None

    # Company stable canon
    if path.is_relative_to(STABLE_COMPANY_DIR):
        rel = path.relative_to(STABLE_COMPANY_DIR)
        target = CANON_COMPANY_DIR / rel
        return ImportDecision(
            source=path,
            target=target,
            classification="canon",
            grade="knowledge",
            domain="company",
            stability="durable",
            reason="stable/company canon",
        )

    # Company semi-stable snapshots (e.g. *_current, metrics, etc.)
    if path.is_relative_to(SEMI_STABLE_DIR):
        # Treat everything except README as a snapshot
        if path.name.lower() == "readme.md":
            return None
        target = CANON_COMPANY_SNAPSHOTS_DIR / path.name
        return ImportDecision(
            source=path,
            target=target,
            classification="canon",
            grade="knowledge",
            domain="company",
            stability="time_bound",
            reason="semi_stable snapshot",
        )

    # V canon / personal brand social content
    if path.is_relative_to(SOCIAL_CONTENT_DIR):
        rel = path.relative_to(SOCIAL_CONTENT_DIR)
        target = CANON_V_SOCIAL_DIR / rel
        return ImportDecision(
            source=path,
            target=target,
            classification="canon",
            grade="knowledge",
            domain="personal_brand",
            stability="time_bound",
            reason="personal-brand/social-content",
        )

    # Articles → ContentLibrary
    if path.is_relative_to(ARTICLES_DIR):
        rel = path.relative_to(ARTICLES_DIR)
        target = CONTENT_LIBRARY_DIR / rel
        return ImportDecision(
            source=path,
            target=target,
            classification="content_library",
            grade="knowledge",
            domain="reference",
            stability="time_bound",
            reason="Documents/Knowledge/Articles",
        )

    # Anything else is ignored by this worker
    return None


def ensure_frontmatter(target: Path, decision: ImportDecision) -> None:
    """Ensure the target file has minimal YAML frontmatter.

    If the file already starts with '---', it is left unchanged.
    Otherwise, a small frontmatter block is prepended.
    """
    try:
        text = target.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to read target for frontmatter %s: %s", target, exc)
        return

    # If it already looks like it has frontmatter, do nothing
    stripped = text.lstrip()
    if stripped.startswith("---"):
        logging.debug("Frontmatter already present, skipping: %s", target)
        return

    fm_lines = [
        "---",
        f"grade: {decision.grade}",
        f"domain: {decision.domain}",
        f"stability: {decision.stability}",
        "form: artifact",
        "---",
        "",
    ]
    new_text = "\n".join(fm_lines) + text

    try:
        target.write_text(new_text, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to write frontmatter to %s: %s", target, exc)


def append_manifest(decision: ImportDecision) -> None:
    """Append a JSON line for this decision to the manifest (on execute only)."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "source": str(decision.source),
        "target": str(decision.target),
        "classification": decision.classification,
        "grade": decision.grade,
        "domain": decision.domain,
        "stability": decision.stability,
        "status": decision.status,
        "reason": decision.reason,
    }
    with MANIFEST_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def execute_decisions(decisions: List[ImportDecision], dry_run: bool) -> None:
    counts = {
        "canon": 0,
        "content_library": 0,
        "archive": 0,
        "skipped_existing": 0,
        "skipped_error": 0,
    }

    for dec in decisions:
        if dec.classification not in counts:
            counts[dec.classification] = 0

        msg_prefix = "DRY-RUN" if dry_run else "EXECUTE"
        logging.info(
            "%s: %s → %s [%s, stability=%s]",
            msg_prefix,
            dec.source,
            dec.target,
            dec.classification,
            dec.stability,
        )

        if dry_run:
            counts[dec.classification] += 1
            continue

        try:
            dec.target.parent.mkdir(parents=True, exist_ok=True)
            if dec.target.exists():
                # If target already exists, skip but record in manifest
                dec.status = "skipped_existing"
                counts["skipped_existing"] += 1
                logging.warning("Target already exists, skipping copy: %s", dec.target)
            else:
                shutil.copy2(dec.source, dec.target)
                ensure_frontmatter(dec.target, dec)
                dec.status = "copied"
                counts[dec.classification] += 1

            append_manifest(dec)
        except Exception as exc:  # noqa: BLE001
            dec.status = "skipped_error"
            counts["skipped_error"] += 1
            logging.error("Error processing %s → %s: %s", dec.source, dec.target, exc)
            append_manifest(dec)

    logging.info("--- Summary ---")
    logging.info("Canon: %s", counts.get("canon", 0))
    logging.info("ContentLibrary: %s", counts.get("content_library", 0))
    logging.info("Archive: %s", counts.get("archive", 0))
    logging.info("Skipped (existing): %s", counts.get("skipped_existing", 0))
    logging.info("Skipped (errors): %s", counts.get("skipped_error", 0))


def build_decisions(limit: Optional[int] = None) -> List[ImportDecision]:
    files = iter_candidate_files()
    decisions: List[ImportDecision] = []
    for path in files:
        dec = classify_file(path)
        if dec is None:
            continue
        decisions.append(dec)
        if limit is not None and len(decisions) >= limit:
            break
    return decisions


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import canon and content-library files into the new knowledge architecture.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan the imports without copying any files (default).",
    )
    mode.add_argument(
        "--execute",
        action="store_true",
        help="Actually copy files and write manifest entries.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of files to process (for testing).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    args = parser.parse_args(argv)
    if not args.dry_run and not args.execute:
        # Default to dry-run if neither flag is provided
        args.dry_run = True
    return args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(verbose=args.verbose)

    logging.info("Workspace root: %s", ROOT)
    logging.info("Manifest path: %s", MANIFEST_PATH)

    decisions = build_decisions(limit=args.limit)
    if not decisions:
        logging.info("No candidate files found for import.")
        return 0

    logging.info("Planned decisions: %d", len(decisions))
    execute_decisions(decisions, dry_run=args.dry_run)

    if args.dry_run:
        logging.info("Dry-run complete. No files were copied. Run with --execute to apply changes.")
    else:
        logging.info("Execution complete. Manifest written to: %s", MANIFEST_PATH)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

