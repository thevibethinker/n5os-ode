import sqlite3
import json
import os

DB_PATH = "N5/data/scheduled_tasks.db"
JSONL_PATH = "N5/config/scheduled_tasks.jsonl"

def export_tasks():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    with open(JSONL_PATH, "w") as f:
        for row in rows:
            task = dict(row)
            # Ensure proper types if needed, though they seem to be strings
            f.write(json.dumps(task) + "\n")

    print(f"Exported {len(rows)} tasks to {JSONL_PATH}")
    conn.close()

if __name__ == "__main__":
    export_tasks()
