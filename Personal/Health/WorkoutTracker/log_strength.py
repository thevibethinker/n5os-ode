#!/usr/bin/env python3
"""
Log strength training sessions to workouts.db

Usage:
  python3 log_strength.py log --type upper --rpe 5 --duration 20 --notes "First circuit"
  python3 log_strength.py log --type upper --rpe 5 --exercises-json '[{"exercise":"push_ups","sets":1,"reps":8}]'
  python3 log_strength.py log --type upper --rpe 5 --deviation-notes "skipped rows, added extra push-ups"
  python3 log_strength.py recent              # Show last 7 sessions
  python3 log_strength.py recent --detail     # Show with exercise breakdown
  python3 log_strength.py soreness <id> "mild"  # Log next-day soreness
"""

import argparse
import sqlite3
import json
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "workouts.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def validate_exercises_json(exercises_str: str) -> str:
    """Validate and normalize exercises JSON."""
    if not exercises_str:
        return None
    try:
        exercises = json.loads(exercises_str)
        if not isinstance(exercises, list):
            raise ValueError("Exercises must be a JSON array")
        for ex in exercises:
            if not isinstance(ex, dict):
                raise ValueError("Each exercise must be an object")
            if "exercise" not in ex:
                raise ValueError("Each exercise must have 'exercise' field")
        return json.dumps(exercises)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

def log_session(args):
    conn = get_db()
    cur = conn.cursor()
    
    exercises_json = None
    if args.exercises_json:
        exercises_json = validate_exercises_json(args.exercises_json)
    
    # Combine deviation notes with general notes if both present
    full_notes = ""
    if args.deviation_notes:
        full_notes = f"[Deviations: {args.deviation_notes}]"
    if args.notes:
        full_notes = f"{full_notes} {args.notes}".strip() if full_notes else args.notes
    
    cur.execute("""
        INSERT INTO strength_sessions 
        (date, session_type, phase, duration_min, rpe, exercises_json, felt_before, felt_after, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args.date or date.today().isoformat(),
        args.type,
        args.phase or "ramp_week1",
        args.duration,
        args.rpe,
        exercises_json,
        args.felt_before,
        args.felt_after,
        full_notes or None
    ))
    
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Logged {args.type} session (ID: {session_id})")
    print(f"  Date: {args.date or date.today().isoformat()}")
    if args.rpe:
        print(f"  RPE: {args.rpe}/10")
    if args.duration:
        print(f"  Duration: {args.duration} min")
    if exercises_json:
        exercises = json.loads(exercises_json)
        print(f"  Exercises: {len(exercises)} logged")
        for ex in exercises:
            sets = ex.get('sets', 1)
            reps = ex.get('reps', '?')
            print(f"    - {ex['exercise']}: {sets}×{reps}")
    if args.deviation_notes:
        print(f"  Deviations: {args.deviation_notes}")
    if args.notes:
        print(f"  Notes: {args.notes}")

def show_recent(args):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, date, session_type, phase, duration_min, rpe, exercises_json, 
               felt_before, felt_after, soreness_next_day, notes
        FROM strength_sessions
        ORDER BY date DESC, created_at DESC
        LIMIT ?
    """, (args.limit or 7,))
    
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No strength sessions logged yet.")
        return
    
    print(f"Last {len(rows)} strength sessions:\n")
    for r in rows:
        soreness = f" → Next day: {r['soreness_next_day']}" if r['soreness_next_day'] else ""
        duration = f" ({r['duration_min']}min)" if r['duration_min'] else ""
        rpe_str = f"RPE {r['rpe']}/10" if r['rpe'] else "RPE ?"
        print(f"[{r['id']}] {r['date']} | {r['session_type']:10} | {rpe_str}{duration}{soreness}")
        
        if args.detail and r['exercises_json']:
            exercises = json.loads(r['exercises_json'])
            for ex in exercises:
                sets = ex.get('sets', 1)
                reps = ex.get('reps', '?')
                note = f" ({ex['notes']})" if ex.get('notes') else ""
                print(f"      • {ex['exercise']}: {sets}×{reps}{note}")
        
        if r['notes']:
            print(f"    {r['notes']}")

def log_soreness(args):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE strength_sessions 
        SET soreness_next_day = ?
        WHERE id = ?
    """, (args.level, args.session_id))
    
    if cur.rowcount == 0:
        print(f"No session found with ID {args.session_id}")
    else:
        print(f"✓ Logged soreness '{args.level}' for session {args.session_id}")
    
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Log strength training sessions")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # log command
    log_parser = subparsers.add_parser("log", help="Log a strength session")
    log_parser.add_argument("--type", "-t", required=True, 
                           choices=["upper", "lower", "core", "full_body", "mobility"],
                           help="Session type")
    log_parser.add_argument("--rpe", "-r", type=int, help="RPE 1-10")
    log_parser.add_argument("--duration", "-d", type=int, help="Duration in minutes")
    log_parser.add_argument("--phase", "-p", help="Training phase (default: ramp_week1)")
    log_parser.add_argument("--exercises-json", "-e", help="JSON array of exercises performed")
    log_parser.add_argument("--deviation-notes", help="What differed from baseline protocol")
    log_parser.add_argument("--felt-before", help="How you felt before")
    log_parser.add_argument("--felt-after", help="How you felt after")
    log_parser.add_argument("--notes", "-n", help="General notes")
    log_parser.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    log_parser.set_defaults(func=log_session)
    
    # recent command
    recent_parser = subparsers.add_parser("recent", help="Show recent sessions")
    recent_parser.add_argument("--limit", "-l", type=int, default=7, help="Number of sessions")
    recent_parser.add_argument("--detail", action="store_true", help="Show exercise breakdown")
    recent_parser.set_defaults(func=show_recent)
    
    # soreness command  
    soreness_parser = subparsers.add_parser("soreness", help="Log next-day soreness")
    soreness_parser.add_argument("session_id", type=int, help="Session ID")
    soreness_parser.add_argument("level", help="Soreness level (none, mild, moderate, severe)")
    soreness_parser.set_defaults(func=log_soreness)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()


