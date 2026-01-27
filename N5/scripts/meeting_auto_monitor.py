#!/usr/bin/env python3
"""
Meeting Auto Monitor - Automated discovery and queueing of new meetings
Monitors Google Drive folders for new transcripts and queues them for processing.
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Set

# Add workspace to Python path for imports
import sys
sys.path.insert(0, '/home/workspace')

from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path(WORKSPACE)

# Paths
PROCESSED_LOG = WORKSPACE / "N5" / "logs" / "meeting-processing" / "processed_transcripts.jsonl"
STAGING_DIR = WORKSPACE / "Documents" / "Meetings" / "_staging"
QUEUE_DIR = WORKSPACE / "N5" / "queues" / "meeting-processing"

# Ensure directories exist
PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_transcripts() -> Set[str]:
    """Load set of already-processed transcript file IDs."""
    if not PROCESSED_LOG.exists():
        return set()
    
    processed = set()
    with open(PROCESSED_LOG, 'r') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                processed.add(record['file_id'])
    
    return processed


def log_processed_transcript(file_id: str, file_name: str, download_path: str):
    """Append to processed transcripts log."""
    record = {
        'file_id': file_id,
        'file_name': file_name,
        'download_path': download_path,
        'discovered_at': datetime.utcnow().isoformat() + 'Z',
        'status': 'downloaded'
    }
    
    with open(PROCESSED_LOG, 'a') as f:
        f.write(json.dumps(record) + '\n')
    
    logger.info(f"Logged transcript: {file_name}")


def create_processing_queue(transcripts: List[Dict]) -> Path:
    """
    Create a queue file that lists all unprocessed transcripts.
    This file will be read by the scheduled task that calls Zo.
    """
    if not transcripts:
        return None
    
    queue_file = QUEUE_DIR / f"queue_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    queue_data = {
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'transcripts': transcripts,
        'count': len(transcripts)
    }
    
    queue_file.write_text(json.dumps(queue_data, indent=2))
    logger.info(f"Created processing queue: {queue_file}")
    
    return queue_file


def main():
    """
    Main monitoring function.
    
    This is called by a scheduled task and prepares transcripts for Zo to process.
    It does NOT do the processing itself - it just downloads and queues.
    """
    logger.info("=== Meeting Auto-Monitor Started ===")
    
    # Note: Actual Google Drive checking happens in the scheduled task
    # This script is just the helper. The real work is done by the scheduled task
    # that calls Zo with instructions to check, download, and process.
    
    logger.info("This script is a helper. The scheduled task will call Zo directly.")
    logger.info("See the scheduled task 'meeting-auto-processor' for the main logic.")
    
    return 0


if __name__ == "__main__":
    exit(main())
