#!/usr/bin/env python3
"""
Test processor with live APIs - to be called by Zo
This file shows Zo how to execute the processor
"""

def test_live_api_integration(use_app_google_calendar_func, use_app_gmail_func):
    """
    Test function that Zo will call with real API tools
    
    Args:
        use_app_google_calendar_func: Zo's Google Calendar API function
        use_app_gmail_func: Zo's Gmail API function
    """
    import sys
    sys.path.insert(0, '/home/workspace/N5/scripts')
    
    from meeting_api_integrator import MeetingAPIIntegrator
    from meeting_processor import MeetingProcessor
    
    # Create API integrator
    api = MeetingAPIIntegrator(
        calendar_tool=use_app_google_calendar_func,
        gmail_tool=use_app_gmail_func
    )
    
    # Create processor
    processor = MeetingProcessor(api)
    
    # Process upcoming meetings
    results = processor.process_upcoming_meetings(days_ahead=7)
    
    return results

if __name__ == "__main__":
    print("This module must be imported and called by Zo with API tools")
