import argparse

#!/usr/bin/env python3
"""
Git Change Checker: Quick audit for overwrites, empty files, or major losses in staged changes.
"""

import subprocess
import sys
from pathlib import Path

def run_git_diff():
    try:
        result = subprocess.run(['git', 'diff', '--staged', '--name-status'], capture_output=True, text=True, cwd='/home/workspace/N5')
        if result.returncode != 0:
            print(f"Git error: {result.stderr}")
            return []
        return result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Error running git: {e}")
        return []

def check_file_changes():
    changes = run_git_diff()
    issues = []

    for line in changes:
        if not line:
            continue
        status, filepath = line.split('\t', 1)
        full_path = Path('/home/workspace') / filepath

        if status in ['M', 'A']:  # Modified or Added
            if full_path.exists():
                size = full_path.stat().st_size
                if size == 0:
                    issues.append(f"⚠️  {filepath}: Now empty (potential overwrite)")
                elif status == 'M':
                    # Check for large deletions: if diff shows many deletions
                    try:
                        diff_result = subprocess.run(['git', 'diff', '--staged', '--stat', filepath], capture_output=True, text=True, cwd='/home/workspace/N5')
                        if 'deletions' in diff_result.stdout:
                            # Rough check: if deletions > insertions significantly
                            # For simplicity, flag if diff has deletions
                            issues.append(f"⚠️  {filepath}: Modified with deletions (check for data loss)")
                    except:
                        pass
            else:
                issues.append(f"❓ {filepath}: Added but file missing")

    if not issues:
        print("✅ No obvious overwrites or major losses detected in staged changes.")
    else:
        print("Potential issues found:")
        for issue in issues:
            print(issue)

if __name__ == "__main__":
    check_file_changes()