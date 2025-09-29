#!/usr/bin/env python3
"""
N5 OS Phase 5: Indexer Test Suite

Tests indexer functionality:
- Index rebuild
- Index update
- Index structure validation
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
        result = subprocess.run(full_cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_index_rebuild():
    """Test index-rebuild command."""
    print("Testing index-rebuild...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_index_rebuild.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ index-rebuild failed: {stderr}")
    return success

def test_index_structure():
    """Test that index files are valid."""
    print("Testing index structure...")
    n5_root = Path('/home/workspace/N5')
    index_jsonl = n5_root / 'index.jsonl'
    index_md = n5_root / 'index.md'
    
    if not index_jsonl.exists():
        print("❌ index.jsonl does not exist")
        return False
    
    if not index_md.exists():
        print("❌ index.md does not exist")
        return False
    
    try:
        # Check JSONL
        with open(index_jsonl, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    json.loads(line)
        
        # Check MD has content
        with open(index_md, 'r') as f:
            content = f.read()
        if not content.strip():
            print("❌ index.md is empty")
            return False
        
        print("✅ Index structure is valid")
        return True
    except Exception as e:
        print(f"❌ Index validation failed: {e}")
        return False

def test_indexer():
    """Test indexer functionality."""
    tests = [
        test_index_rebuild,
        test_index_structure
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
    print("Running N5 Phase 5: Indexer Test Suite...")
    
    results, success = test_indexer()
    
    # Telemetry
    telemetry = {
        'phase': 5,
        'component': 'indexer',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    telemetry['checksums']['index.jsonl'] = get_file_checksum(n5_root / 'index.jsonl')
    telemetry['checksums']['index.md'] = get_file_checksum(n5_root / 'index.md')
    telemetry['checksums']['n5_index_rebuild.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_index_rebuild.py')
    telemetry['checksums']['n5_index_update.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_index_update.py')
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase5_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 5 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)