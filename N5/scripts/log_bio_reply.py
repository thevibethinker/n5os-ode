#!/usr/bin/env python3
"""
Log Bio-Log Reply - Processes a user's SMS reply for the health log.
Usage:
    python3 log_bio_reply.py "Message content here"

Logic:
    - Extracts emojis -> Mood
    - Extracts text -> Diet/Content
    - Determines time period (morning, midday, afternoon, evening, night)
    - Calls journal.py to save entries
    - Triggers Fitbit Sync to correlate vitals
    - Captures a vitals snapshot at that exact moment
"""

import sys
import re
import subprocess
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import pytz

try:
    import emoji
except ImportError:
    emoji = None

# Timezone
ET = pytz.timezone('America/New_York')

# Time period definitions
TIME_PERIODS = {
    (5, 10): "morning",      # 5 AM - 10 AM
    (10, 12): "midday",      # 10 AM - 12 PM  
    (12, 17): "afternoon",   # 12 PM - 5 PM
    (17, 21): "evening",     # 5 PM - 9 PM
    (21, 24): "night",       # 9 PM - midnight
    (0, 5): "night",         # midnight - 5 AM
}

JOURNAL_DB = Path("/home/workspace/N5/data/journal.db")
WORKOUTS_DB = Path("/home/workspace/Personal/Health/workouts.db")

def get_time_period(hour: int) -> str:
    """Determine time period based on hour."""
    for (start, end), period in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    return "night"  # fallback

def extract_emojis(text):
    if emoji:
        return ''.join(c for c in text if c in emoji.EMOJI_DATA)
    # Fallback: basic emoji detection via unicode ranges
    return ''.join(c for c in text if ord(c) > 0x1F300)

def remove_emojis(text):
    if emoji:
        return ''.join(c for c in text if c not in emoji.EMOJI_DATA).strip()
    return ''.join(c for c in text if ord(c) <= 0x1F300).strip()

def sync_fitbit():
    """Trigger Fitbit sync to get latest data."""
    print("✨ Syncing Fitbit Vitals...")
    try:
        result = subprocess.run(
            ["python3", "/home/workspace/Personal/Health/WorkoutTracker/fitbit_sync.py", "sync-recent"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Fitbit sync complete.")
        else:
            print(f"⚠️ Fitbit sync warning: {result.stderr[:100] if result.stderr else 'unknown'}")
    except subprocess.TimeoutExpired:
        print("⚠️ Fitbit sync timed out (will continue)")
    except Exception as e:
        print(f"⚠️ Fitbit sync failed: {e}")

def get_current_vitals() -> dict:
    """Fetch current vitals from workouts.db."""
    vitals = {
        "resting_hr": None,
        "current_hr": None,
        "hrv": None,
        "steps_so_far": None,
        "calories_so_far": None,
        "sleep_minutes": None,
        "sleep_score": None,
    }
    
    today = datetime.now(ET).strftime("%Y-%m-%d")
    current_time = datetime.now(ET).strftime("%Y-%m-%dT%H:%M")
    
    try:
        conn = sqlite3.connect(WORKOUTS_DB)
        cur = conn.cursor()
        
        # Resting HR and latest HRV for today
        cur.execute("SELECT resting_hr, hrv FROM daily_resting_hr WHERE date = ?", (today,))
        row = cur.fetchone()
        if row:
            vitals["resting_hr"] = int(row[0]) if row[0] else None
            vitals["hrv"] = row[1]
        
        # Most recent heart rate (within last 30 min)
        time_30_ago = (datetime.now(ET) - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M")
        cur.execute("""
            SELECT bpm FROM intraday_heart_rate 
            WHERE datetime_local BETWEEN ? AND ?
            ORDER BY datetime_local DESC LIMIT 1
        """, (time_30_ago, current_time))
        row = cur.fetchone()
        if row:
            vitals["current_hr"] = row[0]
        
        # Steps and calories so far today
        cur.execute("SELECT steps, calories_out FROM daily_activity_summary WHERE date = ?", (today,))
        row = cur.fetchone()
        if row:
            vitals["steps_so_far"] = row[0]
            vitals["calories_so_far"] = row[1]
        
        # Sleep from last night
        yesterday = (datetime.now(ET) - timedelta(days=1)).strftime("%Y-%m-%d")
        cur.execute("SELECT minutes_asleep, sleep_score FROM daily_sleep WHERE date = ?", (today,))
        row = cur.fetchone()
        if row:
            vitals["sleep_minutes"] = int(row[0]) if row[0] else None
            vitals["sleep_score"] = int(row[1]) if row[1] else None
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Could not fetch vitals: {e}")
    
    return vitals

def save_bio_snapshot(time_period: str, mood: str, note: str, vitals: dict):
    """Save a bio snapshot to the journal database."""
    try:
        conn = sqlite3.connect(JOURNAL_DB)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO bio_snapshots 
            (created_at, time_period, journal_entry_id, mood, diet_note, 
             resting_hr, current_hr, hrv, steps_so_far, calories_so_far, sleep_minutes, sleep_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"),
            time_period,
            None,
            mood,
            note,
            vitals.get("resting_hr"),
            vitals.get("current_hr"),
            vitals.get("hrv"),
            vitals.get("steps_so_far"),
            vitals.get("calories_so_far"),
            vitals.get("sleep_minutes"),
            vitals.get("sleep_score"),
        ))
        
        conn.commit()
        conn.close()
        print(f"📸 Snapshot saved: {time_period} @ {datetime.now(ET).strftime('%H:%M')}")
        return True
    except Exception as e:
        print(f"⚠️ Could not save snapshot: {e}")
        return False

def process_reply(message: str):
    """Process a bio-log SMS reply."""
    # Use ET timezone
    now_et = datetime.now(ET)
    hour = now_et.hour
    time_period = get_time_period(hour)
    timestamp_display = now_et.strftime("%Y-%m-%d %H:%M")
    
    # Extract Data
    mood_emoji = extract_emojis(message)
    diet_text = remove_emojis(message)
    
    # Dates
    mood_date = now_et.strftime("%Y-%m-%d %H:%M:%S")
    
    # For diet context, morning check-ins refer to yesterday's dinner
    if time_period == "morning":
        diet_date_obj = now_et - timedelta(days=1)
        diet_date = diet_date_obj.replace(hour=23, minute=59, second=0).strftime("%Y-%m-%d %H:%M:%S")
        diet_context = "Dinner/Night (Yesterday)"
    else:
        diet_date = now_et.strftime("%Y-%m-%d %H:%M:%S")
        diet_context = f"{time_period.capitalize()} (Today)"

    journal_entry_id = None
    
    # Execute Log for Mood (if emoji present)
    if mood_emoji:
        print(f"🎭 Logging Mood: {mood_emoji} [{time_period}]")
        subprocess.run([
            "python3", "/home/workspace/N5/scripts/journal.py", "add", "bio_log",
            f"Mood Check-in ({diet_context})",
            "--mood", mood_emoji,
            "--date", mood_date
        ])

    # Execute Log for Diet (if text present)
    if diet_text:
        print(f"🍽️ Logging Diet: {diet_text[:50]}...")
        subprocess.run([
            "python3", "/home/workspace/N5/scripts/journal.py", "add", "bio_log",
            f"Diet Log: {diet_text}",
            "--diet", diet_text,
            "--date", diet_date
        ])
    
    # Sync Fitbit to get fresh data
    sync_fitbit()
    
    # Capture vitals snapshot
    vitals = get_current_vitals()
    save_bio_snapshot(time_period, mood_emoji, diet_text, vitals)
    
    # Print summary
    print("\n" + "="*50)
    print(f"📍 BIO LOG CAPTURED @ {timestamp_display} ET ({time_period})")
    print("="*50)
    if mood_emoji:
        print(f"   Mood: {mood_emoji}")
    if diet_text:
        print(f"   Note: {diet_text[:60]}{'...' if len(diet_text) > 60 else ''}")
    print(f"   ❤️  Resting HR: {vitals['resting_hr'] or '—'} bpm")
    print(f"   💓 Current HR: {vitals['current_hr'] or '—'} bpm")
    print(f"   📊 HRV: {vitals['hrv'] or '—'} ms")
    print(f"   👟 Steps: {vitals['steps_so_far'] or 0:,}")
    print(f"   🔥 Calories: {int(vitals['calories_so_far']) if vitals['calories_so_far'] else 0:,}")
    print(f"   😴 Sleep: {vitals['sleep_minutes'] or '—'} min")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 log_bio_reply.py 'Message'")
        print("       bio 'Message'  (shell alias)")
        sys.exit(1)
        
    message = sys.argv[1]
    process_reply(message)



