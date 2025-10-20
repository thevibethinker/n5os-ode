#!/usr/bin/env python3
"""
N5 Drop Follow-Up Command
Mark a follow-up email as declined to stop receiving reminders.

Usage:
    python3 n5_drop_followup.py <stakeholder-name> [--reason "text"] [--undo]

Examples:
    python3 n5_drop_followup.py "Hamoon Ekhtiari"
    python3 n5_drop_followup.py "Hamoon" --reason "Already followed up via text"
    python3 n5_drop_followup.py "Hamoon" --undo

Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")


def find_meeting_by_stakeholder(stakeholder_name: str) -> Optional[Path]:
    """Find meeting folder by stakeholder name (fuzzy match)."""
    stakeholder_lower = stakeholder_name.lower()
    
    candidates = []
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir():
            continue
        
        metadata_path = meeting_dir / "_metadata.json"
        if not metadata_path.exists():
            continue
        
        with open(metadata_path, 'r') as f:
            metadata = json.loads(f.read())
        
        # Skip if no stakeholder_primary or not external or no follow-up
        if not metadata.get('stakeholder_primary'):
            continue
        if metadata.get('classification') != 'external':
            continue
        if not metadata.get('generated_deliverables'):
            continue
        
        # Check if has follow-up deliverable
        has_followup = any(
            d.get('type') == 'follow_up_email' 
            for d in metadata.get('generated_deliverables', [])
        )
        if not has_followup:
            continue
        
        # Check if stakeholder name matches
        primary = metadata.get('stakeholder_primary', '').lower()
        if stakeholder_lower in primary or primary in stakeholder_lower:
            candidates.append((meeting_dir, metadata))
    
    if not candidates:
        logger.error(f"No meeting found for stakeholder: {stakeholder_name}")
        return None
    
    if len(candidates) > 1:
        logger.warning(f"Multiple meetings found for '{stakeholder_name}':")
        for i, (path, meta) in enumerate(candidates, 1):
            logger.warning(f"  {i}. {meta.get('stakeholder_primary')} ({meta.get('date')})")
        logger.error("Please be more specific or provide the meeting ID")
        return None
    
    return candidates[0][0]


def update_metadata(meeting_dir: Path, updates: dict) -> bool:
    """Update meeting metadata file."""
    metadata_path = meeting_dir / "_metadata.json"
    
    if not metadata_path.exists():
        logger.error(f"Metadata not found: {metadata_path}")
        return False
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.loads(f.read())
        
        metadata.update(updates)
        
        with open(metadata_path, 'w') as f:
            f.write(json.dumps(metadata, indent=2))
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        return False


def drop_followup(stakeholder_name: str, reason: str = "", undo: bool = False) -> int:
    """Mark follow-up as declined (or undo)."""
    
    # Find meeting
    meeting_dir = find_meeting_by_stakeholder(stakeholder_name)
    if not meeting_dir:
        return 1
    
    # Read current metadata
    metadata_path = meeting_dir / "_metadata.json"
    with open(metadata_path, 'r') as f:
        metadata = json.loads(f.read())
    
    stakeholder = metadata.get('stakeholder_primary', 'Unknown')
    meeting_date = metadata.get('date', 'Unknown')
    
    if undo:
        # Remove declined status
        updates = {
            'followup_status': 'pending',
            'followup_status_updated_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        }
        if 'followup_declined_reason' in metadata:
            updates['followup_declined_reason'] = None
        
        if update_metadata(meeting_dir, updates):
            logger.info(f"✓ Follow-up restored for {stakeholder} ({meeting_date})")
            return 0
        return 1
    
    else:
        # Mark as declined
        updates = {
            'followup_status': 'declined',
            'followup_declined_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        }
        if reason:
            updates['followup_declined_reason'] = reason
        
        if update_metadata(meeting_dir, updates):
            logger.info(f"✓ Follow-up declined for {stakeholder} ({meeting_date})")
            if reason:
                logger.info(f"  Reason: {reason}")
            return 0
        return 1


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Drop follow-up email reminder")
    parser.add_argument("stakeholder_name", help="Stakeholder name or meeting identifier")
    parser.add_argument("--reason", default="", help="Optional reason for declining")
    parser.add_argument("--undo", action="store_true", help="Undo decline (restore follow-up)")
    
    args = parser.parse_args()
    
    return drop_followup(args.stakeholder_name, args.reason, args.undo)


if __name__ == "__main__":
    sys.exit(main())
