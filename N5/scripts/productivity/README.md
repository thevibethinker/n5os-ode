# Productivity Tracker - Email Scanner

## Overview

Simple email productivity tracking system that counts sent/incoming emails and tracks unreplied threads.

## Components

### 1. Email Scanner (`email_scanner.py`)
Simple numerical tracking of email volumes across eras.

**Features:**
- Count sent emails (your productivity output)
- Count incoming emails (your workload)
- Filter trivial emails (< 10 words)
- Categorize by subject line
- Era tagging (pre-superhuman, post-superhuman, post-zo)

### 2. Unreplied Thread Tracker (`unreplied_tracker.py`) ⭐ NEW
Tracks emails that haven't been replied to within 3 days.

**Features:**
- Scans last 30 days of incoming emails
- Checks for sent replies in same thread
- Priority scoring (high/medium/low)
- Daily digest generation

**Priority Rules:**
- **High:** Contains urgent/investor/funding keywords OR 7+ days old
- **Medium:** Contains partnership/hiring/customer keywords OR 5+ days old
- **Low:** Everything else 3+ days old

## Usage

### Track Unreplied Threads
```bash
python3 /home/workspace/N5/scripts/productivity/unreplied_tracker.py
# Output: Lists/unreplied_digest.md
```

**Dry run mode:**
```bash
python3 /home/workspace/N5/scripts/productivity/unreplied_tracker.py --dry-run
# Preview without saving
```

### Query Database
```sql
-- Sent email volume by era
SELECT era, COUNT(*) as total, 
       COUNT(DISTINCT date) as days,
       ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT date), 1) as per_day
FROM sent_emails 
GROUP BY era;

-- Current unreplied threads
SELECT subject, from_email, days_pending, priority
FROM unreplied_threads
ORDER BY 
    CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
    days_pending DESC;

-- High priority unreplied
SELECT * FROM unreplied_threads WHERE priority = 'high';
```

## Database Schema

```sql
sent_emails:
  - gmail_id (unique)
  - thread_id
  - date
  - subject
  - word_count
  - subject_category
  - era

incoming_emails:
  - gmail_id (unique)
  - thread_id
  - date
  - subject
  - from_email
  - era

unreplied_threads:
  - thread_id (unique)
  - gmail_message_id
  - subject
  - sender (from_email)
  - received_at
  - days_pending
  - priority (high/medium/low)
  - last_checked
```

## Automation Ideas

1. **Daily digest:** Schedule `unreplied_tracker.py` to run at 9AM
2. **Email alerts:** Send digest to your email
3. **Slack integration:** Post high-priority unreplied to Slack
4. **Gmail sync:** Auto-populate database from Gmail API

## Example Output

```
=== UNREPLIED THREADS ===

HIGH PRIORITY (1):
  [10d] Partnership opportunity - URGENT review needed
      From: investor@example.com

MEDIUM PRIORITY (2):
  [5d] Interview scheduling for senior role
      From: recruiter@bigtech.com
  [7d] Customer feedback on your product
      From: customer@company.com
```

---

**Created:** 2025-10-25  
**Worker:** con_SnJYaitDHV5TlSc8  
**Orchestrator:** con_6NobvGrBPaGJQwZA
