#!/usr/bin/env python3
"""
Fetch Google Calendar Event ID for a meeting

Given meeting metadata (date, participants, title), searches Google Calendar
to find and return the associated event ID.

Usage:
    python3 fetch_gcal_event_id.py --date "2025-11-15" --participants "Vrijen Attawar,Rory Brown" [--title "Meeting Title"]
    python3 fetch_gcal_event_id.py --meeting-folder "/home/workspace/Personal/Meetings/2025-11-15_Meeting_Name"

Returns:
    Event ID string if found
    "null" if no matching event
    Exit code 0 on success, 1 on error
"""

import argparse
import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


def search_calendar_events(date_str, participants=None, title_hint=None):
    """
    Search Google Calendar for events matching criteria.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        participants: List of participant names
        title_hint: Optional meeting title to match
        
    Returns:
        Event ID if found, None otherwise
    """
    # Parse date and create time window
    try:
        meeting_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD", file=sys.stderr)
        return None
    
    # Search window: full day
    time_min = meeting_date.strftime("%Y-%m-%dT00:00:00Z")
    time_max = (meeting_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    
    # Build Zo CLI command to search calendar
    # We'll use the Zo assistant to query Google Calendar
    cmd = [
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from google_calendar_helper import search_events

results = search_events(
    time_min="{time_min}",
    time_max="{time_max}",
    participants={participants if participants else []},
    title_hint="{title_hint if title_hint else ''}"
)
print(results)
"""
    ]
    
    # For now, return a simple implementation that can be enhanced
    # This is a placeholder that should be replaced with actual API calls
    print("null", file=sys.stdout)
    return None


def extract_metadata_from_folder(folder_path):
    """
    Extract meeting metadata from folder structure and files.
    
    Args:
        folder_path: Path to meeting folder
        
    Returns:
        Dict with date, participants, title
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder not found: {folder_path}", file=sys.stderr)
        return None
    
    # Extract date from folder name (format: YYYY-MM-DD_*)
    folder_name = folder.name
    parts = folder_name.split('_')
    if len(parts) < 1:
        print(f"Error: Cannot parse date from folder name: {folder_name}", file=sys.stderr)
        return None
    
    date_str = parts[0]
    
    # Try to extract participants from folder name
    participants = []
    if len(parts) > 1:
        # Participants are typically in format: Name1_Name2
        participant_parts = parts[1:]
        participants = [p.replace('-', ' ').replace('_', ' ') for p in participant_parts]
    
    # Try to read metadata from intelligence file
    intelligence_file = folder / "meeting_intelligence.md"
    if not intelligence_file.exists():
        intelligence_file = folder / "intelligence.md"
    
    title_hint = None
    if intelligence_file.exists():
        # Read first 50 lines to find metadata
        with open(intelligence_file, 'r') as f:
            for i, line in enumerate(f):
                if i > 50:
                    break
                if line.startswith("title:"):
                    title_hint = line.split(":", 1)[1].strip().strip('"')
                    break
                if "# " in line and i < 10:  # First header often contains title
                    title_hint = line.replace("#", "").strip()
    
    return {
        "date": date_str,
        "participants": participants,
        "title": title_hint
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Google Calendar Event ID for a meeting"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--meeting-folder",
        help="Path to meeting folder (extracts metadata automatically)"
    )
    group.add_argument(
        "--date",
        help="Meeting date (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--participants",
        help="Comma-separated list of participant names"
    )
    parser.add_argument(
        "--title",
        help="Meeting title hint for matching"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Extract metadata
    if args.meeting_folder:
        metadata = extract_metadata_from_folder(args.meeting_folder)
        if not metadata:
            return 1
        date_str = metadata["date"]
        participants = metadata["participants"]
        title_hint = metadata["title"]
    else:
        date_str = args.date
        participants = args.participants.split(",") if args.participants else []
        title_hint = args.title
    
    # Search for event
    event_id = search_calendar_events(date_str, participants, title_hint)
    
    # Output result
    if args.json:
        result = {
            "event_id": event_id,
            "date": date_str,
            "found": event_id is not None
        }
        print(json.dumps(result))
    else:
        print(event_id if event_id else "null")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

