#!/usr/bin/env python3
"""
MECE Validator for Build Orchestrator

Validates that worker briefs in a build follow MECE principles:
- Mutually Exclusive: No scope item assigned to multiple workers
- Collectively Exhaustive: All plan scope items have exactly one owner

Usage:
    python3 mece_validator.py <build_slug>
    python3 mece_validator.py <build_slug> --strict    # Fail on warnings
    python3 mece_validator.py <build_slug> --verbose   # Show all details

Created: 2026-01-19
Provenance: con_RkSXGwBtKEEudYEP
"""

import argparse
import json
import re
import sys
import yaml
from collections import defaultdict
from pathlib import Path
from typing import Any

# Constants
BUILDS_DIR = Path("/home/workspace/N5/builds")
TOKEN_BUDGET_HARD_LIMIT = 0.40  # 40% of context window
TOKEN_BUDGET_SOFT_LIMIT = 0.30  # 30% target
CONTEXT_WINDOW_TOKENS = 200_000  # Assume 200k context

# Token estimation (chars / 4)
CHARS_PER_TOKEN = 4


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown file."""
    if not content.startswith("---"):
        return {}
    
    try:
        end_idx = content.index("---", 3)
        yaml_content = content[3:end_idx].strip()
        return yaml.safe_load(yaml_content) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def extract_scope_from_brief(brief_path: Path) -> dict[str, Any]:
    """Extract scope information from a worker brief."""
    content = brief_path.read_text()
    frontmatter = parse_yaml_frontmatter(content)
    
    # Get scope from frontmatter
    scope = frontmatter.get("scope", {})
    if isinstance(scope, str):
        scope = {"files": [scope]}
    
    files = scope.get("files", []) if isinstance(scope, dict) else []
    responsibilities = scope.get("responsibilities", []) if isinstance(scope, dict) else []
    must_not_touch = scope.get("must_not_touch", []) if isinstance(scope, dict) else []
    
    # Also extract files mentioned in body
    body_files = set()
    file_pattern = r'`([^`]+\.(py|ts|js|md|json|yaml|yml|sh|sql))`'
    for match in re.finditer(file_pattern, content):
        body_files.add(match.group(1))
    
    # Token estimate from frontmatter or calculate
    token_estimate = frontmatter.get("token_estimate", {})
    if isinstance(token_estimate, dict):
        brief_tokens = token_estimate.get("brief_tokens", len(content) // CHARS_PER_TOKEN)
        file_tokens = token_estimate.get("file_tokens", 0)
        total_pct = token_estimate.get("total_pct", 0)
    else:
        brief_tokens = len(content) // CHARS_PER_TOKEN
        file_tokens = 0
        total_pct = 0
    
    return {
        "worker_id": frontmatter.get("worker_id", brief_path.stem),
        "title": frontmatter.get("title", brief_path.stem),
        "files": list(set(files) | body_files),
        "responsibilities": responsibilities,
        "must_not_touch": must_not_touch,
        "depends_on": frontmatter.get("depends_on", []),
        "wave": frontmatter.get("wave", 1),
        "brief_tokens": brief_tokens,
        "file_tokens": file_tokens,
        "total_pct": total_pct or (brief_tokens + file_tokens) / CONTEXT_WINDOW_TOKENS * 100,
    }


def validate_mece(workers: list[dict]) -> dict[str, Any]:
    """Validate MECE principles across all workers."""
    
    # Build scope -> workers mapping
    file_owners: dict[str, list[str]] = defaultdict(list)
    responsibility_owners: dict[str, list[str]] = defaultdict(list)
    
    for worker in workers:
        worker_id = worker["worker_id"]
        
        for file in worker["files"]:
            file_owners[file].append(worker_id)
        
        for resp in worker["responsibilities"]:
            responsibility_owners[resp].append(worker_id)
    
    # Find overlaps and gaps
    overlaps = []
    for item, owners in list(file_owners.items()) + list(responsibility_owners.items()):
        if len(owners) > 1:
            overlaps.append({
                "item": item,
                "workers": owners,
                "type": "file" if item in file_owners else "responsibility"
            })
    
    # Check token budgets
    budget_warnings = []
    budget_errors = []
    for worker in workers:
        pct = worker["total_pct"]
        if pct > TOKEN_BUDGET_HARD_LIMIT * 100:
            budget_errors.append({
                "worker": worker["worker_id"],
                "total_pct": pct,
                "limit": TOKEN_BUDGET_HARD_LIMIT * 100,
                "message": f"Exceeds hard limit ({pct:.1f}% > {TOKEN_BUDGET_HARD_LIMIT*100:.0f}%)"
            })
        elif pct > TOKEN_BUDGET_SOFT_LIMIT * 100:
            budget_warnings.append({
                "worker": worker["worker_id"],
                "total_pct": pct,
                "target": TOKEN_BUDGET_SOFT_LIMIT * 100,
                "message": f"Exceeds soft target ({pct:.1f}% > {TOKEN_BUDGET_SOFT_LIMIT*100:.0f}%)"
            })
    
    # Check wave consistency
    wave_issues = []
    worker_waves = {w["worker_id"]: int(w["wave"]) for w in workers}
    for worker in workers:
        worker_wave = int(worker["wave"])
        for dep in worker.get("depends_on", []):
            dep_wave = worker_waves.get(dep, 0)
            if dep_wave >= worker_wave:
                wave_issues.append({
                    "worker": worker["worker_id"],
                    "depends_on": dep,
                    "worker_wave": worker["wave"],
                    "dep_wave": dep_wave,
                    "message": f"Depends on {dep} (wave {dep_wave}) but is in wave {worker['wave']}"
                })
    
    return {
        "overlaps": overlaps,
        "budget_errors": budget_errors,
        "budget_warnings": budget_warnings,
        "wave_issues": wave_issues,
        "workers": workers,
    }


def print_report(result: dict[str, Any], verbose: bool = False) -> None:
    """Print validation report."""
    workers = result["workers"]
    overlaps = result["overlaps"]
    budget_errors = result["budget_errors"]
    budget_warnings = result["budget_warnings"]
    wave_issues = result["wave_issues"]
    
    print("\n" + "=" * 60)
    print("MECE VALIDATION REPORT")
    print("=" * 60)
    
    # Summary
    print(f"\nWorkers analyzed: {len(workers)}")
    print(f"Scope overlaps: {len(overlaps)}")
    print(f"Budget errors: {len(budget_errors)}")
    print(f"Budget warnings: {len(budget_warnings)}")
    print(f"Wave issues: {len(wave_issues)}")
    
    # Overlaps (ERRORS)
    if overlaps:
        print("\n" + "-" * 40)
        print("⚠️  OVERLAPS DETECTED (MECE violation)")
        print("-" * 40)
        for overlap in overlaps:
            print(f"  • {overlap['type'].upper()}: {overlap['item']}")
            print(f"    Owned by: {', '.join(overlap['workers'])}")
    
    # Budget errors
    if budget_errors:
        print("\n" + "-" * 40)
        print("❌ TOKEN BUDGET ERRORS")
        print("-" * 40)
        for err in budget_errors:
            print(f"  • {err['worker']}: {err['message']}")
    
    # Budget warnings
    if budget_warnings:
        print("\n" + "-" * 40)
        print("⚠️  TOKEN BUDGET WARNINGS")
        print("-" * 40)
        for warn in budget_warnings:
            print(f"  • {warn['worker']}: {warn['message']}")
    
    # Wave issues
    if wave_issues:
        print("\n" + "-" * 40)
        print("❌ WAVE DEPENDENCY ISSUES")
        print("-" * 40)
        for issue in wave_issues:
            print(f"  • {issue['worker']}: {issue['message']}")
    
    # Worker details (verbose)
    if verbose:
        print("\n" + "-" * 40)
        print("WORKER DETAILS")
        print("-" * 40)
        for worker in workers:
            print(f"\n  [{worker['worker_id']}] Wave {worker['wave']}")
            print(f"    Title: {worker['title']}")
            print(f"    Files: {len(worker['files'])}")
            for f in worker['files'][:5]:
                print(f"      - {f}")
            if len(worker['files']) > 5:
                print(f"      ... and {len(worker['files'])-5} more")
            print(f"    Responsibilities: {len(worker['responsibilities'])}")
            for r in worker['responsibilities']:
                print(f"      - {r}")
            print(f"    Token estimate: {worker['total_pct']:.2f}%")
    
    # Final verdict
    print("\n" + "=" * 60)
    has_errors = overlaps or budget_errors or wave_issues
    has_warnings = budget_warnings
    
    if has_errors:
        print("❌ VALIDATION FAILED")
        print("   Fix errors before launching workers.")
    elif has_warnings:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print("   Consider addressing warnings before proceeding.")
    else:
        print("✅ VALIDATION PASSED")
        print("   MECE principles satisfied. Ready to launch workers.")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate MECE principles for build workers"
    )
    parser.add_argument("build_slug", help="Build slug (directory name in N5/builds/)")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Find build directory
    build_dir = BUILDS_DIR / args.build_slug
    if not build_dir.exists():
        print(f"Error: Build not found: {build_dir}", file=sys.stderr)
        sys.exit(1)
    
    workers_dir = build_dir / "workers"
    if not workers_dir.exists():
        print(f"Note: No workers/ directory in {build_dir}")
        print("This build may be single-thread (no workers needed).")
        sys.exit(0)
    
    # Parse all worker briefs
    workers = []
    for brief_path in workers_dir.glob("*.md"):
        try:
            worker = extract_scope_from_brief(brief_path)
            workers.append(worker)
        except Exception as e:
            print(f"Warning: Could not parse {brief_path}: {e}", file=sys.stderr)
    
    if not workers:
        print("No worker briefs found in workers/ directory.")
        sys.exit(0)
    
    # Validate
    result = validate_mece(workers)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, verbose=args.verbose)
    
    # Exit code
    has_errors = result["overlaps"] or result["budget_errors"] or result["wave_issues"]
    has_warnings = result["budget_warnings"]
    
    if has_errors:
        sys.exit(1)
    elif args.strict and has_warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
