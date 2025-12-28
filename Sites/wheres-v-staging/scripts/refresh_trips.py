#!/usr/bin/env python3
"""
Where's V - Trip Refresh Script

This script:
1. Pulls travel events from Google Calendar
2. Uses LLM to extract V's trips (filtering out family trips)
3. Updates trip data store
4. Manages intensive refresh agent lifecycle (spawn/delete)

Called by scheduled agents (weekly or 12-hourly).
"""
import json
import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SITE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from trip_store_v2 import (
    load_trips, get_legs_for_trip, _parse_time
)

# Agent IDs (will be set after creation)
WEEKLY_AGENT_LABEL = "wheres-v-weekly-refresh"
INTENSIVE_AGENT_LABEL = "wheres-v-intensive-refresh"

def get_days_until_next_trip() -> int | None:
    """Get days until next upcoming trip."""
    trips = load_trips()
    now = datetime.now(timezone.utc)
    
    for trip in trips:
        if trip.get("status") == "complete":
            continue
        legs = get_legs_for_trip(trip["id"])
        if not legs:
            continue
        
        first_leg = legs[0]
        dep_str = first_leg.get("flight", {}).get("departure_time")
        if not dep_str:
            continue
            
        try:
            dep_time = _parse_time(dep_str)
            if dep_time > now:
                return (dep_time - now).days
        except (ValueError, TypeError):
            continue
    
    return None


def get_next_trip_end_date() -> datetime | None:
    """Get the end date of the next/current trip."""
    trips = load_trips()
    now = datetime.now(timezone.utc)
    
    for trip in trips:
        if trip.get("status") == "complete":
            continue
        legs = get_legs_for_trip(trip["id"])
        if not legs:
            continue
        
        last_leg = legs[-1]
        arr_str = last_leg.get("flight", {}).get("arrival_time")
        if not arr_str:
            continue
            
        try:
            arr_time = _parse_time(arr_str)
            # Return if this trip hasn't ended yet
            if arr_time > now:
                return arr_time
        except (ValueError, TypeError):
            continue
    
    return None


def check_intensive_agent_needed() -> dict:
    """
    Check if intensive (12h) refresh agent should be spawned or deleted.
    
    Returns:
        dict with 'action': 'spawn' | 'delete' | 'none' and reason
    """
    days_until = get_days_until_next_trip()
    trip_end = get_next_trip_end_date()
    now = datetime.now(timezone.utc)
    
    # If trip has ended, delete intensive agent
    if trip_end and trip_end < now:
        return {
            "action": "delete",
            "reason": f"Trip ended at {trip_end.isoformat()}"
        }
    
    # If within 2 weeks of trip, spawn intensive agent
    if days_until is not None and days_until <= 14:
        return {
            "action": "spawn",
            "reason": f"Trip in {days_until} days - need intensive refresh"
        }
    
    # If no upcoming trips or > 2 weeks out, no intensive needed
    if days_until is None:
        return {
            "action": "delete",
            "reason": "No upcoming trips"
        }
    
    return {
        "action": "none",
        "reason": f"Trip in {days_until} days - weekly refresh sufficient"
    }


def main():
    """Main refresh logic."""
    import argparse
    parser = argparse.ArgumentParser(description="Where's V trip refresh")
    parser.add_argument("--check-agents", action="store_true",
                       help="Check if intensive agent should be spawned/deleted")
    parser.add_argument("--refresh", action="store_true",
                       help="Pull latest trips from Calendar")
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't make changes, just report")
    args = parser.parse_args()
    
    if args.check_agents:
        result = check_intensive_agent_needed()
        print(json.dumps(result, indent=2))
        return
    
    if args.refresh:
        # This would call the Calendar ingestion
        # For now, just report status
        days = get_days_until_next_trip()
        end = get_next_trip_end_date()
        print(json.dumps({
            "days_until_next_trip": days,
            "trip_end_date": end.isoformat() if end else None,
            "agent_recommendation": check_intensive_agent_needed()
        }, indent=2))
        return
    
    # Default: show status
    print("Where's V - Trip Refresh Script")
    print("=" * 40)
    days = get_days_until_next_trip()
    if days is not None:
        print(f"Next trip in: {days} days")
    else:
        print("No upcoming trips")
    
    agent_check = check_intensive_agent_needed()
    print(f"Agent action: {agent_check['action']}")
    print(f"Reason: {agent_check['reason']}")


if __name__ == "__main__":
    main()

