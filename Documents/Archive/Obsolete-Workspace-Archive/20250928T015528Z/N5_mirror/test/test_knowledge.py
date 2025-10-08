#!/usr/bin/env python3
"""
N5 OS Phase 6: Knowledge Test Suite

Tests knowledge functionality:
- Knowledge files exist
- Knowledge commands work
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

def test_knowledge_files():
    """Test that knowledge files exist and are readable."""
    print("Testing knowledge files...")
    n5_root = Path('/home/workspace/N5')
    knowledge_dir = n5_root / 'knowledge'
    
    if not knowledge_dir.exists():
        print("❌ Knowledge directory does not exist")
        return False
    
    files = list(knowledge_dir.glob('**/*.md'))
    if not files:
        print("❌ No knowledge files found")
        return False
    
    for file in files:
        try:
            with open(file, 'r') as f:
                content = f.read()
            if not content.strip():
                print(f"❌ Knowledge file {file.name} is empty")
                return False
        except Exception as e:
            print(f"❌ Error reading {file.name}: {e}")
            return False
    
    print("✅ Knowledge files exist and are readable")
    return True

def test_knowledge_find():
    """Test knowledge-find command."""
    print("Testing knowledge-find...")
    n5_root = Path('/home/workspace/N5')
    success, stdout, stderr = run_command_test(
        n5_root / 'scripts' / 'n5_knowledge_find.py',
        [],
        cwd=n5_root
    )
    # knowledge-find might return empty if no facts, so check if it runs without error
    if not success:
        print(f"❌ knowledge-find failed: {stderr}")
    return success

def test_knowledge():
    """Test knowledge functionality."""
    tests = [
        test_knowledge_files,
        test_knowledge_find
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
    print("Running N5 Phase 6: Knowledge Test Suite...")
    
    results, success = test_knowledge()
    
    # Telemetry
    telemetry = {
        'phase': 6,
        'component': 'knowledge',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    for md_file in (n5_root / 'knowledge').glob('**/*.md'):
        telemetry['checksums'][f'knowledge_{md_file.relative_to(n5_root)}'] = get_file_checksum(md_file)
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase6_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 6 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)