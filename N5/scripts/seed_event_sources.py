#!/usr/bin/env python3
"""
Event Allowlist Seeder
Scans historical Gmail data (6 months) to identify frequent event senders.
Helps bootstrap the allowlist with proven sources.

Usage:
    python3 N5/scripts/seed_event_sources.py [--days 180] [--min-count 2]
"""

import argparse
import json
import re
import logging
from pathlib import Path
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("event_seeder")

def build_historical_query(days):
    platforms = [
        '"lu.ma"',
        '"partiful.com/e/"',
        '"supermomos.com/events"',
        '"eventbrite.com/e/"',
        '"meetup.com" "events"'
    ]
    platform_query = " OR ".join(platforms)
    return f"({platform_query}) newer_than:{days}d"

def parse_sender(sender_str):
    match = re.search(r'^(.*?) <(.*?)>$', sender_str)
    if match:
        return match.group(1).strip().strip('"'), match.group(2).strip()
    return "", sender_str.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--min-count", type=int, default=1)
    parser.add_argument("--email-file", help="Path to JSON file containing historical emails")
    args = parser.parse_args()

    if not args.email_file:
        query = build_historical_query(args.days)
        print(f"QUERY_START\n{query}\nQUERY_END")
        return

    try:
        with open(args.email_file, "r") as f:
            emails = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load emails: {e}")
        return

    sender_counts = Counter()
    sender_details = {} # email -> name

    for msg in emails:
        sender_raw = msg.get("from", "")
        if not sender_raw:
            continue
        
        name, email = parse_sender(sender_raw)
        sender_counts[email] += 1
        if name and not sender_details.get(email):
            sender_details[email] = name

    # Sort by frequency
    sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for email, count in sorted_senders:
        if count >= args.min_count:
            results.append({
                "email": email,
                "name": sender_details.get(email, ""),
                "count": count
            })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()

