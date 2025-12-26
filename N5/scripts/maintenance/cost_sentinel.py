#!/usr/bin/env python3
"""
Cost Sentinel: Monitors scheduled task execution for runaway conditions.
Triggers system arrest if thresholds are exceeded.

Run periodically (e.g. every 15m) to ensure system safety.
"""

import sqlite3
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Paths
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "scheduled_tasks.db"
ARREST_FLAG = ROOT / "flags" / "ARREST_SYSTEM.json"
LOG_FILE = ROOT / "logs" / "cost_sentinel.log"

# Default Thresholds
# Can be overridden by env vars or future config
MAX_GLOBAL_RUNS_PER_HOUR = 60  # Risk: ~$X/hr depending on model
MAX_TASK_RUNS_PER_HOUR = 12    # Once every 5m is usually max for a single agent
MAX_FAILURES_PER_HOUR = 10     # If a task fails 10 times in an hour, stop it

def log(msg):
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def trigger_arrest(reason, details):
    """Write the arrest flag file."""
    data = {
        "reason": reason,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "trigger": "cost_sentinel"
    }
    
    ARREST_FLAG.parent.mkdir(parents=True, exist_ok=True)
    ARREST_FLAG.write_text(json.dumps(data, indent=2))
    log(f"⛔ SYSTEM ARREST TRIGGERED: {reason}")
    print(f"System arrested. Check {ARREST_FLAG} for details.")

def check_db():
    if not DB_PATH.exists():
        log("Database not found, skipping check.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Global Velocity Check
        cursor.execute(
            "SELECT count(*) as count FROM executions WHERE started_at > datetime('now', '-1 hour')"
        )
        global_count = cursor.fetchone()['count']
        
        if global_count > MAX_GLOBAL_RUNS_PER_HOUR:
            trigger_arrest(
                "Global Execution Velocity Exceeded",
                f"Global executions: {global_count}/hr (Limit: {MAX_GLOBAL_RUNS_PER_HOUR})"
            )
            return

        # 2. Task Velocity Check
        cursor.execute(
            """
            SELECT task_id, count(*) as count 
            FROM executions 
            WHERE started_at > datetime('now', '-1 hour') 
            GROUP BY task_id 
            HAVING count > ?
            """, (MAX_TASK_RUNS_PER_HOUR,)
        )
        rapid_tasks = cursor.fetchall()
        
        for task in rapid_tasks:
            trigger_arrest(
                f"Task Velocity Exceeded: {task['task_id']}",
                f"Task {task['task_id']} ran {task['count']} times in last hour (Limit: {MAX_TASK_RUNS_PER_HOUR})"
            )
            return

        # 3. Failure Storm Check (Specific task failing rapidly)
        # We look for tasks with > MAX_FAILURES_PER_HOUR failures in the last hour
        # Status 'failed' or 'error' (assuming these are the status codes)
        cursor.execute(
            """
            SELECT task_id, count(*) as count 
            FROM executions 
            WHERE started_at > datetime('now', '-1 hour') 
            AND (status = 'failed' OR status = 'error')
            GROUP BY task_id 
            HAVING count > ?
            """, (MAX_FAILURES_PER_HOUR,)
        )
        failing_tasks = cursor.fetchall()

        for task in failing_tasks:
            trigger_arrest(
                f"Failure Storm Detected: {task['task_id']}",
                f"Task {task['task_id']} failed {task['count']} times in last hour (Limit: {MAX_FAILURES_PER_HOUR})"
            )
            return

        log(f"Check complete. Status: OK. (Global: {global_count}/hr)")

    except Exception as e:
        log(f"Error during check: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if ARREST_FLAG.exists():
        print("System already arrested.")
        sys.exit(0)
    
    check_db()

