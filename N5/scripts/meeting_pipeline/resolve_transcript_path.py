#!/usr/bin/env python3
"""
Path resolution helper for meeting transcripts.
Handles [IMPORTED-TO-ZO] prefix migration.
"""

from pathlib import Path
import sys


def resolve_transcript_path(original_path: str) -> Path:
    """
    Resolve transcript path, handling [IMPORTED-TO-ZO] prefix.
    
    Strategy:
    1. Try original path as-is
    2. Try with [IMPORTED-TO-ZO] prefix added
    3. Return None if neither exists
    
    Args:
        original_path: Path from AI request JSON
        
    Returns:
        Resolved Path object if found, None otherwise
    """
    path = Path(original_path)
    
    # Try original path first
    if path.exists():
        return path
    
    # Try with [IMPORTED-TO-ZO] prefix
    prefixed_name = f"[IMPORTED-TO-ZO] {path.name}"
    prefixed_path = path.parent / prefixed_name
    
    if prefixed_path.exists():
        return prefixed_path
    
    # Neither exists
    return None


def main():
    """CLI interface for path resolution."""
    if len(sys.argv) != 2:
        print("Usage: resolve_transcript_path.py <path>", file=sys.stderr)
        sys.exit(1)
    
    original_path = sys.argv[1]
    resolved = resolve_transcript_path(original_path)
    
    if resolved:
        print(str(resolved))
        sys.exit(0)
    else:
        print(f"ERROR: Path not found: {original_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
