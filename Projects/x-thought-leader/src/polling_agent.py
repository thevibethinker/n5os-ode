#!/usr/bin/env python3
"""
W6: Tweet Polling Agent

Polls monitored X accounts every 15 minutes during approval hours.
Stores new tweets and updates polling state.

ARCHITECTURE: X List is primary SSOT for monitored accounts.
YAML remains as fallback/override source.
On each poll, we sync List → DB, then optionally YAML → DB, before polling.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

import pytz

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "config"))

from x_api import get_user_tweets
from account_sync import sync_accounts
from list_sync import sync_from_list

# Import settings
try:
    from settings import DEFAULT_LIST_ID
except ImportError:
    DEFAULT_LIST_ID = "1703516711629054447"  # Fallback

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("polling_agent")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"
ET = pytz.timezone('America/New_York')


def is_within_approval_hours() -> bool:
    """Check if current time is within 8am-10pm ET."""
    now = datetime.now(ET)
    return 8 <= now.hour < 22


def get_monitored_accounts(active_only: bool = True) -> list[dict]:
    """Get all monitored accounts ordered by priority."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    if active_only:
        accounts = conn.execute("""
            SELECT id, username, last_tweet_id, source
            FROM monitored_accounts
            WHERE active = 1 OR active IS NULL
            ORDER BY priority DESC
        """).fetchall()
    else:
        accounts = conn.execute("""
            SELECT id, username, last_tweet_id, source, active
            FROM monitored_accounts
            ORDER BY priority DESC
        """).fetchall()
    
    conn.close()
    return [dict(a) for a in accounts]


def store_tweet(tweet: dict, account_id: str, author_username: str) -> str:
    """Store a tweet to tweets.db. Returns tweet ID."""
    conn = sqlite3.connect(TWEETS_DB)
    
    # Check if already exists
    existing = conn.execute(
        "SELECT id FROM tweets WHERE id = ?", (tweet['id'],)
    ).fetchone()
    
    if existing:
        conn.close()
        return tweet['id']
    
    # Determine if reply
    is_reply = 0
    reply_to_id = None
    if tweet.get('referenced_tweets'):
        for ref in tweet['referenced_tweets']:
            if ref['type'] == 'replied_to':
                is_reply = 1
                reply_to_id = ref['id']
                break
    
    conn.execute("""
        INSERT INTO tweets (id, account_id, author_username, content, created_at, 
                           engagement_metrics, is_reply, reply_to_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new')
    """, (
        tweet['id'],
        account_id,
        author_username,
        tweet['text'],
        tweet['created_at'],
        json.dumps(tweet.get('public_metrics', {})),
        is_reply,
        reply_to_id
    ))
    conn.commit()
    conn.close()
    
    logger.info(f"Stored tweet {tweet['id']} from @{author_username}")
    return tweet['id']


def update_polling_state(account_id: str, last_tweet_id: str):
    """Update last_polled_at and last_tweet_id for an account."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.execute("""
        UPDATE monitored_accounts 
        SET last_polled_at = datetime('now'),
            last_tweet_id = ?
        WHERE id = ?
    """, (last_tweet_id, account_id))
    conn.commit()
    conn.close()


def poll_account(account: dict) -> list[str]:
    """Poll a single account, return new tweet IDs."""
    logger.info(f"Polling @{account['username']} (ID: {account['id']})")
    
    tweets = get_user_tweets(
        user_id=account['id'],
        since_id=account.get('last_tweet_id'),
        max_results=20
    )
    
    if not tweets:
        logger.info(f"No new tweets from @{account['username']}")
        return []
    
    new_ids = []
    latest_id = None
    
    for tweet in tweets:
        tweet_id = store_tweet(tweet, account['id'], account['username'])
        new_ids.append(tweet_id)
        
        # Track latest for pagination
        if not latest_id or tweet['id'] > latest_id:
            latest_id = tweet['id']
    
    if latest_id:
        update_polling_state(account['id'], latest_id)
    
    logger.info(f"Stored {len(new_ids)} new tweets from @{account['username']}")
    return new_ids


def poll_all_accounts(force: bool = False, list_id: str = None, skip_yaml: bool = False) -> list[str]:
    """Poll all monitored accounts."""
    if not force and not is_within_approval_hours():
        logger.info("Outside approval hours (8am-10pm ET), skipping poll")
        return []
    
    # Step 1: Sync from X List (primary SSOT)
    effective_list_id = list_id or DEFAULT_LIST_ID
    if effective_list_id:
        logger.info(f"Syncing accounts from X List {effective_list_id}...")
        try:
            list_stats = sync_from_list(effective_list_id)
            if list_stats.get("error"):
                logger.error(f"List sync failed: {list_stats['error']}")
            else:
                if list_stats["added"]:
                    logger.info(f"Added {len(list_stats['added'])} from list: {[a['username'] for a in list_stats['added']]}")
                if list_stats["removed"]:
                    logger.info(f"Deactivated {len(list_stats['removed'])} (removed from list): {[a['username'] for a in list_stats['removed']]}")
        except Exception as e:
            logger.error(f"Error syncing from list: {e}")
    
    # Step 2: Sync from YAML (fallback, unless --skip-yaml)
    if not skip_yaml:
        logger.info("Syncing accounts from YAML...")
        sync_stats = sync_accounts()
        if sync_stats["added"]:
            logger.info(f"Added {len(sync_stats['added'])} new accounts from YAML: {sync_stats['added']}")
    else:
        logger.info("Skipping YAML sync (--skip-yaml)")
    
    accounts = get_monitored_accounts(active_only=True)
    if not accounts:
        logger.warning("No monitored accounts found in database")
        return []
    
    logger.info(f"Polling {len(accounts)} active monitored accounts")
    
    all_new_ids = []
    for account in accounts:
        try:
            new_ids = poll_account(account)
            all_new_ids.extend(new_ids)
        except Exception as e:
            logger.error(f"Error polling @{account['username']}: {e}")
            continue
    
    logger.info(f"Total new tweets: {len(all_new_ids)}")
    return all_new_ids


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tweet Polling Agent")
    parser.add_argument("--force", action="store_true", help="Run even outside approval hours")
    parser.add_argument("--account", help="Poll specific account username only")
    parser.add_argument("--list-accounts", action="store_true", help="List monitored accounts")
    parser.add_argument("--list-id", help=f"X List ID to sync from (default: {DEFAULT_LIST_ID})")
    parser.add_argument("--skip-yaml", action="store_true", help="Skip YAML sync, use list only")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive accounts in --list-accounts")
    args = parser.parse_args()
    
    if args.list_accounts:
        accounts = get_monitored_accounts(active_only=not args.include_inactive)
        print(f"Monitored accounts ({len(accounts)}):")
        for a in accounts:
            source = a.get('source', 'yaml')
            active = a.get('active', 1)
            status = "✓" if active else "✗"
            print(f"  [{status}] @{a['username']} (ID: {a['id']}, source: {source})")
        return
    
    if args.account:
        conn = sqlite3.connect(TWEETS_DB)
        conn.row_factory = sqlite3.Row
        account = conn.execute(
            "SELECT * FROM monitored_accounts WHERE username = ?",
            (args.account,)
        ).fetchone()
        conn.close()
        
        if not account:
            print(f"Account @{args.account} not found in monitored accounts")
            sys.exit(1)
        
        new_ids = poll_account(dict(account))
        print(json.dumps({"new_tweet_ids": new_ids}))
    else:
        new_ids = poll_all_accounts(
            force=args.force, 
            list_id=args.list_id,
            skip_yaml=args.skip_yaml
        )
        print(json.dumps({"new_tweet_ids": new_ids}))


if __name__ == "__main__":
    main()



