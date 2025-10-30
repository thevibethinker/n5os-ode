#!/usr/bin/env python3
"""
Productivity Tracker Auto-Scan Script
Processes today's sent emails and calculates RPI score
"""
import sqlite3
import json
from datetime import datetime
from email.utils import parsedate_to_datetime

# Configuration
DB_PATH = "/home/workspace/productivity_tracker.db"
EMAIL_DATA_FILE = "/home/workspace/email_scan_data.json"

def estimate_word_count(text):
    """Estimate word count from text"""
    if not text:
        return 100
    return len(text.split())

def process_emails_from_json(email_data):
    """Process emails from JSON data structure"""
    emails_to_insert = []
    
    for email in email_data:
        # Extract metadata
        gmail_id = email.get('id', '')
        thread_id = email.get('threadId', '')
        
        # Parse date
        headers = email.get('payload', {}).get('headers', [])
        date_str = None
        subject = None
        
        for header in headers:
            if header.get('name') == 'Date':
                date_str = header.get('value', '')
            elif header.get('name') == 'Subject':
                subject = header.get('value', '')
        
        # Convert date
        try:
            if date_str:
                dt = parsedate_to_datetime(date_str)
                date = dt.strftime('%Y-%m-%d')
            else:
                date = datetime.now().strftime('%Y-%m-%d')
        except:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Extract body/snippet for word count
        snippet = email.get('snippet', '')
        word_count = estimate_word_count(snippet)
        
        emails_to_insert.append({
            'gmail_id': gmail_id,
            'thread_id': thread_id,
            'date': date,
            'subject': subject or 'No Subject',
            'word_count': word_count,
            'subject_category': '',  # Will be empty, can be filled manually
            'era': 'now'
        })
    
    return emails_to_insert

def insert_emails_to_db(emails):
    """Insert emails into the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        inserted = 0
        skipped = 0
        
        for email in emails:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO sent_emails 
                    (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email['gmail_id'],
                    email['thread_id'],
                    email['date'],
                    email['subject'],
                    email['word_count'],
                    email['subject_category'],
                    email['era']
                ))
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error inserting email {email['gmail_id']}: {str(e)}")
                skipped += 1
        
        conn.commit()
        conn.close()
        
        return inserted, skipped
    except Exception as e:
        print(f"Database error: {str(e)}")
        return 0, len(emails)

def main():
    """Main execution function"""
    print("🔄 Starting Productivity Tracker Auto-Scan...")
    
    # Load email data
    try:
        with open(EMAIL_DATA_FILE, 'r') as f:
            email_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Email data file not found: {EMAIL_DATA_FILE}")
        return False
    
    print(f"📧 Found {len(email_data)} sent emails")
    
    # Process emails
    emails_to_insert = process_emails_from_json(email_data)
    print(f"✅ Processed {len(emails_to_insert)} emails for insertion")
    
    # Insert into database
    inserted, skipped = insert_emails_to_db(emails_to_insert)
    print(f"✅ Inserted: {inserted} new emails")
    print(f"⏭️  Skipped: {skipped} duplicates")
    
    # Try to calculate RPI
    print("\n🔢 Calculating RPI Score...")
    import subprocess
    today = datetime.now().strftime('%Y-%m-%d')
    result = subprocess.run(
        ['python3', '/home/workspace/N5/scripts/productivity/rpi_calculator.py', '--date', today],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ RPI calculation complete")
        if result.stdout:
            print(f"📊 Output: {result.stdout}")
    else:
        print(f"⚠️  RPI calculation had issues:")
        if result.stderr:
            print(f"   {result.stderr}")
    
    print("\n✨ Productivity Tracker Auto-Scan Complete!")
    return True

if __name__ == '__main__':
    main()
