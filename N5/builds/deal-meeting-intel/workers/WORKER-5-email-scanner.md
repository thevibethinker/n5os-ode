---
created: 2026-01-18
last_edited: 2026-01-18
version: 2.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 5
title: Email Deal Scanner
est_time: 2 hours
dependencies: [1, 3]
status: ready
---

# Worker 5: Email Deal Scanner

## Prerequisites (✅ All Complete)

Phase 1 artifacts are ready:
- ✅ `file 'N5/scripts/deal_signal_router.py'` — DealSignalRouter class
- ✅ `file 'N5/scripts/notion_deal_sync.py'` — Notion sync functions
- ✅ `file 'N5/data/deals.db'` — Database with 77 deals + 32 contacts
- ✅ Gmail integration connected

## Goal

Scan Gmail for deal-related emails and extract intelligence:
1. Search for emails involving known deals/contacts
2. Feed through signal router for matching + extraction
3. Log activities to deal_activities table
4. Queue Notion sync for updates

## Gmail Integration

Use the Zo Gmail integration:

```python
# List available Gmail tools
list_app_tools("gmail")

# Search emails
use_app_gmail(
    tool_name="gmail-search",
    configured_props={
        "q": "from:christine@ribbon.co OR to:christine@ribbon.co",
        "maxResults": 50
    }
)

# Get specific email
use_app_gmail(
    tool_name="gmail-get-email",
    configured_props={"messageId": "..."}
)
```

## Deliverables

### 1. Create `N5/scripts/email_deal_scanner.py`

```python
#!/usr/bin/env python3
"""
Email Deal Scanner - Scan Gmail for deal-related signals

Usage:
  python3 email_deal_scanner.py --days 7 --dry-run
  python3 email_deal_scanner.py --query "from:darwinbox" --dry-run
  python3 email_deal_scanner.py --scan-contacts --dry-run
"""

import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/deals.db'
PROCESSED_EMAILS_TABLE = 'processed_emails'  # Track to avoid duplicates

def get_deal_contacts():
    """Get all contacts from deals.db for email matching."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get contacts with email patterns
    c.execute("""
        SELECT id, full_name, company, contact_type, pipeline
        FROM deal_contacts
        WHERE full_name IS NOT NULL
    """)
    contacts = [dict(r) for r in c.fetchall()]
    
    # Get deals with primary contacts
    c.execute("""
        SELECT id, company, primary_contact, pipeline
        FROM deals
        WHERE primary_contact IS NOT NULL
    """)
    deals = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return contacts, deals

def build_search_queries(contacts, deals, days=7):
    """Build Gmail search queries for known contacts."""
    queries = []
    after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
    
    # Search by contact name
    for c in contacts[:20]:  # Limit to avoid quota
        name = c['full_name']
        queries.append({
            'query': f'("{name}") after:{after_date}',
            'contact_id': c['id'],
            'context': c['pipeline']
        })
    
    # Search by company name for hot deals
    for d in deals:
        if d.get('temperature') == 'hot':
            queries.append({
                'query': f'({d["company"]}) after:{after_date}',
                'deal_id': d['id'],
                'context': d['pipeline']
            })
    
    return queries

def is_email_processed(message_id: str) -> bool:
    """Check if email was already processed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT 1 FROM processed_emails WHERE message_id = ?
    """, (message_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_email_processed(message_id: str, deal_id: str = None):
    """Mark email as processed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO processed_emails (message_id, deal_id, processed_at)
        VALUES (?, ?, ?)
    """, (message_id, deal_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def scan_emails(days: int = 7, dry_run: bool = False):
    """Main scanner function."""
    contacts, deals = get_deal_contacts()
    queries = build_search_queries(contacts, deals, days)
    
    results = {
        'scanned': 0,
        'matched': 0,
        'signals': []
    }
    
    # Note: Actual Gmail API calls happen via Zo tools
    # This script prepares the queries and processes results
    
    print(f"Prepared {len(queries)} search queries")
    print(f"Dry run: {dry_run}")
    
    return results
```

### 2. Create processed_emails table

```sql
CREATE TABLE IF NOT EXISTS processed_emails (
    message_id TEXT PRIMARY KEY,
    deal_id TEXT,
    contact_id TEXT,
    processed_at TEXT,
    signal_extracted BOOLEAN DEFAULT FALSE
);
```

### 3. Create scheduled agent

```python
# Daily email scan at 7 AM
create_agent(
    rrule="FREQ=DAILY;BYHOUR=7;BYMINUTE=0",
    instruction="""
    Run daily email deal scanner:
    
    1. Run: python3 N5/scripts/email_deal_scanner.py --days 1
    2. For each new email with deal signals:
       - Feed through DealSignalRouter
       - Log activity to deal_activities
       - Queue Notion sync if significant
    3. Report: "Scanned X emails, Y deal signals found"
    """,
    delivery_method="email"
)
```

### 4. Create `N5/tests/test_email_deal_scanner.py`

Test cases:
- Query building from contacts/deals
- Duplicate detection
- Signal extraction from email content
- Dry-run mode

## Search Patterns

| Pattern | Purpose |
|---------|---------|
| `from:name@domain.com` | Direct from contact |
| `to:name@domain.com` | Direct to contact |
| `"Company Name"` | Mentions company |
| `subject:(deal OR partnership)` | Deal-related subjects |
| `after:2026/01/01` | Date filtering |

## Acceptance Criteria

- [ ] Builds search queries from deals.db contacts
- [ ] Tracks processed emails to avoid duplicates
- [ ] Feeds signals through DealSignalRouter
- [ ] Creates scheduled agent for daily scans
- [ ] Tests pass
