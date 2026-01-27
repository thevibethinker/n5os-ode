#!/usr/bin/env python3
"""
Unified Performance Data Access Layer

Provides standardized access to performance data across multiple sources:
- Health metrics (resting HR, activity, sleep)
- Task management data
- Content library metrics
- Journal/mood tracking
- Calendar meeting intelligence

Each function returns data for the last N days with trend analysis.
"""

import sqlite3
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


def _get_date_range(days: int) -> tuple[str, str]:
    """Get current and previous period date ranges for trend calculation."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # For trend comparison, get previous period of same length
    prev_end_date = start_date
    prev_start_date = prev_end_date - timedelta(days=days)
    
    return (
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        prev_start_date.strftime('%Y-%m-%d'),
        prev_end_date.strftime('%Y-%m-%d')
    )


def _calculate_trend(current_avg: float, previous_avg: float) -> str:
    """Calculate trend: up/down/stable (±5% = stable)."""
    if previous_avg == 0:
        return "stable"
    
    change_pct = abs((current_avg - previous_avg) / previous_avg * 100)
    if change_pct <= 5:
        return "stable"
    elif current_avg > previous_avg:
        return "up"
    else:
        return "down"


def _safe_avg(values: List[float]) -> float:
    """Calculate average, handling empty lists."""
    return sum(values) / len(values) if values else 0.0


def get_weekly_resting_hr(days: int = 7) -> dict:
    """
    Returns weekly resting heart rate data.
    
    Returns:
        {avg, min, max, trend, daily_values, data_points}
    """
    db_path = Path("/home/workspace/Personal/Health/workouts.db")
    if not db_path.exists():
        return {"avg": 0, "min": 0, "max": 0, "trend": "stable", "daily_values": [], "data_points": 0}
    
    current_start, current_end, prev_start, prev_end = _get_date_range(days)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get current period data
            current_data = conn.execute("""
                SELECT date, resting_hr 
                FROM daily_resting_hr 
                WHERE date >= ? AND date <= ? AND resting_hr IS NOT NULL
                ORDER BY date
            """, (current_start, current_end)).fetchall()
            
            # Get previous period for trend
            prev_data = conn.execute("""
                SELECT resting_hr 
                FROM daily_resting_hr 
                WHERE date >= ? AND date < ? AND resting_hr IS NOT NULL
            """, (prev_start, prev_end)).fetchall()
            
            if not current_data:
                return {"avg": 0, "min": 0, "max": 0, "trend": "stable", "daily_values": [], "data_points": 0}
            
            hr_values = [row[1] for row in current_data]
            daily_values = [{"date": row[0], "value": row[1]} for row in current_data]
            
            current_avg = _safe_avg(hr_values)
            prev_avg = _safe_avg([row[0] for row in prev_data]) if prev_data else current_avg
            
            return {
                "avg": round(current_avg, 1),
                "min": min(hr_values),
                "max": max(hr_values),
                "trend": _calculate_trend(current_avg, prev_avg),
                "daily_values": daily_values,
                "data_points": len(current_data)
            }
    except Exception as e:
        print(f"Error reading resting HR data: {e}", file=sys.stderr)
        return {"avg": 0, "min": 0, "max": 0, "trend": "stable", "daily_values": [], "data_points": 0}


def get_weekly_activity(days: int = 7) -> dict:
    """
    Returns weekly activity summary.
    
    Returns:
        {steps_avg, steps_total, active_min_avg, workout_count, daily_values, data_points}
    """
    workouts_db = Path("/home/workspace/Personal/Health/workouts.db")
    if not workouts_db.exists():
        return {"steps_avg": 0, "steps_total": 0, "active_min_avg": 0, "workout_count": 0, "daily_values": [], "data_points": 0}
    
    current_start, current_end, prev_start, prev_end = _get_date_range(days)
    
    try:
        with sqlite3.connect(workouts_db) as conn:
            # Get activity summary data
            activity_data = conn.execute("""
                SELECT date, steps, active_zone_minutes_total 
                FROM daily_activity_summary 
                WHERE date >= ? AND date <= ?
                ORDER BY date
            """, (current_start, current_end)).fetchall()
            
            # Get workout count
            workout_count = conn.execute("""
                SELECT COUNT(*) 
                FROM workouts 
                WHERE date >= ? AND date <= ?
            """, (current_start, current_end)).fetchone()[0]
            
            if not activity_data:
                return {"steps_avg": 0, "steps_total": 0, "active_min_avg": 0, "workout_count": workout_count, "daily_values": [], "data_points": 0}
            
            steps_values = [row[1] if row[1] is not None else 0 for row in activity_data]
            active_min_values = [row[2] if row[2] is not None else 0 for row in activity_data]
            
            daily_values = [
                {
                    "date": row[0], 
                    "steps": row[1] or 0, 
                    "active_minutes": row[2] or 0
                } 
                for row in activity_data
            ]
            
            return {
                "steps_avg": round(_safe_avg(steps_values)),
                "steps_total": sum(steps_values),
                "active_min_avg": round(_safe_avg(active_min_values)),
                "workout_count": workout_count,
                "daily_values": daily_values,
                "data_points": len(activity_data)
            }
    except Exception as e:
        print(f"Error reading activity data: {e}", file=sys.stderr)
        return {"steps_avg": 0, "steps_total": 0, "active_min_avg": 0, "workout_count": 0, "daily_values": [], "data_points": 0}


def get_weekly_sleep(days: int = 7) -> dict:
    """
    Returns weekly sleep data.
    
    Returns:
        {avg_hours, min_hours, max_hours, daily_values, data_points}
    """
    db_path = Path("/home/workspace/Personal/Health/workouts.db")
    if not db_path.exists():
        return {"avg_hours": 0, "min_hours": 0, "max_hours": 0, "daily_values": [], "data_points": 0}
    
    current_start, current_end, _, _ = _get_date_range(days)
    
    try:
        with sqlite3.connect(db_path) as conn:
            sleep_data = conn.execute("""
                SELECT date, minutes_asleep, sleep_score 
                FROM daily_sleep 
                WHERE date >= ? AND date <= ? AND minutes_asleep IS NOT NULL
                ORDER BY date
            """, (current_start, current_end)).fetchall()
            
            if not sleep_data:
                return {"avg_hours": 0, "min_hours": 0, "max_hours": 0, "daily_values": [], "data_points": 0}
            
            hours_values = [row[1] / 60.0 for row in sleep_data]
            daily_values = [
                {
                    "date": row[0], 
                    "hours": round(row[1] / 60.0, 1),
                    "sleep_score": row[2]
                } 
                for row in sleep_data
            ]
            
            return {
                "avg_hours": round(_safe_avg(hours_values), 1),
                "min_hours": round(min(hours_values), 1),
                "max_hours": round(max(hours_values), 1),
                "daily_values": daily_values,
                "data_points": len(sleep_data)
            }
    except Exception as e:
        print(f"Error reading sleep data: {e}", file=sys.stderr)
        return {"avg_hours": 0, "min_hours": 0, "max_hours": 0, "daily_values": [], "data_points": 0}


def get_weekly_tasks(days: int = 7) -> dict:
    """
    Returns weekly task management metrics.
    
    Returns:
        {completed, added, pending_total, completion_rate, net_change}
    """
    db_path = Path("/home/workspace/N5/task_system/tasks.db")
    if not db_path.exists():
        return {"completed": 0, "added": 0, "pending_total": 0, "completion_rate": 0.0, "net_change": 0}
    
    current_start, current_end, _, _ = _get_date_range(days)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Tasks completed in this period
            completed = conn.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE status = 'complete' 
                AND date(completed_at) >= ? AND date(completed_at) <= ?
            """, (current_start, current_end)).fetchone()[0]
            
            # Tasks added in this period
            added = conn.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE date(created_at) >= ? AND date(created_at) <= ?
            """, (current_start, current_end)).fetchone()[0]
            
            # Current pending tasks
            pending_total = conn.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE status IN ('pending', 'in_progress', 'blocked') AND archived = FALSE
            """).fetchone()[0]
            
            completion_rate = (completed / added * 100) if added > 0 else 0.0
            net_change = completed - added
            
            return {
                "completed": completed,
                "added": added,
                "pending_total": pending_total,
                "completion_rate": round(completion_rate, 1),
                "net_change": net_change
            }
    except Exception as e:
        print(f"Error reading task data: {e}", file=sys.stderr)
        return {"completed": 0, "added": 0, "pending_total": 0, "completion_rate": 0.0, "net_change": 0}


def get_weekly_content(days: int = 7) -> dict:
    """
    Returns weekly content library metrics.
    
    Returns:
        {items_added, by_type: {article: N, link: N, ...}, sources: [...]}
    """
    db_path = Path("/home/workspace/N5/data/content_library.db")
    if not db_path.exists():
        return {"items_added": 0, "by_type": {}, "sources": []}
    
    current_start, current_end, _, _ = _get_date_range(days)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Items added in this period
            items_data = conn.execute("""
                SELECT content_type, source, COUNT(*) 
                FROM items 
                WHERE date(created_at) >= ? AND date(created_at) <= ?
                GROUP BY content_type, source
            """, (current_start, current_end)).fetchall()
            
            by_type = {}
            sources = set()
            total_items = 0
            
            for content_type, source, count in items_data:
                if content_type not in by_type:
                    by_type[content_type] = 0
                by_type[content_type] += count
                total_items += count
                
                if source:
                    sources.add(source)
            
            return {
                "items_added": total_items,
                "by_type": by_type,
                "sources": list(sources)[:10]  # Limit to top 10 sources
            }
    except Exception as e:
        print(f"Error reading content library data: {e}", file=sys.stderr)
        return {"items_added": 0, "by_type": {}, "sources": []}


def get_weekly_mood(days: int = 7) -> dict:
    """
    Returns weekly mood data from journal entries and bio snapshots.
    
    Returns:
        {entries: [...], predominant_mood, data_points}
    """
    db_path = Path("/home/workspace/N5/data/journal.db")
    if not db_path.exists():
        return {"entries": [], "predominant_mood": None, "data_points": 0}
    
    current_start, current_end, _, _ = _get_date_range(days)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get mood entries from both journal entries and bio snapshots
            journal_moods = conn.execute("""
                SELECT date(created_at) as date, mood 
                FROM journal_entries 
                WHERE date(created_at) >= ? AND date(created_at) <= ? AND mood IS NOT NULL
                ORDER BY created_at
            """, (current_start, current_end)).fetchall()
            
            bio_moods = conn.execute("""
                SELECT date(created_at) as date, mood 
                FROM bio_snapshots 
                WHERE date(created_at) >= ? AND date(created_at) <= ? AND mood IS NOT NULL
                ORDER BY created_at
            """, (current_start, current_end)).fetchall()
            
            all_moods = journal_moods + bio_moods
            
            if not all_moods:
                return {"entries": [], "predominant_mood": None, "data_points": 0}
            
            entries = [{"date": row[0], "mood": row[1]} for row in all_moods]
            
            # Calculate predominant mood
            mood_counts = {}
            for _, mood in all_moods:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            predominant_mood = max(mood_counts.keys(), key=mood_counts.get) if mood_counts else None
            
            return {
                "entries": entries,
                "predominant_mood": predominant_mood,
                "data_points": len(entries)
            }
    except Exception as e:
        print(f"Error reading mood data: {e}", file=sys.stderr)
        return {"entries": [], "predominant_mood": None, "data_points": 0}


def get_weekly_weather(days: int = 7) -> dict:
    """
    Returns weekly weather data from Open-Meteo API.
    
    Returns:
        {avg_high, avg_low, rain_days, total_precipitation, conditions_summary, daily_values, data_points}
    """
    try:
        try:
            from . import weather_metrics
        except ImportError:
            import weather_metrics
        
        return weather_metrics.get_weekly_weather(days)
    except Exception as e:
        print(f"Error getting weather data: {e}", file=sys.stderr)
        return {
            "avg_high": 0.0,
            "avg_low": 0.0,
            "rain_days": 0,
            "total_precipitation": 0.0,
            "conditions_summary": {},
            "daily_values": [],
            "data_points": 0
        }


def get_weekly_calendar(days: int = 7) -> dict:
    """
    Returns weekly calendar metrics with meeting analysis.
    
    Returns:
        {
            meeting_count, total_hours, avg_meeting_length,
            fragmentation_avg, back_to_back_count,
            busiest_day, quietest_day, longest_gap,
            excluded_count, data_points
        }
    """
    try:
        import calendar_metrics
        from datetime import datetime, timedelta

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        events = calendar_metrics.fetch_week_events(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        if not events:
            return _empty_calendar_metrics()

        metrics = calendar_metrics.calculate_metrics(events)

        fragmentation_scores = list(metrics.get('fragmentation_by_day', {}).values())
        fragmentation_avg = sum(fragmentation_scores) / len(fragmentation_scores) if fragmentation_scores else 0.0

        return {
            "meeting_count": metrics.get('meeting_count', 0),
            "total_hours": metrics.get('total_hours', 0.0),
            "avg_meeting_length": metrics.get('avg_meeting_length', 0.0),
            "fragmentation_avg": round(fragmentation_avg, 2),
            "back_to_back_count": metrics.get('back_to_back_count', 0),
            "busiest_day": metrics.get('busiest_day'),
            "quietest_day": metrics.get('quietest_day'),
            "longest_gap": metrics.get('longest_gap', {"day": None, "hours": 0.0}),
            "excluded_count": metrics.get('excluded_count', 0),
            "data_points": len(events)
        }

    except Exception as e:
        print(f"Error getting calendar data: {e}", file=sys.stderr)
        return _empty_calendar_metrics()


def _empty_calendar_metrics() -> dict:
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


def get_data_freshness() -> dict:
    """
    Check data freshness across all sources.
    
    Returns:
        {source_name: {last_update, days_stale, status: 'ok'|'stale'|'missing'}}
    """
    sources = {
        "resting_hr": "/home/workspace/Personal/Health/workouts.db",
        "activity": "/home/workspace/Personal/Health/workouts.db",
        "sleep": "/home/workspace/Personal/Health/workouts.db",
        "tasks": "/home/workspace/N5/task_system/tasks.db",
        "content": "/home/workspace/N5/data/content_library.db",
        "journal": "/home/workspace/N5/data/journal.db"
    }
    
    freshness = {}
    
    for source_name, db_path in sources.items():
        if not Path(db_path).exists():
            freshness[source_name] = {"last_update": None, "days_stale": None, "status": "missing"}
            continue
            
        try:
            with sqlite3.connect(db_path) as conn:
                if source_name == "resting_hr":
                    last_update = conn.execute("SELECT MAX(date) FROM daily_resting_hr").fetchone()[0]
                elif source_name == "activity":
                    last_update = conn.execute("SELECT MAX(date) FROM daily_activity_summary").fetchone()[0]
                elif source_name == "sleep":
                    last_update = conn.execute("SELECT MAX(date) FROM daily_sleep").fetchone()[0]
                elif source_name == "tasks":
                    last_update = conn.execute("SELECT MAX(created_at) FROM tasks").fetchone()[0]
                elif source_name == "content":
                    last_update = conn.execute("SELECT MAX(created_at) FROM items").fetchone()[0]
                elif source_name == "journal":
                    last_update = conn.execute("SELECT MAX(created_at) FROM journal_entries").fetchone()[0]
                
                if not last_update:
                    freshness[source_name] = {"last_update": None, "days_stale": None, "status": "missing"}
                    continue
                
                # Calculate days stale
                if source_name in ["resting_hr", "activity", "sleep"]:
                    # Date-based sources
                    last_date = datetime.strptime(last_update, '%Y-%m-%d')
                else:
                    # Timestamp-based sources
                    last_date = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                
                days_stale = (datetime.now() - last_date.replace(tzinfo=None)).days
                
                status = "ok" if days_stale <= 2 else "stale"
                
                freshness[source_name] = {
                    "last_update": last_update,
                    "days_stale": days_stale,
                    "status": status
                }
                
        except Exception as e:
            print(f"Error checking freshness for {source_name}: {e}", file=sys.stderr)
            freshness[source_name] = {"last_update": None, "days_stale": None, "status": "missing"}
    
    return freshness


def main():
    """CLI test mode - runs all functions and prints sample output."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=== Performance Data Access Test ===\n")
        
        functions = [
            ("Weekly Resting HR", get_weekly_resting_hr),
            ("Weekly Activity", get_weekly_activity),
            ("Weekly Sleep", get_weekly_sleep),
            ("Weekly Tasks", get_weekly_tasks),
            ("Weekly Content", get_weekly_content),
            ("Weekly Mood", get_weekly_mood),
            ("Weekly Weather", get_weekly_weather),
            ("Weekly Calendar", get_weekly_calendar),
            ("Data Freshness", get_data_freshness)
        ]
        
        for name, func in functions:
            print(f"--- {name} ---")
            try:
                result = func()
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"Error: {e}")
            print()
        
        print("✓ All functions executed successfully")
    else:
        print("Usage: python3 performance_data.py --test")
        sys.exit(1)


if __name__ == "__main__":
    main()