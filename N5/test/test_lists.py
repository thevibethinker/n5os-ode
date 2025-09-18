#!/usr/bin/env python3
"""
N5 OS Phase 3: Lists Test Suite

Tests lists functionality:
- Lists registry operations
- List item operations
- Export and docgen
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

def test_lists_find():
    """Test lists-find command."""
    print("Testing lists-find...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_lists_find.py',
        ['ideas'],
        cwd=n5_root
    )
    if not success:
        print(f"❌ lists-find failed: {stderr}")
    return success

def test_lists_docgen():
    """Test lists-docgen command."""
    print("Testing lists-docgen...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_lists_docgen.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ lists-docgen failed: {stderr}")
    return success

def test_lists_export():
    """Test lists-export command."""
    print("Testing lists-export...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_lists_export.py',
        ['ideas', 'md', '/tmp/test_export.md'],
        cwd=n5_root
    )
    if not success:
        print(f"❌ lists-export failed: {stderr}")
    return success

def test_lists_registry():
    """Test lists registry structure."""
    print("Testing lists registry...")
    n5_root = Path('/home/workspace/N5')
    index_file = n5_root / 'lists' / 'index.jsonl'
    if not index_file.exists():
        print("❌ Lists index.jsonl does not exist")
        return False
    
    try:
        with open(index_file, 'r') as f:
            lines = f.readlines()
        if not lines:
            print("❌ Lists registry is empty")
            return False
        
        # Check that each line is valid JSON
        for line in lines:
            json.loads(line.strip())
        
        print("✅ Lists registry is valid")
        return True
    except Exception as e:
        print(f"❌ Lists registry validation failed: {e}")
        return False

def test_lists():
    """Test lists functionality."""
    tests = [
        test_lists_registry,
        test_lists_find,
        test_lists_docgen,
        test_lists_export
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
    print("Running N5 Phase 3: Lists Test Suite...")
    
    results, success = test_lists()
    
    # Telemetry
    telemetry = {
        'phase': 3,
        'component': 'lists',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    telemetry['checksums']['lists_index.jsonl'] = get_file_checksum(n5_root / 'lists' / 'index.jsonl')
    for jsonl_file in (n5_root / 'lists').glob('*.jsonl'):
        telemetry['checksums'][f'lists_{jsonl_file.name}'] = get_file_checksum(jsonl_file)
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase3_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 3 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)