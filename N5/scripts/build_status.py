#!/usr/bin/env python3
"""
build_status.py - Global view of all builds across N5/builds/.

Commands:
    list                    List all builds with status
    list --incomplete       Show only active/in-progress builds
    list --json             Output machine-readable JSON
    list --all              Show all complete builds (not just recent)
    regenerate              Write JSON to dashboard data file

Usage:
    python3 N5/scripts/build_status.py list
    python3 N5/scripts/build_status.py list --incomplete
    python3 N5/scripts/build_status.py list --json
    python3 N5/scripts/build_status.py regenerate
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
DASHBOARD_DATA_DIR = WORKSPACE / "Sites" / "build-tracker" / "data"
DASHBOARD_DATA_FILE = DASHBOARD_DATA_DIR / "builds.json"
STALE_THRESHOLD_DAYS = 60  # Builds inactive for 60+ days become stale/backlog
RECENT_COMPLETE_LIMIT = 10
TRACKER_EPOCH = "2026-01-18"  # Builds before this are "pre-tracker"


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format with timezone."""
    now = datetime.now().astimezone()
    return now.isoformat(timespec='seconds')


def get_file_mtime(path: Path) -> datetime | None:
    """Get file modification time as datetime, or None if doesn't exist."""
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return None


def parse_date_string(date_str: str | None) -> datetime | None:
    """Parse a date string (YYYY-MM-DD or ISO format) to datetime."""
    if not date_str:
        return None
    try:
        # Try ISO format first
        if 'T' in date_str:
            return datetime.fromisoformat(date_str)
        # Try simple date format
        return datetime.strptime(date_str, "%Y-%m-%d").astimezone()
    except (ValueError, TypeError):
        return None


def extract_objective(build_dir: Path) -> str | None:
    """Extract objective/description from PLAN.md if it exists.
    
    Returns None if:
    - PLAN.md doesn't exist
    - Objective line not found
    - Objective contains template placeholders like {{...}}
    """
    plan_file = build_dir / "PLAN.md"
    if not plan_file.exists():
        return None
    
    try:
        content = plan_file.read_text()
        # Look for **Objective:** line
        for line in content.split('\n'):
            if line.strip().startswith('**Objective:**'):
                # Extract the text after **Objective:**
                obj = line.replace('**Objective:**', '').strip()
                # Skip if it's a template placeholder
                if obj.startswith('{{') and obj.endswith('}}'):
                    return None
                # Skip if it contains any template markers
                if '{{' in obj:
                    return None
                # Truncate if too long
                if len(obj) > 200:
                    obj = obj[:197] + '...'
                return obj if obj else None
        return None
    except IOError:
        return None


def get_last_activity(build_dir: Path) -> datetime | None:
    """Get the most recent activity timestamp for a build.
    
    Checks: meta.json, completion files, worker briefs, PLAN.md
    Returns the most recent mtime, or None if no files found.
    """
    candidates = []
    
    # meta.json
    meta = build_dir / "meta.json"
    if meta.exists():
        candidates.append(get_file_mtime(meta))
    
    # PLAN.md
    plan = build_dir / "PLAN.md"
    if plan.exists():
        candidates.append(get_file_mtime(plan))
    
    # plan.json
    plan_json = build_dir / "plan.json"
    if plan_json.exists():
        candidates.append(get_file_mtime(plan_json))
    
    # Completion files
    completions_dir = build_dir / "completions"
    if completions_dir.exists():
        for f in completions_dir.glob("*.json"):
            candidates.append(get_file_mtime(f))
    
    # Worker briefs
    workers_dir = build_dir / "workers"
    if workers_dir.exists():
        for f in workers_dir.glob("*.md"):
            candidates.append(get_file_mtime(f))
    
    # Filter None and return max
    valid = [c for c in candidates if c is not None]
    return max(valid) if valid else None


def determine_build_status(
    created: str | None,
    complete_workers: int,
    total_workers: int,
    last_activity: datetime | None,
    is_legacy: bool = False
) -> str:
    """
    Determine build status based on workers and activity.
    
    Returns one of: "complete", "active", "draft", "stale", "pre-tracker"
    
    Args:
        created: ISO date string when build was created
        complete_workers: Number of completed workers
        total_workers: Total number of workers
        last_activity: Most recent activity timestamp
        is_legacy: If True, this is a legacy build without orchestration structure
    """
    # Check if complete
    if total_workers > 0 and complete_workers >= total_workers:
        return "complete"
    
    # Check if pre-tracker
    if created and created < TRACKER_EPOCH:
        return "pre-tracker"
    
    # Check if stale (backlog) - no activity in 60 days
    if last_activity:
        now = datetime.now().astimezone()
        threshold = now - timedelta(days=STALE_THRESHOLD_DAYS)
        if last_activity < threshold:
            return "stale"
    
    # If no workers defined:
    # - Legacy builds (no orchestration): assume complete (they predate worker system)
    # - Modern builds: draft (waiting for architect to define workers)
    if total_workers == 0:
        if is_legacy:
            return "complete"
        else:
            return "draft"
    
    # Otherwise active
    return "active"


def scan_build_v2(build_dir: Path) -> dict | None:
    """Scan a v2 build directory and extract status info."""
    meta_file = build_dir / "meta.json"
    if not meta_file.exists():
        return None
    
    try:
        meta = json.loads(meta_file.read_text())
    except (json.JSONDecodeError, IOError):
        return None
    
    # If meta.json explicitly says complete or abandoned, trust it (user closed/canceled the build)
    meta_status = meta.get("status")
    explicit_complete = meta_status == "complete"
    explicit_abandoned = meta_status == "abandoned"
    
    completions_dir = build_dir / "completions"
    workers_dir = build_dir / "workers"
    workers_data = meta.get("workers", {})
    
    # Determine total workers from meta.json
    # Handle two different workers schemas:
    # 1. New schema: workers: {total: X, complete: Y, ...}
    # 2. Old schema: workers: {W1.1: {...}, W1.2: {...}, ...}
    if "total" in workers_data:
        # New schema - use the provided total
        total_workers = workers_data.get("total", 0)
    else:
        # Old schema - workers is a dict of worker_id -> worker_info
        worker_ids = [k for k in workers_data.keys() if k.startswith("W")]
        total_workers = len(worker_ids)
    
    # ALWAYS count completion files as source of truth for complete count
    # (meta.json counts may be stale)
    complete_workers = 0
    if completions_dir.exists():
        completion_files = list(completions_dir.glob("W*.json"))
        complete_workers = len(completion_files)
    
    # If no workers in meta but we have worker briefs, count those
    if total_workers == 0 and workers_dir.exists():
        worker_briefs = list(workers_dir.glob("W*.md"))
        total_workers = len(worker_briefs)
    
    # Extract created date and objective
    created = meta.get("created")
    objective = extract_objective(build_dir)
    
    # Get last activity timestamp
    last_activity = get_last_activity(build_dir)
    last_activity_str = last_activity.isoformat(timespec='seconds') if last_activity else None
    
    # Determine status
    # If explicitly marked complete or abandoned in meta.json, trust it
    if explicit_complete:
        status = "complete"
        # For explicitly complete builds, use meta.json worker counts (more accurate)
        complete_workers = workers_data.get("complete", complete_workers)
        total_workers = workers_data.get("total", total_workers)
    elif explicit_abandoned:
        status = "abandoned"
    else:
        status = determine_build_status(created, complete_workers, total_workers, last_activity, is_legacy=False)
    
    # Calculate progress
    if total_workers > 0:
        progress_pct = round((complete_workers / total_workers) * 100)
    else:
        progress_pct = 0
    
    build_info = {
        "slug": meta.get("slug", build_dir.name),
        "title": meta.get("title", build_dir.name),
        "status": status,
        "type": meta.get("type", "unknown"),
        "created": meta.get("created"),
        "completed_at": meta.get("completed_at"),
        "last_activity": last_activity_str,
        "objective": objective,
        "workers": {
            "complete": complete_workers,
            "total": total_workers
        },
        "progress_pct": progress_pct,
        "path": str(build_dir.relative_to(WORKSPACE)),
        "_meta_mtime": get_file_mtime(meta_file),
        "_is_v2": True
    }
    
    return build_info


def scan_build_plan_json(build_dir: Path) -> dict | None:
    """Scan a build directory with plan.json but no meta.json."""
    plan_file = build_dir / "plan.json"
    if not plan_file.exists():
        return None
    
    try:
        plan = json.loads(plan_file.read_text())
    except (json.JSONDecodeError, IOError):
        return None
    
    completions_dir = build_dir / "completions"
    workers_dir = build_dir / "workers"
    
    # Count worker briefs for total (handle both W*.md and WORKER-*.md patterns)
    total_workers = 0
    if workers_dir.exists():
        # Count all .md files that look like worker briefs
        all_md = list(workers_dir.glob("*.md"))
        # Filter out non-worker files (like README.md, PLAN.md standalone)
        worker_briefs = [f for f in all_md if f.stem.upper().startswith(('W', 'WORKER'))]
        total_workers = len(worker_briefs)
    
    # Count completion files for complete (handle W*.json and worker-*.json)
    complete_workers = 0
    if completions_dir.exists():
        all_json = list(completions_dir.glob("*.json"))
        complete_workers = len(all_json)
    
    # Determine status based on completion
    if total_workers > 0 and complete_workers >= total_workers:
        status = "complete"
    elif complete_workers > 0 or total_workers > 0:
        status = "active"
    else:
        status = "active"
    
    # Extract objective from PLAN.md
    objective = extract_objective(build_dir)
    
    # Get title/name - plan.json might use "name", "title", or neither
    title = plan.get("title") or plan.get("name") or build_dir.name.replace("-", " ").title()
    slug = plan.get("slug") or build_dir.name
    
    # Get created date from plan.json or directory mtime
    created = plan.get("created")
    if not created:
        mtime = get_file_mtime(plan_file)
        created = mtime.strftime("%Y-%m-%d") if mtime else None
    
    # Get last activity
    last_activity = get_last_activity(build_dir)
    last_activity_str = last_activity.isoformat(timespec='seconds') if last_activity else None
    
    # Determine status
    status = determine_build_status(created, complete_workers, total_workers, last_activity, is_legacy=False)
    
    # Calculate progress
    if total_workers > 0:
        progress_pct = round((complete_workers / total_workers) * 100)
    else:
        progress_pct = 0
    
    build_info = {
        "slug": slug,
        "title": title,
        "status": status,
        "type": plan.get("type", "code_build"),
        "created": created,
        "completed_at": None,
        "last_activity": last_activity_str,
        "objective": objective,
        "workers": {
            "complete": complete_workers,
            "total": total_workers
        },
        "progress_pct": progress_pct,
        "path": str(build_dir.relative_to(WORKSPACE)),
        "_is_v2": True,
        "_meta_mtime": get_file_mtime(plan_file)
    }
    
    return build_info


def scan_build_legacy(build_dir: Path) -> dict | None:
    """Scan a legacy build (no meta.json, no plan.json) and extract info."""
    slug = build_dir.name
    
    # Check for workers/ and completions/ folders - if present, this might be active
    workers_dir = build_dir / "workers"
    completions_dir = build_dir / "completions"
    
    # Count workers and completions
    total_workers = 0
    complete_workers = 0
    
    if workers_dir.exists():
        all_md = list(workers_dir.glob("*.md"))
        worker_briefs = [f for f in all_md if f.stem.upper().startswith(('W', 'WORKER'))]
        total_workers = len(worker_briefs)
    
    if completions_dir.exists():
        all_json = list(completions_dir.glob("*.json"))
        complete_workers = len(all_json)
    
    # Determine status - if we have workers, it's a v2-style build
    has_v2_structure = total_workers > 0 or completions_dir.exists()
    
    if has_v2_structure:
        if total_workers > 0 and complete_workers >= total_workers:
            status = "complete"
            progress_pct = 100
        elif complete_workers > 0 or total_workers > 0:
            status = "active"
            progress_pct = round((complete_workers / total_workers) * 100) if total_workers > 0 else 0
        else:
            status = "active"
            progress_pct = 0
    else:
        # True legacy - no workers structure
        status = "complete"
        progress_pct = 100
    
    # Try to get created date from directory mtime or STATUS.md
    created = None
    status_file = build_dir / "STATUS.md"
    if status_file.exists():
        created_mtime = get_file_mtime(status_file)
        if created_mtime:
            created = created_mtime.strftime("%Y-%m-%d")
    
    if not created:
        dir_mtime = get_file_mtime(build_dir)
        if dir_mtime:
            created = dir_mtime.strftime("%Y-%m-%d")
    
    # Extract objective if PLAN.md exists
    objective = extract_objective(build_dir)
    
    # Get last activity
    last_activity = get_last_activity(build_dir)
    last_activity_str = last_activity.isoformat(timespec='seconds') if last_activity else None
    
    # Determine status - pass is_legacy=True for builds without orchestration structure
    status = determine_build_status(created, complete_workers, total_workers, last_activity, is_legacy=not has_v2_structure)
    
    build_info = {
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "status": status,
        "type": "code_build" if has_v2_structure else "legacy",
        "created": created,
        "completed_at": created if status == "complete" else None,
        "last_activity": last_activity_str,
        "objective": objective,
        "workers": {
            "complete": complete_workers,
            "total": total_workers
        },
        "progress_pct": progress_pct,
        "path": str(build_dir.relative_to(WORKSPACE)),
        "_is_v2": has_v2_structure
    }
    
    return build_info


def scan_all_builds() -> list[dict]:
    """Scan all builds in N5/builds/ and return build info list."""
    builds = []
    
    if not BUILDS_DIR.exists():
        return builds
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        
        # Try v2 format first (meta.json)
        build_info = scan_build_v2(build_dir)
        if build_info:
            builds.append(build_info)
            continue
        
        # Try plan.json format
        build_info = scan_build_plan_json(build_dir)
        if build_info:
            builds.append(build_info)
            continue
        
        # Fall back to legacy format
        build_info = scan_build_legacy(build_dir)
        if build_info:
            builds.append(build_info)
    
    # Mark pre-tracker builds
    for build in builds:
        created = build.get("created", "1970-01-01")
        if created < TRACKER_EPOCH and build.get("status") == "active":
            build["status"] = "pre-tracker"
            build["type"] = "pre-tracker"
    
    return builds


def sort_builds(builds: list[dict]) -> list[dict]:
    """Sort builds: active first, then by created date descending."""
    def sort_key(b):
        # Primary: active status (active=0, complete=1, unknown=2)
        status_order = {"active": 0, "in_progress": 0, "complete": 1}.get(b.get("status"), 2)
        # Secondary: created date (newer first)
        created = b.get("created") or "1970-01-01"
        return (status_order, created)
    
    # Sort by status first, then reverse sort by date (newest first)
    return sorted(builds, key=lambda b: (sort_key(b)[0], -hash(sort_key(b)[1])))


def filter_incomplete(builds: list[dict]) -> list[dict]:
    """Filter to only active/incomplete builds (excludes pre-tracker)."""
    return [b for b in builds if b.get("status") in ("active", "in_progress")]


def cmd_list(args):
    """List all builds."""
    builds = scan_all_builds()
    builds = sort_builds(builds)
    
    if args.incomplete:
        builds = filter_incomplete(builds)
    
    if args.as_json:
        output_json(builds, args.all)
        return
    
    output_human(builds, args.all, args.incomplete)


def output_json(builds: list[dict], show_all: bool):
    """Output builds in JSON format."""
    # Clean up internal fields
    clean_builds = []
    for b in builds:
        clean = {k: v for k, v in b.items() if not k.startswith("_")}
        clean_builds.append(clean)
    
    active_builds = [b for b in clean_builds if b.get("status") in ("active", "in_progress")]
    complete_builds = [b for b in clean_builds if b.get("status") == "complete"]
    stale_builds = [b for b in clean_builds if b.get("status") == "stale"]
    
    # Limit complete builds unless --all
    if not show_all and len(complete_builds) > RECENT_COMPLETE_LIMIT:
        complete_builds = complete_builds[:RECENT_COMPLETE_LIMIT]
    
    output = {
        "generated_at": get_iso_timestamp(),
        "builds": active_builds + complete_builds,
        "summary": {
            "total": len(clean_builds),
            "active": len(active_builds),
            "complete": len([b for b in clean_builds if b.get("status") == "complete"]),
            "stale": len(stale_builds)
        }
    }
    
    print(json.dumps(output, indent=2))


def output_human(builds: list[dict], show_all: bool, incomplete_only: bool):
    """Output builds in human-readable format."""
    active_builds = [b for b in builds if b.get("status") in ("active", "in_progress")]
    complete_builds = [b for b in builds if b.get("status") == "complete"]
    
    if active_builds:
        print("Active Builds:")
        for b in active_builds:
            stale_flag = " ⚠️ stale" if b.get("status") == "stale" else ""
            workers = b.get("workers", {})
            complete = workers.get("complete", 0)
            total = workers.get("total", 0)
            pct = b.get("progress_pct", 0)
            
            if total > 0:
                progress = f"{complete}/{total} workers ({pct}%)"
            else:
                progress = "legacy"
            
            build_type = b.get("type", "unknown")
            created = b.get("created", "unknown")
            
            print(f"  ● {b['slug']:<20} {progress:<20} {build_type:<12} {created}{stale_flag}")
        print()
    
    if not incomplete_only and complete_builds:
        display_complete = complete_builds if show_all else complete_builds[:RECENT_COMPLETE_LIMIT]
        remaining = len(complete_builds) - len(display_complete)
        
        label = "Complete Builds:" if show_all else "Complete Builds (recent):"
        print(label)
        for b in display_complete:
            workers = b.get("workers", {})
            complete = workers.get("complete", 0)
            total = workers.get("total", 0)
            
            if total > 0:
                progress = f"{complete}/{total} workers"
            else:
                progress = "legacy"
            
            build_type = b.get("type", "unknown")
            created = b.get("created", "unknown")
            
            print(f"  ✓ {b['slug']:<20} {progress:<20} {build_type:<12} {created}")
        
        if remaining > 0:
            print(f"  ... and {remaining} more (use --all to see all)")
        print()
    
    # Summary
    total = len(builds)
    active = len(active_builds)
    complete = len(complete_builds)
    stale = len([b for b in builds if b.get("status") == "stale"])
    
    print(f"Total: {total} builds ({active} active, {complete} complete)", end="")
    if stale > 0:
        print(f", {stale} stale", end="")
    print()


def cmd_regenerate(args):
    """Regenerate dashboard data file."""
    builds = scan_all_builds()
    builds = sort_builds(builds)
    
    # Clean up internal fields
    clean_builds = []
    for b in builds:
        clean = {k: v for k, v in b.items() if not k.startswith("_")}
        clean_builds.append(clean)
    
    active_builds = [b for b in clean_builds if b.get("status") == "active"]
    complete_builds = [b for b in clean_builds if b.get("status") == "complete"]
    pre_tracker_builds = [b for b in clean_builds if b.get("status") == "pre-tracker"]
    stale_builds = [b for b in clean_builds if b.get("status") == "stale"]
    draft_builds = [b for b in clean_builds if b.get("status") == "draft"]
    
    output = {
        "generated_at": get_iso_timestamp(),
        "tracker_epoch": TRACKER_EPOCH,
        "stale_threshold_days": STALE_THRESHOLD_DAYS,
        "builds": clean_builds,
        "summary": {
            "total": len(clean_builds),
            "active": len(active_builds),
            "complete": len(complete_builds),
            "draft": len(draft_builds),
            "stale": len(stale_builds),
            "pre_tracker": len(pre_tracker_builds)
        }
    }
    
    # Ensure directory exists
    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    DASHBOARD_DATA_FILE.write_text(json.dumps(output, indent=2) + "\n")
    
    print(f"✓ Dashboard data regenerated")
    print(f"  File: {DASHBOARD_DATA_FILE.relative_to(WORKSPACE)}")
    print(f"  Builds: {len(clean_builds)} total ({len(active_builds)} active, {len(stale_builds)} backlog, {len(pre_tracker_builds)} pre-tracker)")


def main():
    parser = argparse.ArgumentParser(
        description="Global view of all builds across N5/builds/.",
        epilog="Examples:\n"
               "  python3 N5/scripts/build_status.py list\n"
               "  python3 N5/scripts/build_status.py list --incomplete\n"
               "  python3 N5/scripts/build_status.py list --json\n"
               "  python3 N5/scripts/build_status.py regenerate",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List all builds with status"
    )
    list_parser.add_argument(
        "--incomplete", "-i",
        action="store_true",
        help="Show only active/in-progress builds"
    )
    list_parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="as_json",
        help="Output as JSON"
    )
    list_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show all complete builds (not just recent)"
    )
    
    # regenerate command
    regenerate_parser = subparsers.add_parser(
        "regenerate",
        help="Write JSON to dashboard data file"
    )
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "regenerate":
        cmd_regenerate(args)


if __name__ == "__main__":
    main()
