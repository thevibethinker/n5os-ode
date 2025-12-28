#!/usr/bin/env python3
"""
Fitbit → Life Counter Bridge

Syncs Fitbit data to the Life Counter system:
1. Runs Fitbit sync to pull latest data
2. Counts workouts for today/yesterday
3. Increments the Life Counter 'workout' category

Usage:
    python3 fitbit_life_bridge.py sync [--days N]
    python3 fitbit_life_bridge.py status

This script is idempotent - it tracks which workout IDs have already been
counted in the Life Counter to avoid double-counting.
"""

import argparse
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

# Paths
WORKOUTS_DB = Path("/home/workspace/Personal/Health/workouts.db")
WELLNESS_DB = Path("/home/workspace/N5/data/wellness.db")
FITBIT_SYNC_SCRIPT = Path("/home/workspace/Personal/Health/WorkoutTracker/fitbit_sync.py")

# Bridge tracking table in wellness.db
BRIDGE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS fitbit_workout_bridge (
    workout_id INTEGER PRIMARY KEY,
    life_log_id INTEGER NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (life_log_id) REFERENCES life_logs(id)
)
"""


def get_wellness_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(WELLNESS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_workouts_conn() -> sqlite3.Connection:
    if not WORKOUTS_DB.exists():
        raise SystemExit(f"Workouts database not found: {WORKOUTS_DB}")
    conn = sqlite3.connect(WORKOUTS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_bridge_table(conn: sqlite3.Connection) -> None:
    """Create the bridge tracking table if it doesn't exist."""
    conn.execute(BRIDGE_TABLE_SQL)
    conn.commit()


def get_synced_workout_ids(conn: sqlite3.Connection) -> set:
    """Get set of workout IDs already synced to Life Counter."""
    cur = conn.execute("SELECT workout_id FROM fitbit_workout_bridge")
    return {row["workout_id"] for row in cur.fetchall()}


def get_workout_category_id(conn: sqlite3.Connection) -> int:
    """Get the 'workout' category ID from life_categories."""
    cur = conn.execute("SELECT id FROM life_categories WHERE slug = 'workout'")
    row = cur.fetchone()
    if not row:
        raise SystemExit("'workout' category not found in life_categories. Run life_counter.py add-category first.")
    return row["id"]


def get_recent_workouts(conn: sqlite3.Connection, days: int) -> List[dict]:
    """Get workouts from the last N days."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur = conn.execute(
        """
        SELECT id, date, start_time, primary_modality, duration_min, calories
        FROM workouts
        WHERE date >= ?
        ORDER BY date DESC, start_time DESC
        """,
        (cutoff,)
    )
    return [dict(row) for row in cur.fetchall()]


def increment_life_counter(conn: sqlite3.Connection, category_id: int, workout: dict) -> int:
    """Add a life_log entry for the workout and return the log ID."""
    # Use the workout's date/time for the timestamp
    if workout.get("start_time"):
        timestamp = workout["start_time"]
    else:
        timestamp = f"{workout['date']}T12:00:00"
    
    modality = workout.get("primary_modality") or "Exercise"
    duration = workout.get("duration_min")
    note = f"Fitbit: {modality}"
    if duration:
        note += f" ({int(duration)} min)"
    
    cur = conn.execute(
        """
        INSERT INTO life_logs (category_id, timestamp, value, source, note)
        VALUES (?, ?, 1, 'fitbit', ?)
        """,
        (category_id, timestamp, note)
    )
    conn.commit()
    return cur.lastrowid


def record_bridge(conn: sqlite3.Connection, workout_id: int, life_log_id: int) -> None:
    """Record that this workout has been synced."""
    conn.execute(
        "INSERT INTO fitbit_workout_bridge (workout_id, life_log_id) VALUES (?, ?)",
        (workout_id, life_log_id)
    )
    conn.commit()


def run_fitbit_sync(days: int) -> bool:
    """Run the Fitbit sync script. Returns True on success."""
    if not FITBIT_SYNC_SCRIPT.exists():
        print(f"Warning: Fitbit sync script not found: {FITBIT_SYNC_SCRIPT}", file=sys.stderr)
        return False
    
    print(f"Running Fitbit sync for last {days} days...")
    result = subprocess.run(
        ["python3", str(FITBIT_SYNC_SCRIPT), "sync-recent", "--days", str(days)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Fitbit sync failed: {result.stderr}", file=sys.stderr)
        return False
    
    if result.stdout:
        print(result.stdout)
    return True


def cmd_sync(days: int) -> None:
    """Main sync command: pull Fitbit data and update Life Counter."""
    # Step 1: Run Fitbit sync
    run_fitbit_sync(days)
    
    # Step 2: Open databases
    wellness_conn = get_wellness_conn()
    workouts_conn = get_workouts_conn()
    
    # Step 3: Ensure bridge table exists
    ensure_bridge_table(wellness_conn)
    
    # Step 4: Get already-synced workout IDs
    synced_ids = get_synced_workout_ids(wellness_conn)
    
    # Step 5: Get workout category ID
    category_id = get_workout_category_id(wellness_conn)
    
    # Step 6: Get recent workouts
    workouts = get_recent_workouts(workouts_conn, days)
    
    # Step 7: Sync new workouts to Life Counter
    new_count = 0
    for workout in workouts:
        workout_id = workout["id"]
        if workout_id in synced_ids:
            continue
        
        # Increment Life Counter
        life_log_id = increment_life_counter(wellness_conn, category_id, workout)
        record_bridge(wellness_conn, workout_id, life_log_id)
        
        modality = workout.get("primary_modality") or "Exercise"
        print(f"✅ Synced workout #{workout_id}: {modality} on {workout['date']} → life_log #{life_log_id}")
        new_count += 1
    
    if new_count == 0:
        print("No new workouts to sync.")
    else:
        print(f"\n✅ Synced {new_count} new workout(s) to Life Counter.")
    
    # Cleanup
    wellness_conn.close()
    workouts_conn.close()


def cmd_status() -> None:
    """Show sync status."""
    wellness_conn = get_wellness_conn()
    workouts_conn = get_workouts_conn()
    
    ensure_bridge_table(wellness_conn)
    
    # Count synced workouts
    cur = wellness_conn.execute("SELECT COUNT(*) as cnt FROM fitbit_workout_bridge")
    synced_count = cur.fetchone()["cnt"]
    
    # Count total workouts
    cur = workouts_conn.execute("SELECT COUNT(*) as cnt FROM workouts")
    total_workouts = cur.fetchone()["cnt"]
    
    # Count recent (last 7 days)
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cur = workouts_conn.execute("SELECT COUNT(*) as cnt FROM workouts WHERE date >= ?", (cutoff,))
    recent_workouts = cur.fetchone()["cnt"]
    
    synced_ids = get_synced_workout_ids(wellness_conn)
    cur = workouts_conn.execute("SELECT id FROM workouts WHERE date >= ?", (cutoff,))
    recent_ids = {row["id"] for row in cur.fetchall()}
    pending = len(recent_ids - synced_ids)
    
    print("Fitbit → Life Counter Bridge Status")
    print("=" * 40)
    print(f"Total workouts in Fitbit DB:    {total_workouts}")
    print(f"Workouts synced to Life Counter: {synced_count}")
    print(f"Recent workouts (last 7 days):   {recent_workouts}")
    print(f"Pending sync:                    {pending}")
    
    wellness_conn.close()
    workouts_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Fitbit → Life Counter Bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync Fitbit workouts to Life Counter")
    sync_parser.add_argument("--days", type=int, default=7, help="Days to sync (default: 7)")
    
    # status command
    subparsers.add_parser("status", help="Show sync status")
    
    args = parser.parse_args()
    
    if args.command == "sync":
        cmd_sync(args.days)
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()

