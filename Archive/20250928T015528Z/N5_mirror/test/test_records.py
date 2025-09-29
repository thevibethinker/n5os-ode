#!/usr/bin/env python3
"""
N5 OS Phase 4: Records Test Suite

Tests records functionality (list items).
"""

import sys
from pathlib import Path
import json
import hashlib

def test_records_structure():
    """Test that records (list items) are valid."""
    print("Testing records structure...")
    n5_root = Path('/home/workspace/N5')
    lists_dir = n5_root / 'lists'
    
    jsonl_files = list(lists_dir.glob('*.jsonl'))
    if not jsonl_files:
        print("❌ No record files found")
        return False
    
    for jsonl_file in jsonl_files:
        if jsonl_file.name == 'index.jsonl':
            continue  # Skip registry
        
        try:
            with open(jsonl_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:
                    record = json.loads(line)
                    # Check required fields
                    required = ['id', 'created_at', 'title', 'status']
                    for field in required:
                        if field not in record:
                            print(f"❌ Record missing {field} in {jsonl_file}:{line_num}")
                            return False
        except Exception as e:
            print(f"❌ Error validating {jsonl_file}: {e}")
            return False
    
    print("✅ Records structure valid")
    return True

def test_records():
    """Test records functionality."""
    tests = [test_records_structure]
    
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
    print("Running N5 Phase 4: Records Test Suite...")
    
    results, success = test_records()
    
    # Telemetry
    telemetry = {
        'phase': 4,
        'component': 'records',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    for jsonl_file in (n5_root / 'lists').glob('*.jsonl'):
        if jsonl_file.name != 'index.jsonl':
            telemetry['checksums'][f'records_{jsonl_file.name}'] = get_file_checksum(jsonl_file)
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase4_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 4 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)