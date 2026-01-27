#!/usr/bin/env python3
"""
Pre-push validation for N5OS Ode repo.
Run before pushing to verify local and remote are in sync.
"""

import subprocess
import sys
import os

def run(cmd, cwd=None):
    """Run a command and return stdout and return code."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip(), result.returncode

def main():
    print("🔍 N5OS Ode Sync Check")
    print("=" * 40)
    
    # Check if we're in the right directory
    ode_path = "/home/workspace/N5/export/n5os-ode"
    if not os.path.exists(ode_path):
        print("❌ N5OS Ode directory not found at expected path")
        print(f"   Expected: {ode_path}")
        return 1
    
    # Change to the ode directory for git operations
    os.chdir(ode_path)
    
    # Check if we're in a git repo
    _, rc = run("git rev-parse --git-dir")
    if rc != 0:
        print("❌ Not in a git repository")
        return 1
    
    # Fetch latest
    print("\n1. Fetching from origin...")
    _, rc = run("git fetch origin")
    if rc != 0:
        print("❌ Failed to fetch from origin")
        return 1
    
    # Compare commit counts
    print("\n2. Comparing commit counts...")
    local_count, _ = run("git rev-list --count HEAD")
    remote_count, _ = run("git rev-list --count origin/main")
    
    print(f"   Local:  {local_count} commits")
    print(f"   Remote: {remote_count} commits")
    
    if remote_count and local_count:
        if int(remote_count) > int(local_count):
            print("\n⚠️  WARNING: Remote has more commits than local!")
            print("   Run 'git pull origin main' before pushing.")
            return 1
        
        if int(local_count) < 30:
            print("\n⚠️  WARNING: Unusually low commit count!")
            print("   This may indicate history was reset.")
            return 1
    
    # Check for uncommitted changes
    print("\n3. Checking working tree...")
    status, _ = run("git status --porcelain")
    if status:
        print("   Uncommitted changes:")
        for line in status.split('\n')[:5]:  # Show first 5 lines
            print(f"   {line}")
        if len(status.split('\n')) > 5:
            print(f"   ... and {len(status.split('\n')) - 5} more")
    else:
        print("   ✅ Working tree clean")
    
    # Show what would be pushed
    print("\n4. Commits to push:")
    ahead, _ = run("git log origin/main..HEAD --oneline")
    if ahead:
        for line in ahead.split('\n')[:5]:  # Show first 5 commits
            print(f"   {line}")
        if len(ahead.split('\n')) > 5:
            print(f"   ... and {len(ahead.split('\n')) - 5} more commits")
    else:
        print("   (nothing to push)")
    
    print("\n✅ Sync check passed. Safe to push.")
    return 0

if __name__ == "__main__":
    sys.exit(main())