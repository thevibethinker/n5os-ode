# X/Twitter History (Pre-Jan 8, 2026)

This dataset contains V's X/Twitter archive exported before January 8, 2026. It includes tweets, likes, follows, DMs, and account metadata for @thevibethinker.

## How to Get Your Data

1. Go to [x.com/settings/your_twitter_data](https://x.com/settings/your_twitter_data)
2. Log in to your account
3. Click "Download an archive of your data"
4. Verify your identity (password or 2FA)
5. Click "Request archive"
6. Wait for X to prepare your archive (usually 24-48 hours)
7. You'll receive an email when ready — download the zip file
8. Extract to `source/extracted/` and run `python ingest/ingest.py`

**Note**: X archives can be large (this one is ~64MB). The archive contains a lot of ad/diagnostic data that we skip during ingestion.

## Coverage

- **Period**: May 2022 - January 2026
- **Account**: @thevibethinker (V Attawar)
- **Source**: X Data Export (GDPR-style archive)

## What's Included

### Tweets (516)
Your posts on X, including replies and quote tweets. Each record includes engagement metrics (likes, retweets), mentions, hashtags, URLs, and the client used to post.

### Likes (1,960)
Tweets you've liked, with the full text of each liked tweet.

### Following (1,442)
Accounts you follow. Note: Only account IDs are included (not usernames), so you'd need to resolve these via the X API to get handles.

### Followers (243)
Accounts following you. Same caveat about IDs vs. usernames.

### Direct Messages (146)
Your DM conversations. Messages are grouped by conversation thread.

### Note Tweets (29)
Long-form tweets (X's "notes" feature).

### Blocks & Mutes
Accounts you've blocked (32) or muted (12).

### Deleted Tweets (6)
Tweets you've deleted that X still had records of.

## Business Rules & Semantics

- **`is_retweet`**: Derived from whether `full_text` starts with "RT @". True retweets don't have a separate flag in the export.
- **`mentions`/`hashtags`/`urls`**: Stored as JSON arrays. Use `json_extract` or cast to parse.
- **`source`**: The client used to post (e.g., "Twitter for Android", "Twitter Web App"). HTML tags stripped.
- **`in_reply_to_*`**: Set when the tweet is a reply. NULL for original tweets.
- **Following/Followers**: Only have account IDs, not usernames. The `user_link` field provides a URL that can be used to look up the account.

## Example Queries

### How many tweets have I posted?
```sql
SELECT COUNT(*) AS total_tweets FROM tweets;
```

### What are my most liked tweets?
```sql
SELECT 
  created_at,
  full_text,
  favorite_count,
  retweet_count
FROM tweets
ORDER BY favorite_count DESC
LIMIT 10;
```

### How has my tweeting activity changed over time?
```sql
SELECT 
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS tweets
FROM tweets
GROUP BY month
ORDER BY month;
```

### What percentage of my tweets are replies?
```sql
SELECT 
  ROUND(100.0 * SUM(CASE WHEN in_reply_to_status_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS reply_pct,
  ROUND(100.0 * SUM(CASE WHEN is_retweet THEN 1 ELSE 0 END) / COUNT(*), 1) AS retweet_pct,
  ROUND(100.0 * SUM(CASE WHEN in_reply_to_status_id IS NULL AND NOT is_retweet THEN 1 ELSE 0 END) / COUNT(*), 1) AS original_pct
FROM tweets;
```

### What topics do I like most? (by word frequency in liked tweets)
```sql
SELECT 
  word,
  COUNT(*) AS frequency
FROM (
  SELECT UNNEST(STRING_SPLIT(LOWER(full_text), ' ')) AS word
  FROM likes
)
WHERE LENGTH(word) > 4
GROUP BY word
ORDER BY frequency DESC
LIMIT 20;
```

### When do I tweet most?
```sql
SELECT 
  EXTRACT(HOUR FROM created_at) AS hour_of_day,
  COUNT(*) AS tweets
FROM tweets
GROUP BY hour_of_day
ORDER BY hour_of_day;
```

## Notes

- This archive predates January 8, 2026 — tweets after that date are not included.
- Account IDs in following/followers tables need X API lookups to get usernames.
- Some deleted tweets may have been captured before deletion.

