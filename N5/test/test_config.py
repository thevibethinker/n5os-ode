#!/usr/bin/env python3
"""
N5 OS Phase 2: Config Test Suite

Tests configuration functionality:
- prefs.md exists and is readable
- Config merging works correctly
"""

import sys
from pathlib import Path
import json
import hashlib

def test_prefs_exists():
    """Test that prefs.md exists and is readable."""
    print("Testing prefs.md exists...")
    n5_root = Path('/home/workspace/N5')
    prefs_file = n5_root / 'prefs.md'
    if not prefs_file.exists():
        print("❌ prefs.md does not exist")
        return False
    
    try:
        with open(prefs_file, 'r') as f:
            content = f.read()
        if not content.strip():
            print("❌ prefs.md is empty")
            return False
        print("✅ prefs.md exists and readable")
        return True
    except Exception as e:
        print(f"❌ Error reading prefs.md: {e}")
        return False

def test_config_merge():
    """Test config merge functionality."""
    print("Testing config merge...")
    try:
        import sys
        sys.path.insert(0, '/home/workspace/N5/scripts')
        from n5_config_merge import merge_configs
        
        # Test basic merge
        layers = [
            ("global", {"dry_run": False, "timeout": 30}),
            ("project", {"timeout": 60, "tags": ["test"]}),
            ("task", {"dry_run": True})
        ]
        
        merged, explain = merge_configs(layers)
        
        expected = {
            "dry_run": True,  # sticky
            "timeout": 60,    # last wins
            "tags": ["test"]  # from project
        }
        
        if merged == expected:
            print("✅ Config merge works correctly")
            return True
        else:
            print(f"❌ Config merge failed: got {merged}, expected {expected}")
            return False
            
    except Exception as e:
        print(f"❌ Config merge test failed: {e}")
        return False

def test_config():
    """Test config functionality."""
    tests = [
        test_prefs_exists,
        test_config_merge
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
    print("Running N5 Phase 2: Config Test Suite...")
    
    results, success = test_config()
    
    # Telemetry
    telemetry = {
        'phase': 2,
        'component': 'config',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    telemetry['checksums']['prefs.md'] = get_file_checksum(n5_root / 'prefs.md')
    telemetry['checksums']['n5_config_merge.py'] = get_file_checksum(n5_root / 'scripts' / 'n5_config_merge.py')
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase2_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 2 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)