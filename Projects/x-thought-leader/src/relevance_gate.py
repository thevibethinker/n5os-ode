#!/usr/bin/env python3
"""
Semantic Relevance Gate for X Thought Leadership Engine

ALL tweets go to LLM for semantic evaluation.
Question: "Would V have something interesting to say about this?"

Design: Per V's direction - "fuck the cost, make it all semantic"
No keyword filtering. Wide capture → emergent domains.
"""

import os
import sys
import json
import sqlite3
import logging
import requests
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

# Basic hygiene (NOT topic filtering)
MIN_TWEET_LENGTH = 30  # chars - very low bar
MAX_TWEET_AGE_HOURS = 72  # allow slightly older tweets

# Semantic gate threshold
SEMANTIC_THRESHOLD = 0.65  # score >= this triggers downstream

# V's engagement profile for semantic evaluation
SEMANTIC_GATE_PROMPT = """You are evaluating whether V (@thevibethinker) would have something interesting to say about this tweet.

V's engagement profile:
- Founder of Careerspan (AI-powered hiring platform)
- Deep interests: hiring/talent markets, AI/automation philosophy, epistemology & knowledge systems, founder journey, future of work, human potential
- Writing style: adds non-obvious angles, reframes conversations, shares genuine insight, wit without snark
- Engages when: he can contribute something substantive beyond "great point!", when the topic connects to his worldview
- Does NOT engage with: pure news/announcements, memes without depth, promotional spam, hot takes lacking substance, outrage bait

Tweet by @{author}:
\"\"\"{tweet_text}\"\"\"

Question: Would V have something genuinely interesting to contribute to this conversation?

Think step by step:
1. What is the core topic/claim?
2. Does this connect to V's interests or expertise?
3. Could V add a non-obvious angle or reframe?
4. Is there enough substance to engage with?

Score 0.0-1.0:
- 0.0-0.3: No clear angle for V, off-topic, or low substance
- 0.4-0.6: Tangentially relevant, V might engage if inspired
- 0.7-1.0: V would definitely have something valuable to say

Respond with ONLY valid JSON (no markdown, no explanation):
{{"score": X.X, "reasoning": "one sentence why"}}"""


def basic_hygiene(tweet: dict) -> Tuple[bool, str]:
    """
    Basic hygiene checks - NOT topic filtering.
    
    Only rejects obvious spam/noise, not based on topic.
    
    Returns:
        (passed: bool, reason: str)
    """
    content = tweet.get('content', '')
    
    # Reject pure retweets (no original thought)
    if content.startswith('RT @'):
        return (False, 'pure_retweet')
    
    # Reject extremely short (likely low-signal)
    if len(content) < MIN_TWEET_LENGTH:
        return (False, f'too_short_{len(content)}_chars')
    
    # Reject if too old (stale conversation)
    created_at = tweet.get('created_at')
    if created_at:
        try:
            tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now(pytz.UTC) - tweet_time
            if age > timedelta(hours=MAX_TWEET_AGE_HOURS):
                return (False, f'too_old_{int(age.total_seconds()//3600)}h')
        except (ValueError, TypeError):
            pass  # If we can't parse, don't reject on age
    
    return (True, 'hygiene_passed')


def call_semantic_gate(tweet_text: str, author: str) -> Tuple[float, str]:
    """
    Call LLM to evaluate tweet relevance.
    
    Uses Zo's /zo/ask API for semantic evaluation.
    
    Returns:
        (score: 0.0-1.0, reasoning: str)
    """
    prompt = SEMANTIC_GATE_PROMPT.format(
        author=author,
        tweet_text=tweet_text[:500]  # Truncate very long tweets
    )
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        logger.error("ZO_CLIENT_IDENTITY_TOKEN not set, cannot call semantic gate")
        return (0.5, "token_missing_fallback")
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["score", "reasoning"]
                }
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        output = result.get("output", {})
        
        score = float(output.get("score", 0.0))
        reasoning = output.get("reasoning", "no_reasoning")
        
        # Clamp score to valid range
        score = max(0.0, min(1.0, score))
        
        return (score, reasoning)
        
    except requests.exceptions.Timeout:
        logger.warning("Semantic gate timeout")
        return (0.5, "timeout_fallback")
    except requests.exceptions.RequestException as e:
        logger.error(f"Semantic gate API error: {e}")
        return (0.5, f"api_error_{str(e)[:30]}")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Semantic gate parse error: {e}")
        return (0.5, f"parse_error_{str(e)[:30]}")


def process_tweet(tweet_id: str) -> dict:
    """
    Run a tweet through the semantic gate.
    
    1. Basic hygiene check (spam/retweets only)
    2. LLM semantic evaluation (all hygiene-passing tweets)
    
    Updates DB with results and returns summary.
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
    
    # Step 1: Basic hygiene (not topic filtering)
    hygiene_passed, hygiene_reason = basic_hygiene(tweet)
    
    if not hygiene_passed:
        conn.execute("""
            UPDATE tweets 
            SET gate_stage = 0, gate_passed = 0, gate_reason = ?,
                status = 'skipped'
            WHERE id = ?
        """, (f'hygiene:{hygiene_reason}', tweet_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Tweet {tweet_id} failed hygiene: {hygiene_reason}")
        return {
            'tweet_id': tweet_id,
            'passed': False,
            'stage': 0,
            'reason': f'hygiene:{hygiene_reason}',
            'score': 0.0
        }
    
    # Step 2: Semantic evaluation (all hygiene-passing tweets)
    score, reasoning = call_semantic_gate(
        tweet_text=tweet['content'],
        author=tweet['author_username']
    )
    
    passed = score >= SEMANTIC_THRESHOLD
    
    # Update DB
    conn.execute("""
        UPDATE tweets 
        SET gate_stage = 2, gate_passed = ?, gate_reason = ?,
            correlation_score = ?, correlation_computed_at = CURRENT_TIMESTAMP,
            status = CASE WHEN ? = 1 THEN 'correlated' ELSE 'skipped' END
        WHERE id = ?
    """, (1 if passed else 0, reasoning[:200], score, 1 if passed else 0, tweet_id))
    conn.commit()
    conn.close()
    
    status = "PASSED" if passed else "filtered"
    logger.info(f"Tweet {tweet_id} {status}: score={score:.2f} - {reasoning[:60]}")
    
    return {
        'tweet_id': tweet_id,
        'passed': passed,
        'stage': 2,
        'reason': reasoning,
        'score': score
    }


def process_new_tweets(limit: int = 50) -> dict:
    """
    Process all tweets with status='new' through the semantic gate.
    
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
        logger.info("No new tweets to process through semantic gate")
        return {'processed': 0, 'passed': 0, 'filtered': 0}
    
    logger.info(f"Processing {len(tweets)} tweets through SEMANTIC gate (no keyword filtering)...")
    
    stats = {
        'processed': 0,
        'hygiene_rejected': 0,
        'passed': 0,
        'filtered': 0,
        'high_relevance': [],  # score >= threshold
        'avg_score': 0.0
    }
    
    scores = []
    
    for tweet_row in tweets:
        result = process_tweet(tweet_row['id'])
        stats['processed'] += 1
        
        if result.get('error'):
            continue
        
        if result['stage'] == 0:
            stats['hygiene_rejected'] += 1
        else:
            scores.append(result['score'])
            if result['passed']:
                stats['passed'] += 1
                stats['high_relevance'].append({
                    'tweet_id': result['tweet_id'],
                    'score': result['score'],
                    'reason': result['reason']
                })
            else:
                stats['filtered'] += 1
    
    if scores:
        stats['avg_score'] = sum(scores) / len(scores)
    
    logger.info(
        f"Semantic gate complete: {stats['passed']}/{stats['processed']} passed "
        f"({100*stats['passed']/stats['processed']:.0f}%), "
        f"avg_score={stats['avg_score']:.2f}, "
        f"{stats['hygiene_rejected']} hygiene rejected"
    )
    
    return stats


def get_alertable_tweets(limit: int = 10) -> list[dict]:
    """
    Get tweets that passed the gate and are ready for alerting.
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
    """, (SEMANTIC_THRESHOLD, limit)).fetchall()
    conn.close()
    
    return [dict(t) for t in tweets]


def reset_for_reprocessing(limit: int = 100) -> int:
    """
    Reset tweets so they can be reprocessed through the new semantic gate.
    
    Useful when changing gate logic.
    """
    conn = sqlite3.connect(TWEETS_DB)
    
    # SQLite doesn't support LIMIT in UPDATE, so select IDs first
    cursor = conn.execute("""
        SELECT id FROM tweets 
        WHERE status IN ('skipped', 'correlated')
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    ids = [row[0] for row in cursor.fetchall()]
    
    if not ids:
        conn.close()
        return 0
    
    placeholders = ','.join('?' * len(ids))
    conn.execute(f"""
        UPDATE tweets 
        SET gate_stage = NULL, gate_passed = 0, gate_reason = NULL,
            correlation_score = NULL, correlation_computed_at = NULL,
            status = 'new'
        WHERE id IN ({placeholders})
    """, ids)
    
    count = len(ids)
    conn.commit()
    conn.close()
    
    logger.info(f"Reset {count} tweets for reprocessing")
    return count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Relevance Gate (no keyword filtering)")
    parser.add_argument("--process", action="store_true", help="Process new tweets through semantic gate")
    parser.add_argument("--tweet-id", help="Process specific tweet")
    parser.add_argument("--limit", type=int, default=50, help="Max tweets to process")
    parser.add_argument("--alertable", action="store_true", help="List tweets ready for alerting")
    parser.add_argument("--stats", action="store_true", help="Show gate statistics")
    parser.add_argument("--reset", action="store_true", help="Reset tweets for reprocessing")
    parser.add_argument("--threshold", type=float, default=SEMANTIC_THRESHOLD, help="Score threshold")
    args = parser.parse_args()
    
    if args.stats:
        conn = sqlite3.connect(TWEETS_DB)
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN gate_stage = 0 THEN 1 ELSE 0 END) as hygiene_rejected,
                SUM(CASE WHEN gate_stage = 2 AND gate_passed = 0 THEN 1 ELSE 0 END) as semantic_filtered,
                SUM(CASE WHEN gate_passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(CASE WHEN gate_stage = 2 THEN correlation_score END) as avg_score,
                AVG(CASE WHEN gate_passed = 1 THEN correlation_score END) as avg_pass_score
            FROM tweets
            WHERE gate_stage IS NOT NULL
        """).fetchone()
        
        unprocessed = conn.execute(
            "SELECT COUNT(*) FROM tweets WHERE gate_stage IS NULL"
        ).fetchone()[0]
        conn.close()
        
        print("Semantic Gate Statistics:")
        print(f"  Unprocessed: {unprocessed}")
        print(f"  Total processed: {stats[0]}")
        if stats[0]:
            print(f"  Hygiene rejected: {stats[1]} ({100*stats[1]/stats[0]:.1f}%)")
            print(f"  Semantic filtered: {stats[2]} ({100*stats[2]/stats[0]:.1f}%)")
            print(f"  Passed: {stats[3]} ({100*stats[3]/stats[0]:.1f}%)")
        print(f"  Avg score (all): {stats[4]:.2f}" if stats[4] else "  Avg score: N/A")
        print(f"  Avg score (passed): {stats[5]:.2f}" if stats[5] else "  Avg pass score: N/A")
        
    elif args.reset:
        count = reset_for_reprocessing(limit=args.limit)
        print(f"Reset {count} tweets for reprocessing through semantic gate")
        
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


