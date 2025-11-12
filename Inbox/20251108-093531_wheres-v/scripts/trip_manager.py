#!/usr/bin/env python3
"""
Trip Manager - CRUD operations for trips
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
TRIPS_FILE = DATA_DIR / "trips.jsonl"
ACTIVE_TRIP_FILE = DATA_DIR / "active_trip.json"

def ensure_data_dir():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(exist_ok=True)
    if not TRIPS_FILE.exists():
        TRIPS_FILE.touch()

def create_trip(trip_data: dict) -> str:
    """Create a new trip"""
    ensure_data_dir()
    
    # Generate trip ID
    trip_id = f"trip-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    trip_data["trip_id"] = trip_id
    trip_data["created"] = datetime.now().isoformat()
    trip_data["status"] = "active"
    
    # Append to trips.jsonl
    with open(TRIPS_FILE, "a") as f:
        f.write(json.dumps(trip_data) + "\n")
    
    # Set as active trip
    with open(ACTIVE_TRIP_FILE, "w") as f:
        json.dump({"trip_id": trip_id}, f)
    
    return trip_id

def get_active_trip() -> Optional[dict]:
    """Get the currently active trip"""
    ensure_data_dir()
    
    if not ACTIVE_TRIP_FILE.exists():
        return None
    
    with open(ACTIVE_TRIP_FILE) as f:
        active = json.load(f)
    
    trip_id = active.get("trip_id")
    if not trip_id:
        return None
    
    # Find trip in trips.jsonl
    with open(TRIPS_FILE) as f:
        for line in f:
            trip = json.loads(line.strip())
            if trip.get("trip_id") == trip_id:
                return trip
    
    return None

def update_trip(trip_id: str, updates: dict) -> bool:
    """Update a trip"""
    ensure_data_dir()
    
    trips = []
    found = False
    
    # Read all trips
    with open(TRIPS_FILE) as f:
        for line in f:
            trip = json.loads(line.strip())
            if trip.get("trip_id") == trip_id:
                trip.update(updates)
                found = True
            trips.append(trip)
    
    if not found:
        return False
    
    # Rewrite file
    with open(TRIPS_FILE, "w") as f:
        for trip in trips:
            f.write(json.dumps(trip) + "\n")
    
    return True

def list_trips() -> list[dict]:
    """List all trips"""
    ensure_data_dir()
    
    trips = []
    with open(TRIPS_FILE) as f:
        for line in f:
            trip = json.loads(line.strip())
            trips.append(trip)
    
    return trips

if __name__ == "__main__":
    # Test
    test_trip = {
        "outbound": {
            "flight_number": "DL1234",
            "airline": "Delta",
            "departure": {"airport": "EWR", "time": "2025-11-10T08:00:00Z", "city": "Newark"},
            "arrival": {"airport": "SFO", "time": "2025-11-10T14:00:00Z", "city": "San Francisco"}
        },
        "return": {
            "flight_number": "DL5678",
            "airline": "Delta",
            "departure": {"airport": "SFO", "time": "2025-11-15T18:00:00Z", "city": "San Francisco"},
            "arrival": {"airport": "EWR", "time": "2025-11-16T02:00:00Z", "city": "Newark"}
        }
    }
    trip_id = create_trip(test_trip)
    print(f"Created trip: {trip_id}")
    print(f"Active trip: {json.dumps(get_active_trip(), indent=2)}")
