#!/usr/bin/env python3
"""
Newsletter Event Parser - Extracts events from email newsletters and adds to calendar.

This script:
1. Fetches newsletters from Gmail (Supermomos, Beehiiv, Substack, etc.)
2. Extracts event data (title, date, URL, location)
3. Adds events to luma_events.db
4. Exports to luma_candidates.json for the calendar site

Usage:
    python3 newsletter_event_parser.py --days 14
    python3 newsletter_event_parser.py --source supermomos
    python3 newsletter_event_parser.py --dry-run
"""

import argparse
import json
import re
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import subprocess
import sys

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
CANDIDATES_FILE = N5_ROOT / "data" / "luma_candidates.json"

# Newsletter sources configuration
NEWSLETTER_SOURCES = {
    "supermomos": {
        "query": "from:beehiiv supermomos",
        "organizer": "Supermomos",
        "priority": "high"
    },
    "vc_unfiltered": {
        "query": "from:vcunfiltered@mail.beehiiv.com",
        "organizer": "VC Unfiltered", 
        "priority": "medium"
    },
    "fibe": {
        "query": "from:fibe OR fibe.nyc",
        "organizer": "Fibe",
        "priority": "high"
    },
    "substack_founders": {
        "query": "from:substack (founders OR startup OR NYC)",
        "organizer": "Substack",
        "priority": "medium"
    },
    "partiful": {
        "query": "from:partiful",
        "organizer": "Partiful",
        "priority": "high"
    },
    "luma_direct": {
        "query": "from:lu.ma",
        "organizer": "Luma",
        "priority": "high"
    },
    "eventbrite": {
        "query": "from:eventbrite",
        "organizer": "Eventbrite",
        "priority": "medium"
    }
}

# Event URL patterns to extract
EVENT_URL_PATTERNS = [
    r'https?://lu\.ma/[a-zA-Z0-9_-]+',
    r'https?://(?:www\.)?partiful\.com/e/[a-zA-Z0-9_-]+',
    r'https?://(?:www\.)?supermomos\.com/events/[a-zA-Z0-9_-]+',
    r'https?://(?:www\.)?eventbrite\.com/e/[a-zA-Z0-9_-]+',
    r'https?://(?:www\.)?meetup\.com/[^/]+/events/[a-zA-Z0-9_-]+',
]

# Date patterns to extract
DATE_PATTERNS = [
    # "January 15, 2026" or "Jan 15, 2026"
    r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s*(?:20\d{2})?)',
    # "12/15/2025" or "2025-12-15"
    r'(\d{1,2}/\d{1,2}/20\d{2})',
    r'(20\d{2}-\d{2}-\d{2})',
    # "Mon, Dec 8" etc
    r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2})',
]


def extract_urls_from_text(text: str) -> list[str]:
    """Extract event URLs from newsletter text."""
    urls = []
    for pattern in EVENT_URL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(matches)
    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        # Clean URL (remove tracking params)
        clean_url = url.split('?')[0].split('&')[0]
        if clean_url not in seen:
            seen.add(clean_url)
            unique_urls.append(clean_url)
    return unique_urls


def extract_events_from_newsletter(email_content: str, source: str) -> list[dict]:
    """Extract events from a newsletter email content."""
    events = []
    
    # Extract all event URLs
    urls = extract_urls_from_text(email_content)
    
    for url in urls:
        # Try to find context around the URL (title, date)
        event = {
            "url": url,
            "source": source,
            "extracted_at": datetime.now().isoformat()
        }
        
        # Try to extract title from URL or nearby text
        if "lu.ma/" in url:
            slug = url.split("lu.ma/")[-1].split("?")[0]
            event["title"] = slug.replace("-", " ").title()
            event["platform"] = "luma"
        elif "supermomos.com/events/" in url:
            slug = url.split("/events/")[-1].split("?")[0]
            event["title"] = slug.replace("-", " ").title()
            event["platform"] = "supermomos"
        elif "partiful.com/e/" in url:
            event["title"] = "Partiful Event"
            event["platform"] = "partiful"
        elif "eventbrite.com/e/" in url:
            event["title"] = "Eventbrite Event"
            event["platform"] = "eventbrite"
        else:
            event["title"] = "Newsletter Event"
            event["platform"] = "other"
        
        events.append(event)
    
    return events


def add_event_to_db(event: dict, dry_run: bool = False) -> bool:
    """Add an event to the database. Returns True if inserted, False if exists."""
    if dry_run:
        print(f"  [DRY RUN] Would add: {event.get('title', 'Unknown')} - {event.get('url', 'No URL')}")
        return True
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if URL already exists
    cursor.execute("SELECT id FROM events WHERE url = ?", (event["url"],))
    if cursor.fetchone():
        conn.close()
        return False
    
    # Insert new event
    event_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO events (id, url, title, event_date, city, description, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event["url"],
            event.get("title", "Newsletter Event"),
            event.get("event_date", ""),
            event.get("city", "nyc"),
            f"Source: {event.get('source', 'newsletter')} | Platform: {event.get('platform', 'unknown')}",
            now
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"  Error inserting event: {e}")
        conn.close()
        return False


def export_to_calendar():
    """Export future events to the calendar JSON file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get all future events (or events without dates)
    cursor.execute("""
        SELECT * FROM events 
        WHERE event_date >= ? OR event_date = '' OR event_date IS NULL
        ORDER BY event_date ASC
    """, (today,))
    
    rows = cursor.fetchall()
    events = []
    
    for row in rows:
        events.append({
            "id": row["id"],
            "url": row["url"],
            "title": row["title"],
            "event_date": row["event_date"] or "",
            "event_time": row["event_time"] if "event_time" in row.keys() else "",
            "city": row["city"] or "nyc",
            "description": row["description"] or ""
        })
    
    conn.close()
    
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(events, f, indent=2)
    
    return len(events)


def fetch_newsletters_via_zo_ask(source_key: str, days: int = 14) -> list[dict]:
    """
    Use Zo's /zo/ask API to fetch and parse newsletters.
    This leverages LLM intelligence to extract events from complex newsletter formats.
    """
    import os
    import requests
    
    source = NEWSLETTER_SOURCES.get(source_key, {})
    query = source.get("query", "")
    
    prompt = f"""Search Gmail (attawar.v@gmail.com) for newsletters matching: {query}
Look back {days} days.

For each email found, extract ALL events mentioned. For each event, provide:
- title: Event name
- url: Direct link to RSVP/register (lu.ma, partiful, supermomos, eventbrite URLs)
- date: Event date in YYYY-MM-DD format (if mentioned)
- location: City/venue (default to "NYC" if not specified)

Return a JSON array of events. Only include events with valid URLs.
If no events found, return an empty array [].

Example output format:
[
  {{"title": "January Founders Dinner", "url": "https://lu.ma/jan-dinner", "date": "2026-01-15", "location": "NYC"}},
  {{"title": "AI Meetup", "url": "https://partiful.com/e/abc123", "date": "2026-01-20", "location": "NYC"}}
]"""

    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print(f"  Warning: No ZO_CLIENT_IDENTITY_TOKEN, skipping {source_key}")
        return []
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string"},
                            "date": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    }
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            events = result.get("output", [])
            if isinstance(events, list):
                return events
        else:
            print(f"  API error for {source_key}: {response.status_code}")
    except Exception as e:
        print(f"  Error fetching {source_key}: {e}")
    
    return []


def main():
    parser = argparse.ArgumentParser(description="Parse newsletters for events")
    parser.add_argument("--days", type=int, default=14, help="Days to look back")
    parser.add_argument("--source", type=str, help="Specific source to parse")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    parser.add_argument("--export-only", action="store_true", help="Only export to calendar JSON")
    parser.add_argument("--list-sources", action="store_true", help="List available sources")
    args = parser.parse_args()
    
    if args.list_sources:
        print("Available newsletter sources:")
        for key, config in NEWSLETTER_SOURCES.items():
            print(f"  {key}: {config['query']} (priority: {config['priority']})")
        return
    
    if args.export_only:
        count = export_to_calendar()
        print(f"Exported {count} events to calendar")
        return
    
    # Determine which sources to process
    sources = [args.source] if args.source else list(NEWSLETTER_SOURCES.keys())
    
    total_added = 0
    total_found = 0
    
    print(f"Parsing newsletters from last {args.days} days...")
    print(f"Sources: {', '.join(sources)}")
    print("-" * 50)
    
    for source_key in sources:
        if source_key not in NEWSLETTER_SOURCES:
            print(f"Unknown source: {source_key}")
            continue
        
        print(f"\n[{source_key}] Fetching...")
        events = fetch_newsletters_via_zo_ask(source_key, args.days)
        
        print(f"  Found {len(events)} events")
        total_found += len(events)
        
        for event in events:
            # Add source metadata
            event["source"] = source_key
            event["city"] = event.get("location", "nyc")
            event["event_date"] = event.get("date", "")
            
            if add_event_to_db(event, dry_run=args.dry_run):
                total_added += 1
                print(f"  + {event.get('title', 'Unknown')[:50]}")
    
    print("-" * 50)
    print(f"Total: {total_found} events found, {total_added} new events added")
    
    if not args.dry_run and total_added > 0:
        count = export_to_calendar()
        print(f"Exported {count} events to calendar")


if __name__ == "__main__":
    main()

