import sqlite3
from email.utils import parsedate_to_datetime
import base64
import sys

conn = sqlite3.connect('/home/workspace/productivity_tracker.db')
cursor = conn.cursor()

emails = []

# Read emails json from stdin
import json
for line in sys.stdin:
    emails += json.loads(line)

inserted = 0
skipped = 0

for email in emails:
    gmail_id = email.get('id')
    thread_id = email.get('threadId')

    headers = email.get('payload', {}).get('headers', [])
    date_str = None
    subject = None
    for h in headers:
        if h['name'] == 'Date':
            date_str = h['value']
        elif h['name'] == 'Subject':
            subject = h['value']

    # Convert Date string to YYYY-MM-DD
    if date_str:
        dt = parsedate_to_datetime(date_str)
        date = dt.date().isoformat()
    else:
        date = '1970-01-01'

    # Estimate word count from snippet or body
    snippet = email.get('snippet', '')
    if snippet:
        word_count = len(snippet.split())
    else:
        # Try to decode base64 body text
        body_data = email.get('payload', {}).get('body', {}).get('data')
        text = ''
        if body_data:
            try:
                text = base64.urlsafe_b64decode(body_data + '==').decode('utf-8')
            except Exception:
                text = ''
        word_count = len(text.split()) if text else 100

    era = 'now'
    subject_category = None  # placeholder

    try:
        cursor.execute('''
        INSERT OR IGNORE INTO sent_emails (gmail_id, thread_id, date, subject, word_count, subject_category, era)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (gmail_id, thread_id, date, subject, word_count, subject_category, era))
        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    except Exception as e:
        skipped += 1

conn.commit()
conn.close()

print(f'Inserted: {inserted}')
print(f'Skipped: {skipped}')
