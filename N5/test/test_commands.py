#!/usr/bin/env python3
"""
N5 OS Phase 1: Commands Test Suite

Tests command functionality:
- Command scripts execute without errors
- Basic functionality works
"""

import subprocess
import sys
from pathlib import Path
import json
import hashlib

def run_command_test(cmd, args=None, cwd=None):
    """Run a command and check for success."""
    try:
        full_cmd = ['python3', str(cmd)]
        if args:
            full_cmd.extend(args)
        result = subprocess.run(full_cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_docgen():
    """Test docgen command."""
    print("Testing docgen...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(n5_root / 'scripts' / 'n5_docgen.py', cwd=n5_root)
    if not success:
        print(f"❌ docgen failed: {stderr}")
    return success

def test_lists_create():
    """Test lists-create command with dry-run."""
    print("Testing lists-create (dry-run)...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_lists_create.py',
        ['test-list', 'Test List', '--dry-run'],
        cwd=n5_root
    )
    if not success:
        print(f"❌ lists-create failed: {stderr}")
    return success

def test_lists_add():
    """Test lists-add command with dry-run."""
    print("Testing lists-add (dry-run)...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_lists_add.py',
        ['ideas', 'Test item', '--dry-run'],
        cwd=n5_root
    )
    if not success:
        print(f"❌ lists-add failed: {stderr}")
    return success

def test_index_update():
    """Test index-update command."""
    print("Testing index-update...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(n5_root / 'scripts' / 'n5_index_update.py', cwd=n5_root)
    if not success:
        print(f"❌ index-update failed: {stderr}")
    return success

def test_commands():
    """Test key commands."""
    tests = [
        test_docgen,
        test_lists_create,
        test_lists_add,
        test_index_update
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    all_passed = all(results.values())
    return results, all_passed

def get_file_checksum(file_path):
    """Get SHA256 checksum of file."""
    if not file_path.exists():
        return None
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

if __name__ == '__main__':
    print("Running N5 Phase 1: Commands Test Suite...")
    
    results, success = test_commands()
    
    # Telemetry
    telemetry = {
        'phase': 1,
        'component': 'commands',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    for script in (n5_root / 'scripts').glob('n5_*.py'):
        telemetry['checksums'][script.name] = get_file_checksum(script)
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase1_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 1 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)