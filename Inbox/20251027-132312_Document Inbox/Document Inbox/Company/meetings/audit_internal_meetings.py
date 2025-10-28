#!/usr/bin/env python3
"""
Audit internal meetings across all subdirectories.
Identifies duplicates, pending requests, and directory purposes.
"""
import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INBOX_ROOT = Path("/home/workspace/N5/inbox/meeting_requests")

def audit_directory_structure():
    """Phase 1: Complete audit of directory structure."""
    
    logger.info("=" * 60)
    logger.info("PHASE 1: AUDIT DIRECTORY STRUCTURE")
    logger.info("=" * 60)
    
    # 1. Document all subdirectories
    subdirs = [d for d in INBOX_ROOT.iterdir() if d.is_dir()]
    logger.info(f"\nFound {len(subdirs)} subdirectories:")
    for subdir in sorted(subdirs):
        files = list(subdir.glob("*.json"))
        logger.info(f"  - {subdir.name:20s}: {len(files):3d} files")
    
    # 2. Collect all meeting requests
    all_requests = {}
    meeting_id_index = defaultdict(list)
    
    for subdir in [INBOX_ROOT] + subdirs:
        for json_file in subdir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                meeting_id = data.get('meeting_id', json_file.stem.replace('_request', ''))
                status = data.get('status', 'unknown')
                classification = data.get('classification', 'unknown')
                
                location = "ROOT" if subdir == INBOX_ROOT else subdir.name
                
                all_requests[str(json_file)] = {
                    'path': str(json_file),
                    'meeting_id': meeting_id,
                    'status': status,
                    'classification': classification,
                    'location': location,
                    'created_at': data.get('created_at', 'unknown'),
                    'mtime': json_file.stat().st_mtime
                }
                
                meeting_id_index[meeting_id].append(str(json_file))
                
            except Exception as e:
                logger.error(f"Error reading {json_file}: {e}")
    
    logger.info(f"\n✓ Loaded {len(all_requests)} meeting requests")
    
    # 3. Find duplicates
    duplicates = {mid: paths for mid, paths in meeting_id_index.items() if len(paths) > 1}
    
    logger.info(f"\n{'='*60}")
    logger.info(f"DUPLICATES FOUND: {len(duplicates)}")
    logger.info(f"{'='*60}")
    
    if duplicates:
        for meeting_id, paths in sorted(duplicates.items()):
            logger.info(f"\n{meeting_id}:")
            for path in paths:
                req = all_requests[path]
                logger.info(f"  - {req['location']:15s} | {req['status']:10s} | {req['created_at']}")
    else:
        logger.info("✓ No duplicates found")
    
    # 4. Analyze internal meetings specifically
    internal_meetings = {
        path: req for path, req in all_requests.items() 
        if 'internal' in req['classification'] or 'internal' in req['meeting_id']
    }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"INTERNAL MEETINGS: {len(internal_meetings)}")
    logger.info(f"{'='*60}")
    
    by_location = defaultdict(list)
    for path, req in internal_meetings.items():
        by_location[req['location']].append(req)
    
    for location in sorted(by_location.keys()):
        reqs = by_location[location]
        logger.info(f"\n{location}/ ({len(reqs)} meetings):")
        for req in sorted(reqs, key=lambda r: r['meeting_id']):
            logger.info(f"  - {req['meeting_id']:50s} [{req['status']}]")
    
    # 5. Identify pending internal meetings
    pending_internal = [
        req for req in internal_meetings.values()
        if req['status'] == 'pending'
    ]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"PENDING INTERNAL MEETINGS: {len(pending_internal)}")
    logger.info(f"{'='*60}")
    
    if pending_internal:
        for req in sorted(pending_internal, key=lambda r: r['meeting_id']):
            logger.info(f"  - {req['meeting_id']:50s} @ {req['location']:15s}")
    else:
        logger.info("✓ No pending internal meetings")
    
    # 6. Document directory purposes
    logger.info(f"\n{'='*60}")
    logger.info("DIRECTORY PURPOSES (INFERRED)")
    logger.info(f"{'='*60}")
    
    purposes = {
        'ROOT': 'Pending requests awaiting processing',
        'internal': 'DEPRECATED - Internal meeting staging (should be in ROOT)',
        'processed': 'Archive - Successfully processed meetings',
        'failed': 'Archive - Processing errors/failures',
        'excluded': 'Archive - Intentionally excluded (test/invalid)',
        'skipped': 'Archive - Did not meet processing criteria',
        'completed': 'Archive - Legacy/unknown status'
    }
    
    for location, purpose in purposes.items():
        count = len([r for r in all_requests.values() if r['location'] == location])
        logger.info(f"\n{location:15s} ({count:3d} files)")
        logger.info(f"  Purpose: {purpose}")
    
    # Save audit results
    audit_file = Path("/home/.z/workspaces/con_vOKoRXQbeElyNYwS/audit_results.json")
    with open(audit_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_requests': len(all_requests),
            'duplicates': {mid: paths for mid, paths in duplicates.items()},
            'pending_internal': [req for req in pending_internal],
            'directory_summary': {loc: len([r for r in all_requests.values() if r['location'] == loc]) 
                                  for loc in purposes.keys()}
        }, f, indent=2)
    
    logger.info(f"\n✓ Audit complete. Results saved to: {audit_file}")
    
    return {
        'all_requests': all_requests,
        'duplicates': duplicates,
        'pending_internal': pending_internal,
        'meeting_id_index': meeting_id_index
    }

if __name__ == "__main__":
    audit_directory_structure()
