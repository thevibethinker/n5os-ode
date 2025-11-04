#!/usr/bin/env python3
"""
Fix meetings stuck in 'queued_for_ai' status by recreating their AI requests.
This handles the case where requests were processed but AI never completed the work.
"""
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
AI_REQUEST_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_requests"
AI_RESPONSES = WORKSPACE_ROOT / "N5/inbox/ai_responses"


def find_stuck_meetings():
    """Find meetings with status='queued_for_ai' that don't have pending requests."""
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT meeting_id, transcript_path, detected_at
        FROM meetings
        WHERE status = 'queued_for_ai'
        ORDER BY detected_at DESC
    """)
    
    stuck_meetings = cursor.fetchall()
    conn.close()
    
    return stuck_meetings


def recreate_ai_request(meeting_id, transcript_path):
    """Create a fresh AI request for a stuck meeting."""
    AI_REQUEST_QUEUE.mkdir(parents=True, exist_ok=True)
    
    request_id = f"meeting_{meeting_id}_{int(datetime.now().timestamp())}"
    
    request = {
        "request_id": request_id,
        "request_type": "meeting_process",
        "prompt_name": "Meeting Process",
        "inputs": {
            "transcript_path": transcript_path,
            "meeting_id": meeting_id,
            "meeting_type": "external"
        },
        "output_requirements": {
            "blocks": ["notes", "follow_up", "key_quotes", "deliverables"],
            "output_dir": f"/home/workspace/Personal/Meetings/{meeting_id}"
        },
        "status": "pending",
        "priority": 5,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "note": "Recreated by fix_stuck_meetings.py"
    }
    
    request_file = AI_REQUEST_QUEUE / f"{request_id}.json"
    request_file.write_text(json.dumps(request, indent=2))
    
    return request_id


def main():
    logger.info("Finding stuck meetings...")
    
    stuck_meetings = find_stuck_meetings()
    
    if not stuck_meetings:
        logger.info("✓ No stuck meetings found")
        return 0
    
    logger.info(f"Found {len(stuck_meetings)} stuck meeting(s)")
    
    for meeting_id, transcript_path, detected_at in stuck_meetings:
        logger.info(f"\nProcessing: {meeting_id}")
        logger.info(f"  Transcript: {transcript_path}")
        logger.info(f"  Detected: {detected_at}")
        
        # Check if pending request already exists
        pending_requests = list(AI_REQUEST_QUEUE.glob(f"meeting_{meeting_id}_*.json"))
        
        if pending_requests:
            logger.info(f"  ✓ Pending request exists: {pending_requests[0].name}")
            continue
        
        # Check if completed request exists (including in processed subdirectory)
        completed_requests = []
        for existing_file in AI_REQUEST_QUEUE.glob(f"meeting_{meeting_id}_*.json"):
            try:
                with open(existing_file) as f:
                    existing = json.load(f)
                if existing.get("status") == "completed":
                    completed_requests.append(existing_file)
            except:
                pass
        
        processed_dir = AI_REQUEST_QUEUE / "processed"
        if processed_dir.exists():
            for existing_file in processed_dir.glob(f"meeting_{meeting_id}_*.json"):
                try:
                    with open(existing_file) as f:
                        existing = json.load(f)
                    if existing.get("status") == "completed":
                        completed_requests.append(existing_file)
                except:
                    pass
        
        if completed_requests:
            logger.info(f"  ⏭  Already completed ({len(completed_requests)} request(s))")
            continue
        
        # Recreate the AI request
        request_id = recreate_ai_request(meeting_id, transcript_path)
        logger.info(f"  ✓ Created AI request: {request_id}")
    
    logger.info(f"\n✓ Fixed {len(stuck_meetings)} stuck meeting(s)")
    logger.info(f"Run the AI request queue processor to complete these meetings")
    
    return 0


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
