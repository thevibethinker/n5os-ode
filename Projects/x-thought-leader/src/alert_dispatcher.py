#!/usr/bin/env python3
"""
Alert Dispatcher for X Thought Leadership Engine

Routes high-relevance tweets to V via SMS with rate limiting and quiet hours.

Safety features:
- Daily cap: max 8 SMS per day
- Quiet hours: no SMS 10pm-8am ET
- All alerts logged to DB (even rate-limited ones)
- Dry-run mode for testing
"""

import os
import sys
import sqlite3
import logging
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional

import pytz

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "config"))

try:
    from settings import MAX_SMS_PER_DAY, QUIET_HOURS_START, QUIET_HOURS_END
except ImportError:
    MAX_SMS_PER_DAY = 8
    QUIET_HOURS_START = 22  # 10pm
    QUIET_HOURS_END = 8     # 8am

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("alert_dispatcher")

TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"
ET = pytz.timezone('America/New_York')


def get_sms_count_today() -> int:
    """Count SMS alerts sent today (ET timezone)."""
    conn = sqlite3.connect(TWEETS_DB)
    
    # Get start of today in ET
    now_et = datetime.now(ET)
    today_start = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_utc = today_start.astimezone(pytz.UTC).isoformat()
    
    count = conn.execute("""
        SELECT COUNT(*) FROM alerts 
        WHERE alert_type = 'sms' 
          AND status = 'sent'
          AND alerted_at >= ?
    """, (today_start_utc,)).fetchone()[0]
    
    conn.close()
    return count


def is_quiet_hours() -> bool:
    """Check if current time is in quiet hours (10pm-8am ET)."""
    now_et = datetime.now(ET)
    hour = now_et.hour
    
    # Quiet hours span midnight: 22:00 - 08:00
    if QUIET_HOURS_START > QUIET_HOURS_END:
        # e.g., 22-8: quiet if hour >= 22 OR hour < 8
        return hour >= QUIET_HOURS_START or hour < QUIET_HOURS_END
    else:
        # e.g., 1-6: quiet if 1 <= hour < 6
        return QUIET_HOURS_START <= hour < QUIET_HOURS_END


def can_send_sms() -> Tuple[bool, str]:
    """
    Check if SMS can be sent now.
    
    Returns:
        (can_send: bool, reason: str)
    """
    if is_quiet_hours():
        return (False, 'quiet_hours')
    
    count = get_sms_count_today()
    if count >= MAX_SMS_PER_DAY:
        return (False, f'rate_limited:{count}/{MAX_SMS_PER_DAY}')
    
    return (True, f'ok:{count}/{MAX_SMS_PER_DAY}')


def format_sms_message(tweet: dict) -> str:
    """
    Format tweet for SMS alert.
    
    Target: <160 chars for single SMS, but we can go up to 300.
    """
    author = tweet.get('author_username', 'unknown')
    score = tweet.get('correlation_score', 0)
    content = tweet.get('content', '')
    tweet_id = tweet.get('id', '')
    
    # Truncate content to fit
    max_content_len = 180
    if len(content) > max_content_len:
        content = content[:max_content_len-3] + "..."
    
    # Format message
    msg = f"🎯 @{author} ({score:.0%})\n\n{content}\n\nhttps://x.com/{author}/status/{tweet_id}"
    
    return msg


def send_sms(message: str, dry_run: bool = False) -> bool:
    """
    Send SMS using Zo's send_sms_to_user tool via zo/ask API.
    
    Returns True if sent successfully.
    """
    if dry_run:
        logger.info(f"[DRY-RUN] Would send SMS:\n{message}")
        return True
    
    # Use zo/ask API to send SMS
    import requests
    
    token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
    if not token:
        logger.error("ZO_CLIENT_IDENTITY_TOKEN not available")
        return False
    
    prompt = f"""Send the following SMS to the user immediately using the send_sms_to_user tool. Do not add any commentary, just send it.

Message to send:
{message}"""
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info("SMS sent successfully via zo/ask")
            return True
        else:
            logger.error(f"zo/ask returned {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        return False


def log_alert(tweet_id: str, alert_type: str, status: str, message: str) -> str:
    """Log alert to database, return alert ID."""
    conn = sqlite3.connect(TWEETS_DB)
    alert_id = str(uuid.uuid4())[:8]
    
    conn.execute("""
        INSERT INTO alerts (id, tweet_id, alert_type, status, message, alerted_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (alert_id, tweet_id, alert_type, status, message))
    
    conn.commit()
    conn.close()
    
    return alert_id


def dispatch_alert(tweet: dict, dry_run: bool = False) -> dict:
    """
    Dispatch alert for a high-relevance tweet.
    
    1. Check rate limits and quiet hours
    2. Format SMS message
    3. If can send: send via zo/ask
    4. Log to alerts table (always, even if rate limited)
    
    Args:
        tweet: dict with id, content, author_username, correlation_score
        dry_run: if True, don't actually send SMS
        
    Returns:
        {
            'tweet_id': str,
            'alert_id': str,
            'status': 'sent' | 'rate_limited' | 'quiet_hours' | 'error',
            'message': str (the formatted SMS)
        }
    """
    tweet_id = tweet.get('id')
    
    # Check if already alerted
    conn = sqlite3.connect(TWEETS_DB)
    existing = conn.execute(
        "SELECT id FROM alerts WHERE tweet_id = ?", (tweet_id,)
    ).fetchone()
    conn.close()
    
    if existing:
        logger.info(f"Tweet {tweet_id} already has alert {existing[0]}")
        return {
            'tweet_id': tweet_id,
            'alert_id': existing[0],
            'status': 'already_alerted',
            'message': None
        }
    
    # Format message
    message = format_sms_message(tweet)
    
    # Check if we can send
    can_send, reason = can_send_sms()
    
    if not can_send:
        # Log as rate_limited or quiet_hours but don't send
        status = 'quiet_hours' if 'quiet' in reason else 'rate_limited'
        alert_id = log_alert(tweet_id, 'sms', status, message)
        
        logger.info(f"Alert {alert_id} for tweet {tweet_id}: {status} ({reason})")
        
        return {
            'tweet_id': tweet_id,
            'alert_id': alert_id,
            'status': status,
            'message': message
        }
    
    # Try to send
    if dry_run:
        logger.info(f"[DRY-RUN] Would send SMS for tweet {tweet_id}")
        alert_id = log_alert(tweet_id, 'sms', 'dry_run', message)
        return {
            'tweet_id': tweet_id,
            'alert_id': alert_id,
            'status': 'dry_run',
            'message': message
        }
    
    success = send_sms(message, dry_run=False)
    
    if success:
        alert_id = log_alert(tweet_id, 'sms', 'sent', message)
        logger.info(f"Alert {alert_id} sent for tweet {tweet_id}")
        return {
            'tweet_id': tweet_id,
            'alert_id': alert_id,
            'status': 'sent',
            'message': message
        }
    else:
        alert_id = log_alert(tweet_id, 'sms', 'error', message)
        logger.error(f"Alert {alert_id} failed for tweet {tweet_id}")
        return {
            'tweet_id': tweet_id,
            'alert_id': alert_id,
            'status': 'error',
            'message': message
        }


def dispatch_pending_alerts(dry_run: bool = False, limit: int = 10) -> dict:
    """
    Process all alertable tweets (passed gate, score >= threshold, not yet alerted).
    
    Returns summary stats.
    """
    # Import here to avoid circular dependency
    from relevance_gate import get_alertable_tweets
    
    tweets = get_alertable_tweets(limit=limit)
    
    if not tweets:
        logger.info("No tweets pending alert")
        return {'processed': 0, 'sent': 0, 'rate_limited': 0, 'quiet_hours': 0}
    
    logger.info(f"Dispatching alerts for {len(tweets)} high-relevance tweets...")
    
    stats = {
        'processed': 0,
        'sent': 0,
        'rate_limited': 0,
        'quiet_hours': 0,
        'error': 0,
        'alerts': []
    }
    
    for tweet in tweets:
        result = dispatch_alert(tweet, dry_run=dry_run)
        stats['processed'] += 1
        
        status = result['status']
        if status == 'sent' or status == 'dry_run':
            stats['sent'] += 1
        elif status == 'rate_limited':
            stats['rate_limited'] += 1
        elif status == 'quiet_hours':
            stats['quiet_hours'] += 1
        elif status == 'error':
            stats['error'] += 1
        
        stats['alerts'].append(result)
    
    logger.info(f"Alert dispatch complete: {stats['sent']} sent, "
                f"{stats['rate_limited']} rate-limited, {stats['quiet_hours']} quiet-hours")
    
    return stats


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Alert Dispatcher")
    parser.add_argument("--dispatch", action="store_true", help="Dispatch pending alerts")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send SMS")
    parser.add_argument("--tweet-id", help="Dispatch alert for specific tweet")
    parser.add_argument("--limit", type=int, default=10, help="Max alerts to dispatch")
    parser.add_argument("--status", action="store_true", help="Show alert status and limits")
    parser.add_argument("--test-sms", help="Send a test SMS message")
    args = parser.parse_args()
    
    if args.status:
        can_send, reason = can_send_sms()
        count = get_sms_count_today()
        quiet = is_quiet_hours()
        
        print("Alert Dispatcher Status:")
        print(f"  Time (ET): {datetime.now(ET).strftime('%Y-%m-%d %H:%M')}")
        print(f"  Quiet hours: {'YES' if quiet else 'no'} ({QUIET_HOURS_START}:00-{QUIET_HOURS_END}:00)")
        print(f"  SMS today: {count}/{MAX_SMS_PER_DAY}")
        print(f"  Can send: {'YES' if can_send else 'NO'} ({reason})")
        
        # Count pending
        from relevance_gate import get_alertable_tweets
        pending = len(get_alertable_tweets(limit=100))
        print(f"  Pending alerts: {pending}")
        
    elif args.test_sms:
        print(f"Sending test SMS: {args.test_sms}")
        success = send_sms(args.test_sms, dry_run=args.dry_run)
        print(f"Result: {'sent' if success else 'failed'}")
        
    elif args.tweet_id:
        conn = sqlite3.connect(TWEETS_DB)
        conn.row_factory = sqlite3.Row
        tweet = conn.execute("SELECT * FROM tweets WHERE id = ?", (args.tweet_id,)).fetchone()
        conn.close()
        
        if not tweet:
            print(f"Tweet {args.tweet_id} not found")
            sys.exit(1)
        
        result = dispatch_alert(dict(tweet), dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
        
    elif args.dispatch:
        stats = dispatch_pending_alerts(dry_run=args.dry_run, limit=args.limit)
        print(json.dumps(stats, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

