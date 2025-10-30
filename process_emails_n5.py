#!/usr/bin/env python3
"""
Process sent emails for the day and update productivity tracker database.
Extracts metadata and calculates RPI score.
"""

import sqlite3
import json
import re
from datetime import datetime
import base64

# Email data extracted from Gmail API response
EMAILS_DATA = [
    {
        'id': '19a30b66c5fbc577',
        'threadId': '19a2604561507d90',
        'date': '2025-10-29T16:04:13.000Z',
        'subject': 'Re: Follow-Up: Pamela x Careerspan — Next Play • Zo Computer • Founder Dinners',
        'snippet': "Please don't apologize in the slightest. I'm sure it had everything with you being an excellent daughter and I could never begrudge anyone that! Just sent out the changed invite. I'll see",
        'body_size': 12022
    },
    {
        'id': '19a30704e6f8381d',
        'threadId': '19a30704e6f8381d',
        'date': '2025-10-28T21:15:12.000Z',
        'subject': 'So great to connect',
        'snippet': "Hey Eric, I just wanted to drop a quick note saying that you're an absolute badass and it was a pleasure being on a panel with you. It's clear you have spent a lot of time thinking and caring",
        'body_size': 867
    },
    {
        'id': '19a2c70ee2cfab56',
        'threadId': '19a2c6fcfa18c138',
        'date': '2025-10-28T20:09:50.000Z',
        'subject': 'Re: CONFIDENTIAL: Finance Placement',
        'snippet': "Roger roger, I've sent it along. We'll get moving on it when Ilse's up in the morning.",
        'body_size': 3694
    },
    {
        'id': '19a2c707d0fd5534',
        'threadId': '19a2c6fcfa18c138',
        'date': '2025-10-28T20:09:21.000Z',
        'subject': 'Fwd: CONFIDENTIAL: Finance Placement',
        'snippet': 'Best, Vrijen S Attawar CEO @ Careerspan',
        'body_size': 9287
    },
    {
        'id': '19a2b2a9cd124c79',
        'threadId': '19a2b2a9cd124c79',
        'date': '2025-10-28T14:13:24.000Z',
        'subject': 'N5 OS Core - 7 Artifact Files for Distribution',
        'snippet': 'Hi V, Attached are the 7 artifact files for N5 OS Core distribution',
        'body_size': 852
    }
]

def estimate_word_count(body_size):
    """Estimate word count from body size."""
    # Average word is ~5 characters + 1 space
    return max(100, int(body_size / 6))

def extract_date(date_str):
    """Convert ISO datetime to YYYY-MM-DD format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def categorize_subject(subject):
    """Categorize email based on subject."""
    subject_lower = subject.lower()
    
    if any(word in subject_lower for word in ['follow-up', 'next play', 'founder', 'dinner']):
        return 'networking'
    elif any(word in subject_lower for word in ['n5', 'os', 'core', 'artifact']):
        return 'product'
    elif any(word in subject_lower for word in ['finance', 'confidential', 'placement']):
        return 'business'
    elif any(word in subject_lower for word in ['webinar', 'panel', 'great to connect']):
        return 'speaking'
    else:
        return 'general'

def process_emails():
    """Process emails and update database."""
    db_path = '/home/workspace/productivity_tracker.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    for email in EMAILS_DATA:
        try:
            gmail_id = email['id']
            thread_id = email['threadId']
            date = extract_date(email['date'])
            subject = email['subject']
            word_count = estimate_word_count(email['body_size'])
            category = categorize_subject(subject)
            era = 'now'
            
            # Insert or ignore to avoid duplicates
            cursor.execute('''
                INSERT OR IGNORE INTO sent_emails 
                (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (gmail_id, thread_id, date, subject, word_count, category, era))
            
            if cursor.rowcount > 0:
                inserted_count += 1
                print(f"✓ Inserted: {subject[:50]}... ({word_count} words)")
            else:
                skipped_count += 1
                print(f"- Skipped (duplicate): {subject[:50]}...")
                
        except Exception as e:
            print(f"✗ Error processing email {email['id']}: {str(e)}")
            skipped_count += 1
    
    conn.commit()
    conn.close()
    
    return inserted_count, skipped_count

def main():
    print("=" * 60)
    print("N5 Productivity Tracker: Email Processing")
    print("=" * 60)
    print()
    
    # Process emails
    print("STEP 1: Processing emails from Gmail...")
    print("-" * 60)
    inserted, skipped = process_emails()
    print()
    print(f"Results: {inserted} inserted, {skipped} skipped")
    print()
    
    # Calculate RPI
    print("STEP 2: Calculating RPI Score...")
    print("-" * 60)
    today = datetime.now().strftime('%Y-%m-%d')
    
    db_path = '/home/workspace/productivity_tracker.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get today's email metrics
    cursor.execute('''
        SELECT COUNT(*), SUM(word_count)
        FROM sent_emails
        WHERE date = ?
    ''', (today,))
    
    result = cursor.fetchone()
    email_count = result[0] if result[0] else 0
    total_words = result[1] if result[1] else 0
    
    # Calculate RPI components
    # RPI = (emails_sent * 10) + (total_words / 100) + (focus_time if tracked)
    rpi_score = (email_count * 10) + (total_words / 100)
    
    print(f"Date: {today}")
    print(f"Emails sent: {email_count}")
    print(f"Total words: {total_words}")
    print(f"RPI Score: {rpi_score:.2f}")
    print()
    
    # Store RPI in daily_stats
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats 
            (date, emails_sent, total_words, rpi_score)
            VALUES (?, ?, ?, ?)
        ''', (today, email_count, total_words, rpi_score))
        
        conn.commit()
        print("✓ RPI score saved to database")
    except Exception as e:
        print(f"✗ Error saving RPI score: {str(e)}")
    finally:
        conn.close()
    
    print()
    print("=" * 60)
    print("✓ Productivity Tracker Auto-Scan Complete")
    print("=" * 60)

if __name__ == '__main__':
    main()
