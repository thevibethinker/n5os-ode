#!/usr/bin/env python3
"""
Sandbox Validator — Validates that file operations stay within allowed paths.

Zøde's sandbox:
  WRITE allowed: Skills/zode-moltbook/
  WRITE blocked: Everything else (especially N5/scripts/, N5/config/, Sites/, Personal/, N5/data/)
  READ allowed: N5/prefs/, Knowledge/, Documents/System/personas/

Usage: python3 sandbox_validator.py check /path/to/file
       python3 sandbox_validator.py check --write /path/to/file
       python3 sandbox_validator.py check --read /path/to/file
"""

import argparse
import os
import sys
from pathlib import Path

# Workspace root (resolve relative to cwd or absolute)
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/home/workspace"))

# Allowed WRITE paths (relative to workspace root)
WRITE_ALLOWED = [
    "Skills/zode-moltbook/",
]

# Allowed READ paths (in addition to write-allowed paths)
READ_ALLOWED = [
    "N5/prefs/",
    "Knowledge/",
    "Documents/System/personas/",
]

# Explicitly BLOCKED paths (even if they seem like they'd match)
BLOCKED_PATHS = [
    "N5/scripts/",
    "N5/config/",
    "N5/data/",
    "Sites/",
    "Personal/",
    "Prompts/",
]


def _resolve(path: str) -> Path:
    """Resolve a path to absolute, handling both relative and absolute."""
    p = Path(path)
    if not p.is_absolute():
        p = WORKSPACE_ROOT / p
    return p.resolve()


def check_write(path: str) -> tuple[bool, str]:
    """Check if a write to this path is allowed."""
    resolved = _resolve(path)
    workspace_resolved = WORKSPACE_ROOT.resolve()

    # Must be within workspace
    try:
        rel = resolved.relative_to(workspace_resolved)
    except ValueError:
        return False, f"BLOCKED — Outside workspace: {resolved}"

    rel_str = str(rel) + ("/" if resolved.is_dir() else "")

    # Check against blocked list first
    for blocked in BLOCKED_PATHS:
        if rel_str.startswith(blocked) or str(rel).startswith(blocked):
            return False, f"BLOCKED — Restricted path: {blocked}"

    # Check against allowed write paths
    for allowed in WRITE_ALLOWED:
        if rel_str.startswith(allowed) or str(rel).startswith(allowed):
            return True, f"ALLOWED — Within sandbox: {allowed}"

    return False, f"BLOCKED — Not in allowed write paths: {rel}"


def check_read(path: str) -> tuple[bool, str]:
    """Check if a read from this path is allowed."""
    # Write-allowed paths are also read-allowed
    allowed, reason = check_write(path)
    if allowed:
        return True, reason

    resolved = _resolve(path)
    workspace_resolved = WORKSPACE_ROOT.resolve()

    try:
        rel = resolved.relative_to(workspace_resolved)
    except ValueError:
        return False, f"BLOCKED — Outside workspace: {resolved}"

    rel_str = str(rel) + ("/" if resolved.is_dir() else "")

    for allowed_path in READ_ALLOWED:
        if rel_str.startswith(allowed_path) or str(rel).startswith(allowed_path):
            return True, f"ALLOWED — Read access: {allowed_path}"

    return False, f"BLOCKED — Not in allowed read paths: {rel}"


# --- CLI ---

def cmd_check(args):
    path = args.path

    if args.write:
        allowed, reason = check_write(path)
    elif args.read:
        allowed, reason = check_read(path)
    else:
        # Default: check write
        allowed, reason = check_write(path)

    print(reason)
    sys.exit(0 if allowed else 1)


def cmd_list(args):
    """List all sandbox boundaries."""
    print("WRITE allowed:")
    for p in WRITE_ALLOWED:
        print(f"  + {p}")
    print()
    print("READ allowed (additional):")
    for p in READ_ALLOWED:
        print(f"  + {p}")
    print()
    print("BLOCKED:")
    for p in BLOCKED_PATHS:
        print(f"  - {p}")


def main():
    parser = argparse.ArgumentParser(
        description="Sandbox Validator — Check path access for Zøde operations"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    c = sub.add_parser("check", help="Check if a path is allowed")
    c.add_argument("path", help="Path to check")
    c.add_argument("--write", action="store_true", help="Check write access (default)")
    c.add_argument("--read", action="store_true", help="Check read access")

    sub.add_parser("list", help="List sandbox boundaries")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "check": cmd_check,
        "list": cmd_list,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
