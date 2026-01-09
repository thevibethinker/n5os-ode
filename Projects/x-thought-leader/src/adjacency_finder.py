#!/usr/bin/env python3
"""
Second-Order Adjacency Finder

Finds small (1K-5K followers) but high-engagement accounts that orbit V's power mutuals.
These accounts would be impressed by V's mutual connections and likely to follow back.

Strategy:
1. Get recent tweets from power mutuals
2. Find who replies to those tweets
3. Calculate "clout score" = engagement / followers
4. Filter for 1K-5K followers + high clout
5. Surface as candidates for V to engage with
"""

import os
import sys
import json
import sqlite3
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import requests

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "tweets.db"

# Thresholds
MIN_FOLLOWERS = 500       # Too small = not worth it
MAX_FOLLOWERS = 5000      # Too big = won't be impressed by V's mutuals
MIN_CLOUT_SCORE = 0.02    # engagement_rate > 2% is good
MIN_TWEET_COUNT = 50      # Need enough history to judge
POWER_MUTUAL_MIN_FOLLOWERS = 10000  # What counts as a "power mutual"


def get_bearer_token():
    return os.environ.get('X_BEARER_TOKEN')


def api_get(endpoint, params=None):
    """Make authenticated GET request to X API."""
    bearer = get_bearer_token()
    if not bearer:
        logger.error("X_BEARER_TOKEN not set")
        return None
    
    headers = {"Authorization": f"Bearer {bearer}"}
    url = f"https://api.x.com/2/{endpoint}"
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            logger.warning("Rate limited")
            return None
        else:
            logger.error(f"API error {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        logger.error(f"Request error: {e}")
        return None


def init_db():
    """Create adjacency_candidates table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adjacency_candidates (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT,
            followers INTEGER,
            following INTEGER,
            tweet_count INTEGER,
            clout_score REAL,
            engagement_sources TEXT,  -- JSON: which power mutuals they engage with
            discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',  -- pending, approved, rejected, monitoring
            reviewed_at TEXT,
            notes TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")


def get_power_mutuals():
    """Get power mutuals from the DuckDB export or monitored accounts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get high-follower monitored accounts as power mutuals
    cursor.execute("""
        SELECT id, username 
        FROM monitored_accounts 
        WHERE active = 1
    """)
    
    accounts = cursor.fetchall()
    conn.close()
    
    # Look up follower counts
    power_mutuals = []
    for user_id, username in accounts:
        data = api_get(f"users/{user_id}", {"user.fields": "public_metrics"})
        if data and 'data' in data:
            followers = data['data'].get('public_metrics', {}).get('followers_count', 0)
            if followers >= POWER_MUTUAL_MIN_FOLLOWERS:
                power_mutuals.append({
                    'id': user_id,
                    'username': username,
                    'followers': followers
                })
    
    return power_mutuals


def get_power_mutuals_fast():
    """Get power mutuals without extra API calls (use known list)."""
    # Hardcoded from earlier analysis - these are V's actual power mutuals
    return [
        {'id': '16350505', 'username': 'asanwal', 'followers': 61000},
        {'id': '1506474516', 'username': 'Gunnersc0m', 'followers': 414000},
        {'id': '389536683', 'username': 'PhilTorres', 'followers': 38000},
        {'id': '1526623271613091841', 'username': 'LorimerVentures', 'followers': 4000},
        {'id': '14434288', 'username': 'andruyeung', 'followers': 66000},
    ]


def find_engagers_of_power_mutuals(power_mutuals, max_per_mutual=50):
    """
    Find accounts that reply to power mutuals' tweets.
    These are the second-order adjacency targets.
    """
    engagers = defaultdict(lambda: {'count': 0, 'sources': [], 'user_data': None})
    
    for pm in power_mutuals:
        username = pm['username']
        logger.info(f"Searching for replies to @{username}...")
        
        # Search for recent replies to this power mutual
        # Using search query: "to:username" gets replies
        data = api_get("tweets/search/recent", {
            "query": f"to:{username} -is:retweet",
            "max_results": max_per_mutual,
            "tweet.fields": "author_id,public_metrics,created_at",
            "expansions": "author_id",
            "user.fields": "id,username,name,public_metrics,description"
        })
        
        if not data:
            continue
        
        # Extract users from includes
        users = {}
        if 'includes' in data and 'users' in data['includes']:
            for u in data['includes']['users']:
                users[u['id']] = u
        
        # Process tweets
        tweets = data.get('data', [])
        logger.info(f"  Found {len(tweets)} replies to @{username}")
        
        for tweet in tweets:
            author_id = tweet.get('author_id')
            if author_id and author_id in users:
                user = users[author_id]
                engagers[author_id]['count'] += 1
                engagers[author_id]['sources'].append(username)
                engagers[author_id]['user_data'] = user
    
    return engagers


def calculate_clout_score(user_data):
    """
    Calculate clout score = average engagement per tweet / followers.
    Higher = punches above weight.
    """
    metrics = user_data.get('public_metrics', {})
    followers = metrics.get('followers_count', 1)
    tweet_count = metrics.get('tweet_count', 1)
    
    if followers < 1 or tweet_count < 1:
        return 0
    
    # We don't have per-tweet engagement, so use listed_count as a proxy
    # listed_count = how many lists they're on = indicator of influence
    listed = metrics.get('listed_count', 0)
    
    # Simple heuristic: listed_count / followers
    # Also factor in tweet_count (more active = more engaged)
    activity_score = min(tweet_count / 1000, 1)  # Cap at 1
    list_ratio = listed / max(followers, 1)
    
    # Clout score combines list influence with activity
    clout = (list_ratio * 100) + (activity_score * 0.5)
    
    return round(clout, 4)


def filter_candidates(engagers):
    """
    Filter engagers to find high-clout small accounts.
    """
    candidates = []
    
    for user_id, data in engagers.items():
        user = data['user_data']
        if not user:
            continue
        
        metrics = user.get('public_metrics', {})
        followers = metrics.get('followers_count', 0)
        tweet_count = metrics.get('tweet_count', 0)
        
        # Filter by size
        if followers < MIN_FOLLOWERS or followers > MAX_FOLLOWERS:
            continue
        
        # Filter by activity
        if tweet_count < MIN_TWEET_COUNT:
            continue
        
        # Calculate clout
        clout_score = calculate_clout_score(user)
        
        candidates.append({
            'user_id': user_id,
            'username': user.get('username'),
            'name': user.get('name'),
            'description': user.get('description', '')[:100],
            'followers': followers,
            'following': metrics.get('following_count', 0),
            'tweet_count': tweet_count,
            'listed_count': metrics.get('listed_count', 0),
            'clout_score': clout_score,
            'engagement_count': data['count'],
            'sources': list(set(data['sources']))
        })
    
    # Sort by engagement count (how many power mutuals they engage with) then clout
    candidates.sort(key=lambda x: (x['engagement_count'], x['clout_score']), reverse=True)
    
    return candidates


def save_candidates(candidates):
    """Save candidates to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved = 0
    for c in candidates:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO adjacency_candidates 
                (user_id, username, name, followers, following, tweet_count, 
                 clout_score, engagement_sources, discovered_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT status FROM adjacency_candidates WHERE user_id = ?), 'pending'))
            """, (
                c['user_id'], c['username'], c['name'], c['followers'],
                c['following'], c['tweet_count'], c['clout_score'],
                json.dumps(c['sources']), datetime.utcnow().isoformat(),
                c['user_id']
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Error saving {c['username']}: {e}")
    
    conn.commit()
    conn.close()
    
    return saved


def discover_candidates(use_fast=True):
    """Main discovery pipeline."""
    init_db()
    
    # Get power mutuals
    if use_fast:
        power_mutuals = get_power_mutuals_fast()
    else:
        power_mutuals = get_power_mutuals()
    
    logger.info(f"Using {len(power_mutuals)} power mutuals")
    for pm in power_mutuals:
        logger.info(f"  @{pm['username']} ({pm['followers']:,} followers)")
    
    # Find engagers
    engagers = find_engagers_of_power_mutuals(power_mutuals)
    logger.info(f"Found {len(engagers)} unique engagers")
    
    # Filter candidates
    candidates = filter_candidates(engagers)
    logger.info(f"Filtered to {len(candidates)} candidates (1K-5K followers, high clout)")
    
    # Save to DB
    saved = save_candidates(candidates)
    logger.info(f"Saved {saved} candidates to database")
    
    return candidates


def list_candidates(status='pending', limit=20):
    """List candidates from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, username, name, followers, clout_score, 
               engagement_sources, discovered_at, status
        FROM adjacency_candidates
        WHERE status = ?
        ORDER BY clout_score DESC
        LIMIT ?
    """, (status, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def approve_candidate(username):
    """Approve a candidate and add to monitored_accounts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get candidate
    cursor.execute("""
        SELECT user_id, username, followers FROM adjacency_candidates 
        WHERE username = ? OR user_id = ?
    """, (username, username))
    
    row = cursor.fetchone()
    if not row:
        print(f"Candidate not found: {username}")
        conn.close()
        return False
    
    user_id, uname, followers = row
    
    # Add to monitored_accounts
    cursor.execute("""
        INSERT OR IGNORE INTO monitored_accounts (id, username, priority, source, active)
        VALUES (?, ?, 8, 'adjacency', 1)
    """, (user_id, uname))
    
    # Update candidate status
    cursor.execute("""
        UPDATE adjacency_candidates 
        SET status = 'approved', reviewed_at = ?
        WHERE user_id = ?
    """, (datetime.utcnow().isoformat(), user_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Approved @{uname} ({followers:,} followers) → added to monitoring")
    return True


def reject_candidate(username):
    """Reject a candidate."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE adjacency_candidates 
        SET status = 'rejected', reviewed_at = ?
        WHERE username = ? OR user_id = ?
    """, (datetime.utcnow().isoformat(), username, username))
    
    conn.commit()
    conn.close()
    print(f"❌ Rejected {username}")


def main():
    parser = argparse.ArgumentParser(description='Second-Order Adjacency Finder')
    parser.add_argument('--discover', action='store_true', help='Run discovery pipeline')
    parser.add_argument('--list', action='store_true', help='List pending candidates')
    parser.add_argument('--status', default='pending', help='Filter by status (pending/approved/rejected)')
    parser.add_argument('--limit', type=int, default=20, help='Limit results')
    parser.add_argument('--approve', type=str, help='Approve a candidate by username')
    parser.add_argument('--reject', type=str, help='Reject a candidate by username')
    parser.add_argument('--approve-all', action='store_true', help='Approve all pending candidates')
    
    args = parser.parse_args()
    
    if args.discover:
        print("=" * 60)
        print("SECOND-ORDER ADJACENCY FINDER")
        print("Finding small high-clout accounts in your power mutuals' orbit")
        print("=" * 60)
        print()
        
        candidates = discover_candidates()
        
        print()
        print("=" * 60)
        print(f"TOP CANDIDATES ({len(candidates)} found)")
        print("=" * 60)
        print()
        print(f"{'Username':<20} {'Followers':>10} {'Clout':>8} {'Engages':>8} Sources")
        print("-" * 80)
        
        for c in candidates[:20]:
            sources = ', '.join(c['sources'][:2])
            if len(c['sources']) > 2:
                sources += f" +{len(c['sources'])-2}"
            print(f"@{c['username']:<19} {c['followers']:>10,} {c['clout_score']:>8.2f} {c['engagement_count']:>8} {sources}")
        
        print()
        print(f"Run `--list` to see all, `--approve <username>` to add to monitoring")
        
    elif args.list:
        rows = list_candidates(args.status, args.limit)
        
        print(f"\n{'Username':<20} {'Followers':>10} {'Clout':>8} Status")
        print("-" * 50)
        
        for row in rows:
            user_id, username, name, followers, clout, sources, discovered, status = row
            print(f"@{username:<19} {followers:>10,} {clout:>8.2f} {status}")
    
    elif args.approve:
        approve_candidate(args.approve)
    
    elif args.reject:
        reject_candidate(args.reject)
    
    elif args.approve_all:
        rows = list_candidates('pending', 100)
        for row in rows:
            approve_candidate(row[1])  # username is index 1
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

