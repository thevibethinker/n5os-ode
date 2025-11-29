#!/usr/bin/env python3
"""Knowledge alignment audit helper for Worker 9.

Scans the legacy `Knowledge/**` tree and reports:
- Non-stub markdown files (outside known compatibility shells)
- Unexpected DBs and logs under Knowledge/**
- Status of CRM/architectural/reasoning-patterns compatibility areas

Usage:
    python3 N5/scripts/knowledge_alignment_audit.py
    python3 N5/scripts/knowledge_alignment_audit.py --json

This script is read-only; it does not modify the filesystem.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path("/home/workspace")
LEGACY_KNOWLEDGE = ROOT / "Knowledge"


def is_stub_markdown(path: Path, size_threshold: int = 2_048) -> bool:
    """Heuristic to detect stub/compat markdown files.

    - Very small files (<= size_threshold bytes) are treated as stubs.
    - Larger files that contain obvious compatibility language are also stubs.
    """
    try:
        if path.stat().st_size <= size_threshold:
            return True
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to read %s while checking stub status: %s", path, exc)
        return False

    lowered = text.lower()
    if "compatibility shell" in lowered or "compatibility shim" in lowered:
        return True
    if "canonical" in lowered and "personal/knowledge" in lowered:
        return True
    return False


def audit_knowledge_tree() -> Dict[str, object]:
    """Perform the alignment audit and return a structured report dict."""
    report: Dict[str, object] = {
        "root_exists": LEGACY_KNOWLEDGE.exists(),
        "non_stub_markdowns": [],
        "unexpected_dbs": [],
        "unexpected_logs": [],
        "crm_individuals_stub_ok": True,
        "crm_individuals_non_stub": [],
        "reasoning_patterns_stub_ok": True,
        "reasoning_patterns_non_stub": [],
        "architectural_ok": True,
        "architectural_unexpected": [],
    }

    if not LEGACY_KNOWLEDGE.exists():
        logger.info("Legacy Knowledge/ root does not exist; nothing to audit.")
        return report

    # Known compatibility areas
    crm_individuals_root = LEGACY_KNOWLEDGE / "crm" / "individuals"
    reasoning_root = LEGACY_KNOWLEDGE / "reasoning-patterns"
    architectural_root = LEGACY_KNOWLEDGE / "architectural"
    allowed_architectural = {
        architectural_root / "architectural_principles.md",
        architectural_root / "ingestion_standards.md",
        architectural_root / "operational_principles.md",
    }

    # Walk full tree once
    for path in LEGACY_KNOWLEDGE.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(LEGACY_KNOWLEDGE).as_posix()

        # DBs and logs anywhere under Knowledge/**
        if path.suffix.lower() == ".db":
            report["unexpected_dbs"].append(rel)
            continue
        if path.suffix.lower() in {".log", ".sqlite", ".sqlite3"}:
            report["unexpected_logs"].append(rel)
            continue

        # Markdown handling
        if path.suffix.lower() == ".md":
            # Architectural compatibility shell
            if path.parent == architectural_root:
                if path not in allowed_architectural:
                    report["architectural_ok"] = False
                    report["architectural_unexpected"].append(rel)
                continue

            # CRM individuals compatibility area
            if crm_individuals_root in path.parents:
                if not is_stub_markdown(path):
                    report["crm_individuals_stub_ok"] = False
                    report["crm_individuals_non_stub"].append(rel)
                continue

            # Reasoning patterns compatibility area
            if reasoning_root in path.parents:
                if not is_stub_markdown(path):
                    report["reasoning_patterns_stub_ok"] = False
                    report["reasoning_patterns_non_stub"].append(rel)
                continue

            # Everything else: treat non-stub markdowns as interesting
            if not is_stub_markdown(path):
                report["non_stub_markdowns"].append(rel)

    return report


def log_human_summary(report: Dict[str, object]) -> None:
    logger.info("=== Knowledge Alignment Audit ===")
    if not report["root_exists"]:
        logger.info("Knowledge/ root missing; assuming fully migrated.")
        return

    non_stub = report["non_stub_markdowns"] or []
    dbs = report["unexpected_dbs"] or []
    logs = report["unexpected_logs"] or []

    logger.info("Knowledge/ root: %s", LEGACY_KNOWLEDGE)
    logger.info("Non-stub markdowns (outside compatibility zones): %d", len(non_stub))
    logger.info("Unexpected DBs under Knowledge/**: %d", len(dbs))
    logger.info("Unexpected logs under Knowledge/**: %d", len(logs))

    if non_stub:
        logger.info("Examples of non-stub markdowns:")
        for rel in non_stub[:10]:
            logger.info("  - %s", rel)
        if len(non_stub) > 10:
            logger.info("  ... and %d more", len(non_stub) - 10)

    logger.info(
        "CRM individuals stub OK: %s (non-stub count=%d)",
        report["crm_individuals_stub_ok"],
        len(report["crm_individuals_non_stub"] or []),
    )
    logger.info(
        "Reasoning-patterns stub OK: %s (non-stub count=%d)",
        report["reasoning_patterns_stub_ok"],
        len(report["reasoning_patterns_non_stub"] or []),
    )
    logger.info(
        "Architectural compatibility shell OK: %s (unexpected files=%d)",
        report["architectural_ok"],
        len(report["architectural_unexpected"] or []),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit legacy Knowledge/ tree alignment")
    parser.add_argument("--json", action="store_true", help="Emit JSON report to stdout")
    args = parser.parse_args()

    report = audit_knowledge_tree()
    log_human_summary(report)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    # Never fail the pipeline purely from audit; this is informational.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

