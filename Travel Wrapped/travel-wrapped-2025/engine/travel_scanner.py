#!/usr/bin/env python3
"""
Travel Wrapped 2025 - Gmail Scanner Engine
==========================================
2-Stage Gmail scanning for travel booking discovery.

Stage 1: Sender Discovery - Identify travel-related senders in user's inbox
Stage 2: Deep Fetch - Pull all emails from discovered senders for the year

Usage:
    # Stage 1: Discover senders
    python travel_scanner.py discover --year 2025
    
    # Stage 2: Fetch all emails from a sender
    python travel_scanner.py fetch --sender "noreply@jetblue.com" --year 2025
    
    # Full pipeline (both stages)
    python travel_scanner.py full --year 2025

Output: JSON files in ./data/ directory
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Known travel-related senders and keywords
TRAVEL_SENDERS = {
    # Airlines
    "airlines": [
        "jetblue.com", "united.com", "delta.com", "aa.com", "southwest.com",
        "spirit.com", "frontier.com", "alaskaair.com", "hawaiianairlines.com",
        "aircanada.com", "britishairways.com", "lufthansa.com", "emirates.com",
        "qatarairways.com", "singaporeair.com", "cathaypacific.com"
    ],
    # Hotels
    "hotels": [
        "marriott.com", "hilton.com", "ihg.com", "hyatt.com", "wyndham.com",
        "choicehotels.com", "bestwestern.com", "radisson.com", "accor.com",
        "fourseasons.com", "ritzcarlton.com", "starwood.com"
    ],
    # OTAs (Online Travel Agencies)
    "otas": [
        "booking.com", "expedia.com", "hotels.com", "priceline.com",
        "kayak.com", "orbitz.com", "travelocity.com", "hotwire.com",
        "tripadvisor.com", "agoda.com", "trip.com"
    ],
    # Vacation Rentals
    "rentals": [
        "airbnb.com", "vrbo.com", "homeaway.com", "vacasa.com"
    ],
    # Car Rentals
    "cars": [
        "enterprise.com", "hertz.com", "avis.com", "budget.com",
        "nationalcar.com", "alamo.com", "sixt.com", "turo.com"
    ],
    # Rail & Other
    "rail": [
        "amtrak.com", "eurostar.com", "thetrainline.com"
    ],
    # Aggregators & Misc
    "other": [
        "google.com/travel", "flightradar24.com", "flightaware.com",
        "checkmytrip.com", "tripit.com"
    ]
}

TRAVEL_KEYWORDS = [
    "flight confirmation", "booking confirmation", "reservation confirmed",
    "itinerary", "e-ticket", "boarding pass", "check-in", "your trip",
    "hotel reservation", "your stay", "rental confirmation", "car rental",
    "your booking", "trip confirmation", "travel confirmation"
]


def get_all_sender_domains() -> list[str]:
    """Flatten all known travel sender domains."""
    all_domains = []
    for category, domains in TRAVEL_SENDERS.items():
        all_domains.extend(domains)
    return all_domains


def build_gmail_query_for_discovery(year: int) -> str:
    """
    Build a Gmail search query to discover travel-related emails.
    Uses OR logic across known senders and keywords.
    """
    start_date = f"{year}/01/01"
    end_date = f"{year}/12/31"
    
    # Build sender portion
    domains = get_all_sender_domains()
    sender_queries = [f"from:{d}" for d in domains[:20]]  # Limit to avoid query length issues
    
    # Build keyword portion
    keyword_queries = [f'subject:"{kw}"' for kw in TRAVEL_KEYWORDS[:10]]
    
    # Combine with date filter
    query = f"after:{start_date} before:{end_date} ({' OR '.join(sender_queries)} OR {' OR '.join(keyword_queries)})"
    
    return query


def build_gmail_query_for_sender(sender: str, year: int) -> str:
    """Build a Gmail query for all emails from a specific sender in a year."""
    start_date = f"{year}/01/01"
    end_date = f"{year}/12/31"
    return f"from:{sender} after:{start_date} before:{end_date}"


def generate_zo_gmail_instructions(mode: str, year: int, sender: Optional[str] = None) -> dict:
    """
    Generate instructions for Zo to execute via use_app_gmail.
    This output is consumed by the orchestrating prompt.
    """
    if mode == "discover":
        query = build_gmail_query_for_discovery(year)
        return {
            "mode": "discover",
            "year": year,
            "gmail_tool": "gmail-find-email",
            "gmail_params": {
                "q": query,
                "maxResults": 100
            },
            "next_step": "Parse results to extract unique sender domains, then run 'fetch' for each."
        }
    
    elif mode == "fetch":
        if not sender:
            raise ValueError("Sender required for fetch mode")
        query = build_gmail_query_for_sender(sender, year)
        return {
            "mode": "fetch",
            "year": year,
            "sender": sender,
            "gmail_tool": "gmail-find-email",
            "gmail_params": {
                "q": query,
                "maxResults": 50
            },
            "next_step": "Parse email bodies for booking details (dates, destinations, confirmation numbers)."
        }
    
    else:
        raise ValueError(f"Unknown mode: {mode}")


def save_output(data: dict, filename: str) -> Path:
    """Save output to the data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    output_path = data_dir / filename
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    logger.info(f"Output saved to: {output_path.absolute()}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Travel Wrapped 2025 - Gmail Scanner Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Discover command
    discover_parser = subparsers.add_parser(
        "discover",
        help="Stage 1: Discover travel-related senders in Gmail"
    )
    discover_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year to scan (default: 2025)"
    )
    discover_parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the Gmail query without executing"
    )
    
    # Fetch command
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Stage 2: Fetch all emails from a specific sender"
    )
    fetch_parser.add_argument(
        "--sender", required=True,
        help="Sender email domain to fetch (e.g., jetblue.com)"
    )
    fetch_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year to scan (default: 2025)"
    )
    fetch_parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the Gmail query without executing"
    )
    
    # List senders command
    list_parser = subparsers.add_parser(
        "list-senders",
        help="List all known travel sender domains by category"
    )
    
    # Full pipeline info
    full_parser = subparsers.add_parser(
        "full",
        help="Show instructions for running the full pipeline"
    )
    full_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year to scan (default: 2025)"
    )
    
    args = parser.parse_args()
    
    if args.command == "list-senders":
        print("\n=== Known Travel Senders ===\n")
        for category, domains in TRAVEL_SENDERS.items():
            print(f"[{category.upper()}]")
            for d in domains:
                print(f"  - {d}")
            print()
        return 0
    
    elif args.command == "discover":
        instructions = generate_zo_gmail_instructions("discover", args.year)
        
        if args.dry_run:
            print("\n=== DRY RUN: Discovery Query ===\n")
            print(f"Gmail Query:\n{instructions['gmail_params']['q']}\n")
            print(f"Tool to use: {instructions['gmail_tool']}")
            print(f"Max results: {instructions['gmail_params']['maxResults']}")
        else:
            output_path = save_output(instructions, f"discover_{args.year}.json")
            print(f"\n✓ Discovery instructions saved to: {output_path}")
            print("\nNext: Zo will execute this via use_app_gmail and parse the results.")
        
        return 0
    
    elif args.command == "fetch":
        instructions = generate_zo_gmail_instructions("fetch", args.year, args.sender)
        
        if args.dry_run:
            print(f"\n=== DRY RUN: Fetch Query for {args.sender} ===\n")
            print(f"Gmail Query:\n{instructions['gmail_params']['q']}\n")
            print(f"Tool to use: {instructions['gmail_tool']}")
        else:
            safe_sender = args.sender.replace("@", "_at_").replace(".", "_")
            output_path = save_output(instructions, f"fetch_{safe_sender}_{args.year}.json")
            print(f"\n✓ Fetch instructions saved to: {output_path}")
        
        return 0
    
    elif args.command == "full":
        print(f"""
=== Travel Wrapped {args.year} - Full Pipeline ===

This scanner generates instructions for Zo to execute via Gmail integration.

STEP 1: Run discovery
    python travel_scanner.py discover --year {args.year}
    
    → Zo executes the Gmail query via use_app_gmail
    → Parse results to find unique travel senders
    
STEP 2: For each discovered sender, run fetch
    python travel_scanner.py fetch --sender <sender> --year {args.year}
    
    → Zo fetches all emails from that sender
    → Parse booking details from email bodies

STEP 3: Normalize data
    The orchestrating prompt will compile all findings into:
    - data/travel_metrics.json (structured travel data)
    
STEP 4: Generate site
    Use the remote UI blueprint to scaffold the dashboard.

Known sender categories: {', '.join(TRAVEL_SENDERS.keys())}
Total known domains: {len(get_all_sender_domains())}
""")
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())

