#!/usr/bin/env python3
"""
Gmail Ingestion for Where's V
Fetches flight confirmation emails from Gmail.

This script outputs raw email data as JSON for LLM processing.
It does NOT parse flight details - that's done by extract_trips.py.
"""
import json
import sys
from datetime import datetime, timezone, timedelta

# Gmail search queries for flight confirmations
FLIGHT_QUERIES = [
    # Airline confirmation emails
    "from:(united.com OR delta.com OR aa.com OR jetblue.com OR southwest.com) subject:(confirmation OR itinerary OR receipt)",
    # General flight keywords
    "subject:(flight confirmation OR e-ticket OR boarding pass OR itinerary)",
    # Travel booking sites
    "from:(expedia.com OR kayak.com OR google.com) subject:(flight OR trip)",
]

# Hotel search queries (for destination context)
HOTEL_QUERIES = [
    "from:(marriott.com OR hilton.com OR hyatt.com OR ihg.com OR airbnb.com) subject:(confirmation OR reservation)",
    "subject:(hotel confirmation OR hotel reservation OR booking confirmation)",
]


def build_gmail_query(days_back: int = 30, days_forward: int = 60) -> dict:
    """
    Build Gmail search query parameters.
    
    Returns dict with query parameters for the Gmail API.
    """
    # Gmail search supports after: and before: date operators
    now = datetime.now(timezone.utc)
    after_date = (now - timedelta(days=days_back)).strftime("%Y/%m/%d")
    before_date = (now + timedelta(days=days_forward)).strftime("%Y/%m/%d")
    
    # Combine all flight queries with OR
    flight_query = " OR ".join([f"({q})" for q in FLIGHT_QUERIES])
    hotel_query = " OR ".join([f"({q})" for q in HOTEL_QUERIES])
    
    # Add date range
    full_flight_query = f"({flight_query}) after:{after_date}"
    full_hotel_query = f"({hotel_query}) after:{after_date}"
    
    return {
        "flight_query": {
            "tool": "gmail-find-email",
            "params": {
                "q": full_flight_query,
                "maxResults": 50
            }
        },
        "hotel_query": {
            "tool": "gmail-find-email", 
            "params": {
                "q": full_hotel_query,
                "maxResults": 30
            }
        },
        "time_range": {
            "from": after_date,
            "to": before_date
        }
    }


def format_emails_for_extraction(emails: list[dict]) -> str:
    """
    Format emails for LLM extraction prompt.
    
    Args:
        emails: List of email dicts with subject, from, snippet, etc.
        
    Returns:
        Human-readable summary for LLM parsing
    """
    if not emails:
        return "No flight/hotel confirmation emails found."
    
    output = []
    output.append(f"Found {len(emails)} potential travel emails:\n")
    
    for i, email in enumerate(emails, 1):
        output.append(f"--- Email {i} ---")
        output.append(f"From: {email.get('from', 'Unknown')}")
        output.append(f"Subject: {email.get('subject', 'No subject')}")
        output.append(f"Date: {email.get('date', 'Unknown')}")
        
        # Include snippet if available
        if email.get("snippet"):
            snippet = email["snippet"][:300]
            if len(email.get("snippet", "")) > 300:
                snippet += "..."
            output.append(f"Preview: {snippet}")
        
        # Include body excerpt if available
        if email.get("body"):
            body = email["body"][:1000]
            if len(email.get("body", "")) > 1000:
                body += "..."
            output.append(f"Body excerpt: {body}")
        
        output.append(f"Message ID: {email.get('id', 'Unknown')}")
        output.append("")
    
    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--query":
        query = build_gmail_query()
        print(json.dumps(query, indent=2))
    else:
        print("Gmail Ingestion Script")
        print("=" * 40)
        print("\nThis script prepares Gmail queries for travel email extraction.")
        print("\nUsage:")
        print("  --query    Output the Gmail API query parameters")
        print("\nThe actual API call is made by extract_trips.py through the Zo API.")
        print("\nFlight queries:")
        for q in FLIGHT_QUERIES:
            print(f"  - {q[:60]}...")
        print("\nHotel queries:")
        for q in HOTEL_QUERIES:
            print(f"  - {q[:60]}...")

