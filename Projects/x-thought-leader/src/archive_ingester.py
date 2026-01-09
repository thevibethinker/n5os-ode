#!/usr/bin/env python3
"""
W10: X Archive Ingester — Import V's tweet history for voice training

Supports:
- Standard X archive (ZIP or extracted folder)
- DuckDB dataset format
"""

import os
import sys
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TWEETS_DB = PROJECT_ROOT / "db" / "tweets.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("archive_ingester")


def parse_twitter_date(date_str: str) -> str:
    """Convert Twitter's date format to ISO."""
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.isoformat()
    except:
        return date_str


def calculate_engagement_score(tweet: dict) -> float:
    """Normalize engagement to 0-1 scale."""
    likes = int(tweet.get('favorite_count', 0))
    retweets = int(tweet.get('retweet_count', 0))
    # Simple weighted score, capped at 1.0
    raw = (likes + retweets * 2) / 100
    return min(raw, 1.0)


def ingest_from_archive_js(archive_path: Path) -> int:
    """Ingest from standard X archive tweets.js file."""
    tweets_file = archive_path / "data" / "tweets.js"
    if not tweets_file.exists():
        # Try alternate location
        tweets_file = archive_path / "tweets.js"
    
    if not tweets_file.exists():
        raise FileNotFoundError(f"tweets.js not found in {archive_path}")
    
    # Read and parse (remove JS wrapper)
    content = tweets_file.read_text()
    # Strip "window.YTD.tweets.part0 = " prefix
    json_start = content.find('[')
    if json_start == -1:
        raise ValueError("Invalid tweets.js format")
    
    tweets_data = json.loads(content[json_start:])
    
    conn = sqlite3.connect(TWEETS_DB)
    inserted = 0
    
    for item in tweets_data:
        tweet = item.get('tweet', item)
        
        # Skip retweets (start with "RT @")
        text = tweet.get('full_text', '')
        if text.startswith('RT @'):
            continue
        
        # Skip very short tweets
        if len(text) < 20:
            continue
        
        try:
            conn.execute("""
                INSERT OR IGNORE INTO voice_samples 
                (id, source, content, created_at, engagement_metrics, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tweet['id'],
                'archive',
                text,
                parse_twitter_date(tweet.get('created_at', '')),
                json.dumps({
                    'likes': tweet.get('favorite_count'),
                    'retweets': tweet.get('retweet_count'),
                    'is_reply': tweet.get('in_reply_to_status_id') is not None
                }),
                json.dumps(['archive'])
            ))
            inserted += 1
        except Exception as e:
            logger.warning(f"Failed to insert tweet {tweet.get('id')}: {e}")
    
    conn.commit()
    conn.close()
    return inserted


def ingest_from_duckdb(duckdb_path: Path) -> int:
    """Ingest from DuckDB dataset format."""
    try:
        import duckdb
    except ImportError:
        logger.error("DuckDB not installed. Run: pip install duckdb")
        return 0
    
    duck = duckdb.connect(str(duckdb_path), read_only=True)
    
    # Discover table structure
    tables = duck.execute("SHOW TABLES").fetchall()
    logger.info(f"Found tables: {[t[0] for t in tables]}")
    
    # Look for tweets table
    tweet_table = None
    for t in tables:
        if 'tweet' in t[0].lower():
            tweet_table = t[0]
            break
    
    if not tweet_table:
        tweet_table = tables[0][0] if tables else None
    
    if not tweet_table:
        raise ValueError("No tweet table found in DuckDB")
    
    # Get schema
    schema = duck.execute(f"DESCRIBE {tweet_table}").fetchall()
    columns = [s[0] for s in schema]
    logger.info(f"Columns: {columns}")
    
    # Map columns (handle various naming conventions)
    id_col = next((c for c in columns if c.lower() in ('id', 'tweet_id', 'status_id')), columns[0])
    text_col = next((c for c in columns if c.lower() in ('text', 'full_text', 'content', 'tweet_text')), None)
    date_col = next((c for c in columns if c.lower() in ('created_at', 'timestamp', 'date')), None)
    
    if not text_col:
        raise ValueError(f"No text column found. Available: {columns}")
    
    # Query tweets
    query = f"SELECT * FROM {tweet_table}"
    rows = duck.execute(query).fetchall()
    
    conn = sqlite3.connect(TWEETS_DB)
    inserted = 0
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        text = row_dict.get(text_col, '')
        
        # Skip retweets and short tweets
        if not text or text.startswith('RT @') or len(text) < 20:
            continue
        
        try:
            conn.execute("""
                INSERT OR IGNORE INTO voice_samples 
                (id, source, content, created_at, engagement_metrics)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(row_dict.get(id_col, hash(text))),
                'archive',
                text,
                str(row_dict.get(date_col, '')) if date_col else None,
                json.dumps(row_dict, default=str)
            ))
            inserted += 1
        except Exception as e:
            logger.warning(f"Failed to insert row: {e}")
    
    conn.commit()
    conn.close()
    duck.close()
    return inserted


def get_voice_sample_stats() -> dict:
    """Get statistics about ingested voice samples."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    stats = {}
    
    # Total count
    stats['total'] = conn.execute("SELECT COUNT(*) FROM voice_samples").fetchone()[0]
    
    # By source
    rows = conn.execute("""
        SELECT source, COUNT(*) as count 
        FROM voice_samples GROUP BY source
    """).fetchall()
    stats['by_source'] = {r['source']: r['count'] for r in rows}
    
    conn.close()
    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ingest X archive for voice training")
    parser.add_argument("path", nargs='?', help="Path to archive (folder, ZIP, or DuckDB)")
    parser.add_argument("--format", choices=['auto', 'archive', 'duckdb'], default='auto')
    parser.add_argument("--stats", action="store_true", help="Show voice sample statistics")
    args = parser.parse_args()
    
    if args.stats:
        stats = get_voice_sample_stats()
        print(json.dumps(stats, indent=2))
        return
    
    if not args.path:
        parser.print_help()
        return
    
    path = Path(args.path)
    if not path.exists():
        logger.error(f"Path not found: {path}")
        sys.exit(1)
    
    # Auto-detect format
    if args.format == 'auto':
        if path.suffix == '.duckdb' or path.suffix == '.db':
            fmt = 'duckdb'
        elif path.is_dir() or path.suffix == '.zip':
            fmt = 'archive'
        else:
            fmt = 'duckdb'  # Guess DuckDB for unknown extensions
    else:
        fmt = args.format
    
    logger.info(f"Ingesting from {path} (format: {fmt})")
    
    if fmt == 'duckdb':
        count = ingest_from_duckdb(path)
    else:
        # Handle ZIP extraction if needed
        if path.suffix == '.zip':
            import zipfile
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(path, 'r') as zf:
                    zf.extractall(tmpdir)
                count = ingest_from_archive_js(Path(tmpdir))
        else:
            count = ingest_from_archive_js(path)
    
    logger.info(f"Ingested {count} tweets for voice training")
    print(json.dumps({"success": True, "tweets_ingested": count}))


if __name__ == "__main__":
    main()


