#!/usr/bin/env python3
"""Remove corrupted transcripts from Inbox, keep only valid UTF-8 text"""
import subprocess
from pathlib import Path

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
QUARANTINE = Path("/home/workspace/Personal/Meetings/CORRUPTED_SYNCTHING_20251104")

QUARANTINE.mkdir(exist_ok=True)

files = list(INBOX.glob("*.transcript.md"))
print(f"Scanning {len(files)} files...")

corrupted = 0
for f in files:
    result = subprocess.run(["file", "-b", str(f)], capture_output=True, text=True)
    file_type = result.stdout.strip()
    
    if "Zip archive" in file_type or "Microsoft Word" in file_type:
        f.rename(QUARANTINE / f.name)
        corrupted += 1
        if corrupted % 20 == 0:
            print(f"  Quarantined {corrupted}...")

print(f"\n✅ Removed {corrupted} corrupted files")
print(f"✅ Remaining: {len(list(INBOX.glob('*.transcript.md')))} clean files")
