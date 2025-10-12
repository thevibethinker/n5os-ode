#!/usr/bin/env python3
"""
Test Cycle Runner for Meeting Monitor
Executes a single test cycle with the Zo API tools passed in.
"""

import sys
from pathlib import Path

# Add N5/scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')

def run_test_cycle(use_app_google_calendar, use_app_gmail, lookahead_days=7):
    """
    Run a single test cycle of the meeting monitor.
    
    Args:
        use_app_google_calendar: Zo's Google Calendar tool function
        use_app_gmail: Zo's Gmail tool function
        lookahead_days: How far ahead to look (default 7)
        
    Returns:
        dict: Test results
    """
    from run_meeting_monitor import run_single_cycle_with_zo_tools
    
    print("=" * 60)
    print("MEETING MONITOR TEST CYCLE")
    print("=" * 60)
    print()
    print("Context: Phase 2B Priority 4 - Complete")
    print("Status: Running end-to-end validation")
    print()
    print("Test Parameters:")
    print(f"  - Lookahead: {lookahead_days} days")
    print(f"  - Using: Google Calendar API + Gmail API")
    print()
    print("=" * 60)
    print()
    
    try:
        result = run_single_cycle_with_zo_tools(
            use_app_google_calendar,
            use_app_gmail,
            lookahead_days=lookahead_days
        )
        
        print()
        print("=" * 60)
        print("TEST CYCLE RESULTS")
        print("=" * 60)
        print()
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            return result
        
        # Print results
        print(f"✅ Total events checked: {result.get('total_events', 0)}")
        print(f"✅ New events processed: {result.get('new_events', 0)}")
        print(f"✅ Already processed: {result.get('already_processed', 0)}")
        print(f"⚠️  Urgent meetings: {result.get('urgent_count', 0)}")
        print(f"❌ Errors: {result.get('errors', 0)}")
        print()
        
        if result.get('new_events', 0) > 0:
            print("📋 NEW MEETINGS DETECTED:")
            print()
            for detail in result.get('processed_details', []):
                print(f"  - {detail['summary']}")
                print(f"    Time: {detail['start_time']}")
                print(f"    Attendee: {detail['attendee_email']}")
                if detail.get('profile_dir'):
                    print(f"    Profile: N5/records/meetings/{detail['profile_dir']}/")
                print()
        
        if result.get('digest_section'):
            print("📧 DIGEST SECTION GENERATED:")
            print()
            print(result['digest_section'])
            print()
        
        print("=" * 60)
        print("FILES TO CHECK:")
        print("=" * 60)
        print()
        print("  1. Log file: N5/logs/meeting_monitor.log")
        print("  2. State file: N5/records/meetings/.processed.json")
        print("  3. Profiles: N5/records/meetings/ (if any created)")
        print()
        print("Run health check:")
        print("  python3 N5/scripts/monitor_health.py")
        print()
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'fatal': True}

if __name__ == '__main__':
    print("This script must be called with API tools from Zo.")
    print("It cannot run standalone.")
