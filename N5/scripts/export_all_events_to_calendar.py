#!/usr/bin/env python3
"""
Export ALL future events from luma_events.db to luma_candidates.json.

The calendar site reads from luma_candidates.json.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/luma_events.db")
CANDIDATES_FILE = Path("/home/workspace/N5/data/luma_candidates.json")

def export_all_events():
    """Export all future events from database to JSON for calendar site."""
    if not DB_PATH.exists():
        print("Database not found")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get future events only (with valid dates)
    cursor = conn.execute("""
        SELECT * FROM events 
        WHERE event_date >= ?
        ORDER BY event_date ASC
    """, (today,))
    
    events = []
    for row in cursor:
        event = dict(row)
        events.append({
            "id": event.get("id"),
            "url": event.get("url"),
            "title": event.get("title"),
            "description": event.get("description", ""),
            "event_date": event.get("event_date"),
            "event_time": event.get("event_time"),
            "venue_name": event.get("venue_name", ""),
            "venue_address": event.get("venue_address", ""),
            "location": event.get("location", ""),
            "organizer_name": event.get("organizer_name", ""),
            "organizers": event.get("organizers", ""),
            "city": event.get("city", "nyc"),
            "price": event.get("price", ""),
            "attendee_count": event.get("attendee_count", 0),
            "cover_image_url": event.get("cover_image_url", ""),
            "source": "luma",
            "invitation_status": event.get("invitation_status", "public")  # going, invited, pending, public
        })
    
    conn.close()
    
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(events, f, indent=2)
    
    print(f"Exported {len(events)} future events to {CANDIDATES_FILE}")
    return len(events)

if __name__ == "__main__":
    export_all_events()

