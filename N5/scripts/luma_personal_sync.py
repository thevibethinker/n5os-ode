#!/usr/bin/env python3
"""
Lu.ma Personal Events Sync

Syncs V's personal lu.ma events (invitations, RSVPs, pending) to the calendar database.
This script is designed to be run by a Zo agent that can access lu.ma via browser.

Usage:
    python3 luma_personal_sync.py --check    # Check current personal events (requires browser)
    python3 luma_personal_sync.py --list     # List current personal events in DB
    python3 luma_personal_sync.py --add <json>  # Add/update events from JSON
"""

import argparse
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/luma_events.db")
EXPORT_PATH = Path("/home/workspace/N5/data/luma_candidates.json")

def get_personal_events():
    """List personal events (non-public) from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, url, event_date, event_time, organizers, city, invitation_status
        FROM events 
        WHERE invitation_status != 'public' AND invitation_status IS NOT NULL
        ORDER BY event_date
    """)
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events

def add_or_update_event(event_data: dict):
    """Add or update a personal event"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Check if exists by URL
    cursor.execute("SELECT id FROM events WHERE url = ?", (event_data.get("url", ""),))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE events 
            SET invitation_status = ?, title = ?, event_date = ?, event_time = ?, 
                organizers = ?, city = ?, description = ?
            WHERE id = ?
        """, (
            event_data.get("invitation_status", "invited"),
            event_data.get("title"),
            event_data.get("event_date"),
            event_data.get("event_time"),
            event_data.get("organizers"),
            event_data.get("city"),
            event_data.get("description"),
            existing[0]
        ))
        action = "updated"
    else:
        event_id = f"personal-{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO events (id, url, title, event_date, event_time, organizers, city, description, scraped_at, invitation_status, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (
            event_id,
            event_data.get("url"),
            event_data.get("title"),
            event_data.get("event_date"),
            event_data.get("event_time"),
            event_data.get("organizers"),
            event_data.get("city"),
            event_data.get("description"),
            now,
            event_data.get("invitation_status", "invited"),
        ))
        action = "inserted"
    
    conn.commit()
    conn.close()
    return action

def export_to_calendar():
    """Re-export all events to calendar JSON"""
    import subprocess
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/export_all_events_to_calendar.py"],
        capture_output=True, text=True
    )
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Lu.ma Personal Events Sync")
    parser.add_argument("--list", action="store_true", help="List personal events in DB")
    parser.add_argument("--add", type=str, help="Add event from JSON string")
    parser.add_argument("--check", action="store_true", help="Instructions to check lu.ma")
    parser.add_argument("--export", action="store_true", help="Export to calendar")
    
    args = parser.parse_args()
    
    if args.list:
        events = get_personal_events()
        print(f"Personal events ({len(events)}):")
        print("-" * 60)
        for e in events:
            status_emoji = {"going": "✅", "invited": "📩", "pending": "⏳"}.get(e["invitation_status"], "?")
            print(f"{status_emoji} {e['invitation_status'].upper():8} | {e['event_date']} | {e['title'][:40]}")
        return
    
    if args.add:
        event_data = json.loads(args.add)
        action = add_or_update_event(event_data)
        print(f"{action.capitalize()}: {event_data.get('title')}")
        export_to_calendar()
        return
    
    if args.export:
        result = export_to_calendar()
        print(result)
        return
    
    if args.check:
        print("""
To sync personal lu.ma events:

1. Agent should visit https://lu.ma/home using view_webpage
2. Extract events with status (Going, Invited, Pending)
3. For each event, call:
   python3 luma_personal_sync.py --add '{"title": "...", "url": "...", "event_date": "YYYY-MM-DD", "invitation_status": "going|invited|pending", ...}'

Invitation statuses:
- going: V has RSVPed and is attending
- invited: V received a personal invitation
- pending: V applied, awaiting approval
- public: Discovered via scraper (default)
""")
        return
    
    parser.print_help()

if __name__ == "__main__":
    main()

