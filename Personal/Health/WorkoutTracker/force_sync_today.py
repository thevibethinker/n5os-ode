import sys
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/workspace/Personal/Health/WorkoutTracker")
sys.path.append(str(BASE_DIR))

import fitbit_sync
import workout_tracker

def force_sync():
    conn = workout_tracker.get_connection()
    cfg = fitbit_sync.load_config()
    token = fitbit_sync.ensure_access_token(cfg)
    
    # Use today's date
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Force syncing intraday for {date_str}...")
    
    # Call the internal sync function
    fitbit_sync._sync_intraday_for_date(conn, workout_tracker, token, date_str)
    print("Done.")

if __name__ == "__main__":
    force_sync()
