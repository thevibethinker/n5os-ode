#!/usr/bin/env python3
"""
Simplified Email Scanner - Just count and categorize
Tracks: sent emails, incoming emails, unreplied threads
"""

import sqlite3
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path('/home/workspace/productivity_tracker.db')
MIN_WORD_COUNT = 10  # Ignore very short emails

def init_db():
    """Create simplified schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY,
            gmail_id TEXT UNIQUE NOT NULL,
            thread_id TEXT,
            date DATE NOT NULL,
            subject TEXT,
            word_count INTEGER,
            subject_category TEXT,
            era TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incoming_emails (
            id INTEGER PRIMARY KEY,
            gmail_id TEXT UNIQUE NOT NULL,
            thread_id TEXT,
            date DATE NOT NULL,
            subject TEXT,
            from_email TEXT,
            era TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unreplied_threads (
            id INTEGER PRIMARY KEY,
            thread_id TEXT UNIQUE NOT NULL,
            subject TEXT,
            from_email TEXT,
            received_date TIMESTAMP NOT NULL,
            days_unreplied INTEGER,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"✓ Database initialized: {DB_PATH}")

def categorize_subject(subject: str) -> str:
    """Simple subject line categorization"""
    subject_lower = subject.lower()
    
    patterns = {
        'hiring': r'\b(hiring|candidate|interview|recruit|resume|job|position)\b',
        'sales': r'\b(demo|pitch|proposal|opportunity|interested|partnership)\b',
        'investor': r'\b(investor|funding|raise|capital|investment|pitch deck)\b',
        'customer': r'\b(customer|user|feedback|support|issue|bug)\b',
        'internal': r'\b(team|meeting|sync|standup|update|review)\b',
        'legal': r'\b(contract|agreement|legal|terms|compliance)\b',
        'product': r'\b(feature|product|roadmap|design|development)\b',
    }
    
    for category, pattern in patterns.items():
        if re.search(pattern, subject_lower):
            return category
    
    # Check for Re:/Fwd:
    if subject_lower.startswith(('re:', 'fwd:', 'fw:')):
        return 'response'
    
    return 'other'

def determine_era(date_str: str) -> str:
    """Determine era based on date"""
    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    superhuman_date = datetime(2024, 11, 12, tzinfo=date.tzinfo)
    zo_date = datetime(2025, 10, 1, tzinfo=date.tzinfo)
    
    if date >= zo_date:
        return 'post-zo'
    elif date >= superhuman_date:
        return 'post-superhuman'
    else:
        return 'pre-superhuman'

def count_words(text: str) -> int:
    """Simple word counter"""
    return len(re.findall(r'\b\w+\b', text))

def store_sent_email(conn, email_data: dict, my_email: str):
    """Store sent email"""
    cursor = conn.cursor()
    
    subject = email_data.get('subject', '')
    payload = email_data.get('payload', '')
    word_count = count_words(payload)
    
    if word_count < MIN_WORD_COUNT:
        return False  # Too short
    
    date_str = email_data.get('date')
    date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    era = determine_era(date_str)
    category = categorize_subject(subject)
    
    try:
        cursor.execute('''INSERT INTO sent_emails 
                         (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (email_data['id'], email_data.get('threadId'), date, subject, 
                       word_count, category, era))
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate

def store_incoming_email(conn, email_data: dict, my_email: str):
    """Store incoming email"""
    cursor = conn.cursor()
    
    sender = email_data.get('sender', '')
    if my_email.lower() in sender.lower():
        return False  # Not incoming
    
    date_str = email_data.get('date')
    date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    era = determine_era(date_str)
    
    try:
        cursor.execute('''INSERT INTO incoming_emails 
                         (gmail_id, thread_id, date, subject, from_email, era)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (email_data['id'], email_data.get('threadId'), date, 
                       email_data.get('subject', ''), sender, era))
        return True
    except sqlite3.IntegrityError:
        return False

def main(dry_run: bool = False):
    """Main execution"""
    try:
        init_db()
        logger.info("✓ Email scanner ready for API integration")
        logger.info(f"Minimum word count: {MIN_WORD_COUNT}")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
