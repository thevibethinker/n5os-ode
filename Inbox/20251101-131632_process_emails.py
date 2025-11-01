#!/usr/bin/env python3
import sqlite3
import base64
from datetime import datetime
from email.utils import parsedate_to_datetime

def extract_word_count(body_text):
    """Estimate word count from text"""
    if not body_text:
        return 100
    words = body_text.split()
    return len(words)

def extract_date_from_header(date_str):
    """Convert email date header to YYYY-MM-DD format"""
    try:
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        dt = parsedate_to_datetime(date_str)
        return dt.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def process_emails(emails_list):
    """Process the Gmail API response and insert into database"""
    
    # Connect to database
    conn = sqlite3.connect('/home/workspace/productivity_tracker.db')
    cursor = conn.cursor()
    
    stats = {
        'found': 0,
        'inserted': 0,
        'duplicates': 0,
        'errors': 0
    }
    
    for email in emails_list:
        try:
            stats['found'] += 1
            
            gmail_id = email.get('id')
            thread_id = email.get('threadId')
            date_str = None
            subject = None
            word_count = 100
            
            # Extract date and subject from headers
            headers = email.get('payload', {}).get('headers', [])
            for header in headers:
                if header.get('name') == 'Date':
                    date_str = header.get('value')
                elif header.get('name') == 'Subject':
                    subject = header.get('value')
            
            # Extract body text to count words
            parts = email.get('payload', {}).get('parts', [])
            body_text = ""
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        try:
                            body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
                        except:
                            pass
            
            word_count = extract_word_count(body_text)
            date = extract_date_from_header(date_str)
            
            # Insert into database
            cursor.execute('''
                INSERT OR IGNORE INTO sent_emails 
                (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                gmail_id,
                thread_id,
                date,
                subject or 'No Subject',
                word_count,
                '',
                'now'
            ))
            
            if cursor.rowcount > 0:
                stats['inserted'] += 1
                print(f"✓ Inserted: {subject or 'No Subject'} ({word_count} words)")
            else:
                stats['duplicates'] += 1
                print(f"✗ Duplicate: {subject or 'No Subject'}")
                
        except Exception as e:
            stats['errors'] += 1
            print(f"✗ Error processing email: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return stats
