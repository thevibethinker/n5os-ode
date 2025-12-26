#!/usr/bin/env python3
"""
N5 Ignore System - Mark directories as non-existent for N5 operations.

Directories containing `.n5ignored` are:
- Excluded from n5_index_rebuild.py
- Excluded from grep_search results (when using N5 tools)
- Treated as archived/deprecated by agents
- Hidden from workspace overviews

Usage:
    python3 n5_ignore.py mark <path> --reason "Why this is ignored"
    python3 n5_ignore.py check <path>
    python3 n5_ignore.py list
    python3 n5_ignore.py unmark <path>
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/workspace")
MARKER_FILE = ".n5ignored"


def is_ignored(path: Path) -> bool:
    """Check if path or any parent has .n5ignored marker."""
    path = Path(path).resolve()
    
    # Check the path itself and all parents up to workspace
    current = path if path.is_dir() else path.parent
    while current >= WORKSPACE:
        marker = current / MARKER_FILE
        if marker.exists():
            return True
        if current == WORKSPACE:
            break
        current = current.parent
    return False


def get_ignore_info(path: Path) -> dict | None:
    """Get ignore info if path is ignored."""
    path = Path(path).resolve()
    
    current = path if path.is_dir() else path.parent
    while current >= WORKSPACE:
        marker = current / MARKER_FILE
        if marker.exists():
            try:
                return {
                    "ignored_at": str(current),
                    "marker": str(marker),
                    **json.loads(marker.read_text())
                }
            except json.JSONDecodeError:
                return {
                    "ignored_at": str(current),
                    "marker": str(marker),
                    "reason": marker.read_text().strip() or "No reason provided"
                }
        if current == WORKSPACE:
            break
        current = current.parent
    return None


def mark_ignored(path: Path, reason: str) -> bool:
    """Mark a directory as ignored."""
    path = Path(path).resolve()
    
    if not path.is_dir():
        print(f"❌ Error: {path} is not a directory")
        return False
    
    marker = path / MARKER_FILE
    data = {
        "reason": reason,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "effect": "Excluded from indexes, grep searches, and workspace overviews"
    }
    
    marker.write_text(json.dumps(data, indent=2))
    print(f"✓ Marked as ignored: {path}")
    print(f"  Reason: {reason}")
    return True


def unmark_ignored(path: Path) -> bool:
    """Remove ignore marker from a directory."""
    path = Path(path).resolve()
    marker = path / MARKER_FILE
    
    if not marker.exists():
        print(f"❌ No .n5ignored marker found at {path}")
        return False
    
    marker.unlink()
    print(f"✓ Removed ignore marker from: {path}")
    return True


def list_ignored() -> list[dict]:
    """Find all ignored directories in workspace."""
    ignored = []
    
    for marker in WORKSPACE.rglob(MARKER_FILE):
        info = get_ignore_info(marker.parent)
        if info:
            ignored.append(info)
    
    return ignored


def get_exclude_patterns() -> list[str]:
    """Get glob patterns for all ignored directories (for use in grep/find)."""
    patterns = []
    for marker in WORKSPACE.rglob(MARKER_FILE):
        rel_path = marker.parent.relative_to(WORKSPACE)
        patterns.append(f"{rel_path}/**")
    return patterns


def main():
    parser = argparse.ArgumentParser(description="N5 Ignore System")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # mark command
    mark_parser = subparsers.add_parser("mark", help="Mark directory as ignored")
    mark_parser.add_argument("path", help="Directory to mark")
    mark_parser.add_argument("--reason", "-r", required=True, help="Reason for ignoring")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if path is ignored")
    check_parser.add_argument("path", help="Path to check")
    
    # list command
    subparsers.add_parser("list", help="List all ignored directories")
    
    # unmark command
    unmark_parser = subparsers.add_parser("unmark", help="Remove ignore marker")
    unmark_parser.add_argument("path", help="Directory to unmark")
    
    # patterns command (for scripting)
    subparsers.add_parser("patterns", help="Output exclude patterns for grep/find")
    
    args = parser.parse_args()
    
    if args.command == "mark":
        success = mark_ignored(Path(args.path), args.reason)
        sys.exit(0 if success else 1)
        
    elif args.command == "check":
        path = Path(args.path)
        info = get_ignore_info(path)
        if info:
            print(f"🚫 IGNORED: {path}")
            print(f"   Ignored at: {info['ignored_at']}")
            print(f"   Reason: {info.get('reason', 'No reason')}")
            sys.exit(0)
        else:
            print(f"✓ Not ignored: {path}")
            sys.exit(1)
            
    elif args.command == "list":
        ignored = list_ignored()
        if not ignored:
            print("No ignored directories found.")
        else:
            print(f"Found {len(ignored)} ignored directories:\n")
            for info in ignored:
                print(f"🚫 {info['ignored_at']}")
                print(f"   Reason: {info.get('reason', 'No reason')}")
                print()
                
    elif args.command == "unmark":
        success = unmark_ignored(Path(args.path))
        sys.exit(0 if success else 1)
        
    elif args.command == "patterns":
        patterns = get_exclude_patterns()
        for p in patterns:
            print(p)


if __name__ == "__main__":
    main()

