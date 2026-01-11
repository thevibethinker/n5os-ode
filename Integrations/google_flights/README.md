---
created: 2026-01-11
last_edited: 2026-01-11
version: 2.0
provenance: con_5vDZAeY5mhvQxV6D
---

# Google Flights Integration

Natural language flight search with V's baseline preferences. Uses SerpApi to query Google Flights data.

## Setup

**Required:** `SERPAPI_PRIVATE_KEY` environment variable (set in [Settings > Developers](/?t=settings&s=developers))

## Commands

### `report` - Route Report (Primary)
```bash
# Round-trip (default)
python3 google_flights.py report --to LAX --date 2026-02-15 --return-date 2026-02-20

# One-way
python3 google_flights.py report --to MIA --date 2026-02-01 --one-way

# With booking links (slower - fetches direct airline URLs)
python3 google_flights.py report --to RDU --date 2026-01-22 --return-date 2026-01-24 --booking-link

# Specific origin (overrides baseline)
python3 google_flights.py report --from EWR --to LAX --date 2026-02-15 --return-date 2026-02-20

# Time preference filter
python3 google_flights.py report --to LAX --date 2026-02-15 --return-date 2026-02-20 --time midday
```

### `search` - JSON Output
```bash
python3 google_flights.py search --to LAX --date 2026-02-15 --return-date 2026-02-20 --json
```

### `baseline` - Show Preferences
```bash
python3 google_flights.py baseline
```

### Multi-City
```bash
python3 google_flights.py report --multi-city '[
  {"from":"JFK","to":"LAX","date":"2026-01-22"},
  {"from":"LAX","to":"DEN","date":"2026-01-25"},
  {"from":"DEN","to":"JFK","date":"2026-01-28"}
]'
```

## Baseline Preferences

Loaded from `Knowledge/reference/travel_baseline.yaml`:

| Setting | Value |
|---------|-------|
| Home Airports | LGA (primary) → JFK (if JetBlue) → EWR (backup) |
| Primary Airline | JetBlue (+50 score) |
| Secondary Airline | Delta (+10 score) |
| Excluded Airlines | Spirit, Frontier |
| Cabin | Economy (main cabin, not basic) |
| Stops | Nonstop only |

## Scoring System

Flights are ranked by composite score:

- **+50** JetBlue (primary airline)
- **+10** Delta (secondary airline)
- **+30** JFK origin (when JetBlue)
- **+20** LGA origin (primary home airport)
- **+10** EWR origin (backup)
- **+40** Time preference match (morning/midday/evening/redeye)
- **-10 per $50** Price penalty (normalized)

## Booking Links

When `--booking-link` is passed, the integration:
1. Fetches Google's redirect URL for each flight
2. Follows the redirect to extract the direct airline booking URL
3. Returns clickable links to airline booking pages (e.g., JetBlue's trip-summary)

**Note:** These are the same URLs Google Flights generates when you click "Book". They're affiliate links that work in any browser.

## Limitations

- Multi-city searches don't include booking links (Google Flights limitation)
- Booking link fetching adds ~5-10 seconds per flight (rate limited)
- Price insights are estimates based on Google's data
- API calls are limited by SerpApi quota

## Files

- `google_flights.py` - Main CLI tool
- `Knowledge/reference/travel_baseline.yaml` - Preference config
- `Prompts/Flight Search.prompt.md` - Natural language interface

