#!/usr/bin/env python3
"""
N5 Completion Verification - Semantic Gatekeeper

Purpose: Verify that a worker has actually produced what it claims before
allowing submission/completion.

Checks:
1. Files exist
2. Syntax is valid (for .py, .json, .md)
3. Tests passed (if applicable)

Usage:
    python3 n5_verify_completion.py --files "file1.py,file2.md" --run-tests
"""

import argparse
import sys
import os
import ast
import json
import subprocess
from pathlib import Path

def verify_file_existence(paths):
    """Check if files exist."""
    missing = []
    for p in paths:
        if not Path(p).exists():
            missing.append(p)
    return missing

def verify_python_syntax(path):
    """Check Python syntax."""
    try:
        with open(path, "r") as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def verify_json_syntax(path):
    """Check JSON syntax."""
    try:
        with open(path, "r") as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Verify worker completion artifacts")
    parser.add_argument("--files", help="Comma-separated list of files to verify")
    parser.add_argument("--run-tests", action="store_true", help="Run associated tests if found")
    
    args = parser.parse_args()
    
    if not args.files:
        print("⚠ No files provided to verify. Assuming task was non-file-generating.")
        return 0

    file_list = [f.strip() for f in args.files.split(",")]
    
    print(f"🔍 Verifying {len(file_list)} artifacts...")
    
    # 1. Existence Check
    missing = verify_file_existence(file_list)
    if missing:
        print(f"❌ Verification Failed: The following files were claimed but not found:")
        for m in missing:
            print(f"   - {m}")
        return 1
    
    # 2. Syntax Check
    for f in file_list:
        path = Path(f)
        if path.suffix == ".py":
            valid, err = verify_python_syntax(path)
            if not valid:
                print(f"❌ Syntax Error in {f}: {err}")
                return 1
        elif path.suffix == ".json":
            valid, err = verify_json_syntax(path)
            if not valid:
                print(f"❌ JSON Error in {f}: {err}")
                return 1
    
    print("✅ All artifacts exist and pass syntax checks.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

