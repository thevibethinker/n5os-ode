#!/usr/bin/env python3
"""
Where's V - Trip Ingestion Script

This script:
1. Queries Gmail for flight/hotel confirmations (query-based, not label-dependent)
2. Queries Google Calendar for travel events
3. Sends to LLM for extraction (no regex - LLM handles all parsing)
4. Deduplicates against existing trips
5. Updates the trip store

Usage:
  python3 ingest_trips.py --dry-run    # Show what would be extracted, don't save
  python3 ingest_trips.py              # Run full ingestion
  python3 ingest_trips.py --manual     # Output instructions for manual Zo run
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"

# Gmail queries for travel confirmations
GMAIL_QUERIES = {
    "flights": "(from:jetblue.com OR from:united.com OR from:delta.com OR from:aa.com OR from:southwest.com) subject:(confirmation OR itinerary OR receipt OR e-ticket) newer_than:90d",
    "trains": "from:amtrak.com subject:(confirmation OR reservation OR itinerary) newer_than:90d",
    "hotels": "(from:marriott.com OR from:hilton.com OR from:hyatt.com OR from:ihg.com OR from:airbnb.com) subject:(confirmation OR reservation) newer_than:90d"
}

LLM_EXTRACTION_PROMPT = """You are extracting V (Vrijen Attawar)'s travel schedule for the Where's V dashboard.

TODAY: {today}
V lives in NYC (home airports: JFK, LGA, EWR)

**CRITICAL RULES:**
1. ONLY extract trips for V (Vrijen Attawar) - exclude family members like "Sandeep"
2. Multi-segment trips are ONE trip (e.g., NYC→Denver→Houston is one trip with 2 flight segments)
3. Include return flights to form complete round-trips when possible
4. Include train segments (Amtrak) - they have segment_type: "train"
5. Include hotel details when found

**RAW FLIGHT/TRAIN EMAIL DATA:**
{email_data}

**RAW HOTEL EMAIL DATA:**
{hotel_data}

**CALENDAR EVENTS:**
{calendar_data}

**OUTPUT FORMAT - JSON with all V's upcoming trips:**
{{
  "trips": [
    {{
      "id": "trip_YYYYMMDD_destination",
      "summary": "Destination description",
      "notes": "Purpose if known",
      "departure_date": "YYYY-MM-DD",
      "return_date": "YYYY-MM-DD or null if one-way",
      "segments": [
        {{
          "sequence": 1,
          "type": "flight",
          "carrier": "JetBlue",
          "number": "B6 1234",
          "from_airport": "JFK",
          "to_airport": "BOS",
          "from_city": "New York",
          "to_city": "Boston",
          "departure": "2026-01-22T08:00:00-05:00",
          "arrival": "2026-01-22T09:15:00-05:00",
          "confirmation": "ABC123"
        }},
        {{
          "sequence": 2,
          "type": "train",
          "carrier": "Amtrak",
          "number": "Acela 2151",
          "from_city": "Boston",
          "to_city": "New York",
          "departure": "2026-01-24T14:00:00-05:00",
          "arrival": "2026-01-24T17:30:00-05:00"
        }}
      ],
      "hotels": [
        {{
          "name": "Hotel Name",
          "city": "Boston",
          "check_in": "2026-01-22",
          "check_out": "2026-01-24",
          "confirmation": "12345",
          "phone": "+1-617-555-0000"
        }}
      ]
    }}
  ],
  "excluded": [
    {{"traveler": "Sandeep", "summary": "United Dec 15", "reason": "Not V's trip"}}
  ]
}}

Return ONLY valid JSON, no markdown fencing."""


def get_existing_confirmations() -> set:
    """Get all existing confirmation codes from the trip store."""
    legs_file = DATA_DIR / "legs_v2.jsonl"
    confirmations = set()
    if legs_file.exists():
        with open(legs_file) as f:
            for line in f:
                if line.strip():
                    leg = json.loads(line)
                    if leg.get("confirmation"):
                        confirmations.add(leg["confirmation"])
    return confirmations


def generate_manual_instructions():
    """Output instructions for running ingestion in a Zo conversation."""
    print("""
=== WHERE'S V MANUAL INGESTION ===

Run these commands in a Zo conversation:

1. FETCH FLIGHT EMAILS:
   use_app_gmail(
       tool_name="gmail-find-email",
       configured_props={{
           "q": "{flights}",
           "maxResults": 20,
           "withTextPayload": true
       }},
       email="attawar.v@gmail.com"
   )

2. FETCH HOTEL EMAILS:
   use_app_gmail(
       tool_name="gmail-find-email",
       configured_props={{
           "q": "{hotels}",
           "maxResults": 10,
           "withTextPayload": true
       }},
       email="attawar.v@gmail.com"
   )

3. FETCH CALENDAR:
   use_app_google_calendar(
       tool_name="google_calendar-list-events",
       configured_props={{
           "calendarId": "primary",
           "timeMin": "<today>T00:00:00Z",
           "timeMax": "<60_days_from_now>T00:00:00Z",
           "maxResults": 50,
           "singleEvents": true,
           "orderBy": "startTime"
       }},
       email="attawar.v@gmail.com"
   )

4. Send all data to LLM with the extraction prompt in this file.

5. Update trips_v2.jsonl and legs_v2.jsonl with extracted trips.
""".format(**GMAIL_QUERIES))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Where's V trip ingestion")
    parser.add_argument("--dry-run", action="store_true", help="Show extraction prompt without saving")
    parser.add_argument("--manual", action="store_true", help="Output manual instructions")
    parser.add_argument("--status", action="store_true", help="Show current trip status")
    args = parser.parse_args()
    
    if args.manual:
        generate_manual_instructions()
        return
    
    if args.status:
        # Import and show current state
        from trip_store_v2 import get_current_state
        state = get_current_state()
        print(json.dumps(state, indent=2, default=str))
        return
    
    # For actual ingestion, we need to be run from a Zo conversation
    # that can call the Gmail and Calendar APIs
    print("""
Where's V Trip Ingestion
========================

This script requires Gmail and Calendar API access.
It must be run from within a Zo conversation.

Options:
  --manual    Show manual ingestion instructions
  --status    Show current trip status
  --dry-run   Preview extraction without saving

For automated ingestion, use the scheduled agent or run manually in Zo.
""")
    
    existing = get_existing_confirmations()
    print(f"\nExisting confirmations in store: {len(existing)}")
    for conf in sorted(existing):
        print(f"  - {conf}")


if __name__ == "__main__":
    main()
