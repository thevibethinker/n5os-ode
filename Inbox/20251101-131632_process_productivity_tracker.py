import sqlite3
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

# Email data from Gmail API response
emails_data = [
    {
        "gmail_id": "19a3b68daf7f085a",
        "thread_id": "19a2604561507d90",
        "date": "2025-10-31T17:55:19+0000",
        "subject": "Re: Follow-Up: Pamela x Careerspan — Next Play • Zo Computer • Founder Dinners",
        "snippet": "Amazing! Glad you're going to be able to join...",
        "word_count": 85
    },
    {
        "gmail_id": "19a36381a1234054",
        "thread_id": "19a36381a1234054",
        "date": "2025-10-30T17:43:58+0000",
        "subject": "Hello from Careerspan!",
        "snippet": "Hey Grady, I just wanted to take a few minutes to thank you...",
        "word_count": 120
    },
    {
        "gmail_id": "19a35df7ac6d4229",
        "thread_id": "199f10c8d44647ee",
        "date": "2025-10-30T16:07:10+0000",
        "subject": "Re: Dylan Johnson x Vrijen Attawar",
        "snippet": "Hey Dylan, Absolutely — let me do it right now :)",
        "word_count": 180
    },
    {
        "gmail_id": "19a33bf2f7dc93cc",
        "thread_id": "19a33bf2f7dc93cc",
        "date": "2025-10-30T06:12:39+0000",
        "subject": "Huge fan — got a product rec for you",
        "snippet": "Hey Nate, I'm a longtime follower and fan...",
        "word_count": 95
    }
]

# Connect to database
conn = sqlite3.connect('/home/workspace/productivity_tracker.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sent_emails (
        gmail_id TEXT PRIMARY KEY,
        thread_id TEXT,
        date TEXT,
        subject TEXT,
        word_count INTEGER,
        subject_category TEXT,
        era TEXT
    )
''')

# Process each email
emails_inserted = 0
emails_skipped = 0

for email in emails_data:
    try:
        # Parse date to YYYY-MM-DD format
        date_obj = datetime.fromisoformat(email["date"].replace("+0000", "+00:00"))
        date_str = date_obj.strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT OR IGNORE INTO sent_emails
            (gmail_id, thread_id, date, subject, word_count, subject_category, era)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            email["gmail_id"],
            email["thread_id"],
            date_str,
            email["subject"],
            email["word_count"],
            None,  # subject_category
            "now"  # era
        ))
        
        if cursor.rowcount > 0:
            emails_inserted += 1
            logging.info(f"Inserted email: {email['subject']}")
        else:
            emails_skipped += 1
            logging.info(f"Skipped duplicate email: {email['subject']}")
    except Exception as e:
        logging.error(f"Error inserting email {email['gmail_id']}: {e}")

conn.commit()

logging.info(f"Completed: {emails_inserted} emails inserted, {emails_skipped} emails skipped")

# Verify the data
cursor.execute('SELECT COUNT(*) FROM sent_emails')
total = cursor.fetchone()[0]
logging.info(f"Total emails in database: {total}")

conn.close()
