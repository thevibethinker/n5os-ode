---
title: Flight Search
description: Natural language flight search using V's baseline preferences
tags: [travel, flights, search, utility]
tool: true
created: 2025-12-21
last_edited: 2025-12-21
version: 1.0
provenance: con_q7r0aONFiaolYKUe
---

# Flight Search

Search for flights using natural language. The system automatically applies V's baseline preferences (JetBlue priority, JFK override, no Spirit/Frontier, nonstop only, no basic economy).

## Usage

**Natural language examples:**
- "Find me flights to LA next month"
- "Search LAX February 15"
- "Flights to Denver, leaving Jan 10, returning Jan 15"
- "One-way to Miami on March 1"

**Direct command:**
```bash
python3 /home/workspace/Integrations/google_flights.py report --to <AIRPORT_CODE> --date <YYYY-MM-DD> [--return-date <YYYY-MM-DD>]
```

## Workflow

When V requests a flight search:

1. **Parse the intent:**
   - Destination (required): Extract airport code or city name → convert to IATA code
   - Outbound date (required): Parse natural language dates ("next Friday", "February 15", "in 2 weeks")
   - Return date (optional): If mentioned, include for round-trip search
   
2. **Execute the search:**
   ```bash
   python3 /home/workspace/Integrations/google_flights.py report --to <CODE> --date <YYYY-MM-DD> [--return-date <YYYY-MM-DD>]
   ```

3. **Present the Route Report:**
   - Price insights (current level vs typical)
   - Top 10 ranked options with scores
   - Clear recommendation with reasoning

4. **Offer follow-up actions:**
   - "Want me to set up price monitoring for this route?"
   - "Should I add any preferences to your baseline?" (e.g., "no 6 AM flights")

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

## Future Capabilities (Not Yet Implemented)

- **Price Monitoring Agent:** Scheduled task to watch a route and alert on price drops
- **Historical Analysis:** Compare current prices to historical patterns
- **Route Dossiers:** Deep analysis with booking recommendations

