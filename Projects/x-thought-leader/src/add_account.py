#!/usr/bin/env python3
import sys
import sqlite3
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.x_api import XApiWrapper

def add_account(username: str, notes: str = None):
    """Add a new monitored account."""
    api = XApiWrapper()
    print(f"Fetching details for @{username}...")
    
    user_data = api.get_user_by_username(username)
    if not user_data:
        print(f"❌ Error: Could not find user @{username}")
        sys.exit(1)
        
    user_id = user_data['id']
    display_name = user_data['name']
    
    print(f"Found: {display_name} (ID: {user_id})")
    
    db_path = project_root / "db" / "tweets.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO monitored_accounts (user_id, username, display_name, notes)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, display_name, notes))
        conn.commit()
        print(f"✅ Successfully added @{username} to monitored accounts.")
    except sqlite3.IntegrityError:
        print(f"⚠️  Account @{username} is already being monitored.")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Add a Twitter/X account to monitor")
    parser.add_argument("username", help="X handle (without @)")
    parser.add_argument("--notes", help="Optional notes about this account")
    
    args = parser.parse_args()
    add_account(args.username, args.notes)

if __name__ == "__main__":
    main()

