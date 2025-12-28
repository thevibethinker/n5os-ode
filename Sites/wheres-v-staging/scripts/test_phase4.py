#!/usr/bin/env python3
"""Phase 4 unit tests - Scheduled sync"""

import subprocess
import requests

def test_scheduled_task_exists():
    """Test that scheduled task was created"""
    try:
        result = subprocess.run(
            ['list_scheduled_tasks'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "list_scheduled_tasks not available"
        
        if "Where's V" not in result.stdout:
            return False, "No Where's V task found"
        
        return True, "Scheduled task for Where's V exists"
    except Exception as e:
        return False, str(e)

def test_sync_script_exists():
    """Test that manual sync script exists"""
    import os
    script_path = "/home/workspace/Sites/wheres-v-staging/scripts/sync.sh"
    if not os.path.exists(script_path):
        return False, f"sync.sh not found at {script_path}"
    
    if not os.access(script_path, os.X_OK):
        return False, "sync.sh not executable"
    
    return True, "sync.sh exists and is executable"

def test_email_scanner_exists():
    """Test that email_scanner.py exists"""
    import os
    script_path = "/home/workspace/Sites/wheres-v-staging/scripts/email_scanner.py"
    if not os.path.exists(script_path):
        return False, f"email_scanner.py not found"
    
    return True, "email_scanner.py exists"

if __name__ == "__main__":
    print("=== Phase 4 Unit Tests ===\n")
    
    tests = [
        ("Scheduled task exists", test_scheduled_task_exists),
        ("Sync script exists", test_sync_script_exists),
        ("Email scanner exists", test_email_scanner_exists),
    ]
    
    passed = 0
    for name, test_func in tests:
        success, msg = test_func()
        status = "✓" if success else "✗"
        print(f"{status} {name}: {msg}")
        if success:
            passed += 1
    
    print(f"\n=== Phase 4 Tests: {passed}/{len(tests)} PASSED ===")
    
    exit(0 if passed == len(tests) else 1)
