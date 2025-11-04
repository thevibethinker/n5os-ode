#!/usr/bin/env python3
"""
Deduplicate AI Request Queue
Removes duplicate pending requests for meetings that have already been processed.
"""
import json
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

AI_REQUESTS_DIR = Path("/home/workspace/N5/inbox/ai_requests")
PROCESSED_DIR = AI_REQUESTS_DIR / "processed"


def scan_requests():
    """Scan all requests and group by meeting_id."""
    requests_by_meeting = defaultdict(list)
    
    for request_file in AI_REQUESTS_DIR.glob("*.json"):
        try:
            with open(request_file) as f:
                request = json.load(f)
            
            meeting_id = request.get("inputs", {}).get("meeting_id")
            if not meeting_id:
                continue
            
            requests_by_meeting[meeting_id].append({
                "file": request_file,
                "request_id": request.get("request_id"),
                "status": request.get("status"),
                "created_at": request.get("created_at"),
                "data": request
            })
        except Exception as e:
            logger.error(f"Error reading {request_file.name}: {e}")
    
    return requests_by_meeting


def deduplicate_meeting(meeting_id, requests):
    """For a meeting, keep only the most recent completed OR one pending."""
    # Sort by creation time (oldest first)
    requests.sort(key=lambda r: r["created_at"])
    
    completed = [r for r in requests if r["status"] == "completed"]
    pending = [r for r in requests if r["status"] == "pending"]
    
    to_archive = []
    
    if completed:
        # Meeting has been completed - archive ALL pending requests
        logger.info(f"  {meeting_id}: {len(completed)} completed, archiving {len(pending)} pending")
        to_archive.extend(pending)
        
        # Also archive all but the most recent completed
        if len(completed) > 1:
            to_archive.extend(completed[:-1])
            logger.info(f"    Also archiving {len(completed)-1} old completed requests")
    
    elif len(pending) > 1:
        # No completed, but multiple pending - keep only the oldest
        logger.info(f"  {meeting_id}: {len(pending)} pending, keeping oldest")
        to_archive.extend(pending[1:])
    
    return to_archive


def archive_request(request_info):
    """Move request file to processed directory."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    source = request_info["file"]
    dest = PROCESSED_DIR / source.name
    
    # If destination exists, append timestamp
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        import time
        dest = PROCESSED_DIR / f"{stem}_{int(time.time())}{suffix}"
    
    source.rename(dest)
    logger.info(f"    Archived: {source.name}")


def main():
    logger.info("AI Request Deduplication")
    logger.info("=" * 60)
    
    requests_by_meeting = scan_requests()
    
    logger.info(f"Found {len(requests_by_meeting)} unique meetings with requests")
    
    total_archived = 0
    
    for meeting_id, requests in requests_by_meeting.items():
        if len(requests) > 1:
            logger.info(f"\n{meeting_id}: {len(requests)} requests")
            to_archive = deduplicate_meeting(meeting_id, requests)
            
            for request_info in to_archive:
                archive_request(request_info)
                total_archived += 1
    
    logger.info(f"\n{'=' * 60}")
    logger.info(f"✓ Archived {total_archived} duplicate/obsolete requests")
    logger.info(f"✓ Remaining: {len(list(AI_REQUESTS_DIR.glob('*.json')))} active requests")
    
    return 0


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
