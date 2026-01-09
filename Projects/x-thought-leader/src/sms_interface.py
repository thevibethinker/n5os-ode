#!/usr/bin/env python3
"""
SMS Approval Interface for X Thought Leadership Engine

Handles sending draft variants to V via SMS and parsing responses.
"""

import os
import re
import sqlite3
import json
import logging
from datetime import datetime, time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("sms_interface")

TWEETS_DB = "/home/workspace/Projects/x-thought-leader/db/tweets.db"
ET = pytz.timezone('America/New_York')

VARIANT_EMOJIS = {
    'supportive': '1️⃣',
    'challenging': '2️⃣',
    'spicy': '3️⃣',
    'comedic': '4️⃣'
}

VARIANT_ORDER = ['supportive', 'challenging', 'spicy', 'comedic']

@dataclass
class ApprovalResponse:
    action: str          # 'select', 'skip', 'regenerate'
    variant: Optional[str] = None
    feedback: Optional[str] = None

@dataclass
class Draft:
    id: str
    tweet_id: str
    variant: str
    content: str

def get_eod_expiry() -> str:
    """Get end of day in ET as ISO string."""
    now = datetime.now(ET)
    eod = datetime.combine(now.date(), time(23, 59, 59), tzinfo=ET)
    return eod.isoformat()

def format_approval_message(tweet: Dict[str, Any], drafts: List[Any]) -> str:
    """
    Format tweet + 4 variants into SMS message.
    
    Keeps total under ~1000 chars if possible (SMS limits).
    Truncates original tweet if needed.
    """
    # Handle both Draft objects and dicts
    draft_objs = []
    for d in drafts:
        if hasattr(d, 'variant'):
            draft_objs.append(d)
        else:
            draft_objs.append(Draft(id=d['id'], tweet_id=d['tweet_id'], variant=d['variant'], content=d['content']))
    
    # Truncate original if too long
    original = tweet.get('content', tweet.get('text', ''))
    if len(original) > 200:
        original = original[:197] + "..."
    
    author = tweet.get('author_username', 'unknown')
    
    lines = [
        f"🐦 @{author} just posted:",
        f'"{original}"',
        "",
        "Your 4 variants:",
        ""
    ]
    
    # Sort drafts by variant order
    drafts_by_variant = {d.variant: d for d in draft_objs}
    
    for i, variant in enumerate(VARIANT_ORDER, 1):
        draft = drafts_by_variant.get(variant)
        if draft:
            emoji = VARIANT_EMOJIS[variant]
            lines.append(f"{emoji} {variant.upper()}")
            lines.append(draft.content)
            lines.append("")
    
    lines.extend([
        "Reply: 1-4 to post, 0 to skip, or \"3: make it edgier\"",
        f"Expires: EOD"
    ])
    
    return "\n".join(lines)

def parse_response(text: str) -> ApprovalResponse:
    """
    Parse V's SMS response into structured action.
    """
    text = text.strip().lower()
    
    # Skip patterns
    if text in ('0', 'skip', 'pass', 'no', 'nope'):
        return ApprovalResponse(action='skip')
    
    # Direct number selection
    if text in ('1', '2', '3', '4'):
        variant = VARIANT_ORDER[int(text) - 1]
        return ApprovalResponse(action='select', variant=variant)
    
    # Variant name selection
    for variant in VARIANT_ORDER:
        if text == variant:
            return ApprovalResponse(action='select', variant=variant)
    
    # Regeneration with feedback: "3: make it edgier" or "spicy: less aggressive"
    # Matches "3: feedback", "spicy: feedback", "3 feedback", "spicy feedback"
    regen_match = re.match(r'^(\d|supportive|challenging|spicy|comedic)[:\s]+(.+)$', text)
    if regen_match:
        variant_ref = regen_match.group(1)
        feedback = regen_match.group(2).strip()
        
        if variant_ref.isdigit():
            idx = int(variant_ref) - 1
            if 0 <= idx < len(VARIANT_ORDER):
                variant = VARIANT_ORDER[idx]
            else:
                return ApprovalResponse(action='unknown')
        else:
            variant = variant_ref
        
        return ApprovalResponse(action='regenerate', variant=variant, feedback=feedback)
    
    # Default: couldn't parse
    logger.warning(f"Could not parse response: {text}")
    return ApprovalResponse(action='unknown')

def record_approval_request(tweet_id: str, expires_at: str) -> int:
    """Record approval request in queue."""
    conn = sqlite3.connect(TWEETS_DB)
    cursor = conn.execute("""
        INSERT INTO approval_queue (tweet_id, expires_at)
        VALUES (?, ?)
        ON CONFLICT(tweet_id) DO UPDATE SET
            sent_at = CURRENT_TIMESTAMP,
            expires_at = excluded.expires_at,
            response_received = 0
    """, (tweet_id, expires_at))
    queue_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return queue_id

def record_response(tweet_id: str, response: ApprovalResponse):
    """Record V's response in queue and update tweet status."""
    conn = sqlite3.connect(TWEETS_DB)
    
    # Format response text for storage
    resp_text = response.action
    if response.variant:
        resp_text += f":{response.variant}"
    if response.feedback:
        resp_text += f":{response.feedback}"
        
    conn.execute("""
        UPDATE approval_queue
        SET response_received = 1,
            response_text = ?,
            response_at = CURRENT_TIMESTAMP,
            selected_variant = ?,
            refinement_suggestion = ?
        WHERE tweet_id = ?
    """, (
        resp_text,
        response.variant if response.action == 'select' else None,
        response.feedback,
        tweet_id
    ))
    
    # Update tweet status
    if response.action == 'skip':
        new_status = 'skipped'
    elif response.action == 'select':
        new_status = 'approved'
    elif response.action == 'regenerate':
        new_status = 'drafted' # Back to drafted for regen
    else:
        new_status = None
        
    if new_status:
        conn.execute("""
            UPDATE tweets SET status = ? WHERE id = ?
        """, (new_status, tweet_id))
    
    conn.commit()
    conn.close()

def expire_pending() -> int:
    """
    Expire old approval requests past their expiry time.
    
    Returns count of expired entries.
    Called periodically or at EOD.
    """
    conn = sqlite3.connect(TWEETS_DB)
    
    # Find IDs to expire
    rows = conn.execute("""
        SELECT tweet_id FROM approval_queue
        WHERE response_received = 0
        AND expires_at < datetime('now')
    """).fetchall()
    
    tweet_ids = [row[0] for row in rows]
    count = len(tweet_ids)
    
    if count > 0:
        cursor = conn.execute("""
            UPDATE approval_queue
            SET response_received = 1,
                response_text = 'EXPIRED',
                response_at = CURRENT_TIMESTAMP
            WHERE response_received = 0
            AND expires_at < datetime('now')
        """)
        
        # Update corresponding tweets
        placeholders = ','.join(['?'] * count)
        conn.execute(f"""
            UPDATE tweets
            SET status = 'expired'
            WHERE id IN ({placeholders})
        """, tweet_ids)
        
        conn.commit()
        logger.info(f"Expired {count} pending approval requests")
    
    conn.close()
    return count

def get_pending() -> List[Dict[str, Any]]:
    """Get all pending (not yet responded) approval requests."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT aq.*, t.content as tweet_content, t.author_username
        FROM approval_queue aq
        JOIN tweets t ON aq.tweet_id = t.id
        WHERE aq.response_received = 0
        AND aq.expires_at > datetime('now')
        ORDER BY aq.sent_at ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_drafts_for_tweet(tweet_id: str) -> List[Dict[str, Any]]:
    """Get drafts for a tweet."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM drafts WHERE tweet_id = ?
    """, (tweet_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SMS Interface CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # format command
    fmt_parser = subparsers.add_parser("format", help="Format approval message")
    fmt_parser.add_argument("tweet_id", help="Tweet ID")
    
    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse response")
    parse_parser.add_argument("response", help="Response text")
    
    # pending command
    pending_parser = subparsers.add_parser("pending", help="List pending approvals")
    
    # expire command
    expire_parser = subparsers.add_parser("expire", help="Expire old requests")
    
    args = parser.parse_args()
    
    if args.command == "parse":
        result = parse_response(args.response)
        print(json.dumps({
            "action": result.action,
            "variant": result.variant,
            "feedback": result.feedback
        }))
    elif args.command == "pending":
        pending = get_pending()
        print(json.dumps(pending, indent=2))
    elif args.command == "expire":
        count = expire_pending()
        print(json.dumps({"expired": count}))
    elif args.command == "format":
        conn = sqlite3.connect(TWEETS_DB)
        conn.row_factory = sqlite3.Row
        tweet_row = conn.execute("SELECT * FROM tweets WHERE id = ?", (args.tweet_id,)).fetchone()
        if not tweet_row:
            print(f"Error: Tweet {args.tweet_id} not found")
        else:
            tweet = dict(tweet_row)
            draft_rows = conn.execute("SELECT * FROM drafts WHERE tweet_id = ?", (args.tweet_id,)).fetchall()
            drafts = [dict(r) for r in draft_rows]
            print(format_approval_message(tweet, drafts))
        conn.close()
    else:
        parser.print_help()

