#!/usr/bin/env python3
"""Content classification engine for the Zoffice Consultancy Stack."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path("/home/workspace")
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
TIERS_CONFIG = CONFIG_DIR / "tiers.json"
REDACTION_CONFIG = CONFIG_DIR / "redaction-patterns.json"
EXPORT_MANIFEST_PATH = Path("/home/workspace/N5/builds/consulting-zoffice-stack/CONSULTING_MANIFEST.json")


def load_json_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def compute_checksum(path: Path) -> str:
    if path.is_dir():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def has_n5protected(path: Path) -> bool:
    current = path if path.is_dir() else path.parent
    for ancestor in [current] + list(current.parents):
        if (ancestor / ".n5protected").exists():
            return True
    return False


def classify_path(path: Path) -> Tuple[str, str]:
    path = path.expanduser()
    config = load_json_config(TIERS_CONFIG)
    patterns = load_json_config(REDACTION_CONFIG)
    tier2_dirs = config.get("tier2_dirs", [])
    tier1_dirs = config.get("tier1_dirs", [])

    rel_path = None
    try:
        rel_path = path.relative_to(WORKSPACE_ROOT)
    except Exception:
        rel_path = path
    parts = [str(p) for p in rel_path.parts]

    for marker in tier2_dirs:
        if marker in parts:
            return "Tier 2", f"Path contains tier2 marker '{marker}'"

    if has_n5protected(path):
        return "Tier 1", ".n5protected marker present (review required)"

    lower_text = ""
    if path.is_file():
        try:
            lower_text = path.read_text(errors="ignore").lower()
        except Exception:
            lower_text = ""
    for keyword in patterns.get("tier2_keywords", []):
        if keyword in lower_text:
            return "Tier 2", f"Keyword '{keyword}' detected in content"

    for marker in tier1_dirs:
        if marker in parts:
            return "Tier 1", f"Path lives under tier1 directory '{marker}'"

    for keyword in patterns.get("tier1_keywords", []):
        if keyword in lower_text:
            return "Tier 1", f"Keyword '{keyword}' detected in content"

    return "Tier 0", "No sensitive indicators detected"


def classify_directory(target: Path) -> List[Dict]:
    if not target.exists():
        return []
    results = []
    for entry in target.iterdir():
        if entry.name.startswith("."):
            continue
        tier, reason = classify_path(entry)
        stats = entry.stat()
        results.append({
            "path": str(entry.relative_to(WORKSPACE_ROOT)),
            "tier": tier,
            "reason": reason,
            "modified_at": datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc).isoformat(),
            "size": stats.st_size
        })
    return results


def build_manifest(since: Optional[str] = None) -> Dict:
    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since)
        if since_dt.tzinfo is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)
    git_sha = None
    try:
        git_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
    except Exception:
        git_sha = "unknown"

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "va_version": git_sha,
        "bundles": [],
        "review_queue": [],
        "excluded": []
    }

    paths_to_include = [
        WORKSPACE_ROOT / "Skills",
        WORKSPACE_ROOT / "Documents/System",
        WORKSPACE_ROOT / "Prompts",
        WORKSPACE_ROOT / "N5/docs"
    ]

    for base in paths_to_include:
        if not base.exists():
            continue
        for entry in base.iterdir():
            if entry.name.startswith("."):
                continue
            stats = entry.stat()
            modified_at = datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc)
            if since_dt and modified_at < since_dt:
                continue
            tier, reason = classify_path(entry)
            bundle = {
                "name": entry.name,
                "tier": tier,
                "path": str(entry.relative_to(WORKSPACE_ROOT)),
                "version": "1.0.0",
                "last_modified": modified_at.isoformat(),
                "checksum": compute_checksum(entry) if entry.is_file() else "",
                "files": [p.name for p in entry.iterdir()] if entry.is_dir() else [entry.name],
                "reason": reason
            }
            manifest["bundles"].append(bundle)
            if tier == "Tier 1":
                manifest["review_queue"].append(bundle)
            elif tier == "Tier 2":
                manifest["excluded"].append(bundle)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Zoffice Workspace Content Classifier")
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify_parser = subparsers.add_parser("classify", help="Classify a specific path")
    classify_parser.add_argument("--path", required=True, help="Path to classify")
    classify_parser.add_argument("--output", help="Optional JSON output path")

    manifest_parser = subparsers.add_parser("manifest", help="Generate export manifest")
    manifest_parser.add_argument("--since", help="Only include files modified after ISO timestamp")
    manifest_parser.add_argument("--output", default=str(EXPORT_MANIFEST_PATH))

    check_parser = subparsers.add_parser("check", help="Check a single path and print tier")
    check_parser.add_argument("--path", required=True)

    args = parser.parse_args()

    if args.command == "classify":
        target = Path(args.path)
        entries = classify_directory(target)
        result = {"entries": entries}
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))

    elif args.command == "manifest":
        manifest = build_manifest(args.since)
        Path(args.output).write_text(json.dumps(manifest, indent=2))
        print(f"Manifest written to {args.output}")

    elif args.command == "check":
        target = Path(args.path)
        tier, reason = classify_path(target)
        print(json.dumps({"tier": tier, "reason": reason}, indent=2))


if __name__ == "__main__":
    main()
