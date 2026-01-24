---
created: 2026-01-21
last_edited: 2026-01-21
version: 1.0
provenance: con_zIzjOx6flwUrvw2a
---

# Google Takeout Ingestion

## Source Data

Three zip files from Google Takeout (Jan 2026):
- `takeout-20260121T034159Z-001.zip` — Main archive (YouTube history, Maps, Reservations)
- `takeout-20260121T034159Z-5-001.zip` — YouTube subscriptions
- `takeout-20260121T034159Z-6-001.zip` — Timeline, Wallet, Search Contributions

## Data Extracted

| Source Path | Format | Target Table |
|-------------|--------|--------------|
| `YouTube and YouTube Music/history/watch-history.html` | HTML | `youtube_watch_history` |
| `YouTube and YouTube Music/history/search-history.html` | HTML | `youtube_search_history` |
| `YouTube and YouTube Music/subscriptions/subscriptions.csv` | CSV | `youtube_subscriptions` |
| `Purchases & Reservations/Reservations/*.json` | JSON (per-reservation) | `reservations` |
| `Maps (your places)/Saved Places.json` | GeoJSON | `maps_saved_places` |
| `Maps (your places)/Reviews.json` | GeoJSON | `maps_reviews` |
| `Search Contributions/Thumbs.json` | JSON array | `search_thumbs` |

## Parsing Notes

### YouTube Watch/Search History (HTML)
Google exports history as HTML with special Unicode characters:
- `\xa0` (non-breaking space) after "Watched" / "Searched for"
- `\u202f` (narrow no-break space) before AM/PM in timestamps

Pattern for watch entries:
```
Watched\xa0<a href="URL">TITLE</a><br>
<a href="CHANNEL_URL">CHANNEL</a><br>
TIMESTAMP<br>
```

### Reservations (JSON)
Each reservation is a separate `action_*.json` file with structure:
```json
{
  "uniqueId": "...",
  "booking": {
    "name": "Dining Reservation",
    "merchantName": "Restaurant Name",
    "address": "...",
    "partySize": 2,
    "startTime": "2025-01-15T19:30:00-05:00"
  },
  "lastModifiedTime": "..."
}
```

### Maps Data (GeoJSON)
Standard GeoJSON with location info in `properties.location`.

## Data Not Ingested

Skipped as low-value for personal analytics:
- `Timeline/Settings.json` — device settings
- `Maps/Commute routes/` — route preferences
- `Google Wallet/` — boarding passes (PDF)
- `Discover/` — content preferences

## Re-running Ingestion

```bash
cd /home/workspace/Datasets/scheduled-google-takeout-1
# Fresh export? Extract first:
# unzip source/*.zip -d source/extracted/
python ingest/ingest.py
python generate_schema.py
```
