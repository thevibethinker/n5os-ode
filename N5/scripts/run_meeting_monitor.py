#!/usr/bin/env python3
"""
Run Meeting Monitor with Zo API Tools
Wrapper script for Zo to execute the meeting monitor with proper API access.
"""

import sys
from pathlib import Path

# Add N5/scripts to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from meeting_monitor import MeetingMonitor


def run_monitor_with_zo_tools(use_app_google_calendar, use_app_gmail, 
                               poll_interval_minutes=15, lookahead_days=7,
                               max_cycles=None):
    """
    Run the meeting monitor with Zo's API tools.
    
    Args:
        use_app_google_calendar: Zo's Google Calendar tool function
        use_app_gmail: Zo's Gmail tool function
        poll_interval_minutes: How often to poll (default 15)
        lookahead_days: How far ahead to look (default 7)
        max_cycles: Max cycles to run (None = infinite)
        
    Returns:
        dict: Summary of monitoring session
    """
    monitor = MeetingMonitor(
        calendar_tool=use_app_google_calendar,
        gmail_tool=use_app_gmail,
        poll_interval_minutes=poll_interval_minutes,
        lookahead_days=lookahead_days
    )
    
    summary = monitor.run_continuous(max_cycles=max_cycles)
    
    return summary


def run_single_cycle_with_zo_tools(use_app_google_calendar, use_app_gmail, 
                                    lookahead_days=7):
    """
    Run a single monitoring cycle (for testing).
    
    Args:
        use_app_google_calendar: Zo's Google Calendar tool function
        use_app_gmail: Zo's Gmail tool function
        lookahead_days: How far ahead to look (default 7)
        
    Returns:
        dict: Results from single cycle
    """
    monitor = MeetingMonitor(
        calendar_tool=use_app_google_calendar,
        gmail_tool=use_app_gmail,
        lookahead_days=lookahead_days
    )
    
    result = monitor.run_single_cycle()
    
    return result


if __name__ == '__main__':
    print("This script is designed to be called by Zo with API tools.")
    print("It cannot run standalone.")
