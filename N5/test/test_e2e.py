#!/usr/bin/env python3
"""
N5 OS End-to-End Tests

Tests full workflows:
- Boot: Initialize system
- Cycle: Update and rebuild
- Safety: Validate everything
- Edge cases
"""

import subprocess
import sys
from pathlib import Path
import json
import hashlib
import tempfile
import shutil

def get_file_checksum(file_path):
    """Get SHA256 checksum of file."""
    if not file_path.exists():
        return None
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def run_command_test(cmd, args=None, cwd=None):
    """Run a command and check for success."""
    try:
        full_cmd = ['python3', str(cmd)]
        if args:
            full_cmd.extend(args)
        result = subprocess.run(full_cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_boot_workflow():
    """Test boot workflow: initialize from scratch."""
    print("Testing boot workflow...")
    n5_root = Path('/home/workspace/N5')
    
    # Simulate boot by rebuilding index
    success, _, _ = run_command_test(
        n5_root / 'scripts' / 'n5_index_rebuild.py',
        [],
        cwd=n5_root
    )
    
    if not success:
        print("❌ Boot workflow failed")
        return False
    
    # Check essential files exist
    essentials = [
        n5_root / 'index.jsonl',
        n5_root / 'index.md',
        n5_root / 'commands.md',
        n5_root / 'prefs.md'
    ]
    
    for file in essentials:
        if not file.exists():
            print(f"❌ Essential file missing: {file}")
            return False
    
    print("✅ Boot workflow successful")
    return True

def test_cycle_workflow():
    """Test cycle workflow: update and maintain."""
    print("Testing cycle workflow...")
    n5_root = Path('/home/workspace/N5')
    
    # Run update cycle
    commands = [
        ('n5_docgen.py', []),
        ('n5_lists_docgen.py', []),
        ('n5_index_update.py', []),
    ]
    
    for cmd, args in commands:
        success, _, stderr = run_command_test(n5_root / 'scripts' / cmd, args, cwd=n5_root)
        if not success:
            print(f"❌ Cycle failed at {cmd}: {stderr}")
            return False
    
    print("✅ Cycle workflow successful")
    return True

def test_safety_workflow():
    """Test safety workflow: validation."""
    print("Testing safety workflow...")
    n5_root = Path('/home/workspace/N5')
    
    # Run all validations
    validations = [
        ('n5_validate_modules_flows.py', []),
        ('n5_docgen.py', []),  # Validates schemas
    ]
    
    for cmd, args in validations:
        success, _, stderr = run_command_test(n5_root / 'scripts' / cmd, args, cwd=n5_root)
        if not success:
            print(f"❌ Safety failed at {cmd}: {stderr}")
            return False
    
    print("✅ Safety workflow successful")
    return True

def test_edge_cases():
    """Test edge cases."""
    print("Testing edge cases...")
    n5_root = Path('/home/workspace/N5')
    
    # Test dry-run modes
    dry_run_tests = [
        ('n5_lists_create.py', ['test-edge', 'Test Edge', '--dry-run']),
        ('n5_lists_add.py', ['ideas', 'Edge case item', '--dry-run']),
    ]
    
    for cmd, args in dry_run_tests:
        success, _, stderr = run_command_test(n5_root / 'scripts' / cmd, args, cwd=n5_root)
        if not success:
            print(f"❌ Edge case failed at {cmd}: {stderr}")
            return False
    
    # Test invalid inputs
    invalid_tests = [
        ('n5_lists_find.py', ['nonexistent-list']),
    ]
    
    for cmd, args in invalid_tests:
        success, _, _ = run_command_test(n5_root / 'scripts' / cmd, args, cwd=n5_root)
        # These should fail gracefully
        if success:
            print(f"❌ Edge case should have failed: {cmd}")
            return False
    
    print("✅ Edge cases handled correctly")
    return True

def test_e2e():
    """Test end-to-end workflows."""
    tests = [
        test_boot_workflow,
        test_cycle_workflow,
        test_safety_workflow,
        test_edge_cases
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    all_passed = all(results.values())
    return results, all_passed

if __name__ == '__main__':
    print("Running N5 End-to-End Tests...")
    
    results, success = test_e2e()
    
    # Telemetry
    telemetry = {
        'phase': 'e2e',
        'component': 'e2e',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    key_files = [
        'index.jsonl', 'index.md', 'commands.md', 'commands.jsonl',
        'prefs.md', 'lists/index.jsonl'
    ]
    for file in key_files:
        telemetry['checksums'][file] = get_file_checksum(n5_root / file)
    
    # Save telemetry
    with open('/home/workspace/N5/test/e2e_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nEnd-to-End Tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)