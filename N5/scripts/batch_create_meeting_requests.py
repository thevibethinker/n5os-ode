#!/usr/bin/env python3
"""
Batch create AI requests for all transcripts in Inbox
Run this after bulk import to queue all meetings for processing
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from meeting_pipeline.request_manager import create_or_get_request

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

def main():
    transcripts = list(INBOX.glob("*.transcript.md"))
    print(f"Found {len(transcripts)} transcripts in Inbox")
    
    created = 0
    skipped = 0
    errors = 0
    
    for transcript in transcripts:
        try:
            # Extract meeting_id from filename
            meeting_id = transcript.stem.replace(".transcript", "")
            
            result = create_or_get_request(meeting_id, str(transcript))
            if result.get("created"):
                created += 1
                print(f"✅ Created: {transcript.name}")
            else:
                skipped += 1
                print(f"⏭️  Skipped (exists): {transcript.name}")
        except Exception as e:
            errors += 1
            print(f"❌ Error: {transcript.name} - {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(transcripts)}")
    
    return 0 if errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
