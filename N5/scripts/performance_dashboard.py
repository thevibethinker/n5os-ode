#!/usr/bin/env python3
"""
Weekly Performance Intelligence Dashboard v2

Generates a comprehensive weekly performance report integrating:
- Vitals (RHR, sleep, activity, workouts)
- Calendar load (meetings, fragmentation, back-to-back)
- Cognitive/output (tasks, content consumption)
- Environment (weather)
- Automated signals detection
- Data quality monitoring
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

# Import data access layer
sys.path.insert(0, str(Path(__file__).parent))
import performance_data

# ═══════════════════════════════════════════════════════════════════
# FORMATTING HELPERS
# ═══════════════════════════════════════════════════════════════════

SPARK_CHARS = "▁▂▃▄▅▆▇█"
BOX_WIDTH = 70

def sparkline(values: list, width: int = 7) -> str:
    """Generate ASCII sparkline from values."""
    if not values:
        return "░" * width
    
    # Extract numeric values if list of dicts
    if values and isinstance(values[0], dict):
        values = [v.get('value', v.get('hours', v.get('steps', 0))) for v in values]
    
    # Take last `width` values
    values = values[-width:]
    
    if not values or all(v == 0 for v in values):
        return "░" * len(values)
    
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return SPARK_CHARS[4] * len(values)
    
    return "".join(
        SPARK_CHARS[min(7, int((v - min_v) / (max_v - min_v) * 7))]
        for v in values
    )


def trend_arrow(trend: str) -> str:
    """Convert trend string to arrow."""
    return {"up": "↑", "down": "↓", "stable": "→"}.get(trend, "→")


def progress_bar(value: float, max_value: float, width: int = 10) -> str:
    """Generate progress bar like [████████░░]."""
    if max_value <= 0:
        return "[" + "░" * width + "]"
    
    filled = min(width, int((value / max_value) * width))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def format_box(title: str, lines: list[str]) -> str:
    """Format content in a bordered box with title."""
    result = []
    result.append(f"┌─ {title} " + "─" * (BOX_WIDTH - len(title) - 4) + "┐")
    result.append("│" + " " * BOX_WIDTH + "│")
    
    for line in lines:
        # Pad line to box width
        padded = f"  {line}"
        if len(padded) < BOX_WIDTH:
            padded = padded + " " * (BOX_WIDTH - len(padded))
        elif len(padded) > BOX_WIDTH:
            padded = padded[:BOX_WIDTH-3] + "..."
        result.append("│" + padded + "│")
    
    result.append("│" + " " * BOX_WIDTH + "│")
    result.append("└" + "─" * BOX_WIDTH + "┘")
    return "\n".join(result)


def workout_bar(count: int, days: int = 7) -> str:
    """Generate workout visualization: █░█░█░░"""
    if count >= days:
        return "█" * days
    return "█░" * count + "░" * (days - count * 2) if count * 2 <= days else "█" * count + "░" * (days - count)


# ═══════════════════════════════════════════════════════════════════
# SIGNAL DETECTION
# ═══════════════════════════════════════════════════════════════════

def detect_signals(data: dict) -> list[str]:
    """Detect anomalies and generate signals/warnings."""
    signals = []
    
    # RHR signals
    rhr = data.get('resting_hr', {})
    if rhr.get('data_points', 0) > 0:
        daily = rhr.get('daily_values', [])
        if daily:
            values = [d.get('value', 0) for d in daily]
            avg = rhr.get('avg', 0)
            # Check for spikes
            for i, d in enumerate(daily):
                if d.get('value', 0) > avg + 5:
                    day_name = datetime.strptime(d['date'], '%Y-%m-%d').strftime('%a')
                    signals.append(f"⚠️  RHR elevated on {day_name} ({d['value']} vs {avg:.0f} avg)")
                    break
        
        if rhr.get('trend') == 'up':
            signals.append(f"⚠️  RHR trending up vs last week")
    
    # Sleep signals
    sleep = data.get('sleep', {})
    if sleep.get('data_points', 0) > 0:
        for d in sleep.get('daily_values', []):
            if d.get('hours', 0) < 6:
                day_name = datetime.strptime(d['date'], '%Y-%m-%d').strftime('%a')
                signals.append(f"⚠️  Low sleep on {day_name} ({d['hours']:.1f} hrs)")
                break
    
    # Calendar signals
    calendar = data.get('calendar', {})
    if calendar.get('data_points', 0) > 0:
        if calendar.get('fragmentation_avg', 0) > 0.6:
            signals.append(f"⚠️  High calendar fragmentation ({calendar['fragmentation_avg']:.2f})")
        
        if calendar.get('back_to_back_count', 0) >= 3:
            signals.append(f"⚠️  Meeting overload: {calendar['back_to_back_count']} back-to-back instances")
    
    # Task signals
    tasks = data.get('tasks', {})
    if tasks.get('added', 0) > 0:
        rate = tasks.get('completion_rate', 0)
        if rate < 50:
            signals.append(f"⚠️  Low task completion rate ({rate:.0f}%)")
    
    # Positive signals
    activity = data.get('activity', {})
    if activity.get('data_points', 0) > 0:
        if activity.get('steps_avg', 0) > 8000:
            signals.append(f"✓  Strong activity week ({activity['steps_avg']:,} steps/day avg)")
        if activity.get('workout_count', 0) >= 3:
            signals.append(f"✓  Good workout consistency ({activity['workout_count']} sessions)")
    
    # net_change > 0 means completing more than adding (clearing backlog)
    if tasks.get('net_change', 0) > 0:
        signals.append(f"✓  Clearing backlog (net {tasks['net_change']:+d} tasks)")
    
    if sleep.get('avg_hours', 0) >= 7:
        signals.append(f"✓  Solid sleep average ({sleep['avg_hours']:.1f} hrs)")
    
    return signals[:6]  # Limit to 6 signals


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD SECTIONS
# ═══════════════════════════════════════════════════════════════════

def render_header(week_start: date) -> str:
    """Render dashboard header."""
    # Week is backwards-looking: week_start is the Monday, week_end is the Sunday (yesterday or earlier)
    week_end = week_start + timedelta(days=6)  # Sunday of that week
    
    header = f"""════════════════════════════════════════════════════════════════════════
  WEEKLY PERFORMANCE INTELLIGENCE  │  {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')} (Last Week)     
═════════════════════════════════════════════════════════════════════════"""
    return header


def render_vitals(data: dict) -> str:
    """Render vitals section."""
    rhr = data.get('resting_hr', {})
    sleep = data.get('sleep', {})
    activity = data.get('activity', {})
    
    # RHR line
    rhr_spark = sparkline(rhr.get('daily_values', []))
    rhr_trend = trend_arrow(rhr.get('trend', 'stable'))
    rhr_line = f"Resting HR      {rhr.get('avg', 0):.0f} bpm avg    {rhr_spark}    {rhr_trend} vs last week"
    
    # Sleep line
    sleep_spark = sparkline(sleep.get('daily_values', []))
    sleep_trend = trend_arrow('stable')  # Would need trend calculation
    sleep_line = f"Sleep           {sleep.get('avg_hours', 0):.1f} hrs avg   {sleep_spark}    {sleep_trend} stable"
    
    # Activity line
    activity_spark = sparkline(activity.get('daily_values', []))
    activity_line = f"Activity        {activity.get('steps_avg', 0):,} steps   {activity_spark}"
    
    # Workouts line
    workout_viz = workout_bar(activity.get('workout_count', 0))
    workout_line = f"Workouts        {activity.get('workout_count', 0)} sessions    {workout_viz}"
    
    return format_box("VITALS", [rhr_line, sleep_line, activity_line, workout_line])


def render_calendar(data: dict) -> str:
    """Render calendar load section."""
    cal = data.get('calendar', {})
    
    meeting_count = cal.get('meeting_count', 0)
    total_hours = cal.get('total_hours', 0)
    
    # Assume 40hr work week for percentage
    work_pct = min(100, int(total_hours / 40 * 100))
    meetings_bar = progress_bar(total_hours, 40, 10)
    meetings_line = f"Meetings        {meeting_count} ({total_hours:.1f} hrs)   {meetings_bar} {work_pct}% of work time"
    
    frag = cal.get('fragmentation_avg', 0)
    frag_level = "HIGH" if frag > 0.6 else "MED" if frag > 0.4 else "LOW"
    busiest = cal.get('busiest_day', 'N/A')
    frag_line = f"Fragmentation   {frag:.2f} ({frag_level})    Most fragmented: {busiest}"
    
    b2b = cal.get('back_to_back_count', 0)
    gap = cal.get('longest_gap', {})
    gap_str = f"{gap.get('hours', 0):.1f} hrs" if gap.get('hours') else "N/A"
    # Convert ISO date to abbreviated weekday name
    gap_day_raw = gap.get('day', '')
    if gap_day_raw:
        try:
            gap_day = datetime.strptime(gap_day_raw, '%Y-%m-%d').strftime('%a')
        except ValueError:
            gap_day = gap_day_raw[:3]  # Fallback to first 3 chars
    else:
        gap_day = ''
    gap_window = gap.get('window', '')
    b2b_line = f"Back-to-back    {b2b} instances    Longest gap: {gap_str} ({gap_day} {gap_window})"
    
    excluded = cal.get('excluded_count', 0)
    excluded_line = f"Excluded: {excluded} events tagged [SKIP]" if excluded > 0 else ""
    
    lines = [meetings_line, frag_line, b2b_line]
    if excluded_line:
        lines.append(excluded_line)
    
    return format_box("CALENDAR LOAD", lines)


def render_cognitive(data: dict) -> str:
    """Render cognitive/output section."""
    tasks = data.get('tasks', {})
    content = data.get('content', {})
    
    completed = tasks.get('completed', 0)
    added = tasks.get('added', 0)
    rate = tasks.get('completion_rate', 0)
    tasks_line = f"Tasks Completed    {completed} of {added + completed} due    ({rate:.0f}% completion rate)"
    
    net = tasks.get('net_change', 0)
    # net_change = completed - added: positive means clearing, negative means growing
    net_str = f"Net: {net:+d}" + (" (clearing backlog)" if net > 0 else " (adding to backlog)" if net < 0 else "")
    added_line = f"Tasks Added        {added} new          {net_str}"
    
    pending = tasks.get('pending_total', 0)
    pending_line = f"Pending Backlog    {pending} tasks"
    
    # Content consumption
    items = content.get('items_added', 0)
    by_type = content.get('by_type', {})
    type_breakdown = ", ".join(f"{v} {k}s" for k, v in by_type.items()) if by_type else "none"
    content_line = f"Content Consumed   {items} items        {type_breakdown}"
    
    return format_box("COGNITIVE/OUTPUT", [tasks_line, added_line, pending_line, content_line])


def render_environment(data: dict) -> str:
    """Render environment section."""
    weather = data.get('weather', {})
    
    avg_high = weather.get('avg_high', 0)
    avg_low = weather.get('avg_low', 0)
    avg_temp = (avg_high + avg_low) / 2 if avg_high or avg_low else 0
    
    conditions = weather.get('conditions_summary', {})
    main_condition = max(conditions.keys(), key=conditions.get) if conditions else "Unknown"
    
    # Precipitation from Open-Meteo is in mm - convert to inches
    precip_mm = weather.get("total_precipitation", 0)
    precip_in = precip_mm / 25.4
    
    # Weather emoji
    emoji = "☀️" if "Clear" in main_condition or "Sunny" in main_condition else \
            "🌧️" if "Rain" in main_condition else \
            "🌨️" if "Snow" in main_condition else \
            "☁️"
    
    # Note: precip from API is in mm, convert display
    weather_line = f"Weather (NYC)   {avg_temp:.0f}°F avg   {emoji} {main_condition}, {precip_in:.1f}\" precip"
    
    return format_box("ENVIRONMENT", [weather_line])


def render_signals(signals: list[str]) -> str:
    """Render signals section."""
    if not signals:
        signals = ["✓  All metrics within normal ranges"]
    
    return format_box("SIGNALS", signals)


def render_data_quality(data: dict) -> str:
    """Render data quality section."""
    freshness = data.get('freshness', {})
    
    def status_icon(source_data):
        if not source_data or source_data.get('status') == 'missing':
            return "✗"
        days = source_data.get('days_stale', 0)
        if days is None or days > 2:
            return "⚠️"
        return "✓"
    
    def coverage(data_dict):
        dp = data_dict.get('data_points', 0)
        if dp >= 7:
            return f"✓ {dp}/7 days"
        elif dp > 0:
            return f"⚠️ {dp}/7 days"
        return "✗ no data"
    
    rhr_cov = coverage(data.get('resting_hr', {}))
    sleep_cov = coverage(data.get('sleep', {}))
    tasks_status = "✓" if data.get('tasks', {}).get('completed', 0) > 0 or data.get('tasks', {}).get('pending_total', 0) > 0 else "⚠️"
    cal_status = "✓" if data.get('calendar', {}).get('data_points', 0) > 0 else "⚠️"
    weather_status = "✓" if data.get('weather', {}).get('data_points', 0) > 0 else "⚠️"
    content_status = "✓" if data.get('content', {}).get('items_added', 0) >= 0 else "⚠️"
    
    line = f"Resting HR: {rhr_cov}  │  Sleep: {sleep_cov}  │  Tasks: {tasks_status}"
    line2 = f"Calendar: {cal_status}             │  Weather: {weather_status}          │  Content: {content_status}"
    
    return format_box("DATA QUALITY", [line, line2])


# ═══════════════════════════════════════════════════════════════════
# MAIN GENERATION
# ═══════════════════════════════════════════════════════════════════

def gather_data(days: int = 7) -> dict:
    """Gather all data from performance_data module."""
    return {
        'resting_hr': performance_data.get_weekly_resting_hr(days),
        'activity': performance_data.get_weekly_activity(days),
        'sleep': performance_data.get_weekly_sleep(days),
        'tasks': performance_data.get_weekly_tasks(days),
        'content': performance_data.get_weekly_content(days),
        'mood': performance_data.get_weekly_mood(days),
        'calendar': performance_data.get_weekly_calendar(days),
        'weather': performance_data.get_weekly_weather(days),
        'freshness': performance_data.get_data_freshness(),
    }


def generate_dashboard(week_start: datetime = None, debug: bool = False) -> str:
    """Generate the full dashboard."""
    if week_start is None:
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    
    week_end = week_start + timedelta(days=6)
    
    # Gather data
    data = gather_data(7)
    
    if debug:
        import json
        print("=== DEBUG: Raw Data ===")
        print(json.dumps(data, indent=2, default=str))
        print("=" * 50)
    
    # Detect signals
    signals = detect_signals(data)
    
    # Render sections
    sections = [
        render_header(week_start),
        "",
        render_vitals(data),
        "",
        render_calendar(data),
        "",
        render_cognitive(data),
        "",
        render_environment(data),
        "",
        render_signals(signals),
        "",
        render_data_quality(data),
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} ET"
    ]
    
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Generate Weekly Performance Dashboard")
    parser.add_argument("--week", help="Week start date (YYYY-MM-DD, defaults to LAST week's Monday)")
    parser.add_argument("--debug", action="store_true", help="Print raw data")
    parser.add_argument("--output", help="Custom output path")
    args = parser.parse_args()
    
    # Determine week start (Monday of LAST week by default - backwards-looking)
    if args.week:
        week_start = datetime.strptime(args.week, "%Y-%m-%d").date()
    else:
        # Default to LAST week (the 7 days ending yesterday)
        yesterday = date.today() - timedelta(days=1)
        # Find the Monday of that week
        week_start = yesterday - timedelta(days=yesterday.weekday())
        # If yesterday was a Sunday, we want the week that just ended
        # If yesterday was any other day, we still want the most recent complete week
    
    # Generate dashboard
    dashboard = generate_dashboard(week_start, args.debug)
    print(dashboard)
    
    # Save to file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("/home/workspace/Personal/Health/Reports") / f"Performance_Dashboard_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
