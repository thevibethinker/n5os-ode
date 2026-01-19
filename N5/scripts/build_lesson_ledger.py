#!/usr/bin/env python3
"""
build_lesson_ledger.py - Manage cross-worker lesson ledger for builds.

Usage:
    python3 N5/scripts/build_lesson_ledger.py init <slug>
    python3 N5/scripts/build_lesson_ledger.py read <slug> [--since TIMESTAMP]
    python3 N5/scripts/build_lesson_ledger.py append <slug> "<message>" [--source SOURCE]

Commands:
    init    Create empty BUILD_LESSONS.json for a build
    read    Display ledger contents (optionally filtered by timestamp)
    append  Add a timestamped lesson entry

Options:
    --source    Who logged the lesson: W#.# (worker), V, or orchestrator (default: orchestrator)
    --since     ISO timestamp to filter entries from (for read command)

Examples:
    python3 N5/scripts/build_lesson_ledger.py init my-feature
    python3 N5/scripts/build_lesson_ledger.py append my-feature "API returns snake_case not camelCase" --source W1.1
    python3 N5/scripts/build_lesson_ledger.py read my-feature
    python3 N5/scripts/build_lesson_ledger.py read my-feature --since "2026-01-19T10:00:00"

The ledger is append-only. Entries cannot be modified or deleted.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
LEDGER_FILENAME = "BUILD_LESSONS.json"


def get_ledger_path(slug: str) -> Path:
    """Get path to ledger file for a build."""
    return BUILDS_DIR / slug / LEDGER_FILENAME


def load_ledger(slug: str) -> dict:
    """Load ledger from file. Returns empty structure if not found."""
    ledger_path = get_ledger_path(slug)
    if not ledger_path.exists():
        return None
    
    try:
        with open(ledger_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Ledger file corrupted: {e}", file=sys.stderr)
        return None


def save_ledger(slug: str, ledger: dict) -> bool:
    """Save ledger to file."""
    ledger_path = get_ledger_path(slug)
    try:
        with open(ledger_path, "w") as f:
            json.dump(ledger, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving ledger: {e}", file=sys.stderr)
        return False


def cmd_init(slug: str) -> int:
    """Initialize a new lesson ledger for a build."""
    build_dir = BUILDS_DIR / slug
    
    if not build_dir.exists():
        print(f"Error: Build '{slug}' does not exist at {build_dir}", file=sys.stderr)
        return 1
    
    ledger_path = get_ledger_path(slug)
    if ledger_path.exists():
        print(f"Ledger already exists: {ledger_path}")
        return 0
    
    ledger = {
        "schema_version": "1.0",
        "build_slug": slug,
        "created": datetime.now().isoformat(),
        "purpose": "Cross-worker insights and lessons (append-only)",
        "entries": []
    }
    
    if save_ledger(slug, ledger):
        print(f"✓ Created ledger: {ledger_path}")
        return 0
    return 1


def cmd_read(slug: str, since: str = None) -> int:
    """Read and display ledger contents."""
    ledger = load_ledger(slug)
    
    if ledger is None:
        print(f"Error: No ledger found for build '{slug}'", file=sys.stderr)
        print(f"Expected at: {get_ledger_path(slug)}", file=sys.stderr)
        return 1
    
    entries = ledger.get("entries", [])
    
    # Filter by timestamp if requested
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            entries = [
                e for e in entries 
                if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) >= since_dt
            ]
        except ValueError as e:
            print(f"Error: Invalid timestamp format: {e}", file=sys.stderr)
            return 1
    
    if not entries:
        print(f"No lessons logged yet for '{slug}'.")
        return 0
    
    print(f"=== Build Lesson Ledger: {slug} ===")
    print(f"Total entries: {len(entries)}")
    print()
    
    for entry in entries:
        ts = entry.get("timestamp", "unknown")
        source = entry.get("source", "unknown")
        message = entry.get("message", "")
        
        # Format timestamp for display (just date and time, no microseconds)
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            ts_display = dt.strftime("%Y-%m-%d %H:%M")
        except:
            ts_display = ts
        
        print(f"[{ts_display}] ({source})")
        print(f"  {message}")
        print()
    
    return 0


def cmd_append(slug: str, message: str, source: str = "orchestrator") -> int:
    """Append a new lesson to the ledger."""
    ledger = load_ledger(slug)
    
    if ledger is None:
        print(f"Error: No ledger found for build '{slug}'", file=sys.stderr)
        print(f"Expected at: {get_ledger_path(slug)}", file=sys.stderr)
        print("Hint: Run 'init' first or check the build slug.", file=sys.stderr)
        return 1
    
    if not message.strip():
        print("Error: Message cannot be empty", file=sys.stderr)
        return 1
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "message": message.strip()
    }
    
    ledger["entries"].append(entry)
    
    if save_ledger(slug, ledger):
        entry_num = len(ledger["entries"])
        print(f"✓ Lesson #{entry_num} logged to '{slug}' by {source}")
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage cross-worker lesson ledger for builds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s init my-feature
    %(prog)s append my-feature "API returns snake_case" --source W1.1
    %(prog)s read my-feature
    %(prog)s read my-feature --since "2026-01-19T10:00:00"
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init command
    init_parser = subparsers.add_parser("init", help="Create empty ledger for a build")
    init_parser.add_argument("slug", help="Build slug")
    
    # read command
    read_parser = subparsers.add_parser("read", help="Display ledger contents")
    read_parser.add_argument("slug", help="Build slug")
    read_parser.add_argument("--since", help="Filter entries from this ISO timestamp")
    
    # append command
    append_parser = subparsers.add_parser("append", help="Add a lesson to the ledger")
    append_parser.add_argument("slug", help="Build slug")
    append_parser.add_argument("message", help="The lesson to log")
    append_parser.add_argument(
        "--source", 
        default="orchestrator",
        help="Who logged this: W#.# (worker ID), V, or orchestrator (default: orchestrator)"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        return cmd_init(args.slug)
    elif args.command == "read":
        return cmd_read(args.slug, args.since)
    elif args.command == "append":
        return cmd_append(args.slug, args.message, args.source)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
