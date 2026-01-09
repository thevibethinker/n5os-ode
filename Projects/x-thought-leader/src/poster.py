#!/usr/bin/env python3
"""
Tweet Poster for X Thought Leadership Engine

Posts approved tweets as replies and records them for voice learning.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from x_api import post_reply, XAPIError

TWEETS_DB = "/home/workspace/Projects/x-thought-leader/db/tweets.db"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger("poster")


def get_draft(tweet_id: str, variant: str) -> dict | None:
    """Get a specific draft for a tweet."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT * FROM drafts
        WHERE tweet_id = ? AND variant = ?
    """, (tweet_id, variant)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_original_tweet(tweet_id: str) -> dict | None:
    """Get the original tweet we're replying to."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT * FROM tweets WHERE id = ?
    """, (tweet_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def record_posted_tweet(
    original: dict,
    our_tweet_id: str,
    our_content: str,
    variant: str,
    position_ids: list
) -> None:
    """Record our posted tweet to database for tracking and voice learning."""
    conn = sqlite3.connect(TWEETS_DB)
    
    # Insert into posted_tweets
    conn.execute("""
        INSERT INTO posted_tweets 
        (id, original_tweet_id, original_author, original_content,
         our_content, variant_used, position_ids)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        our_tweet_id,
        original['id'],
        original['author_username'],
        original['content'],
        our_content,
        variant,
        json.dumps(position_ids)
    ))
    
    # Update original tweet status
    conn.execute("""
        UPDATE tweets SET status = 'posted' WHERE id = ?
    """, (original['id'],))
    
    # Track variant preference for voice learning
    conn.execute("""
        INSERT INTO voice_samples (content, source, metadata)
        VALUES (?, 'posted_tweet', ?)
    """, (
        our_content,
        json.dumps({
            'variant': variant,
            'original_tweet_id': original['id'],
            'original_author': original['author_username'],
            'posted_at': datetime.utcnow().isoformat()
        })
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"Recorded posted tweet {our_tweet_id}")


def post_approved_tweet(tweet_id: str, variant: str, dry_run: bool = False) -> dict | None:
    """
    Post the approved variant as a reply.
    
    Args:
        tweet_id: Original tweet ID we're replying to
        variant: Which variant was approved (supportive, challenging, spicy, comedic)
        dry_run: If True, don't actually post
    
    Returns:
        Posted tweet dict or None on failure
    """
    # Get the draft
    draft = get_draft(tweet_id, variant)
    if not draft:
        logger.error(f"No draft found for {tweet_id} variant {variant}")
        return None
    
    # Get original tweet
    original = get_original_tweet(tweet_id)
    if not original:
        logger.error(f"Original tweet {tweet_id} not found")
        return None
    
    content = draft['content']
    position_ids = json.loads(draft.get('position_ids') or '[]')
    
    if dry_run:
        logger.info(f"DRY RUN: Would post '{content[:50]}...' as reply to {tweet_id}")
        return {
            'id': 'dry-run-id',
            'content': content,
            'dry_run': True
        }
    
    # Post reply via X API
    try:
        result = post_reply(tweet_id, content)
        if not result:
            logger.error(f"Failed to post reply to {tweet_id}")
            return None
        
        # Record it
        record_posted_tweet(original, result['id'], content, variant, position_ids)
        
        logger.info(f"Posted tweet {result['id']} as reply to {tweet_id}")
        return result
        
    except XAPIError as e:
        logger.error(f"X API error posting reply: {e}")
        return None


def get_pending_posts() -> list[dict]:
    """Get approved tweets waiting to be posted."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT aq.*, t.content as original_content, t.author_username
        FROM approval_queue aq
        JOIN tweets t ON aq.tweet_id = t.id
        WHERE aq.status = 'APPROVED'
        ORDER BY aq.approved_at ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def post_all_approved(dry_run: bool = False) -> dict:
    """Post all approved tweets."""
    pending = get_pending_posts()
    results = {
        'posted': 0,
        'failed': 0,
        'details': []
    }
    
    for item in pending:
        tweet_id = item['tweet_id']
        variant = item['selected_variant']
        
        result = post_approved_tweet(tweet_id, variant, dry_run=dry_run)
        
        if result:
            results['posted'] += 1
            results['details'].append({
                'tweet_id': tweet_id,
                'variant': variant,
                'posted_id': result.get('id'),
                'status': 'success'
            })
            
            # Mark as posted in approval queue
            if not dry_run:
                conn = sqlite3.connect(TWEETS_DB)
                conn.execute("""
                    UPDATE approval_queue 
                    SET status = 'POSTED'
                    WHERE tweet_id = ?
                """, (tweet_id,))
                conn.commit()
                conn.close()
        else:
            results['failed'] += 1
            results['details'].append({
                'tweet_id': tweet_id,
                'variant': variant,
                'status': 'failed'
            })
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tweet Poster CLI")
    subparsers = parser.add_subparsers(dest='command')
    
    # Post single tweet
    post_parser = subparsers.add_parser('post', help='Post a specific approved tweet')
    post_parser.add_argument('tweet_id', help='Original tweet ID')
    post_parser.add_argument('variant', help='Variant to post')
    post_parser.add_argument('--dry-run', action='store_true', help="Don't actually post")
    
    # Post all approved
    all_parser = subparsers.add_parser('all', help='Post all approved tweets')
    all_parser.add_argument('--dry-run', action='store_true', help="Don't actually post")
    
    # List pending
    pending_parser = subparsers.add_parser('pending', help='List approved tweets waiting to post')
    
    args = parser.parse_args()
    
    if args.command == 'post':
        result = post_approved_tweet(args.tweet_id, args.variant, dry_run=args.dry_run)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("Failed to post tweet")
            sys.exit(1)
            
    elif args.command == 'all':
        results = post_all_approved(dry_run=args.dry_run)
        print(json.dumps(results, indent=2))
        
    elif args.command == 'pending':
        pending = get_pending_posts()
        print(json.dumps(pending, indent=2))
        
    else:
        parser.print_help()

