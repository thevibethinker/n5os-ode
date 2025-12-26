import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("/home/workspace/Personal/Health/workouts.db")

# V's Zones (33 years old)
ZONES = {
    "Z1": (94, 112),
    "Z2": (113, 131),
    "Z3": (132, 150),
    "Z4": (151, 169),
    "Z5": (170, 220) # Max
}

ARCHETYPES = {
    "Engine Building": {
        "target_zone": "Z2",
        "description": "80% run. Foundation, mitochondria, base building.",
        "min_duration": 30,
        "hr_range": ZONES["Z2"]
    },
    "The 20% Interval": {
        "target_zone": "Z4/Z5",
        "description": "20% run. 4x4 intervals, VO2 max, explosive power.",
        "hr_range": (151, 190)
    }
}

def validate_workout(date):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get the latest workout for the date
    cur.execute("SELECT * FROM workouts WHERE date = ? AND primary_modality IN ('Run', 'Treadmill run') ORDER BY id DESC LIMIT 1", (date,))
    workout = cur.fetchone()
    
    if not workout:
        return "No run found for this date."
        
    avg_hr = workout['avg_hr']
    duration = workout['duration_min']
    
    if not avg_hr:
        return f"Workout found but missing average heart rate data."

    # Classification logic
    if avg_hr <= ZONES["Z2"][1] + 2: # Tolerance of 2bpm
        archetype = "Engine Building"
        target = ARCHETYPES[archetype]
        status = "✅ ADHERED" if avg_hr >= ZONES["Z2"][0] - 2 else "⚠️ TOO EASY (Z1)"
        if duration < target['min_duration']:
            status += f" | 🕒 TOO SHORT ({int(duration)}/30 mins)"
    elif avg_hr >= ZONES["Z4"][0] - 5: # Intervals often have lower averages due to rest, but we look for high peaks/sustained high HR
        archetype = "The 20% Interval"
        status = "✅ ADHERED (Intensity hit)"
    else:
        archetype = "THE GRAY ZONE"
        status = "❌ FAILED ADHERENCE (Too hard for Z2, too easy for Intervals)"

    return {
        "date": date,
        "modality": workout['primary_modality'],
        "duration": round(duration, 1),
        "avg_hr": round(avg_hr, 1),
        "archetype_detected": archetype,
        "status": status
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")
    
    result = validate_workout(date)
    print(json.dumps(result, indent=2))
