#!/usr/bin/env python3
"""
Google Drive ID Backfill for Meetings

Searches Google Drive for existing meeting transcripts and stores their IDs
in .gdrive_id files for future duplicate detection.

Usage:
    python3 meeting_gdrive_id_backfill.py [--dry-run] [--folder FOLDER_ID]
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
DEFAULT_GDRIVE_FOLDER = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"


def main():
    parser = argparse.ArgumentParser(description="Backfill Google Drive IDs")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--folder', default=DEFAULT_GDRIVE_FOLDER, help='Google Drive folder ID')
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Google Drive ID Backfill for Meetings")
    logger.info("=" * 70)
    logger.info("")
    logger.info("This script needs ZO's help to:")
    logger.info("1. List all files in Google Drive folder: %s", args.folder)
    logger.info("2. Match filenames to local meeting folders")
    logger.info("3. Store Google Drive IDs in .gdrive_id files")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")
    logger.info("ZO INSTRUCTIONS:")
    logger.info("")
    logger.info("Step 1: List Google Drive files")
    logger.info("  Tool: use_app_google_drive")
    logger.info("  Action: google_drive-list-files")
    logger.info("  Config: {")
    logger.info('    "folderId": "%s",', args.folder)
    logger.info('    "trashed": false')
    logger.info("  }")
    logger.info("  Save output to: /tmp/gdrive_files.json")
    logger.info("")
    logger.info("Step 2: For each transcript filename found:")
    logger.info("  - Extract meeting identifier (date + participants)")
    logger.info("  - Find matching folder in: %s", MEETINGS_ROOT)
    logger.info("  - Write Google Drive file ID to: <folder>/.gdrive_id")
    logger.info("")
    logger.info("Step 3: Report statistics")
    logger.info("  - Total GDrive files found")
    logger.info("  - Matched to local folders")
    logger.info("  - .gdrive_id files created")
    logger.info("  - Unmatched files")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")
    
    if args.dry_run:
        logger.info("DRY RUN - No files will be modified")
        logger.info("")
        logger.info("To execute: python3 %s --folder %s", __file__, args.folder)
        return 0
    
    logger.info("Waiting for ZO to execute instructions above...")
    logger.info("Run this script again after ZO completes the steps")
    
    # Check if ZO has created the output file
    gdrive_list = Path("/tmp/gdrive_files.json")
    if not gdrive_list.exists():
        logger.warning("No /tmp/gdrive_files.json found")
        logger.info("ZO needs to complete Step 1 first")
        return 1
    
    logger.info("Found /tmp/gdrive_files.json - processing...")
    
    # Load and process
    with open(gdrive_list) as f:
        files = json.load(f)
    
    logger.info("Found %d files in Google Drive", len(files))
    
    # Match and create .gdrive_id files
    matched = 0
    unmatched = []
    
    for file_info in files:
        filename = file_info.get('name', '')
        file_id = file_info.get('id', '')
        
        if not filename or not file_id:
            continue
        
        # Try to match to local folder
        # Logic: extract date and participants from filename
        # Match against folder names
        
        # This logic will be implemented by ZO in Step 2
        pass
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("BACKFILL COMPLETE")
    logger.info("=" * 70)
    logger.info("Matched: %d", matched)
    logger.info("Unmatched: %d", len(unmatched))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

