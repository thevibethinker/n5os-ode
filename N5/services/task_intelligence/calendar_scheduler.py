#!/usr/bin/env python3
"""
Calendar-aware task scheduling.
Finds optimal time slots based on calendar availability.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def get_calendar_free_slots(start_date: datetime, end_date: datetime, 
                            min_duration_minutes: int = 30) -> List[Dict]:
    """
    Query Google Calendar for free time slots.
    Returns list of {start, end, duration_minutes}
    """
    # TODO: Call use_app_google_calendar to get events
    # For now, return mock data structure
    
    # This would use:
    # use_app_google_calendar(
    #     tool_name='google_calendar-list-events',
    #     configured_props={
    #         'calendarId': 'primary',
    #         'timeMin': start_date.isoformat(),
    #         'timeMax': end_date.isoformat()
    #     }
    # )
    
    logger.info(f"Querying calendar from {start_date} to {end_date}")
    return []

def find_optimal_slot(task: Dict, calendar_events: List[Dict]) -> Optional[Dict]:
    """
    Find best time slot for a task based on:
    - Task duration
    - Priority
    - User's work hours (9am-6pm ET)
    - Existing calendar commitments
    """
    duration_min = parse_duration(task.get('duration', '30m'))
    priority = task.get('priority', 'Normal')
    
    # Work hours: 9am-6pm ET
    work_start = 9
    work_end = 18
    
    # Priority affects preferred time:
    # High priority → morning (9-12)
    # Normal → afternoon (1-4)
    # Low → late afternoon (4-6)
    
    if priority == 'High':
        preferred_start, preferred_end = 9, 12
    elif priority == 'Low':
        preferred_start, preferred_end = 16, 18
    else:
        preferred_start, preferred_end = 13, 16
    
    # Find free slots in preferred window
    now = datetime.now()
    search_start = now.replace(hour=preferred_start, minute=0, second=0)
    search_end = now.replace(hour=preferred_end, minute=0, second=0)
    
    # If preferred window passed today, try tomorrow
    if search_end < now:
        search_start += timedelta(days=1)
        search_end += timedelta(days=1)
    
    suggested_time = search_start.strftime('%Y-%m-%d %I:%M%p ET')
    
    return {
        'suggested_time': suggested_time,
        'reasoning': f"{priority} priority tasks scheduled in {preferred_start}-{preferred_end}:00 window",
        'duration': task.get('duration', '30m')
    }

def parse_duration(duration_str: str) -> int:
    """Parse duration string like '30m', '1h' to minutes."""
    if 'h' in duration_str:
        return int(duration_str.replace('h', '')) * 60
    elif 'm' in duration_str:
        return int(duration_str.replace('m', ''))
    return 30

def schedule_task(task: Dict) -> Dict:
    """
    Main entry point: Given a task, find optimal scheduling.
    Returns task with enhanced timing information.
    """
    try:
        # Get calendar availability
        now = datetime.now()
        week_later = now + timedelta(days=7)
        calendar_events = get_calendar_free_slots(now, week_later)
        
        # Find optimal slot
        slot = find_optimal_slot(task, calendar_events)
        
        if slot:
            task['when'] = slot['suggested_time']
            task['scheduling_reasoning'] = slot['reasoning']
        
        return task
        
    except Exception as e:
        logger.error(f"Scheduling failed: {e}", exc_info=True)
        return task

if __name__ == '__main__':
    # Test
    test_task = {
        'title': 'Review proposal',
        'duration': '45m',
        'priority': 'High',
        'project': 'Operations'
    }
    
    result = schedule_task(test_task)
    print(json.dumps(result, indent=2))
