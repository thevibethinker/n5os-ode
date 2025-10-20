#!/usr/bin/env python3
import json
from pathlib import Path

processed_file = Path("/home/workspace/Knowledge/market_intelligence/.processed_meetings.json")
meetings_dir = Path("/home/workspace/N5/records/meetings")

# Load processed meetings
processed = set()
if processed_file.exists():
    with open(processed_file) as f:
        processed = set(json.load(f))

# Find all meetings with B31 files
all_meetings = []
for meeting_dir in meetings_dir.iterdir():
    if not meeting_dir.is_dir():
        continue
    if "external" not in meeting_dir.name:
        continue
    b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    if b31.exists():
        all_meetings.append(meeting_dir.name)

# Filter unprocessed, sort by date (most recent first)
unprocessed = [m for m in all_meetings if m not in processed]
unprocessed.sort(reverse=True)

print(f"Total meetings with B31: {len(all_meetings)}")
print(f"Already processed: {len(processed)}")
print(f"Unprocessed: {len(unprocessed)}")
print("\nMost recent 10 unprocessed:")
for i, m in enumerate(unprocessed[:10], 1):
    print(f"{i}. {m}")
