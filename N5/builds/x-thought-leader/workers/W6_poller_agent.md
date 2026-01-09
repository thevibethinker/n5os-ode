---
created: 2026-01-09
worker_id: W6
component: Polling Agent
status: pending
depends_on: [W1, W2]
---

# W6: Polling Agent

## Objective
Create a scheduled agent that polls monitored X accounts for new tweets and triggers the processing pipeline.

## Output Files
- `Projects/x-thought-leader/agents/poller.py` — The polling script
- Agent registration via `create_agent` tool

## Dependencies
- W1 (Database) — needs tweets.db to exist
- W2 (X API) — uses XAPIClient for fetching

## Core Logic

```python
def poll_monitored_accounts(db_path: str) -> dict:
    """
    Main polling function.
    
    1. Get list of monitored accounts from DB
    2. For each account:
       a. Get last_tweet_id (high watermark)
       b. Fetch new tweets since that ID
       c. Store new tweets in DB
       d. Update last_tweet_id
    3. Return summary stats
    """
    
def poll_single_account(
    client: XAPIClient,
    db: sqlite3.Connection,
    account: dict
) -> int:
    """
    Poll one account for new tweets.
    Returns count of new tweets found.
    """
```

## Polling Strategy

### Rate Limit Aware
- Basic tier: 100 requests/24h per user endpoint
- With 1 account (Anand): Can poll ~4x per hour safely
- Polling interval: **Every 15 minutes** during active hours

### High Watermark Pattern
```sql
-- Get last seen tweet ID for account
SELECT last_tweet_id FROM monitored_accounts WHERE user_id = ?

-- After fetching, update
UPDATE monitored_accounts SET last_tweet_id = ?, last_polled = ? WHERE user_id = ?
```

### Active Hours Only
- Poll between 8 AM - 10 PM ET (approval window)
- No point polling when V can't approve

## Agent Schedule

```python
# Register via create_agent
rrule = "FREQ=MINUTELY;INTERVAL=15;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20,21;BYMINUTE=0,15,30,45"

instruction = """
Run the X Thought Leadership polling agent:

1. Execute: python3 /home/workspace/Projects/x-thought-leader/agents/poller.py
2. The script will:
   - Poll all monitored accounts for new tweets
   - Store new tweets in tweets.db
   - Trigger position matching for new tweets
   - If high-correlation matches found, generate drafts
   - If drafts ready for approval, trigger SMS notification

Report: New tweets found, matches generated, drafts pending approval.
"""
```

## Script Structure

```python
#!/usr/bin/env python3
"""
X Thought Leadership Engine - Polling Agent
Runs every 15 minutes during active hours (8 AM - 10 PM ET)
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from x_api import XAPIClient
from position_matcher import match_tweet_to_positions
from draft_generator import generate_drafts, store_drafts

DB_PATH = Path(__file__).parent.parent / "db" / "tweets.db"
MIN_CORRELATION_SCORE = 0.5

def main():
    et = pytz.timezone("America/New_York")
    now = datetime.now(et)
    
    # Skip if outside active hours
    if not (8 <= now.hour < 22):
        print(f"Outside active hours ({now.hour}:00 ET). Skipping.")
        return
    
    client = XAPIClient()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        stats = poll_all_accounts(client, conn)
        print(f"Polling complete: {stats}")
        
        if stats["new_tweets"] > 0:
            match_stats = process_new_tweets(conn)
            print(f"Matching complete: {match_stats}")
            
            if match_stats["high_correlation"] > 0:
                draft_stats = generate_pending_drafts(conn)
                print(f"Draft generation: {draft_stats}")
                
                if draft_stats["new_drafts"] > 0:
                    notify_for_approval(conn)
                    
    finally:
        conn.close()

def poll_all_accounts(client, conn) -> dict:
    """Poll all monitored accounts."""
    accounts = conn.execute(
        "SELECT * FROM monitored_accounts WHERE active = 1"
    ).fetchall()
    
    total_new = 0
    for account in accounts:
        new_count = poll_single_account(client, conn, dict(account))
        total_new += new_count
        
    return {"accounts_polled": len(accounts), "new_tweets": total_new}

def poll_single_account(client, conn, account: dict) -> int:
    """Poll one account, store new tweets."""
    tweets = client.get_user_tweets(
        account["user_id"],
        since_id=account["last_tweet_id"],
        max_results=20
    )
    
    if not tweets:
        return 0
    
    for tweet in tweets:
        conn.execute("""
            INSERT OR IGNORE INTO tweets 
            (tweet_id, user_id, author_username, text, created_at, fetched_at, processed)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (
            tweet["id"],
            account["user_id"],
            account["username"],
            tweet["text"],
            tweet["created_at"],
            datetime.utcnow().isoformat()
        ))
    
    # Update high watermark
    latest_id = max(t["id"] for t in tweets)
    conn.execute("""
        UPDATE monitored_accounts 
        SET last_tweet_id = ?, last_polled = ?
        WHERE user_id = ?
    """, (latest_id, datetime.utcnow().isoformat(), account["user_id"]))
    
    conn.commit()
    return len(tweets)

if __name__ == "__main__":
    main()
```

## Error Handling

- Rate limit hit → Log, skip account, continue with others
- API error → Log, retry once, then skip
- DB error → Log and exit (critical)

## Monitoring

Log output should include:
- Timestamp (ET)
- Accounts polled
- New tweets per account
- High-correlation matches found
- Drafts generated
- Any errors

## Acceptance Criteria
- [ ] Polls all active monitored accounts
- [ ] Respects rate limits
- [ ] Uses high watermark to avoid duplicates
- [ ] Stores new tweets correctly
- [ ] Triggers downstream processing (matching, drafts)
- [ ] Runs only during active hours
- [ ] Agent registered with correct schedule

