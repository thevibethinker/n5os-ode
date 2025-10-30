#!/usr/bin/env python3
"""
Process Gmail sent emails and insert into productivity tracker database.
"""

import sqlite3
import json
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "/home/workspace/productivity_tracker.db"

def count_words(text):
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())

def extract_email_data(email_data):
    """Extract relevant data from email message."""
    try:
        gmail_id = email_data.get('id')
        thread_id = email_data.get('threadId')
        
        # Parse date from headers
        headers = email_data.get('payload', {}).get('headers', [])
        date_str = None
        subject = None
        
        for header in headers:
            if header.get('name') == 'Date':
                date_str = header.get('value')
            elif header.get('name') == 'Subject':
                subject = header.get('value')
        
        # Parse date
        date = None
        if date_str:
            try:
                dt = parsedate_to_datetime(date_str)
                date = dt.strftime('%Y-%m-%d')
            except Exception as e:
                logger.warning(f"Failed to parse date '{date_str}': {e}")
        
        # Extract word count from snippet or body
        snippet = email_data.get('snippet', '')
        word_count = count_words(snippet) if snippet else 100
        
        return {
            'gmail_id': gmail_id,
            'thread_id': thread_id,
            'date': date,
            'subject': subject or 'Untitled',
            'word_count': max(word_count, 1),  # At least 1
            'era': 'now'
        }
    except Exception as e:
        logger.error(f"Error extracting email data: {e}")
        return None

def insert_email(cursor, email_data):
    """Insert email into database."""
    if not email_data or not email_data.get('gmail_id'):
        return False
    
    try:
        cursor.execute(
            """INSERT OR IGNORE INTO sent_emails 
               (gmail_id, thread_id, date, subject, word_count, subject_category, era)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                email_data['gmail_id'],
                email_data['thread_id'],
                email_data['date'],
                email_data['subject'],
                email_data['word_count'],
                None,  # subject_category
                email_data['era']
            )
        )
        return True
    except Exception as e:
        logger.error(f"Failed to insert email {email_data.get('gmail_id')}: {e}")
        return False

def process_emails(emails):
    """Process emails and insert into database."""
    if not emails:
        logger.warning("No emails provided")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for email_data in emails:
        extracted = extract_email_data(email_data)
        if not extracted:
            skipped += 1
            continue
        
        if insert_email(cursor, extracted):
            inserted += 1
            logger.debug(f"Inserted email: {extracted['subject'][:50]}...")
        else:
            skipped += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Emails processed: inserted={inserted}, skipped={skipped}")
    return inserted, skipped

if __name__ == "__main__":
    # This would be called with email data from Gmail
    # For now, just logging the structure
    logger.info("Email processing script ready")
