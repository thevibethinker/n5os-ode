#!/usr/bin/env python3
"""
Google Drive Transcript Fetcher V2
Simple wrapper that uses Zo's built-in Google Drive tools
"""
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

FOLDER_ID = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"

def main():
    """
    This is a stub that will be called by Zo's scheduled task.
    The actual work (listing, downloading, converting) will be done
    by Zo directly using use_app_google_drive tool.
    
    This script just signals that the task should run.
    """
    logger.info(f"Triggering Google Drive fetch from folder: {FOLDER_ID}")
    logger.info("Zo will handle: list → download → convert → mark processed")
    
    # Output for Zo to consume
    print(json.dumps({
        "action": "fetch_transcripts",
        "folder_id": FOLDER_ID,
        "target_inbox": "/home/workspace/Personal/Meetings/Inbox"
    }))
    
    return 0

if __name__ == "__main__":
    exit(main())
