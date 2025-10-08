#!/usr/bin/env python3
"""
N5 OS Phase 7: Modules Test Suite

Tests modules functionality:
- Modules directory exists
- Existing test suite passes
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

def test_modules_directory():
    """Test that modules directory exists."""
    print("Testing modules directory...")
    n5_root = Path('/home/workspace/N5')
    modules_dir = n5_root / 'modules'
    
    if not modules_dir.exists():
        print("❌ Modules directory does not exist")
        return False
    
    files = list(modules_dir.glob('*.md'))
    if not files:
        print("❌ No module files found")
        return False
    
    print("✅ Modules directory exists with files")
    return True

def test_modules_validation():
    """Test modules validation via existing test suite."""
    print("Testing modules validation...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_test_modules_flows.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ Modules validation failed: {stderr}")
    return success

def test_modules():
    """Test modules functionality."""
    tests = [
        test_modules_directory,
        test_modules_validation
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
    print("Running N5 Phase 7: Modules Test Suite...")
    
    results, success = test_modules()
    
    # Telemetry
    telemetry = {
        'phase': 7,
        'component': 'modules',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    for md_file in (n5_root / 'modules').glob('*.md'):
        telemetry['checksums'][f'modules_{md_file.name}'] = get_file_checksum(md_file)
    telemetry['checksums']['n5_test_modules_flows.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_test_modules_flows.py')
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase7_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 7 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)