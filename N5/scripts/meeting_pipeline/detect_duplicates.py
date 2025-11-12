#!/usr/bin/env python3
"""
Duplicate Detection Monitor
Scans Inbox for duplicate meeting files despite semantic normalization
ALERT: Critical if duplicates found - indicates semantic normalizer failure
"""
import sys
import logging
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, '/home/workspace/N5/scripts/meeting_pipeline')
from semantic_filename import get_meeting_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

INBOX_PATH = Path("/home/workspace/Personal/Meetings/Inbox")
AUDIT_LOG = Path("/home/workspace/N5/logs/drive_ingestion_audit.jsonl")


def scan_for_duplicates():
    """
    Scan Inbox and detect duplicate meeting_ids
    
    Returns:
        dict: {meeting_id: [list of files]} for duplicates
    """
    files = list(INBOX_PATH.glob("*.transcript.md"))
    logger.info(f"Scanning {len(files)} files in Inbox")
    
    # Group by meeting_id
    by_id = {}
    for f in files:
        mid = get_meeting_id(f.name)
        if mid not in by_id:
            by_id[mid] = []
        by_id[mid].append(f.name)
    
    # Find duplicates
    duplicates = {mid: files for mid, files in by_id.items() if len(files) > 1}
    
    return duplicates


def log_audit(event_type, data):
    """Log to audit trail"""
    import json
    with open(AUDIT_LOG, 'a') as f:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            **data
        }
        f.write(json.dumps(entry) + "\n")


def main():
    """
    Main execution
    
    Exit codes:
        0: No duplicates (all good)
        1: Duplicates detected (CRITICAL)
    """
    try:
        logger.info("Starting duplicate detection scan")
        
        duplicates = scan_for_duplicates()
        
        if not duplicates:
            logger.info("✓ No duplicates detected")
            log_audit("duplicate_scan", {"status": "clean", "duplicates_found": 0})
            return 0
        
        # CRITICAL: Duplicates found
        logger.error(f"🚨 DUPLICATES DETECTED: {len(duplicates)} groups")
        
        for mid, files in duplicates.items():
            logger.error(f"  {mid}:")
            for f in files:
                logger.error(f"    - {f}")
        
        log_audit("duplicate_scan", {
            "status": "DUPLICATES_FOUND",
            "duplicate_count": len(duplicates),
            "groups": {mid: files for mid, files in list(duplicates.items())[:5]}
        })
        
        logger.error("🚨 ACTION REQUIRED: Pause ingestion and investigate")
        logger.error("Run: touch /home/workspace/N5/data/flags/ingestion.meetings.paused")
        
        return 1
        
    except Exception as e:
        logger.error(f"Error during scan: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
