#!/usr/bin/env python3
"""
Google Calendar API Helper

Provides functions for searching and matching calendar events.
Uses Zo's google_calendar integration via subprocess calls.
"""

import json
import subprocess
from datetime import datetime
from typing import List, Optional, Dict


def search_events(time_min: str, time_max: str, participants: List[str] = None, title_hint: str = None) -> Optional[str]:
    """
    Search Google Calendar for events matching criteria.
    
    Args:
        time_min: ISO 8601 format (e.g., "2025-11-15T00:00:00Z")
        time_max: ISO 8601 format
        participants: List of participant names to match
        title_hint: Optional title substring to match
        
    Returns:
        Event ID if unique match found, None otherwise
    """
    
    # Use Zo CLI to query Google Calendar
    # This creates a subprocess that calls the Zo assistant with calendar query
    query_cmd = [
        "zo", "run",
        f"Use google calendar to list events between {time_min} and {time_max}. Return as JSON with fields: id, summary, attendees, start, end"
    ]
    
    try:
        result = subprocess.run(
            query_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None
        
        # Parse JSON response
        events = json.loads(result.stdout)
        
        # Filter events by criteria
        matches = []
        for event in events:
            # Check title match
            if title_hint and title_hint.lower() not in event.get("summary", "").lower():
                continue
            
            # Check participants match
            if participants:
                event_attendees = [a.get("email", "") for a in event.get("attendees", [])]
                event_names = [a.get("displayName", "") for a in event.get("attendees", [])]
                
                # At least one participant should match
                match_found = False
                for participant in participants:
                    participant_lower = participant.lower()
                    if any(participant_lower in name.lower() for name in event_names):
                        match_found = True
                        break
                    if any(participant_lower in email.lower() for email in event_attendees):
                        match_found = True
                        break
                
                if not match_found:
                    continue
            
            matches.append(event)
        
        # Return event ID if unique match
        if len(matches) == 1:
            return matches[0].get("id")
        elif len(matches) == 0:
            return None
        else:
            # Multiple matches - try to pick best one
            # Prefer events with more attendees (less likely to be personal)
            matches.sort(key=lambda e: len(e.get("attendees", [])), reverse=True)
            return matches[0].get("id")
    
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


def get_event_details(event_id: str) -> Optional[Dict]:
    """
    Get full details for a specific calendar event.
    
    Args:
        event_id: Google Calendar event ID
        
    Returns:
        Event details dict or None
    """
    query_cmd = [
        "zo", "run",
        f"Use google calendar to get event details for event ID {event_id}. Return as JSON."
    ]
    
    try:
        result = subprocess.run(
            query_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None
        
        return json.loads(result.stdout)
    
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 google_calendar_helper.py <time_min> <time_max>")
        sys.exit(1)
    
    event_id = search_events(sys.argv[1], sys.argv[2])
    print(f"Found event: {event_id}")

