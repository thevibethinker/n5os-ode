#!/usr/bin/env python3
"""
Tweet-Position Correlator

Scores new tweets against positions database and stores results.
Bridges the gap between polling_agent and draft_generator.
"""

import sys
import sqlite3
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from position_matcher import match_positions

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("correlator")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"


def get_new_tweets(limit: int = 50) -> list[dict]:
    """Get tweets that haven't been scored yet."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, content, author_username, is_reply
        FROM tweets 
        WHERE status = 'new'
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    tweets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tweets


def score_tweet(tweet: dict, min_score: float = 0.3) -> dict:
    """
    Score a tweet against all positions.
    
    Returns dict with:
        - top_score: highest similarity score
        - matches: list of (position_id, position_title, score) tuples
    """
    # Skip retweets and low-value tweets
    content = tweet['content']
    if content.startswith('RT @'):
        return {'top_score': 0.0, 'matches': [], 'skip_reason': 'retweet'}
    
    if len(content) < 20:
        return {'top_score': 0.0, 'matches': [], 'skip_reason': 'too_short'}
    
    # Run through position matcher
    matches = match_positions(content, top_n=5)
    
    if not matches:
        return {'top_score': 0.0, 'matches': [], 'skip_reason': 'no_matches'}
    
    # Filter by minimum score
    filtered = [m for m in matches if m.similarity_score >= min_score]
    
    if not filtered:
        return {
            'top_score': matches[0].similarity_score if matches else 0.0,
            'matches': [],
            'skip_reason': 'below_threshold'
        }
    
    return {
        'top_score': filtered[0].similarity_score,
        'matches': [(m.position_id, m.title, m.similarity_score) for m in filtered]
    }


def store_correlations(tweet_id: str, score_result: dict):
    """Store correlation results to database."""
    conn = sqlite3.connect(TWEETS_DB)
    
    top_score = score_result['top_score']
    matches = score_result.get('matches', [])
    skip_reason = score_result.get('skip_reason')
    
    if skip_reason:
        # Mark as skipped
        conn.execute("""
            UPDATE tweets 
            SET status = 'skipped', 
                correlation_score = ?,
                correlation_computed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (top_score, tweet_id))
        logger.info(f"Skipped {tweet_id}: {skip_reason}")
    else:
        # Store correlations
        for pos_id, pos_title, score in matches:
            conn.execute("""
                INSERT OR REPLACE INTO position_correlations 
                (tweet_id, position_id, position_title, similarity_score)
                VALUES (?, ?, ?, ?)
            """, (tweet_id, pos_id, pos_title, score))
        
        # Update tweet status
        conn.execute("""
            UPDATE tweets 
            SET status = 'correlated', 
                correlation_score = ?,
                correlation_computed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (top_score, tweet_id))
        logger.info(f"Correlated {tweet_id}: score={top_score:.3f}, matches={len(matches)}")
    
    conn.commit()
    conn.close()


def run_correlation(min_score: float = 0.3, limit: int = 50) -> dict:
    """
    Main entry point: score all new tweets.
    
    Returns summary dict.
    """
    tweets = get_new_tweets(limit)
    
    if not tweets:
        logger.info("No new tweets to correlate")
        return {'processed': 0, 'correlated': 0, 'skipped': 0}
    
    logger.info(f"Correlating {len(tweets)} new tweets...")
    
    stats = {'processed': 0, 'correlated': 0, 'skipped': 0}
    
    for tweet in tweets:
        result = score_tweet(tweet, min_score=min_score)
        store_correlations(tweet['id'], result)
        
        stats['processed'] += 1
        if result.get('skip_reason'):
            stats['skipped'] += 1
        else:
            stats['correlated'] += 1
    
    logger.info(f"Done: {stats['correlated']} correlated, {stats['skipped']} skipped")
    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Correlate tweets with positions")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum correlation score")
    parser.add_argument("--limit", type=int, default=50, help="Max tweets to process")
    parser.add_argument("--tweet-id", help="Correlate specific tweet only")
    parser.add_argument("--status", action="store_true", help="Show correlation status")
    args = parser.parse_args()
    
    if args.status:
        conn = sqlite3.connect(TWEETS_DB)
        counts = conn.execute("""
            SELECT status, COUNT(*) as cnt 
            FROM tweets 
            GROUP BY status
        """).fetchall()
        conn.close()
        print("Tweet status counts:")
        for status, cnt in counts:
            print(f"  {status}: {cnt}")
    elif args.tweet_id:
        conn = sqlite3.connect(TWEETS_DB)
        conn.row_factory = sqlite3.Row
        tweet = conn.execute("SELECT * FROM tweets WHERE id = ?", (args.tweet_id,)).fetchone()
        conn.close()
        if tweet:
            result = score_tweet(dict(tweet), min_score=args.min_score)
            store_correlations(args.tweet_id, result)
            print(f"Result: {result}")
        else:
            print(f"Tweet {args.tweet_id} not found")
    else:
        import json
        stats = run_correlation(min_score=args.min_score, limit=args.limit)
        print(json.dumps(stats))




