#!/usr/bin/env python3
"""
AI Reply Generator for X Thought Leadership Engine

Generates draft replies for high-relevance tweets using V's voice.
Human-in-the-loop: V reviews/edits before posting.

Workflow:
1. relevance_gate.py identifies high-score tweets
2. This module generates 2-3 reply variants per tweet
3. Drafts go to approval queue (SMS alert + web UI)
4. V approves/edits → post via API
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
DB_PATH = PROJECT_ROOT / "db" / "tweets.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# V's voice characteristics for reply generation
V_VOICE_PROMPT = """You are helping V (@thevibethinker) write Twitter replies.

V's voice characteristics:
- Founder of Careerspan (AI-powered hiring)
- Thoughtful, not hot-take-bro
- Adds genuine value, not just "Great point!"
- Uses analogies and reframes
- Occasionally contrarian but always substantive
- Avoids: emojis overload, generic praise, self-promotion in replies

V's core positions:
- AI will transform hiring from pattern-matching to potential-matching
- The "Library of Alexandria" framing: AI as personal knowledge infrastructure
- Hiring is broken because we optimize for credentials over capability
- Career coaching needs to evolve from advice-giving to system-building

Reply style:
- Lead with insight, not agreement
- Add a non-obvious angle or reframe
- Keep it tight (under 280 chars ideally, max 400)
- Sound like a peer, not a fan
"""

def generate_reply_variants(tweet_text: str, tweet_author: str, context: str = "") -> List[Dict]:
    """
    Generate 2-3 reply variants for a tweet using Zo's /zo/ask API.
    
    Returns list of {variant: str, style: str, char_count: int}
    """
    prompt = f"""{V_VOICE_PROMPT}

Tweet to reply to (by @{tweet_author}):
\"\"\"{tweet_text}\"\"\"

{f"Additional context: {context}" if context else ""}

Generate exactly 3 reply variants:
1. INSIGHT variant: Lead with a non-obvious observation or reframe
2. QUESTION variant: Ask a thought-provoking follow-up question
3. ADDITIVE variant: Build on their point with a specific example or data

Format your response as JSON array:
[
  {{"style": "insight", "reply": "..."}},
  {{"style": "question", "reply": "..."}},
  {{"style": "additive", "reply": "..."}}
]

Keep each reply under 280 characters. No emojis. Sound like V, not a bot."""

    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            output = response.json().get('output', '')
            
            # Parse JSON from response
            try:
                # Find JSON array in response
                start = output.find('[')
                end = output.rfind(']') + 1
                if start >= 0 and end > start:
                    variants = json.loads(output[start:end])
                    for v in variants:
                        v['char_count'] = len(v.get('reply', ''))
                    return variants
            except json.JSONDecodeError:
                logger.error(f"Failed to parse reply variants: {output[:200]}")
                return []
        else:
            logger.error(f"Zo API error: {response.status_code} {response.text[:200]}")
            return []
            
    except Exception as e:
        logger.error(f"Error generating replies: {e}")
        return []


def queue_reply_drafts(tweet_id: str, variants: List[Dict]) -> int:
    """
    Save reply variants to the drafts table for approval.
    Returns number of drafts queued.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure drafts table has reply columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reply_drafts (
            id TEXT PRIMARY KEY,
            tweet_id TEXT NOT NULL,
            variant_style TEXT,
            reply_text TEXT,
            char_count INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            posted_at TEXT,
            FOREIGN KEY(tweet_id) REFERENCES tweets(id)
        )
    """)
    
    queued = 0
    for v in variants:
        import uuid
        draft_id = str(uuid.uuid4())[:8]
        
        cursor.execute("""
            INSERT OR IGNORE INTO reply_drafts 
            (id, tweet_id, variant_style, reply_text, char_count, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (draft_id, tweet_id, v.get('style'), v.get('reply'), v.get('char_count')))
        
        if cursor.rowcount > 0:
            queued += 1
    
    conn.commit()
    conn.close()
    return queued


def get_tweets_needing_replies(limit: int = 10) -> List[Dict]:
    """
    Get high-relevance tweets that don't have reply drafts yet.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.id, t.account_id, t.author_username, t.content, t.correlation_score,
               t.created_at, ma.username as monitored_username
        FROM tweets t
        LEFT JOIN monitored_accounts ma ON t.account_id = ma.id
        WHERE t.gate_passed = 1 
          AND t.correlation_score >= 0.6
          AND t.id NOT IN (SELECT DISTINCT tweet_id FROM reply_drafts)
        ORDER BY t.correlation_score DESC, t.created_at DESC
        LIMIT ?
    """, (limit,))
    
    tweets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tweets


def generate_batch_replies(limit: int = 5, dry_run: bool = False) -> Dict:
    """
    Generate reply drafts for high-relevance tweets.
    """
    tweets = get_tweets_needing_replies(limit)
    
    stats = {
        'tweets_processed': 0,
        'drafts_generated': 0,
        'drafts_queued': 0,
        'errors': 0
    }
    
    for tweet in tweets:
        logger.info(f"Generating replies for tweet {tweet['id']} by @{tweet.get('author_username', 'unknown')}")
        
        variants = generate_reply_variants(
            tweet_text=tweet['content'],
            tweet_author=tweet.get('author_username') or tweet.get('monitored_username', 'unknown')
        )
        
        stats['tweets_processed'] += 1
        stats['drafts_generated'] += len(variants)
        
        if variants and not dry_run:
            queued = queue_reply_drafts(tweet['id'], variants)
            stats['drafts_queued'] += queued
        
        if dry_run and variants:
            print(f"\n--- Tweet by @{tweet.get('author_username', 'unknown')} ---")
            print(f"{tweet['content'][:200]}...")
            print(f"\nGenerated {len(variants)} reply variants:")
            for v in variants:
                print(f"  [{v['style']}] ({v['char_count']} chars): {v['reply']}")
    
    return stats


def get_pending_drafts(limit: int = 20) -> List[Dict]:
    """
    Get pending reply drafts for review.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT rd.*, t.content as tweet_content, t.author_username,
               t.correlation_score
        FROM reply_drafts rd
        JOIN tweets t ON rd.tweet_id = t.id
        WHERE rd.status = 'pending'
        ORDER BY t.correlation_score DESC, rd.created_at DESC
        LIMIT ?
    """, (limit,))
    
    drafts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return drafts


def approve_draft(draft_id: str) -> bool:
    """Mark a draft as approved."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reply_drafts 
        SET status = 'approved', approved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (draft_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def format_drafts_for_sms(drafts: List[Dict], max_drafts: int = 3) -> str:
    """
    Format top drafts for SMS notification.
    """
    if not drafts:
        return "No pending reply drafts."
    
    lines = ["🎯 Reply drafts ready:\n"]
    
    for i, d in enumerate(drafts[:max_drafts], 1):
        author = d.get('author_username', '?')
        tweet_preview = d.get('tweet_content', '')[:50]
        reply_preview = d.get('reply_text', '')[:80]
        
        lines.append(f"{i}. @{author}: \"{tweet_preview}...\"")
        lines.append(f"   → {reply_preview}...")
        lines.append("")
    
    lines.append(f"Review: va.zo.computer → X Thought Leader")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI Reply Generator")
    parser.add_argument("--generate", action="store_true", help="Generate reply drafts for high-relevance tweets")
    parser.add_argument("--limit", type=int, default=5, help="Max tweets to process")
    parser.add_argument("--dry-run", action="store_true", help="Show drafts without saving")
    parser.add_argument("--pending", action="store_true", help="Show pending drafts for review")
    parser.add_argument("--approve", type=str, help="Approve a draft by ID")
    parser.add_argument("--sms-preview", action="store_true", help="Show SMS notification preview")
    
    args = parser.parse_args()
    
    if args.generate:
        stats = generate_batch_replies(limit=args.limit, dry_run=args.dry_run)
        print(json.dumps(stats, indent=2))
        
    elif args.pending:
        drafts = get_pending_drafts(args.limit)
        if not drafts:
            print("No pending drafts.")
        else:
            print(f"\n{'='*70}")
            print(f"PENDING REPLY DRAFTS ({len(drafts)} total)")
            print(f"{'='*70}\n")
            
            for d in drafts:
                print(f"Draft ID: {d['id']} | Style: {d['variant_style']} | Score: {d.get('correlation_score', '?')}")
                print(f"Tweet by @{d.get('author_username', '?')}:")
                print(f"  \"{d.get('tweet_content', '')[:100]}...\"")
                print(f"Reply ({d['char_count']} chars):")
                print(f"  \"{d['reply_text']}\"")
                print()
                
    elif args.approve:
        if approve_draft(args.approve):
            print(f"✅ Draft {args.approve} approved")
        else:
            print(f"❌ Draft {args.approve} not found")
            
    elif args.sms_preview:
        drafts = get_pending_drafts(5)
        print(format_drafts_for_sms(drafts))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


