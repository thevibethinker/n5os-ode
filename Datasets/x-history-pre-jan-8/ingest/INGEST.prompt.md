# X/Twitter Archive Ingestion

## Source Files

- `source/twitter-2026-01-08-*.zip` - Full Twitter/X data export archive
- Extracted to `source/extracted/data/` with the following key files:
  - `tweets.js` - Your tweets (516 items)
  - `like.js` - Tweets you liked (1,960 items)
  - `following.js` - Accounts you follow (1,442 items)
  - `follower.js` - Accounts following you (243 items)
  - `direct-messages.js` - DM conversations (43 conversations, 146 messages)
  - `note-tweet.js` - Long-form tweets (29 items)
  - `block.js` - Blocked accounts (32 items)
  - `mute.js` - Muted accounts (12 items)
  - `deleted-tweets.js` - Deleted tweets (6 items)
  - `account.js` - Account info

## Tables Created

| Table | Description | Row Count |
|-------|-------------|-----------|
| `tweets` | Your tweets/posts on X | 516 |
| `likes` | Tweets you liked | 1,960 |
| `following` | Accounts you follow | 1,442 |
| `followers` | Accounts following you | 243 |
| `direct_messages` | Direct message conversations | 146 |
| `note_tweets` | Long-form tweets (notes) | 29 |
| `blocks` | Accounts you blocked | 32 |
| `mutes` | Accounts you muted | 12 |
| `deleted_tweets` | Tweets you deleted | 6 |
| `account` | Your account information | 1 |

## Transformations

- Twitter's JS format (`window.YTD.xxx.part0 = [...]`) parsed to JSON
- Timestamps converted from string to TIMESTAMP:
  - `tweets.created_at`: `%a %b %d %H:%M:%S %z %Y` format
  - `direct_messages.created_at`: ISO 8601 format
  - `note_tweets.created_at/updated_at`: ISO 8601 format
- HTML stripped from `source` field (e.g., `<a href="...">Twitter for Android</a>` → `Twitter for Android`)
- Mentions, hashtags, and URLs extracted from tweet entities and stored as JSON arrays
- `is_retweet` boolean derived from `full_text.startswith('RT @')`

## Data Excluded (per scope guidelines)

- `ad-engagements.js` (1.9MB) - Ad targeting data
- `ad-impressions.js` (1.5MB) - Ad impressions
- `ip-audit.js` - IP address logs
- `personalization.js` - Personalization/inference data
- `device-token.js` - Device tokens
- Various diagnostic/internal files

## Running

```bash
cd /home/workspace/x-history-pre-jan-8
python ingest/ingest.py
```

## Extending

To add new export files:
1. Place the new Twitter archive zip in `source/`
2. Extract to `source/extracted/`
3. Modify `ingest.py` to handle new data files
4. Re-run the ingestion script

