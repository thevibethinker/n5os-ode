#!/usr/bin/env python3
"""
Luma Calendar Integration - Checks Google Calendar for conflicts and tracks bookings.

Usage:
    python3 N5/scripts/luma_calendar.py --check-conflicts
    python3 N5/scripts/luma_calendar.py --events-this-week
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
CONFIG_PATH = N5_ROOT / "config" / "luma_scoring.json"


def load_config() -> dict:
    """Load scoring configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


async def get_calendar_events(start_date: str, end_date: str, email: str = "attawar.v@gmail.com") -> list[dict]:
    """
    Fetch calendar events from Google Calendar.
    
    This is a placeholder that returns the structure we'd get from the Pipedream integration.
    In the scheduled task, we'll use use_app_google_calendar directly.
    """
    # This function will be called via Zo's tool system
    # For now, return empty to allow testing
    logger.info(f"Would fetch calendar events from {start_date} to {end_date}")
    return []


def count_events_in_week(week_start: datetime) -> dict:
    """Count approved/registered events in a given week."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    week_end = week_start + timedelta(days=7)
    
    cursor.execute("""
        SELECT COUNT(*) FROM events 
        WHERE (approved_at IS NOT NULL OR registered_at IS NOT NULL)
        AND event_datetime >= ?
        AND event_datetime < ?
    """, (week_start.isoformat(), week_end.isoformat()))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "event_count": count
    }


def get_week_availability(config: dict = None) -> dict:
    """Check how many more events can be booked this week and next."""
    if config is None:
        config = load_config()
    
    booking_rules = config.get("booking_rules", {})
    max_per_week = booking_rules.get("max_events_per_week", 3)
    target_per_week = booking_rules.get("target_events_per_week", 2)
    
    now = datetime.now(timezone.utc)
    
    # This week (Monday to Sunday)
    days_since_monday = now.weekday()
    this_week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    next_week_start = this_week_start + timedelta(days=7)
    week_after_start = this_week_start + timedelta(days=14)
    
    this_week = count_events_in_week(this_week_start)
    next_week = count_events_in_week(next_week_start)
    week_after = count_events_in_week(week_after_start)
    
    return {
        "this_week": {
            **this_week,
            "slots_available": max(0, max_per_week - this_week["event_count"]),
            "at_target": this_week["event_count"] >= target_per_week
        },
        "next_week": {
            **next_week,
            "slots_available": max(0, max_per_week - next_week["event_count"]),
            "at_target": next_week["event_count"] >= target_per_week
        },
        "week_after": {
            **week_after,
            "slots_available": max(0, max_per_week - week_after["event_count"]),
            "at_target": week_after["event_count"] >= target_per_week
        },
        "config": {
            "max_per_week": max_per_week,
            "target_per_week": target_per_week
        }
    }


def check_time_conflict(event_datetime: str, calendar_events: list[dict], buffer_minutes: int = 60) -> dict:
    """
    Check if an event time conflicts with existing calendar events.
    
    Args:
        event_datetime: ISO datetime string of the Luma event
        calendar_events: List of Google Calendar events
        buffer_minutes: Buffer time before/after events
        
    Returns:
        {has_conflict: bool, conflicting_event: dict or None}
    """
    try:
        ev_dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
    except:
        return {"has_conflict": False, "conflicting_event": None, "error": "Invalid datetime"}
    
    buffer = timedelta(minutes=buffer_minutes)
    
    for cal_event in calendar_events:
        try:
            cal_start = datetime.fromisoformat(cal_event.get("start", "").replace("Z", "+00:00"))
            cal_end = datetime.fromisoformat(cal_event.get("end", "").replace("Z", "+00:00"))
            
            # Check overlap with buffer
            if (ev_dt >= cal_start - buffer) and (ev_dt <= cal_end + buffer):
                return {
                    "has_conflict": True,
                    "conflicting_event": cal_event
                }
        except:
            continue
    
    return {"has_conflict": False, "conflicting_event": None}


def filter_by_availability(events: list[dict], availability: dict) -> list[dict]:
    """
    Filter events based on weekly availability.
    
    Prioritizes:
    1. Primary booking window (2-3 weeks out) if slots available
    2. Opportunistic window (this week) if under target
    """
    config = load_config()
    booking_rules = config.get("booking_rules", {})
    
    primary_min = booking_rules.get("primary_window_days", {}).get("min", 14)
    primary_max = booking_rules.get("primary_window_days", {}).get("max", 21)
    opp_min = booking_rules.get("opportunistic_window_days", {}).get("min", 1)
    opp_max = booking_rules.get("opportunistic_window_days", {}).get("max", 7)
    
    now = datetime.now(timezone.utc)
    
    primary_candidates = []
    opportunistic_candidates = []
    other_candidates = []
    
    for event in events:
        try:
            ev_dt = datetime.fromisoformat(event["event_datetime"].replace("Z", "+00:00"))
            days_until = (ev_dt - now).days
            
            if primary_min <= days_until <= primary_max:
                primary_candidates.append(event)
            elif opp_min <= days_until <= opp_max:
                opportunistic_candidates.append(event)
            else:
                other_candidates.append(event)
        except:
            other_candidates.append(event)
    
    result = []
    
    # Add primary candidates if we have slots in those weeks
    if availability["next_week"]["slots_available"] > 0 or availability["week_after"]["slots_available"] > 0:
        result.extend(primary_candidates)
    
    # Add 1 opportunistic if under target this week
    if not availability["this_week"]["at_target"] and opportunistic_candidates:
        result.append(opportunistic_candidates[0])
    
    return result


def mark_event_approved(event_id: str) -> dict:
    """Mark an event as approved for registration."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE events 
        SET approved_at = ?
        WHERE id = ?
    """, (datetime.now(timezone.utc).isoformat(), event_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"event_id": event_id, "approved": affected > 0}


def mark_event_rejected(event_id: str, reason: str = None) -> dict:
    """Mark an event as rejected."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE events 
        SET rejected_at = ?, score_rationale = COALESCE(score_rationale, '[]') || ?
        WHERE id = ?
    """, (datetime.now(timezone.utc).isoformat(), json.dumps([f"Rejected: {reason}"]) if reason else "[]", event_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"event_id": event_id, "rejected": affected > 0}


def mark_event_registered(event_id: str, gcal_event_id: str = None) -> dict:
    """Mark an event as successfully registered."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE events 
        SET registered_at = ?, registration_status = 'confirmed', gcal_event_id = ?
        WHERE id = ?
    """, (datetime.now(timezone.utc).isoformat(), gcal_event_id, event_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"event_id": event_id, "registered": affected > 0}


def get_approved_pending_registration() -> list[dict]:
    """Get events that are approved but not yet registered."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM events 
        WHERE approved_at IS NOT NULL 
        AND registered_at IS NULL
        AND event_datetime >= datetime('now')
        ORDER BY event_datetime ASC
    """)
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return events


async def main():
    parser = argparse.ArgumentParser(description="Luma calendar integration")
    parser.add_argument("--check-availability", action="store_true", help="Check weekly availability")
    parser.add_argument("--pending-registration", action="store_true", help="List events pending registration")
    args = parser.parse_args()
    
    if args.check_availability:
        availability = get_week_availability()
        print(json.dumps(availability, indent=2))
        
    elif args.pending_registration:
        events = get_approved_pending_registration()
        print(f"Events pending registration: {len(events)}")
        for ev in events:
            print(f"  - {ev['title'][:50]} ({ev['event_date']})")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

