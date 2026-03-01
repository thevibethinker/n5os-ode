#!/usr/bin/env python3
"""
promote.py — Promote a completed build to a first-class Skill.

Consumes lineage_analyzer and artifact_classifier output to migrate
operational files, adapt paths, generate SKILL.md, and finalize the build.

Usage:
    python3 Skills/build-promote/scripts/promote.py run <slug> [--name <skill-slug>] [--dry-run] [--yes]
    python3 Skills/build-promote/scripts/promote.py preview <slug>
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SKILLS_DIR = WORKSPACE / "Skills"

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))
from artifact_classifier import classify_build
from lineage_analyzer import get_base_name, scan_all_builds

# Path replacement order: most specific first
PATH_REPLACEMENT_TEMPLATES = [
    ("N5/builds/{build}/workspace/state", "Skills/{skill}/state"),
    ("N5/builds/{build}/workspace/memory", "Skills/{skill}/state/memory"),
    ("N5/builds/{build}/workspace/staging", "Skills/{skill}/state/staging"),
    ("N5/builds/{build}/workspace/analytics", "Skills/{skill}/state/analytics"),
    ("N5/builds/{build}/workspace/learnings", "Skills/{skill}/state/learnings"),
    ("N5/builds/{build}/workspace/posts", "Skills/{skill}/state/posts"),
    ("N5/builds/{build}/workspace", "Skills/{skill}/state"),
    ("N5/builds/{build}/artifacts", "Skills/{skill}/assets"),
    ("N5/builds/{build}/scripts", "Skills/{skill}/scripts"),
]

# Category → target directory mapping
CATEGORY_TARGET_DIR = {
    "operational_script": "scripts",
    "governance": "assets",
    "runtime_state": "state",
    "prompt": "prompts",
    "reference": "references",
    "static_asset": "assets",
}


def propose_skill_name(slug: str) -> str:
    """Propose a clean skill slug from a build slug."""
    return get_base_name(slug)


def run_promotion(slug: str, skill_name: str, dry_run: bool = False,
                  auto_yes: bool = False, cluster_mode: bool = False) -> dict:
    """Execute the full promotion workflow."""
    result = {
        "slug": slug,
        "skill_name": skill_name,
        "dry_run": dry_run,
        "steps": [],
        "files_moved": 0,
        "paths_adapted": 0,
        "success": False,
    }

    build_dir = BUILDS_DIR / slug
    skill_dir = SKILLS_DIR / skill_name

    # === Step 1: Pre-flight ===
    step1 = {"name": "pre_flight", "status": "pass", "details": ""}

    if not build_dir.exists():
        step1["status"] = "fail"
        step1["details"] = f"Build not found: {build_dir}"
        result["steps"].append(step1)
        return result

    meta_path = build_dir / "meta.json"
    meta = None
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
        except json.JSONDecodeError:
            pass

    if meta:
        status = meta.get("status", "unknown")
        if status not in ("complete", "finalized", "active"):
            step1["status"] = "warn"
            step1["details"] = f"Build status is '{status}' — expected complete/finalized"
        if meta.get("transition_note"):
            step1["status"] = "fail"
            step1["details"] = f"Build already promoted: {meta['transition_note']}"
            result["steps"].append(step1)
            return result

    if skill_dir.exists() and (skill_dir / "SKILL.md").exists():
        step1["status"] = "fail"
        step1["details"] = f"Skill already exists: {skill_dir}. Use --name to specify a different slug."
        result["steps"].append(step1)
        return result

    step1["details"] = "Build validated, ready for promotion"
    result["steps"].append(step1)
    print(f"[1/9] Pre-flight: {step1['details']}", file=sys.stderr)

    # === Step 2: Name proposal ===
    step2 = {"name": "name_proposal", "status": "pass", "details": f"Skill slug: {skill_name}"}
    result["steps"].append(step2)
    print(f"[2/9] Name: {skill_name}", file=sys.stderr)

    # === Step 3: Classification ===
    classification = classify_build(slug)
    if "error" in classification:
        step3 = {"name": "classification", "status": "fail", "details": classification["error"]}
        result["steps"].append(step3)
        return result

    # Filter to only promotable files
    to_migrate = [
        c for c in classification["classifications"]
        if c["category"] in CATEGORY_TARGET_DIR and c["target"]
    ]

    step3 = {
        "name": "classification",
        "status": "pass",
        "details": f"{len(to_migrate)} files to migrate, {classification['total_files']} total",
        "summary": classification["summary"],
    }
    result["steps"].append(step3)
    print(f"[3/9] Classification: {len(to_migrate)} files to migrate", file=sys.stderr)

    if not to_migrate:
        print("  No operational files to migrate. Build may already be cleaned up.", file=sys.stderr)
        if not dry_run:
            # Still finalize the build
            _finalize_build(build_dir, meta, meta_path, skill_name)
        result["success"] = True
        return result

    # Show migration plan
    print(f"\n  Migration plan:", file=sys.stderr)
    for c in to_migrate:
        print(f"    {c['relative']} → {skill_name}/{c['target']}", file=sys.stderr)

    if dry_run:
        print(f"\n  [DRY RUN] No changes made.", file=sys.stderr)
        result["success"] = True
        return result

    if not auto_yes:
        print(f"\n  Proceed with promotion? [y/N] ", file=sys.stderr, end="")
        try:
            answer = input().strip().lower()
            if answer not in ("y", "yes"):
                print("  Aborted.", file=sys.stderr)
                return result
        except EOFError:
            print("  Non-interactive mode. Use --yes to auto-confirm.", file=sys.stderr)
            return result

    # === Step 4: Directory creation ===
    needed_dirs = set()
    for c in to_migrate:
        target_path = skill_dir / c["target"]
        needed_dirs.add(target_path.parent)

    for d in sorted(needed_dirs):
        d.mkdir(parents=True, exist_ok=True)

    step4 = {"name": "directory_creation", "status": "pass",
             "details": f"Created {len(needed_dirs)} directories"}
    result["steps"].append(step4)
    print(f"[4/9] Directories: {len(needed_dirs)} created", file=sys.stderr)

    # === Step 5: File migration ===
    migrated = 0
    for c in to_migrate:
        src = Path(c["path"])
        dst = skill_dir / c["target"]
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            migrated += 1

    result["files_moved"] = migrated
    step5 = {"name": "file_migration", "status": "pass", "details": f"{migrated} files copied"}
    result["steps"].append(step5)
    print(f"[5/9] Migration: {migrated} files copied", file=sys.stderr)

    # === Step 6: Path adaptation ===
    replacements = [
        (old.format(build=slug), new.format(skill=skill_name))
        for old, new in PATH_REPLACEMENT_TEMPLATES
    ]

    total_replacements = 0
    adapted_files = 0
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script_file in sorted(scripts_dir.iterdir()):
            if script_file.suffix not in (".py", ".ts", ".js"):
                continue
            try:
                content = script_file.read_text(encoding="utf-8")
                original = content
                for old_path, new_path in replacements:
                    if old_path in content:
                        count = content.count(old_path)
                        content = content.replace(old_path, new_path)
                        total_replacements += count

                # Remove sys.path.insert hacks referencing build path
                build_path_pattern = f"N5/builds/{slug}"
                lines = content.split("\n")
                cleaned_lines = []
                for line in lines:
                    if "sys.path.insert" in line and build_path_pattern in line:
                        total_replacements += 1
                        continue
                    if "sys.path.append" in line and build_path_pattern in line:
                        total_replacements += 1
                        continue
                    cleaned_lines.append(line)
                content = "\n".join(cleaned_lines)

                if content != original:
                    script_file.write_text(content, encoding="utf-8")
                    adapted_files += 1
            except (IOError, UnicodeDecodeError):
                pass

    result["paths_adapted"] = total_replacements
    step6 = {"name": "path_adaptation", "status": "pass",
             "details": f"{adapted_files} files, {total_replacements} replacements"}
    result["steps"].append(step6)
    print(f"[6/9] Path adaptation: {adapted_files} files, {total_replacements} replacements", file=sys.stderr)

    # === Step 7: SKILL.md generation ===
    skill_md = _generate_skill_md(slug, skill_name, meta, classification, skill_dir)
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(skill_md, encoding="utf-8")

    step7 = {"name": "skill_md", "status": "pass", "details": f"Generated {skill_md_path}"}
    result["steps"].append(step7)
    print(f"[7/9] SKILL.md: Generated (draft)", file=sys.stderr)

    # === Step 8: Protection markers ===
    state_dir = skill_dir / "state"
    if state_dir.exists():
        n5p = state_dir / ".n5protected"
        if not n5p.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            n5p.write_text(
                f"Protected: runtime state for {skill_name}\n"
                f"Promoted from: N5/builds/{slug}\n"
                f"Date: {today}\n"
            )

    step8 = {"name": "protection", "status": "pass", "details": "Markers set"}
    result["steps"].append(step8)
    print(f"[8/9] Protection: markers set", file=sys.stderr)

    # === Step 9: Build finalization ===
    _finalize_build(build_dir, meta, meta_path, skill_name)
    _cleanup_build(build_dir, to_migrate)

    step9 = {"name": "build_finalization", "status": "pass",
             "details": f"Build finalized, operational files removed"}
    result["steps"].append(step9)
    print(f"[9/9] Build finalized: operational files removed from build", file=sys.stderr)

    result["success"] = True

    # Summary
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"  Promotion complete: {skill_name}", file=sys.stderr)
    print(f"  Files moved:     {result['files_moved']}", file=sys.stderr)
    print(f"  Paths adapted:   {result['paths_adapted']}", file=sys.stderr)
    print(f"  SKILL.md:        Skills/{skill_name}/SKILL.md (draft)", file=sys.stderr)
    print(f"  Build finalized: N5/builds/{slug}/", file=sys.stderr)
    print(f"\n  Next: python3 Skills/build-promote/scripts/verify.py check {skill_name}", file=sys.stderr)

    return result


def _finalize_build(build_dir: Path, meta: dict | None, meta_path: Path, skill_name: str):
    """Update build meta.json with transition info."""
    if meta is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    today = datetime.now().strftime("%Y-%m-%d")
    if meta.get("status") not in ("complete", "finalized"):
        meta["status"] = "complete"
    meta["completed_at"] = meta.get("completed_at") or now
    meta["transition_note"] = (
        f"Promoted to Skills/{skill_name}/. Build folder retained as historical record."
    )
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _cleanup_build(build_dir: Path, migrated_files: list):
    """Remove migrated operational files from build, keep scaffolding."""
    for c in migrated_files:
        src = Path(c["path"])
        if src.exists():
            src.unlink()

    # Clean up empty directories left behind
    for d in sorted(build_dir.rglob("*"), reverse=True):
        if d.is_dir():
            try:
                d.rmdir()  # Only removes empty dirs
            except OSError:
                pass

    # Clear __pycache__
    for pycache in build_dir.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)


def _generate_skill_md(slug: str, skill_name: str, meta: dict | None,
                       classification: dict, skill_dir: Path) -> str:
    """Generate a draft SKILL.md."""
    title = meta.get("title", skill_name) if meta else skill_name
    objective = meta.get("objective", "") if meta else ""
    today = datetime.now().strftime("%Y-%m-%d")

    # Find scripts
    scripts_dir = skill_dir / "scripts"
    scripts = []
    if scripts_dir.exists():
        for f in sorted(scripts_dir.iterdir()):
            if f.suffix in (".py", ".ts", ".js"):
                scripts.append(f.name)

    # Find state directories
    state_dir = skill_dir / "state"
    state_subdirs = []
    if state_dir.exists():
        for d in sorted(state_dir.iterdir()):
            if d.is_dir() and d.name != "__pycache__":
                state_subdirs.append(d.name)

    # Build directory tree
    tree_lines = [f"Skills/{skill_name}/"]
    tree_lines.append(f"├── SKILL.md")
    if scripts_dir.exists():
        tree_lines.append(f"├── scripts/")
        for s in scripts:
            tree_lines.append(f"│   └── {s}")
    assets_dir = skill_dir / "assets"
    if assets_dir.exists():
        tree_lines.append(f"├── assets/")
    prompts_dir = skill_dir / "prompts"
    if prompts_dir.exists():
        tree_lines.append(f"├── prompts/")
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        tree_lines.append(f"├── references/")
    if state_dir.exists():
        tree_lines.append(f"└── state/")
        for sd in state_subdirs:
            tree_lines.append(f"    ├── {sd}/")

    tree = "\n".join(tree_lines)

    # Scripts table
    scripts_table = "| Script | Description |\n|--------|-------------|\n"
    for s in scripts:
        scripts_table += f"| `{s}` | *(review and document)* |\n"

    md = f"""---
name: {skill_name}
description: {objective or title}
compatibility: Created for Zo Computer
status: draft
metadata:
  author: va.zo.computer
  promoted_from: {slug}
  promoted_at: "{today}"
---

# {title}

> **Status:** Draft — review and finalize after promotion.

## Overview

{objective or f"Skill promoted from build `{slug}`."}

## Directory Structure

```
{tree}
```

## Scripts

{scripts_table}

## How to Invoke

```bash
# List available commands
python3 Skills/{skill_name}/scripts/<script>.py --help
```

## Configuration

- State directory: `Skills/{skill_name}/state/`
- Build origin: `N5/builds/{slug}/`

## Dependencies

- Python 3.10+
- stdlib only (no external packages)
"""
    return md


def cmd_run(args):
    """Execute promotion."""
    slug = args.slug
    skill_name = args.name or propose_skill_name(slug)
    result = run_promotion(
        slug, skill_name,
        dry_run=args.dry_run,
        auto_yes=args.yes,
        cluster_mode=args.cluster,
    )

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)

    return 0 if result["success"] else 1


def cmd_preview(args):
    """Preview promotion (alias for run --dry-run)."""
    slug = args.slug
    skill_name = args.name or propose_skill_name(slug)
    result = run_promotion(slug, skill_name, dry_run=True, auto_yes=True)

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)

    return 0 if result["success"] else 1


def main():
    parser = argparse.ArgumentParser(
        description="Promote a completed build to a first-class Skill.",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_run = subparsers.add_parser("run", help="Execute promotion")
    p_run.add_argument("slug", help="Build slug to promote")
    p_run.add_argument("--name", "-n", help="Skill slug (default: derived from build slug)")
    p_run.add_argument("--dry-run", action="store_true", help="Preview without changes")
    p_run.add_argument("--yes", "-y", action="store_true", help="Auto-confirm")
    p_run.add_argument("--cluster", action="store_true", help="Promote from cluster canonical")
    p_run.add_argument("--json", action="store_true", help="JSON output")

    p_preview = subparsers.add_parser("preview", help="Preview promotion (dry-run)")
    p_preview.add_argument("slug", help="Build slug to preview")
    p_preview.add_argument("--name", "-n", help="Skill slug override")
    p_preview.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "run": cmd_run,
        "preview": cmd_preview,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
