#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from pathlib import Path
from meeting_pipeline.request_manager import create_or_get_request

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

transcripts = list(INBOX.glob("*.transcript.md"))
print(f"Found {len(transcripts)} transcripts")

created = 0
skipped = 0

for t in transcripts:
    mid = t.stem.replace(".transcript", "")
    out = f"/home/workspace/Personal/Meetings/{mid}"
    
    r = create_or_get_request(mid, str(t), "external", out, "Bulk 2025-11-04")
    
    if r.get("created"):
        created += 1
        if created % 20 == 0:
            print(f"  {created}...")
    else:
        skipped += 1

print(f"\n✅ Created: {created}")
print(f"⏭️  Skipped: {skipped}")
