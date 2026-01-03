#!/usr/bin/env python3
"""
Weighted Vest Tracker for Wellness Database

Tags workouts with vest weight and calculates adjusted strain scores.

Usage:
    python3 vest_tracker.py tag <workout_id> <vest_weight_lb>
    python3 vest_tracker.py tag-recent <n> <vest_weight_lb>  # Tag last N workouts
    python3 vest_tracker.py remove <workout_id>              # Remove vest tag
    python3 vest_tracker.py list                             # Show all vest workouts
    python3 vest_tracker.py recalc                           # Recalculate all strain scores

Strain Calculation:
    base_strain = (avg_hr / estimated_max_hr) * duration_min * (1 + distance_km)
    load_multiplier = 1 + (vest_weight_lb / body_weight_lb)
    adjusted_strain = base_strain * load_multiplier
"""

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from N5.lib.paths import WELLNESS_DB, WORKOUTS_DB

# Default estimates if no data available
DEFAULT_BODY_WEIGHT_LB = 200.0
DEFAULT_MAX_HR = 185  # Can be refined with age: 220 - age


def get_wellness_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(WELLNESS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_body_weight_lb() -> float:
    """Fetch most recent body weight from workouts.db, convert to lbs."""
    try:
        conn = sqlite3.connect(WORKOUTS_DB)
        cur = conn.cursor()
        cur.execute("SELECT weight_kg FROM daily_weight ORDER BY date DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return row[0] * 2.205
    except Exception:
        pass
    return DEFAULT_BODY_WEIGHT_LB


def calculate_base_strain(duration_min: float, distance_km: float, avg_hr: float, peak_hr: float) -> float:
    """
    Calculate base strain score from workout metrics.
    
    Formula emphasizes:
    - Heart rate intensity (avg_hr / max_hr)
    - Duration (time under load)
    - Distance (work performed)
    """
    if not duration_min or not avg_hr:
        return 0.0
    
    # Use peak_hr as proxy for max HR if available, otherwise use default
    estimated_max_hr = max(peak_hr or DEFAULT_MAX_HR, DEFAULT_MAX_HR)
    
    # Intensity factor: how hard you worked relative to max capacity
    intensity = min(avg_hr / estimated_max_hr, 1.0)
    
    # Distance factor: add 1 to avoid zero multiplication for stationary workouts
    distance_factor = 1 + (distance_km or 0)
    
    # Base strain: intensity * duration * distance factor
    base_strain = intensity * duration_min * distance_factor
    
    return round(base_strain, 2)


def calculate_adjusted_strain(base_strain: float, vest_weight_lb: float, body_weight_lb: float) -> float:
    """
    Adjust strain score based on added load.
    
    A 16lb vest on a 200lb person = 8% increase in load = 8% increase in strain.
    """
    if not vest_weight_lb or vest_weight_lb <= 0:
        return base_strain
    
    load_multiplier = 1 + (vest_weight_lb / body_weight_lb)
    return round(base_strain * load_multiplier, 2)


def tag_workout(workout_id: int, vest_weight_lb: float) -> dict:
    """Tag a workout with vest weight and calculate adjusted strain."""
    conn = get_wellness_conn()
    cur = conn.cursor()
    
    # Fetch workout data
    cur.execute("""
        SELECT id, timestamp, duration_min, distance_km, avg_hr, peak_hr, calories
        FROM life_logs WHERE id = ?
    """, (workout_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return {"error": f"Workout ID {workout_id} not found"}
    
    # Calculate strain
    body_weight_lb = get_latest_body_weight_lb()
    base_strain = calculate_base_strain(
        row["duration_min"], row["distance_km"], row["avg_hr"], row["peak_hr"]
    )
    adjusted_strain = calculate_adjusted_strain(base_strain, vest_weight_lb, body_weight_lb)
    
    # Update record
    cur.execute("""
        UPDATE life_logs 
        SET vest_weight_lb = ?, adjusted_strain = ?
        WHERE id = ?
    """, (vest_weight_lb, adjusted_strain, workout_id))
    conn.commit()
    conn.close()
    
    return {
        "workout_id": workout_id,
        "timestamp": row["timestamp"],
        "vest_weight_lb": vest_weight_lb,
        "body_weight_lb": round(body_weight_lb, 1),
        "base_strain": base_strain,
        "adjusted_strain": adjusted_strain,
        "load_multiplier": round(1 + (vest_weight_lb / body_weight_lb), 3)
    }


def tag_recent_workouts(n: int, vest_weight_lb: float) -> list:
    """Tag the last N workouts with vest weight."""
    conn = get_wellness_conn()
    cur = conn.cursor()
    
    # Get workout category ID
    cur.execute("SELECT id FROM life_categories WHERE slug = 'workout'")
    cat_row = cur.fetchone()
    if not cat_row:
        conn.close()
        return [{"error": "Workout category not found"}]
    
    workout_cat_id = cat_row["id"]
    
    # Get last N workouts
    cur.execute("""
        SELECT id FROM life_logs 
        WHERE category_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (workout_cat_id, n))
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = tag_workout(row["id"], vest_weight_lb)
        results.append(result)
    
    return results


def remove_vest_tag(workout_id: int) -> dict:
    """Remove vest tag from a workout."""
    conn = get_wellness_conn()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE life_logs 
        SET vest_weight_lb = NULL, adjusted_strain = NULL
        WHERE id = ?
    """, (workout_id,))
    
    if cur.rowcount == 0:
        conn.close()
        return {"error": f"Workout ID {workout_id} not found"}
    
    conn.commit()
    conn.close()
    return {"workout_id": workout_id, "status": "vest tag removed"}


def list_vest_workouts() -> list:
    """List all workouts tagged with a weighted vest."""
    conn = get_wellness_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            ll.id,
            datetime(ll.timestamp) as date_time,
            ll.duration_min,
            ll.distance_km,
            ll.calories,
            ll.avg_hr,
            ll.peak_hr,
            ll.vest_weight_lb,
            ll.adjusted_strain
        FROM life_logs ll
        JOIN life_categories lc ON ll.category_id = lc.id
        WHERE lc.slug = 'workout' AND ll.vest_weight_lb IS NOT NULL
        ORDER BY ll.timestamp DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def recalculate_all_strain() -> dict:
    """Recalculate strain scores for all vest workouts."""
    conn = get_wellness_conn()
    cur = conn.cursor()
    body_weight_lb = get_latest_body_weight_lb()
    
    cur.execute("""
        SELECT id, duration_min, distance_km, avg_hr, peak_hr, vest_weight_lb
        FROM life_logs
        WHERE vest_weight_lb IS NOT NULL
    """)
    rows = cur.fetchall()
    
    updated = 0
    for row in rows:
        base_strain = calculate_base_strain(
            row["duration_min"], row["distance_km"], row["avg_hr"], row["peak_hr"]
        )
        adjusted_strain = calculate_adjusted_strain(base_strain, row["vest_weight_lb"], body_weight_lb)
        
        cur.execute("""
            UPDATE life_logs SET adjusted_strain = ? WHERE id = ?
        """, (adjusted_strain, row["id"]))
        updated += 1
    
    conn.commit()
    conn.close()
    
    return {"updated": updated, "body_weight_lb": round(body_weight_lb, 1)}


def main():
    parser = argparse.ArgumentParser(description="Weighted Vest Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # tag command
    tag_parser = subparsers.add_parser("tag", help="Tag a workout with vest weight")
    tag_parser.add_argument("workout_id", type=int, help="Workout ID from life_logs")
    tag_parser.add_argument("vest_weight_lb", type=float, help="Vest weight in pounds")
    
    # tag-recent command
    recent_parser = subparsers.add_parser("tag-recent", help="Tag last N workouts")
    recent_parser.add_argument("n", type=int, help="Number of recent workouts to tag")
    recent_parser.add_argument("vest_weight_lb", type=float, help="Vest weight in pounds")
    
    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove vest tag from workout")
    remove_parser.add_argument("workout_id", type=int, help="Workout ID")
    
    # list command
    subparsers.add_parser("list", help="List all vest workouts")
    
    # recalc command
    subparsers.add_parser("recalc", help="Recalculate all strain scores")
    
    args = parser.parse_args()
    
    if args.command == "tag":
        result = tag_workout(args.workout_id, args.vest_weight_lb)
        print_result(result)
    elif args.command == "tag-recent":
        results = tag_recent_workouts(args.n, args.vest_weight_lb)
        for r in results:
            print_result(r)
    elif args.command == "remove":
        result = remove_vest_tag(args.workout_id)
        print_result(result)
    elif args.command == "list":
        results = list_vest_workouts()
        if not results:
            print("No vest workouts found.")
        else:
            print(f"{'ID':<6} {'Date':<20} {'Dur':>6} {'Dist':>6} {'AvgHR':>6} {'Vest':>6} {'Strain':>8}")
            print("-" * 66)
            for r in results:
                print(f"{r['id']:<6} {r['date_time']:<20} {r['duration_min'] or 0:>6.1f} {r['distance_km'] or 0:>6.2f} {r['avg_hr'] or 0:>6.0f} {r['vest_weight_lb']:>6.0f} {r['adjusted_strain'] or 0:>8.1f}")
    elif args.command == "recalc":
        result = recalculate_all_strain()
        print_result(result)


def print_result(result: dict):
    """Pretty print a result dict."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()


if __name__ == "__main__":
    main()


