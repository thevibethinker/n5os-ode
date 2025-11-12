#!/usr/bin/env python3
"""
Auto-standardization watcher.
Scans for unstandardized meetings with B26 and standardizes them.

Can run as cron job or continuous service.
"""

import logging
import sys
import time
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))
from standardize_meeting import standardize_meeting, validate_folder_name

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def find_unstandardized_meetings() -> List[Path]:
    """Find meeting folders that need standardization."""
    unstandardized = []
    
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir():
            continue
        
        # Skip Inbox and other special folders
        if meeting_dir.name in ["Inbox", ".stfolder", ".stversions"]:
            continue
        
        # Skip if already standardized
        if validate_folder_name(meeting_dir.name):
            continue
        
        # Only process if has B26
        b26_file = meeting_dir / "B26_metadata.md"
        if not b26_file.exists():
            continue
        
        unstandardized.append(meeting_dir)
    
    return unstandardized


def run_once() -> int:
    """Run one pass of standardization."""
    logger.info("Scanning for unstandardized meetings...")
    
    unstandardized = find_unstandardized_meetings()
    
    if not unstandardized:
        logger.info("✓ All meetings are standardized")
        return 0
    
    logger.info(f"Found {len(unstandardized)} meeting(s) to standardize")
    
    success_count = 0
    for meeting_dir in unstandardized:
        meeting_id = meeting_dir.name
        logger.info(f"Processing: {meeting_id}")
        
        try:
            if standardize_meeting(meeting_id):
                success_count += 1
            else:
                logger.warning(f"  Standardization failed for {meeting_id}")
        except Exception as e:
            logger.error(f"  Error standardizing {meeting_id}: {e}")
    
    logger.info(f"✓ Standardized {success_count}/{len(unstandardized)} meetings")
    return 0


def run_continuous(interval_seconds: int = 60):
    """Run continuously, checking every interval."""
    logger.info(f"Starting continuous mode (checking every {interval_seconds}s)")
    
    while True:
        try:
            run_once()
        except Exception as e:
            logger.error(f"Error in run_once: {e}")
        
        time.sleep(interval_seconds)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-standardize meetings watcher")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=60, help="Check interval (seconds) for continuous mode")
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous(args.interval)
    else:
        sys.exit(run_once())
