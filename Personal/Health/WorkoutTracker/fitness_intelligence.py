import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("/home/workspace/Personal/Health/workouts.db")

def get_efficiency_trend(days=30):
    conn = sqlite3.connect(DB_PATH)
    # Efficiency = Distance / (Avg HR * Duration) -> meters per heartbeat
    query = """
    SELECT 
        date,
        distance_km,
        duration_min,
        avg_hr,
        (distance_km * 1000) / (avg_hr * duration_min) as efficiency_metric
    FROM workouts 
    WHERE primary_modality IN ('Run', 'Treadmill run') 
      AND avg_hr IS NOT NULL 
      AND avg_hr > 100
      AND date > date('now', '-{} days')
    ORDER BY date ASC
    """.format(days)
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_resting_hr_trend(days=14):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, resting_hr FROM daily_resting_hr WHERE date > date('now', '-{} days') ORDER BY date ASC".format(days)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def analyze_improvement():
    efficiency = get_efficiency_trend()
    rhr = get_resting_hr_trend()
    
    report = {
        "efficiency_trend": "Insufficient data" if len(efficiency) < 3 else "Calculating...",
        "resting_hr_trend": "Insufficient data" if len(rhr) < 5 else "Calculating...",
    }
    
    if len(efficiency) >= 3:
        first_half = efficiency.head(len(efficiency)//2)['efficiency_metric'].mean()
        second_half = efficiency.tail(len(efficiency)//2)['efficiency_metric'].mean()
        change = ((second_half - first_half) / first_half) * 100
        report["efficiency_trend"] = f"{change:+.1f}% change in meters/heartbeat"
        
    if len(rhr) >= 5:
        avg_rhr = rhr['resting_hr'].mean()
        latest_rhr = rhr['resting_hr'].iloc[-1]
        report["resting_hr_trend"] = f"Avg: {avg_rhr:.1f}, Latest: {latest_rhr:.0f} (Target: Downward trend)"
        
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_improvement(), indent=2))
