#!/usr/bin/env python3
"""
Wellness Monitor - Triangulates subjective (Journal) and objective (Fitbit) health data.
Creates a unified 'wellness.db' for correlation analysis.

Usage:
    python3 wellness_monitor.py sync      # Sync data from sources to wellness.db
    python3 wellness_monitor.py report    # Generate a correlation report
"""

import sqlite3
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent))
import wellness_extractor

# Paths
JOURNAL_DB_PATH = Path("/home/workspace/N5/data/journal.db")
WORKOUTS_DB_PATH = Path("/home/workspace/Personal/Health/workouts.db")
WELLNESS_DB_PATH = Path("/home/workspace/N5/data/wellness.db")

def get_db_connection(db_path):
    if not db_path.exists():
        return None
    return sqlite3.connect(db_path)

def init_wellness_db():
    """Initialize unified wellness database."""
    WELLNESS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WELLNESS_DB_PATH)
    cursor = conn.cursor()
    
    # Table schema - 25 columns (date + 24 data columns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_wellness (
            date DATE PRIMARY KEY,
            -- Subjective (Journal)
            mood_emoji TEXT,
            mood_wakeup TEXT,
            mood_workday TEXT,
            mood_end TEXT,
            mood_score_wakeup INTEGER,
            mood_score_workday INTEGER,
            mood_score_end INTEGER,
            diet_summary TEXT,
            diet_score_day INTEGER,
            diet_score_night INTEGER,
            late_night_eating INTEGER,
            journal_word_count INTEGER,
            screen_time_hours REAL,
            -- Objective (Fitbit)
            resting_hr REAL,
            hrv REAL,
            spo2 REAL,
            skin_temp_delta REAL,
            sleep_duration_hours REAL,
            sleep_efficiency INTEGER,
            step_count INTEGER,
            active_minutes INTEGER,
            calories_burned REAL,
            -- Context
            meeting_count INTEGER,
            meeting_hours REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_journal_data(date_str):
    """Get mood and diet for a specific date."""
    conn = get_db_connection(JOURNAL_DB_PATH)
    if not conn:
        return {}, "", 0, {}, None
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT content, mood, diet, created_at
        FROM journal_entries 
        WHERE date(created_at) = ?
        ORDER BY created_at ASC
    """, (date_str,))
    
    rows = cursor.fetchall()
    
    moods = {'wakeup': None, 'workday': None, 'end': None,
              'score_wakeup': None, 'score_workday': None, 'score_end': None}
    diet_scores = {'day': None, 'night': None}
    late_night = None
    diets = []
    word_count = 0
    
    for row in rows:
        word_count += len(row['content'].split())
        hour = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S").hour
        extracted = wellness_extractor.process_entry(row['content'] + " " + (row['diet'] or ""), row['mood'])
        
        if row['mood'] or row['content']:
            if hour < 11:
                moods['wakeup'] = row['mood']
                moods['score_wakeup'] = extracted['mood_score']
            elif 11 <= hour < 19:
                moods['workday'] = row['mood']
                moods['score_workday'] = extracted['mood_score']
                diet_scores['day'] = extracted['diet_score']
            else:
                moods['end'] = row['mood']
                moods['score_end'] = extracted['mood_score']
        if row['diet']:
            diets.append(row['diet'])

    conn.close()
    diet_summary = "; ".join(diets) if diets else None
    return moods, diet_summary, word_count, diet_scores, late_night

def get_fitbit_data(date_str):
    """Fetch metrics from workouts.db for given date."""
    conn = get_db_connection(WORKOUTS_DB_PATH)
    if not conn:
        return {}
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    data = {}
    
    # Resting HR, HRV, SPO2, Skin Temp Delta
    try:
        cursor.execute("SELECT resting_hr, hrv, spo2, skin_temp_delta FROM daily_resting_hr WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        if row: 
            data['resting_hr'] = row['resting_hr']
            data['hrv'] = row['hrv']
            data['spo2'] = row['spo2']
            data['skin_temp_delta'] = row['skin_temp_delta']
    except sqlite3.OperationalError:
        pass

    # Sleep
    try:
        cursor.execute("SELECT minutes_asleep, sleep_score FROM daily_sleep WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        if row:
            data['sleep_duration_hours'] = (row['minutes_asleep'] or 0) / 60
            data['sleep_efficiency'] = row['sleep_score']
    except sqlite3.OperationalError:
        pass

    # Activity - Using activity_calories and active minutes
    try:
        cursor.execute("""
            SELECT steps, activity_calories,
                   minutes_lightly_active + minutes_fairly_active + minutes_very_active as active_minutes
            FROM daily_activity_summary WHERE date = ?
        """, (date_str,))
        row = cursor.fetchone()
        if row: 
            data['step_count'] = row['steps']
            data['calories_burned'] = row['activity_calories']
            data['active_minutes'] = row['active_minutes']
    except sqlite3.OperationalError:
        pass

    conn.close()
    return data

def process_context_file(context_file_path, date_str):
    """Parse calendar events JSON."""
    if not context_file_path:
        return {}
    path = Path(context_file_path)
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r') as f:
            events = json.load(f)
    except json.JSONDecodeError:
        return {'meeting_count': None, 'meeting_hours': None}
    
    count = 0
    duration_minutes = 0
    ignore_keywords = ["block", "focus", "lunch", "ooo", "dnd", "travel", "commute"]
    
    for event in events:
        summary = event.get('summary', '').lower()
        if any(k in summary for k in ignore_keywords):
            continue
        if event.get('status') == 'cancelled':
            continue
        start = event.get('start', {})
        if 'date' in start:
            continue
        try:
            s_dt = datetime.fromisoformat(start.get('dateTime'))
            e_dt = datetime.fromisoformat(event.get('end', {}).get('dateTime'))
            duration_minutes += (e_dt - s_dt).total_seconds() / 60
            count += 1
        except (ValueError, TypeError):
            continue
    
    return {'meeting_count': count, 'meeting_hours': round(duration_minutes / 60, 2)}

def sync_data(context_file=None):
    """Sync data from all sources to wellness.db."""
    init_wellness_db()
    
    today = datetime.now().date()
    print(f"Syncing wellness data (last 60 days)...")
    
    conn = sqlite3.connect(WELLNESS_DB_PATH)
    cursor = conn.cursor()
    
    for i in range(60):
        day = today - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        
        moods, diet_summary, word_count, diet_scores, late_night = get_journal_data(date_str)
        fitbit = get_fitbit_data(date_str)
        context = process_context_file(context_file, date_str) if context_file else {}

        # INSERT with 25 placeholders (date + 24 columns)
        cursor.execute("""
            INSERT INTO daily_wellness (
                date, mood_emoji, mood_wakeup, mood_workday, mood_end,
                mood_score_wakeup, mood_score_workday, mood_score_end,
                diet_summary, diet_score_day, diet_score_night, late_night_eating,
                journal_word_count, screen_time_hours,
                resting_hr, hrv, spo2, skin_temp_delta,
                sleep_duration_hours, sleep_efficiency, step_count, active_minutes, calories_burned,
                meeting_count, meeting_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                mood_emoji=excluded.mood_emoji, mood_wakeup=excluded.mood_wakeup, mood_workday=excluded.mood_workday, mood_end=excluded.mood_end,
                mood_score_wakeup=excluded.mood_score_wakeup, mood_score_workday=excluded.mood_score_workday, mood_score_end=excluded.mood_score_end,
                diet_summary=excluded.diet_summary, diet_score_day=excluded.diet_score_day, diet_score_night=excluded.diet_score_night, late_night_eating=excluded.late_night_eating,
                journal_word_count=excluded.journal_word_count,
                resting_hr=excluded.resting_hr, hrv=excluded.hrv, spo2=excluded.spo2, skin_temp_delta=excluded.skin_temp_delta,
                sleep_duration_hours=excluded.sleep_duration_hours, sleep_efficiency=excluded.sleep_efficiency, step_count=excluded.step_count, active_minutes=excluded.active_minutes, calories_burned=excluded.calories_burned,
                meeting_count=excluded.meeting_count, meeting_hours=excluded.meeting_hours, updated_at=CURRENT_TIMESTAMP
        """, (
            date_str,
            moods['end'] or moods['workday'] or moods['wakeup'],
            moods['wakeup'], moods['workday'], moods['end'],
            moods['score_wakeup'], moods['score_workday'], moods['score_end'],
            diet_summary, diet_scores['day'], diet_scores['night'], late_night,
            word_count,
            None,  # screen_time_hours (not currently sourced)
            fitbit.get('resting_hr'), fitbit.get('hrv'), fitbit.get('spo2'), fitbit.get('skin_temp_delta'),
            fitbit.get('sleep_duration_hours'), fitbit.get('sleep_efficiency'),
            fitbit.get('step_count'), fitbit.get('active_minutes'), fitbit.get('calories_burned'),
            context.get('meeting_count'), context.get('meeting_hours')
        ))
    
    conn.commit()
    conn.close()
    print("✓ Wellness database synchronized.")

def generate_report():
    """Generate a simple CLI report."""
    conn = sqlite3.connect(WELLNESS_DB_PATH)
    df = pd.read_sql_query("SELECT * FROM daily_wellness ORDER BY date DESC LIMIT 14", conn)
    conn.close()
    
    if df.empty:
        print("No data found.")
        return
    
    print("\n=== Last 14 Days Wellness Log ===")
    df = df.fillna('')
    cols = ['date', 'mood_score_wakeup', 'mood_score_workday', 'mood_score_end', 
            'diet_score_day', 'diet_score_night', 'resting_hr', 'hrv', 'spo2', 
            'sleep_duration_hours', 'calories_burned']
    print(df[cols].to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['sync', 'report'], default='sync')
    parser.add_argument('--context-file', help='Path to JSON file with calendar events for context injection')
    args = parser.parse_args()
    
    if args.command == 'sync':
        sync_data(args.context_file)
    elif args.command == 'report':
        generate_report()

