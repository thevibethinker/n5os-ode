#!/usr/bin/env python3
"""
Meeting Merge Tool v2
Convention: Second (later) meeting merges into first (earlier)
Second meeting's blocks get "_2" suffix
"""
import argparse, sqlite3, logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
REGISTRY_DB = WORKSPACE_ROOT / "N5/data/block_registry.db"

def determine_merge_order(meeting1_id, meeting2_id):
    """
    Determine which is first/second based on detected_at timestamp
    Returns: (first_id, second_id)
    """
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT meeting_id, detected_at FROM meetings 
        WHERE meeting_id IN (?, ?)
        ORDER BY detected_at ASC
    """, (meeting1_id, meeting2_id))
    
    results = cursor.fetchall()
    conn.close()
    
    if len(results) != 2:
        raise ValueError(f"Both meetings must exist. Found: {len(results)}")
    
    return results[0][0], results[1][0]

def merge_meetings(meeting1_id, meeting2_id, dry_run=False):
    """
    Auto-merge: second (later) meeting → first (earlier) meeting
    Second meeting's blocks get "_2" suffix
    """
    # Determine order automatically
    first_id, second_id = determine_merge_order(meeting1_id, meeting2_id)
    
    logger.info(f"Auto-detected merge order:")
    logger.info(f"  First:  {first_id} (target)")
    logger.info(f"  Second: {second_id} (will merge with '_2' suffix)")
    
    if dry_run:
        logger.info("DRY RUN MODE")
    
    # Get second meeting's blocks
    registry_conn = sqlite3.connect(REGISTRY_DB)
    reg_cursor = registry_conn.cursor()
    
    reg_cursor.execute("""
        SELECT block_id, meeting_id, block_type, status, priority, 
               queued_at, generated_at, content, file_path, size_bytes,
               generation_duration_seconds, validation_issues
        FROM blocks WHERE meeting_id = ?
    """, (second_id,))
    
    second_blocks = reg_cursor.fetchall()
    logger.info(f"Found {len(second_blocks)} blocks in second meeting")
    
    if not dry_run and len(second_blocks) > 0:
        # Copy blocks with "_2" suffix
        for block in second_blocks:
            block_id, meeting_id, block_type, *rest = block
            
            # New block_id: first_meeting_blocktype_2
            # e.g., "2025-10-27_meeting_B01_2"
            new_block_id = f"{first_id}_{block_type}_2"
            
            reg_cursor.execute("""
                INSERT OR REPLACE INTO blocks 
                (block_id, meeting_id, block_type, status, priority,
                 queued_at, generated_at, content, file_path, size_bytes,
                 generation_duration_seconds, validation_issues)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_block_id, first_id, block_type) + tuple(rest))
            
            logger.info(f"  Copied: {block_type} → {new_block_id}")
        
        registry_conn.commit()
        logger.info(f"✓ Merged {len(second_blocks)} blocks into first meeting")
    
    # Update meeting statuses
    if not dry_run:
        pipeline_conn = sqlite3.connect(PIPELINE_DB)
        cursor = pipeline_conn.cursor()
        
        # Mark second as merged
        cursor.execute("""
            UPDATE meetings 
            SET status = 'merged',
                notes = 'Merged into: ' || ? || ' (as _2 blocks)'
            WHERE meeting_id = ?
        """, (first_id, second_id))
        
        # Update first with merge note
        cursor.execute("""
            UPDATE meetings
            SET notes = COALESCE(notes || '\n', '') || 'Merged from: ' || ? || ' (_2 suffix)'
            WHERE meeting_id = ?
        """, (second_id, first_id))
        
        pipeline_conn.commit()
        pipeline_conn.close()
        
        logger.info(f"✓ Updated meeting statuses")
    
    registry_conn.close()
    
    logger.info(f"✓ Merge complete: {second_id} → {first_id}")
    logger.info(f"  Second meeting's blocks now have '_2' suffix")
    logger.info(f"  Both transcript files preserved")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge two meetings (auto-detects first/second by timestamp)"
    )
    parser.add_argument("meeting1", help="First meeting ID")
    parser.add_argument("meeting2", help="Second meeting ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview merge")
    
    args = parser.parse_args()
    
    try:
        exit(merge_meetings(args.meeting1, args.meeting2, args.dry_run))
    except Exception as e:
        logging.error(f"Error: {e}")
        exit(1)
