#!/usr/bin/env python3
import os
from pathlib import Path

MEETINGS_DIR = Path("/home/workspace/Inbox/20251028-132902_Meetings")
ACTIONS_DIR = Path("/home/workspace/N5/inbox/meeting_actions")

# Get all extracted meetings
extracted_meetings = set()
for f in os.listdir(ACTIONS_DIR):
    if f.endswith(".json") and not f.endswith("_email_request.json"):
        # Format: 20251028-132902_Meetings_[meeting_name].json
        if "Meetings_" in f:
            meeting_name = f.split("Meetings_", 1)[1].replace(".json", "")
            # Remove trailing numbers like _175632
            meeting_name = meeting_name.rsplit("_", 1)[0] if meeting_name[-1].isdigit() else meeting_name
            extracted_meetings.add(meeting_name)

print("Extracted meetings:", len(extracted_meetings))

# Find all meetings with Smart Blocks
meetings_with_blocks = []
for dir_name in sorted(os.listdir(MEETINGS_DIR)):
    meeting_dir = MEETINGS_DIR / dir_name
    
    if not meeting_dir.is_dir() or dir_name.startswith("."):
        continue
    
    # Check for Smart Blocks
    has_blocks = (meeting_dir / "B01_DETAILED_RECAP.md").exists() or \
                 (meeting_dir / "B25_DELIVERABLE_CONTENT_MAP.md").exists()
    
    if has_blocks:
        meetings_with_blocks.append(dir_name)
        
        # Check if extracted
        if dir_name not in extracted_meetings:
            print(f"UNPROCESSED: {dir_name}")

print(f"\nTotal meetings with blocks: {len(meetings_with_blocks)}")
print(f"Total extracted: {len(extracted_meetings)}")
print(f"Unprocessed: {len(meetings_with_blocks) - len(extracted_meetings)}")
