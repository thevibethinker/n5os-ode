#!/usr/bin/env python3
"""
N5 OS Comprehensive Test Runner

Executes all test phases and collects telemetry.
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

def run_test_phase(phase_num, test_file):
    """Run a test phase and return results."""
    print(f"\n{'='*50}")
    print(f"Running Phase {phase_num}")
    print('='*50)
    
    try:
        result = subprocess.run(
            ['python3', str(test_file)],
            cwd='/home/workspace/N5',
            capture_output=True,
            text=True,
            timeout=300
        )
        success = result.returncode == 0
        print(result.stdout)
        if not success:
            print(result.stderr)
        return success, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running phase {phase_num}: {e}")
        return False, "", str(e)

def collect_telemetry():
    """Collect all telemetry files."""
    test_dir = Path('/home/workspace/N5/test')
    telemetry_files = list(test_dir.glob('*_telemetry.json'))
    
    telemetry = {}
    for file in telemetry_files:
        with open(file, 'r') as f:
            phase_data = json.load(f)
            telemetry[phase_data['phase']] = phase_data
    
    return telemetry

def main():
    """Run all test phases."""
    print("N5 OS Comprehensive Test Plan Execution")
    print("=======================================")
    
    test_phases = [
        (0, 'test/test_schemas.py'),
        (1, 'test/test_commands.py'),
        (2, 'test/test_config.py'),
        (3, 'test/test_lists.py'),
        (4, 'test/test_records.py'),  # Assuming phase 4 is records, but we skipped it
        (5, 'test/test_indexer.py'),
        (6, 'test/test_knowledge.py'),
        (7, 'test/test_modules.py'),
        (8, 'test/test_safety.py'),
        ('integration', 'test/test_integration.py'),
        ('e2e', 'test/test_e2e.py')
    ]
    
    results = {}
    all_success = True
    
    for phase, test_file in test_phases:
        test_path = Path('/home/workspace/N5') / test_file
        if not test_path.exists():
            print(f"Skipping phase {phase}: {test_file} not found")
            results[phase] = {'success': False, 'error': 'Test file not found'}
            all_success = False
            continue
            
        success, stdout, stderr = run_test_phase(phase, test_path)
        results[phase] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        if not success:
            all_success = False
    
    # Collect telemetry
    telemetry = collect_telemetry()
    
    # Overall summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    print(f"Overall Result: {'PASSED' if all_success else 'FAILED'}")
    
    for phase, result in results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"Phase {phase}: {status}")
    
    # Save master telemetry
    master_telemetry = {
        'test_run': {
            'timestamp': '2025-09-18T04:10:31Z',
            'overall_success': all_success,
            'results': results
        },
        'phases': telemetry
    }
    
    with open('/home/workspace/N5/test/master_telemetry.json', 'w') as f:
        json.dump(master_telemetry, f, indent=2)
    
    print(f"\nDetailed telemetry saved to: /home/workspace/N5/test/master_telemetry.json")
    
    return all_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)