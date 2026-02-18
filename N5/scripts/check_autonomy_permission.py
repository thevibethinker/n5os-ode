#!/usr/bin/env python3
"""
check_autonomy_permission.py - Validate if a path is allowed for zoputer edits.

Checks a given path against the autonomy configuration to determine if
zoputer is permitted to modify it autonomously.

Usage:
    python3 check_autonomy_permission.py <path>
    python3 check_autonomy_permission.py "Learnings/foo.md"      # → allowed
    python3 check_autonomy_permission.py "Skills/bar/SKILL.md"   # → forbidden

Exit codes:
    0 = allowed
    1 = forbidden
    2 = error (invalid config, missing file, etc.)
"""

import argparse
import fnmatch
import os
import sys
from pathlib import Path

import yaml


CONFIG_PATH = Path("/home/workspace/Documents/consulting/autonomy-config.yaml")


def load_config() -> dict:
    """Load and parse the autonomy configuration."""
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(2)
    
    with open(CONFIG_PATH, 'r') as f:
        content = f.read()
    
    # Skip YAML frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    try:
        config = yaml.safe_load(content)
        return config
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in config: {e}", file=sys.stderr)
        sys.exit(2)


def check_n5protected(path: str) -> bool:
    """
    Check if path or any ancestor (excluding workspace root) contains .n5protected.
    
    The workspace root may have .n5protected for PII marking, but that doesn't
    prevent autonomous edits to allowed paths. We check the target path and
    its parent directories, stopping before the workspace root.
    """
    workspace_root = Path("/home/workspace")
    check_path = workspace_root / path
    
    # Start from the target's parent and walk up (stop before workspace root)
    # Also check the target itself if it's a directory
    current = check_path
    
    while current > workspace_root:
        protected_marker = current / ".n5protected"
        if protected_marker.exists():
            return True
        
        # Also check if the current directory itself has the marker
        if current.is_dir():
            marker_in_dir = current / ".n5protected"
            if marker_in_dir.exists():
                return True
        
        current = current.parent
    
    # Do NOT check workspace root's .n5protected - that's for PII marking
    return False


def matches_pattern(path: str, pattern: str) -> bool:
    """Check if path matches a glob pattern."""
    # Normalize path separators
    path = path.replace("\\", "/").strip("/")
    pattern = pattern.replace("\\", "/").strip("/")
    
    # Handle ** patterns (recursive match)
    if "**" in pattern:
        # Convert ** to match any depth
        # e.g., "Skills/**/*" should match "Skills/foo/bar/baz.md"
        parts = pattern.split("**")
        if len(parts) == 2:
            prefix = parts[0].rstrip("/")
            suffix = parts[1].lstrip("/")
            
            if prefix and not path.startswith(prefix):
                return False
            
            remaining = path[len(prefix):].lstrip("/") if prefix else path
            
            if suffix:
                return fnmatch.fnmatch(remaining, f"*{suffix}") or fnmatch.fnmatch(remaining, f"*/{suffix}")
            return True
    
    # Standard glob matching
    return fnmatch.fnmatch(path, pattern)


def is_allowed(path: str, config: dict) -> tuple[bool, str]:
    """
    Check if a path is allowed for zoputer edits.
    
    Returns:
        (is_allowed: bool, reason: str)
    """
    path = path.replace("\\", "/").strip("/")
    
    # Check .n5protected first (always takes precedence)
    if check_n5protected(path):
        return False, "Path or ancestor contains .n5protected"
    
    allowed_patterns = config.get("allowed_self_edits", [])
    forbidden_patterns = config.get("forbidden_self_edits", [])
    
    # Check forbidden patterns first (forbidden takes precedence)
    for pattern in forbidden_patterns:
        if matches_pattern(path, pattern):
            return False, f"Matches forbidden pattern: {pattern}"
    
    # Check if explicitly allowed
    for pattern in allowed_patterns:
        if matches_pattern(path, pattern):
            return True, f"Matches allowed pattern: {pattern}"
    
    # Default: not explicitly allowed = forbidden
    return False, "Not in allowed_self_edits list"


def main():
    parser = argparse.ArgumentParser(
        description="Check if a path is allowed for zoputer autonomous edits.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 check_autonomy_permission.py "Learnings/foo.md"
    python3 check_autonomy_permission.py "Skills/bar/SKILL.md"
    python3 check_autonomy_permission.py --verbose "Runtime/cache.json"

Exit codes:
    0 = allowed
    1 = forbidden
    2 = error
        """
    )
    parser.add_argument("path", help="Path to check (relative to workspace root)")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Show detailed reasoning")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Only output 'allowed' or 'forbidden'")
    parser.add_argument("--config", type=str,
                        help="Override config path")
    
    args = parser.parse_args()
    
    # Allow config override for testing
    global CONFIG_PATH
    if args.config:
        CONFIG_PATH = Path(args.config)
    
    config = load_config()
    allowed, reason = is_allowed(args.path, config)
    
    if args.quiet:
        print("allowed" if allowed else "forbidden")
    elif args.verbose:
        print(f"Path: {args.path}")
        print(f"Status: {'ALLOWED' if allowed else 'FORBIDDEN'}")
        print(f"Reason: {reason}")
        print(f"Autonomy level: {config.get('autonomy_level', 'unknown')}")
    else:
        status = "✓ allowed" if allowed else "✗ forbidden"
        print(f"{args.path}: {status}")
        if not allowed:
            print(f"  Reason: {reason}")
    
    sys.exit(0 if allowed else 1)


if __name__ == "__main__":
    main()
