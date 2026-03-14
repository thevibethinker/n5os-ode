---
created: 2026-01-09
worker_id: W10
component: X Archive Ingester
status: pending
depends_on: [W1]
---

# W10: X Archive Ingester

## Objective
Parse V's X data archive to extract historical tweets for voice training.

## Output Files
- `Projects/x-thought-leader/src/archive_ingester.py`

## Input
V has requested their X archive. When it arrives:
- Downloaded as ZIP file
- Contains `data/tweets.js` with all tweets
- Will likely be placed in `Datasets/` as DuckDB or raw

## X Archive Structure

```
twitter-archive.zip/
├── data/
│   ├── tweets.js          # Main tweet data
│   ├── like.js            # Liked tweets
│   ├── following.js       # Who V follows
│   └── ...
└── Your archive.html
```

### tweets.js Format
```javascript
window.YTD.tweets.part0 = [
  {
    "tweet": {
      "id": "1234567890",
      "full_text": "The tweet content here...",
      "created_at": "Wed Oct 10 20:19:24 +0000 2018",
      "retweet_count": "5",
      "favorite_count": "23",
      "in_reply_to_status_id": "1234567889",  // if reply
      "in_reply_to_user_id": "987654321",
      "entities": {
        "hashtags": [...],
        "user_mentions": [...],
        "urls": [...]
      }
    }
  },
  ...
]
```

## Core Functions

```python
def parse_archive(archive_path: str) -> list[dict]:
    """
    Parse X archive ZIP or extracted folder.
    Returns list of tweet objects.
    """

def filter_original_tweets(tweets: list[dict]) -> list[dict]:
    """
    Filter to only V's original tweets (not RTs, not pure replies).
    These are best for voice training.
    """

def store_historical_tweets(db_path: str, tweets: list[dict]) -> int:
    """
    Store in tweets.db historical_tweets table.
    Returns count stored.
    """
```

## Historical Tweets Table

```sql
CREATE TABLE historical_tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT,
    is_reply INTEGER DEFAULT 0,
    reply_to_tweet_id TEXT,
    retweet_count INTEGER,
    favorite_count INTEGER,
    -- Voice training fields
    analyzed INTEGER DEFAULT 0,
    voice_features TEXT  -- JSON: extracted style features
);
```

## DuckDB Alternative

If V stores archive as DuckDB in Datasets/:
```python
def load_from_duckdb(db_path: str) -> list[dict]:
    """Load tweets from DuckDB dataset."""
    import duckdb
    conn = duckdb.connect(db_path)
    return conn.execute("SELECT * FROM tweets").fetchall()
```

## Acceptance Criteria
- [ ] Parses ZIP or extracted archive
- [ ] Handles tweets.js JavaScript format
- [ ] Filters to original tweets
- [ ] Stores in database
- [ ] Works with DuckDB if that's the format V uses
