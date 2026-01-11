---
title: Flight Search
description: "Natural language flight search using V's baseline preferences"
tags:
  - travel
  - flights
  - search
  - utility
tool: true
created: 2025-12-21
last_edited: 2026-01-11
version: 2.1
provenance: con_an9JiKXgrCY551K6
---
# Flight Search

Search for flights using natural language. The system automatically applies V's baseline preferences (JetBlue priority, JFK override, no Spirit/Frontier, nonstop only, no basic economy).

## Usage

**Natural language examples:**
- "Find me flights to LA, leaving Feb 15, returning Feb 20" → Round-trip (default)
- "One-way to Miami on March 1" → One-way (explicit)
- "Multi-city: NYC to LA on Jan 22, LA to Denver on Jan 25, Denver back to NYC on Jan 28"

**Direct commands:**

```bash
# Round-trip (DEFAULT) - requires return date
python3 /home/workspace/Integrations/google_flights/google_flights.py report \
  --to <CODE> --date <YYYY-MM-DD> --return-date <YYYY-MM-DD>

# With direct booking links (adds ~10s for API calls)
python3 /home/workspace/Integrations/google_flights/google_flights.py report \
  --to <CODE> --date <YYYY-MM-DD> --return-date <YYYY-MM-DD> --booking-link

# One-way (explicit)
python3 /home/workspace/Integrations/google_flights/google_flights.py report \
  --to <CODE> --date <YYYY-MM-DD> --one-way

# Multi-city
python3 /home/workspace/Integrations/google_flights/google_flights.py report \
  --multi-city '[{"from":"JFK","to":"LAX","date":"2026-01-22"},{"from":"LAX","to":"DEN","date":"2026-01-25"},{"from":"DEN","to":"JFK","date":"2026-01-28"}]'
```

## Workflow

When V requests a flight search:

1. **Parse the intent:**
   - Destination (required): Extract airport code or city name → convert to IATA code
   - Outbound date (required): Parse natural language dates ("next Friday", "February 15", "in 2 weeks")
   - Return date: **Required for round-trip** (default). If not mentioned, ask for it.
   - Trip type: Assume round-trip unless "one-way" is explicitly stated
   
2. **Execute the search:**
   - **Round-trip (default):** Must include `--return-date`
   - **One-way:** Must include `--one-way` flag
   - **Multi-city:** Use `--multi-city` with JSON array
   - **Add `--booking-link`** when V wants to book immediately (generates clickable airline URLs)

3. **Present the Route Report:**
   - All prices show **(RT)** or **(OW)** suffix for clarity
   - Price insights (current level vs typical)
   - Top 10 ranked options with scores
   - Direct booking links when `--booking-link` is used
   - Clear recommendation with reasoning

4. **Offer follow-up actions:**
   - "Want me to set up price monitoring for this route?"
   - "Should I add any preferences to your baseline?" (e.g., "no 6 AM flights")

## Key Behavior Changes (v2.0)

| Before | After |
|--------|-------|
| Missing return date → one-way search | Missing return date → **error** (must use `--one-way` or provide return date) |
| Prices had no label | Prices always show **(RT)** or **(OW)** suffix |
| No booking links | `--booking-link` generates direct airline URLs |
| No multi-city | `--multi-city` supports complex itineraries |

## Common Airport Codes

| City | Code |
|------|------|
| Los Angeles | LAX |
| San Francisco | SFO |
| Chicago | ORD |
| Miami | MIA |
| Denver | DEN |
| Boston | BOS |
| Seattle | SEA |
| Las Vegas | LAS |
| Atlanta | ATL |
| Dallas | DFW |
| Raleigh | RDU |
| London | LHR |
| Paris | CDG |

## Baseline Reference

V's preferences are stored in `file 'Knowledge/reference/travel_baseline.yaml'`

Current settings:
- **Home airports:** LGA (primary) → JFK (if JetBlue) → EWR (backup)
- **Airlines:** JetBlue (primary), Delta (secondary)
- **Excluded:** Spirit, Frontier
- **Cabin:** Economy (main cabin, not basic)
- **Stops:** Nonstop only

## Future Capabilities

- **Price Monitoring Agent:** Scheduled task to watch a route and alert on price drops
- **Historical Analysis:** Compare current prices to historical patterns
- **Route Dossiers:** Deep analysis with booking recommendations


