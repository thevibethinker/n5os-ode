#!/usr/bin/env python3
"""
Find all meetings in [M] state for MG-5 v2 Follow-Up Email Generation workflow

v2.0 (2026-01-03): Fixed field name bug - uses 'status' instead of 'meeting_state'
"""

import json
import os
from pathlib import Path

# Valid statuses that indicate meeting is in [M] state (not yet processed)
M_STATE_STATUSES = {'manifest_generated', 'intelligence_generated', 'mg2_completed'}

def scan_meetings():
    meetings_dir = Path('/home/workspace/Personal/Meetings')
    m_meetings = []

    # Walk through all subdirectories looking for manifest.json
    for manifest_path in meetings_dir.rglob('manifest.json'):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            # Check if in [M] state - use 'status' field (not 'meeting_state')
            status = manifest.get('status', '')
            if status in M_STATE_STATUSES:
                # Get parent folder to check for other files
                meeting_folder = manifest_path.parent
                
                # Check if it's internal
                meeting_type = manifest.get('meeting_type', '')
                if meeting_type == 'internal':
                    print(f"Skipping internal: {meeting_folder.name}")
                    continue
                
                # Check if already has FOLLOW_UP_EMAIL.md
                follow_up_file = meeting_folder / 'FOLLOW_UP_EMAIL.md'
                if follow_up_file.exists():
                    print(f"Already has follow-up email: {meeting_folder.name}")
                    continue
                
                # Valid candidate found
                m_meetings.append({
                    'folder': str(meeting_folder),
                    'name': meeting_folder.name,
                    'manifest': manifest
                })
                print(f"Found candidate: {meeting_folder.name}")
                
        except Exception as e:
            print(f"Error reading {manifest_path}: {e}")
    
    print(f"\nTotal meetings in [M] state (external, no follow-up): {len(m_meetings)}")
    return m_meetings

if __name__ == "__main__":
    m_meetings = scan_meetings()
    
    if not m_meetings:
        exit(0)
    
    # Save results
    output = {
        'count': len(m_meetings),
        'meetings': m_meetings
    }
    
    with open('/home/.z/workspaces/con_HXwtIFx4qvItSjNO/m_meetings.json', 'w') as f:
        json.dump(output, f, indent=2)
    

