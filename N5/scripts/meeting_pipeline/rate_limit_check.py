#!/usr/bin/env python3
"""
Rate Limit Guardian
Detects runaway ingestion (too many files created too fast)
ALERT: If >50 files/hour, pause system and investigate
"""
import sys
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

INBOX_PATH = Path("/home/workspace/Personal/Meetings/Inbox")
AUDIT_LOG = Path("/home/workspace/N5/logs/drive_ingestion_audit.jsonl")
PAUSE_FLAG = Path("/home/workspace/N5/data/flags/ingestion.meetings.paused")

# Safety limits
MAX_FILES_PER_HOUR = 50
MAX_FILES_PER_10MIN = 15


def count_recent_files(seconds):
    """Count files created in last N seconds"""
    now = time.time()
    cutoff = now - seconds
    
    files = [
        f for f in INBOX_PATH.glob("*.transcript.md")
        if f.stat().st_mtime > cutoff
    ]
    
    return len(files)


def create_pause_flag(reason):
    """Create pause flag to stop ingestion"""
    content = f"""paused=true
reason={reason}
timestamp={datetime.now(timezone.utc).isoformat()}
contact=operator
action_required=investigate_rate_limit
"""
    PAUSE_FLAG.write_text(content)
    logger.error(f"🚨 PAUSE FLAG CREATED: {PAUSE_FLAG}")


def log_audit(event_type, data):
    """Log to audit trail"""
    with open(AUDIT_LOG, 'a') as f:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            **data
        }
        f.write(json.dumps(entry) + "\n")


def main():
    """
    Check ingestion rate and pause if exceeded
    
    Exit codes:
        0: Rate OK
        1: Rate limit exceeded (system paused)
    """
    try:
        # Check 10-minute rate
        recent_10min = count_recent_files(600)
        logger.info(f"Files in last 10 min: {recent_10min} (limit: {MAX_FILES_PER_10MIN})")
        
        if recent_10min > MAX_FILES_PER_10MIN:
            logger.error(f"🚨 RATE LIMIT EXCEEDED: {recent_10min} files in 10 minutes")
            create_pause_flag(f"rate_limit_10min_{recent_10min}_files")
            log_audit("rate_limit_exceeded", {
                "period": "10min",
                "count": recent_10min,
                "limit": MAX_FILES_PER_10MIN,
                "action": "paused"
            })
            return 1
        
        # Check hourly rate
        recent_1hour = count_recent_files(3600)
        logger.info(f"Files in last 1 hour: {recent_1hour} (limit: {MAX_FILES_PER_HOUR})")
        
        if recent_1hour > MAX_FILES_PER_HOUR:
            logger.error(f"🚨 RATE LIMIT EXCEEDED: {recent_1hour} files in 1 hour")
            create_pause_flag(f"rate_limit_1hour_{recent_1hour}_files")
            log_audit("rate_limit_exceeded", {
                "period": "1hour",
                "count": recent_1hour,
                "limit": MAX_FILES_PER_HOUR,
                "action": "paused"
            })
            return 1
        
        # All good
        logger.info("✓ Rate limit OK")
        log_audit("rate_limit_check", {
            "status": "ok",
            "recent_10min": recent_10min,
            "recent_1hour": recent_1hour
        })
        return 0
        
    except Exception as e:
        logger.error(f"Error during rate check: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
