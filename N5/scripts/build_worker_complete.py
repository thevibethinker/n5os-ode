#!/usr/bin/env python3
"""Legacy worker completion notification.

This is a thin wrapper around update_build.py for backwards compatibility
with v1 build system that used --build-id and --worker-num.

Usage:
  python3 build_worker_complete.py --build-id <slug> --worker-num <num> --status <status>
"""

import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Legacy worker completion')
    parser.add_argument('--build-id', required=True, help='Build slug')
    parser.add_argument('--worker-num', required=True, help='Worker number')
    parser.add_argument('--status', default='complete', 
                       choices=['complete', 'partial', 'blocked', 'failed'])
    parser.add_argument('--summary', help='Summary of work')
    
    args = parser.parse_args()
    
    # Convert to new format
    # Worker W1 → Drop D1.1, W2 → D1.2, etc.
    drop_id = f"W{args.worker_num}"  # Keep legacy format for legacy builds
    
    # Call update_build.py
    cmd = [
        'python3', '/home/workspace/N5/scripts/update_build.py',
        'complete', args.build_id, drop_id,
        '--status', args.status,
    ]
    
    if args.summary:
        cmd.extend(['--summary', args.summary])
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())