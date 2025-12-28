import sqlite3
import argparse
import sys
from datetime import datetime, timedelta

DB_PATH = "/home/workspace/N5/data/performance.db"
WORKOUTS_DB = "/home/workspace/Personal/Health/workouts.db"

def get_performance_data():
    conn = sqlite3.connect(WORKOUTS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get hourly HR patterns across last 30 days
    cursor.execute("""
        SELECT 
            CAST(strftime('%H', datetime_local) AS INTEGER) as hour,
            AVG(bpm) as avg_hr,
            AVG(bpm * bpm) - AVG(bpm) * AVG(bpm) as variance
        FROM intraday_heart_rate
        WHERE datetime_local >= date('now', '-30 days')
        GROUP BY hour
        ORDER BY hour
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def recommend_slots(intensity_score):
    performance_data = get_performance_data()
    
    # Baseline is median HR
    avgs = [row['avg_hr'] for row in performance_data if row['avg_hr']]
    baseline = sorted(avgs)[len(avgs)//2] if avgs else 80
    
    recommendations = []
    for row in performance_data:
        hour = row['hour']
        avg_hr = row['avg_hr']
        variance = row['variance']
        
        if avg_hr is None: continue
        
        hr_delta = avg_hr - baseline
        
        score = 0
        if intensity_score > 8: # High Intensity
            if hr_delta > 5: score = 10 
            elif hr_delta > 0: score = 7
            else: score = 2
        elif intensity_score < 3: # Low Intensity
            if hr_delta < -2: score = 10 
            elif hr_delta < 2: score = 8
            else: score = 4
        else: # Moderate
            if abs(hr_delta) < 5: score = 10
            else: score = 5
            
        if variance and variance > 200: score -= 3
        
        recommendations.append({
            'hour': hour,
            'score': max(0, score),
            'hr_delta': hr_delta,
            'variance': variance or 0
        })
        
    return sorted(recommendations, key=lambda x: x['score'], reverse=True)

def main():
    parser = argparse.ArgumentParser(description="Predictive Scheduler")
    parser.add_argument('--type', choices=['EXTERNAL', 'INTERNAL', 'SOLO'], default='INTERNAL')
    args = parser.parse_args()
    
    # In a real system, these would be pulled from the DB per person/type
    intensities = {'EXTERNAL': 12, 'INTERNAL': 6, 'SOLO': 2}
    intensity_score = intensities.get(args.type, 5)
    
    print(f"--- PREDICTIVE SCHEDULING FOR {args.type} ---")
    recs = recommend_slots(intensity_score)
    
    print(f"\nTop Recommended Hours (24h format):")
    for r in recs[:5]:
        print(f"{r['hour']:02d}:00 (Score: {r['score']}/10) | HR Delta: {r['hr_delta']:+.1f} | Var: {r['variance']:.1f}")

if __name__ == "__main__":
    main()
