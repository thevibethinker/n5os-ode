#!/usr/bin/env python3
"""
Google Drive Meeting Transcript Orchestrator
Downloads unprocessed transcripts and enqueues them to Huey pipeline

Designed to be called by scheduled task (Zo orchestration)
"""
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
STAGING_DIR = WORKSPACE / "N5/data/staging/meetings"
GDRIVE_FOLDER_ID = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"
PROCESSED_MARKER = "[ZO-PROCESSED]"

# Add services to path for Huey
sys.path.insert(0, str(WORKSPACE / "N5/services"))

def main(dry_run=False):
    """
    Main orchestration function
    
    This is called by a Zo scheduled task which:
    1. Lists files from Google Drive
    2. Filters unprocessed files
    3. Downloads them
    4. Enqueues to Huey for processing
    """
    from huey_queue.tasks import process_batch
    
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Google Drive Meeting Orchestrator")
    logger.info("=" * 60)
    
    # Instructions for Zo to execute
    logger.info("""
    
    🤖 ZO: Please execute the following steps:
    
    1. List files from Google Drive folder {folder_id}
       Tool: use_app_google_drive
       Action: google_drive-list-files
       Config: {{"folderId": "{folder_id}", "trashed": false}}
    
    2. Filter for unprocessed transcripts:
       - Skip files starting with "{marker}"
       - Only .docx files
       - Save list to: {staging_dir}/download_queue.json
    
    3. Download each file:
       Tool: use_app_google_drive  
       Action: google_drive-download-file
       For each file_id in queue:
         - Download to {staging_dir}/{{filename}}
    
    4. After all downloads complete, run:
       python3 {script} --execute
    
    """.format(
        folder_id=GDRIVE_FOLDER_ID,
        marker=PROCESSED_MARKER,
        staging_dir=STAGING_DIR,
        script=__file__
    ))
    
    if dry_run:
        logger.info("✅ Dry-run complete - instructions printed for Zo")
        return 0
    
    # This executes AFTER Zo has downloaded files
    logger.info("📦 Checking staging directory for downloaded files...")
    
    docx_files = list(STAGING_DIR.glob("*.docx"))
    if not docx_files:
        logger.info("No files to process")
        return 0
    
    logger.info(f"Found {len(docx_files)} files to process")
    
    # Enqueue to Huey
    logger.info("🚀 Enqueueing batch to Huey...")
    result = process_batch.schedule(args=(str(STAGING_DIR),), delay=0)
    
    logger.info(f"✅ Batch enqueued: {result.id}")
    logger.info("Worker will process: deduplicate → convert → stage")
    
    return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Execute after Zo downloads")
    parser.add_argument("--dry-run", action="store_true", help="Print instructions only")
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run or not args.execute))
