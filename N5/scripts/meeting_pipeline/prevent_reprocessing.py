#!/usr/bin/env python3
"""
Prevent Reprocessing of Completed Meetings
Creates .processed marker file to prevent re-touching completed meetings
"""
from pathlib import Path
import json
from datetime import datetime

MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")

def mark_processed(meeting_dir: Path):
    """Mark meeting as processed to prevent reprocessing"""
    marker = meeting_dir / ".processed"
    
    # Check if has blocks
    blocks = list(meeting_dir.glob("B*.md"))
    if len(blocks) == 0:
        return False
    
    metadata = {
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "blocks_generated": [b.name for b in blocks],
        "block_count": len(blocks)
    }
    
    marker.write_text(json.dumps(metadata, indent=2))
    return True

def is_processed(meeting_dir: Path) -> bool:
    """Check if meeting already processed"""
    marker = meeting_dir / ".processed"
    return marker.exists()

def mark_all_completed():
    """Mark all meetings with B## blocks as processed"""
    marked = 0
    
    for meeting_dir in MEETINGS_ROOT.iterdir():
        if not meeting_dir.is_dir():
            continue
        if meeting_dir.name in ["Inbox", "BACKUP", "CURRENT_BACKUP", "BULK_IMPORT"]:
            continue
        
        # Skip if already marked
        if is_processed(meeting_dir):
            continue
        
        # Mark if has blocks
        if mark_processed(meeting_dir):
            print(f"✓ Marked: {meeting_dir.name}")
            marked += 1
    
    print(f"\n✓ Marked {marked} meetings as processed")

if __name__ == "__main__":
    mark_all_completed()
