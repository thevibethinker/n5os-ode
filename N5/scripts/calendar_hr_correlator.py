#!/usr/bin/env python3
"""
Calendar-HR Correlator - Correlates Google Calendar meetings with heart rate data.

Analyzes HR patterns before, during, and after meetings to identify:
- Which meetings/people cause stress spikes
- Time-of-day patterns
- Recovery patterns after high-stress meetings

Usage:
    python3 calendar_hr_correlator.py sync --days 30    # Sync calendar events with HR
    python3 calendar_hr_correlator.py report            # Show meeting HR report
    python3 calendar_hr_correlator.py people            # Show per-person HR patterns
    python3 calendar_hr_correlator.py trends            # Show trends over time

provenance: con_wne5ccsJoVnFSW6f
"""

import argparse
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, stdev

# Paths
WORKOUTS_DB = Path("/home/workspace/Personal/Health/workouts.db")
PERFORMANCE_DB = Path("/home/workspace/N5/data/performance.db")

# Classification thresholds
HR_SPIKE_THRESHOLD = 8      # +8 bpm = moderate activation
HR_HIGH_THRESHOLD = 15      # +15 bpm = high activation
RECOVERY_WINDOW_MIN = 15    # Minutes to check post-meeting
BASELINE_WINDOW_MIN = 10    # Minutes before meeting for baseline


def init_db():
    """Initialize performance database with meeting HR correlation tables."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_hr_correlation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            event_date DATE,
            event_start_time TEXT,
            event_end_time TEXT,
            event_title TEXT,
            event_duration_min INTEGER,
            attendees TEXT,
            organizer TEXT,
            
            -- HR Metrics
            hr_baseline REAL,
            hr_baseline_samples INTEGER,
            hr_during_avg REAL,
            hr_during_max REAL,
            hr_during_min REAL,
            hr_during_samples INTEGER,
            hr_after_avg REAL,
            hr_after_samples INTEGER,
            
            -- Derived Metrics
            hr_delta REAL,              -- during_avg - baseline
            hr_spike_max REAL,          -- during_max - baseline
            recovery_delta REAL,        -- after_avg - during_avg (negative = recovery)
            
            -- Classification
            activation_level TEXT,      -- LOW, MODERATE, HIGH, VERY_HIGH
            meeting_type TEXT,          -- EXTERNAL, INTERNAL, SOLO, UNKNOWN
            
            -- Metadata
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS person_hr_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_email TEXT UNIQUE,
            person_name TEXT,
            meeting_count INTEGER DEFAULT 0,
            avg_hr_delta REAL,
            avg_hr_spike REAL,
            max_hr_spike REAL,
            avg_recovery_time_min REAL,
            classification TEXT,        -- ENERGIZING, NEUTRAL, DRAINING
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_meeting_date ON meeting_hr_correlation(event_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_activation ON meeting_hr_correlation(activation_level)
    """)
    
    conn.commit()
    conn.close()
    

def get_hr_data(start_time: str, end_time: str) -> list:
    """Fetch HR data for a time window."""
    conn = sqlite3.connect(WORKOUTS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT datetime_local, bpm
        FROM intraday_heart_rate
        WHERE datetime_local >= ? AND datetime_local < ?
        AND bpm IS NOT NULL AND bpm > 0
        ORDER BY datetime_local
    """, (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_baseline_hr(meeting_start: datetime) -> tuple:
    """Get baseline HR from 10 minutes before meeting."""
    baseline_start = meeting_start - timedelta(minutes=BASELINE_WINDOW_MIN)
    baseline_end = meeting_start
    
    data = get_hr_data(
        baseline_start.strftime("%Y-%m-%dT%H:%M:%S"),
        baseline_end.strftime("%Y-%m-%dT%H:%M:%S")
    )
    
    if not data:
        return None, 0
    
    hr_values = [d['bpm'] for d in data]
    return mean(hr_values), len(hr_values)


def get_meeting_hr(meeting_start: datetime, meeting_end: datetime) -> dict:
    """Get HR metrics during meeting."""
    data = get_hr_data(
        meeting_start.strftime("%Y-%m-%dT%H:%M:%S"),
        meeting_end.strftime("%Y-%m-%dT%H:%M:%S")
    )
    
    if not data:
        return {'avg': None, 'max': None, 'min': None, 'samples': 0}
    
    hr_values = [d['bpm'] for d in data]
    return {
        'avg': mean(hr_values),
        'max': max(hr_values),
        'min': min(hr_values),
        'samples': len(hr_values)
    }


def get_recovery_hr(meeting_end: datetime) -> tuple:
    """Get average HR for 15 minutes after meeting."""
    recovery_start = meeting_end
    recovery_end = meeting_end + timedelta(minutes=RECOVERY_WINDOW_MIN)
    
    data = get_hr_data(
        recovery_start.strftime("%Y-%m-%dT%H:%M:%S"),
        recovery_end.strftime("%Y-%m-%dT%H:%M:%S")
    )
    
    if not data:
        return None, 0
    
    hr_values = [d['bpm'] for d in data]
    return mean(hr_values), len(hr_values)


def classify_activation(hr_delta: float) -> str:
    """Classify activation level based on HR delta."""
    if hr_delta is None:
        return "UNKNOWN"
    if hr_delta < 5:
        return "LOW"
    elif hr_delta < HR_SPIKE_THRESHOLD:
        return "MODERATE"
    elif hr_delta < HR_HIGH_THRESHOLD:
        return "HIGH"
    else:
        return "VERY_HIGH"


def classify_meeting_type(event: dict) -> str:
    """Classify meeting as EXTERNAL, INTERNAL, SOLO based on attendees."""
    attendees = event.get('attendees', [])
    if not attendees or len(attendees) <= 1:
        return "SOLO"
    
    # Check if any attendees are external (not @mycareerspan.com or @gmail.com)
    internal_domains = ['mycareerspan.com', 'gmail.com', 'careerspan.com']
    for attendee in attendees:
        email = attendee.get('email', '')
        domain = email.split('@')[-1] if '@' in email else ''
        if domain and domain not in internal_domains:
            return "EXTERNAL"
    
    return "INTERNAL"


def parse_event_time(event: dict) -> tuple:
    """Parse event start and end times."""
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Handle dateTime (timed events) vs date (all-day events)
    start_str = start.get('dateTime') or start.get('date')
    end_str = end.get('dateTime') or end.get('date')
    
    if not start_str or not end_str:
        return None, None
    
    # Parse ISO format with timezone
    try:
        # Remove timezone suffix for parsing
        start_clean = start_str[:19] if 'T' in start_str else start_str
        end_clean = end_str[:19] if 'T' in end_str else end_str
        
        if 'T' in start_str:
            start_dt = datetime.fromisoformat(start_clean)
            end_dt = datetime.fromisoformat(end_clean)
        else:
            # All-day event, skip
            return None, None
            
        return start_dt, end_dt
    except ValueError:
        return None, None


def correlate_event(event: dict) -> dict:
    """Correlate a single calendar event with HR data."""
    event_id = event.get('id', '')
    title = event.get('summary', 'Untitled')
    
    start_dt, end_dt = parse_event_time(event)
    if not start_dt or not end_dt:
        return None
    
    # Skip very short events (< 10 min) or very long (> 4 hours)
    duration_min = (end_dt - start_dt).total_seconds() / 60
    if duration_min < 10 or duration_min > 240:
        return None
    
    # Get HR data
    baseline_hr, baseline_samples = get_baseline_hr(start_dt)
    meeting_hr = get_meeting_hr(start_dt, end_dt)
    recovery_hr, recovery_samples = get_recovery_hr(end_dt)
    
    # Skip if no HR data
    if not baseline_hr or not meeting_hr['avg']:
        return None
    
    # Calculate deltas
    hr_delta = meeting_hr['avg'] - baseline_hr
    hr_spike_max = meeting_hr['max'] - baseline_hr if meeting_hr['max'] else None
    recovery_delta = (recovery_hr - meeting_hr['avg']) if recovery_hr else None
    
    # Extract attendees
    attendees = event.get('attendees', [])
    attendee_emails = [a.get('email', '') for a in attendees if a.get('email')]
    organizer = event.get('organizer', {}).get('email', '')
    
    return {
        'event_id': event_id,
        'event_date': start_dt.date().isoformat(),
        'event_start_time': start_dt.strftime("%H:%M"),
        'event_end_time': end_dt.strftime("%H:%M"),
        'event_title': title,
        'event_duration_min': int(duration_min),
        'attendees': json.dumps(attendee_emails),
        'organizer': organizer,
        
        'hr_baseline': round(baseline_hr, 1),
        'hr_baseline_samples': baseline_samples,
        'hr_during_avg': round(meeting_hr['avg'], 1),
        'hr_during_max': meeting_hr['max'],
        'hr_during_min': meeting_hr['min'],
        'hr_during_samples': meeting_hr['samples'],
        'hr_after_avg': round(recovery_hr, 1) if recovery_hr else None,
        'hr_after_samples': recovery_samples,
        
        'hr_delta': round(hr_delta, 1),
        'hr_spike_max': round(hr_spike_max, 1) if hr_spike_max else None,
        'recovery_delta': round(recovery_delta, 1) if recovery_delta else None,
        
        'activation_level': classify_activation(hr_delta),
        'meeting_type': classify_meeting_type(event)
    }


def save_correlation(data: dict):
    """Save correlation data to database."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO meeting_hr_correlation (
            event_id, event_date, event_start_time, event_end_time,
            event_title, event_duration_min, attendees, organizer,
            hr_baseline, hr_baseline_samples, hr_during_avg, hr_during_max,
            hr_during_min, hr_during_samples, hr_after_avg, hr_after_samples,
            hr_delta, hr_spike_max, recovery_delta, activation_level, meeting_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['event_id'], data['event_date'], data['event_start_time'],
        data['event_end_time'], data['event_title'], data['event_duration_min'],
        data['attendees'], data['organizer'],
        data['hr_baseline'], data['hr_baseline_samples'], data['hr_during_avg'],
        data['hr_during_max'], data['hr_during_min'], data['hr_during_samples'],
        data['hr_after_avg'], data['hr_after_samples'],
        data['hr_delta'], data['hr_spike_max'], data['recovery_delta'],
        data['activation_level'], data['meeting_type']
    ))
    
    conn.commit()
    conn.close()


def update_person_patterns():
    """Update person-level HR patterns from meeting data."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all unique organizers and attendees
    cursor.execute("SELECT DISTINCT organizer FROM meeting_hr_correlation WHERE organizer != ''")
    organizers = [r['organizer'] for r in cursor.fetchall()]
    
    cursor.execute("SELECT attendees FROM meeting_hr_correlation")
    all_attendees = set()
    for row in cursor.fetchall():
        try:
            attendees = json.loads(row['attendees'])
            all_attendees.update(attendees)
        except:
            pass
    
    all_people = set(organizers) | all_attendees
    
    for email in all_people:
        if not email or '@' not in email:
            continue
            
        # Get meetings where this person was involved
        cursor.execute("""
            SELECT hr_delta, hr_spike_max, recovery_delta
            FROM meeting_hr_correlation
            WHERE organizer = ? OR attendees LIKE ?
        """, (email, f'%{email}%'))
        
        rows = cursor.fetchall()
        if not rows:
            continue
        
        deltas = [r['hr_delta'] for r in rows if r['hr_delta'] is not None]
        spikes = [r['hr_spike_max'] for r in rows if r['hr_spike_max'] is not None]
        
        if not deltas:
            continue
        
        avg_delta = mean(deltas)
        avg_spike = mean(spikes) if spikes else None
        max_spike = max(spikes) if spikes else None
        
        # Classify: ENERGIZING (low HR), NEUTRAL, DRAINING (high HR)
        if avg_delta < 3:
            classification = "ENERGIZING"
        elif avg_delta < 8:
            classification = "NEUTRAL"
        else:
            classification = "DRAINING"
        
        # Extract name from email
        name = email.split('@')[0].replace('.', ' ').title()
        
        cursor.execute("""
            INSERT OR REPLACE INTO person_hr_patterns (
                person_email, person_name, meeting_count, avg_hr_delta,
                avg_hr_spike, max_hr_spike, classification, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (email, name, len(rows), round(avg_delta, 1), 
              round(avg_spike, 1) if avg_spike else None,
              round(max_spike, 1) if max_spike else None, classification))
    
    conn.commit()
    conn.close()


def sync_with_calendar(events: list):
    """Sync calendar events with HR data."""
    init_db()
    
    processed = 0
    skipped = 0
    
    for event in events:
        result = correlate_event(event)
        if result:
            save_correlation(result)
            processed += 1
            print(f"  ✓ {result['event_date']} {result['event_start_time']} - {result['event_title'][:40]}")
        else:
            skipped += 1
    
    # Update person patterns
    update_person_patterns()
    
    print(f"\n✓ Synced {processed} meetings, skipped {skipped}")


def report_meetings(limit: int = 20):
    """Generate meeting HR report."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM meeting_hr_correlation
        ORDER BY event_date DESC, event_start_time DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No meeting data found. Run 'sync' first.")
        return
    
    print("\n" + "=" * 80)
    print("MEETING HR CORRELATION REPORT")
    print("=" * 80)
    
    for row in rows:
        activation = row['activation_level']
        emoji = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "VERY_HIGH": "🔴"}.get(activation, "⚪")
        
        print(f"\n{emoji} {row['event_title'][:50]}")
        print(f"   Date: {row['event_date']} {row['event_start_time']}-{row['event_end_time']} ({row['event_duration_min']} min)")
        print(f"   Type: {row['meeting_type']}")
        print(f"   HR Baseline: {row['hr_baseline']} bpm")
        print(f"   HR During:   {row['hr_during_avg']} bpm (max: {row['hr_during_max']})")
        print(f"   HR Delta:    {'+' if row['hr_delta'] > 0 else ''}{row['hr_delta']} bpm → {activation}")
        if row['hr_after_avg']:
            recovery = row['recovery_delta']
            recovery_str = f"{'+' if recovery > 0 else ''}{recovery}" if recovery else "N/A"
            print(f"   Recovery:    {row['hr_after_avg']} bpm ({recovery_str})")


def report_people():
    """Generate per-person HR pattern report."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM person_hr_patterns
        WHERE meeting_count >= 2
        ORDER BY avg_hr_delta DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No person data found. Run 'sync' first with enough meetings.")
        return
    
    print("\n" + "=" * 80)
    print("PERSON HR PATTERNS (sorted by impact)")
    print("=" * 80)
    
    print(f"\n{'Person':<30} {'Meetings':>8} {'Avg Δ':>8} {'Max Spike':>10} {'Type':<12}")
    print("-" * 80)
    
    for row in rows:
        emoji = {"ENERGIZING": "🟢", "NEUTRAL": "🟡", "DRAINING": "🔴"}.get(row['classification'], "⚪")
        max_spike = f"+{row['max_hr_spike']}" if row['max_hr_spike'] else "N/A"
        print(f"{emoji} {row['person_name']:<28} {row['meeting_count']:>8} {'+' if row['avg_hr_delta'] > 0 else ''}{row['avg_hr_delta']:>7} {max_spike:>10} {row['classification']:<12}")


def report_trends():
    """Show trends over time."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # By time of day
    cursor.execute("""
        SELECT 
            CAST(substr(event_start_time, 1, 2) AS INTEGER) as hour,
            COUNT(*) as count,
            ROUND(AVG(hr_delta), 1) as avg_delta,
            ROUND(AVG(hr_during_avg), 1) as avg_hr
        FROM meeting_hr_correlation
        GROUP BY hour
        ORDER BY hour
    """)
    
    rows = cursor.fetchall()
    
    print("\n" + "=" * 80)
    print("HOURLY MEETING PATTERNS")
    print("=" * 80)
    print(f"\n{'Hour':<8} {'Meetings':>10} {'Avg HR':>10} {'Avg Δ':>10}")
    print("-" * 40)
    
    for row in rows:
        hour_str = f"{row['hour']:02d}:00"
        delta_str = f"+{row['avg_delta']}" if row['avg_delta'] > 0 else str(row['avg_delta'])
        print(f"{hour_str:<8} {row['count']:>10} {row['avg_hr']:>10} {delta_str:>10}")
    
    # By meeting type
    cursor.execute("""
        SELECT 
            meeting_type,
            COUNT(*) as count,
            ROUND(AVG(hr_delta), 1) as avg_delta,
            ROUND(MAX(hr_spike_max), 1) as max_spike
        FROM meeting_hr_correlation
        GROUP BY meeting_type
    """)
    
    rows = cursor.fetchall()
    
    print("\n" + "=" * 80)
    print("BY MEETING TYPE")
    print("=" * 80)
    print(f"\n{'Type':<12} {'Count':>8} {'Avg Δ':>10} {'Max Spike':>12}")
    print("-" * 45)
    
    for row in rows:
        delta_str = f"+{row['avg_delta']}" if row['avg_delta'] > 0 else str(row['avg_delta'])
        spike_str = f"+{row['max_spike']}" if row['max_spike'] else "N/A"
        print(f"{row['meeting_type']:<12} {row['count']:>8} {delta_str:>10} {spike_str:>12}")
    
    conn.close()


def generate_performance_profile():
    """Generate personalized time-of-day performance profile."""
    conn = sqlite3.connect(WORKOUTS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("PERSONAL PERFORMANCE PROFILE")
    print("="*80)
    
    # Get hourly HR patterns across all days
    cursor.execute("""
        SELECT 
            CAST(strftime('%H', datetime_local) AS INTEGER) as hour,
            AVG(bpm) as avg_hr,
            MIN(bpm) as min_hr,
            MAX(bpm) as max_hr,
            COUNT(*) as samples,
            AVG(bpm * bpm) - AVG(bpm) * AVG(bpm) as variance
        FROM intraday_heart_rate
        WHERE datetime_local >= date('now', '-30 days')
        GROUP BY hour
        ORDER BY hour
    """)
    
    hourly_data = cursor.fetchall()
    conn.close()
    
    if not hourly_data:
        print("No HR data available for profiling.")
        return
    
    # Calculate baseline (median HR)
    all_avgs = [row['avg_hr'] for row in hourly_data if row['avg_hr']]
    baseline = sorted(all_avgs)[len(all_avgs)//2] if all_avgs else 80
    
    print(f"\n📊 Baseline HR: {baseline:.1f} bpm (30-day median)\n")
    
    # Categorize hours
    deep_work_hours = []  # Low HR, low variance = calm focus
    meeting_hours = []    # Moderate HR, can handle activation
    recovery_hours = []   # Naturally low, good for breaks
    
    print("Hour    Avg HR   Variance   Energy State")
    print("-" * 50)
    
    for row in hourly_data:
        hour = row['hour']
        avg_hr = row['avg_hr'] or 0
        variance = row['variance'] or 0
        samples = row['samples']
        
        if samples < 100:  # Skip hours with insufficient data
            continue
        
        # Determine energy state
        hr_delta = avg_hr - baseline
        
        if hr_delta < -3 and variance < 100:
            state = "🧘 Recovery"
            recovery_hours.append(hour)
        elif hr_delta < 2 and variance < 150:
            state = "🎯 Deep Work"
            deep_work_hours.append(hour)
        elif hr_delta < 8:
            state = "💬 Meetings OK"
            meeting_hours.append(hour)
        else:
            state = "⚡ High Energy"
        
        print(f"{hour:02d}:00   {avg_hr:5.1f}    {variance:6.1f}     {state}")
    
    print("\n" + "="*80)
    print("OPTIMAL SCHEDULE RECOMMENDATIONS")
    print("="*80)
    
    if deep_work_hours:
        print(f"\n🎯 DEEP WORK WINDOWS: {format_hour_ranges(deep_work_hours)}")
        print("   Your HR is low and stable - ideal for focused, cognitively demanding tasks")
    
    if meeting_hours:
        print(f"\n💬 MEETING WINDOWS: {format_hour_ranges(meeting_hours)}")
        print("   Moderate energy - good for collaborative work and calls")
    
    if recovery_hours:
        print(f"\n🧘 RECOVERY WINDOWS: {format_hour_ranges(recovery_hours)}")
        print("   Natural low point - schedule breaks, walks, or light admin")
    
    # Check for the 2pm dip
    afternoon_hours = [row for row in hourly_data if 13 <= row['hour'] <= 16]
    if afternoon_hours:
        afternoon_avg = sum(r['avg_hr'] for r in afternoon_hours if r['avg_hr']) / len(afternoon_hours)
        morning_hours = [row for row in hourly_data if 9 <= row['hour'] <= 12]
        if morning_hours:
            morning_avg = sum(r['avg_hr'] for r in morning_hours if r['avg_hr']) / len(morning_hours)
            
            print(f"\n📉 AFTERNOON DIP ANALYSIS:")
            print(f"   Morning avg (9am-12pm): {morning_avg:.1f} bpm")
            print(f"   Afternoon avg (1pm-4pm): {afternoon_avg:.1f} bpm")
            diff = afternoon_avg - morning_avg
            if diff < -3:
                print(f"   ⚠️  Significant afternoon dip detected ({diff:+.1f} bpm)")
                print(f"   → Consider lighter tasks or a short break around 2-3pm")
            elif diff > 3:
                print(f"   ⬆️  Afternoon energy actually rises ({diff:+.1f} bpm)")
            else:
                print(f"   ✓  Stable energy through afternoon ({diff:+.1f} bpm)")


def format_hour_ranges(hours):
    """Format list of hours into readable ranges."""
    if not hours:
        return "None identified"
    
    hours = sorted(hours)
    ranges = []
    start = hours[0]
    end = hours[0]
    
    for h in hours[1:]:
        if h == end + 1:
            end = h
        else:
            ranges.append(f"{start:02d}:00-{end+1:02d}:00" if start != end else f"{start:02d}:00")
            start = end = h
    
    ranges.append(f"{start:02d}:00-{end+1:02d}:00" if start != end else f"{start:02d}:00")
    return ", ".join(ranges)


def main():
    parser = argparse.ArgumentParser(description="Calendar-HR Correlator")
    parser.add_argument('command', choices=['sync', 'report', 'people', 'trends', 'profile'],
                       help="Command to run")
    parser.add_argument('--days', type=int, default=30, help="Days to sync (for sync command)")
    parser.add_argument('--limit', type=int, default=20, help="Limit results (for report command)")
    parser.add_argument('--events-json', type=str, help="Path to calendar events JSON file")
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        if args.events_json:
            with open(args.events_json) as f:
                events = json.load(f)
            sync_with_calendar(events)
        else:
            print("For sync, provide calendar events via --events-json")
            print("Events should be fetched via Google Calendar API first.")
            sys.exit(1)
    elif args.command == 'report':
        report_meetings(args.limit)
    elif args.command == 'people':
        report_people()
    elif args.command == 'trends':
        report_trends()
    elif args.command == 'profile':
        generate_performance_profile()


if __name__ == "__main__":
    main()



