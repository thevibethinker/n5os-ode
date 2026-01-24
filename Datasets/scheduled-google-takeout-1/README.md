---
created: 2026-01-21
last_edited: 2026-01-21
version: 1
provenance: con_zIzjOx6flwUrvw2a
---
# Google Takeout Dataset

Personal data export from **Attawar.V@gmail.com** (January 2026).

## Data Coverage

| Table | Rows | Description |
|-------|------|-------------|
| `youtube_watch_history` | 110 | YouTube/YouTube Music watch history |
| `youtube_search_history` | 11 | YouTube search queries |
| `youtube_subscriptions` | 19 | YouTube channel subscriptions |
| `reservations` | 55 | Dining reservations via Google |
| `maps_saved_places` | 10 | Starred places in Google Maps |
| `maps_reviews` | 25 | Google Maps reviews written |
| `search_thumbs` | 10 | Movie/show ratings (thumbs up/down) |

**Date Range:** Reservations span 2019–2025; watch history from Aug 2021 – Jan 2026.

## How to Export Your Own Data

1. Go to [Google Takeout](https://takeout.google.com)
2. Click "Deselect all" then select only:
   - YouTube and YouTube Music (includes watch/search history, subscriptions)
   - Maps (your places) (saved places, reviews)
   - Purchases & Reservations
   - Search Contributions (thumbs ratings)
3. Choose format: `.zip`, delivery method: one-time export
4. Download and extract to `source/extracted/`
5. Run: `python ingest/ingest.py`

## Example Queries

### Most-watched channels/artists (YouTube Music)
```sql
SELECT 
    SPLIT_PART(title, ' - ', -1) as artist,
    COUNT(*) as plays
FROM youtube_watch_history
WHERE is_music = true
GROUP BY artist
ORDER BY plays DESC
LIMIT 10;
```

### Favorite restaurants (by reservation frequency)
```sql
SELECT 
    merchant_name,
    COUNT(*) as visits,
    AVG(party_size) as avg_party_size
FROM reservations
WHERE merchant_name IS NOT NULL
GROUP BY merchant_name
ORDER BY visits DESC
LIMIT 10;
```

### Recent YouTube searches
```sql
SELECT query, searched_at
FROM youtube_search_history
ORDER BY searched_at DESC
LIMIT 20;
```

### All 5-star reviews
```sql
SELECT place_name, address, reviewed_at
FROM maps_reviews
WHERE rating = 5
ORDER BY reviewed_at DESC;
```

### Watch activity by day of week
```sql
SELECT 
    DAYNAME(watched_at) as day,
    COUNT(*) as videos
FROM youtube_watch_history
WHERE watched_at IS NOT NULL
GROUP BY DAYOFWEEK(watched_at), day
ORDER BY DAYOFWEEK(watched_at);
```

### Subscribed channels
```sql
SELECT channel_name, channel_url
FROM youtube_subscriptions
ORDER BY channel_name;
```

## Notes

- **Watch history** may be incomplete if history was paused or deleted in YouTube settings
- **Reservations** are captured from Gmail/Google Assistant; not all bookings may be included
- Timestamps are in local time (EST) as exported by Google
- Some older reservations have `start_time = NULL` (metadata was lost)
