#!/usr/bin/env python3
"""
Elevate Existing Auto-Generated Stakeholder Profiles

ARCHITECTURE:
- Python: Find profiles, locate meetings, read B08/B01 files, write output
- LLM: Read content, understand, synthesize, generate rich profiles

This script collects data and prepares it for LLM processing.
"""

import json
import re
from pathlib import Path
from datetime import datetime

STAKEHOLDERS_DIR = Path('/home/workspace/N5/stakeholders')
MEETINGS_DIR = Path('/home/workspace/Personal/Meetings')


def find_auto_gen_profiles():
    """Find all auto-generated profiles that need elevation (MECHANICS)"""
    profiles = []
    
    for profile_path in STAKEHOLDERS_DIR.glob('*.md'):
        content = profile_path.read_text()
        
        if 'Auto-generated stakeholder profile from calendar meeting detection' in content:
            # Extract basic info
            email_match = re.search(r'\*\*Email\*\*:\s*(\S+@\S+)', content)
            name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            
            profiles.append({
                'profile_path': str(profile_path),
                'name': name_match.group(1) if name_match else 'Unknown',
                'email': email_match.group(1) if email_match else None,
                'filename': profile_path.name
            })
    
    return profiles


def find_meetings_for_stakeholder(name, email):
    """Find all meetings with B08 blocks for this stakeholder (MECHANICS)"""
    meetings = []
    
    for b08_file in MEETINGS_DIR.rglob('B08*.md'):
        try:
            b08_content = b08_file.read_text()
            meeting_dir = b08_file.parent
            
            # Check if this B08 mentions the person
            match = False
            if email and email.lower() in b08_content.lower():
                match = True
            elif name and name in b08_content:
                match = True
            
            if match:
                # Extract meeting date from directory name
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', meeting_dir.name)
                meeting_date = date_match.group(1) if date_match else None
                
                # Try to find B01 detailed recap
                b01_candidates = list(meeting_dir.glob('B01*.md'))
                b01_content = None
                if b01_candidates:
                    try:
                        b01_content = b01_candidates[0].read_text()
                    except:
                        pass
                
                meetings.append({
                    'meeting_dir': meeting_dir.name,
                    'meeting_date': meeting_date,
                    'b08_path': str(b08_file),
                    'b08_content': b08_content,
                    'b01_content': b01_content,
                    'b01_path': str(b01_candidates[0]) if b01_candidates else None
                })
        except:
            pass
    
    # Sort by date
    meetings.sort(key=lambda m: m['meeting_date'] or '0000-00-00', reverse=True)
    return meetings


def prepare_elevation_batch():
    """Prepare data for LLM to process (MECHANICS)"""
    profiles = find_auto_gen_profiles()
    
    print(f"📋 Found {len(profiles)} auto-generated profiles to elevate\n")
    
    batch = []
    for profile in profiles:
        meetings = find_meetings_for_stakeholder(profile['name'], profile['email'])
        
        if meetings:
            print(f"✅ {profile['name']:30} → {len(meetings)} meeting(s) with B08 data")
            batch.append({
                'profile': profile,
                'meetings': meetings,
                'has_data': True
            })
        else:
            print(f"⚠️  {profile['name']:30} → No B08 data found (calendar-only)")
            batch.append({
                'profile': profile,
                'meetings': [],
                'has_data': False
            })
    
    return batch


def save_elevation_data(batch, output_path='/home/.z/workspaces/con_IL7RpeK6jyf43uV9/elevation_batch.json'):
    """Save batch data for LLM processing (MECHANICS)"""
    # Strip large content for JSON serialization
    serializable = []
    for item in batch:
        serializable.append({
            'profile': item['profile'],
            'has_data': item['has_data'],
            'meeting_count': len(item['meetings']),
            'meetings': [
                {
                    'meeting_dir': m['meeting_dir'],
                    'meeting_date': m['meeting_date'],
                    'b08_path': m['b08_path'],
                    'b01_path': m['b01_path']
                }
                for m in item['meetings']
            ]
        })
    
    Path(output_path).write_text(json.dumps(serializable, indent=2))
    print(f"\n💾 Saved elevation data to: {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("STAKEHOLDER PROFILE ELEVATION - DATA COLLECTION")
    print("=" * 60)
    print()
    
    batch = prepare_elevation_batch()
    
    print()
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Total profiles: {len(batch)}")
    print(f"   With B08 data: {sum(1 for b in batch if b['has_data'])}")
    print(f"   Calendar-only: {sum(1 for b in batch if not b['has_data'])}")
    print("=" * 60)
    
    save_elevation_data(batch)
    
    print()
    print("✨ Ready for LLM processing")
    print("   LLM will read B08/B01 content and generate elevated profiles")

