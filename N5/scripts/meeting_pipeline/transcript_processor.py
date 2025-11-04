#!/usr/bin/env python3
"""
Meeting Pipeline - Transcript Processor (Approach B)
Runs as Zo agent with integrated intelligence
"""
import argparse, json, logging, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
REGISTRY_DB = WORKSPACE_ROOT / "N5/data/block_registry.db"
WATCH_DIRS = [
    WORKSPACE_ROOT / "Personal/Meetings/Inbox",
    WORKSPACE_ROOT / "Inbox/Meetings"
]

def scan_for_new_transcripts():
    """Scan watch directories for unprocessed transcripts"""
    logger.info("Scanning for new transcripts...")
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT meeting_id FROM meetings")
    processed = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    new_transcripts = []
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        for tf in watch_dir.glob("**/*.transcript.md"):
            meeting_id = tf.stem.replace('.transcript', '')
            if meeting_id not in processed:
                new_transcripts.append((meeting_id, tf))
                logger.info(f"  Found: {meeting_id}")
    
    logger.info(f"Found {len(new_transcripts)} new transcripts")
    return new_transcripts

def register_meeting(meeting_id, transcript_path):
    """Register new meeting in pipeline database"""
    conn = sqlite3.connect(PIPELINE_DB)
    conn.execute("""
        INSERT INTO meetings (meeting_id, transcript_path, meeting_type, status, detected_at)
        VALUES (?, ?, ?, ?, ?)
    """, (meeting_id, str(transcript_path), "UNKNOWN", "analyzing", 
          datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    logger.info(f"Registered: {meeting_id}")

def main(dry_run=False):
    """
    Main loop - runs AS Zo agent
    Phase 1 (Python): Detect transcripts
    Phase 2 (Zo): Analyze + select blocks
    Phase 3 (Python): Queue blocks
    Phase 4 (Zo): Generate blocks
    Phase 5 (Python): Save + finalize
    """
    logger.info("Meeting Pipeline - Transcript Processor")
    if dry_run:
        logger.info("DRY RUN MODE")
    
    new_transcripts = scan_for_new_transcripts()
    if len(new_transcripts) == 0:
        logger.info("No new transcripts")
        return 0
    
    for meeting_id, transcript_path in new_transcripts:
        logger.info(f"Processing: {meeting_id}")
        if not dry_run:
            register_meeting(meeting_id, transcript_path)
        
        transcript = transcript_path.read_text()
        logger.info(f"  Loaded: {len(transcript)} bytes")
        
        logger.info("PHASE 2: Zo analyzes transcript + selects blocks")
        logger.info("  (Zo loads Meeting_Block_Selector prompt here)")
        logger.info("PHASE 3: Python queues blocks to registry")
        logger.info("PHASE 4: Zo generates each block")
        logger.info("PHASE 5: Python saves + finalizes")
        logger.info(f"Complete: {meeting_id}")
    
    logger.info(f"Processed {len(new_transcripts)} transcripts")
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

def mark_processed(transcript_path):
    """Rename transcript with [IMPORTED-TO-ZO] prefix"""
    if transcript_path.name.startswith('[IMPORTED-TO-ZO]'):
        return  # Already marked
    
    new_name = f"[IMPORTED-TO-ZO] {transcript_path.name}"
    new_path = transcript_path.parent / new_name
    transcript_path.rename(new_path)
    logger.info(f"  Renamed: {new_name}")
