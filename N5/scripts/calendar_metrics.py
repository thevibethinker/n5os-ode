#!/usr/bin/env python3
"""
Calendar Metrics Module

Fetches calendar events from Google Calendar and calculates performance metrics
including meeting analysis, fragmentation scoring, and productivity insights.
"""

import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path


CACHE_PATH = Path("/home/workspace/N5/data/calendar_cache.json")
CACHE_MAX_AGE_HOURS = 24


def fetch_week_events(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch events from cached calendar data.
    
    The cache is populated by Zo when running the dashboard generator
    or via: python3 N5/scripts/calendar_metrics.py --sync
    
    Returns list of event dicts with: title, start, end, duration_min, description, is_all_day
    """
    if not CACHE_PATH.exists():
        print(f"Calendar cache not found. Run dashboard with --sync or update cache.", file=sys.stderr)
        return []
    
    try:
        with open(CACHE_PATH) as f:
            cache = json.load(f)
        
        # Check cache age
        cached_at = datetime.fromisoformat(cache.get('cached_at', '2000-01-01'))
        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
        
        if age_hours > CACHE_MAX_AGE_HOURS:
            print(f"Calendar cache is {age_hours:.1f} hours old. Consider refreshing.", file=sys.stderr)
        
        events = cache.get('events', [])
        
        # Filter to requested date range
        filtered = [e for e in events 
                   if e.get('start', '')[:10] >= start_date 
                   and e.get('start', '')[:10] <= end_date]
        
        return filtered
        
    except Exception as e:
        print(f"Error reading calendar cache: {e}", file=sys.stderr)
        return []


def process_calendar_events(raw_events: list[dict]) -> list[dict]:
    """
    Process raw calendar events from Google Calendar API into standardized format.
    Returns list of: {title, start, end, duration_min, description, is_all_day}
    """
    processed_events = []
    
    for event in raw_events:
        try:
            # Extract basic info
            title = event.get("summary", "Untitled Event")
            description = event.get("description", "")
            
            # Handle start/end times
            start_info = event.get("start", {})
            end_info = event.get("end", {})
            
            # Check if all-day event
            is_all_day = "date" in start_info
            
            if is_all_day:
                start_str = start_info.get("date", "")
                end_str = end_info.get("date", "")
                duration_min = 0  # All-day events don't count for fragmentation
            else:
                start_str = start_info.get("dateTime", "")
                end_str = end_info.get("dateTime", "")
                
                # Calculate duration
                if start_str and end_str:
                    start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    duration_min = int((end_dt - start_dt).total_seconds() / 60)
                else:
                    duration_min = 0
            
            processed_events.append({
                "title": title,
                "start": start_str,
                "end": end_str,
                "duration_min": duration_min,
                "description": description,
                "is_all_day": is_all_day
            })
            
        except Exception as e:
            print(f"Error processing event: {e}", file=sys.stderr)
            continue
    
    return processed_events


def is_real_meeting(event: dict) -> bool:
    """
    Returns False if event should be excluded from metrics.
    
    Exclusion rules:
    - Description contains '[SKIP]' tag (V-OS system tag)
    - Title contains: 'Block', 'Hold', 'Focus', 'Buffer', 'Travel'
    - All-day events
    - Duration < 10 minutes
    - Events with no other attendees (self-only, unless titled as "1:1" or "Meeting")
    """
    title = event.get("title", "").lower()
    description = event.get("description", "")
    duration_min = event.get("duration_min", 0)
    is_all_day = event.get("is_all_day", False)
    
    # Check for [SKIP] tag in description
    if "[SKIP]" in description or "[skip]" in description.lower():
        return False
    
    # Check for V-OS tag format: V-OS Tags: {Zo} [SKIP] *
    vos_pattern = r'V-OS Tags:.*\[SKIP\].*\*'
    if re.search(vos_pattern, description, re.IGNORECASE):
        return False
    
    # Exclude all-day events
    if is_all_day:
        return False
    
    # Exclude very short events (< 10 minutes)
    if duration_min < 10:
        return False
    
    # Check title for exclusion keywords
    exclusion_keywords = ['block', 'hold', 'focus', 'buffer', 'travel']
    for keyword in exclusion_keywords:
        if keyword in title:
            return False
    
    # TODO: Check attendee count (would need attendees data from API)
    # For now, assume events with "1:1" or "Meeting" in title are real meetings
    # even if they might be self-only
    
    return True


def calculate_metrics(events: list[dict]) -> dict:
    """
    Returns: {
        meeting_count: int,
        total_hours: float,
        avg_meeting_length: float,
        fragmentation_by_day: {date: score},  # 0-1, higher = more fragmented
        back_to_back_count: int,
        busiest_day: str,
        quietest_day: str,
        longest_gap: {day: str, hours: float},
        excluded_count: int  # How many events were filtered out
    }
    """
    # Filter to real meetings
    real_meetings = [event for event in events if is_real_meeting(event)]
    excluded_count = len(events) - len(real_meetings)
    
    if not real_meetings:
        return {
            "meeting_count": 0,
            "total_hours": 0.0,
            "avg_meeting_length": 0.0,
            "fragmentation_by_day": {},
            "back_to_back_count": 0,
            "busiest_day": None,
            "quietest_day": None,
            "longest_gap": {"day": None, "hours": 0.0},
            "excluded_count": excluded_count
        }
    
    # Basic metrics
    meeting_count = len(real_meetings)
    total_minutes = sum(event["duration_min"] for event in real_meetings)
    total_hours = total_minutes / 60.0
    avg_meeting_length = total_minutes / meeting_count if meeting_count > 0 else 0.0
    
    # Group by day for fragmentation and daily analysis
    events_by_day = {}
    for event in real_meetings:
        if event.get("start") and not event.get("is_all_day"):
            try:
                start_dt = datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
                day_key = start_dt.strftime('%Y-%m-%d')
                
                if day_key not in events_by_day:
                    events_by_day[day_key] = []
                
                events_by_day[day_key].append({
                    "start": start_dt,
                    "end": datetime.fromisoformat(event["end"].replace('Z', '+00:00')),
                    "duration_min": event["duration_min"]
                })
            except:
                continue
    
    # Sort events within each day
    for day in events_by_day:
        events_by_day[day].sort(key=lambda x: x["start"])
    
    # Calculate fragmentation by day
    fragmentation_by_day = {}
    for day, day_events in events_by_day.items():
        fragmentation_by_day[day] = calculate_fragmentation(day_events)
    
    # Find busiest and quietest days
    daily_hours = {day: sum(e["duration_min"] for e in events) / 60.0 
                   for day, events in events_by_day.items()}
    
    busiest_day = max(daily_hours.keys(), key=daily_hours.get) if daily_hours else None
    quietest_day = min(daily_hours.keys(), key=daily_hours.get) if daily_hours else None
    
    # Calculate back-to-back meetings
    back_to_back_count = 0
    for day_events in events_by_day.values():
        for i in range(len(day_events) - 1):
            current_end = day_events[i]["end"]
            next_start = day_events[i + 1]["start"]
            gap_minutes = (next_start - current_end).total_seconds() / 60
            
            if gap_minutes < 15:  # Less than 15 minutes gap = back-to-back
                back_to_back_count += 1
    
    # Find longest gap between meetings
    longest_gap = {"day": None, "hours": 0.0}
    for day, day_events in events_by_day.items():
        if len(day_events) < 2:
            continue
        
        for i in range(len(day_events) - 1):
            current_end = day_events[i]["end"]
            next_start = day_events[i + 1]["start"]
            gap_hours = (next_start - current_end).total_seconds() / 3600
            
            if gap_hours > longest_gap["hours"]:
                longest_gap = {"day": day, "hours": gap_hours}
    
    return {
        "meeting_count": meeting_count,
        "total_hours": round(total_hours, 1),
        "avg_meeting_length": round(avg_meeting_length, 1),
        "fragmentation_by_day": fragmentation_by_day,
        "back_to_back_count": back_to_back_count,
        "busiest_day": busiest_day,
        "quietest_day": quietest_day,
        "longest_gap": longest_gap,
        "excluded_count": excluded_count
    }


def calculate_fragmentation(day_events: list[dict], work_start=9, work_end=18) -> float:
    """
    Fragmentation = 1 - (largest_uninterrupted_block / total_work_hours)
    Higher score = more fragmented day
    """
    if not day_events:
        return 0.0
    
    work_start_time = work_start * 60  # Convert to minutes from midnight
    work_end_time = work_end * 60
    total_work_minutes = (work_end - work_start) * 60
    
    # Convert events to minutes from midnight
    meeting_blocks = []
    for event in day_events:
        start_minutes = event["start"].hour * 60 + event["start"].minute
        end_minutes = event["end"].hour * 60 + event["end"].minute
        
        # Only count meetings within work hours
        start_minutes = max(start_minutes, work_start_time)
        end_minutes = min(end_minutes, work_end_time)
        
        if start_minutes < end_minutes:
            meeting_blocks.append((start_minutes, end_minutes))
    
    if not meeting_blocks:
        return 0.0
    
    # Sort and merge overlapping blocks
    meeting_blocks.sort()
    merged_blocks = [meeting_blocks[0]]
    
    for start, end in meeting_blocks[1:]:
        last_start, last_end = merged_blocks[-1]
        if start <= last_end:  # Overlapping or adjacent
            merged_blocks[-1] = (last_start, max(last_end, end))
        else:
            merged_blocks.append((start, end))
    
    # Find largest gap between meetings (or before/after meetings)
    gaps = []
    
    # Gap before first meeting
    first_meeting_start = merged_blocks[0][0]
    if first_meeting_start > work_start_time:
        gaps.append(first_meeting_start - work_start_time)
    
    # Gaps between meetings
    for i in range(len(merged_blocks) - 1):
        gap_start = merged_blocks[i][1]
        gap_end = merged_blocks[i + 1][0]
        gaps.append(gap_end - gap_start)
    
    # Gap after last meeting
    last_meeting_end = merged_blocks[-1][1]
    if last_meeting_end < work_end_time:
        gaps.append(work_end_time - last_meeting_end)
    
    # Find largest gap
    largest_gap = max(gaps) if gaps else 0
    
    # Calculate fragmentation score
    fragmentation = 1.0 - (largest_gap / total_work_minutes)
    return max(0.0, min(1.0, fragmentation))  # Clamp to 0-1


def main():
    """CLI test mode - shows sample metrics with dummy data."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=== Calendar Metrics Test ===\n")
        
        # Create sample events for testing
        sample_events = [
            {
                "title": "Daily Centering Task",
                "start": "2026-01-19T08:15:00-05:00",
                "end": "2026-01-19T08:30:00-05:00",
                "duration_min": 15,
                "description": "",
                "is_all_day": False
            },
            {
                "title": "Chat with Ben (Zo cofounder)",
                "start": "2026-01-19T15:00:00-05:00",
                "end": "2026-01-19T15:30:00-05:00",
                "duration_min": 30,
                "description": "Booked by Vrijen Attawar",
                "is_all_day": False
            },
            {
                "title": "BLOCK",
                "start": "2026-01-19T16:00:00-05:00",
                "end": "2026-01-19T17:30:00-05:00",
                "duration_min": 90,
                "description": "",
                "is_all_day": False
            }
        ]
        
        print(f"Testing with {len(sample_events)} sample events...")
        
        try:
            # Test filtering
            real_meetings = [event for event in sample_events if is_real_meeting(event)]
            print(f"Real meetings after filtering: {len(real_meetings)}")
            
            # Calculate metrics
            metrics = calculate_metrics(sample_events)
            print("\n--- Calculated Metrics ---")
            print(json.dumps(metrics, indent=2))
            
            print(f"\n✓ Test completed successfully")
            
        except Exception as e:
            print(f"Error during test: {e}")
            sys.exit(1)
    else:
        print("Usage: python3 calendar_metrics.py --test")
        print("\nThis module provides calendar metrics calculation for the performance dashboard.")
        print("Functions available:")
        print("- process_calendar_events(raw_events)")
        print("- is_real_meeting(event)")
        print("- calculate_metrics(events)")
        print("- calculate_fragmentation(day_events)")


if __name__ == "__main__":
    main()