#!/usr/bin/env python3
"""
artifact_classifier.py — Classify build artifacts for promotion routing.

Inspects every file in a build folder and classifies it into categories
that determine where it goes during promotion to a Skill.

Usage:
    python3 Skills/build-promote/scripts/artifact_classifier.py classify <slug>
    python3 Skills/build-promote/scripts/artifact_classifier.py classify <slug> --json
    python3 Skills/build-promote/scripts/artifact_classifier.py classify-cluster <slug>
"""

import argparse
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
STATE_DIR = WORKSPACE / "Skills" / "build-promote" / "state"

# Build scaffolding files that stay in the build
SCAFFOLDING_NAMES = {
    "meta.json",
    "PLAN.md",
    "STATUS.md",
    "BUILD.md",
    "BUILD_LESSONS.json",
    "FINALIZATION.json",
    ".n5protected",
}

SCAFFOLDING_DIRS = {
    "workers",
    "completions",
    "deposits",
    "drops",
}

# Governance keywords (case-insensitive) for content inspection
GOVERNANCE_KEYWORDS = [
    "constitution",
    "persona",
    "rubric",
    "pii",
    "privacy",
    "boundaries",
    "governance",
    "policy",
    "guidelines",
    "compliance",
    "ethics",
    "identity",
    "voice guidelines",
]

# Prompt-related keywords
PROMPT_KEYWORDS = [
    "system prompt",
    "you are",
    "your role",
    "instructions:",
    "## prompt",
    "## system",
    "assistant_prompt",
    "user_prompt",
]

# State directories within workspace/
STATE_DIRS = {
    "state",
    "memory",
    "staging",
    "analytics",
    "learnings",
    "cache",
    "data",
    "logs",
}

# Image extensions
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}


def classify_file(file_path: Path, build_root: Path) -> dict:
    """Classify a single file."""
    rel = file_path.relative_to(build_root)
    parts = rel.parts
    name = file_path.name
    ext = file_path.suffix.lower()

    result = {
        "path": str(build_root / rel),
        "relative": str(rel),
        "category": "unknown",
        "target": None,
        "confidence": "low",
        "reason": "",
    }

    # === Layer 1: Heuristic (path/extension-based) ===

    # Scaffolding check (top-level build files)
    if name in SCAFFOLDING_NAMES:
        result["category"] = "build_scaffolding"
        result["target"] = None  # stays in build
        result["confidence"] = "high"
        result["reason"] = f"Build scaffolding file: {name}"
        return result

    # Scaffolding directories
    if parts and parts[0] in SCAFFOLDING_DIRS:
        result["category"] = "build_scaffolding"
        result["target"] = None
        result["confidence"] = "high"
        result["reason"] = f"Build scaffolding directory: {parts[0]}/"
        return result

    # __pycache__ and .pyc
    if "__pycache__" in parts or ext == ".pyc":
        result["category"] = "obsolete"
        result["target"] = None
        result["confidence"] = "high"
        result["reason"] = "Python bytecode cache"
        return result

    # Scripts
    if ext in (".py", ".ts", ".js", ".sh") and (
        "scripts" in parts or "scripts" == (parts[0] if parts else "")
    ):
        result["category"] = "operational_script"
        result["target"] = f"scripts/{name}"
        result["confidence"] = "high"
        result["reason"] = f"Script in scripts/ directory"
        return result

    # Standalone scripts outside scripts/ dir
    if ext in (".py", ".ts") and len(parts) == 1:
        # Check if it looks like a CLI script
        result["category"] = "operational_script"
        result["target"] = f"scripts/{name}"
        result["confidence"] = "medium"
        result["reason"] = f"Script at build root"
        return result

    # Workspace state directories
    if parts and parts[0] == "workspace":
        sub = parts[1] if len(parts) > 1 else ""
        if sub in STATE_DIRS or sub == "posts":
            result["category"] = "runtime_state"
            # Map workspace/X/... → state/X/...
            state_path = str(rel).replace("workspace/", "", 1)
            # Collapse workspace/state/X → state/X (avoid state/state)
            if state_path.startswith("state/"):
                result["target"] = f"state/{state_path[6:]}" if len(state_path) > 6 else "state/"
            else:
                result["target"] = f"state/{state_path}"
            result["confidence"] = "high"
            result["reason"] = f"Runtime state in workspace/{sub}/"
            return result

        # Workspace root files
        result["category"] = "runtime_state"
        state_path = str(rel).replace("workspace/", "", 1)
        result["target"] = f"state/{state_path}"
        result["confidence"] = "medium"
        result["reason"] = "File in workspace/ directory"
        return result

    # Images in artifacts/
    if ext in IMAGE_EXTS:
        result["category"] = "static_asset"
        result["target"] = f"assets/{name}"
        result["confidence"] = "high"
        result["reason"] = f"Image file: {ext}"
        return result

    # Prompts directory
    if parts and parts[0] == "prompts":
        result["category"] = "prompt"
        result["target"] = f"prompts/{name}"
        result["confidence"] = "high"
        result["reason"] = "File in prompts/ directory"
        return result

    # References directory
    if parts and parts[0] == "references":
        result["category"] = "reference"
        result["target"] = f"references/{name}"
        result["confidence"] = "high"
        result["reason"] = "File in references/ directory"
        return result

    # Artifacts directory — needs content inspection
    if parts and parts[0] == "artifacts":
        if ext in IMAGE_EXTS:
            result["category"] = "static_asset"
            result["target"] = f"assets/{name}"
            result["confidence"] = "high"
            result["reason"] = f"Image in artifacts/"
            return result
        # Default: governance doc, but will be refined by content inspection
        if ext == ".md":
            result["category"] = "governance"
            result["target"] = f"assets/{name}"
            result["confidence"] = "medium"
            result["reason"] = "Markdown in artifacts/ (default governance)"

    # === Layer 2: Content inspection for ambiguous files ===
    if result["category"] in ("unknown", "governance") and ext in (".md", ".txt", ".py", ".ts"):
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            first_lines = content[:3000].lower()

            # Check for governance signals
            gov_hits = sum(1 for kw in GOVERNANCE_KEYWORDS if kw in first_lines)
            if gov_hits >= 2:
                result["category"] = "governance"
                result["target"] = f"assets/{name}"
                result["confidence"] = "high" if gov_hits >= 3 else "medium"
                result["reason"] = f"Governance keywords detected ({gov_hits} matches)"
                return result

            # Check for prompt signals
            prompt_hits = sum(1 for kw in PROMPT_KEYWORDS if kw in first_lines)
            if prompt_hits >= 2:
                result["category"] = "prompt"
                result["target"] = f"prompts/{name}"
                result["confidence"] = "medium"
                result["reason"] = f"Prompt keywords detected ({prompt_hits} matches)"
                return result

            # Check if Python file has CLI (argparse)
            if ext == ".py" and ("argparse" in first_lines or "if __name__" in first_lines):
                result["category"] = "operational_script"
                result["target"] = f"scripts/{name}"
                result["confidence"] = "high"
                result["reason"] = "Python script with CLI"
                return result

            # Check if it's a reference/spec doc
            if ext == ".md" and any(
                kw in first_lines
                for kw in ["api", "endpoint", "specification", "documentation", "reference"]
            ):
                result["category"] = "reference"
                result["target"] = f"references/{name}"
                result["confidence"] = "medium"
                result["reason"] = "Reference/spec document"
                return result

        except (IOError, UnicodeDecodeError):
            pass

    # If still governance from artifacts/ heuristic, keep it
    if result["category"] == "governance":
        return result

    # Binary files or other unknown
    if ext in IMAGE_EXTS:
        result["category"] = "static_asset"
        result["target"] = f"assets/{name}"
        result["confidence"] = "medium"
        result["reason"] = f"Image file"
        return result

    # DB files
    if ext in (".db", ".sqlite", ".sqlite3", ".duckdb"):
        result["category"] = "runtime_state"
        result["target"] = f"state/{name}"
        result["confidence"] = "medium"
        result["reason"] = "Database file"
        return result

    # JSON/JSONL data files (not at root)
    if ext in (".json", ".jsonl") and len(parts) > 1:
        result["category"] = "runtime_state"
        sub_path = "/".join(parts[:-1])
        result["target"] = f"state/{sub_path}/{name}"
        result["confidence"] = "medium"
        result["reason"] = f"Data file in {sub_path}/"
        return result

    # Mark remaining as intermediate
    if result["category"] == "unknown":
        result["category"] = "intermediate"
        result["confidence"] = "low"
        result["reason"] = "Could not classify — review manually"

    return result


def classify_build(slug: str) -> dict:
    """Classify all files in a build."""
    build_root = BUILDS_DIR / slug
    if not build_root.exists():
        return {"error": f"Build not found: {slug}"}

    classifications = []
    summary = {}

    for file_path in sorted(build_root.rglob("*")):
        if not file_path.is_file():
            continue
        result = classify_file(file_path, build_root)
        classifications.append(result)
        cat = result["category"]
        summary[cat] = summary.get(cat, 0) + 1

    return {
        "build_slug": slug,
        "build_path": str(build_root),
        "total_files": len(classifications),
        "classifications": classifications,
        "summary": summary,
    }


def cmd_classify(args):
    """Classify all files in a build."""
    result = classify_build(args.slug)

    if "error" in result:
        print(result["error"], file=sys.stderr)
        return 1

    if args.json:
        json.dump(result, sys.stdout, indent=2)
    else:
        print(f"\n=== Classification: {args.slug} ===", file=sys.stderr)
        print(f"Total files: {result['total_files']}", file=sys.stderr)
        print(f"\nSummary:", file=sys.stderr)
        for cat, count in sorted(result["summary"].items()):
            print(f"  {cat}: {count}", file=sys.stderr)

        # Group by category
        by_cat = {}
        for c in result["classifications"]:
            cat = c["category"]
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(c)

        for cat in sorted(by_cat.keys()):
            items = by_cat[cat]
            print(f"\n--- {cat} ({len(items)}) ---", file=sys.stderr)
            for item in items:
                conf = item["confidence"]
                target = item["target"] or "(stays in build)"
                print(
                    f"  [{conf}] {item['relative']} → {target}",
                    file=sys.stderr,
                )
                if conf == "low":
                    print(f"         reason: {item['reason']}", file=sys.stderr)

    return 0


def cmd_classify_cluster(args):
    """Classify across a build cluster."""
    # Try to load lineage data
    lineage_path = STATE_DIR / "lineage.json"
    if lineage_path.exists():
        try:
            lineage = json.loads(lineage_path.read_text())
        except (json.JSONDecodeError, IOError):
            lineage = None
    else:
        # Run inline scan
        sys.path.insert(0, str(Path(__file__).parent))
        try:
            from lineage_analyzer import scan_all_builds
            lineage = scan_all_builds()
        except ImportError:
            print("lineage.json not found. Run: lineage_analyzer.py scan --save", file=sys.stderr)
            return 1

    # Find the cluster
    cluster_id = lineage.get("slug_to_cluster", {}).get(args.slug)
    if not cluster_id:
        print(f"Build '{args.slug}' not found in lineage data", file=sys.stderr)
        return 1

    cluster = lineage["clusters"][cluster_id]
    builds = cluster["builds"]
    canonical = cluster["canonical"]

    print(f"\n=== Cluster Classification: {cluster_id} ===", file=sys.stderr)
    print(f"Builds: {builds}", file=sys.stderr)
    print(f"Canonical: {canonical}", file=sys.stderr)

    all_results = {}
    for slug in builds:
        result = classify_build(slug)
        if "error" not in result:
            all_results[slug] = result

    # Cross-reference: mark files in non-canonical builds as obsolete
    # if the canonical build has a newer version
    canonical_files = set()
    if canonical in all_results:
        for c in all_results[canonical]["classifications"]:
            canonical_files.add(Path(c["relative"]).name)

    for slug in builds:
        if slug == canonical or slug not in all_results:
            continue
        for c in all_results[slug]["classifications"]:
            fname = Path(c["relative"]).name
            if fname in canonical_files and c["category"] not in (
                "build_scaffolding",
                "obsolete",
            ):
                c["category"] = "obsolete"
                c["confidence"] = "medium"
                c["reason"] = f"Superseded by same file in canonical build: {canonical}"

    if args.json:
        json.dump(
            {
                "cluster_id": cluster_id,
                "canonical": canonical,
                "builds": all_results,
            },
            sys.stdout,
            indent=2,
        )
    else:
        for slug, result in all_results.items():
            marker = " (canonical)" if slug == canonical else ""
            print(f"\n--- {slug}{marker} ---", file=sys.stderr)
            print(f"  Files: {result['total_files']}", file=sys.stderr)
            for cat, count in sorted(result["summary"].items()):
                print(f"    {cat}: {count}", file=sys.stderr)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Classify build artifacts for promotion routing.",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_classify = subparsers.add_parser("classify", help="Classify a single build")
    p_classify.add_argument("slug", help="Build slug")
    p_classify.add_argument("--json", action="store_true", help="JSON output")
    p_classify.add_argument("--dry-run", action="store_true", help="Preview only (same as default)")

    p_cluster = subparsers.add_parser(
        "classify-cluster", help="Classify across a build cluster"
    )
    p_cluster.add_argument("slug", help="Any build slug in the cluster")
    p_cluster.add_argument("--json", action="store_true", help="JSON output")
    p_cluster.add_argument("--dry-run", action="store_true", help="Preview only")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "classify": cmd_classify,
        "classify-cluster": cmd_classify_cluster,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
