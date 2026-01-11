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
import re

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


async def search_multi_city(
    session: aiohttp.ClientSession,
    legs: list[dict],
    prefs: Optional[FlightPreferences] = None
) -> dict:
    """
    Search multi-city flights using SerpApi type=3.
    
    legs format: [{"from": "JFK", "to": "LAX", "date": "2026-01-22"}, ...]
    """
    prefs = prefs or FlightPreferences()
    
    # Convert legs to SerpApi format
    multi_city_data = []
    for leg in legs:
        multi_city_data.append({
            "departure_id": normalize_airport_code(leg["from"]),
            "arrival_id": normalize_airport_code(leg["to"]),
            "date": leg["date"]
        })
    
    params = {
        "engine": "google_flights",
        "api_key": get_api_key(),
        "type": "3",  # Multi-city
        "multi_city_json": json.dumps(multi_city_data),
        "currency": "USD",
        "hl": "en",
        "gl": "us",
        "travel_class": prefs.cabin_class,
        "stops": prefs.max_stops,
    }
    
    if prefs.exclude_basic_economy:
        params["exclude_basic"] = "true"
    
    try:
        async with session.get(SERPAPI_BASE, params=params, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                data["_search_params"] = {
                    "type": "multi_city",
                    "legs": legs
                }
                return data
            else:
                logger.error(f"API error {resp.status}: {await resp.text()}")
                return {"error": f"HTTP {resp.status}"}
    except asyncio.TimeoutError:
        logger.error("Timeout searching multi-city")
        return {"error": "timeout"}
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e)}


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


def format_flight(item: dict, rank: int, is_round_trip: bool = False, booking_url: Optional[str] = None) -> str:
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
    
    # Add trip type suffix to price
    price_suffix = " (RT)" if is_round_trip else " (OW)"
    price_display = f"${price}{price_suffix}" if price != "N/A" else "N/A"
    
    result = (
        f"#{rank} | {item['departure_airport']} | {airline} {flight_num} | "
        f"{price_display} | {dep_time}→{arr_time} | {hours}h{mins}m | {stops_str} | "
        f"Score: {item['score']:.0f}"
    )
    
    if booking_url:
        result += f"\n   📎 Book: {booking_url}"
    
    return result


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


async def extract_airline_url(session: aiohttp.ClientSession, redirect_url: str, post_data: str) -> Optional[str]:
    """POST to Google redirect, extract airline URL from meta refresh."""
    try:
        async with session.post(redirect_url, data=post_data, timeout=TIMEOUT) as resp:
            html = await resp.text()
        
        # Extract URL from meta refresh: content="0;url='https://...'"
        match = re.search(r"content=[\"'][^\"']*url=['\"]?([^\"'>\s]+)['\"]?", html, re.I)
        if match:
            url = match.group(1)
            # Unescape HTML entities
            url = url.replace("&amp;", "&")
            return url
        
        return None
    except Exception as e:
        logger.warning(f"Failed to extract airline URL: {e}")
        return None


async def get_booking_url(
    session: aiohttp.ClientSession,
    base_params: dict,
    departure_token: str,
) -> Optional[str]:
    """
    3-step flow to get direct airline booking URL for a round-trip.
    
    Step 1: Already done (we have departure_token from initial search)
    Step 2: Get return options with booking_token
    Step 3: Get booking_options with redirect URL
    Step 4: POST to redirect, extract airline URL from meta refresh
    
    Returns the direct airline booking URL or None if not available.
    """
    try:
        # Step 2: Get return flights using departure_token
        params2 = {**base_params, "departure_token": departure_token}
        async with session.get(SERPAPI_BASE, params=params2, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return None
            data2 = await resp.json()
        
        return_flights = data2.get("other_flights", [])
        if not return_flights:
            return None
        
        # Get booking_token from first return flight
        booking_token = return_flights[0].get("booking_token")
        if not booking_token:
            return None
        
        # Step 3: Get booking options
        params3 = {**base_params, "booking_token": booking_token}
        async with session.get(SERPAPI_BASE, params=params3, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return None
            data3 = await resp.json()
        
        booking_options = data3.get("booking_options", [])
        if not booking_options:
            return None
        
        # Find airline direct booking (prefer over 3rd party)
        for opt in booking_options:
            together = opt.get("together", {})
            if together.get("airline"):  # Direct airline booking
                br = together.get("booking_request", {})
                if br.get("url") and br.get("post_data"):
                    return await extract_airline_url(session, br["url"], br["post_data"])
        
        # Fallback: try first booking option even if not direct airline
        first_opt = booking_options[0].get("together", {})
        br = first_opt.get("booking_request", {})
        if br.get("url") and br.get("post_data"):
            return await extract_airline_url(session, br["url"], br["post_data"])
        
        return None
    except Exception as e:
        logger.warning(f"Failed to get booking URL: {e}")
        return None


async def multi_airport_search(
    arrival: str,
    outbound_date: str,
    departure: Optional[str] = None,
    return_date: Optional[str] = None,
    time_pref: Optional[str] = None,
    aircraft_pref: Optional[str] = None,
    prefs: Optional[FlightPreferences] = None,
    fetch_booking_links: bool = False
) -> dict:
    """Search from specific or home airports and rank results.
    
    Args:
        arrival: Destination airport code (IATA)
        outbound_date: Departure date (YYYY-MM-DD)
        departure: Specific origin airport (optional, defaults to home airports)
        return_date: Return date for round-trip (optional)
        time_pref: Time of day preference (morning/midday/evening)
        aircraft_pref: Filter by aircraft type
        prefs: FlightPreferences object (loaded from baseline if not provided)
        fetch_booking_links: If True, fetch direct airline booking URLs (adds API calls)
    
    Returns:
        dict with ranked_flights, total_options, price_insights, search_params
    """
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
            aircraft_pref_lower = aircraft_pref.lower()
            for res in results:
                for list_key in ["best_flights", "other_flights"]:
                    if list_key in res:
                        filtered = []
                        for f in res[list_key]:
                            is_match = True
                            for segment in f.get("flights", []):
                                airplane = segment.get("airplane", "").lower()
                                if aircraft_pref_lower not in airplane:
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
                            "source": flight_list_key,
                            "departure_token": flight.get("departure_token")
                        })
        
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        # Fetch booking links for top results if requested (round-trip only)
        if fetch_booking_links and return_date and ranked:
            base_params = {
                "engine": "google_flights",
                "api_key": get_api_key(),
                "departure_id": origins[0] if len(origins) == 1 else ranked[0]["departure_airport"],
                "arrival_id": arrival,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "currency": "USD",
                "hl": "en",
                "gl": "us",
            }
            
            # Fetch booking URLs for top 10 flights (to match display)
            for item in ranked[:10]:
                if item.get("departure_token"):
                    # Update base_params with correct departure airport
                    base_params["departure_id"] = item["departure_airport"]
                    booking_url = await get_booking_url(session, base_params, item["departure_token"])
                    item["booking_url"] = booking_url
    
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


def print_route_report(data: dict, show_booking_links: bool = False) -> None:
    """Print a formatted route report."""
    if "error" in data:
        print("\n" + "!" * 70)
        print(f"ERROR: {data['error']}")
        print("!" * 70 + "\n")
        return

    params = data["search_params"]
    insights = data["price_insights"]
    ranked = data["ranked_flights"]
    
    is_round_trip = bool(params.get("return_date"))
    trip_type_label = "ROUND TRIP" if is_round_trip else "ONE WAY"
    
    print("\n" + "=" * 70)
    print(f"ROUTE REPORT: {params['departure']} → {params['arrival']}")
    print(f"Date: {params['outbound_date']}", end="")
    if params.get("return_date"):
        print(f" → {params['return_date']} ({trip_type_label})")
    else:
        print(f" ({trip_type_label})")
    print("=" * 70)
    
    # No results handling
    if not ranked:
        print("\n⚠️  No flights found matching your criteria.")
        print("   Possible reasons:")
        print("   • Invalid airport code (verify IATA code)")
        print("   • No nonstop flights available on this route")
        print("   • All available options are basic economy (excluded)")
        print("   • Route not served by preferred airlines")
        print("\n   Try: Relaxing search criteria or checking airport code")
        print("=" * 70)
        return
    
    # Price insights
    if insights.get("lowest_price"):
        price_suffix = " (RT)" if is_round_trip else " (OW)"
        print(f"\n💰 Price Insights:")
        print(f"   Lowest Available: ${insights['lowest_price']}{price_suffix}")
        if insights.get("price_level"):
            print(f"   Current Level: {insights['price_level']}")
        if insights.get("typical_range"):
            print(f"   Typical Range: ${insights['typical_range'][0]} - ${insights['typical_range'][1]}{price_suffix}")
    
    # Top recommendations
    print(f"\n✈️  Top {min(10, len(ranked))} Options (of {data['total_options']} found):")
    print("-" * 70)
    
    for i, item in enumerate(ranked[:10], 1):
        booking_url = item.get("booking_url") if show_booking_links else None
        print(format_flight(item, i, is_round_trip=is_round_trip, booking_url=booking_url))
    
    print("-" * 70)
    
    # Recommendation
    if ranked:
        top = ranked[0]
        flight = top["flight"]
        airline = flight.get("flights", [{}])[0].get("airline", "Unknown")
        print(f"\n🎯 Recommendation: Book #{1} - {airline} from {top['departure_airport']}")
        print(f"   Reasoning: Best score ({top['score']:.0f}) based on your preferences")
        if show_booking_links and top.get("booking_url"):
            print(f"   📎 Direct booking: {top['booking_url']}")
    
    print("\n" + "=" * 70)


def print_multi_city_report(data: dict):
    """Print formatted multi-city search results."""
    legs = data.get("legs", [])
    results = data.get("results", [])
    
    print("\n" + "=" * 70)
    print("MULTI-CITY ROUTE REPORT")
    print("-" * 70)
    for i, leg in enumerate(legs, 1):
        print(f"  Leg {i}: {leg['from']} → {leg['to']} on {leg['date']}")
    print("=" * 70)
    
    if not results:
        print("\n❌ No flights found for this itinerary.")
        return
    
    # Price insights if available
    price_insights = data.get("price_insights")
    if price_insights:
        print(f"\n💰 Price Insights:")
        print(f"   Lowest Available: ${price_insights.get('lowest_price', 'N/A')} (MC)")
        print(f"   Current Level: {price_insights.get('price_level', 'unknown')}")
    
    print(f"\n✈️  Top {len(results)} Options:")
    print("-" * 70)
    
    for i, option in enumerate(results, 1):
        price = option.get("price", "N/A")
        total_duration = option.get("total_duration", 0)
        hours = total_duration // 60
        mins = total_duration % 60
        
        # Get flight details from each leg
        # Multi-city structure: option["flights"] is a list of leg dicts, each with segment info directly
        flights_info = []
        for leg in option.get("flights", []):
            # Check if this is a segment directly (multi-city) or has nested flights (round-trip)
            if "flights" in leg:
                # Nested structure (round-trip style)
                segments = leg.get("flights", [])
                if segments:
                    first_seg = segments[0]
                    last_seg = segments[-1]
            else:
                # Direct segment (multi-city style)
                first_seg = leg
                last_seg = leg
            
            airline = first_seg.get("airline", "")
            flight_num = first_seg.get("flight_number", "")
            dep_airport = first_seg.get("departure_airport", {})
            arr_airport = last_seg.get("arrival_airport", {})
            dep_time = dep_airport.get("time", "").split(" ")[-1] if dep_airport.get("time") else ""
            arr_time = arr_airport.get("time", "").split(" ")[-1] if arr_airport.get("time") else ""
            dep_code = dep_airport.get("id", "")
            arr_code = arr_airport.get("id", "")
            flights_info.append(f"{airline} {flight_num} {dep_code}→{arr_code} {dep_time}→{arr_time}")
        
        print(f"#{i} | ${price} (MC) | {hours}h{mins}m total")
        for leg_num, flight_info in enumerate(flights_info, 1):
            print(f"     Leg {leg_num}: {flight_info}")
        print()
    
    print("-" * 70)
    print("(MC) = Multi-city total price")
    print("=" * 70)


async def main():
    parser = argparse.ArgumentParser(description="Google Flights Search with V's Preferences")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search flights")
    search_parser.add_argument("--from", dest="departure", help="Origin airport code")
    search_parser.add_argument("--to", help="Destination airport code (required unless --multi-city)")
    search_parser.add_argument("--date", help="Outbound date (YYYY-MM-DD) (required unless --multi-city)")
    search_parser.add_argument("--return-date", help="Return date for round trip")
    search_parser.add_argument("--one-way", action="store_true", help="Search one-way only (no return)")
    search_parser.add_argument("--multi-city", type=str, help='Multi-city JSON: [{"from":"JFK","to":"LAX","date":"2026-01-22"},...]')
    search_parser.add_argument("--time", choices=["morning", "midday", "evening"], help="Time of day preference")
    search_parser.add_argument("--aircraft", help="Aircraft type filter (e.g. airbus)")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    search_parser.add_argument("--booking-link", action="store_true", help="Include direct airline booking URLs (requires additional API calls)")
    
    # Report command (same as search but formatted)
    report_parser = subparsers.add_parser("report", help="Generate route report")
    report_parser.add_argument("--from", dest="departure", help="Origin airport code")
    report_parser.add_argument("--to", help="Destination airport code (required unless --multi-city)")
    report_parser.add_argument("--date", help="Outbound date (YYYY-MM-DD) (required unless --multi-city)")
    report_parser.add_argument("--return-date", help="Return date for round trip")
    report_parser.add_argument("--one-way", action="store_true", help="Search one-way only (no return)")
    report_parser.add_argument("--multi-city", type=str, help='Multi-city JSON: [{"from":"JFK","to":"LAX","date":"2026-01-22"},...]')
    report_parser.add_argument("--time", choices=["morning", "midday", "evening"], help="Time of day preference")
    report_parser.add_argument("--aircraft", help="Aircraft type filter (e.g. airbus)")
    report_parser.add_argument("--booking-link", action="store_true", help="Include direct airline booking URLs (requires additional API calls)")
    
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
        
        # Handle multi-city
        multi_city = getattr(args, "multi_city", None)
        if multi_city:
            try:
                legs = json.loads(multi_city)
                # Validate legs
                for i, leg in enumerate(legs):
                    if not all(k in leg for k in ["from", "to", "date"]):
                        print(f"Error: Leg {i+1} missing required fields (from, to, date)")
                        sys.exit(1)
                    if not validate_date(leg["date"]):
                        sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON for --multi-city: {e}")
                sys.exit(1)
            
            async with aiohttp.ClientSession() as session:
                data = await search_multi_city(session, legs, prefs)
            
            # Format multi-city output
            if "error" in data:
                print(f"Error: {data['error']}")
                sys.exit(1)
            
            all_flights = data.get("best_flights", []) + data.get("other_flights", [])
            price_insights = data.get("price_insights")
            
            print_multi_city_report({
                "legs": legs,
                "results": all_flights,
                "price_insights": price_insights
            })
            return
        
        # Validate required args for non-multi-city
        if not args.to:
            print("Error: --to is required (unless using --multi-city)")
            sys.exit(1)
        if not args.date:
            print("Error: --date is required (unless using --multi-city)")
            sys.exit(1)
        
        # Default to round-trip unless --one-way specified
        one_way = getattr(args, "one_way", False)
        return_date = getattr(args, "return_date", None)
        
        # Warn about conflicting flags
        if one_way and return_date:
            print("⚠️  Warning: --one-way specified with --return-date. Ignoring return date.")
            return_date = None
        
        if not one_way and not return_date:
            print("Error: Round-trip requires --return-date. Use --one-way for one-way search.")
            sys.exit(1)
        
        data = await multi_airport_search(
            departure=getattr(args, "departure", None),
            arrival=args.to,
            outbound_date=args.date,
            return_date=return_date if not one_way else None,
            time_pref=getattr(args, "time", None),
            aircraft_pref=getattr(args, "aircraft", None),
            prefs=prefs,
            fetch_booking_links=getattr(args, "booking_link", False)
        )
        
        if args.command == "search" and getattr(args, "json", False):
            # Remove raw_results for cleaner JSON output
            output = {k: v for k, v in data.items() if k != "raw_results"}
            print(json.dumps(output, indent=2, default=str))
        else:
            print_route_report(data, show_booking_links=getattr(args, "booking_link", False))
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())











