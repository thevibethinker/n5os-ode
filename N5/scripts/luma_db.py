#!/usr/bin/env python3
"""
Database layer for Luma events.
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)
N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"

def init_db():
    """Initialize SQLite database for events."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT,
            event_time TEXT,
            event_datetime TEXT,
            venue_name TEXT,
            venue_address TEXT,
            city TEXT,
            organizers TEXT,
            price TEXT,
            attendee_count INTEGER,
            status TEXT,
            cover_image_url TEXT,
            scraped_at TEXT NOT NULL,
            scored_at TEXT,
            score REAL,
            score_rationale TEXT,
            digest_sent_at TEXT,
            approved_at TEXT,
            rejected_at TEXT,
            registered_at TEXT,
            registration_status TEXT,
            gcal_event_id TEXT,
            raw_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_events(events: list[dict]):
    """Save events to database, updating existing ones."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for ev in events:
        # Check if exists
        cursor.execute("SELECT id FROM events WHERE id = ?", (ev["id"],))
        exists = cursor.fetchone()
        
        # Ensure minimal fields
        ev.setdefault("description", "")
        ev.setdefault("event_date", "")
        ev.setdefault("event_time", "")
        ev.setdefault("event_datetime", "")
        ev.setdefault("venue_name", "")
        ev.setdefault("venue_address", "")
        ev.setdefault("city", "")
        ev.setdefault("organizers", "[]")
        ev.setdefault("price", "Unknown")
        ev.setdefault("attendee_count", 0)
        ev.setdefault("status", "unknown")
        ev.setdefault("cover_image_url", "")
        ev.setdefault("scraped_at", datetime.now(timezone.utc).isoformat())
        ev.setdefault("raw_data", "{}")

        if exists:
            # Update (but preserve approval status)
            cursor.execute("""
                UPDATE events SET
                    title = ?, description = ?, event_date = ?, event_time = ?,
                    event_datetime = ?, venue_name = ?, venue_address = ?,
                    organizers = ?, price = ?, attendee_count = ?, status = ?,
                    cover_image_url = ?, scraped_at = ?, raw_data = ?
                WHERE id = ? AND approved_at IS NULL AND rejected_at IS NULL
            """, (
                ev["title"], ev["description"], ev["event_date"], ev["event_time"],
                ev["event_datetime"], ev["venue_name"], ev["venue_address"],
                ev["organizers"], ev["price"], ev["attendee_count"], ev["status"],
                ev["cover_image_url"], ev["scraped_at"], ev["raw_data"], ev["id"]
            ))
            if cursor.rowcount > 0:
                updated += 1
        else:
            cursor.execute("""
                INSERT INTO events (
                    id, url, title, description, event_date, event_time,
                    event_datetime, venue_name, venue_address, city, organizers,
                    price, attendee_count, status, cover_image_url, scraped_at, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ev["id"], ev["url"], ev["title"], ev["description"],
                ev["event_date"], ev["event_time"], ev["event_datetime"],
                ev["venue_name"], ev["venue_address"], ev["city"], ev["organizers"],
                ev["price"], ev["attendee_count"], ev["status"], ev["cover_image_url"],
                ev["scraped_at"], ev["raw_data"]
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    return {"inserted": inserted, "updated": updated}

