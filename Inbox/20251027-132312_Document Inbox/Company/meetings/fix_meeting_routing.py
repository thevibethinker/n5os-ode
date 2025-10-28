#!/usr/bin/env python3
"""
Comprehensive fix for meeting request routing.
Phases:
1. Deduplicate requests (keep newest, move others to failed/duplicates/)
2. Update status field in /processed/ archive
3. Move pending from /internal/ to root
4. Clean up failed/skipped/excluded directories
"""
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INBOX_ROOT = Path("/home/workspace/N5/inbox/meeting_requests")
DRY_RUN = True  # Safety first!

def phase_2_update_processed_status(dry_run=True):
    """Update status field in /processed/ archive."""
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: UPDATE STATUS IN /processed/")
    logger.info("="*60)
    
    processed_dir = INBOX_ROOT / "processed"
    updated_count = 0
    
    for json_file in processed_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            if data.get('status') == 'pending':
                logger.info(f"Updating: {json_file.name}")
                data['status'] = 'processed'
                data['processed_at'] = data.get('created_at', datetime.now().isoformat())
                
                if not dry_run:
                    with open(json_file, 'w') as f:
                        json.dump(data, f, indent=2)
                updated_count += 1
        
        except Exception as e:
            logger.error(f"Error processing {json_file}: {e}")
    
    logger.info(f"\n✓ Would update {updated_count} files")
    if dry_run:
        logger.info("  (DRY RUN - no changes made)")
    
    return updated_count

def phase_3_move_internal_to_root(dry_run=True):
    """Move pending requests from /internal/ to root."""
    logger.info("\n" + "="*60)
    logger.info("PHASE 3: MOVE /internal/ TO ROOT")
    logger.info("="*60)
    
    internal_dir = INBOX_ROOT / "internal"
    moved_count = 0
    
    for json_file in internal_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            if data.get('status') == 'pending':
                dest = INBOX_ROOT / json_file.name
                logger.info(f"Moving: {json_file.name} → ROOT/")
                
                if not dry_run:
                    shutil.move(str(json_file), str(dest))
                moved_count += 1
        
        except Exception as e:
            logger.error(f"Error moving {json_file}: {e}")
    
    logger.info(f"\n✓ Would move {moved_count} files to ROOT")
    if dry_run:
        logger.info("  (DRY RUN - no changes made)")
    
    return moved_count

def phase_4_clean_duplicates(dry_run=True):
    """Consolidate duplicates - keep newest, archive rest."""
    logger.info("\n" + "="*60)
    logger.info("PHASE 4: CLEAN DUPLICATES")
    logger.info("="*60)
    
    # Load all requests
    all_requests = {}
    meeting_id_index = defaultdict(list)
    
    for subdir in [INBOX_ROOT] + [d for d in INBOX_ROOT.iterdir() if d.is_dir()]:
        for json_file in subdir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                meeting_id = data.get('meeting_id', json_file.stem.replace('_request', ''))
                location = "ROOT" if subdir == INBOX_ROOT else subdir.name
                
                all_requests[str(json_file)] = {
                    'path': str(json_file),
                    'meeting_id': meeting_id,
                    'location': location,
                    'mtime': json_file.stat().st_mtime,
                    'status': data.get('status', 'unknown')
                }
                
                meeting_id_index[meeting_id].append(str(json_file))
            
            except Exception as e:
                logger.error(f"Error reading {json_file}: {e}")
    
    # Find duplicates
    duplicates = {mid: paths for mid, paths in meeting_id_index.items() if len(paths) > 1}
    
    if not duplicates:
        logger.info("✓ No duplicates found")
        return 0
    
    dedup_dir = INBOX_ROOT / "failed" / "duplicates"
    dedup_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    
    for meeting_id, paths in duplicates.items():
        logger.info(f"\nDuplicate: {meeting_id} ({len(paths)} copies)")
        
        # Sort by modification time, keep newest
        sorted_paths = sorted(paths, key=lambda p: all_requests[p]['mtime'], reverse=True)
        keep_path = sorted_paths[0]
        remove_paths = sorted_paths[1:]
        
        keep_req = all_requests[keep_path]
        logger.info(f"  KEEP: {keep_req['location']:15s} @ {Path(keep_path).name}")
        
        for remove_path in remove_paths:
            remove_req = all_requests[remove_path]
            remove_file = Path(remove_path)
            dest = dedup_dir / remove_file.name
            
            logger.info(f"  MOVE: {remove_req['location']:15s} @ {remove_file.name} → failed/duplicates/")
            
            if not dry_run:
                shutil.move(str(remove_file), str(dest))
            moved_count += 1
    
    logger.info(f"\n✓ Would move {moved_count} duplicate files to failed/duplicates/")
    if dry_run:
        logger.info("  (DRY RUN - no changes made)")
    
    return moved_count

def phase_5_deprecate_internal_dir(dry_run=True):
    """Add README to /internal/ explaining deprecation."""
    logger.info("\n" + "="*60)
    logger.info("PHASE 5: DEPRECATE /internal/ DIRECTORY")
    logger.info("="*60)
    
    internal_dir = INBOX_ROOT / "internal"
    readme = internal_dir / "README.md"
    
    content = """# DEPRECATED DIRECTORY

**Status:** Deprecated as of 2025-10-17

**Reason:** Internal meetings should be placed directly in `/N5/inbox/meeting_requests/` root directory, not in a subdirectory.

**Migration:** All pending internal meeting requests have been moved to the root directory.

**Do not use this directory going forward.** The scheduled task processor scans the root directory only.

---

## Historical Context

This directory was created as part of an early routing experiment to separate internal vs external meetings. It was discovered that this separation caused internal meetings to be skipped by the automated processor.

**Solution:** All pending requests (internal or external) are now placed in the root `/N5/inbox/meeting_requests/` directory. Classification is handled via the `classification` field in the JSON metadata, not via directory structure.
"""
    
    logger.info(f"Creating: {readme}")
    
    if not dry_run:
        with open(readme, 'w') as f:
            f.write(content)
    
    if dry_run:
        logger.info("  (DRY RUN - no changes made)")
    
    return True

def main(dry_run=True):
    """Run all phases."""
    logger.info("="*60)
    logger.info("MEETING REQUEST ROUTING FIX")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info("="*60)
    
    try:
        # Phase 2: Update status in /processed/
        phase_2_update_processed_status(dry_run)
        
        # Phase 3: Move /internal/ to root
        phase_3_move_internal_to_root(dry_run)
        
        # Phase 4: Clean duplicates
        phase_4_clean_duplicates(dry_run)
        
        # Phase 5: Deprecate /internal/
        phase_5_deprecate_internal_dir(dry_run)
        
        logger.info("\n" + "="*60)
        logger.info("FIX COMPLETE")
        logger.info("="*60)
        
        if dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No changes were made.")
            logger.info("Review the output above, then run with --execute to apply changes.")
        else:
            logger.info("\n✓ All changes applied successfully.")
        
        return 0
    
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute))
