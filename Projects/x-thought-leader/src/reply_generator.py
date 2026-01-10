#!/usr/bin/env python3
"""
AI Reply Generator for X Thought Leadership Engine

TWO-STAGE TRANSFORMATION APPROACH:
1. Generate NEUTRAL insight (what to say)
2. Transform to V's voice (how to say it)

This separates content quality from style quality, allowing:
- Iteration on the neutral version before transformation
- Reuse of the transformation layer for other content types
- Better debugging (is the insight weak, or the voice wrong?)

Canonical voice system: N5/prefs/communication/voice-transformation-system.md
X platform profile: N5/prefs/communication/platforms/x.md
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pytz

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from voice_model import (
    get_neutral_prompt, 
    get_transform_prompt,
    PLATFORM_VOICE,
    TRANSFORMATION_PAIRS,
    ANTI_PATTERNS
)

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("reply_generator")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"
ET = pytz.timezone('America/New_York')

# Use Zo's API (same as relevance_gate.py)
ZO_API_URL = "https://api.zo.computer/zo/ask"


# =============================================================================
# LLM INTERFACE
# =============================================================================

NEUTRAL_SCHEMA = {
    "type": "object",
    "properties": {
        "insight": {"type": "string"},
        "angle": {"type": "string", "enum": ["reframe", "question", "evidence", "connection", "challenge"]},
        "strength": {"type": "number"}
    },
    "required": ["insight", "angle", "strength"]
}

TRANSFORM_SCHEMA = {
    "type": "object",
    "properties": {
        "transformed": {"type": "string"},
        "technique": {"type": "string"},
        "profanity_used": {"type": "boolean"},
        "char_count": {"type": "integer"}
    },
    "required": ["transformed", "technique", "char_count"]
}


def call_llm(prompt: str, schema: dict = None) -> dict:
    """Call Zo's /zo/ask API with optional JSON schema."""
    auth_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not auth_token:
        logger.error("ZO_CLIENT_IDENTITY_TOKEN not set")
        return {"error": "no_auth_token"}
    
    headers = {
        "authorization": auth_token,
        "content-type": "application/json"
    }
    
    payload = {"input": prompt}
    
    if schema:
        payload["output_format"] = schema
    
    try:
        resp = requests.post(
            ZO_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        result = resp.json()
        
        output = result.get("output", "")
        
        # If schema was provided, output should be dict; otherwise parse JSON from text
        if schema and isinstance(output, dict):
            return output
        elif schema:
            # Try to parse JSON from text response
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # Extract JSON from text if wrapped
                import re
                json_match = re.search(r'\{[^{}]*\}', output, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {"error": "json_parse_failed", "raw": output[:200]}
        else:
            return {"text": output}
            
    except requests.exceptions.Timeout:
        logger.error("Zo API timeout")
        return {"error": "timeout"}
    except Exception as e:
        logger.error(f"Zo API error: {e}")
        return {"error": str(e)}


# =============================================================================
# TWO-STAGE GENERATION
# =============================================================================

def generate_neutral_insight(tweet: dict) -> dict:
    """Stage 1: Generate the raw insight (what to say)."""
    prompt = get_neutral_prompt(
        author=tweet['author_username'],
        original_tweet=tweet['content'],
        relevance_context=tweet.get('gate_reason', '')
    )
    
    result = call_llm(prompt, schema=NEUTRAL_SCHEMA)
    
    if "error" in result:
        return {"error": result["error"]}
    
    logger.info(f"Neutral insight generated: angle={result.get('angle')}, strength={result.get('strength', 0):.2f}")
    return result


def transform_to_voice(neutral_insight: str) -> dict:
    """Stage 2: Transform neutral insight to V's voice."""
    prompt = get_transform_prompt(neutral_insight)
    
    # Don't use schema - just get text and parse
    result = call_llm(prompt, schema=None)
    
    if "error" in result:
        return {"error": result["error"]}
    
    # Parse the text response
    text = result.get("text", "")
    
    # Try to extract JSON from response
    try:
        import re
        json_match = re.search(r'\{[^{}]*"transformed"[^{}]*\}', text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            logger.info(f"Transformed: {parsed.get('technique', 'unknown')}, {len(parsed.get('transformed', ''))} chars")
            return parsed
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # Fallback: treat entire response as the transformed text
    # Clean up any markdown or extra formatting
    cleaned = text.strip()
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()
    
    logger.info(f"Transformed (raw): {len(cleaned)} chars")
    return {
        "transformed": cleaned[:280],  # Enforce length limit
        "technique": "raw_response",
        "char_count": len(cleaned[:280]),
        "profanity_used": False
    }


def generate_reply_variants(tweet: dict, num_variants: int = 3, dry_run: bool = False) -> List[dict]:
    """Generate multiple reply variants using two-stage approach."""
    variants = []
    angles = ["reframe", "question", "evidence"]  # Different angles for variety
    
    for i, angle_hint in enumerate(angles[:num_variants]):
        # Stage 1: Generate neutral insight
        neutral_result = generate_neutral_insight(tweet)
        
        if "error" in neutral_result:
            logger.warning(f"Variant {i+1} neutral generation failed: {neutral_result['error']}")
            continue
        
        neutral_text = neutral_result.get("insight", "")
        if not neutral_text:
            continue
        
        # Stage 2: Transform to voice
        transform_result = transform_to_voice(neutral_text)
        
        if "error" in transform_result:
            logger.warning(f"Variant {i+1} transform failed: {transform_result['error']}")
            continue
        
        variant = {
            "variant_type": neutral_result.get("angle", angle_hint),
            "neutral_insight": neutral_text,
            "insight_strength": neutral_result.get("strength", 0),
            "reply_text": transform_result.get("transformed", ""),
            "technique": transform_result.get("technique", ""),
            "char_count": transform_result.get("char_count", len(transform_result.get("transformed", ""))),
            "profanity_used": transform_result.get("profanity_used", False)
        }
        
        if dry_run:
            print(f"\n  [{variant['variant_type'].upper()}] (strength={variant['insight_strength']:.2f})")
            print(f"  NEUTRAL: {variant['neutral_insight']}")
            print(f"  TRANSFORMED ({variant['char_count']} chars): {variant['reply_text']}")
            print(f"  Technique: {variant['technique']}")
        else:
            # Save to DB
            save_draft(tweet['id'], variant)
        
        variants.append(variant)
    
    return variants


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def ensure_schema():
    """Ensure reply_drafts table has neutral_insight column."""
    conn = sqlite3.connect(TWEETS_DB)
    
    # Check if neutral_insight column exists
    cursor = conn.execute("PRAGMA table_info(reply_drafts)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "neutral_insight" not in columns:
        conn.execute("ALTER TABLE reply_drafts ADD COLUMN neutral_insight TEXT")
        conn.execute("ALTER TABLE reply_drafts ADD COLUMN insight_strength REAL")
        conn.execute("ALTER TABLE reply_drafts ADD COLUMN technique TEXT")
        conn.commit()
        logger.info("Added neutral_insight columns to reply_drafts")
    
    conn.close()


def save_draft(tweet_id: str, variant: dict):
    """Save a reply draft to the database."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.execute("""
        INSERT INTO reply_drafts (
            tweet_id, variant_type, reply_text, status, created_at,
            neutral_insight, insight_strength, technique
        ) VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP, ?, ?, ?)
    """, (
        tweet_id,
        variant['variant_type'],
        variant['reply_text'],
        variant.get('neutral_insight'),
        variant.get('insight_strength'),
        variant.get('technique')
    ))
    conn.commit()
    conn.close()


def get_tweets_needing_replies(limit: int = 10) -> List[dict]:
    """Get tweets that passed the gate but don't have replies yet."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT t.id, t.content, t.author_username, t.correlation_score, t.gate_reason
        FROM tweets t
        LEFT JOIN reply_drafts rd ON t.id = rd.tweet_id
        WHERE t.gate_passed = 1 AND rd.id IS NULL
        ORDER BY t.correlation_score DESC
        LIMIT ?
    """, (limit,))
    
    tweets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tweets


def get_pending_drafts(limit: int = 10) -> List[dict]:
    """Get pending drafts for review."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT rd.*, t.content as original_content, t.author_username, t.correlation_score as tweet_score
        FROM reply_drafts rd
        JOIN tweets t ON rd.tweet_id = t.id
        WHERE rd.status = 'pending'
        ORDER BY rd.created_at DESC
        LIMIT ?
    """, (limit,))
    
    drafts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return drafts


# =============================================================================
# MAIN GENERATION FLOW
# =============================================================================

def generate_replies(limit: int = 5, dry_run: bool = False) -> dict:
    """Main entry point: generate replies for passed tweets."""
    ensure_schema()
    
    tweets = get_tweets_needing_replies(limit)
    
    stats = {
        "tweets_processed": 0,
        "drafts_generated": 0,
        "drafts_queued": 0,
        "approach": "two-stage-transformation",
        "errors": 0
    }
    
    for tweet in tweets:
        logger.info(f"Generating replies for tweet {tweet['id']} by @{tweet['author_username']} (score={tweet['correlation_score']:.2f})")
        
        if dry_run:
            print(f"\n{'='*70}")
            print(f"Tweet by @{tweet['author_username']} (score={tweet['correlation_score']:.2f})")
            print(f"{'='*70}")
            print(f"{tweet['content'][:300]}...")
            print(f"\nGate reason: {tweet.get('gate_reason', 'N/A')[:200]}...")
        
        try:
            variants = generate_reply_variants(tweet, num_variants=3, dry_run=dry_run)
            stats["tweets_processed"] += 1
            stats["drafts_generated"] += len(variants)
            
            if not dry_run:
                stats["drafts_queued"] += len(variants)
                
        except Exception as e:
            logger.error(f"Error generating replies for {tweet['id']}: {e}")
            stats["errors"] += 1
    
    return stats


def format_drafts_for_sms(drafts: List[dict]) -> str:
    """Format pending drafts for SMS alert."""
    if not drafts:
        return "No pending drafts"
    
    lines = ["🎯 X Reply Drafts Ready:\n"]
    
    for i, d in enumerate(drafts[:3], 1):
        lines.append(f"{i}. @{d['author_username']} ({d.get('tweet_score', 0):.1f})")
        lines.append(f"   NEUTRAL: {d.get('neutral_insight', 'N/A')[:60]}...")
        lines.append(f"   REPLY: {d['reply_text'][:80]}...")
        lines.append("")
    
    lines.append(f"Total pending: {len(drafts)}")
    return "\n".join(lines)


# =============================================================================
# ITERATION SUPPORT
# =============================================================================

def iterate_on_neutral(limit: int = 1) -> dict:
    """
    Re-transform existing drafts with their neutral insights.
    Useful when tweaking the transformation prompt.
    """
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT rd.id, rd.neutral_insight, rd.reply_text, rd.variant_type
        FROM reply_drafts rd
        WHERE rd.neutral_insight IS NOT NULL AND rd.status = 'pending'
        ORDER BY rd.created_at DESC
        LIMIT ?
    """, (limit,))
    
    drafts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    stats = {"reviewed": 0, "regenerated": 0, "errors": 0}
    
    for draft in drafts:
        stats["reviewed"] += 1
        neutral_text = draft.get("neutral_insight")
        
        if not neutral_text:
            continue
        
        print(f"\n--- Draft {draft['id']} ---")
        print(f"NEUTRAL: {neutral_text}")
        print(f"CURRENT: {draft['reply_text']}")
        
        # Re-transform
        transform_result = transform_to_voice(neutral_text)
        
        if "error" not in transform_result and "transformed" in transform_result:
            stats["regenerated"] += 1
            print(f"NEW: {transform_result['transformed']}")
            print(f"Technique: {transform_result.get('technique')}")
        else:
            stats["errors"] += 1
            print(f"Error: {transform_result.get('error', 'unknown')}")
    
    return stats


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="X Reply Generator - Two-Stage Voice Transformation")
    parser.add_argument("--generate", action="store_true", help="Generate replies for passed tweets")
    parser.add_argument("--limit", type=int, default=5, help="Max tweets to process")
    parser.add_argument("--dry-run", action="store_true", help="Print drafts without saving")
    parser.add_argument("--pending", action="store_true", help="Show pending drafts")
    parser.add_argument("--stats", action="store_true", help="Show generation statistics")
    parser.add_argument("--iterate", action="store_true", help="Re-transform existing neutral insights")
    parser.add_argument("--tweet-id", type=str, help="Process specific tweet ID")
    parser.add_argument("--sms-preview", action="store_true", help="Format pending drafts for SMS")
    
    args = parser.parse_args()
    
    if args.generate:
        stats = generate_replies(limit=args.limit, dry_run=args.dry_run)
        print(json.dumps(stats, indent=2))
        
    elif args.pending:
        drafts = get_pending_drafts(args.limit)
        print(f"Pending drafts ({len(drafts)}):")
        for d in drafts:
            print(f"\n[@{d['author_username']}] {d['original_content'][:80]}...")
            print(f"  NEUTRAL: {d.get('neutral_insight', 'N/A')[:100]}...")
            print(f"  TRANSFORMED: {d['reply_text'][:100]}...")
            print(f"  Variant: {d['variant_type']} | Score: {d.get('tweet_score', 'N/A')}")
            
    elif args.stats:
        conn = sqlite3.connect(TWEETS_DB)
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(LENGTH(reply_text)) as avg_len,
                MIN(LENGTH(reply_text)) as min_len,
                MAX(LENGTH(reply_text)) as max_len,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected
            FROM reply_drafts
        """)
        row = cursor.fetchone()
        conn.close()
        
        print("Reply Draft Statistics:")
        print(f"  Total: {row[0]}")
        print(f"  Pending: {row[4]}, Approved: {row[5]}, Rejected: {row[6]}")
        if row[1]:
            print(f"  Length: avg={row[1]:.0f}, min={row[2]}, max={row[3]}")
            
    elif args.iterate:
        stats = iterate_on_neutral(limit=args.limit)
        print(json.dumps(stats, indent=2))
        
    elif args.tweet_id:
        ensure_schema()
        conn = sqlite3.connect(TWEETS_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id, content, author_username, correlation_score, gate_reason
            FROM tweets
            WHERE id = ? AND gate_passed = 1
        """, (args.tweet_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print(f"Tweet {args.tweet_id} not found or not passed gate")
            return
            
        tweet = dict(row)
        variants = generate_reply_variants(tweet, dry_run=True)
        print(f"\nGenerated {len(variants)} variants for @{tweet['author_username']}")
            
    elif args.sms_preview:
        drafts = get_pending_drafts(5)
        print(format_drafts_for_sms(drafts))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()



