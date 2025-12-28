#!/usr/bin/env python3
"""
Meeting-HR Correlator

Correlates calendar meetings with intraday heart rate data to identify
stress patterns. Answers: "Which meetings spike my HR?"

Usage:
    python3 correlate_meeting_hr.py sync [--days N]   # Sync last N days (default 14)
    python3 correlate_meeting_hr.py report            # Show stress report
    python3 correlate_meeting_hr.py query "person"    # Find meetings with person

Database: N5/data/performance.db
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Paths
PERFORMANCE_DB = Path("/home/workspace/N5/data/performance.db")
WORKOUTS_DB = Path("/home/workspace/Personal/Health/workouts.db")

def get_db_connection(db_path: Path):
    """Get SQLite connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize performance database with required tables."""
    PERFORMANCE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_hr_correlation (
            id INTEGER PRIMARY KEY,
            meeting_date TEXT NOT NULL,
            meeting_title TEXT,
            meeting_type TEXT,
            attendees TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_minutes INTEGER,
            hr_baseline_before REAL,
            hr_during_avg REAL,
            hr_during_max REAL,
            hr_spike_delta REAL,
            hr_recovery_minutes INTEGER,
            time_of_day TEXT,
            day_of_week TEXT,
            hrv_daily REAL,
            sleep_score_prev_night REAL,
            stress_indicator TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(meeting_date, start_time)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_performance (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            hour INTEGER NOT NULL,
            hr_avg REAL,
            hr_min REAL,
            hr_max REAL,
            hr_variance REAL,
            reading_count INTEGER,
            had_meeting INTEGER DEFAULT 0,
            meeting_count INTEGER DEFAULT 0,
            meeting_minutes INTEGER DEFAULT 0,
            day_of_week TEXT,
            is_workday INTEGER,
            sleep_score REAL,
            hrv_morning REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, hour)
        )
    """)
    
    conn.commit()
    conn.close()

def get_hr_for_period(start_dt: datetime, end_dt: datetime) -> dict:
    """
    Get HR stats for a time period.
    Returns: {avg, min, max, readings: []}
    """
    conn = get_db_connection(WORKOUTS_DB)
    cursor = conn.cursor()
    
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    cursor.execute("""
        SELECT bpm FROM intraday_heart_rate
        WHERE datetime_local >= ? AND datetime_local < ?
        AND bpm IS NOT NULL
        ORDER BY datetime_local
    """, (start_str, end_str))
    
    readings = [row['bpm'] for row in cursor.fetchall()]
    conn.close()
    
    if not readings:
        return {'avg': None, 'min': None, 'max': None, 'readings': []}
    
    return {
        'avg': sum(readings) / len(readings),
        'min': min(readings),
        'max': max(readings),
        'readings': readings
    }

def get_daily_context(date_str: str) -> dict:
    """Get HRV and sleep score for a date."""
    conn = get_db_connection(WORKOUTS_DB)
    cursor = conn.cursor()
    
    # HRV
    cursor.execute("SELECT hrv FROM daily_resting_hr WHERE date = ?", (date_str,))
    row = cursor.fetchone()
    hrv = row['hrv'] if row else None
    
    # Sleep (previous night)
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("SELECT sleep_score FROM daily_sleep WHERE date = ?", (prev_date,))
    row = cursor.fetchone()
    sleep = row['sleep_score'] if row else None
    
    conn.close()
    return {'hrv': hrv, 'sleep_score': sleep}

def classify_stress(spike_delta: float, hr_during_avg: float) -> str:
    """Classify stress level based on HR spike."""
    if spike_delta is None:
        return 'unknown'
    
    # Thresholds (calibrate to V's baseline)
    if spike_delta >= 15 or hr_during_avg >= 95:
        return 'high'
    elif spike_delta >= 8 or hr_during_avg >= 85:
        return 'medium'
    else:
        return 'low'

def get_time_of_day(hour: int) -> str:
    """Classify hour into time-of-day bucket."""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def process_meeting(meeting: dict, date_str: str) -> dict:
    """
    Process a single meeting and correlate with HR data.
    
    meeting: {title, start, end, attendees}
    """
    start_dt = datetime.fromisoformat(meeting['start'].replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(meeting['end'].replace('Z', '+00:00'))
    
    # Convert to local time (assuming ET)
    # For simplicity, just use the time as-is since Fitbit stores local time
    start_local = start_dt.replace(tzinfo=None)
    end_local = end_dt.replace(tzinfo=None)
    
    duration = int((end_local - start_local).total_seconds() / 60)
    
    # Get baseline HR (30 min before meeting)
    baseline_start = start_local - timedelta(minutes=30)
    baseline_hr = get_hr_for_period(baseline_start, start_local)
    
    # Get during-meeting HR
    during_hr = get_hr_for_period(start_local, end_local)
    
    # Calculate spike
    spike_delta = None
    if baseline_hr['avg'] and during_hr['avg']:
        spike_delta = during_hr['avg'] - baseline_hr['avg']
    
    # Get daily context
    context = get_daily_context(date_str)
    
    # Classify meeting type
    attendees = meeting.get('attendees', [])
    if not attendees or len(attendees) <= 1:
        meeting_type = 'solo'
    elif any('careerspan' in a.lower() or 'mycareerspan' in a.lower() for a in attendees):
        meeting_type = 'internal'
    else:
        meeting_type = 'external'
    
    return {
        'meeting_date': date_str,
        'meeting_title': meeting.get('title', 'Untitled'),
        'meeting_type': meeting_type,
        'attendees': json.dumps(attendees),
        'start_time': start_local.strftime("%H:%M"),
        'end_time': end_local.strftime("%H:%M"),
        'duration_minutes': duration,
        'hr_baseline_before': baseline_hr['avg'],
        'hr_during_avg': during_hr['avg'],
        'hr_during_max': during_hr['max'],
        'hr_spike_delta': spike_delta,
        'hr_recovery_minutes': None,  # TODO: implement recovery detection
        'time_of_day': get_time_of_day(start_local.hour),
        'day_of_week': start_local.strftime("%A"),
        'hrv_daily': context['hrv'],
        'sleep_score_prev_night': context['sleep_score'],
        'stress_indicator': classify_stress(spike_delta, during_hr['avg'])
    }

def sync_hourly_data(days: int = 14):
    """Sync hourly performance data from intraday HR."""
    print(f"Syncing hourly performance data (last {days} days)...")
    
    conn_perf = get_db_connection(PERFORMANCE_DB)
    conn_hr = get_db_connection(WORKOUTS_DB)
    
    cursor_perf = conn_perf.cursor()
    cursor_hr = conn_hr.cursor()
    
    today = datetime.now().date()
    synced = 0
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_of_week = date.strftime("%A")
        is_workday = 1 if date.weekday() < 5 else 0
        
        # Get daily context
        context = get_daily_context(date_str)
        
        for hour in range(24):
            start_dt = datetime.combine(date, datetime.min.time().replace(hour=hour))
            end_dt = start_dt + timedelta(hours=1)
            
            start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
            end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
            
            cursor_hr.execute("""
                SELECT 
                    AVG(bpm) as avg,
                    MIN(bpm) as min,
                    MAX(bpm) as max,
                    COUNT(*) as count
                FROM intraday_heart_rate
                WHERE datetime_local >= ? AND datetime_local < ?
                AND bpm IS NOT NULL
            """, (start_str, end_str))
            
            row = cursor_hr.fetchone()
            
            if row and row['count'] > 0:
                # Calculate variance
                cursor_hr.execute("""
                    SELECT bpm FROM intraday_heart_rate
                    WHERE datetime_local >= ? AND datetime_local < ?
                    AND bpm IS NOT NULL
                """, (start_str, end_str))
                readings = [r['bpm'] for r in cursor_hr.fetchall()]
                avg = row['avg']
                variance = sum((x - avg) ** 2 for x in readings) / len(readings) if readings else 0
                
                cursor_perf.execute("""
                    INSERT OR REPLACE INTO hourly_performance
                    (date, hour, hr_avg, hr_min, hr_max, hr_variance, reading_count,
                     day_of_week, is_workday, sleep_score, hrv_morning)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date_str, hour, row['avg'], row['min'], row['max'], variance, row['count'],
                    day_of_week, is_workday, context['sleep_score'], context['hrv']
                ))
                synced += 1
    
    conn_perf.commit()
    conn_perf.close()
    conn_hr.close()
    
    print(f"✓ Synced {synced} hourly records")

def generate_stress_report():
    """Generate report of high-stress meetings."""
    conn = get_db_connection(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("MEETING STRESS REPORT")
    print("="*60)
    
    # High stress meetings
    cursor.execute("""
        SELECT * FROM meeting_hr_correlation
        WHERE stress_indicator = 'high'
        ORDER BY hr_spike_delta DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        print("\n🔴 HIGH STRESS MEETINGS:")
        print("-" * 60)
        for row in rows:
            print(f"  {row['meeting_date']} {row['start_time']} - {row['meeting_title'][:40]}")
            print(f"    Type: {row['meeting_type']} | Duration: {row['duration_minutes']}min")
            print(f"    HR Spike: +{row['hr_spike_delta']:.1f}bpm (baseline {row['hr_baseline_before']:.0f} → {row['hr_during_avg']:.0f})")
            print(f"    Context: HRV {row['hrv_daily'] or '—'}, Sleep {row['sleep_score_prev_night'] or '—'}")
            print()
    else:
        print("\n  No high-stress meetings recorded yet.")
    
    # Stress by meeting type
    print("\n📊 STRESS BY MEETING TYPE:")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            meeting_type,
            COUNT(*) as count,
            AVG(hr_spike_delta) as avg_spike,
            AVG(hr_during_avg) as avg_hr
        FROM meeting_hr_correlation
        WHERE hr_spike_delta IS NOT NULL
        GROUP BY meeting_type
        ORDER BY avg_spike DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['meeting_type']:10} | {row['count']:3} meetings | Avg Spike: +{row['avg_spike']:.1f}bpm | Avg HR: {row['avg_hr']:.0f}")
    
    # Stress by time of day
    print("\n⏰ STRESS BY TIME OF DAY:")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            time_of_day,
            COUNT(*) as count,
            AVG(hr_spike_delta) as avg_spike,
            AVG(hr_during_avg) as avg_hr
        FROM meeting_hr_correlation
        WHERE hr_spike_delta IS NOT NULL
        GROUP BY time_of_day
        ORDER BY 
            CASE time_of_day 
                WHEN 'morning' THEN 1 
                WHEN 'afternoon' THEN 2 
                WHEN 'evening' THEN 3 
                ELSE 4 
            END
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['time_of_day']:10} | {row['count']:3} meetings | Avg Spike: +{row['avg_spike']:.1f}bpm | Avg HR: {row['avg_hr']:.0f}")
    
    conn.close()

def generate_hourly_report():
    """Generate hourly performance analysis."""
    conn = get_db_connection(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("HOURLY PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Average HR by hour (workdays only)
    print("\n📈 AVERAGE HR BY HOUR (Workdays):")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            hour,
            AVG(hr_avg) as avg_hr,
            AVG(hr_variance) as avg_variance,
            COUNT(*) as days
        FROM hourly_performance
        WHERE is_workday = 1
        AND hr_avg IS NOT NULL
        GROUP BY hour
        ORDER BY hour
    """)
    
    print("Hour | Avg HR | Variance | Days")
    print("-" * 40)
    
    rows = cursor.fetchall()
    peak_hour = max(rows, key=lambda r: r['avg_hr'] or 0) if rows else None
    low_hour = min(rows, key=lambda r: r['avg_hr'] or 999) if rows else None
    
    for row in rows:
        if 6 <= row['hour'] <= 22:  # Only show waking hours
            marker = ""
            if peak_hour and row['hour'] == peak_hour['hour']:
                marker = " 🔺 PEAK"
            elif low_hour and row['hour'] == low_hour['hour']:
                marker = " 🔻 LOW"
            print(f" {row['hour']:02d}  |  {row['avg_hr']:.0f}   |   {row['avg_variance']:.1f}   | {row['days']}{marker}")
    
    # 2PM hypothesis check
    print("\n🎯 2PM ENERGY DROP HYPOTHESIS:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN hour BETWEEN 9 AND 12 THEN 'morning (9-12)'
                WHEN hour BETWEEN 13 AND 15 THEN 'early afternoon (1-3pm)'
                WHEN hour BETWEEN 16 AND 18 THEN 'late afternoon (4-6pm)'
            END as period,
            AVG(hr_avg) as avg_hr,
            AVG(hr_variance) as avg_variance
        FROM hourly_performance
        WHERE is_workday = 1
        AND hour BETWEEN 9 AND 18
        AND hr_avg IS NOT NULL
        GROUP BY period
        ORDER BY 
            CASE period
                WHEN 'morning (9-12)' THEN 1
                WHEN 'early afternoon (1-3pm)' THEN 2
                WHEN 'late afternoon (4-6pm)' THEN 3
            END
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        if row['period']:
            print(f"  {row['period']:25} | HR: {row['avg_hr']:.0f} | Variance: {row['avg_variance']:.1f}")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Meeting-HR Correlator")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # sync command
    sync_parser = subparsers.add_parser('sync', help='Sync meeting and HR data')
    sync_parser.add_argument('--days', type=int, default=14, help='Days to sync (default 14)')
    
    # report command
    subparsers.add_parser('report', help='Generate stress report')
    
    # hourly command
    subparsers.add_parser('hourly', help='Generate hourly performance report')
    
    # query command
    query_parser = subparsers.add_parser('query', help='Query meetings')
    query_parser.add_argument('term', help='Search term')
    
    args = parser.parse_args()
    
    # Always init DB
    init_db()
    
    if args.command == 'sync':
        sync_hourly_data(args.days)
        print("\n✓ Sync complete. Use 'report' or 'hourly' to see analysis.")
        print("  Note: Meeting data requires calendar sync (run separately)")
    
    elif args.command == 'report':
        generate_stress_report()
    
    elif args.command == 'hourly':
        generate_hourly_report()
    
    elif args.command == 'query':
        # TODO: implement meeting search
        print(f"Searching for '{args.term}'...")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

