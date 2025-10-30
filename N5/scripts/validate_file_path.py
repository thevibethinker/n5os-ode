#!/usr/bin/env python3
"""
File Path Validation - Pre-creation validation helper

Simple wrapper around sandbox_enforcer for AI to call before file creation.

Usage (from AI):
    Before creating any file, validate the path:
    
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/validate_file_path.py", 
         target_path, "--convo-id", current_convo_id],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        # Validation failed - path violates sandbox-first protocol
        print(result.stdout)  # Show user the violation message
        # Either: declare as permanent first, OR create in sandbox instead
        return
    
    # Validation passed - safe to create file
    create_or_rewrite_file(target_path, content)

Principles: P5 (Anti-Overwrite), P7 (Dry-Run), P18 (Verify State)
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Validate file path before creation"""
    if len(sys.argv) < 2:
        print("Usage: validate_file_path.py <path> [--convo-id CONVO_ID] [--declared PATH1 PATH2 ...]")
        print("\nValidates path against sandbox-first protocol before file creation")
        print("Exit code 0: Valid, Exit code 1: Violation")
        return 1
    
    # Pass all arguments directly to sandbox_enforcer
    enforcer_path = Path(__file__).parent / "sandbox_enforcer.py"
    
    result = subprocess.run(
        [sys.executable, str(enforcer_path)] + sys.argv[1:],
        capture_output=True,
        text=True
    )
    
    # Pass through stdout/stderr and exit code
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    
    return result.returncode


if __name__ == "__main__":
    exit(main())
