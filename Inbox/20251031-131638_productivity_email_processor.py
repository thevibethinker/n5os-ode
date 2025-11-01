#!/usr/bin/env python3
"""
Process sent emails from today and update productivity database with RPI calculation.
"""
import sqlite3
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def extract_word_count(text):
    """Estimate word count from text."""
    if not text:
        return 100
    words = text.split()
    return len(words)


def parse_email_date(date_str):
    """Parse email date and convert to YYYY-MM-DD format."""
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        return datetime.now().strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def process_emails():
    """Process today's sent emails and insert into database."""
    
    # Email data from Gmail API - 10 emails found
    emails = [
        {
            'id': '19a33bf2f7dc93cc',
            'threadId': '19a33bf2f7dc93cc',
            'date': '2025-10-30T06:12:39.000Z',
            'subject': 'Huge fan — got a product rec for you',
            'text': 'Hey Nate, I\'m a longtime follower and fan. You are—pound-for-pound—the best source of tactical AI advice on the internet. I\'m reaching out because I\'m a big believer in zo.computer. I think someone like yourself could set up a wicked awesome setup that far outstrips anything tools like n8n or Zapier could do.'
        },
        {
            'id': '19a30b66c5fbc577',
            'threadId': '19a2604561507d90',
            'date': '2025-10-29T16:04:13+0000',
            'subject': 'Re: Follow-Up: Pamela x Careerspan',
            'text': 'Please don\'t apologize in the slightest. I\'m sure it had everything with you being an excellent daughter and I could never begrudge anyone that! Just sent out the changed invite. I\'ll see you Monday morning.'
        },
        {
            'id': '19a304054a8d84cc',
            'threadId': '19a304054a8d84cc',
            'date': '2025-10-29T13:55:14+0000',
            'subject': 'Setting up Zo',
            'text': 'My repo - https://github.com/vrijenattawar/zo-n5os-core. Give a clean Zo the repo install instructions plus this guide'
        },
        {
            'id': '19a3016b12cc7a6d',
            'threadId': '19a2604561507d90',
            'date': '2025-10-29T13:09:45+0000',
            'subject': 'Re: Follow-Up: Pamela x Careerspan',
            'text': 'Super excited to see you later today as well! I should have something pretty cool to spin up for you. Duly noted on Ben, Steffy and Jesse. Would absolutely love to be connected to Sarah.'
        }
    ]
    
    try:
        conn = sqlite3.connect('/home/workspace/productivity_tracker.db')
        cursor = conn.cursor()
        logger.info("Connected to productivity database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return 1
    
    inserted_count = 0
    skipped_count = 0
    
    for email in emails:
        try:
            gmail_id = email['id']
            thread_id = email['threadId']
            date = parse_email_date(email['date'])
            subject = email['subject']
            word_count = extract_word_count(email['text'])
            era = "now"
            subject_category = None
            
            cursor.execute(
                """INSERT OR IGNORE INTO sent_emails 
                (gmail_id, thread_id, date, subject, word_count, subject_category, era)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (gmail_id, thread_id, date, subject, word_count, subject_category, era)
            )
            
            if cursor.rowcount > 0:
                inserted_count += 1
                logger.info(f"Inserted: {subject[:40]}... ({word_count} words)")
            else:
                skipped_count += 1
                logger.info(f"Skipped: {subject[:40]}... (duplicate)")
                
        except Exception as e:
            logger.error(f"Error processing email {email.get('id')}: {e}")
            continue
    
    conn.commit()
    logger.info(f"Inserted {inserted_count} new, skipped {skipped_count} duplicates")
    
    # Calculate RPI using correct schema
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT COUNT(*) as actual_emails, SUM(word_count) as actual_words
            FROM sent_emails
            WHERE date = ?
        """, (today,))
        
        result = cursor.fetchone()
        actual_emails = result[0] or 0
        actual_words = result[1] or 0
        
        # Default expected values
        expected_emails = 5
        expected_words = 500
        
        # Calculate ratios and RPI
        email_ratio = actual_emails / expected_emails if expected_emails > 0 else 0
        word_ratio = actual_words / expected_words if expected_words > 0 else 0
        
        # RPI = (email_ratio + word_ratio) / 2 * 100
        rpi_score = ((email_ratio + word_ratio) / 2) * 100
        
        # Insert into both tables
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats 
            (date, emails_sent, rpi)
            VALUES (?, ?, ?)
        """, (today, actual_emails, rpi_score))
        
        cursor.execute("""
            INSERT OR REPLACE INTO rpi_scores 
            (date, actual_emails, actual_words, expected_emails, expected_words, 
             email_ratio, word_ratio, rpi_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (today, actual_emails, actual_words, expected_emails, expected_words,
              email_ratio, word_ratio, rpi_score))
        
        conn.commit()
        logger.info(f"RPI Score for {today}: {rpi_score:.2f}")
        logger.info(f"  Actual: {actual_emails} emails, {actual_words} words")
        logger.info(f"  Expected: {expected_emails} emails, {expected_words} words")
        logger.info(f"  Ratios: email={email_ratio:.2f}, word={word_ratio:.2f}")
        
    except Exception as e:
        logger.error(f"Error calculating RPI: {e}")
        conn.close()
        return 1
    
    conn.close()
    logger.info("Productivity scan complete")
    return 0


if __name__ == "__main__":
    exit(process_emails())
