#!/usr/bin/env python3
"""
Trip Store for Where's V
Simple JSONL-based storage for flight trips.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).parent.parent / "data" / "trips.jsonl"

def _load_trips() -> list[dict]:
    """Load all trips from JSONL file."""
    if not DATA_FILE.exists():
        return []
    trips = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                trips.append(json.loads(line))
    return trips

def _save_trips(trips: list[dict]) -> None:
    """Save all trips to JSONL file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        for trip in trips:
            f.write(json.dumps(trip) + "\n")

def add_trip(
    flight_number: str,
    departure_airport: str,
    arrival_airport: str,
    departure_time: str,  # ISO format
    arrival_time: str,    # ISO format
    email_id: Optional[str] = None
) -> dict:
    """
    Add a new trip. Returns the created trip.
    
    Args:
        flight_number: e.g., "UA123", "DL456"
        departure_airport: 3-letter code, e.g., "JFK"
        arrival_airport: 3-letter code, e.g., "LAX"
        departure_time: ISO format datetime
        arrival_time: ISO format datetime
        email_id: Gmail message ID (for deduplication)
    """
    trips = _load_trips()
    
    # Check for duplicate by email_id
    if email_id:
        for trip in trips:
            if trip.get("email_id") == email_id:
                return trip  # Already exists
    
    trip = {
        "id": f"trip_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "flight_number": flight_number,
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "email_id": email_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    trips.append(trip)
    _save_trips(trips)
    return trip

def get_active_trip() -> Optional[dict]:
    """
    Get the current or next upcoming trip.
    Returns None if no active trips.
    """
    trips = _load_trips()
    now = datetime.now(timezone.utc)
    
    active_trips = []
    for trip in trips:
        try:
            arrival = datetime.fromisoformat(trip["arrival_time"].replace("Z", "+00:00"))
            # Trip is active if arrival time is in the future
            if arrival > now:
                active_trips.append(trip)
        except (KeyError, ValueError):
            continue
    
    if not active_trips:
        return None
    
    # Sort by departure time, return soonest
    active_trips.sort(key=lambda t: t.get("departure_time", ""))
    return active_trips[0]

def get_status() -> dict:
    """
    Get current status for parent-facing display.
    
    Returns:
        {
            "status": "home" | "departing" | "flying" | "arrived",
            "message": "Human-readable status",
            "flight": {...} or None
        }
    """
    trip = get_active_trip()
    
    if not trip:
        return {
            "status": "home",
            "message": "V is home in NYC",
            "flight": None
        }
    
    now = datetime.now(timezone.utc)
    
    try:
        departure = datetime.fromisoformat(trip["departure_time"].replace("Z", "+00:00"))
        arrival = datetime.fromisoformat(trip["arrival_time"].replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return {
            "status": "home",
            "message": "V is home in NYC",
            "flight": None
        }
    
    hours_until_departure = (departure - now).total_seconds() / 3600
    
    if hours_until_departure > 24:
        return {
            "status": "home",
            "message": f"V is home. Upcoming trip to {trip['arrival_airport']} on {departure.strftime('%b %d')}",
            "flight": trip
        }
    elif hours_until_departure > 0:
        return {
            "status": "departing",
            "message": f"V is heading to the airport. Flight {trip['flight_number']} to {trip['arrival_airport']}",
            "flight": trip
        }
    elif now < arrival:
        return {
            "status": "flying",
            "message": f"V is in the air! Flight {trip['flight_number']} to {trip['arrival_airport']}. Landing ~{arrival.strftime('%I:%M %p')}",
            "flight": trip
        }
    else:
        return {
            "status": "arrived",
            "message": f"V has landed in {trip['arrival_airport']}",
            "flight": trip
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: trip_store.py [status|add]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status = get_status()
        print(json.dumps(status, indent=2))
    elif cmd == "add":
        # Example: trip_store.py add UA123 JFK LAX 2025-01-15T10:00:00Z 2025-01-15T13:00:00Z
        if len(sys.argv) < 7:
            print("Usage: trip_store.py add <flight> <from> <to> <depart_iso> <arrive_iso>")
            sys.exit(1)
        trip = add_trip(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print(json.dumps(trip, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

