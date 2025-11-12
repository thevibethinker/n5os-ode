#!/usr/bin/env python3
"""
N5OS Lite File Protection System

Lightweight directory protection using .protected marker files.
Prevents accidental deletion or modification of critical directories.

Usage:
    python3 file_guard.py protect <path> [--reason "..."]
    python3 file_guard.py unprotect <path>
    python3 file_guard.py check <path>
    python3 file_guard.py list
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List


PROTECTION_FILENAME = ".protected"


def protect_directory(path: Path, reason: str = "Protected directory") -> bool:
    """
    Protect a directory by creating .protected marker file.
    
    Args:
        path: Directory to protect
        reason: Reason for protection
        
    Returns:
        True if successful, False otherwise
    """
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return False
    
    if not path.is_dir():
        print(f"Error: Path is not a directory: {path}", file=sys.stderr)
        return False
    
    protection_file = path / PROTECTION_FILENAME
    
    if protection_file.exists():
        print(f"Directory already protected: {path}")
        return True
    
    protection_data = {
        "protected": True,
        "reason": reason,
        "created": datetime.now(timezone.utc).isoformat(),
        "created_by": "file_guard"
    }
    
    try:
        with open(protection_file, 'w') as f:
            json.dump(protection_data, f, indent=2)
        print(f"✓ Protected: {path}")
        print(f"  Reason: {reason}")
        return True
    except Exception as e:
        print(f"Error protecting directory: {e}", file=sys.stderr)
        return False


def unprotect_directory(path: Path) -> bool:
    """
    Remove protection from a directory.
    
    Args:
        path: Directory to unprotect
        
    Returns:
        True if successful, False otherwise
    """
    protection_file = path / PROTECTION_FILENAME
    
    if not protection_file.exists():
        print(f"Directory not protected: {path}")
        return False
    
    try:
        protection_file.unlink()
        print(f"✓ Unprotected: {path}")
        return True
    except Exception as e:
        print(f"Error unprotecting directory: {e}", file=sys.stderr)
        return False


def check_protection(path: Path, quiet: bool = False) -> Optional[Dict]:
    """
    Check if a path or any parent directory is protected.
    
    Args:
        path: Path to check
        quiet: If True, don't print output
        
    Returns:
        Protection data dict if protected, None otherwise
    """
    current = Path(path).resolve()
    
    # Check path and all parents up to root
    while True:
        protection_file = current / PROTECTION_FILENAME
        
        if protection_file.exists():
            try:
                with open(protection_file) as f:
                    data = json.load(f)
                
                if not quiet:
                    print(f"⚠️  PROTECTED: {current}")
                    print(f"   Reason: {data.get('reason', 'No reason provided')}")
                    print(f"   Created: {data.get('created', 'Unknown')}")
                
                return data
            except Exception as e:
                if not quiet:
                    print(f"Error reading protection file: {e}", file=sys.stderr)
                return None
        
        # Move to parent
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent
    
    if not quiet:
        print(f"Not protected: {path}")
    
    return None


def list_protected(root: Path = None) -> List[Path]:
    """
    List all protected directories under root.
    
    Args:
        root: Root path to search (default: current directory)
        
    Returns:
        List of protected directory paths
    """
    if root is None:
        root = Path.cwd()
    
    protected_dirs = []
    
    for protection_file in root.rglob(PROTECTION_FILENAME):
        dir_path = protection_file.parent
        try:
            with open(protection_file) as f:
                data = json.load(f)
            protected_dirs.append((dir_path, data))
        except Exception:
            continue
    
    if not protected_dirs:
        print(f"No protected directories found under: {root}")
        return []
    
    print(f"Protected directories under {root}:")
    print()
    
    for dir_path, data in sorted(protected_dirs):
        rel_path = dir_path.relative_to(root) if dir_path != root else dir_path
        print(f"  {rel_path}")
        print(f"    Reason: {data.get('reason', 'No reason')}")
        print()
    
    return [d[0] for d in protected_dirs]


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="N5OS Lite File Protection System"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Protect command
    protect_parser = subparsers.add_parser('protect', help='Protect a directory')
    protect_parser.add_argument('path', type=Path, help='Directory to protect')
    protect_parser.add_argument('--reason', default='Protected directory',
                               help='Reason for protection')
    
    # Unprotect command
    unprotect_parser = subparsers.add_parser('unprotect', help='Unprotect a directory')
    unprotect_parser.add_argument('path', type=Path, help='Directory to unprotect')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if path is protected')
    check_parser.add_argument('path', type=Path, help='Path to check')
    check_parser.add_argument('--quiet', action='store_true',
                             help='Quiet mode (exit code only)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List protected directories')
    list_parser.add_argument('--root', type=Path, default=None,
                            help='Root path to search (default: current directory)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'protect':
        success = protect_directory(args.path, args.reason)
        return 0 if success else 1
    
    elif args.command == 'unprotect':
        success = unprotect_directory(args.path)
        return 0 if success else 1
    
    elif args.command == 'check':
        result = check_protection(args.path, quiet=args.quiet)
        return 0 if result else 1
    
    elif args.command == 'list':
        root = args.root if args.root else Path.cwd()
        list_protected(root)
        return 0
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
