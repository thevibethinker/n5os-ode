#!/usr/bin/env python3
import json
from pathlib import Path

# Load processed meetings
processed_file = Path("/home/workspace/Knowledge/market_intelligence/.processed_meetings.json")
processed_data = json.loads(processed_file.read_text())
processed_ids = {m['meeting_id'] for m in processed_data['GTM']['meetings']}

# Find all external meetings with B31
meetings_dir = Path("/home/workspace/N5/records/meetings")
all_b31_meetings = []

for meeting_dir in sorted(meetings_dir.glob("2025-*_external-*"), reverse=True):
    b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    if b31.exists():
        all_b31_meetings.append(meeting_dir.name)

# Find unprocessed
unprocessed = [m for m in all_b31_meetings if m not in processed_ids]

print(f"=== GTM AGGREGATION STATUS ===\n")
print(f"Already processed: {len(processed_ids)}")
print(f"Total with B31: {len(all_b31_meetings)}")
print(f"Unprocessed: {len(unprocessed)}\n")

if unprocessed:
    print(f"=== UNPROCESSED MEETINGS WITH B31 (most recent first) ===\n")
    for i, name in enumerate(unprocessed[:15], 1):
        print(f"{i:2}. {name}")
