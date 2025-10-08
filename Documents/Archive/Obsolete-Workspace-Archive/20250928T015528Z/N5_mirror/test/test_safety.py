#!/usr/bin/env python3
"""
N5 OS Phase 8: Safety Test Suite

Tests safety functionality:
- Validation scripts work
- Schema validation
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

def test_validation_script():
    """Test validation script."""
    print("Testing validation script...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_validate_modules_flows.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ Validation script failed: {stderr}")
    return success

def test_docgen_validation():
    """Test that docgen validates commands."""
    print("Testing docgen validation...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_docgen.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ Docgen validation failed: {stderr}")
    return success

def test_safety():
    """Test safety functionality."""
    tests = [
        test_validation_script,
        test_docgen_validation
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
    print("Running N5 Phase 8: Safety Test Suite...")
    
    results, success = test_safety()
    
    # Telemetry
    telemetry = {
        'phase': 8,
        'component': 'safety',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    telemetry['checksums']['n5_validate_modules_flows.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_validate_modules_flows.py')
    telemetry['checksums']['n5_docgen.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_docgen.py')
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase8_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 8 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)