#!/usr/bin/env python3
"""
X List Sync Module for Thought Leadership Engine

Syncs members from an X List (SSOT) to the monitored_accounts table.
Supports soft-delete for removed members, idempotent syncs, and dry-run mode.

Usage:
    python list_sync.py --list-id 1703516711629054447
    python list_sync.py --list-id 1703516711629054447 --dry-run
"""

# ---
# created: 2026-01-09
# last_edited: 2026-01-09
# version: 1.0
# provenance: con_nRtJ8573Bwl836An
# ---

import os
import sys
import argparse
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from x_api import get_list_info, get_list_members, XAPIError

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("list_sync")

# Default paths
DB_PATH = Path(__file__).parent.parent / "db" / "tweets.db"
DEFAULT_LIST_ID = "1703516711629054447"  # V's "Curated opinions" list


def get_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure monitored_accounts table has required columns."""
    cursor = conn.cursor()
    
    # Check if 'source' column exists
    cursor.execute("PRAGMA table_info(monitored_accounts)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'source' not in columns:
        logger.info("Adding 'source' column to monitored_accounts table")
        cursor.execute("ALTER TABLE monitored_accounts ADD COLUMN source TEXT DEFAULT 'yaml'")
        conn.commit()
    
    if 'active' not in columns:
        logger.info("Adding 'active' column to monitored_accounts table")
        cursor.execute("ALTER TABLE monitored_accounts ADD COLUMN active INTEGER DEFAULT 1")
        conn.commit()
    
    if 'synced_at' not in columns:
        logger.info("Adding 'synced_at' column to monitored_accounts table")
        cursor.execute("ALTER TABLE monitored_accounts ADD COLUMN synced_at TEXT")
        conn.commit()


def sync_from_list(
    list_id: str,
    dry_run: bool = False,
    db_path: Path = DB_PATH
) -> dict:
    """
    Sync X list members to monitored_accounts table.
    
    - Fetches all members from list
    - Adds new members to DB (source='list')
    - Marks members removed from list as inactive (soft delete)
    - Returns stats: {added: [], removed: [], unchanged: [], list_info: {}}
    
    Args:
        list_id: The X list ID to sync from
        dry_run: If True, don't make any DB changes
        db_path: Path to the SQLite database
        
    Returns:
        Dict with sync statistics
    """
    stats = {
        "added": [],
        "removed": [],
        "unchanged": [],
        "reactivated": [],
        "list_info": None,
        "error": None
    }
    
    # Get list info
    logger.info(f"Fetching list info for {list_id}...")
    try:
        list_info = get_list_info(list_id)
        if not list_info:
            stats["error"] = f"List {list_id} not found or not accessible"
            logger.error(stats["error"])
            return stats
        stats["list_info"] = list_info
        logger.info(f"List: {list_info.get('name')} ({list_info.get('member_count', '?')} members)")
    except XAPIError as e:
        stats["error"] = f"API error fetching list: {e}"
        logger.error(stats["error"])
        return stats
    
    # Get list members
    logger.info(f"Fetching members from list {list_id}...")
    try:
        members = get_list_members(list_id)
        logger.info(f"Fetched {len(members)} members from X API")
    except XAPIError as e:
        stats["error"] = f"API error fetching members: {e}"
        logger.error(stats["error"])
        return stats
    
    if not members:
        logger.warning("No members found in list")
    
    # Build lookup of current list members
    list_member_ids = {m['id'] for m in members}
    list_member_data = {m['id']: m for m in members}
    
    # Connect to DB
    conn = get_db_connection(db_path)
    ensure_schema(conn)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Get existing accounts from list source
    cursor.execute("""
        SELECT id, username, active FROM monitored_accounts 
        WHERE source = 'list'
    """)
    existing = {row['id']: dict(row) for row in cursor.fetchall()}
    existing_ids = set(existing.keys())
    
    # Determine changes
    to_add = list_member_ids - existing_ids
    to_remove = existing_ids - list_member_ids
    to_check = list_member_ids & existing_ids  # Already exist, check if reactivation needed
    
    # Process additions
    for user_id in to_add:
        user = list_member_data[user_id]
        username = user.get('username', '')
        name = user.get('name', '')
        description = user.get('description', '')
        metrics = user.get('public_metrics', {})
        followers = metrics.get('followers_count', 0)
        
        logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Adding @{username} (ID: {user_id})")
        stats["added"].append({"id": user_id, "username": username, "followers": followers})
        
        if not dry_run:
            cursor.execute("""
                INSERT INTO monitored_accounts (id, username, priority, source, active, synced_at, notes)
                VALUES (?, ?, ?, 'list', 1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    source = 'list',
                    active = 1,
                    synced_at = excluded.synced_at
            """, (user_id, username, 5, now, f"{name} | {followers} followers"))
    
    # Process removals (soft delete)
    for user_id in to_remove:
        user_info = existing.get(user_id, {})
        username = user_info.get('username', 'unknown')
        
        # Only mark as inactive if currently active
        if user_info.get('active', 1) == 1:
            logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Deactivating @{username} (ID: {user_id}) - removed from list")
            stats["removed"].append({"id": user_id, "username": username})
            
            if not dry_run:
                cursor.execute("""
                    UPDATE monitored_accounts 
                    SET active = 0, synced_at = ?
                    WHERE id = ?
                """, (now, user_id))
    
    # Check for reactivations (previously inactive, now back in list)
    for user_id in to_check:
        user_info = existing.get(user_id, {})
        username = user_info.get('username', 'unknown')
        
        if user_info.get('active', 1) == 0:
            logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Reactivating @{username} (ID: {user_id})")
            stats["reactivated"].append({"id": user_id, "username": username})
            
            if not dry_run:
                cursor.execute("""
                    UPDATE monitored_accounts 
                    SET active = 1, synced_at = ?
                    WHERE id = ?
                """, (now, user_id))
        else:
            # Update synced_at timestamp
            stats["unchanged"].append({"id": user_id, "username": username})
            if not dry_run:
                cursor.execute("""
                    UPDATE monitored_accounts SET synced_at = ? WHERE id = ?
                """, (now, user_id))
    
    if not dry_run:
        conn.commit()
    conn.close()
    
    # Summary
    logger.info(f"Sync complete: +{len(stats['added'])} added, -{len(stats['removed'])} removed, "
                f"~{len(stats['reactivated'])} reactivated, ={len(stats['unchanged'])} unchanged")
    
    return stats


def list_monitored_accounts(db_path: Path = DB_PATH, source: Optional[str] = None) -> list:
    """List all monitored accounts, optionally filtered by source."""
    conn = get_db_connection(db_path)
    ensure_schema(conn)
    cursor = conn.cursor()
    
    if source:
        cursor.execute("""
            SELECT id, username, priority, source, active, synced_at, notes
            FROM monitored_accounts
            WHERE source = ?
            ORDER BY priority DESC, username
        """, (source,))
    else:
        cursor.execute("""
            SELECT id, username, priority, source, active, synced_at, notes
            FROM monitored_accounts
            ORDER BY source, priority DESC, username
        """)
    
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def main():
    parser = argparse.ArgumentParser(description="Sync X List to monitored_accounts")
    parser.add_argument("--list-id", default=DEFAULT_LIST_ID, 
                        help=f"X List ID (default: {DEFAULT_LIST_ID})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without making changes")
    parser.add_argument("--list-accounts", action="store_true",
                        help="List current monitored accounts and exit")
    parser.add_argument("--source", choices=["list", "yaml", "manual"],
                        help="Filter accounts by source (with --list-accounts)")
    parser.add_argument("--db", type=Path, default=DB_PATH,
                        help=f"Database path (default: {DB_PATH})")
    
    args = parser.parse_args()
    
    if args.list_accounts:
        accounts = list_monitored_accounts(args.db, args.source)
        print(f"\nMonitored accounts ({len(accounts)}):")
        for acc in accounts:
            active = "✓" if acc.get('active', 1) else "✗"
            print(f"  [{active}] @{acc['username']} (ID: {acc['id']}, source: {acc.get('source', 'yaml')}, priority: {acc.get('priority', 5)})")
        return
    
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Syncing from X List {args.list_id}...")
    stats = sync_from_list(args.list_id, dry_run=args.dry_run, db_path=args.db)
    
    if stats.get("error"):
        print(f"\n❌ Error: {stats['error']}")
        sys.exit(1)
    
    print(f"\n✅ Sync {'would complete' if args.dry_run else 'complete'}:")
    print(f"   List: {stats['list_info'].get('name', 'Unknown')}")
    print(f"   Added: {len(stats['added'])}")
    for acc in stats['added']:
        print(f"      + @{acc['username']} ({acc['followers']} followers)")
    print(f"   Removed: {len(stats['removed'])}")
    for acc in stats['removed']:
        print(f"      - @{acc['username']}")
    print(f"   Reactivated: {len(stats['reactivated'])}")
    for acc in stats['reactivated']:
        print(f"      ↻ @{acc['username']}")
    print(f"   Unchanged: {len(stats['unchanged'])}")


if __name__ == "__main__":
    main()

