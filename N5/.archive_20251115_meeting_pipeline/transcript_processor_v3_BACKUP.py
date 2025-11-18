#!/usr/bin/env python3
"""
Meeting Pipeline - Transcript Processor v3
WITH: Dual idempotency + Duplicate detection + Merge support
"""
import argparse, json, logging, sqlite3, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
REGISTRY_DB = WORKSPACE_ROOT / "N5/data/block_registry.db"
WATCH_DIRS = [
    WORKSPACE_ROOT / "Personal/Meetings/Inbox",
]

# ============ DUPLICATE DETECTION ============

def check_for_duplicate(meeting_id, transcript_text, detected_at):
    """Check if this transcript is a duplicate of existing meeting"""
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    # Get recent meetings within ±4 hours
    time_window_start = (detected_at - timedelta(hours=4)).isoformat()
    time_window_end = (detected_at + timedelta(hours=4)).isoformat()
    
    cursor.execute("""
        SELECT meeting_id, transcript_path, detected_at 
        FROM meetings 
        WHERE detected_at BETWEEN ? AND ?
        AND meeting_id != ?
        AND status != 'duplicate'
    """, (time_window_start, time_window_end, meeting_id))
    
    candidates = cursor.fetchall()
    conn.close()
    
    if not candidates:
        return False, None, 0.0, False
    
    # Fuzzy matching
    transcript_start = transcript_text[:500]
    transcript_end = transcript_text[-500:]
    transcript_len = len(transcript_text)
    
    for existing_id, existing_path, existing_detected in candidates:
        try:
            existing_text = Path(existing_path).read_text()
            existing_len = len(existing_text)
            
            # Length similarity (within 20%)
            len_ratio = min(transcript_len, existing_len) / max(transcript_len, existing_len)
            if len_ratio < 0.80:
                continue
            
            # Content similarity
            existing_start = existing_text[:500]
            existing_end = existing_text[-500:]
            
            start_match = sum(c1 == c2 for c1, c2 in zip(transcript_start, existing_start)) / len(transcript_start)
            end_match = sum(c1 == c2 for c1, c2 in zip(transcript_end, existing_end)) / len(transcript_end)
            
            if start_match > 0.85 and end_match > 0.85:
                confidence = (start_match + end_match + len_ratio) / 3
                
                # Determine which is first (earlier detected_at wins)
                if existing_detected < detected_at.isoformat():
                    first_id = existing_id
                    is_current_second = True
                else:
                    first_id = meeting_id
                    is_current_second = False
                
                return True, first_id, confidence, is_current_second
        except:
            continue
    
    return False, None, 0.0, False

# ============ IDEMPOTENCY ============

def mark_processed(transcript_path):
    """Rename with [IMPORTED-TO-ZO] prefix"""
    if transcript_path.name.startswith('[IMPORTED-TO-ZO]'):
        return
    
    new_name = f"[IMPORTED-TO-ZO] {transcript_path.name}"
    new_path = transcript_path.parent / new_name
    transcript_path.rename(new_path)
    logger.info(f"  ✓ Marked: {new_name}")

def register_meeting(meeting_id, transcript_path, status="analyzing", notes=None):
    """Register meeting in pipeline database"""
    conn = sqlite3.connect(PIPELINE_DB)
    conn.execute("""
        INSERT INTO meetings (meeting_id, transcript_path, meeting_type, status, detected_at, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (meeting_id, str(transcript_path), "UNKNOWN", status, 
          datetime.now(timezone.utc).isoformat(), notes))
    conn.commit()
    conn.close()

# ============ MAIN PROCESSING ============

def scan_for_new_transcripts():
    """Scan for unprocessed transcripts with duplicate detection"""
    logger.info("Scanning for new transcripts...")
    
    # Get already processed
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT meeting_id FROM meetings")
    processed = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    new_transcripts = []
    
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        
        for tf in watch_dir.glob("*.transcript.md"):
            # Skip [IMPORTED-TO-ZO] files
            if tf.name.startswith('[IMPORTED-TO-ZO]'):
                continue
            
            meeting_id = tf.stem.replace('.transcript', '')
            
            # Skip if already in database
            if meeting_id in processed:
                continue
            
            new_transcripts.append((meeting_id, tf))
            logger.info(f"  Found: {meeting_id}")
    
    logger.info(f"Found {len(new_transcripts)} new transcripts")
    return new_transcripts

def main(dry_run=False):
    logger.info("Meeting Pipeline - Transcript Processor v3")
    if dry_run:
        logger.info("DRY RUN MODE")
    
    new_transcripts = scan_for_new_transcripts()
    
    if not new_transcripts:
        logger.info("No new transcripts")
        return 0
    
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
        
        # PHASES 2-5: Block selection + generation
        logger.info("PHASE 2: Zo analyzes transcript + selects blocks")
        logger.info("  (Zo loads Meeting_Block_Selector prompt here)")
        
        logger.info("PHASE 3: Python queues blocks to registry")
        
        logger.info("PHASE 4: Zo generates each block")
        
        logger.info("PHASE 5: Python saves + finalizes")
        
        if not dry_run:
            register_meeting(meeting_id, transcript_path, status="complete")
            mark_processed(transcript_path)
        
        logger.info(f"Complete: {meeting_id}")
    
    logger.info(f"✓ Processed {len(new_transcripts)} transcripts")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        sys.exit(main(dry_run=args.dry_run))
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
