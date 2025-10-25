#!/usr/bin/env python3
"""
Simple Email Volume Scanner
Just counts sent/received emails, filters short ones, tracks subjects
"""

import sqlite3
import logging
import argparse
import re
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path('/home/workspace/productivity_tracker.db')
MIN_WORD_COUNT = 15  # Ignore very short emails

def determine_era(date_str: str) -> str:
    """Simple era detection based on date"""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    superhuman_date = datetime(2024, 11, 12, tzinfo=dt.tzinfo)
    zo_date = datetime(2025, 9, 1, tzinfo=dt.tzinfo)
    
    if dt < superhuman_date:
        return 'pre-superhuman'
    elif dt < zo_date:
        return 'post-superhuman'
    else:
        return 'post-zo'

def extract_subject_categories(subject: str) -> list:
    """Extract category hints from subject line"""
    subject_lower = subject.lower()
    categories = []
    
    # Common patterns
    if 're:' in subject_lower or 'fwd:' in subject_lower:
        categories.append('reply')
    else:
        categories.append('new')
    
    # Content hints
    patterns = {
        'meeting': r'\b(meeting|call|sync|catch up|coffee)\b',
        'hiring': r'\b(hire|hiring|candidate|interview|position|role)\b',
        'partnership': r'\b(partner|partnership|collaboration|collab)\b',
        'investor': r'\b(invest|funding|raise|capital|pitch)\b',
        'product': r'\b(product|feature|demo|launch)\b',
        'client': r'\b(client|customer|user)\b',
        'ops': r'\b(operations|admin|logistics|schedule)\b',
    }
    
    for category, pattern in patterns.items():
        if re.search(pattern, subject_lower):
            categories.append(category)
    
    return categories

def count_words(text: str) -> int:
    """Simple word counter"""
    if not text:
        return 0
    return len(text.split())

def process_email_batch(emails: list, my_email: str, is_sent: bool) -> dict:
    """Process batch of emails and return stats"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {
        'processed': 0,
        'inserted': 0,
        'skipped_short': 0,
        'skipped_duplicate': 0,
        'errors': 0
    }
    
    for email in emails:
        try:
            gmail_id = email.get('id')
            subject = email.get('subject', '(no subject)')
            date = email.get('date')
            sender = email.get('sender', '')
            payload = email.get('payload', '') or email.get('snippet', '')
            
            # Word count filter
            word_count = count_words(payload)
            if word_count < MIN_WORD_COUNT:
                stats['skipped_short'] += 1
                stats['processed'] += 1
                continue
            
            # Determine direction
            sender_email = re.search(r'<(.+?)>', sender)
            sender_email = sender_email.group(1) if sender_email else sender
            is_incoming = sender_email.lower() != my_email.lower()
            
            # For sent folder, all should be outgoing
            if is_sent:
                is_incoming = False
            
            # Era
            era = determine_era(date)
            
            # Subject categories
            categories = extract_subject_categories(subject)
            category_str = ','.join(categories)
            
            # Store
            try:
                cursor.execute('''INSERT INTO emails 
                             (gmail_message_id, thread_id, subject, sent_at, 
                              email_type, subject_tag, word_count, response_time_hours,
                              is_substantial, is_incoming, era)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (gmail_id, gmail_id[:10], subject, date, 
                           category_str, None, word_count, None,
                           True, is_incoming, era))
                stats['inserted'] += 1
            except sqlite3.IntegrityError:
                stats['skipped_duplicate'] += 1
            
            stats['processed'] += 1
            
        except Exception as e:
            logger.error(f"Error processing {email.get('id')}: {e}")
            stats['errors'] += 1
    
    conn.commit()
    conn.close()
    
    return stats

def generate_report():
    """Generate volume analysis report"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("EMAIL VOLUME ANALYSIS")
    print("="*60)
    
    # By era and direction
    print("\n### Volume by Era:")
    cursor.execute('''
        SELECT era, 
               COUNT(*) as total,
               SUM(CASE WHEN is_incoming = 0 THEN 1 ELSE 0 END) as sent,
               SUM(CASE WHEN is_incoming = 1 THEN 1 ELSE 0 END) as received
        FROM emails
        GROUP BY era
        ORDER BY CASE era 
            WHEN 'pre-superhuman' THEN 1 
            WHEN 'post-superhuman' THEN 2 
            WHEN 'post-zo' THEN 3 
        END
    ''')
    
    for row in cursor.fetchall():
        print(f"  {row[0]:20} | Total: {row[1]:4} | Sent: {row[2]:4} | Received: {row[3]:4}")
    
    # Subject analysis
    print("\n### Top Subject Patterns (Sent):")
    cursor.execute('''
        SELECT subject, COUNT(*) as count
        FROM emails
        WHERE is_incoming = 0
        GROUP BY LOWER(SUBSTR(subject, 1, 40))
        ORDER BY count DESC
        LIMIT 15
    ''')
    
    for row in cursor.fetchall():
        print(f"  [{row[1]:2}x] {row[0][:50]}")
    
    # Category breakdown
    print("\n### Category Hints (from subjects):")
    cursor.execute('''
        SELECT email_type, COUNT(*) as count
        FROM emails
        WHERE is_incoming = 0
        GROUP BY email_type
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        categories = row[0].split(',') if row[0] else ['unknown']
        print(f"  {row[1]:4} emails | {', '.join(categories[:3])}")
    
    conn.close()

def main(scan_type='sent', dry_run=False):
    """Main execution"""
    
    if dry_run:
        logger.info("[DRY RUN] Would scan Gmail and process emails")
        return 0
    
    logger.info(f"Starting {scan_type} email scan...")
    logger.info("Note: Actual Gmail API calls must be made via Zo's use_app_gmail")
    logger.info("This script processes results from those calls")
    
    # Generate report if data exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emails")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        generate_report()
    else:
        logger.info("No data yet - run with email data")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--type", default="sent", choices=['sent', 'received', 'both'])
    args = parser.parse_args()
    
    exit(main(scan_type=args.type, dry_run=args.dry_run))
