#!/usr/bin/env python3
"""
Run Meeting Processor
Execute meeting prep pipeline with real Google Calendar and Gmail APIs
"""

import sys
import os

# This script is designed to be called by Zo with API tool access
# It cannot be run standalone as it requires Zo's app tool functions


def run_processor_with_zo_tools(use_app_google_calendar, use_app_gmail, days_ahead=7):
    """
    Run the meeting processor with Zo's app tools
    
    Args:
        use_app_google_calendar: Zo's Google Calendar tool function
        use_app_gmail: Zo's Gmail tool function
        days_ahead: Number of days ahead to process (default: 7)
    
    Returns:
        Processing results dict
    """
    
    # Import modules
    from meeting_api_integrator import MeetingAPIIntegrator
    from meeting_processor import MeetingProcessor
    
    print("🚀 Initializing Meeting Processor with Google Calendar & Gmail APIs\n")
    
    # Create API integrator
    api_integrator = MeetingAPIIntegrator(
        calendar_tool=use_app_google_calendar,
        gmail_tool=use_app_gmail
    )
    
    # Create processor
    processor = MeetingProcessor(api_integrator)
    
    # Process meetings
    results = processor.process_upcoming_meetings(days_ahead=days_ahead)
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Run Meeting Processor")
    print("=" * 60)
    print()
    print("This script must be called by Zo with API tool access.")
    print("It cannot be run standalone.")
    print()
    print("Zo will call: run_processor_with_zo_tools()")
    print("             with use_app_google_calendar and use_app_gmail functions")
    print("=" * 60)
