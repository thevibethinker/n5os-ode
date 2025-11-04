#!/usr/bin/env python3
"""
Mark all meetings WITH B31 files but NOT in gtm_processing_registry as unprocessed.
This adds them to the registry with insights_extracted=0 so they appear in the queue.
"""

import sqlite3
from pathlib import Path

DB_PATH = "/home/workspace/Knowledge/market_intelligence/gtm_intelligence.db"
MEETINGS_PATH = Path("/home/workspace/Personal/Meetings")

# Find all meetings WITH B31 files
meetings_with_b31 = []
for b31_file in sorted(MEETINGS_PATH.glob("*/B31_*.md")):
    meeting_id = b31_file.parent.name
    meetings_with_b31.append((meeting_id, str(b31_file)))

print(f"Found {len(meetings_with_b31)} meetings with B31 files")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get already registered meetings
cursor.execute("SELECT meeting_id FROM gtm_processing_registry")
registered = set(row[0] for row in cursor.fetchall())

print(f"Already registered: {len(registered)}")

# Mark unprocessed meetings
added = 0
for meeting_id, b31_path in meetings_with_b31:
    if meeting_id not in registered:
        cursor.execute("""
            INSERT INTO gtm_processing_registry 
            (meeting_id, b31_path, insights_extracted, extraction_version)
            VALUES (?, ?, 0, 'marked_unprocessed')
        """, (meeting_id, b31_path))
        added += 1

conn.commit()
conn.close()

print(f"\n✓ Added {added} meetings to registry as unprocessed")
print(f"✓ Total meetings now in registry: {len(registered) + added}")
print("\nThese meetings are now marked for processing with insights_extracted=0")
