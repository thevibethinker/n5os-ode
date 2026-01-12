#!/usr/bin/env python3
"""
Stage Calculator - Determines current trip stage based on time
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

def parse_time(time_str: str) -> datetime:
    """Parse ISO 8601 timestamp"""
    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))

def calculate_stage(trip: dict) -> dict:
    """
    Calculate current trip stage
    Returns: {
        "stage": "preparing|heading_to_airport|in_air_out|landed_destination|at_destination|in_air_return|home",
        "message": "Parent-friendly status message",
        "next_event": "What happens next",
        "progress_percent": 0-100
    }
    """
    now = datetime.now(timezone.utc)
    
    outbound = trip.get("outbound", {})
    return_flight = trip.get("return")
    
    # Parse times
    dep_time = parse_time(outbound["departure"]["time"])
    arr_time = parse_time(outbound["arrival"]["time"])
    
    # Outbound: Preparing
    if now < dep_time - timedelta(hours=2):
        hours_until = int((dep_time - now).total_seconds() / 3600)
        return {
            "stage": "preparing",
            "message": f"Preparing for trip to {outbound['arrival']['city']}",
            "next_event": f"Departure in {hours_until} hours",
            "progress_percent": 0
        }
    
    # Outbound: Heading to airport
    if dep_time - timedelta(hours=2) <= now < dep_time:
        return {
            "stage": "heading_to_airport",
            "message": f"Heading to {outbound['departure']['airport']} airport",
            "next_event": f"Flight {outbound['flight_number']} departs soon",
            "progress_percent": 10
        }
    
    # Outbound: In the air
    if dep_time <= now < arr_time:
        elapsed = (now - dep_time).total_seconds()
        total = (arr_time - dep_time).total_seconds()
        progress = 20 + int((elapsed / total) * 30)  # 20-50%
        
        mins_remaining = int((arr_time - now).total_seconds() / 60)
        return {
            "stage": "in_air_out",
            "message": f"Flying to {outbound['arrival']['city']}",
            "next_event": f"Landing in {mins_remaining} minutes",
            "progress_percent": progress
        }
    
    # Check if we have a return flight
    if return_flight:
        ret_dep_time = parse_time(return_flight["departure"]["time"])
        ret_arr_time = parse_time(return_flight["arrival"]["time"])
        
        # Landed at destination
        if arr_time <= now < arr_time + timedelta(hours=1):
            return {
                "stage": "landed_destination",
                "message": f"Landed safely in {outbound['arrival']['city']}",
                "next_event": f"Return flight {return_flight['flight_number']} on {ret_dep_time.strftime('%b %d')}",
                "progress_percent": 50
            }
        
        # At destination
        if arr_time + timedelta(hours=1) <= now < ret_dep_time - timedelta(hours=2):
            days_until_return = (ret_dep_time - now).days
            return {
                "stage": "at_destination",
                "message": f"In {outbound['arrival']['city']}",
                "next_event": f"Return flight in {days_until_return} days" if days_until_return > 0 else "Return flight today",
                "progress_percent": 50
            }
        
        # Heading to airport for return
        if ret_dep_time - timedelta(hours=2) <= now < ret_dep_time:
            return {
                "stage": "heading_to_airport_return",
                "message": f"Heading to {return_flight['departure']['airport']} airport",
                "next_event": f"Return flight {return_flight['flight_number']} departs soon",
                "progress_percent": 60
            }
        
        # In the air (return)
        if ret_dep_time <= now < ret_arr_time:
            elapsed = (now - ret_dep_time).total_seconds()
            total = (ret_arr_time - ret_dep_time).total_seconds()
            progress = 70 + int((elapsed / total) * 25)  # 70-95%
            
            mins_remaining = int((ret_arr_time - now).total_seconds() / 60)
            return {
                "stage": "in_air_return",
                "message": "Flying home",
                "next_event": f"Landing in {mins_remaining} minutes",
                "progress_percent": progress
            }
        
        # Home
        if now >= ret_arr_time:
            return {
                "stage": "home",
                "message": "Back home safe ✈️",
                "next_event": "Trip complete",
                "progress_percent": 100
            }
    
    # No return flight - just show arrived
    if now >= arr_time:
        return {
            "stage": "landed_destination",
            "message": f"Arrived in {outbound['arrival']['city']}",
            "next_event": "Enjoying the trip",
            "progress_percent": 100
        }
    
    # Fallback
    return {
        "stage": "unknown",
        "message": "Tracking trip",
        "next_event": "",
        "progress_percent": 0
    }

if __name__ == "__main__":
    import json
    from trip_manager import get_active_trip
    
    trip = get_active_trip()
    if trip:
        stage = calculate_stage(trip)
        print(json.dumps(stage, indent=2))
    else:
        print("No active trip")
