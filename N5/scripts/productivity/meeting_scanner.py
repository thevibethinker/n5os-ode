#!/usr/bin/env python3
"""
Meeting Scanner - Google Calendar Expected Load Tracker
Scans Google Calendar and stores meeting time consumption to calculate True RPI
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")
TIMEZONE = "America/New_York"

def fetch_calendar_events(start: datetime, end: datetime) -> List[dict]:
    """Fetch events from Google Calendar using Zo app integration."""
    logger.info(f"Note: This script requires Google Calendar integration via Zo.")
    logger.info(f"Fetching events from {start.date()} to {end.date()}")
    
    # Format times for Google Calendar API (RFC3339 with timezone)
    time_min = start.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S-05:00")
    time_max = end.replace(hour=23, minute=59, second=59, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S-05:00")
    
    logger.info(f"API Query: timeMin={time_min}, timeMax={time_max}")
    logger.info("This script must be called by Zo agent with google_calendar app access")
    logger.info("Returning empty list - integrate with use_app_google_calendar in production")
    
    return []

def parse_datetime(dt_str: str, is_all_day: bool = False) -> datetime:
    """Parse datetime from Google Calendar API response."""
    if is_all_day:
        # All-day events are in format YYYY-MM-DD
        return datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        # Timed events are RFC3339 format
        # Handle both Z and timezone offset formats
        if dt_str.endswith('Z'):
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            return datetime.fromisoformat(dt_str)

def calculate_duration(start_str: str, end_str: str, is_all_day: bool = False) -> float:
    """Calculate event duration in hours, rounded to 0.25 hour increments."""
    start = parse_datetime(start_str, is_all_day)
    end = parse_datetime(end_str, is_all_day)
    
    duration_seconds = (end - start).total_seconds()
    duration_hours = duration_seconds / 3600
    
    # Cap all-day events at 4 hours
    if is_all_day:
        duration_hours = min(duration_hours, 4.0)
    
    # Cap single meetings at 4 hours
    duration_hours = min(duration_hours, 4.0)
    
    # Round to nearest 0.25 hours (15 min increments)
    rounded = round(duration_hours * 4) / 4
    
    return max(rounded, 0.25)  # Minimum 15 minutes

def is_declined_or_cancelled(event: dict) -> bool:
    """Check if event should be excluded from load calculation."""
    
    # Check if event is cancelled
    if event.get('status') == 'cancelled':
        return True
    
    # Check if user declined the invitation
    attendees = event.get('attendees', [])
    for attendee in attendees:
        if attendee.get('self', False):  # This is the user
            response_status = attendee.get('responseStatus', 'accepted')
            if response_status == 'declined':
                return True
    
    return False

def extract_date(event: dict) -> str:
    """Extract date string YYYY-MM-DD from event."""
    start = event.get('start', {})
    
    # Check for all-day event first
    if 'date' in start:
        return start['date']
    
    # Otherwise parse from dateTime
    dt_str = start.get('dateTime', '')
    if dt_str:
        dt = parse_datetime(dt_str)
        return dt.strftime("%Y-%m-%d")
    
    raise ValueError(f"Could not extract date from event: {event.get('id', 'unknown')}")

def extract_metadata(event: dict) -> dict:
    """Extract relevant metadata from event for JSON storage."""
    attendees = event.get('attendees', [])
    
    return {
        'event_id': event.get('id'),
        'summary': event.get('summary', 'No title'),
        'attendees': len(attendees),
        'organizer': event.get('organizer', {}).get('email'),
        'location': event.get('location'),
        'recurring': event.get('recurringEventId') is not None,
        'status': event.get('status'),
        'visibility': event.get('visibility', 'default')
    }

def process_events(events: List[dict]) -> Dict[str, Tuple[float, List[dict]]]:
    """Process events into daily time consumption with metadata.
    
    Returns:
        Dict mapping date strings to (total_hours, list of event metadata)
    """
    daily_load = {}
    
    for event in events:
        # Skip declined/cancelled
        if is_declined_or_cancelled(event):
            logger.debug(f"Skipping declined/cancelled: {event.get('summary', 'No title')}")
            continue
        
        # Get event timing
        start = event.get('start', {})
        end = event.get('end', {})
        
        is_all_day = 'date' in start  # All-day events have 'date' not 'dateTime'
        
        start_str = start.get('date') if is_all_day else start.get('dateTime')
        end_str = end.get('date') if is_all_day else end.get('dateTime')
        
        if not start_str or not end_str:
            logger.warning(f"Missing start/end time for event: {event.get('id')}")
            continue
        
        # Calculate duration
        try:
            duration_hours = calculate_duration(start_str, end_str, is_all_day)
        except Exception as e:
            logger.warning(f"Error calculating duration for {event.get('summary')}: {e}")
            continue
        
        # Get date
        try:
            event_date = extract_date(event)
        except Exception as e:
            logger.warning(f"Error extracting date: {e}")
            continue
        
        # Get metadata
        metadata = extract_metadata(event)
        
        # Aggregate
        if event_date not in daily_load:
            daily_load[event_date] = (0.0, [])
        
        current_hours, current_events = daily_load[event_date]
        daily_load[event_date] = (current_hours + duration_hours, current_events + [metadata])
        
        logger.info(f"  {event_date}: {metadata['summary']} ({duration_hours:.2f}h)")
    
    return daily_load

def store_expected_load(daily_load: Dict[str, Tuple[float, List[dict]]], dry_run: bool = False) -> int:
    """Store daily load to database.
    
    Returns number of records stored.
    """
    if dry_run:
        logger.info("[DRY RUN] Would store to database:")
        for date_str, (hours, events) in sorted(daily_load.items()):
            logger.info(f"[DRY RUN]   {date_str}: {hours:.2f}h across {len(events)} events")
        return len(daily_load)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    records_stored = 0
    
    for date_str, (hours, events) in daily_load.items():
        metadata = {
            'scanned_at': datetime.now(timezone.utc).isoformat(),
            'events': events
        }
        
        try:
            # Delete existing calendar entries for this date first
            cursor.execute(
                "DELETE FROM expected_load WHERE date = ? AND source = 'calendar'",
                (date_str,)
            )
            
            # Insert new record
            cursor.execute("""
                INSERT INTO expected_load (date, source, type, hours, title, metadata)
                VALUES (?, 'calendar', 'meeting', ?, ?, ?)
            """, (date_str, hours, f"Daily meeting load ({len(events)} events)", json.dumps(metadata)))
            
            records_stored += 1
            logger.info(f"✓ Stored {date_str}: {hours:.2f}h ({len(events)} events)")
            
        except Exception as e:
            logger.error(f"Error storing {date_str}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    conn.close()
    
    return records_stored

def verify_database_state() -> bool:
    """Verify expected_load table exists and has data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expected_load'")
        if not cursor.fetchone():
            logger.error("Table 'expected_load' does not exist")
            return False
        
        # Check recent records
        cursor.execute("SELECT COUNT(*) FROM expected_load WHERE source='calendar'")
        count = cursor.fetchone()[0]
        
        logger.info(f"✓ Database verification: {count} calendar load records found")
        
        # Show sample
        cursor.execute("""
            SELECT date, hours, title 
            FROM expected_load 
            WHERE source='calendar'
            ORDER BY date DESC 
            LIMIT 5
        """)
        
        logger.info("Recent records:")
        for row in cursor.fetchall():
            logger.info(f"  {row[0]}: {row[1]:.2f}h - {row[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

def main(date: Optional[str] = None, start_date: Optional[str] = None, 
         end_date: Optional[str] = None, dry_run: bool = False) -> int:
    """Scan Google Calendar and store expected load."""
    try:
        # Date validation
        if date:
            start = end = datetime.strptime(date, "%Y-%m-%d")
        elif start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            # Default: scan last 7 days
            end = datetime.now()
            start = end - timedelta(days=7)
        
        logger.info(f"=== Meeting Scanner ===")
        logger.info(f"Scanning: {start.date()} to {end.date()}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        
        # Fetch events from Google Calendar
        events = fetch_calendar_events(start, end)
        
        if not events:
            logger.warning("No events returned from Google Calendar")
            logger.warning("NOTE: This script requires Zo agent execution with google_calendar app")
            logger.warning("Run this via Zo chat to enable Google Calendar integration")
            
            if not dry_run:
                # Still verify database state
                logger.info("\n=== Database Verification ===")
                verify_database_state()
            
            return 0
        
        logger.info(f"Found {len(events)} events")
        
        # Process events
        logger.info("\n=== Processing Events ===")
        daily_load = process_events(events)
        
        if not daily_load:
            logger.info("No processable events found (all declined/cancelled)")
            return 0
        
        # Store to database
        logger.info(f"\n=== Storing to Database ===")
        records = store_expected_load(daily_load, dry_run)
        
        # Summary
        total_hours = sum(hours for hours, _ in daily_load.values())
        total_events = sum(len(events) for _, events in daily_load.values())
        
        logger.info(f"\n=== Summary ===")
        logger.info(f"✓ Processed {len(daily_load)} days")
        logger.info(f"✓ {total_events} meetings tracked")
        logger.info(f"✓ {total_hours:.2f} total hours of load")
        logger.info(f"✓ {records} database records {'would be ' if dry_run else ''}stored")
        
        if not dry_run:
            logger.info("\n=== Database Verification ===")
            if not verify_database_state():
                logger.error("Database verification failed")
                return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan Google Calendar for expected load (meetings, blocked time)"
    )
    parser.add_argument("--date", help="Single date YYYY-MM-DD")
    parser.add_argument("--start", dest="start_date", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", dest="end_date", help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    
    args = parser.parse_args()
    exit(main(date=args.date, start_date=args.start_date, end_date=args.end_date, dry_run=args.dry_run))
