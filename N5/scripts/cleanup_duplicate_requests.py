#!/usr/bin/env python3
"""
Clean up AI requests for meetings that already have folders (already processed)
Keep only requests for new transcripts without folders
"""
import json
from pathlib import Path

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REQUESTS_DIR = Path("/home/workspace/N5/inbox/ai_requests")
BACKUP_DIR = REQUESTS_DIR / "ALREADY_PROCESSED_20251104"

def main():
    # Get all existing meeting folders
    meeting_folders = set()
    for item in MEETINGS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            meeting_folders.add(item.name)
    
    print(f"Found {len(meeting_folders)} existing meeting folders")
    
    # Check all AI requests
    requests = list(REQUESTS_DIR.glob("meeting_*.json"))
    print(f"Found {len(requests)} AI requests")
    
    to_remove = []
    to_keep = []
    
    for req_file in requests:
        try:
            with open(req_file) as f:
                data = json.load(f)
            
            meeting_id = data.get("inputs", {}).get("meeting_id")
            if not meeting_id:
                continue
            
            # Check if folder exists
            if meeting_id in meeting_folders:
                to_remove.append((req_file, meeting_id))
            else:
                to_keep.append((req_file, meeting_id))
        except Exception as e:
            print(f"Error reading {req_file}: {e}")
    
    print(f"\n📊 Analysis:")
    print(f"  ✅ Keep: {len(to_keep)} (no folder yet)")
    print(f"  🗑️  Remove: {len(to_remove)} (folder exists)")
    
    if to_remove:
        BACKUP_DIR.mkdir(exist_ok=True)
        for req_file, meeting_id in to_remove:
            dest = BACKUP_DIR / req_file.name
            req_file.rename(dest)
        print(f"\n✅ Moved {len(to_remove)} duplicate requests to {BACKUP_DIR}")
    
    print(f"\n📊 Final state: {len(to_keep)} AI requests remaining")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
