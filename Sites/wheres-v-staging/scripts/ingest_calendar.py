#!/usr/bin/env python3
"""
Calendar Ingestion for Where's V
Fetches travel-related events from Google Calendar.

This script outputs raw calendar event data as JSON for LLM processing.
It does NOT parse flight details - that's done by extract_trips.py.
"""
import json
import sys
import subprocess
from datetime import datetime, timezone, timedelta

# Keywords that suggest travel events
TRAVEL_KEYWORDS = [
    "flight", "fly", "airport", "airline",
    "travel", "trip", "vacation",
    "united", "delta", "american", "jetblue", "southwest", "spirit", "frontier",
    "hotel", "airbnb", "check-in", "checkout"
]


def fetch_calendar_events(days_back: int = 30, days_forward: int = 60) -> list[dict]:
    """
    Fetch calendar events that may be travel-related.
    
    Uses Zo's Google Calendar integration via the use_app_google_calendar tool.
    Since we're a Python script, we invoke this through the Zo API.
    
    Returns list of event dicts with: summary, description, start, end, location
    """
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_back)).isoformat()
    time_max = (now + timedelta(days=days_forward)).isoformat()
    
    # Build the calendar query
    # This will be invoked by extract_trips.py via Zo API
    query_params = {
        "calendarId": "primary",
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": 100,
        "singleEvents": True,
        "orderBy": "startTime"
    }
    
    return {
        "tool": "google_calendar-list-events",
        "params": query_params,
        "time_range": {
            "from": time_min,
            "to": time_max
        }
    }


def filter_travel_events(events: list[dict]) -> list[dict]:
    """
    Filter events to those likely related to travel.
    
    Args:
        events: List of calendar event dicts
        
    Returns:
        Filtered list of events that match travel keywords
    """
    travel_events = []
    
    for event in events:
        # Check summary, description, and location for travel keywords
        text_to_check = " ".join([
            event.get("summary", ""),
            event.get("description", ""),
            event.get("location", "")
        ]).lower()
        
        for keyword in TRAVEL_KEYWORDS:
            if keyword in text_to_check:
                travel_events.append(event)
                break
    
    return travel_events


def format_for_extraction(events: list[dict]) -> str:
    """
    Format events for LLM extraction prompt.
    
    Returns a human-readable summary of events for the LLM to parse.
    """
    if not events:
        return "No travel-related calendar events found."
    
    output = []
    output.append(f"Found {len(events)} potential travel events:\n")
    
    for i, event in enumerate(events, 1):
        output.append(f"--- Event {i} ---")
        output.append(f"Title: {event.get('summary', 'No title')}")
        
        start = event.get("start", {})
        end = event.get("end", {})
        output.append(f"Start: {start.get('dateTime') or start.get('date', 'Unknown')}")
        output.append(f"End: {end.get('dateTime') or end.get('date', 'Unknown')}")
        
        if event.get("location"):
            output.append(f"Location: {event['location']}")
        
        if event.get("description"):
            # Truncate long descriptions
            desc = event["description"][:500]
            if len(event["description"]) > 500:
                desc += "..."
            output.append(f"Description: {desc}")
        
        output.append("")
    
    return "\n".join(output)


if __name__ == "__main__":
    # When run directly, output the query parameters needed
    # The actual API call is made by extract_trips.py through Zo
    
    if len(sys.argv) > 1 and sys.argv[1] == "--query":
        query = fetch_calendar_events()
        print(json.dumps(query, indent=2))
    else:
        print("Calendar Ingestion Script")
        print("=" * 40)
        print("\nThis script prepares calendar queries for travel event extraction.")
        print("\nUsage:")
        print("  --query    Output the Google Calendar API query parameters")
        print("\nThe actual API call is made by extract_trips.py through the Zo API.")
        print("\nTravel keywords searched:")
        for kw in TRAVEL_KEYWORDS:
            print(f"  - {kw}")

