#!/usr/bin/env python3
"""
Where's V - Manual Refresh Script

Run this to pull latest travel data from Gmail and update the dashboard.

Usage:
    python3 refresh.py           # Full refresh
    python3 refresh.py --status  # Show current status only
    python3 refresh.py --dry-run # Show what would be extracted without saving
"""
import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
ZO_API_URL = "https://api.zo.computer/zo/ask"

EXTRACTION_PROMPT = """You are extracting V (Vrijen Attawar)'s travel itinerary from emails.

**V's profile:**
- Lives in NYC (home airports: JFK, LGA, EWR)
- Today is {today}

**RULES:**
- ONLY extract trips where V (Vrijen Attawar) is the traveler
- Trips must originate from NYC area (JFK/LGA/EWR)
- Include ALL segment types: flights, trains (Amtrak), buses
- For multi-city trips, capture each leg separately
- Include hotel details when found (name, address, phone, dates, confirmation)

**EMAILS:**
{emails}

**Return JSON (no markdown):**
{{
  "trips": [
    {{
      "id": "trip_YYYYMMDD_destination",
      "destination": "Primary destination city",
      "notes": "Brief trip description",
      "segments": [
        {{
          "sequence": 1,
          "type": "flight|train|bus",
          "carrier": "JetBlue|United|Amtrak|etc",
          "number": "B6 1234",
          "from_code": "JFK",
          "from_city": "New York",
          "to_code": "RDU",
          "to_city": "Raleigh",
          "departure": "2026-01-22T12:00:00-05:00",
          "arrival": "2026-01-22T13:50:00-05:00",
          "confirmation": "ABCDEF"
        }}
      ],
      "hotels": [
        {{
          "name": "Hotel Name",
          "city": "City",
          "address": "Full address",
          "phone": "+1-555-555-5555",
          "check_in": "2026-01-22",
          "check_out": "2026-01-24",
          "confirmation": "123456"
        }}
      ]
    }}
  ],
  "excluded": [
    {{"reason": "Not V's trip", "summary": "Description"}}
  ]
}}"""


async def fetch_emails(token: str) -> str:
    """Fetch travel-related emails via Zo API."""
    prompt = """Use the Gmail tool to search for travel confirmation emails.

Search query: subject:(confirmation OR itinerary OR reservation OR receipt OR booking) newer_than:90d

Return the full email payloads as text. Include withTextPayload=true.
Use the attawar.v@gmail.com account.

After fetching, return ALL the email content as plain text for extraction."""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={"authorization": token, "content-type": "application/json"},
            json={"input": prompt},
            timeout=aiohttp.ClientTimeout(total=180)
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Failed to fetch emails: {await resp.text()}")
            result = await resp.json()
            return result.get("output", "")


async def extract_trips(token: str, emails: str, dry_run: bool = False) -> dict:
    """Send emails to LLM for extraction."""
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    prompt = EXTRACTION_PROMPT.format(today=today, emails=emails[:100000])
    
    print(f"Sending {len(emails)} chars to LLM for extraction...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={"authorization": token, "content-type": "application/json"},
            json={"input": prompt},
            timeout=aiohttp.ClientTimeout(total=180)
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"LLM extraction failed: {await resp.text()}")
            result = await resp.json()
            output = result.get("output", "")
            
            # Parse JSON from response
            output = output.strip()
            if output.startswith("```"):
                start = output.find("{")
                end = output.rfind("}") + 1
                output = output[start:end]
            
            return json.loads(output)


def save_trips(extracted: dict):
    """Save extracted trips to the data store."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    trips = []
    legs = []
    
    for trip_data in extracted.get("trips", []):
        trip_id = trip_data.get("id", f"trip_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        trip = {
            "id": trip_id,
            "home_base": "NYC",
            "status": "upcoming",
            "notes": trip_data.get("notes", ""),
            "destination": trip_data.get("destination", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "legs": [],
            "sources": {"gmail_message_ids": [], "calendar_event_ids": []}
        }
        
        for seg in trip_data.get("segments", []):
            leg_id = f"leg_{trip_id}_{seg.get('sequence', 1):02d}"
            trip["legs"].append(leg_id)
            
            leg = {
                "id": leg_id,
                "trip_id": trip_id,
                "sequence": seg.get("sequence", 1),
                "type": seg.get("type", "flight"),
                "destination_city": seg.get("to_city", ""),
                "hotel": None
            }
            
            if seg.get("type") == "train":
                leg["train"] = {
                    "carrier": seg.get("carrier", "Amtrak"),
                    "service": seg.get("number", ""),
                    "departure_station": seg.get("from_code", ""),
                    "arrival_station": seg.get("to_code", ""),
                    "departure_time": seg.get("departure", ""),
                    "arrival_time": seg.get("arrival", ""),
                    "confirmation": seg.get("confirmation", "")
                }
            else:
                leg["flight"] = {
                    "number": seg.get("number", ""),
                    "departure_airport": seg.get("from_code", ""),
                    "arrival_airport": seg.get("to_code", ""),
                    "departure_time": seg.get("departure", ""),
                    "arrival_time": seg.get("arrival", ""),
                    "confirmation": seg.get("confirmation", "")
                }
            
            legs.append(leg)
        
        # Attach hotels to appropriate legs
        for hotel in trip_data.get("hotels", []):
            # Find the leg arriving at this hotel's city
            for leg in legs:
                if leg["trip_id"] == trip_id and leg["destination_city"].lower() == hotel.get("city", "").lower():
                    leg["hotel"] = hotel
                    break
        
        trips.append(trip)
    
    # Write to JSONL files
    with open(DATA_DIR / "trips_v2.jsonl", "w") as f:
        for trip in trips:
            f.write(json.dumps(trip) + "\n")
    
    with open(DATA_DIR / "legs_v2.jsonl", "w") as f:
        for leg in legs:
            f.write(json.dumps(leg) + "\n")
    
    # Update last scan time
    with open(DATA_DIR / "last_scan.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M ET"))
    
    return {"trips": len(trips), "legs": len(legs)}


def show_status():
    """Show current trip status."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from trip_store_v2 import get_current_state
    
    state = get_current_state()
    print(json.dumps(state, indent=2, default=str))


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Where's V - Manual Refresh")
    parser.add_argument("--status", action="store_true", help="Show current status only")
    parser.add_argument("--dry-run", action="store_true", help="Extract but don't save")
    parser.add_argument("--emails-file", type=str, help="Use local emails file instead of fetching")
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set")
        print("This script must be run from within a Zo conversation.")
        sys.exit(1)
    
    print("=" * 50)
    print("Where's V - Manual Refresh")
    print("=" * 50)
    
    # Get emails
    if args.emails_file:
        print(f"Loading emails from {args.emails_file}...")
        with open(args.emails_file) as f:
            emails = f.read()
    else:
        print("Fetching emails from Gmail...")
        emails = await fetch_emails(token)
    
    print(f"Got {len(emails)} chars of email data")
    
    # Extract trips
    extracted = await extract_trips(token, emails, dry_run=args.dry_run)
    
    print(f"\nExtracted {len(extracted.get('trips', []))} trips:")
    for trip in extracted.get("trips", []):
        print(f"  - {trip.get('destination')}: {len(trip.get('segments', []))} segments")
        for seg in trip.get("segments", []):
            print(f"      {seg.get('sequence')}. {seg.get('type')}: {seg.get('from_code')} → {seg.get('to_code')}")
    
    if extracted.get("excluded"):
        print(f"\nExcluded {len(extracted['excluded'])} items:")
        for exc in extracted["excluded"]:
            print(f"  - {exc.get('summary')}: {exc.get('reason')}")
    
    if args.dry_run:
        print("\n[DRY RUN - no changes saved]")
    else:
        result = save_trips(extracted)
        print(f"\nSaved: {result['trips']} trips, {result['legs']} legs")
        print("\nCurrent status:")
        show_status()


if __name__ == "__main__":
    asyncio.run(main())
