#!/usr/bin/env python3
"""
Orchestrator for X Thought Leadership Engine

Main entry point that ties the full pipeline together:
Poll → Correlate → Draft → SMS → (await approval) → Post

Designed to be run by a Zo scheduled agent every 2 hours during approval window.
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
import pytz

PROJECT_DIR = "/home/workspace/Projects/x-thought-leader"
TWEETS_DB = f"{PROJECT_DIR}/db/tweets.db"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger("orchestrator")

# Approval window: 8am - 10pm ET
APPROVAL_START_HOUR = 8
APPROVAL_END_HOUR = 22
TIMEZONE = pytz.timezone('America/New_York')


def is_approval_window() -> bool:
    """Check if we're within the approval window (8am-10pm ET)."""
    now = datetime.now(TIMEZONE)
    return APPROVAL_START_HOUR <= now.hour < APPROVAL_END_HOUR


def run_step(name: str, cmd: list[str]) -> dict:
    """Run a pipeline step and capture result."""
    logger.info(f"Running {name}: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )
        return {
            'step': name,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'step': name,
            'success': False,
            'error': 'timeout'
        }
    except Exception as e:
        return {
            'step': name,
            'success': False,
            'error': str(e)
        }


def step_poll() -> dict:
    """Step 1: Poll monitored accounts for new tweets."""
    return run_step(
        "poll",
        ["python3", "src/polling_agent.py", "--force"]
    )


def step_correlate(min_score: float = 0.3) -> dict:
    """Step 2: Correlate new tweets against positions."""
    return run_step(
        "correlate",
        ["python3", "src/correlator.py", "--min-score", str(min_score)]
    )


def step_draft(min_score: float = 0.3) -> dict:
    """Step 3: Generate drafts for correlated tweets."""
    # First get the list of ready tweets
    list_result = subprocess.run(
        ["python3", "src/draft_generator.py", "--list-ready", "--min-score", str(min_score)],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    # Parse tweet IDs from output (format: [20083299] @asanwal...)
    import re
    tweet_ids = re.findall(r'\[(\d{15,25})\]', list_result.stdout)  # Full tweet IDs are 18-20 digits
    
    drafted = 0
    for tweet_id in tweet_ids[:5]:  # Limit to 5 per run to avoid spam
        result = run_step(
            f"draft-{tweet_id}",
            ["python3", "src/draft_generator.py", "--tweet-id", tweet_id]
        )
        if result['success']:
            drafted += 1
    
    return {
        'step': 'draft',
        'success': True,
        'drafted': drafted,
        'candidates': len(tweet_ids)
    }


def step_send_sms() -> dict:
    """Step 4: Send SMS for tweets that have drafts but no approval request."""
    import sqlite3
    
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    # Find tweets with drafts that haven't been sent for approval
    rows = conn.execute("""
        SELECT DISTINCT d.tweet_id
        FROM drafts d
        LEFT JOIN approval_queue aq ON d.tweet_id = aq.tweet_id
        WHERE aq.id IS NULL
        AND d.generated_at > datetime('now', '-1 day')
        LIMIT 3
    """).fetchall()
    conn.close()
    
    sent = 0
    for row in rows:
        tweet_id = row['tweet_id']
        
        # Format SMS
        format_result = subprocess.run(
            ["python3", "src/sms_interface.py", "format", tweet_id],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        if format_result.returncode == 0:
            sms_content = format_result.stdout
            
            # Send via Zo's send_sms_to_user (called from agent context)
            # For now, just log it - actual sending happens via Zo tool
            logger.info(f"SMS ready for tweet {tweet_id}")
            
            # Record that we've queued this
            conn = sqlite3.connect(TWEETS_DB)
            conn.execute("""
                INSERT INTO approval_queue (tweet_id, sent_at, expires_at, status)
                VALUES (?, CURRENT_TIMESTAMP, datetime('now', '+12 hours'), 'PENDING')
            """, (tweet_id,))
            conn.commit()
            conn.close()
            
            sent += 1
            
            # Return SMS content for Zo to send
            print(f"SMS_CONTENT_START\n{sms_content}\nSMS_CONTENT_END")
    
    return {
        'step': 'sms',
        'success': True,
        'sent': sent
    }


def step_expire() -> dict:
    """Step 5: Expire old approval requests."""
    return run_step(
        "expire",
        ["python3", "src/sms_interface.py", "expire"]
    )


def step_post_approved() -> dict:
    """Step 6: Post any approved tweets."""
    return run_step(
        "post",
        ["python3", "src/poster.py", "all"]
    )


def run_full_pipeline(min_score: float = 0.3, force: bool = False) -> dict:
    """Run the complete pipeline."""
    if not force and not is_approval_window():
        logger.info("Outside approval window (8am-10pm ET). Skipping.")
        return {
            'status': 'skipped',
            'reason': 'outside_approval_window',
            'current_hour': datetime.now(TIMEZONE).hour
        }
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'steps': []
    }
    
    # Step 1: Poll
    poll_result = step_poll()
    results['steps'].append(poll_result)
    
    # Step 2: Correlate
    correlate_result = step_correlate(min_score)
    results['steps'].append(correlate_result)
    
    # Step 3: Draft
    draft_result = step_draft(min_score)
    results['steps'].append(draft_result)
    
    # Step 4: Expire old requests
    expire_result = step_expire()
    results['steps'].append(expire_result)
    
    # Step 5: Post approved tweets
    post_result = step_post_approved()
    results['steps'].append(post_result)
    
    # Step 6: Send SMS for new drafts (returns content for Zo to send)
    sms_result = step_send_sms()
    results['steps'].append(sms_result)
    
    results['completed_at'] = datetime.utcnow().isoformat()
    results['status'] = 'completed'
    
    return results


def get_status() -> dict:
    """Get current system status."""
    import sqlite3
    
    conn = sqlite3.connect(TWEETS_DB)
    
    status = {
        'in_approval_window': is_approval_window(),
        'current_time_et': datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M %Z'),
        'counts': {}
    }
    
    # Tweet counts by status
    rows = conn.execute("""
        SELECT status, COUNT(*) as count FROM tweets GROUP BY status
    """).fetchall()
    status['counts']['tweets'] = {r[0]: r[1] for r in rows}
    
    # Approval queue
    rows = conn.execute("""
        SELECT status, COUNT(*) as count FROM approval_queue GROUP BY status
    """).fetchall()
    status['counts']['approvals'] = {r[0]: r[1] for r in rows}
    
    # Posted tweets
    count = conn.execute("SELECT COUNT(*) FROM posted_tweets").fetchone()[0]
    status['counts']['posted'] = count
    
    # Pending for SMS
    count = conn.execute("""
        SELECT COUNT(DISTINCT d.tweet_id)
        FROM drafts d
        LEFT JOIN approval_queue aq ON d.tweet_id = aq.tweet_id
        WHERE aq.id IS NULL
    """).fetchone()[0]
    status['counts']['ready_for_sms'] = count
    
    conn.close()
    return status


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="X Thought Leader Orchestrator")
    subparsers = parser.add_subparsers(dest='command')
    
    # Run full pipeline
    run_parser = subparsers.add_parser('run', help='Run full pipeline')
    run_parser.add_argument('--min-score', type=float, default=0.3, 
                           help='Min correlation score (default: 0.3)')
    run_parser.add_argument('--force', action='store_true',
                           help='Run even outside approval window')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    # Individual steps
    poll_parser = subparsers.add_parser('poll', help='Just poll for new tweets')
    correlate_parser = subparsers.add_parser('correlate', help='Just run correlation')
    draft_parser = subparsers.add_parser('draft', help='Just generate drafts')
    sms_parser = subparsers.add_parser('sms', help='Just send SMS notifications')
    post_parser = subparsers.add_parser('post', help='Just post approved tweets')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        force_mode = args.force
        results = run_full_pipeline(min_score=args.min_score, force=force_mode)
        print(json.dumps(results, indent=2))
        
    elif args.command == 'status':
        status = get_status()
        print(json.dumps(status, indent=2))
        
    elif args.command == 'poll':
        print(json.dumps(step_poll(), indent=2))
        
    elif args.command == 'correlate':
        print(json.dumps(step_correlate(), indent=2))
        
    elif args.command == 'draft':
        print(json.dumps(step_draft(), indent=2))
        
    elif args.command == 'sms':
        print(json.dumps(step_send_sms(), indent=2))
        
    elif args.command == 'post':
        print(json.dumps(step_post_approved(), indent=2))
        
    else:
        parser.print_help()





