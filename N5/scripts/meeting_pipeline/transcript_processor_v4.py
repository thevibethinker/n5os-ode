#!/usr/bin/env python3
"""
Meeting Pipeline - Transcript Processor v4
WITH: AI Request Queue Integration

Detects new transcripts, checks for duplicates, and submits AI processing requests.
"""
import sqlite3
import logging
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher

WORKSPACE_ROOT = Path("/home/workspace")
MEETING_INBOX = WORKSPACE_ROOT / "Personal/Meetings/Inbox"
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
AI_REQUEST_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_requests"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def get_processed_transcripts():
    """Get set of already processed transcript filenames."""
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT meeting_id FROM meetings")
    processed = {row[0] for row in cursor.fetchall()}
    conn.close()
    return processed


def scan_for_new_transcripts():
    """Scan inbox for unprocessed transcripts."""
    if not MEETING_INBOX.exists():
        return []
    
    processed = get_processed_transcripts()
    new_transcripts = []
    
    for transcript_path in MEETING_INBOX.glob("*.transcript.md"):
        # Skip [ZO-PROCESSED] files
        if transcript_path.name.startswith("[ZO-PROCESSED]"):
            continue
        
        # Extract meeting_id from filename
        meeting_id = transcript_path.stem.replace(".transcript", "")
        
        if meeting_id not in processed:
            new_transcripts.append((meeting_id, transcript_path))
    
    return new_transcripts


def register_meeting(meeting_id, transcript_path, meeting_type="UNKNOWN", status="detected", notes=None):
    """Register meeting in database."""
    conn = sqlite3.connect(PIPELINE_DB)
    detected_at = datetime.now(timezone.utc).isoformat()
    
    conn.execute("""
        INSERT INTO meetings (meeting_id, transcript_path, meeting_type, status, detected_at, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (meeting_id, str(transcript_path), meeting_type, status, detected_at, notes))
    
    conn.commit()
    conn.close()


def check_for_duplicate(meeting_id, transcript_text, detected_at):
    """Check if this transcript is a duplicate of an existing one."""
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    # Get all existing meetings within 7 days
    cursor.execute("""
        SELECT meeting_id, transcript_path
        FROM meetings
        WHERE status != 'duplicate'
        AND datetime(detected_at) > datetime(?, '-7 days')
    """, (detected_at.isoformat(),))
    
    candidates = cursor.fetchall()
    conn.close()
    
    transcript_len = len(transcript_text)
    threshold = 0.85  # 85% similarity = duplicate
    
    for existing_id, existing_path in candidates:
        if existing_id == meeting_id:
            continue
        
        try:
            existing_text = Path(existing_path).read_text()
            existing_len = len(existing_text)
            
            # Quick length check (within 20%)
            len_ratio = min(transcript_len, existing_len) / max(transcript_len, existing_len)
            if len_ratio < 0.80:
                continue
            
            # Full similarity check
            similarity = SequenceMatcher(None, transcript_text, existing_text).ratio()
            
            if similarity >= threshold:
                # Determine which is first
                is_current_second = meeting_id > existing_id
                first_id = existing_id if is_current_second else meeting_id
                return True, first_id, similarity, is_current_second
        
        except Exception as e:
            logger.warning(f"Error comparing with {existing_id}: {e}")
            continue
    
    return False, None, 0.0, False


def create_ai_request(meeting_id, transcript_path):
    """Create an AI processing request for this meeting."""
    AI_REQUEST_QUEUE.mkdir(parents=True, exist_ok=True)
    
    request_id = f"meeting_{meeting_id}_{int(datetime.now().timestamp())}"
    
    request = {
        "request_id": request_id,
        "request_type": "meeting_process",
        "prompt_name": "Meeting Process",
        "inputs": {
            "transcript_path": str(transcript_path),
            "meeting_id": meeting_id,
            "meeting_type": "external"  # Could be detected more intelligently
        },
        "output_requirements": {
            "blocks": ["notes", "follow_up", "key_quotes", "deliverables"],
            "output_dir": f"/home/workspace/Personal/Meetings/{meeting_id}"
        },
        "status": "pending",
        "priority": 5,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    request_file = AI_REQUEST_QUEUE / f"{request_id}.json"
    request_file.write_text(json.dumps(request, indent=2))
    logger.info(f"  ✓ Created AI request: {request_id}")
    
    return request_id


def mark_processed(transcript_path):
    """Rename transcript to mark as processed."""
    new_name = f"[ZO-PROCESSED] {transcript_path.name}"
    new_path = transcript_path.parent / new_name
    transcript_path.rename(new_path)
    logger.info(f"  ✓ Marked: {new_name}")


def main(dry_run=False):
    logger.info("Meeting Pipeline - Transcript Processor v4")
    if dry_run:
        logger.info("DRY RUN MODE")
    
    new_transcripts = scan_for_new_transcripts()
    
    if not new_transcripts:
        logger.info("No new transcripts")
        return 0
    
    logger.info(f"Found {len(new_transcripts)} new transcript(s)")
    
    for meeting_id, transcript_path in new_transcripts:
        logger.info(f"Processing: {meeting_id}")
        
        # Load transcript
        transcript_text = transcript_path.read_text()
        logger.info(f"  Loaded: {len(transcript_text)} bytes")
        
        # DUPLICATE DETECTION
        detected_at = datetime.now(timezone.utc)
        is_dup, first_id, conf, is_current_second = check_for_duplicate(
            meeting_id, transcript_text, detected_at
        )
        
        if is_dup:
            if is_current_second:
                logger.warning(f"⚠️  DUPLICATE DETECTED: {meeting_id}")
                logger.warning(f"   Original (first): {first_id}")
                logger.warning(f"   Confidence: {conf:.0%}")
                logger.warning(f"   Action: Marking as duplicate, skipping processing")
                
                if not dry_run:
                    register_meeting(
                        meeting_id, 
                        transcript_path, 
                        status="duplicate", 
                        notes=f"Duplicate of {first_id} (detected {conf:.0%} confidence)"
                    )
                    mark_processed(transcript_path)
                
                continue
            else:
                logger.warning(f"⚠️  This is FIRST, duplicate will come later: {first_id}")
        
        # Register in database as "queued_for_ai"
        if not dry_run:
            register_meeting(meeting_id, transcript_path, status="queued_for_ai")
        
        # Create AI processing request
        if not dry_run:
            request_id = create_ai_request(meeting_id, transcript_path)
            logger.info(f"  ✓ Queued for AI: {request_id}")
        
        # DO NOT mark as processed yet - that happens after AI completes
        logger.info(f"  ⏳ Awaiting AI processing")
    
    logger.info(f"✓ Queued {len(new_transcripts)} transcript(s) for AI processing")
    logger.info("Note: Run ai_request_processor.py to process the queue")
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        sys.exit(main(dry_run=args.dry_run))
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
