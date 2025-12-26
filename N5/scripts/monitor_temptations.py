#!/usr/bin/env python3
import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Since this script is run by an agent (Zo), we can't directly call Zo tools from Python easily
# unless we use the API. 
# HOWEVER, the agent instruction can be: 
# "Run this script. If it outputs 'TRIGGER_SMS', then send an SMS."
# OR, this script is purely for logic and the Agent does the heavy lifting.
# Let's make this script output a JSON action that the Agent can parse?
# No, the Agent reads stdout.

# BETTER APPROACH:
# The Agent Instruction will be:
# "Run `python3 N5/scripts/monitor_temptations.py`. 
# If the script outputs a message starting with 'ACTION: SMS', send that SMS to V."

DB_PATH = Path("/home/workspace/N5/data/journal.db")
STATE_FILE = Path("/home/workspace/N5/data/temptation_monitor.state")

def get_last_processed_id():
    if not STATE_FILE.exists():
        return 0
    try:
        return int(STATE_FILE.read_text().strip())
    except:
        return 0

def update_last_processed_id(entry_id):
    STATE_FILE.write_text(str(entry_id))

def main():
    if not DB_PATH.exists():
        return

    last_id = get_last_processed_id()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find oldest unprocessed temptation entry
    cursor.execute("""
        SELECT id, created_at, content 
        FROM journal_entries 
        WHERE entry_type = 'temptation' AND id > ?
        ORDER BY id ASC
        LIMIT 1
    """, (last_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("NO_ACTION")
        return

    # Check time
    created_at = datetime.fromisoformat(row['created_at'])
    now = datetime.now()
    diff = now - created_at
    
    # If it's been at least 2 hours (and less than 24h - don't nag about old stuff)
    if timedelta(hours=2) <= diff <= timedelta(hours=24):
        print(f"ACTION: SMS | Hey V, checking in on the temptation you noted earlier ({diff.seconds//3600}h ago). How are you holding up?")
        update_last_processed_id(row['id'])
    elif diff > timedelta(hours=24):
        # Too old, just skip it
        update_last_processed_id(row['id'])
        print("NO_ACTION (Skipped old entry)")
    else:
        # Too soon
        print(f"WAITING (Only {diff.seconds//60} mins elapsed)")

if __name__ == "__main__":
    main()

