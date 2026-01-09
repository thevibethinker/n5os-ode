#!/usr/bin/env python3
"""
Account Sync: YAML → DB synchronization for monitored accounts.

Single Source of Truth: config/monitored_accounts.yaml
This module syncs that YAML to the DB, resolving X user IDs via API as needed.
"""

import sys
import sqlite3
import logging
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from x_api import get_user_id

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("account_sync")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"
ACCOUNTS_YAML = PROJECT_ROOT / "config" / "monitored_accounts.yaml"


def load_yaml_accounts() -> list[dict]:
    """Load verified accounts from YAML config."""
    if not ACCOUNTS_YAML.exists():
        logger.error(f"Config file not found: {ACCOUNTS_YAML}")
        return []
    
    with open(ACCOUNTS_YAML) as f:
        data = yaml.safe_load(f)
    
    candidates = data.get("candidates", [])
    # Only return verified accounts
    verified = [c for c in candidates if c.get("verified", False)]
    logger.info(f"Loaded {len(verified)} verified accounts from YAML")
    return verified


def get_db_accounts() -> dict[str, dict]:
    """Get current monitored accounts from DB, keyed by username."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM monitored_accounts").fetchall()
    conn.close()
    return {r["username"]: dict(r) for r in rows}


def resolve_user_id(username: str) -> tuple[str, str] | None:
    """Resolve X username to user ID via API. Returns (user_id, display_name) or None."""
    try:
        user_id = get_user_id(username)
        if user_id:
            # For now, use username as display_name since get_user_id only returns ID
            return user_id, username
    except Exception as e:
        logger.error(f"API error resolving @{username}: {e}")
    return None


def sync_accounts(dry_run: bool = False) -> dict:
    """
    Sync YAML accounts to DB.
    
    Returns stats: {added: [], skipped: [], failed: [], removed: []}
    """
    yaml_accounts = load_yaml_accounts()
    db_accounts = get_db_accounts()
    
    stats = {"added": [], "skipped": [], "failed": [], "removed": []}
    
    yaml_usernames = set()
    
    for account in yaml_accounts:
        # Clean handle (remove @)
        handle = account["handle"].lstrip("@").lower()
        yaml_usernames.add(handle)
        
        if handle in db_accounts:
            stats["skipped"].append(handle)
            logger.debug(f"@{handle} already in DB, skipping")
            continue
        
        # Need to add - resolve user ID first
        logger.info(f"Resolving @{handle}...")
        result = resolve_user_id(handle)
        
        if not result:
            stats["failed"].append(handle)
            logger.warning(f"Could not resolve @{handle}, skipping")
            continue
        
        user_id, display_name = result
        
        if dry_run:
            logger.info(f"[DRY RUN] Would add @{handle} (ID: {user_id})")
            stats["added"].append(handle)
            continue
        
        # Insert into DB
        conn = sqlite3.connect(TWEETS_DB)
        try:
            conn.execute("""
                INSERT INTO monitored_accounts 
                (id, username, display_name, category, priority, added_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                user_id,
                handle,
                display_name,
                account.get("category", "general"),
                10  # default priority
            ))
            conn.commit()
            stats["added"].append(handle)
            logger.info(f"✅ Added @{handle} (ID: {user_id})")
        except sqlite3.IntegrityError as e:
            logger.warning(f"DB error adding @{handle}: {e}")
            stats["failed"].append(handle)
        finally:
            conn.close()
    
    # Check for accounts in DB but not in YAML (orphans)
    for db_username in db_accounts:
        if db_username.lower() not in yaml_usernames:
            stats["removed"].append(db_username)
            logger.warning(f"⚠️  @{db_username} in DB but not in YAML (orphan)")
    
    return stats


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Sync monitored accounts from YAML to DB")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    stats = sync_accounts(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(stats))
    else:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Sync complete:")
        print(f"  Added:   {len(stats['added'])} - {stats['added']}")
        print(f"  Skipped: {len(stats['skipped'])} (already in DB)")
        print(f"  Failed:  {len(stats['failed'])} - {stats['failed']}")
        if stats["removed"]:
            print(f"  Orphans: {len(stats['removed'])} - {stats['removed']} (in DB but not YAML)")


if __name__ == "__main__":
    main()


