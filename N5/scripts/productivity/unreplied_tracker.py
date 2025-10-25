#!/usr/bin/env python3
"""
Unreplied Thread Tracker
Identifies incoming emails not replied to within 3 days
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path('/home/workspace/productivity_tracker.db')
REPLY_THRESHOLD_DAYS = 3

def init_unreplied_table():
    """Create unreplied_threads table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unreplied_threads (
            id INTEGER PRIMARY KEY,
            thread_id TEXT UNIQUE NOT NULL,
            gmail_message_id TEXT NOT NULL,
            subject TEXT,
            sender TEXT,
            received_at TIMESTAMP NOT NULL,
            days_pending INTEGER,
            priority TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✓ Unreplied threads table initialized")

def check_for_reply(thread_id: str, received_at: datetime, conn) -> bool:
    """Check if we've sent a reply in this thread after received_at"""
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM sent_emails 
        WHERE thread_id = ? 
        AND datetime(date) > datetime(?)
    ''', (thread_id, received_at.isoformat()))
    
    count = cursor.fetchone()[0]
    return count > 0

def calculate_priority(subject: str, from_email: str, days_pending: int) -> str:
    """Calculate priority based on subject, sender, and age"""
    subject_lower = subject.lower()
    
    # High priority keywords
    high_keywords = ['urgent', 'asap', 'important', 'investor', 'funding', 'crisis', 'emergency']
    # Medium priority
    med_keywords = ['partnership', 'hiring', 'interview', 'customer', 'client', 'meeting']
    
    # Check subject
    if any(kw in subject_lower for kw in high_keywords):
        return 'high'
    elif any(kw in subject_lower for kw in med_keywords):
        return 'medium'
    
    # Age-based escalation
    if days_pending >= 7:
        return 'high'
    elif days_pending >= 5:
        return 'medium'
    
    return 'low'

def scan_unreplied_threads(dry_run: bool = False):
    """Scan for threads that haven't been replied to in 3+ days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all incoming emails
    cursor.execute('''
        SELECT gmail_id, thread_id, subject, from_email, date 
        FROM incoming_emails
        WHERE date >= date('now', '-30 days')
        ORDER BY date DESC
    ''')
    
    incoming = cursor.fetchall()
    unreplied = []
    now = datetime.now()
    
    for gmail_id, thread_id, subject, from_email, date_str in incoming:
        received_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        days_pending = (now - received_at).days
        
        # Skip if less than threshold
        if days_pending < REPLY_THRESHOLD_DAYS:
            continue
        
        # Check if we've replied
        has_reply = check_for_reply(thread_id, received_at, conn)
        
        if not has_reply:
            priority = calculate_priority(subject, from_email, days_pending)
            unreplied.append({
                'thread_id': thread_id,
                'gmail_id': gmail_id,
                'subject': subject,
                'from_email': from_email,
                'received_at': received_at,
                'days_pending': days_pending,
                'priority': priority
            })
            
            if not dry_run:
                # Store in database
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO unreplied_threads 
                        (thread_id, gmail_message_id, subject, sender, received_at, days_pending, priority)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (thread_id, gmail_id, subject, from_email, received_at.isoformat(), 
                          days_pending, priority))
                except Exception as e:
                    logger.error(f"Error storing unreplied thread: {e}")
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    # Generate report
    logger.info(f"✓ Found {len(unreplied)} unreplied threads (>{REPLY_THRESHOLD_DAYS} days)")
    
    if unreplied:
        logger.info("\n=== UNREPLIED THREADS ===")
        
        # Group by priority
        by_priority = {'high': [], 'medium': [], 'low': []}
        for item in unreplied:
            by_priority[item['priority']].append(item)
        
        for priority in ['high', 'medium', 'low']:
            items = by_priority[priority]
            if items:
                logger.info(f"\n{priority.upper()} PRIORITY ({len(items)}):")
                for item in items[:5]:  # Show top 5
                    logger.info(f"  [{item['days_pending']}d] {item['subject'][:60]}")
                    logger.info(f"      From: {item['from_email']}")
    
    return unreplied

def generate_digest():
    """Generate a daily digest of unreplied threads"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT priority, COUNT(*) as count, 
               AVG(days_pending) as avg_days,
               MAX(days_pending) as max_days
        FROM unreplied_threads
        GROUP BY priority
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END
    ''')
    
    summary = cursor.fetchall()
    
    cursor.execute('''
        SELECT subject, sender, days_pending, priority
        FROM unreplied_threads
        WHERE priority = 'high'
        ORDER BY days_pending DESC
        LIMIT 10
    ''')
    
    high_priority = cursor.fetchall()
    conn.close()
    
    # Generate markdown digest
    digest = "# Unreplied Emails Digest\n\n"
    digest += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n\n"
    
    if summary:
        digest += "## Summary\n\n"
        digest += "| Priority | Count | Avg Days | Oldest |\n"
        digest += "|----------|-------|----------|--------|\n"
        for priority, count, avg_days, max_days in summary:
            digest += f"| {priority.title()} | {count} | {avg_days:.1f} | {max_days} |\n"
        digest += "\n"
    
    if high_priority:
        digest += "## High Priority (Top 10)\n\n"
        for subject, sender, days, priority in high_priority:
            digest += f"### [{days}d] {subject}\n"
            digest += f"**From:** {sender}  \n"
            digest += f"**Priority:** {priority.upper()}  \n\n"
    
    return digest

def main(dry_run: bool = False):
    """Main execution"""
    try:
        init_unreplied_table()
        unreplied = scan_unreplied_threads(dry_run=dry_run)
        
        if not dry_run and unreplied:
            digest = generate_digest()
            digest_path = Path('/home/workspace/Lists/unreplied_digest.md')
            digest_path.write_text(digest)
            logger.info(f"✓ Digest saved to: {digest_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without storing")
    exit(main(dry_run=parser.parse_args().dry_run))
