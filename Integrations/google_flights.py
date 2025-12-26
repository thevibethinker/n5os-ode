#!/usr/bin/env python3
"""
Google Flights Integration via SerpApi
Natural language flight search with preference-aware ranking.

Usage:
    python3 google_flights.py search --to LAX --date 2025-02-15
    python3 google_flights.py search --to LAX --date 2025-02-15 --return-date 2025-02-20
    python3 google_flights.py report --to LAX --date 2025-02-15

Environment:
    SERPAPI_PRIVATE_KEY: API key (set in Zo Settings > Developers)
"""

import argparse
import asyncio
import aiohttp
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SERPAPI_BASE = "https://serpapi.com/search.json"
BASELINE_PATH = Path("/home/workspace/Knowledge/reference/travel_baseline.yaml")
TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)

# Common IATA Verification Map (Expandable)
IATA_MAP = {
    "NEW YORK": "JFK",
    "NEWARK": "EWR",
    "LAGUARDIA": "LGA",
    "LOS ANGELES": "LAX",
    "LONDON": "LHR",
    "SAN FRANCISCO": "SFO",
    "SAN DIEGO": "SAN",
    "DENVER": "DEN",
    "AUSTIN": "AUS",
    "CHICAGO": "ORD",
    "BOSTON": "BOS",
    "MIAMI": "MIA",
    "SEATTLE": "SEA",
    "PORTLAND": "PDX",
    "LAS VEGAS": "LAS",
    "PHOENIX": "PHX",
    "DALLAS": "DFW",
    "HOUSTON": "IAH",
    "ATLANTA": "ATL",
    "WASHINGTON": "IAD",
    "BALTIMORE": "BWI",
    "PHILADELPHIA": "PHL",
}


@dataclass
class FlightPreferences:
    """V's codified flight preferences."""
    home_airports: list = field(default_factory=lambda: ["LGA", "JFK", "EWR"])
    preferred_airlines: list = field(default_factory=lambda: ["B6", "DL"])
    excluded_airlines: list = field(default_factory=lambda: ["F9", "NK"])
    primary_airline: str = "B6"  # JetBlue
    jfk_override_airline: str = "B6"  # If JetBlue, prefer JFK
    cabin_class: int = 1  # 1=Economy, 2=Premium Economy, 3=Business, 4=First
    max_stops: int = 0
    exclude_basic_economy: bool = True


def load_baseline() -> FlightPreferences:
    """Load preferences from YAML baseline."""
    prefs = FlightPreferences()
    
    if BASELINE_PATH.exists():
        try:
            with open(BASELINE_PATH) as f:
                config = yaml.safe_load(f)
            
            # Map airports by priority
            airports = config.get("airports", {}).get("departure_priority", [])
            prefs.home_airports = [a["code"] for a in sorted(airports, key=lambda x: x.get("priority", 99))]
            
            # Map airlines
            airlines = config.get("airlines", {})
            prefs.preferred_airlines = [a["code"] for a in airlines.get("preferred", [])]
            prefs.excluded_airlines = [a["code"] for a in airlines.get("excluded", [])]
            
            # Find primary airline
            for a in airlines.get("preferred", []):
                if a.get("tier") == "primary":
                    prefs.primary_airline = a["code"]
                    prefs.jfk_override_airline = a["code"]
                    break
            
            # Routing
            routing = config.get("routing", {})
            prefs.max_stops = routing.get("max_stops", 0)
            
            # Cabin
            cabin = config.get("cabin", {})
            prefs.exclude_basic_economy = "basic_economy" in cabin.get("exclude_fare_types", [])
            
            logger.info(f"Loaded baseline from {BASELINE_PATH}")
        except Exception as e:
            logger.warning(f"Could not load baseline: {e}. Using defaults.")
    
    return prefs


def get_api_key() -> str:
    """Get SerpApi key from environment."""
    key = os.environ.get("SERPAPI_PRIVATE_KEY")
    if not key:
        logger.error("SERPAPI_PRIVATE_KEY not found in environment")
        sys.exit(1)
    return key


def validate_date(date_str: str) -> bool:
    """Validate that the date is in YYYY-MM-DD format and not in the past."""
    try:
        search_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if search_date < today:
            logger.error(f"Invalid date: {date_str} is in the past.")
            return False
        return True
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Must be YYYY-MM-DD.")
        return False


def normalize_airport_code(code: str) -> str:
    """Normalize input to 3-letter IATA code."""
    code = code.strip().upper()
    if len(code) == 3:
        return code
    
    # Try fuzzy mapping
    return IATA_MAP.get(code, code)


async def search_flights(
    session: aiohttp.ClientSession,
    departure: str,
    arrival: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    prefs: Optional[FlightPreferences] = None
) -> dict:
    """Search flights for a specific origin/destination pair."""
    prefs = prefs or FlightPreferences()
    
    params = {
        "engine": "google_flights",
        "api_key": get_api_key(),
        "departure_id": departure,
        "arrival_id": arrival,
        "outbound_date": outbound_date,
        "currency": "USD",
        "hl": "en",
        "gl": "us",
        "travel_class": prefs.cabin_class,
        "stops": prefs.max_stops,
    }
    
    if return_date:
        params["return_date"] = return_date
        params["type"] = "1"  # Round trip
    else:
        params["type"] = "2"  # One way
    
    if prefs.exclude_basic_economy:
        params["exclude_basic"] = "true"
    
    try:
        async with session.get(SERPAPI_BASE, params=params, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                data["_search_params"] = {
                    "departure": departure,
                    "arrival": arrival,
                    "outbound_date": outbound_date,
                    "return_date": return_date
                }
                return data
            else:
                logger.error(f"API error {resp.status}: {await resp.text()}")
                return {"error": f"HTTP {resp.status}", "_search_params": params}
    except asyncio.TimeoutError:
        logger.error(f"Timeout searching {departure}->{arrival}")
        return {"error": "timeout", "_search_params": params}
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "_search_params": params}


def score_flight(flight: dict, departure_airport: str, prefs: FlightPreferences, time_pref: Optional[str] = None) -> float:
    """
    Score a flight based on V's preferences.
    Higher score = better match.
    """
    score = 100.0
    
    # Get flight details
    segments = flight.get("flights", [])
    if not segments:
        return 0
    
    first_segment = segments[0]
    airline_code = first_segment.get("airline", "")
    
    # Extract airline code from various formats
    if len(airline_code) > 2:
        # Sometimes it's the full name, try to extract code
        flight_number = first_segment.get("flight_number", "")
        if flight_number and len(flight_number) >= 2:
            airline_code = flight_number[:2]
    
    # Hard exclusions
    for excluded in prefs.excluded_airlines:
        if excluded in airline_code or excluded in first_segment.get("airline", ""):
            return -1000  # Hard exclude
    
    # Preferred airline bonus
    if airline_code in prefs.preferred_airlines or prefs.primary_airline in first_segment.get("airline", ""):
        score += 50
        # Extra bonus for primary airline
        if airline_code == prefs.primary_airline or prefs.primary_airline in first_segment.get("airline", ""):
            score += 25
    
    # JFK + JetBlue override logic
    if departure_airport == "JFK" and (airline_code == "B6" or "JetBlue" in first_segment.get("airline", "")):
        score += 30  # Strong bonus for JFK+JetBlue combo
    
    # Airport priority penalty (lower priority airports get penalized)
    # Only apply if it is one of our home airports
    if departure_airport in prefs.home_airports:
        try:
            airport_rank = prefs.home_airports.index(departure_airport)
            score -= airport_rank * 10  # LGA=0, JFK=-10, EWR=-20
        except ValueError:
            pass

    # Time of day preference
    if time_pref:
        dep_time_str = first_segment.get("departure_airport", {}).get("time", "")
        if dep_time_str:
            try:
                # Format: "2026-01-09 11:10"
                dep_dt = datetime.strptime(dep_time_str, "%Y-%m-%d %H:%M")
                hour = dep_dt.hour
                
                is_match = False
                if time_pref == "morning" and 5 <= hour <= 10:
                    is_match = True
                elif time_pref == "midday" and 11 <= hour <= 15:
                    is_match = True
                elif time_pref == "evening" and 16 <= hour <= 21:
                    is_match = True
                
                if is_match:
                    score += 40
                else:
                    score -= 20
            except Exception:
                pass

    # Stops penalty
    total_stops = len(segments) - 1
    score -= total_stops * 40
    
    # Duration penalty (prefer shorter flights)
    total_duration = flight.get("total_duration", 0)
    if total_duration > 0:
        score -= total_duration / 60  # -1 point per hour
    
    # Price factor (lower is better, but don't dominate)
    price = flight.get("price", 0)
    if price > 0:
        score -= price / 50  # -1 point per $50
    
    return score


def rank_flights(all_results: list, prefs: FlightPreferences) -> list:
    """
    Rank all flights across all searched airports.
    Returns sorted list of (flight, score, departure_airport).
    """
    scored = []
    
    for result in all_results:
        if "error" in result:
            continue
        
        departure = result.get("_search_params", {}).get("departure", "???")
        
        # Process best_flights and other_flights
        for flight_list_key in ["best_flights", "other_flights"]:
            for flight in result.get(flight_list_key, []):
                score = score_flight(flight, departure, prefs)
                if score > -500:  # Not hard excluded
                    scored.append({
                        "flight": flight,
                        "score": score,
                        "departure_airport": departure,
                        "source": flight_list_key
                    })
    
    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def format_flight(item: dict, rank: int) -> str:
    """Format a single flight for display."""
    flight = item["flight"]
    segments = flight.get("flights", [])
    
    if not segments:
        return f"#{rank}: No segment data"
    
    first = segments[0]
    last = segments[-1]
    
    dep_airport = first.get("departure_airport", {})
    arr_airport = last.get("arrival_airport", {})
    
    airline = first.get("airline", "Unknown")
    flight_num = first.get("flight_number", "")
    price = flight.get("price", "N/A")
    duration = flight.get("total_duration", 0)
    stops = len(segments) - 1
    
    hours = duration // 60
    mins = duration % 60
    
    dep_time = dep_airport.get("time", "").split(" ")[-1] if dep_airport.get("time") else "?"
    arr_time = arr_airport.get("time", "").split(" ")[-1] if arr_airport.get("time") else "?"
    
    stops_str = "Nonstop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
    
    return (
        f"#{rank} | {item['departure_airport']} | {airline} {flight_num} | "
        f"${price} | {dep_time}→{arr_time} | {hours}h{mins}m | {stops_str} | "
        f"Score: {item['score']:.0f}"
    )


def extract_price_insights(results: list) -> dict:
    """Extract price insights from search results."""
    insights = {
        "lowest_price": None,
        "price_level": None,
        "typical_range": None
    }
    
    for result in results:
        if "price_insights" in result:
            pi = result["price_insights"]
            insights["lowest_price"] = pi.get("lowest_price")
            insights["price_level"] = pi.get("price_level")
            if "typical_price_range" in pi:
                insights["typical_range"] = pi["typical_price_range"]
            break
    
    return insights


async def multi_airport_search(
    arrival: str,
    outbound_date: str,
    departure: Optional[str] = None,
    return_date: Optional[str] = None,
    time_pref: Optional[str] = None,
    aircraft_pref: Optional[str] = None,
    prefs: Optional[FlightPreferences] = None
) -> dict:
    """Search from specific or home airports and rank results."""
    prefs = prefs or load_baseline()
    
    # Normalize and Validate
    arrival = normalize_airport_code(arrival)
    
    origins = [normalize_airport_code(departure)] if departure else prefs.home_airports
    
    if not validate_date(outbound_date):
        return {"error": f"Invalid outbound date: {outbound_date}", "ranked_flights": [], "total_options": 0, "price_insights": {}, "search_params": {"arrival": arrival, "outbound_date": outbound_date}}
    
    if return_date and not validate_date(return_date):
        return {"error": f"Invalid return date: {return_date}", "ranked_flights": [], "total_options": 0, "price_insights": {}, "search_params": {"arrival": arrival, "outbound_date": outbound_date}}

    async with aiohttp.ClientSession() as session:
        # Search from all departure airports in parallel
        tasks = [
            search_flights(session, dep, arrival, outbound_date, return_date, prefs)
            for dep in origins
        ]
        
        results = await asyncio.gather(*tasks)
    
    # Filter by aircraft if requested
    if aircraft_pref:
        aircraft_pref = aircraft_pref.lower()
        for res in results:
            for list_key in ["best_flights", "other_flights"]:
                if list_key in res:
                    filtered = []
                    for f in res[list_key]:
                        # Check all segments
                        is_match = True
                        for segment in f.get("flights", []):
                            airplane = segment.get("airplane", "").lower()
                            if aircraft_pref not in airplane:
                                is_match = False
                                break
                        if is_match:
                            filtered.append(f)
                    res[list_key] = filtered

    # Rank all results
    ranked = []
    for result in results:
        if "error" in result:
            continue
        dep = result.get("_search_params", {}).get("departure", "???")
        for flight_list_key in ["best_flights", "other_flights"]:
            for flight in result.get(flight_list_key, []):
                score = score_flight(flight, dep, prefs, time_pref=time_pref)
                if score > -500:
                    ranked.append({
                        "flight": flight,
                        "score": score,
                        "departure_airport": dep,
                        "source": flight_list_key
                    })
    
    ranked.sort(key=lambda x: x["score"], reverse=True)
    
    # Extract price insights
    insights = extract_price_insights(results)
    
    return {
        "ranked_flights": ranked[:15],
        "total_options": len(ranked),
        "price_insights": insights,
        "search_params": {
            "departure": departure if departure else "Home Airports",
            "arrival": arrival,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "time_pref": time_pref,
            "aircraft_pref": aircraft_pref
        },
        "raw_results": results
    }


def print_route_report(data: dict) -> None:
    """Print a formatted route report."""
    if "error" in data:
        print("\n" + "!" * 70)
        print(f"ERROR: {data['error']}")
        print("!" * 70 + "\n")
        return

    params = data["search_params"]
    insights = data["price_insights"]
    ranked = data["ranked_flights"]
    
    print("\n" + "=" * 70)
    origin_label = params['departure']
    print(f"ROUTE REPORT: {origin_label} → {params['arrival']}")
    print(f"Date: {params['outbound_date']}", end="")
    if params.get("return_date"):
        print(f" → {params['return_date']} (Round Trip)")
    else:
        print(" (One Way)")
    print("=" * 70)
    
    # Price insights
    if insights.get("lowest_price"):
        print(f"\n💰 Price Insights:")
        print(f"   Lowest Available: ${insights['lowest_price']}")
        if insights.get("price_level"):
            print(f"   Current Level: {insights['price_level']}")
        if insights.get("typical_range"):
            print(f"   Typical Range: ${insights['typical_range'][0]} - ${insights['typical_range'][1]}")
    
    # Top recommendations
    print(f"\n✈️  Top {min(10, len(ranked))} Options (of {data['total_options']} found):")
    print("-" * 70)
    
    for i, item in enumerate(ranked[:10], 1):
        print(format_flight(item, i))
    
    print("-" * 70)
    
    # Recommendation
    if ranked:
        top = ranked[0]
        flight = top["flight"]
        airline = flight.get("flights", [{}])[0].get("airline", "Unknown")
        print(f"\n🎯 Recommendation: Book #{1} - {airline} from {top['departure_airport']}")
        print(f"   Reasoning: Best score ({top['score']:.0f}) based on your preferences")
    
    print("\n" + "=" * 70)


async def main():
    parser = argparse.ArgumentParser(description="Google Flights Search with V's Preferences")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search flights")
    search_parser.add_argument("--from", dest="departure", help="Origin airport code")
    search_parser.add_argument("--to", required=True, help="Destination airport code")
    search_parser.add_argument("--date", required=True, help="Outbound date (YYYY-MM-DD)")
    search_parser.add_argument("--return-date", help="Return date for round trip")
    search_parser.add_argument("--time", choices=["morning", "midday", "evening"], help="Time of day preference")
    search_parser.add_argument("--aircraft", help="Aircraft type filter (e.g. airbus)")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Report command (same as search but formatted)
    report_parser = subparsers.add_parser("report", help="Generate route report")
    report_parser.add_argument("--from", dest="departure", help="Origin airport code")
    report_parser.add_argument("--to", required=True, help="Destination airport code")
    report_parser.add_argument("--date", required=True, help="Outbound date (YYYY-MM-DD)")
    report_parser.add_argument("--return-date", help="Return date for round trip")
    report_parser.add_argument("--time", choices=["morning", "midday", "evening"], help="Time of day preference")
    report_parser.add_argument("--aircraft", help="Aircraft type filter (e.g. airbus)")
    
    # Check baseline
    subparsers.add_parser("baseline", help="Show current baseline preferences")
    
    args = parser.parse_args()
    
    if args.command == "baseline":
        prefs = load_baseline()
        print(f"Departure Airports: {prefs.home_airports}")
        print(f"Preferred Airlines: {prefs.preferred_airlines}")
        print(f"Excluded Airlines: {prefs.excluded_airlines}")
        print(f"Primary Airline: {prefs.primary_airline}")
        print(f"Max Stops: {prefs.max_stops}")
        print(f"Exclude Basic Economy: {prefs.exclude_basic_economy}")
        return
    
    if args.command in ["search", "report"]:
        prefs = load_baseline()
        data = await multi_airport_search(
            departure=getattr(args, "departure", None),
            arrival=args.to,
            outbound_date=args.date,
            return_date=getattr(args, "return_date", None),
            time_pref=getattr(args, "time", None),
            aircraft_pref=getattr(args, "aircraft", None),
            prefs=prefs
        )
        
        if args.command == "search" and getattr(args, "json", False):
            # Remove raw_results for cleaner JSON output
            output = {k: v for k, v in data.items() if k != "raw_results"}
            print(json.dumps(output, indent=2, default=str))
        else:
            print_route_report(data)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())



