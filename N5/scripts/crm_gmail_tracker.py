#!/usr/bin/env python3
"""
Gmail Sent Items Tracker for CRM V3
Monitors sent folder, detects replies to external contacts, queues enrichment.

Architecture:
- Scans Gmail sent folder for recent emails
- Filters spam/auto-replies using heuristics
- Creates profiles for new contacts (email → CRM)
- Schedules low-priority enrichment jobs (7 days out, priority 25)

Usage:
    python3 crm_gmail_tracker.py [--gmail-account EMAIL] [--since TIMESTAMP]

Worker 5 of CRM V3 Unified Build
"""

import os
import sys
import sqlite3
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

# Add N5 scripts to path for imports
sys.path.insert(0, '/home/workspace/N5/scripts')
from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
STATE_FILE = '/home/workspace/N5/data/gmail_tracker_state.json'
LOG_FILE = '/home/workspace/N5/logs/gmail_tracker.log'

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def is_spam_response(subject: str, snippet: str, to_email: str) -> bool:
    """
    Detect spam/unwanted responses.
    
    Rules:
    - Subject contains: "unsubscribe", "out of office", "autoreply", "delivery failure"
    - Snippet contains spam trigger phrases
    - To email is noreply/automated address
    
    Returns True if spam, False if legitimate
    """
    spam_keywords = [
        'unsubscribe', 'out of office', 'autoreply', 
        'automatic reply', 'delivery failure', 'mailer-daemon',
        'do not reply', 'noreply', 'delivery status notification',
        'vacation', 'away from', 'out-of-office', 'auto-reply',
        'automated response', 'postmaster'
    ]
    
    text = f"{subject} {snippet}".lower()
    
    # Check for spam keywords
    if any(keyword in text for keyword in spam_keywords):
        return True
    
    # Check for noreply email addresses
    email_lower = to_email.lower()
    if 'noreply' in email_lower or 'no-reply' in email_lower:
        return True
    
    # Check for common automated senders
    automated_domains = ['notification', 'mailer', 'daemon', 'postmaster']
    if any(domain in email_lower for domain in automated_domains):
        return True
    
    return False


def extract_email_from_to_field(to_value: str) -> Optional[str]:
    """
    Extract clean email address from To header.
    
    Handles formats:
    - "Name <email@domain.com>"
    - "email@domain.com"
    - "Name1 <email1@domain.com>, Name2 <email2@domain.com>"
    
    Returns first email found or None
    """
    if not to_value:
        return None
    
    # Handle angle bracket format
    if '<' in to_value and '>' in to_value:
        email = to_value.split('<')[1].split('>')[0].strip()
        return email if '@' in email else None
    
    # Handle plain email (split on comma for multiple recipients)
    parts = to_value.split(',')
    for part in parts:
        email = part.strip()
        if '@' in email:
            return email
    
    return None


def process_sent_email(email: Dict) -> Optional[int]:
    """
    Process single sent email.
    
    Returns profile_id if processed, None if skipped
    """
    to_email = email.get('to_email')
    subject = email.get('subject', '(no subject)')
    snippet = email.get('snippet', '')
    
    if not to_email:
        logger.debug("Skipping email: no recipient found")
        return None
    
    # 1. Spam check
    if is_spam_response(subject, snippet, to_email):
        logger.debug(f"Skipping spam/auto-reply: {to_email}")
        return None
    
    # 2. Check if profile exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM profiles WHERE email = ?", (to_email,))
    row = cursor.fetchone()
    
    if row:
        # Profile exists, skip
        logger.debug(f"Profile exists for {to_email}, skipping")
        conn.close()
        return None
    
    # 3. Create profile
    # Generate name from email (best guess)
    name = to_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
    
    try:
        profile_id = get_or_create_profile(to_email, name, source='gmail_reply')
        
        # 4. Schedule low-priority enrichment (7 days out)
        scheduled_for = (datetime.now() + timedelta(days=7)).isoformat()
        metadata = json.dumps({
            'thread_id': email.get('thread_id'),
            'subject': subject,
            'sent_at': email.get('sent_at'),
            'snippet': snippet[:100]  # First 100 chars
        })
        
        schedule_enrichment_job(
            profile_id=profile_id,
            scheduled_for=scheduled_for,
            checkpoint='checkpoint_1',
            priority=25,  # Low priority
            trigger_source='gmail_reply',
            trigger_metadata=metadata
        )
        
        logger.info(f"Created profile {profile_id} for {to_email} from sent email")
        return profile_id
        
    except Exception as e:
        logger.error(f"Failed to process email for {to_email}: {e}")
        return None
    finally:
        conn.close()


def load_state() -> Dict:
    """Load tracker state from JSON file"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # First run: start from 7 days ago
        return {
            'last_run': (datetime.now() - timedelta(days=7)).isoformat(),
            'processed_count': 0,
            'total_emails_checked': 0
        }


def save_state(state: Dict):
    """Save tracker state to JSON file"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def parse_gmail_messages(messages: List[Dict]) -> List[Dict]:
    """
    Parse Gmail API message format into simplified email dicts.
    
    Args:
        messages: Raw Gmail API message list
        
    Returns:
        List of email dicts with to_email, subject, sent_at, snippet
    """
    emails = []
    
    for msg in messages:
        headers = msg.get('payload', {}).get('headers', [])
        
        # Extract fields from headers
        to_email = None
        subject = None
        date = None
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            
            if name == 'to':
                to_email = extract_email_from_to_field(value)
            elif name == 'subject':
                subject = value
            elif name == 'date':
                date = value
        
        if to_email:  # Only include if we found a recipient
            emails.append({
                'message_id': msg.get('id'),
                'thread_id': msg.get('threadId'),
                'to_email': to_email,
                'subject': subject or '(no subject)',
                'sent_at': date or datetime.now().isoformat(),
                'snippet': msg.get('snippet', '')
            })
    
    return emails


def fetch_sent_emails_from_gmail(since_timestamp: str, gmail_account: str = 'attawar.v@gmail.com') -> List[Dict]:
    """
    Fetch sent emails from Gmail using Zo's Gmail tool.
    
    Args:
        since_timestamp: ISO format datetime  
        gmail_account: Gmail account email
        
    Returns:
        List of simplified email dicts
    """
    try:
        # Import Zo's Gmail tool
        sys.path.insert(0, '/home/.z/lib')
        from tools.app_gmail import use_app_gmail
        
        # Convert timestamp to Gmail search format (YYYY/MM/DD)
        dt = datetime.fromisoformat(since_timestamp)
        search_date = dt.strftime('%Y/%m/%d')
        
        search_query = f"in:sent after:{search_date}"
        logger.info(f"Searching Gmail ({gmail_account}): {search_query}")
        
        result = use_app_gmail(
            tool_name='gmail-find-email',
            configured_props={
                'q': search_query,
                'maxResults': 100,
                'includeSpamTrash': False,
                'metadataOnly': False
            },
            email=gmail_account
        )
        
        messages = result.get('ret', [])
        logger.info(f"Found {len(messages)} sent emails from Gmail API")
        
        return parse_gmail_messages(messages)
        
    except Exception as e:
        logger.error(f"Gmail API error: {e}")
        return []


def main():
    """Main tracker loop"""
    parser = argparse.ArgumentParser(description='Gmail Sent Items Tracker for CRM V3')
    parser.add_argument('--gmail-data', type=str, 
                       help='Path to JSON file with Gmail messages (for testing)')
    parser.add_argument('--gmail-account', type=str, default='attawar.v@gmail.com',
                       help='Gmail account to scan (default: attawar.v@gmail.com)')
    parser.add_argument('--since', type=str,
                       help='ISO timestamp to check emails since (overrides state file)')
    args = parser.parse_args()
    
    logger.info("=== Gmail Sent Items Tracker Started ===")
    
    # Load state
    state = load_state()
    last_run = args.since or state.get('last_run')
    
    logger.info(f"Checking emails since: {last_run}")
    logger.info(f"Gmail account: {args.gmail_account}")
    
    # Fetch sent emails
    if args.gmail_data and os.path.exists(args.gmail_data):
        # TEST MODE: Load from JSON file
        logger.info(f"TEST MODE: Loading Gmail data from: {args.gmail_data}")
        with open(args.gmail_data, 'r') as f:
            data = json.load(f)
            messages = data.get('messages', [])
            emails = parse_gmail_messages(messages)
    else:
        # LIVE MODE: Fetch from Gmail API
        logger.info("LIVE MODE: Fetching from Gmail API")
        emails = fetch_sent_emails_from_gmail(last_run, args.gmail_account)
    
    processed_count = 0
    skipped_count = 0
    
    for email in emails:
        result = process_sent_email(email)
        if result:
            processed_count += 1
        else:
            skipped_count += 1
    
    # Update state
    new_state = {
        'last_run': datetime.now().isoformat(),
        'processed_count': processed_count,
        'total_emails_checked': len(emails),
        'skipped_count': skipped_count,
        'previous_run': last_run
    }
    save_state(new_state)
    
    logger.info(f"=== Gmail Tracker Complete ===")
    logger.info(f"Emails checked: {len(emails)}")
    logger.info(f"New profiles created: {processed_count}")
    logger.info(f"Skipped (spam/existing): {skipped_count}")
    
    print(f"✓ Processed {processed_count} new contacts from {len(emails)} sent emails")
    print(f"  Skipped: {skipped_count} (spam/auto-replies/existing profiles)")
    
    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"✗ Error: {e}")
        sys.exit(1)


