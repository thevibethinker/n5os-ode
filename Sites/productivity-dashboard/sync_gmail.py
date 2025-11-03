#!/usr/bin/env python3
"""
Gmail productivity sync script.
Fetches SENT emails from today and updates the productivity dashboard database.
"""

import sqlite3
import sys
import json
import subprocess
from datetime import date


def count_words(text):
    """Count words in text payload, excluding quoted replies and signatures."""
    if not text:
        return 0
    
    lines = text.split('\n')
    original_lines = []
    
    for line in lines:
        # Skip quoted lines (start with > or multiple >)
        if line.strip().startswith('>'):
            continue
        
        # Stop at common reply markers
        if any(marker in line for marker in [
            'On ', ' wrote:',
            'From:',
            'Sent:',
            'To:',
            'Subject:',
            '-----Original Message-----',
            '________________________________',
        ]):
            break
        
        # Skip signature blocks
        if any(sig in line for sig in [
            'V-OS Tags:',
            '{TWIN}',
            '{CATG}',
            'Best,',
            'Sent via Superhuman',
            '---',
        ]):
            break
        
        original_lines.append(line)
    
    original_text = ' '.join(original_lines)
    return len(original_text.split())


def fetch_gmail_via_cli():
    """Use Zo CLI to fetch Gmail data."""
    today = date.today().isoformat()
    
    # Create a temporary Python script to call the Gmail tool
    script = f"""
import sys
import json
sys.path.insert(0, '/root/.config/zo/lib')

try:
    from pipedream import use_app_gmail
    result = use_app_gmail(
        tool_name="gmail-find-email",
        configured_props={{
            "q": "in:sent after:{today}",
            "withTextPayload": True,
            "maxResults": 100
        }}
    )
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"error": str(e)}}), file=sys.stderr)
    sys.exit(1)
"""
    
    # For now, return empty list (will be integrated with proper API)
    return []


def sync_gmail_to_dashboard():
    """Fetch sent emails and update dashboard database."""
    
    today = date.today().isoformat()
    print(f"📅 Syncing Gmail data for {today}...")
    
    # For now, manually pass the email data since API integration needs work
    # This will be replaced with actual Gmail API call
    print("⚠️  Manual mode: Please trigger via API endpoint")
    print("    Use: curl -X POST http://localhost:3000/api/refresh")
    
    return False


if __name__ == "__main__":
    # Check if email data was passed as argument (from API call)
    if len(sys.argv) > 1 and sys.argv[1] == "--with-data":
        # Read JSON from stdin
        import json
        data = json.load(sys.stdin)
        emails = data.get('emails', [])
        today = date.today().isoformat()
        
        total_emails = len(emails)
        total_words = 0
        
        for email in emails:
            payload = email.get('payload', '')
            words = count_words(payload)
            total_words += words
            print(f"  • {email.get('subject', 'No subject')[:50]}: {words} words")
        
        rpi = total_emails + (total_words / 100)
        print(f"📊 Metrics: {total_emails} emails, {total_words} words, RPI: {rpi:.2f}")
        
        # Update database
        db_path = '/home/workspace/productivity_tracker.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats (date, email_count, total_words, rpi)
            VALUES (?, ?, ?, ?)
        """, (today, total_emails, total_words, rpi))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Dashboard updated successfully!")
        sys.exit(0)
    else:
        success = sync_gmail_to_dashboard()
        sys.exit(0 if success else 1)
