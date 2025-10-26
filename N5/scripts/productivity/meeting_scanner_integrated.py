#!/usr/bin/env python3
"""
Meeting Scanner - Integrated Version
This version is designed to be called BY Zo agent with Calendar integration.
The standalone meeting_scanner.py contains the core logic but cannot access APIs directly.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path to import meeting_scanner
sys.path.insert(0, str(Path(__file__).parent))

import meeting_scanner

def integrate_calendar_api(calendar_events_json: str):
    """
    Integration point for Zo agent to provide Calendar API results.
    
    Usage from Zo:
    1. Call use_app_google_calendar to get events
    2. Pass events JSON to this script
    3. Script processes and stores to database
    """
    
    try:
        events = json.loads(calendar_events_json)
        return events
    except Exception as e:
        meeting_scanner.logger.error(f"Error parsing calendar events: {e}")
        return []

if __name__ == "__main__":
    print("This script requires Zo agent execution with Calendar API integration")
    print("See meeting_scanner.py for standalone testing")
