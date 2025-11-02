#!/usr/bin/env python3
import sqlite3
import json
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

def count_words(text):
    """Count words in text, default to 100 if empty."""
    if not text:
        return 100
    return len(text.split())

def extract_date_from_email(email_data):
    """Extract and format date from email data."""
    date_str = email_data.get('date', '')
    try:
        # Parse ISO format date and return as YYYY-MM-DD
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def process_emails(emails):
    """Process email data and return list of tuples for insertion."""
    processed = []
    
    for email in emails:
        try:
            gmail_id = email.get('id', '')
            thread_id = email.get('threadId', '')
            date = extract_date_from_email(email)
            subject = email.get('subject', 'No Subject')
            
            # Extract text for word count
            snippet = email.get('snippet', '')
            text_content = email.get('text', snippet)
            word_count = count_words(text_content)
            
            era = 'now'
            subject_category = 'general'  # Default category
            
            processed.append((
                gmail_id, thread_id, date, subject, 
                word_count, subject_category, era
            ))
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            continue
    
    return processed

def insert_emails(db_path, email_data_list):
    """Insert emails into the database."""
    inserted = 0
    skipped = 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for email_data in email_data_list:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO sent_emails 
                    (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', email_data)
                
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Error inserting email record: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return inserted, skipped
    except Exception as e:
        logger.error(f"Database error: {e}")
        return 0, 0

def main():
    # Read email data from stdin or JSON file
    try:
        # Get email data from command line or stdin
        email_json = sys.stdin.read()
        emails = json.loads(email_json)
        
        if not isinstance(emails, list):
            emails = [emails]
        
        logger.info(f"Number of emails found: {len(emails)}")
        
        # Process emails
        processed_emails = process_emails(emails)
        logger.info(f"Number of emails processed: {len(processed_emails)}")
        
        # Insert into database
        db_path = '/home/workspace/productivity_tracker.db'
        inserted, skipped = insert_emails(db_path, processed_emails)
        
        logger.info(f"Number of emails inserted (new): {inserted}")
        logger.info(f"Number of emails skipped (duplicates): {skipped}")
        
        return 0
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
