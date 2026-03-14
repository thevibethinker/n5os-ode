#!/usr/bin/env python3
"""
Pulse Dashboard Sync Script

Scans scripts/builds/ for Pulse and legacy build formats, generating
dashboard-compatible JSON for Sites/build-tracker/data/builds.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


BUILD_DIR = Path("./scripts/builds")
DEFAULT_OUTPUT = Path("./Sites/build-tracker/data/builds.json")


def parse_timestamp(ts: str | None) -> datetime | None:
    """Parse various timestamp formats to UTC datetime."""
    if not ts:
        return None

    # Try ISO 8601 formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]:
        try:
            result = datetime.strptime(ts, fmt)
            # Ensure UTC
            if result.tzinfo is None:
                result = result.replace(tzinfo=timezone.utc)
            return result
        except ValueError:
            continue

    return None


def count_pulse_drops(drops: dict) -> dict:
    """Count drops by status from Pulse meta.json."""
    counts = {"complete": 0, "running": 0, "pending": 0, "dead": 0, "failed": 0}
    
    for drop_id, drop_data in drops.items():
        status = drop_data.get("status", "pending").lower()
        if status in counts:
            counts[status] += 1
        elif status == "active":
            counts["running"] += 1
        elif status in ("blocked", "error", "cancelled"):
            counts["failed"] += 1
        else:
            counts["pending"] += 1
    
    counts["total"] = sum(counts.values())
    return counts


def read_pulse_meta(build_path: Path) -> dict | None:
    """Read and parse Pulse format meta.json."""
    meta_file = build_path / "meta.json"
    
    if not meta_file.exists():
        return None
    
    try:
        with open(meta_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to parse {meta_file}: {e}", file=sys.stderr)
        return None
    
    # Pulse format check
    if "drops" not in data:
        return None
    
    # Extract fields with defaults
    drops_data = data.get("drops", {})
    drop_counts = count_pulse_drops(drops_data)
    
    # Calculate progress
    total = drop_counts["total"]
    complete = drop_counts["complete"]
    progress_pct = int((complete / total * 100)) if total > 0 else 0
    
    # Determine last activity from drops
    last_activity = None
    for drop_id, drop_data in drops_data.items():
        # Check various timestamp fields
        for ts_field in ("completed_at", "started_at", "failed_at"):
            ts = drop_data.get(ts_field)
            if ts:
                parsed = parse_timestamp(ts)
                if parsed and (last_activity is None or parsed > last_activity):
                    last_activity = parsed
                    break
    
    # Fall back to build-level timestamps
    if not last_activity:
        for field in ("started_at", "created_at"):
            ts = data.get(field)
            if ts:
                parsed = parse_timestamp(ts)
                if parsed and (last_activity is None or parsed > last_activity):
                    last_activity = parsed
                    break
    
    # Use created_at as final fallback
    created_at = None
    for field in ("created_at", "created", "started_at"):
        ts = data.get(field)
        if ts:
            created_at = parse_timestamp(ts)
            if created_at:
                break
    
    # Format ISO strings
    last_activity_str = last_activity.isoformat() if last_activity else None
    created_at_str = created_at.isoformat() if created_at else None
    
    # Determine status
    status = data.get("status", "pending").lower()
    if status in ("pending", "active"):
        # For pending/active, check if any drops are running
        if drop_counts["running"] > 0:
            status = "active"
        elif drop_counts["complete"] > 0:
            status = "active"
        else:
            status = "pending"
    elif status not in ("complete", "failed"):
        status = "pending"
    
    return {
        "slug": data.get("slug", build_path.name),
        "title": data.get("title", build_path.name.replace("-", " ").title()),
        "status": status,
        "format": "pulse",
        "streams": {
            "current": data.get("current_stream", 1),
            "total": data.get("total_streams", 1),
        },
        "drops": drop_counts,
        "progress_pct": progress_pct,
        "created_at": created_at_str,
        "last_activity": last_activity_str,
        "path": str(build_path.relative_to(".")),
    }


def read_legacy_build(build_path: Path) -> dict | None:
    """Read legacy build format (workers/ directory)."""
    workers_dir = build_path / "workers"
    
    if not workers_dir.exists() or not workers_dir.is_dir():
        return None
    
    # Legacy builds have workers/*.md files
    # Limited info available, use defaults
    created_at = None
    try:
        stat = build_path.stat()
        created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        pass
    
    # Try to read STATUS.md or BUILD_STATUS.md for additional info
    status = "pending"
    status_file = None
    for name in ("STATUS.md", "BUILD_STATUS.md"):
        if (build_path / name).exists():
            status_file = build_path / name
            break
    
    if status_file:
        try:
            with open(status_file, "r") as f:
                content = f.read().lower()
                if "complete" in content:
                    status = "complete"
                elif "active" in content or "in progress" in content:
                    status = "active"
                elif "failed" in content or "blocked" in content:
                    status = "failed"
        except IOError:
            pass
    
    return {
        "slug": build_path.name,
        "title": build_path.name.replace("-", " ").title(),
        "status": status,
        "format": "legacy",
        "streams": {"current": 1, "total": 1},
        "drops": {
            "complete": 0,
            "running": 0,
            "pending": 1,
            "dead": 0,
            "failed": 0,
            "total": 1,
        },
        "progress_pct": 0,
        "created_at": created_at,
        "last_activity": created_at,
        "path": str(build_path.relative_to(".")),
    }


def scan_builds(build_dir: Path) -> list[dict]:
    """Scan build directory for Pulse and legacy builds."""
    builds = []
    
    if not build_dir.exists():
        print(f"Warning: Build directory not found: {build_dir}", file=sys.stderr)
        return builds
    
    for entry in build_dir.iterdir():
        if not entry.is_dir():
            continue
        
        # Skip hidden directories
        if entry.name.startswith("."):
            continue
        
        # Try Pulse format first
        build_data = read_pulse_meta(entry)
        if build_data:
            builds.append(build_data)
            continue
        
        # Try legacy format
        build_data = read_legacy_build(entry)
        if build_data:
            builds.append(build_data)
    
    return builds


def sort_builds(builds: list[dict]) -> list[dict]:
    """Sort builds: active first, then by last_activity descending."""
    def sort_key(build: dict) -> tuple:
        # Active builds first
        is_active = build["status"] == "active"
        
        # Sort by last_activity (missing = oldest)
        last_activity = build.get("last_activity")
        if last_activity:
            try:
                activity_ts = datetime.fromisoformat(last_activity).timestamp()
            except ValueError:
                activity_ts = 0
        else:
            activity_ts = 0
        
        return (0 if is_active else 1, -activity_ts)
    
    return sorted(builds, key=sort_key)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Pulse builds to Build Tracker dashboard JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Output to default location
  %(prog)s --output /tmp/builds.json    # Custom output path
  %(prog)s --dry-run                    # Print JSON to stdout
        """,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON to stdout instead of writing to file",
    )
    
    args = parser.parse_args()
    
    # Scan for builds
    builds = scan_builds(BUILD_DIR)
    
    # Sort builds
    builds = sort_builds(builds)
    
    # Build output JSON
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "builds": builds,
    }
    
    # Output
    if args.dry_run:
        print(json.dumps(output, indent=2))
    else:
        # Ensure parent directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Synced {len(builds)} builds to {args.output}")
        if builds:
            pulse_count = sum(1 for b in builds if b["format"] == "pulse")
            legacy_count = len(builds) - pulse_count
            print(f"  Pulse: {pulse_count}, Legacy: {legacy_count}")


if __name__ == "__main__":
    main()
