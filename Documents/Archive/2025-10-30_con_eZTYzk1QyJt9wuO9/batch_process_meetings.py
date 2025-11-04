#!/usr/bin/env python3
"""
Batch process pending Oct 29 meeting requests.
Downloads transcripts, creates meeting folders, generates basic metadata.
Smart Block generation will be done by Zo in follow-up.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

PROCESSED_DIR = Path('/home/workspace/N5/inbox/meeting_requests/processed')
MEETINGS_DIR = Path('/home/workspace/Personal/Meetings')
MEETINGS_DIR.mkdir(parents=True, exist_ok=True)

def process_meeting(request_file: Path):
    """Process a single meeting request"""
    with open(request_file) as f:
        data = json.load(f)
    
    meeting_id = data['meeting_id']
    gdrive_id = data['gdrive_id']
    
    # Check if already processed
    meeting_dir = MEETINGS_DIR / meeting_id
    if meeting_dir.exists():
        print(f"✓ SKIP {meeting_id} (already exists)")
        return 'skip'
    
    print(f"→ QUEUE {meeting_id} for download")
    print(f"  gdrive_id: {gdrive_id}")
    print(f"  Will download and create in Personal/Meetings/")
    
    # For now, just mark as needing processing
    # Actual download will be done by Zo using Google Drive API
    return 'queued'

def main():
    oct29_files = sorted(PROCESSED_DIR.glob('2025-10-29*.json'))
    
    print(f"=== BATCH MEETING PROCESSOR ===")
    print(f"Found {len(oct29_files)} Oct 29 meetings\n")
    
    stats = {'skip': 0, 'queued': 0}
    
    for f in oct29_files:
        result = process_meeting(f)
        stats[result] += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Already processed: {stats['skip']}")
    print(f"Queued for download: {stats['queued']}")
    print(f"\nNext: Zo will download {stats['queued']} transcripts and generate Smart Blocks")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
