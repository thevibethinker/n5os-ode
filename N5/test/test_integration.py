#!/usr/bin/env python3
"""
N5 OS Integration Tests

Tests cross-phase interactions:
- commands+config
- lists+indexer
- indexer+commands
- modules+flows
"""

import subprocess
import sys
from pathlib import Path
import json
import hashlib
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
        result = subprocess.run(full_cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_commands_config_integration():
    """Test commands work with config."""
    print("Testing commands + config integration...")
    n5_root = Path('/home/workspace/N5')
    # Test docgen which uses config
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_docgen.py',
        [],
        cwd=n5_root
    )
    if not success:
        print(f"❌ Commands+config failed: {stderr}")
    return success

def test_lists_indexer_integration():
    """Test lists update indexer."""
    print("Testing lists + indexer integration...")
    n5_root = Path('/home/workspace/N5')
    # Run lists-docgen, then index-update
    success1, _, _ = run_command_test(n5_root / 'scripts' / 'n5_lists_docgen.py', [], cwd=n5_root)
    success2, _, _ = run_command_test(n5_root / 'scripts' / 'n5_index_update.py', [], cwd=n5_root)
    
    if not (success1 and success2):
        print("❌ Lists+indexer failed")
        return False
    
    # Check if index includes lists
    with open(n5_root / 'index.jsonl', 'r') as f:
        index_lines = f.readlines()
    
    has_lists = any('lists/' in line for line in index_lines)
    if not has_lists:
        print("❌ Index does not include lists")
        return False
    
    print("✅ Lists+indexer integration works")
    return True

def test_indexer_commands_integration():
    """Test indexer updates command docs."""
    print("Testing indexer + commands integration...")
    n5_root = Path('/home/workspace/N5')
    # Run docgen, then index-rebuild
    success1, _, _ = run_command_test(n5_root / 'scripts' / 'n5_docgen.py', [], cwd=n5_root)
    success2, _, _ = run_command_test(n5_root / 'scripts' / 'n5_index_rebuild.py', [], cwd=n5_root)
    
    if not (success1 and success2):
        print("❌ Indexer+commands failed")
        return False
    
    # Check if index includes commands
    with open(n5_root / 'index.jsonl', 'r') as f:
        index_lines = f.readlines()
    
    has_commands = any('commands/' in line for line in index_lines)
    if not has_commands:
        print("❌ Index does not include commands")
        return False
    
    print("✅ Indexer+commands integration works")
    return True

def test_modules_flows_integration():
    """Test modules and flows work together."""
    print("Testing modules + flows integration...")
    n5_root = Path('/home/workspace/N5')
    # Test flow-run if possible, or just validate
    success, _, _ = run_command_test(
        n5_root / 'scripts' / 'n5_validate_modules_flows.py',
        [],
        cwd=n5_root
    )
    if not success:
        print("❌ Modules+flows failed")
    return success

def test_integration():
    """Test integration across phases."""
    tests = [
        test_commands_config_integration,
        test_lists_indexer_integration,
        test_indexer_commands_integration,
        test_modules_flows_integration
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    all_passed = all(results.values())
    return results, all_passed

if __name__ == '__main__':
    print("Running N5 Integration Tests...")
    
    results, success = test_integration()
    
    # Telemetry
    telemetry = {
        'phase': 'integration',
        'component': 'integration',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    telemetry['checksums']['index.jsonl'] = get_file_checksum(n5_root / 'index.jsonl')
    
    # Save telemetry
    with open('/home/workspace/N5/test/integration_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nIntegration Tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)