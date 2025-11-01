#!/usr/bin/env python3
"""
Meeting Merge Tool
Manually combine two meetings into one (post-processing)
"""
import argparse, sqlite3, logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
REGISTRY_DB = WORKSPACE_ROOT / "N5/data/block_registry.db"

def merge_meetings(source_id, target_id, dry_run=False):
    """
    Merge source meeting into target
    - Copies all blocks from source → target
    - Marks source as merged
    - Preserves both transcripts as references
    """
    logger.info(f"Merging: {source_id} → {target_id}")
    
    if dry_run:
        logger.info("DRY RUN MODE")
    
    # Step 1: Verify both meetings exist
    pipeline_conn = sqlite3.connect(PIPELINE_DB)
    cursor = pipeline_conn.cursor()
    
    cursor.execute("SELECT meeting_id, status FROM meetings WHERE meeting_id IN (?, ?)", 
                   (source_id, target_id))
    meetings = cursor.fetchall()
    
    if len(meetings) != 2:
        logger.error(f"❌ Both meetings must exist. Found: {len(meetings)}")
        return 1
    
    logger.info(f"✓ Both meetings found in database")
    
    # Step 2: Copy blocks from source → target in block_registry
    registry_conn = sqlite3.connect(REGISTRY_DB)
    reg_cursor = registry_conn.cursor()
    
    reg_cursor.execute("SELECT * FROM blocks WHERE meeting_id = ?", (source_id,))
    source_blocks = reg_cursor.fetchall()
    
    logger.info(f"  Found {len(source_blocks)} blocks in source meeting")
    
    if not dry_run:
        for block in source_blocks:
            # Update meeting_id to target, keep other fields
            new_block_id = block[0].replace(source_id, target_id)
            reg_cursor.execute("""
                INSERT OR REPLACE INTO blocks 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_block_id, target_id) + block[2:])
        
        registry_conn.commit()
        logger.info(f"  ✓ Copied {len(source_blocks)} blocks to target")
    
    # Step 3: Mark source meeting as merged
    if not dry_run:
        cursor.execute("""
            UPDATE meetings 
            SET status = 'merged',
                notes = 'Merged into: ' || ?
            WHERE meeting_id = ?
        """, (target_id, source_id))
        
        pipeline_conn.commit()
        logger.info(f"  ✓ Marked source as merged")
    
    # Step 4: Add merge metadata to target
    if not dry_run:
        cursor.execute("""
            UPDATE meetings
            SET notes = COALESCE(notes || '\n', '') || 'Merged from: ' || ?
            WHERE meeting_id = ?
        """, (source_id, target_id))
        
        pipeline_conn.commit()
        logger.info(f"  ✓ Updated target metadata")
    
    pipeline_conn.close()
    registry_conn.close()
    
    logger.info(f"✓ Merge complete: {source_id} → {target_id}")
    logger.info("  Both transcript files preserved on filesystem")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge two meetings")
    parser.add_argument("--source", required=True, help="Source meeting ID (will be merged into target)")
    parser.add_argument("--target", required=True, help="Target meeting ID (receives blocks from source)")
    parser.add_argument("--dry-run", action="store_true", help="Preview merge without executing")
    
    args = parser.parse_args()
    exit(merge_meetings(args.source, args.target, args.dry_run))
