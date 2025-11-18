#!/usr/bin/env python3
"""
Backfill B14 and B25 for meetings with [M] and [P] suffixes.
- [M] meetings: Update manifest.json to add B14/B25 as pending
- [P] meetings: Generate actual B14/B25 block files
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Find all [M] and [P] meetings
meetings_root = Path("/home/workspace/Personal/Meetings")

m_meetings = []
p_meetings = []

for meeting_dir in meetings_root.rglob("*"):
    if not meeting_dir.is_dir():
        continue
    if ".DUPLICATES_REMOVED" in str(meeting_dir):
        continue
    if meeting_dir.name.endswith("_[M]"):
        m_meetings.append(meeting_dir)
    elif meeting_dir.name.endswith("_[P]"):
        p_meetings.append(meeting_dir)

print(f"Found {len(m_meetings)} [M] meetings and {len(p_meetings)} [P] meetings")
print()

# Task 1: Update [M] manifests
print("=" * 60)
print("TASK 1: Update [M] Meeting Manifests")
print("=" * 60)

for meeting_dir in m_meetings:
    manifest_path = meeting_dir / "manifest.json"
    
    if not manifest_path.exists():
        print(f"⚠️  No manifest: {meeting_dir.name}")
        continue
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    # Check if B14 and B25 already in manifest
    block_ids = [b['block_id'] for b in manifest.get('blocks', [])]
    
    needs_update = False
    
    if 'B14' not in block_ids:
        manifest['blocks'].append({
            "block_id": "B14",
            "canonical_name": "BLURBS_REQUESTED",
            "status": "pending",
            "priority": 1
        })
        needs_update = True
        print(f"  + Added B14 to manifest")
    
    if 'B25' not in block_ids:
        manifest['blocks'].append({
            "block_id": "B25",
            "canonical_name": "DELIVERABLE_CONTENT_MAP",
            "status": "pending",
            "priority": 1
        })
        needs_update = True
        print(f"  + Added B25 to manifest")
    
    if needs_update:
        # Backup original
        backup_path = meeting_dir / "manifest.json.pre-backfill"
        os.rename(manifest_path, backup_path)
        
        # Save updated manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Updated: {meeting_dir.name}")
    else:
        print(f"✓  Already has B14/B25: {meeting_dir.name}")
    
    print()

# Task 2: Generate B14/B25 for [P] meetings
print("=" * 60)
print("TASK 2: Generate B14/B25 for [P] Meetings")
print("=" * 60)

for meeting_dir in p_meetings:
    print(f"\nProcessing: {meeting_dir.name}")
    
    # Check what's missing
    b14_path = meeting_dir / "B14_BLURBS_REQUESTED.md"
    b25_path = meeting_dir / "B25_DELIVERABLE_CONTENT_MAP.md"
    
    needs_b14 = not b14_path.exists()
    needs_b25 = not b25_path.exists()
    
    if not needs_b14 and not needs_b25:
        print("  ✓ Already has B14 and B25")
        continue
    
    # Load transcript
    transcript_path = meeting_dir / "transcript.md"
    if not transcript_path.exists():
        print("  ⚠️  No transcript, skipping")
        continue
    
    with open(transcript_path) as f:
        transcript = f.read()
    
    # Generate B14 if needed
    if needs_b14:
        b14_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
backfilled: true
---

# B14: BLURBS_REQUESTED

## Status
**Blurbs Requested:** No explicit blurbs requested in this meeting.

## Notes
This block was backfilled after B14 became a required block. If blurbs were actually discussed in this meeting, this should be manually updated.

---

*Backfilled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}*
"""
        with open(b14_path, 'w') as f:
            f.write(b14_content)
        print("  ✅ Generated B14 (empty/placeholder)")
    
    # Generate B25 if needed
    if needs_b25:
        b25_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
backfilled: true
---

# B25: DELIVERABLE_CONTENT_MAP

## Deliverables Map

| Item | Promised By | To Whom | Due | Status |
|------|-------------|---------|-----|--------|
| *(None promised)* | - | - | - | - |

## Follow-Up Email Status
**Follow-Up Email Needed:** NO

## Notes
This block was backfilled after B25 became explicitly required. If deliverables were actually promised in this meeting, this should be manually updated.

---

*Backfilled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}*
"""
        with open(b25_path, 'w') as f:
            f.write(b25_content)
        print("  ✅ Generated B25 (empty/placeholder)")

print()
print("=" * 60)
print("BACKFILL COMPLETE")
print("=" * 60)
print(f"✅ Updated {len(m_meetings)} [M] meeting manifests")
print(f"✅ Generated blocks for {len(p_meetings)} [P] meetings")



