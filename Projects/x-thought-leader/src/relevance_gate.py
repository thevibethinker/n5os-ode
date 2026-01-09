#!/usr/bin/env python3
"""
Two-Stage Relevance Gate for X Thought Leadership Engine

Stage 1: Cheap heuristic filter (runs on ALL tweets)
  - Keyword matching, length checks, retweet filtering
  - ~80% of tweets filtered here (no LLM cost)

Stage 2: LLM correlation (runs on Stage 1 passes only)
  - Uses position_matcher for semantic similarity
  - Threshold: score >= 0.7 triggers alert

Design: Expensive gate pattern - we'd rather miss some good tweets
than spam V with low-relevance alerts.
"""

import sys
import re
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional

import pytz

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("relevance_gate")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"
ET = pytz.timezone('America/New_York')

# Stage 1 configuration
STAGE1_KEYWORDS = {
    # HIGH SIGNAL - Career/Hiring (Careerspan core)
    'hiring', 'talent', 'recruiting', 'recruiter', 'candidates', 'sourcing',
    'job market', 'labor market', 'workforce', 'employer', 'employee',
    'talent acquisition', 'headhunter', 'applicant', 'job seeker',
    'offer letter', 'compensation', 'salary', 'equity',
    
    # HIGH SIGNAL - Future of Work
    'future of work', 'remote work', 'hybrid', 'return to office', 'rto',
    'work from home', 'wfh', 'distributed team', 'async',
    'four day week', '4 day week', 'burnout', 'quiet quitting',
    
    # HIGH SIGNAL - AI + Work intersection
    'ai', 'artificial intelligence', 'llm', 'gpt', 'claude', 'automation',
    'machine learning', 'agents', 'agentic', 'copilot',
    'ai replacing', 'ai jobs', 'ai hiring', 'ai recruiting',
    
    # HIGH SIGNAL - Founder/Startup
    'founder', 'startup', 'entrepreneur', 'building', 'shipping',
    'product', 'saas', 'b2b', 'pmf', 'product market fit',
    'seed', 'series a', 'fundraising', 'investor',
    
    # MEDIUM SIGNAL - Business/Strategy
    'strategy', 'growth', 'revenue', 'customers', 'market',
    'scale', 'scaling', 'org design', 'culture',
    
    # MEDIUM SIGNAL - Career Development
    'career', 'job', 'role', 'position', 'interview', 'resume',
    'leadership', 'management', 'team', 'promotion', 'layoff',
    'career change', 'career advice', 'mentorship',
}

STAGE1_MIN_LENGTH = 50
STAGE1_MAX_AGE_HOURS = 48

# Stage 2 configuration
STAGE2_THRESHOLD = 0.65  # Lowered from 0.7 to catch more borderline relevant tweets


def stage1_heuristic(tweet: dict) -> Tuple[bool, str, int]:
    """
    Fast heuristic filter (Stage 1).
    
    Args:
        tweet: dict with 'content', 'is_reply', 'created_at'
        
    Returns:
        (passed: bool, reason: str, stage: 1)
    """
    content = tweet.get('content', '')
    content_lower = content.lower()
    
    # Reject pure retweets (but allow quote tweets)
    if content.startswith('RT @'):
        return (False, 'retweet', 1)
    
    # Reject if too short (likely low-signal)
    if len(content) < STAGE1_MIN_LENGTH:
        return (False, 'too_short', 1)
    
    # Reject if reply to non-monitored account (harder to engage)
    # Note: replies to monitored accounts are fine (we're in the conversation)
    if tweet.get('is_reply') and not tweet.get('reply_to_monitored'):
        return (False, 'reply_to_unknown', 1)
    
    # Reject if too old
    created_at = tweet.get('created_at')
    if created_at:
        try:
            tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now(pytz.UTC) - tweet_time
            if age > timedelta(hours=STAGE1_MAX_AGE_HOURS):
                return (False, 'too_old', 1)
        except (ValueError, TypeError):
            pass  # If we can't parse, don't reject on age
    
    # Check for keyword matches
    keyword_matches = []
    for kw in STAGE1_KEYWORDS:
        # Use word boundary matching for single words, substring for phrases
        if ' ' in kw:
            if kw in content_lower:
                keyword_matches.append(kw)
        else:
            if re.search(rf'\b{re.escape(kw)}\b', content_lower):
                keyword_matches.append(kw)
    
    if not keyword_matches:
        return (False, 'no_keywords', 1)
    
    # Passed Stage 1
    return (True, f'keywords:{",".join(keyword_matches[:3])}', 1)


def stage2_correlation(tweet: dict, min_score: float = STAGE2_THRESHOLD) -> Tuple[bool, str, int, float]:
    """
    LLM-powered correlation check (Stage 2).
    
    Uses position_matcher to compute semantic similarity with V's positions.
    
    Args:
        tweet: dict with 'content'
        min_score: minimum score to pass (default 0.7)
        
    Returns:
        (passed: bool, reason: str, stage: 2, score: float)
    """
    try:
        from position_matcher import match_positions
    except ImportError:
        logger.error("position_matcher not available, falling back to pass-through")
        return (True, 'matcher_unavailable', 2, 0.5)
    
    content = tweet.get('content', '')
    
    try:
        matches = match_positions(content, top_n=3)
        
        if not matches:
            return (False, 'no_position_matches', 2, 0.0)
        
        top_score = matches[0].similarity_score
        top_title = matches[0].title[:50] if hasattr(matches[0], 'title') else 'unknown'
        
        if top_score >= min_score:
            return (True, f'position:{top_title}|score:{top_score:.2f}', 2, top_score)
        else:
            return (False, f'below_threshold:{top_score:.2f}<{min_score}', 2, top_score)
            
    except Exception as e:
        logger.error(f"Stage 2 error: {e}")
        return (False, f'error:{str(e)[:50]}', 2, 0.0)


def process_tweet(tweet_id: str) -> dict:
    """
    Run a tweet through both gate stages.
    
    Updates DB with results and returns summary.
    
    Returns:
        {
            'tweet_id': str,
            'passed': bool,
            'stage': int (1 or 2),
            'reason': str,
            'score': float (0.0 if Stage 1 rejection)
        }
    """
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    tweet_row = conn.execute(
        "SELECT * FROM tweets WHERE id = ?", (tweet_id,)
    ).fetchone()
    
    if not tweet_row:
        conn.close()
        return {'tweet_id': tweet_id, 'error': 'not_found'}
    
    tweet = dict(tweet_row)
    
    # Stage 1: Heuristic filter
    s1_passed, s1_reason, s1_stage = stage1_heuristic(tweet)
    
    if not s1_passed:
        # Failed Stage 1, update DB and return
        conn.execute("""
            UPDATE tweets 
            SET gate_stage = ?, gate_passed = 0, gate_reason = ?
            WHERE id = ?
        """, (s1_stage, s1_reason, tweet_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Tweet {tweet_id} failed Stage 1: {s1_reason}")
        return {
            'tweet_id': tweet_id,
            'passed': False,
            'stage': 1,
            'reason': s1_reason,
            'score': 0.0
        }
    
    # Stage 2: LLM correlation
    s2_passed, s2_reason, s2_stage, s2_score = stage2_correlation(tweet)
    
    # Update DB with final results
    conn.execute("""
        UPDATE tweets 
        SET gate_stage = ?, gate_passed = ?, gate_reason = ?,
            correlation_score = ?, correlation_computed_at = CURRENT_TIMESTAMP,
            status = CASE WHEN ? = 1 THEN 'correlated' ELSE 'skipped' END
        WHERE id = ?
    """, (s2_stage, 1 if s2_passed else 0, s2_reason, s2_score, 1 if s2_passed else 0, tweet_id))
    conn.commit()
    conn.close()
    
    status = "PASSED" if s2_passed else "failed"
    logger.info(f"Tweet {tweet_id} {status} Stage 2: {s2_reason} (score={s2_score:.2f})")
    
    return {
        'tweet_id': tweet_id,
        'passed': s2_passed,
        'stage': 2,
        'reason': s2_reason,
        'score': s2_score
    }


def process_new_tweets(limit: int = 50) -> dict:
    """
    Process all tweets with status='new' through the gate.
    
    Returns summary stats.
    """
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    tweets = conn.execute("""
        SELECT id FROM tweets 
        WHERE status = 'new' AND gate_stage IS NULL
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    
    if not tweets:
        logger.info("No new tweets to process through gate")
        return {'processed': 0, 'stage1_passed': 0, 'stage2_passed': 0}
    
    logger.info(f"Processing {len(tweets)} tweets through relevance gate...")
    
    stats = {
        'processed': 0,
        'stage1_passed': 0,
        'stage1_failed': 0,
        'stage2_passed': 0,
        'stage2_failed': 0,
        'high_relevance': []  # Tweets that passed with score >= 0.7
    }
    
    for tweet_row in tweets:
        result = process_tweet(tweet_row['id'])
        stats['processed'] += 1
        
        if result.get('error'):
            continue
        
        if result['stage'] == 1:
            stats['stage1_failed'] += 1
        else:
            stats['stage1_passed'] += 1
            if result['passed']:
                stats['stage2_passed'] += 1
                if result['score'] >= STAGE2_THRESHOLD:
                    stats['high_relevance'].append({
                        'tweet_id': result['tweet_id'],
                        'score': result['score'],
                        'reason': result['reason']
                    })
            else:
                stats['stage2_failed'] += 1
    
    logger.info(f"Gate complete: {stats['stage1_passed']}/{stats['processed']} passed Stage 1, "
                f"{stats['stage2_passed']} passed Stage 2, "
                f"{len(stats['high_relevance'])} high-relevance")
    
    return stats


def get_alertable_tweets(limit: int = 10) -> list[dict]:
    """
    Get tweets that passed the gate and are ready for alerting.
    
    Returns tweets with gate_passed=1 and score >= threshold that
    haven't been alerted yet.
    """
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    tweets = conn.execute("""
        SELECT t.id, t.content, t.author_username, t.correlation_score,
               t.gate_reason, t.created_at
        FROM tweets t
        LEFT JOIN alerts a ON t.id = a.tweet_id
        WHERE t.gate_passed = 1 
          AND t.correlation_score >= ?
          AND a.id IS NULL
        ORDER BY t.correlation_score DESC
        LIMIT ?
    """, (STAGE2_THRESHOLD, limit)).fetchall()
    conn.close()
    
    return [dict(t) for t in tweets]


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Two-Stage Relevance Gate")
    parser.add_argument("--process", action="store_true", help="Process new tweets through gate")
    parser.add_argument("--tweet-id", help="Process specific tweet")
    parser.add_argument("--limit", type=int, default=50, help="Max tweets to process")
    parser.add_argument("--alertable", action="store_true", help="List tweets ready for alerting")
    parser.add_argument("--stats", action="store_true", help="Show gate statistics")
    parser.add_argument("--threshold", type=float, default=STAGE2_THRESHOLD, help="Stage 2 score threshold")
    args = parser.parse_args()
    
    threshold = args.threshold
    
    if args.stats:
        conn = sqlite3.connect(TWEETS_DB)
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN gate_stage = 1 AND gate_passed = 0 THEN 1 ELSE 0 END) as stage1_rejected,
                SUM(CASE WHEN gate_stage = 2 AND gate_passed = 0 THEN 1 ELSE 0 END) as stage2_rejected,
                SUM(CASE WHEN gate_passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(CASE WHEN gate_passed = 1 THEN correlation_score END) as avg_pass_score
            FROM tweets
            WHERE gate_stage IS NOT NULL
        """).fetchone()
        conn.close()
        
        print("Gate Statistics:")
        print(f"  Total processed: {stats[0]}")
        print(f"  Stage 1 rejected: {stats[1]} ({100*stats[1]/stats[0]:.1f}%)" if stats[0] else "  Stage 1 rejected: 0")
        print(f"  Stage 2 rejected: {stats[2]}")
        print(f"  Passed: {stats[3]} ({100*stats[3]/stats[0]:.1f}%)" if stats[0] else "  Passed: 0")
        print(f"  Avg pass score: {stats[4]:.2f}" if stats[4] else "  Avg pass score: N/A")
        
    elif args.alertable:
        tweets = get_alertable_tweets(limit=args.limit)
        print(f"Alertable tweets ({len(tweets)}):")
        for t in tweets:
            print(f"  [{t['id']}] @{t['author_username']} (score={t['correlation_score']:.2f})")
            print(f"    {t['content'][:100]}...")
            print()
        
    elif args.tweet_id:
        result = process_tweet(args.tweet_id)
        print(json.dumps(result, indent=2))
        
    elif args.process:
        stats = process_new_tweets(limit=args.limit)
        print(json.dumps(stats, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()



