#!/usr/bin/env python3
"""
Requeue incomplete meetings for reprocessing.
Clears incomplete folders and adds them back to processing queue.
"""
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

import shutil
from pathlib import Path
from meeting_pipeline.request_manager import create_or_get_request

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
INBOX_DIR = MEETINGS_DIR / "Inbox"

def find_incomplete_meetings():
    """Find meetings without B26 or with incomplete processing."""
    incomplete = []
    
    # 1. Check standardized folders (2025-*) for missing B26
    for folder in MEETINGS_DIR.glob("2025-*"):
        if not folder.is_dir():
            continue
        b26 = folder / "B26_metadata.md"
        if not b26.exists():
            incomplete.append({
                "folder": folder,
                "reason": "missing_b26",
                "type": "standardized"
            })
    
    # 2. Check transcript folders (never processed)
    for folder in MEETINGS_DIR.glob("*transcript*"):
        if not folder.is_dir():
            continue
        if folder.name == "Inbox":
            continue
        b26 = folder / "B26_metadata.md"
        if not b26.exists():
            # Find transcript file
            transcript = None
            for ext in [".transcript.md", ".transcript.txt"]:
                t = folder / (folder.name + ext)
                if t.exists():
                    transcript = t
                    break
            
            if transcript:
                incomplete.append({
                    "folder": folder,
                    "transcript": transcript,
                    "reason": "never_processed",
                    "type": "transcript"
                })
    
    # 3. Check unknown folders
    for folder in MEETINGS_DIR.glob("*unknown*"):
        if not folder.is_dir():
            continue
        incomplete.append({
            "folder": folder,
            "reason": "unknown",
            "type": "unknown"
        })
    
    return incomplete

def requeue_meeting(meeting_info):
    """Requeue a meeting for processing."""
    folder = meeting_info["folder"]
    meeting_id = folder.name
    
    # Find transcript
    transcript_path = None
    if meeting_info.get("transcript"):
        transcript_path = str(meeting_info["transcript"])
    else:
        # Try to find transcript in Inbox
        for ext in [".transcript.md", ".transcript.txt"]:
            t = INBOX_DIR / (meeting_id + ext)
            if t.exists():
                transcript_path = str(t)
                break
    
    if not transcript_path:
        print(f"  ⚠️  No transcript found for {meeting_id}")
        return False
    
    # Create request
    output_dir = str(MEETINGS_DIR / meeting_id)
    result = create_or_get_request(
        meeting_id=meeting_id,
        transcript_path=transcript_path,
        meeting_type="external",  # Will be inferred
        output_dir=output_dir,
        reason="Requeue incomplete - cleanup 2025-11-04",
        force_recreate=True
    )
    
    return result.get("created", False)

def main():
    print("Finding incomplete meetings...")
    incomplete = find_incomplete_meetings()
    
    print(f"\nFound {len(incomplete)} incomplete meetings:")
    for m in incomplete:
        print(f"  - {m['folder'].name} ({m['reason']})")
    
    if not incomplete:
        print("\n✅ No incomplete meetings found")
        return
    
    print(f"\n{'='*60}")
    response = input(f"Requeue {len(incomplete)} meetings? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted")
        return
    
    print(f"\n{'='*60}")
    print("Requeuing meetings...")
    
    requeued = 0
    cleared = 0
    
    for meeting_info in incomplete:
        folder = meeting_info["folder"]
        print(f"\n{folder.name}:")
        
        # Requeue first
        if requeue_meeting(meeting_info):
            print(f"  ✅ Requeued")
            requeued += 1
        else:
            print(f"  ⏭️  Already queued")
        
        # Clear folder (delete all B*.md files)
        for b_file in folder.glob("B*.md"):
            b_file.unlink()
            print(f"  🗑️  Deleted {b_file.name}")
            cleared += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Requeued: {requeued} meetings")
    print(f"🗑️  Cleared: {cleared} files")
    print(f"\nMeetings will be reprocessed automatically")

if __name__ == "__main__":
    main()
