#!/usr/bin/env python3
"""
Execute meeting monitor test cycle with real Zo API tools.
This script is designed to be called with the actual tool functions.
"""

import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

def execute_with_tools(use_app_google_calendar_func, use_app_gmail_func):
    """Execute the test with real API tools."""
    from run_meeting_monitor import run_single_cycle_with_zo_tools
    from datetime import datetime
    import pytz
    
    print("=" * 80)
    print("MEETING MONITOR TEST CYCLE - EXECUTING WITH REAL API TOOLS")
    print("=" * 80)
    print()
    print(f"Timestamp: {datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d %I:%M:%S %p ET')}")
    print()
    print("Configuration:")
    print("  - Calendar API: Connected ✓")
    print("  - Gmail API: Connected ✓")
    print("  - Lookahead: 7 days")
    print("  - Mode: Single test cycle")
    print()
    print("=" * 80)
    print()
    
    try:
        result = run_single_cycle_with_zo_tools(
            use_app_google_calendar_func,
            use_app_gmail_func,
            lookahead_days=7
        )
        
        print()
        print("=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print()
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            return result
        
        print(f"✅ Total events checked: {result.get('total_events', 0)}")
        print(f"✅ New events processed: {result.get('new_events', 0)}")  
        print(f"✅ Already processed: {result.get('already_processed', 0)}")
        print(f"⚠️  Urgent meetings: {result.get('urgent_count', 0)}")
        print(f"❌ Errors: {result.get('errors', 0)}")
        print()
        
        if result.get('new_events', 0) > 0:
            print("📋 NEW MEETINGS FOUND:")
            for detail in result.get('processed_details', []):
                print(f"  - {detail['summary']} at {detail['start_time']}")
                print(f"    Attendee: {detail['attendee_email']}")
            print()
        else:
            print("ℹ️  No new meetings with V-OS tags found")
            print("   (This is expected if Howie hasn't added V-OS tags yet)")
            print()
        
        print("=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print()
        print("1. Check log file:")
        print("   cat N5/logs/meeting_monitor.log")
        print()
        print("2. Run health check:")
        print("   python3 N5/scripts/monitor_health.py")
        print()
        print("3. Check state file:")
        print("   cat N5/records/meetings/.processed.json")
        print()
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'fatal': True}

# This will be imported and called by the main execution
__all__ = ['execute_with_tools']
