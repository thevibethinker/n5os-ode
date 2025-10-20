#!/usr/bin/env python3
"""
Post-write Digest Scan

Background scanner for detecting placeholder text in all digest files.
Useful to catch legacy or manual file changes.

Usage:
    post_write_digest_scan.py
"""

import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='/home/workspace/N5/logs/digest_validation.log',
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

DIGESTS_DIR = Path("/home/workspace/N5/digests")
VALIDATOR_SCRIPT = Path("/home/workspace/N5/scripts/validate_digest_output.py")


def scan_all_digests():
    if not DIGESTS_DIR.exists():
        print("Digests directory does not exist.")
        return
    
    for digest_file in DIGESTS_DIR.glob("daily-meeting-prep-*.md"):
        result = subprocess.run([
            "python3",
            str(VALIDATOR_SCRIPT),
            str(digest_file),
        ], capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Placeholder detected in {digest_file}: {result.stdout.strip()}")
            print(f"[ALERT] Placeholder detected in {digest_file}")
        else:
            print(f"[OK] {digest_file} clean.")


if __name__ == '__main__':
    scan_all_digests()
