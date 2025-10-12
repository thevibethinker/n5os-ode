#!/usr/bin/env python3
"""
Test script to demonstrate BLUF format for Aniket meeting
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date
import pytz

# Add N5 scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')

from meeting_prep_digest import (
    filter_external_meetings,
    generate_digest,
    extract_tags_from_description,
    get_stakeholder_profile_path
)

# Load mock Aniket meeting
mock_file = Path('/home/.z/workspaces/con_HevtEA7qTz2z9DBL/aniket_meeting_mock.json')
with open(mock_file) as f:
    data = json.load(f)

meetings = data['meetings']

# Filter to external meetings only
external_meetings = filter_external_meetings(meetings)

print(f"\n{'='*60}")
print("ANIKET MEETING DIGEST — DRY RUN (BLUF FORMAT DEMO)")
print(f"{'='*60}\n")

if not external_meetings:
    print("No external meetings found in mock data.\n")
    sys.exit(0)

# Generate digest
target_date = date(2025, 10, 12)
digest_content = generate_digest(external_meetings, target_date)

print(digest_content)

print(f"\n{'='*60}")
print("END DRY RUN — NO FILES SAVED")
print(f"{'='*60}\n")
