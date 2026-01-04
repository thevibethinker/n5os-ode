#!/usr/bin/env python3
from N5.lib.paths import WORKOUTS_DB, WORKOUT_TRACKER_DIR
"""
Workout Prescription Engine v2.0

LLM-powered prescription generator. Python handles:
- Data gathering (Fitbit readiness, cycle position)
- Reading source plan files

LLM handles:
- Interpreting the plans
- Synthesizing 10K + Jair programs
- Generating contextual prescription

Usage:
    python3 workout_prescriber.py              # Today's prescription
    python3 workout_prescriber.py 2026-01-05   # Specific date
    python3 workout_prescriber.py --status     # Show cycle status (no LLM)
    python3 workout_prescriber.py --data-only  # Just show data, no LLM call
"""

import sqlite3
import json
import argparse
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DB_PATH = WORKOUTS_DB
CYCLE_START = datetime(2026, 1, 4)  # Cycle restart: Sunday Jan 4, 2026 (Day 1 = active day per user preference)

# Plan file locations
TENK_PLAN_PATH = WORKOUT_TRACKER_DIR / "10K_Prep_Plan.md")
JAIR_PLAN_PATH = WORKOUT_TRACKER_DIR / "Jair-Lee-Training-Program-Phase1.md")


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def get_cycle_info(target_date: datetime) -> Dict[str, Any]:
    """Calculate week number and day of cycle."""
    days_since_start = (target_date - CYCLE_START).days
    
    if days_since_start < 0:
        return {"in_cycle": False, "message": f"Date is before cycle start ({CYCLE_START.date()})"}
    
    week_number = (days_since_start // 7) + 1
    day_of_cycle = (days_since_start % 7) + 1  # 1-7
    day_of_week = target_date.weekday()  # 0=Mon, 6=Sun
    
    # Map to plan terminology
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    return {
        "in_cycle": True,
        "week_number": week_number,
        "day_of_cycle": day_of_cycle,
        "day_of_week": day_of_week,
        "day_name": day_names[day_of_week],
        "date": target_date.strftime("%Y-%m-%d"),
        "date_formatted": target_date.strftime("%A, %B %d, %Y"),
        "days_since_start": days_since_start,
    }


def get_readiness_data(target_date: datetime) -> Dict[str, Any]:
    """Gather Fitbit readiness data from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    date_str = target_date.strftime("%Y-%m-%d")
    
    # Get current RHR
    cursor.execute("SELECT resting_hr FROM daily_resting_hr WHERE date = ?", (date_str,))
    row = cursor.fetchone()
    current_rhr = row[0] if row else None
    
    # Get 14-day RHR baseline
    baseline_start = (target_date - timedelta(days=14)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT AVG(resting_hr) FROM daily_resting_hr 
        WHERE date BETWEEN ? AND ? AND date != ?
    """, (baseline_start, date_str, date_str))
    row = cursor.fetchone()
    baseline_rhr = row[0] if row and row[0] else None
    
    # Get sleep data
    cursor.execute("""
        SELECT efficiency, duration_min FROM sleep_sessions 
        WHERE date = ? AND is_main_sleep = 1
    """, (date_str,))
    row = cursor.fetchone()
    sleep_efficiency = row[0] if row else None
    sleep_duration_min = row[1] if row else None
    
    # Get recent workout history (last 7 days)
    week_ago = (target_date - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT date, primary_modality, duration_min, avg_hr, notes 
        FROM workouts 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    """, (week_ago, date_str))
    recent_workouts = [
        {"date": r[0], "type": r[1], "duration_min": round(r[2], 1) if r[2] else None, 
         "avg_hr": round(r[3], 1) if r[3] else None, "notes": r[4]}
        for r in cursor.fetchall()
    ]
    
    # Get strength session history
    cursor.execute("""
        SELECT date, session_type, exercises_json, notes 
        FROM strength_sessions 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    """, (week_ago, date_str))
    recent_strength = [
        {"date": r[0], "session_type": r[1], "exercises": r[2], "notes": r[3]}
        for r in cursor.fetchall()
    ]
    
    conn.close()
    
    # Calculate simple readiness score for context
    rhr_score = 100
    if current_rhr and baseline_rhr:
        rhr_delta = current_rhr - baseline_rhr
        rhr_score = max(0, min(100, 100 - (rhr_delta * 10)))
    
    sleep_eff_score = sleep_efficiency if sleep_efficiency else 80
    sleep_dur_score = min(100, (sleep_duration_min / 420) * 100) if sleep_duration_min else 80
    
    readiness_score = (rhr_score * 0.4) + (sleep_eff_score * 0.3) + (sleep_dur_score * 0.3)
    
    return {
        "rhr_current": current_rhr,
        "rhr_baseline": round(baseline_rhr, 1) if baseline_rhr else None,
        "rhr_delta": round(current_rhr - baseline_rhr, 1) if current_rhr and baseline_rhr else None,
        "sleep_efficiency_pct": sleep_efficiency,
        "sleep_duration_min": sleep_duration_min,
        "sleep_duration_hours": round(sleep_duration_min / 60, 1) if sleep_duration_min else None,
        "readiness_score": round(readiness_score, 1),
        "recent_workouts": recent_workouts,
        "recent_strength_sessions": recent_strength,
    }


def read_plan_files() -> Dict[str, str]:
    """Read the actual training plan markdown files."""
    plans = {}
    
    if TENK_PLAN_PATH.exists():
        plans["10k_plan"] = TENK_PLAN_PATH.read_text()
    else:
        plans["10k_plan"] = f"ERROR: Plan file not found at {TENK_PLAN_PATH}"
    
    if JAIR_PLAN_PATH.exists():
        plans["jair_plan"] = JAIR_PLAN_PATH.read_text()
    else:
        plans["jair_plan"] = f"ERROR: Plan file not found at {JAIR_PLAN_PATH}"
    
    return plans


def call_llm_for_prescription(cycle_info: Dict, readiness: Dict, plans: Dict) -> str:
    """Call Zo LLM API to generate the prescription."""
    
    prompt = f"""You are a workout prescription engine. Your job is to tell V exactly what workout to do today.

## TODAY'S CONTEXT
- Date: {cycle_info['date_formatted']}
- Day of week: {cycle_info['day_name']}
- Training cycle: Week {cycle_info['week_number']}, Day {cycle_info['day_of_cycle']}
- Cycle started: 2026-01-04 (Sunday)

## READINESS DATA (from Fitbit)
- Resting HR: {readiness['rhr_current']} bpm (baseline: {readiness['rhr_baseline']}, delta: {readiness['rhr_delta']})
- Sleep last night: {readiness['sleep_duration_hours']} hours, {readiness['sleep_efficiency_pct']}% efficiency
- Calculated readiness score: {readiness['readiness_score']}/100

## RECENT WORKOUT HISTORY (last 7 days)
{json.dumps(readiness['recent_workouts'], indent=2) if readiness['recent_workouts'] else "No workouts logged"}

## RECENT STRENGTH SESSIONS
{json.dumps(readiness['recent_strength_sessions'], indent=2) if readiness['recent_strength_sessions'] else "No strength sessions logged"}

## V'S 10K TRAINING PLAN (PRIMARY)
```markdown
{plans['10k_plan']}
```

## JAIR LEE STRENGTH PROGRAM (SECONDARY - for strength days)
```markdown
{plans['jair_plan']}
```

## YOUR TASK
Based on the plans above and today's context:

1. Determine what TODAY's workout should be according to the synthesized plan
2. If it's a strength day, pull the specific exercises from Jair's program
3. Adjust intensity if readiness is low (<70: reduce intensity, <50: active recovery only, <40: rest)
4. Consider what V has done recently to avoid overtraining

Output a clear, actionable prescription in this format:

**TODAY'S WORKOUT: [TYPE]**
Duration: X minutes
[If strength: list the specific exercises with sets/reps]
[If cardio: specify zone and any intervals]

**READINESS ADJUSTMENT:** [None / Reduced intensity / Active recovery only / Rest recommended]

**RATIONALE:** Brief explanation of why this workout fits today based on the plan and readiness.
"""

    # Call Zo API
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        return "ERROR: ZO_CLIENT_IDENTITY_TOKEN not available. Run with --data-only to see gathered data."
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result.get("output", "ERROR: No output in response")
    except requests.exceptions.RequestException as e:
        return f"ERROR calling Zo API: {e}"


def get_prescription(target_date: Optional[datetime] = None, data_only: bool = False) -> str:
    """Generate workout prescription for a date."""
    if target_date is None:
        target_date = datetime.now()
    
    cycle_info = get_cycle_info(target_date)
    
    if not cycle_info["in_cycle"]:
        return f"❌ {cycle_info['message']}"
    
    readiness = get_readiness_data(target_date)
    plans = read_plan_files()
    
    if data_only:
        return json.dumps({
            "cycle_info": cycle_info,
            "readiness": readiness,
            "plans_loaded": {
                "10k_plan": "loaded" if "ERROR" not in plans["10k_plan"] else plans["10k_plan"],
                "jair_plan": "loaded" if "ERROR" not in plans["jair_plan"] else plans["jair_plan"],
            }
        }, indent=2, default=str)
    
    # Call LLM for intelligent prescription
    prescription = call_llm_for_prescription(cycle_info, readiness, plans)
    
    header = f"""📅 {cycle_info['date_formatted']}
📊 Week {cycle_info['week_number']}, Day {cycle_info['day_of_cycle']} of training cycle
🔋 Readiness: {readiness['readiness_score']}/100

---

{prescription}
"""
    return header


def show_cycle_status():
    """Show current cycle status (no LLM needed)."""
    today = datetime.now()
    
    lines = [
        "=" * 50,
        "TRAINING CYCLE STATUS",
        "=" * 50,
        f"Cycle Start: {CYCLE_START.date()} (Sunday)",
        f"Today: {today.strftime('%Y-%m-%d %A')}",
        "",
    ]
    
    cycle_info = get_cycle_info(today)
    if cycle_info["in_cycle"]:
        lines.extend([
            f"Week: {cycle_info['week_number']}",
            f"Day of Cycle: {cycle_info['day_of_cycle']}",
            f"Days Since Start: {cycle_info['days_since_start']}",
            "",
            "Plan files:",
            f"  10K: {TENK_PLAN_PATH} ({'exists' if TENK_PLAN_PATH.exists() else 'MISSING'})",
            f"  Jair: {JAIR_PLAN_PATH} ({'exists' if JAIR_PLAN_PATH.exists() else 'MISSING'})",
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Workout Prescription Engine (LLM-powered)")
    parser.add_argument("date", nargs="?", help="Date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--status", action="store_true", help="Show cycle status (no LLM)")
    parser.add_argument("--data-only", action="store_true", help="Show gathered data without LLM call")
    
    args = parser.parse_args()
    
    if args.status:
        print(show_cycle_status())
        return
    
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_date = datetime.now()
    
    result = get_prescription(target_date, data_only=args.data_only)
    print(result)


if __name__ == "__main__":
    main()



