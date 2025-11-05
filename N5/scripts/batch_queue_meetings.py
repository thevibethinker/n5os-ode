#!/usr/bin/env python3
"""
Batch create AI requests for all transcripts in Inbox
"""
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

from pathlib import Path
from meeting_pipeline.request_manager import create_or_get_request

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

def main():
    transcripts = list(INBOX.glob("*.transcript.md"))
    print(f"Found {len(transcripts)} transcripts")
    
    created = 0
    skipped = 0
    
    for transcript in transcripts:
        meeting_id = transcript.stem.replace(".transcript", "")
        
        # Check if meeting folder exists to determine type
        meeting_folder = Path("/home/workspace/Personal/Meetings") / meeting_id
        if meeting_folder.exists():
            meeting_type = "external"  # Default
        else:
            meeting_type = "external"
        
        output_dir = f"/home/workspace/Personal/Meetings/{meeting_id}"
        
        result = create_or_get_request(
            meeting_id=meeting_id,
            transcript_path=str(transcript),
            meeting_type=meeting_type,
            output_dir=output_dir,
            reason="Bulk import 2025-11-04"
        )
        
        if result.get("created"):
            created += 1
            if created % 10 == 0:
                print(f"  {created} created...")
        else:
            skipped += 1
    
    print(f"\n✅ Created: {created} new requests")
    print(f"⏭️  Skipped: {skipped} (already exist)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
