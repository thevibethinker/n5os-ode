#!/usr/bin/env python3
"""
Trip Extraction Orchestrator for Where's V

Coordinates Calendar + Gmail ingestion and uses LLM (via Zo API) 
to extract structured Trip/Leg data.

This is the main ingestion script that should be run to populate trip data.
"""
import json
import os
import sys
import asyncio
import aiohttp
from datetime import datetime, timezone
from pathlib import Path

# Import local modules
sys.path.insert(0, str(Path(__file__).parent))
from trip_store_v2 import (
    create_trip, create_leg, load_trips, load_legs,
    HOME_AIRPORTS, get_current_state
)
from ingest_calendar import fetch_calendar_events, filter_travel_events, format_for_extraction
from ingest_gmail import build_gmail_query, format_emails_for_extraction

ZO_API_URL = "https://api.zo.computer/zo/ask"

# LLM extraction prompt
EXTRACTION_PROMPT = """You are extracting travel data for "Where's V", a travel tracker for V (Vrijen).

**CRITICAL FILTERING RULES:**
- V lives in NYC. His home airports are: JFK, LGA, EWR
- ONLY extract trips that ORIGINATE from NYC (JFK/LGA/EWR)
- Trips starting from other cities (Houston, Chicago, etc.) are NOT V's trips
- These non-NYC trips are likely family/friends whose travel appears on V's shared calendar
- When in doubt, EXCLUDE the trip

**INCLUDE (V's trips):**
- JFK → MIA → JFK (NYC round trip ✓)
- LGA → SFO → EWR (NYC to NYC, different airports ✓)
- JFK → MIA → LAX → JFK (Multi-city starting/ending NYC ✓)

**EXCLUDE (not V's trips):**
- IAH → DEN → IAH (Houston round trip - NOT V)
- ORD → LAX → ORD (Chicago round trip - NOT V)
- MIA → NYC (One-way TO NYC - probably someone visiting V)

**Trip/Leg Structure:**
A Trip is a complete journey from NYC and back to NYC.
A Leg is a single flight segment within a trip.

Example:
- Trip: NYC → Puerto Rico → NYC
  - Leg 1: JFK → SJU (Feb 20, outbound)
  - Leg 2: SJU → JFK (Feb 27, return)

**Extract from the following data:**

CALENDAR EVENTS:
{calendar_data}

GMAIL FLIGHT CONFIRMATIONS:
{email_data}

**Output JSON:**
{{
  "trips": [
    {{
      "legs": [
        {{
          "sequence": 1,
          "flight_number": "B6 1803",
          "departure_airport": "JFK",
          "arrival_airport": "SJU", 
          "departure_time": "2026-02-20T13:00:00Z",
          "arrival_time": "2026-02-20T16:58:00Z",
          "destination_city": "San Juan"
        }},
        ...
      ],
      "hotel": null or {{ "name": "...", "address": "...", "check_in": "...", "check_out": "..." }}
    }}
  ],
  "excluded": [
    {{
      "reason": "Trip originates from Houston (IAH), not NYC - likely family travel",
      "summary": "IAH → DEN → IAH, Feb 7-10"
    }}
  ]
}}

Return ONLY valid JSON, no markdown fencing or explanation."""


async def call_zo_api(prompt: str) -> str:
    """Call Zo API for LLM extraction."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Zo API error {resp.status}: {error_text}")
            result = await resp.json()
            return result.get("output", "")


def parse_llm_response(response: str) -> dict:
    """Parse LLM response to extract JSON."""
    # Try to find JSON in the response
    response = response.strip()
    
    # If response starts with ```, extract content between them
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        if end > start:
            response = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end > start:
            response = response[start:end].strip()
    
    # Find JSON object boundaries
    start = response.find("{")
    end = response.rfind("}") + 1
    
    if start >= 0 and end > start:
        json_str = response[start:end]
        return json.loads(json_str)
    
    raise ValueError(f"Could not parse JSON from response: {response[:200]}...")


async def extract_from_calendar_and_gmail(
    calendar_events: list[dict],
    flight_emails: list[dict],
    hotel_emails: list[dict],
    dry_run: bool = False
) -> dict:
    """
    Extract trips from calendar and email data using LLM.
    
    Args:
        calendar_events: List of calendar event dicts
        flight_emails: List of flight confirmation email dicts
        hotel_emails: List of hotel confirmation email dicts
        dry_run: If True, just print what would be done
        
    Returns:
        Dict with extracted trips
    """
    # Format data for LLM
    calendar_text = format_for_extraction(filter_travel_events(calendar_events))
    
    all_emails = flight_emails + hotel_emails
    email_text = format_emails_for_extraction(all_emails)
    
    prompt = EXTRACTION_PROMPT.format(
        calendar_data=calendar_text,
        email_data=email_text
    )
    
    if dry_run:
        print("=" * 60)
        print("DRY RUN - Would send this prompt to Zo API:")
        print("=" * 60)
        print(prompt[:2000])
        if len(prompt) > 2000:
            print(f"\n... ({len(prompt) - 2000} more characters)")
        print("=" * 60)
        return {"trips": []}
    
    # Call LLM
    print("Calling Zo API for extraction...")
    response = await call_zo_api(prompt)
    
    # Parse response
    print("Parsing LLM response...")
    extracted = parse_llm_response(response)
    
    return extracted


def save_extracted_trips(extracted: dict) -> dict:
    """
    Save extracted trips to the trip store.
    
    Args:
        extracted: Dict with 'trips' key containing list of trip data
        
    Returns:
        Summary of what was saved
    """
    saved = {"trips": 0, "legs": 0, "skipped": 0}
    
    for trip_data in extracted.get("trips", []):
        legs = trip_data.get("legs", [])
        if not legs:
            saved["skipped"] += 1
            continue
        
        # Create trip
        trip = create_trip(
            status="upcoming",
            calendar_event_ids=trip_data.get("calendar_event_ids", []),
            gmail_message_ids=trip_data.get("gmail_message_ids", [])
        )
        saved["trips"] += 1
        
        # Create legs
        for leg_data in legs:
            create_leg(
                trip_id=trip["id"],
                sequence=leg_data.get("sequence", 1),
                flight_number=leg_data.get("flight_number", "Unknown"),
                departure_airport=leg_data.get("departure_airport", "???"),
                arrival_airport=leg_data.get("arrival_airport", "???"),
                departure_time=leg_data.get("departure_time", ""),
                arrival_time=leg_data.get("arrival_time", ""),
                destination_city=leg_data.get("destination_city"),
                hotel=leg_data.get("hotel")
            )
            saved["legs"] += 1
    
    return saved


async def run_full_extraction(dry_run: bool = False):
    """
    Run the full extraction pipeline.
    
    1. Fetch calendar events (via Zo app tools - requires interactive session)
    2. Fetch emails (via Zo app tools - requires interactive session)  
    3. Send to LLM for extraction
    4. Save to trip store
    """
    print("Where's V - Trip Extraction Pipeline")
    print("=" * 50)
    
    # For now, since we can't directly call app tools from a script,
    # we'll output the queries needed and rely on extract_trips.py
    # being called from within a Zo conversation that can use the tools
    
    print("\nThis script needs to be run from within a Zo conversation")
    print("that can call use_app_google_calendar and use_app_gmail.")
    print("\nThe Zo conversation should:")
    print("1. Call use_app_google_calendar to get events")
    print("2. Call use_app_gmail to get flight/hotel emails")
    print("3. Pass the results to this script")
    print("\nAlternatively, manually add trips with trip_store_v2.py")
    
    if dry_run:
        print("\n--- DRY RUN MODE ---")
        calendar_query = fetch_calendar_events()
        gmail_query = build_gmail_query()
        
        print("\nCalendar query:")
        print(json.dumps(calendar_query, indent=2))
        
        print("\nGmail query:")
        print(json.dumps(gmail_query, indent=2))
    
    return {"status": "needs_interactive_session"}


def run_with_data(calendar_json: str, email_json: str, dry_run: bool = False):
    """
    Run extraction with pre-fetched data.
    
    Args:
        calendar_json: JSON string of calendar events
        email_json: JSON string of email data (flight + hotel combined)
        dry_run: If True, just show what would be extracted
    """
    calendar_events = json.loads(calendar_json) if calendar_json else []
    emails = json.loads(email_json) if email_json else []
    
    async def _run():
        extracted = await extract_from_calendar_and_gmail(
            calendar_events=calendar_events,
            flight_emails=emails,
            hotel_emails=[],
            dry_run=dry_run
        )
        
        if not dry_run and extracted.get("trips"):
            saved = save_extracted_trips(extracted)
            print(f"\nSaved: {saved['trips']} trips, {saved['legs']} legs")
            if saved["skipped"]:
                print(f"Skipped: {saved['skipped']} empty trips")
        
        return extracted
    
    return asyncio.run(_run())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract trips from Calendar and Gmail")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without saving")
    parser.add_argument("--calendar", type=str, help="JSON file with calendar events")
    parser.add_argument("--email", type=str, help="JSON file with email data")
    parser.add_argument("--status", action="store_true", help="Show current trip status")
    
    args = parser.parse_args()
    
    if args.status:
        state = get_current_state()
        print(json.dumps(state, indent=2, default=str))
    elif args.calendar or args.email:
        calendar_data = ""
        email_data = ""
        
        if args.calendar:
            with open(args.calendar) as f:
                calendar_data = f.read()
        
        if args.email:
            with open(args.email) as f:
                email_data = f.read()
        
        result = run_with_data(calendar_data, email_data, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, default=str))
    else:
        asyncio.run(run_full_extraction(dry_run=args.dry_run))


