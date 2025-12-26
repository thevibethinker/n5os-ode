#!/usr/bin/env python3
"""
Find Meetings Ready for Follow-Up Email Generation

PURPOSE: Find meetings that have completed intelligence generation but don't yet
have a follow-up email. Uses manifest.json status instead of folder suffix.

This aligns with the manifest-based state machine used by the Weekly Organizer.

PIPELINE POSITION: Runs BEFORE MG-5 (Follow-Up Email Generator)
READY WHEN: status = 'intelligence_generated' or 'mg2_completed'
            AND FOLLOW_UP_EMAIL.md does not exist
            AND not classified as 'no_follow_up_needed'

Usage:
    python3 find_meetings_for_follow_up.py                    # List meetings needing follow-up
    python3 find_meetings_for_follow_up.py --json             # JSON output
    python3 find_meetings_for_follow_up.py --oldest           # Return only oldest meeting
    python3 find_meetings_for_follow_up.py --inbox-only       # Only check Inbox
    python3 find_meetings_for_follow_up.py --include-week-of  # Include Week-of folders (backfill)
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


INBOX_PATH = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")

# Status values that indicate intelligence is complete and ready for follow-up email
READY_FOR_FOLLOWUP_STATUSES = {
    'intelligence_generated',
    'mg2_completed',
}

# Status values that indicate follow-up was explicitly skipped (no email needed)
NO_FOLLOWUP_STATUSES = {
    'no_follow_up_needed',
    'follow_up_skipped',
}


def get_manifest_status(meeting_dir: Path) -> Tuple[str, Dict]:
    """
    Read manifest.json and return (status, full_manifest).
    """
    manifest_path = meeting_dir / "manifest.json"
    if not manifest_path.exists():
        return ('no_manifest', {})
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        status = manifest.get('status', 'unknown')
        return (status, manifest)
    except Exception as e:
        return ('error', {'error': str(e)})


def has_follow_up_email(meeting_dir: Path) -> bool:
    """Check if FOLLOW_UP_EMAIL.md exists."""
    return (meeting_dir / "FOLLOW_UP_EMAIL.md").exists()


def get_meeting_date(folder_name: str) -> Optional[datetime]:
    """Extract date from folder name like 2025-12-22_Meeting-Name."""
    try:
        date_str = folder_name[:10]
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


def is_internal_meeting(meeting_dir: Path, manifest: Dict) -> bool:
    """
    Check if this is an internal meeting (no follow-up email needed).
    Uses manifest.json meeting_type if available.
    """
    meeting_type = manifest.get('meeting_type', '').lower()
    if meeting_type == 'internal':
        return True
    
    # Also check B26 metadata if exists
    b26_path = meeting_dir / "B26_MEETING_METADATA.md"
    if b26_path.exists():
        content = b26_path.read_text().lower()
        if 'internal-only' in content or 'internal meeting' in content:
            return True
    
    return False


def find_meetings_for_follow_up(
    inbox_only: bool = True,
    include_week_of: bool = False,
) -> List[Dict]:
    """
    Find all meetings that need follow-up email generation.
    
    Args:
        inbox_only: Only check Inbox folder
        include_week_of: Also check Week-of folders (for backfill)
    
    Returns:
        List of meeting info dicts sorted by date (oldest first)
    """
    candidates = []
    
    # Scan Inbox
    if INBOX_PATH.exists():
        for item in INBOX_PATH.iterdir():
            if item.is_dir() and not item.name.startswith(('.', '_')):
                candidates.append(item)
    
    # Optionally scan Week-of folders
    if include_week_of and not inbox_only:
        for week_folder in MEETINGS_ROOT.iterdir():
            if week_folder.is_dir() and week_folder.name.startswith('Week-of-'):
                for item in week_folder.iterdir():
                    if item.is_dir() and not item.name.startswith(('.', '_')):
                        candidates.append(item)
    
    results = []
    
    for meeting_dir in candidates:
        status, manifest = get_manifest_status(meeting_dir)
        
        # Skip if no manifest or error
        if status in ('no_manifest', 'error'):
            continue
        
        # Skip if already has follow-up email
        if has_follow_up_email(meeting_dir):
            continue
        
        # Skip if explicitly marked as no follow-up needed
        if status in NO_FOLLOWUP_STATUSES:
            continue
        
        # Skip if not ready (still being processed)
        if status not in READY_FOR_FOLLOWUP_STATUSES:
            continue
        
        # Check if internal meeting (optional - LLM should make final call)
        is_internal = is_internal_meeting(meeting_dir, manifest)
        
        meeting_date = get_meeting_date(meeting_dir.name)
        
        results.append({
            'path': str(meeting_dir),
            'name': meeting_dir.name,
            'status': status,
            'meeting_date': meeting_date.isoformat() if meeting_date else None,
            'is_internal': is_internal,
            'location': 'inbox' if 'Inbox' in str(meeting_dir) else 'week-of',
        })
    
    # Sort by date (oldest first)
    results.sort(key=lambda x: x['meeting_date'] or '9999-99-99')
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Find meetings ready for follow-up email generation"
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--oldest', action='store_true',
        help='Return only the oldest meeting (for MG-5 single-run)'
    )
    parser.add_argument(
        '--inbox-only', action='store_true', default=True,
        help='Only check Inbox folder (default)'
    )
    parser.add_argument(
        '--include-week-of', action='store_true',
        help='Also check Week-of folders (for backfill)'
    )
    
    args = parser.parse_args()
    
    inbox_only = args.inbox_only and not args.include_week_of
    
    meetings = find_meetings_for_follow_up(
        inbox_only=inbox_only,
        include_week_of=args.include_week_of,
    )
    
    if args.oldest:
        if meetings:
            meeting = meetings[0]
            if args.json:
                print(json.dumps(meeting, indent=2))
            else:
                print(meeting['path'])
        else:
            if args.json:
                print(json.dumps(None))
            else:
                print("No meetings found")
            sys.exit(1)
    else:
        if args.json:
            print(json.dumps(meetings, indent=2))
        else:
            print(f"\nMeetings ready for follow-up email ({len(meetings)} found):\n")
            for m in meetings:
                internal_flag = " [INTERNAL]" if m['is_internal'] else ""
                print(f"  {m['meeting_date']} | {m['name']}{internal_flag}")
                print(f"    Status: {m['status']} | Location: {m['location']}")
            
            if not meetings:
                print("  (none)")
            else:
                print(f"\nRun MG-5 to generate follow-up emails for these meetings.")


if __name__ == "__main__":
    main()

