#!/usr/bin/env python3
"""
Calendar Data Fetcher

Standalone script that fetches calendar events from Google Calendar
and processes them into metrics. This is called by performance_data.py
to avoid circular import issues.
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta


def fetch_and_process_calendar_data(days=7):
    """
    Fetch calendar events and return processed metrics.
    Uses command-line call to avoid import issues.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        start_rfc = start_date.strftime('%Y-%m-%dT00:00:00-05:00')
        end_rfc = end_date.strftime('%Y-%m-%dT00:00:00-05:00')
        
        # Create a Python script that calls the Google Calendar API
        temp_script = f'''
import sys
import json
sys.path.insert(0, '/home/workspace')

# This will be filled in by the parent process
from N5.scripts.calendar_metrics import process_calendar_events, calculate_metrics

# Simulate fetching data - in real implementation this would call use_app_google_calendar
# For now return basic structure
sample_events = []  # Empty for now until we implement real fetching

# Process and calculate metrics
processed_events = process_calendar_events(sample_events)
metrics = calculate_metrics(processed_events)

# Calculate average fragmentation
fragmentation_scores = list(metrics.get('fragmentation_by_day', {{}}).values())
fragmentation_avg = sum(fragmentation_scores) / len(fragmentation_scores) if fragmentation_scores else 0.0

result = {{
    "meeting_count": metrics.get('meeting_count', 0),
    "total_hours": metrics.get('total_hours', 0.0),
    "avg_meeting_length": metrics.get('avg_meeting_length', 0.0),
    "fragmentation_avg": round(fragmentation_avg, 2),
    "back_to_back_count": metrics.get('back_to_back_count', 0),
    "busiest_day": metrics.get('busiest_day'),
    "quietest_day": metrics.get('quietest_day'),
    "longest_gap": metrics.get('longest_gap', {{"day": None, "hours": 0.0}}),
    "excluded_count": metrics.get('excluded_count', 0),
    "data_points": len(sample_events)
}}

print(json.dumps(result))
'''
        
        # Write temp script and execute
        with open('/tmp/calendar_fetcher.py', 'w') as f:
            f.write(temp_script)
        
        # Execute the script
        result = subprocess.run([sys.executable, '/tmp/calendar_fetcher.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error in calendar fetcher: {result.stderr}", file=sys.stderr)
            return {
                "meeting_count": 0,
                "total_hours": 0.0,
                "avg_meeting_length": 0.0,
                "fragmentation_avg": 0.0,
                "back_to_back_count": 0,
                "busiest_day": None,
                "quietest_day": None,
                "longest_gap": {"day": None, "hours": 0.0},
                "excluded_count": 0,
                "data_points": 0
            }
            
    except Exception as e:
        print(f"Error in fetch_and_process_calendar_data: {e}", file=sys.stderr)
        return {
            "meeting_count": 0,
            "total_hours": 0.0,
            "avg_meeting_length": 0.0,
            "fragmentation_avg": 0.0,
            "back_to_back_count": 0,
            "busiest_day": None,
            "quietest_day": None,
            "longest_gap": {"day": None, "hours": 0.0},
            "excluded_count": 0,
            "data_points": 0
        }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        result = fetch_and_process_calendar_data()
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 calendar_data_fetcher.py --test")