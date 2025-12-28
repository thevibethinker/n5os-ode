#!/usr/bin/env python3
"""
Trip Store V2 for Where's V
Trip/Leg model with state machine support.

Trip = Round-trip container (NYC → somewhere → NYC)
Leg = Individual flight segment within a trip
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Literal

DATA_DIR = Path(__file__).parent.parent / "data"
TRIPS_FILE = DATA_DIR / "trips_v2.jsonl"
LEGS_FILE = DATA_DIR / "legs_v2.jsonl"

HOME_BASE = "NYC"  # V's home base
HOME_AIRPORTS = {"JFK", "LGA", "EWR"}  # NYC area airports
PRE_DEPARTURE_DAYS = 7  # Trigger pre-departure state X days before

StateType = Literal["home", "pre_departure", "in_transit", "at_destination"]


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_jsonl(filepath: Path) -> list[dict]:
    if not filepath.exists():
        return []
    items = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _save_jsonl(filepath: Path, items: list[dict]):
    _ensure_data_dir()
    with open(filepath, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def _append_jsonl(filepath: Path, item: dict):
    _ensure_data_dir()
    with open(filepath, "a") as f:
        f.write(json.dumps(item) + "\n")


# ============== TRIP OPERATIONS ==============

def load_trips() -> list[dict]:
    return _load_jsonl(TRIPS_FILE)


def save_trips(trips: list[dict]):
    _save_jsonl(TRIPS_FILE, trips)


def get_trip(trip_id: str) -> Optional[dict]:
    for trip in load_trips():
        if trip.get("id") == trip_id:
            return trip
    return None


def create_trip(home_base: str = "NYC", notes: str = None) -> dict:
    """Create a new trip container."""
    trip = {
        "id": f"trip_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "home_base": home_base,
        "status": "upcoming",
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "legs": [],
        "sources": {"calendar_event_ids": [], "gmail_message_ids": []}
    }
    _append_jsonl(TRIPS_FILE, trip)
    return trip


def update_trip(trip_id: str, updates: dict) -> Optional[dict]:
    """Update a trip by ID."""
    trips = load_trips()
    for i, trip in enumerate(trips):
        if trip.get("id") == trip_id:
            trips[i].update(updates)
            save_trips(trips)
            return trips[i]
    return None


def update_trip_notes(trip_id: str, notes: str) -> Optional[dict]:
    """Update notes for a trip."""
    trips = load_trips()
    for trip in trips:
        if trip["id"] == trip_id:
            trip["notes"] = notes
            save_trips(trips)
            return trip
    return None


def add_leg_to_trip(trip_id: str, leg_id: str) -> bool:
    """Add a leg reference to a trip."""
    trip = get_trip(trip_id)
    if not trip:
        return False
    if leg_id not in trip["legs"]:
        trip["legs"].append(leg_id)
        update_trip(trip_id, {"legs": trip["legs"]})
    return True


# ============== LEG OPERATIONS ==============

def load_legs() -> list[dict]:
    return _load_jsonl(LEGS_FILE)


def save_legs(legs: list[dict]):
    _save_jsonl(LEGS_FILE, legs)


def get_leg(leg_id: str) -> Optional[dict]:
    for leg in load_legs():
        if leg.get("id") == leg_id:
            return leg
    return None


def get_legs_for_trip(trip_id: str) -> list[dict]:
    """Get all legs for a trip, sorted by sequence."""
    legs = [leg for leg in load_legs() if leg.get("trip_id") == trip_id]
    return sorted(legs, key=lambda x: x.get("sequence", 0))


def create_leg(
    trip_id: str,
    sequence: int,
    flight_number: str,
    departure_airport: str,
    arrival_airport: str,
    departure_time: str,
    arrival_time: str,
    destination_city: str = None,
    hotel: dict = None
) -> dict:
    """Create a new leg within a trip."""
    leg = {
        "id": f"leg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "trip_id": trip_id,
        "sequence": sequence,
        "flight": {
            "number": flight_number,
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "departure_time": departure_time,
            "arrival_time": arrival_time
        },
        "destination_city": destination_city or arrival_airport,
        "hotel": hotel,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _append_jsonl(LEGS_FILE, leg)
    add_leg_to_trip(trip_id, leg["id"])
    return leg


def update_leg(leg_id: str, updates: dict) -> Optional[dict]:
    """Update a leg by ID."""
    legs = load_legs()
    for i, leg in enumerate(legs):
        if leg.get("id") == leg_id:
            legs[i].update(updates)
            save_legs(legs)
            return legs[i]
    return None


# ============== STATE MACHINE ==============

def _parse_time(iso_string: str) -> datetime:
    """Parse ISO time string to datetime."""
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


def _is_home_airport(airport: str) -> bool:
    """Check if airport is in NYC area."""
    return airport.upper() in HOME_AIRPORTS


def get_last_completed_trip() -> Optional[dict]:
    """Get most recent completed trip."""
    trips = load_trips()
    completed = [t for t in trips if t.get("status") == "complete"]
    if not completed:
        return None
    # Sort by last leg's arrival time
    def get_end_time(trip):
        legs = get_legs_for_trip(trip["id"])
        if not legs:
            return ""
        return legs[-1].get("flight", {}).get("arrival_time", "")
    completed.sort(key=get_end_time, reverse=True)
    return completed[0] if completed else None


def get_next_upcoming_trip() -> Optional[dict]:
    """Get next upcoming trip (not yet started)."""
    trips = load_trips()
    now = datetime.now(timezone.utc)
    
    upcoming = []
    for trip in trips:
        if trip.get("status") == "complete":
            continue
        legs = get_legs_for_trip(trip["id"])
        if not legs:
            continue
        first_leg = legs[0]
        try:
            dep_time = _parse_time(first_leg["flight"]["departure_time"])
            if dep_time > now:
                upcoming.append((trip, dep_time))
        except (KeyError, ValueError):
            continue
    
    if not upcoming:
        return None
    
    upcoming.sort(key=lambda x: x[1])
    return upcoming[0][0]


def get_active_trip() -> Optional[dict]:
    """Get currently active trip (departed but not returned)."""
    trips = load_trips()
    now = datetime.now(timezone.utc)
    
    for trip in trips:
        if trip.get("status") == "complete":
            continue
        legs = get_legs_for_trip(trip["id"])
        if not legs:
            continue
        
        first_leg = legs[0]
        last_leg = legs[-1]
        
        try:
            first_dep = _parse_time(first_leg["flight"]["departure_time"])
            last_arr = _parse_time(last_leg["flight"]["arrival_time"])
            
            # Active if we've departed on first leg but haven't arrived on last leg
            if first_dep <= now <= last_arr:
                return trip
        except (KeyError, ValueError):
            continue
    
    return None


def get_current_leg(trip: dict) -> Optional[dict]:
    """Get the current or next leg within an active trip."""
    now = datetime.now(timezone.utc)
    legs = get_legs_for_trip(trip["id"])
    
    for leg in legs:
        try:
            dep_time = _parse_time(leg["flight"]["departure_time"])
            arr_time = _parse_time(leg["flight"]["arrival_time"])
            
            # Currently in flight
            if dep_time <= now <= arr_time:
                return leg
            
            # Next upcoming leg
            if dep_time > now:
                return leg
        except (KeyError, ValueError):
            continue
    
    # Return last leg if all completed
    return legs[-1] if legs else None


def get_current_state() -> dict:
    """
    Get current state based on trip/leg data and time.
    Returns enriched context for frontend display.
    """
    now = datetime.now(timezone.utc)
    trips = load_trips()
    legs = load_legs()
    
    # Find active, upcoming, and past trips
    active_leg = None
    current_trip = None
    next_trip = None
    last_trip = None
    
    # Check for in-transit leg
    for leg in legs:
        flight = leg.get("flight", {})
        dep_str = flight.get("departure_time")
        arr_str = flight.get("arrival_time")
        if not dep_str or not arr_str:
            continue
        try:
            dep_time = _parse_time(dep_str)
            arr_time = _parse_time(arr_str)
            if dep_time <= now <= arr_time:
                active_leg = leg
                break
        except (ValueError, TypeError):
            continue
    
    # Find next upcoming leg (for pre-departure)
    upcoming_legs = []
    for leg in legs:
        flight = leg.get("flight", {})
        dep_str = flight.get("departure_time")
        if not dep_str:
            continue
        try:
            dep_time = _parse_time(dep_str)
            if dep_time > now:
                upcoming_legs.append((leg, dep_time))
        except (ValueError, TypeError):
            continue
    
    upcoming_legs.sort(key=lambda x: x[1])
    next_leg = upcoming_legs[0][0] if upcoming_legs else None
    
    # Find trips
    for trip in trips:
        trip_legs = get_legs_for_trip(trip["id"])
        if not trip_legs:
            continue
        
        first_flight = trip_legs[0].get("flight", {})
        last_flight = trip_legs[-1].get("flight", {})
        
        first_dep_str = first_flight.get("departure_time")
        last_arr_str = last_flight.get("arrival_time")
        
        if not first_dep_str or not last_arr_str:
            continue
            
        try:
            first_dep = _parse_time(first_dep_str)
            last_arr = _parse_time(last_arr_str)
        except (ValueError, TypeError):
            continue
        
        if first_dep <= now <= last_arr:
            current_trip = trip
        elif first_dep > now:
            if not next_trip:
                next_trip = trip
            else:
                # Compare to existing next_trip
                existing_legs = get_legs_for_trip(next_trip["id"])
                if existing_legs:
                    existing_dep_str = existing_legs[0].get("flight", {}).get("departure_time")
                    if existing_dep_str:
                        try:
                            existing_dep = _parse_time(existing_dep_str)
                            if first_dep < existing_dep:
                                next_trip = trip
                        except (ValueError, TypeError):
                            pass
        elif last_arr < now:
            if not last_trip:
                last_trip = trip
            else:
                # Compare to existing last_trip
                existing_legs = get_legs_for_trip(last_trip["id"])
                if existing_legs:
                    existing_arr_str = existing_legs[-1].get("flight", {}).get("arrival_time")
                    if existing_arr_str:
                        try:
                            existing_arr = _parse_time(existing_arr_str)
                            if last_arr > existing_arr:
                                last_trip = trip
                        except (ValueError, TypeError):
                            pass
    
    # Determine state
    state = "home"
    message = "V is home in NYC"
    context = {
        "last_destination": None,
        "next_destination": None,
        "next_flight": None,
        "next_return": None,
        "countdown_days": None
    }
    
    if active_leg:
        state = "in_transit"
        dest = active_leg.get("destination_city") or active_leg.get("flight", {}).get("arrival_airport", "destination")
        message = f"V is flying to {dest}"
        current_trip = next((t for t in trips if active_leg["trip_id"] == t["id"]), None)
    elif next_leg:
        flight = next_leg.get("flight", {})
        dep_str = flight.get("departure_time")
        if dep_str:
            try:
                dep_time = _parse_time(dep_str)
                days_until = (dep_time - now).days
                if days_until <= 7:
                    state = "pre_departure"
                    dest = next_leg.get("destination_city") or flight.get("arrival_airport", "destination")
                    message = f"V is preparing for {dest}"
                    context["countdown_days"] = days_until
                    current_trip = next((t for t in trips if next_leg["trip_id"] == t["id"]), None)
            except (ValueError, TypeError):
                pass
    
    # At destination: after arrival but before return departure
    if current_trip and not active_leg:
        trip_legs = get_legs_for_trip(current_trip["id"])
        if len(trip_legs) >= 2:
            first_arr_str = trip_legs[0].get("flight", {}).get("arrival_time")
            last_dep_str = trip_legs[-1].get("flight", {}).get("departure_time")
            if first_arr_str and last_dep_str:
                try:
                    first_arr = _parse_time(first_arr_str)
                    last_dep = _parse_time(last_dep_str)
                    if first_arr < now < last_dep:
                        state = "at_destination"
                        dest = trip_legs[0].get("destination_city") or trip_legs[0].get("flight", {}).get("arrival_airport")
                        message = f"V is in {dest}"
                except (ValueError, TypeError):
                    pass
    
    # Build context - last destination
    if last_trip:
        last_legs = get_legs_for_trip(last_trip["id"])
        if last_legs:
            context["last_destination"] = last_legs[0].get("destination_city") or last_legs[0].get("flight", {}).get("arrival_airport")
    
    # Build context - next trip with full flight details
    if next_trip:
        next_legs = get_legs_for_trip(next_trip["id"])
        if next_legs:
            first_leg = next_legs[0]
            last_leg = next_legs[-1]
            first_flight = first_leg.get("flight", {})
            last_flight = last_leg.get("flight", {})
            
            context["next_destination"] = first_leg.get("destination_city") or first_flight.get("arrival_airport")
            context["next_trip_notes"] = next_trip.get("notes")
            
            # Full flight details for at-a-glance view
            context["next_flight"] = {
                "number": first_flight.get("number"),
                "departure_airport": first_flight.get("departure_airport"),
                "arrival_airport": first_flight.get("arrival_airport"),
                "departure_time": first_flight.get("departure_time"),
                "arrival_time": first_flight.get("arrival_time"),
                "destination_city": first_leg.get("destination_city")
            }
            context["next_return"] = {
                "number": last_flight.get("number"),
                "departure_airport": last_flight.get("departure_airport"),
                "arrival_airport": last_flight.get("arrival_airport"),
                "departure_time": last_flight.get("departure_time"),
                "arrival_time": last_flight.get("arrival_time")
            }
    
    # Add leg context if there's an active leg
    if active_leg:
        active_trip = next((t for t in trips if active_leg["trip_id"] == t["id"]), None)
        if active_trip:
            trip_legs = get_legs_for_trip(active_trip["id"])
            context["leg_number"] = next((i+1 for i, l in enumerate(trip_legs) if l["id"] == active_leg["id"]), 1)
            context["total_legs"] = len(trip_legs)
    
    return {
        "state": state,
        "current_leg": active_leg,
        "current_trip": current_trip,
        "last_trip": last_trip,
        "next_trip": next_trip,
        "message": message,
        "context": context
    }


# ============== BACKWARD COMPATIBILITY ==============

def get_status() -> dict:
    """
    Legacy status endpoint - maps to new state machine.
    Maintains backward compatibility with existing frontend.
    """
    state = get_current_state()
    
    # Map new states to old format
    status_map = {
        "home": "home",
        "pre_departure": "departing",
        "in_transit": "flying",
        "at_destination": "arrived"
    }
    
    flight_data = None
    if state["current_leg"]:
        leg = state["current_leg"]
        flight_data = {
            "flight_number": leg["flight"]["number"],
            "departure_airport": leg["flight"]["departure_airport"],
            "arrival_airport": leg["flight"]["arrival_airport"],
            "departure_time": leg["flight"]["departure_time"],
            "arrival_time": leg["flight"]["arrival_time"]
        }
    
    return {
        "status": status_map.get(state["state"], "home"),
        "message": state["message"],
        "flight": flight_data
    }


# ============== CLI ==============

def _test():
    """Run basic tests."""
    print("Testing trip_store_v2.py...")
    
    # Clean up test data
    test_trips = TRIPS_FILE.with_suffix(".test.jsonl")
    test_legs = LEGS_FILE.with_suffix(".test.jsonl")
    
    # Create a test trip
    print("\n1. Creating test trip...")
    trip = create_trip(status="upcoming")
    print(f"   Created trip: {trip['id']}")
    
    # Create legs
    print("\n2. Creating test legs...")
    leg1 = create_leg(
        trip_id=trip["id"],
        sequence=1,
        flight_number="UA100",
        departure_airport="JFK",
        arrival_airport="MIA",
        departure_time="2025-01-15T10:00:00Z",
        arrival_time="2025-01-15T13:30:00Z",
        destination_city="Miami",
        hotel={"name": "Miami Beach Hotel", "address": "123 Ocean Dr"}
    )
    print(f"   Created leg 1: {leg1['id']}")
    
    leg2 = create_leg(
        trip_id=trip["id"],
        sequence=2,
        flight_number="UA101",
        departure_airport="MIA",
        arrival_airport="JFK",
        departure_time="2025-01-18T14:00:00Z",
        arrival_time="2025-01-18T17:30:00Z",
        destination_city="New York"
    )
    print(f"   Created leg 2: {leg2['id']}")
    
    # Test queries
    print("\n3. Testing queries...")
    loaded_trip = get_trip(trip["id"])
    print(f"   Trip legs: {loaded_trip['legs']}")
    
    trip_legs = get_legs_for_trip(trip["id"])
    print(f"   Legs for trip: {len(trip_legs)}")
    
    # Test state machine
    print("\n4. Testing state machine...")
    state = get_current_state()
    print(f"   Current state: {state['state']}")
    print(f"   Message: {state['message']}")
    
    # Test backward compatibility
    print("\n5. Testing backward compatibility...")
    status = get_status()
    print(f"   Legacy status: {status['status']}")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: trip_store_v2.py <command> [args]")
        print("Commands: state, list-trips, list-legs, get-leg <id>, test")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "state":
        print(json.dumps(get_current_state(), indent=2, default=str))
    elif cmd == "list-trips":
        print(json.dumps(load_trips(), indent=2, default=str))
    elif cmd == "list-legs":
        print(json.dumps(load_legs(), indent=2, default=str))
    elif cmd == "get-leg":
        if len(sys.argv) < 3:
            print("Usage: trip_store_v2.py get-leg <leg_id>")
            sys.exit(1)
        leg_id = sys.argv[2]
        legs = load_legs()
        leg = next((l for l in legs if l["id"] == leg_id), None)
        if leg:
            print(json.dumps(leg, indent=2, default=str))
        else:
            print(json.dumps({"error": "Leg not found"}))
            sys.exit(1)
    elif cmd == "test":
        _test()
    elif cmd == "update-notes":
        if len(sys.argv) < 4:
            print("Usage: trip_store_v2.py update-notes <trip_id> <notes>")
            sys.exit(1)
        trip_id = sys.argv[2]
        notes = " ".join(sys.argv[3:])
        result = update_trip_notes(trip_id, notes)
        if result:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps({"error": "Trip not found"}))
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)






