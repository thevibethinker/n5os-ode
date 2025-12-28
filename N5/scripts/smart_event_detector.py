#!/usr/bin/env python3
"""
Smart Event Detector (Tier 2)
Scans ALL recent emails for event signals from sources NOT on the allowlist.
Catches events you might otherwise miss.

Usage:
    python3 N5/scripts/smart_event_detector.py [--days 2] [--dry-run]
"""

import argparse
import json
import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("smart_event_detector")

N5_ROOT = Path("/home/workspace/N5")
CONFIG_FILE = N5_ROOT / "config" / "event_sources.json"
OUTPUT_FILE = N5_ROOT / "data" / "detected_events.json"

# URL patterns for each platform
EVENT_URL_PATTERNS = {
    "luma": [
        r"https?://lu\.ma/[a-zA-Z0-9_-]+",
        r"https?://luma\.com/join/[a-zA-Z0-9_-]+",
    ],
    "partiful": [
        r"https?://partiful\.com/e/[a-zA-Z0-9]+",
    ],
    "supermomos": [
        r"https?://(?:www\.)?supermomos\.com/events/[a-zA-Z0-9_-]+",
    ],
    "eventbrite": [
        r"https?://(?:www\.)?eventbrite\.com/e/[a-zA-Z0-9_-]+-\d+",
    ],
    "meetup": [
        r"https?://(?:www\.)?meetup\.com/[^/\s]+/events/\d+",
    ],
}

# Gmail search terms for each platform
GMAIL_SEARCH_TERMS = [
    '"lu.ma"',
    '"partiful.com/e/"',
    '"supermomos.com/events"',
    '"eventbrite.com/e/"',
    '"meetup.com/events"',
]


def load_allowlist() -> list[str]:
    """Load current allowlist senders."""
    if not CONFIG_FILE.exists():
        return []
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return config.get("senders", [])
    except Exception as e:
        logger.error(f"Error loading allowlist: {e}")
        return []


def build_gmail_query(days: int = 2) -> str:
    """
    Build Gmail query that:
    1. Matches emails containing event platform URLs
    2. Excludes senders already on the allowlist
    """
    # Platform terms (OR'd together)
    platform_query = " OR ".join(GMAIL_SEARCH_TERMS)
    
    # Exclusion terms for allowlisted senders
    allowlist = load_allowlist()
    exclusions = " ".join([f"-from:{sender}" for sender in allowlist])
    
    # Time constraint
    time_constraint = f"newer_than:{days}d"
    
    # Build final query
    if exclusions:
        query = f"({platform_query}) {time_constraint} {exclusions}"
    else:
        query = f"({platform_query}) {time_constraint}"
    
    return query


def extract_event_urls(text: str) -> list[dict]:
    """Extract all event URLs from text, categorized by platform."""
    results = []
    seen_urls = set()
    
    for platform, patterns in EVENT_URL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for url in matches:
                # Clean URL (remove trailing punctuation, query params for dedup)
                clean_url = re.sub(r'[.,;!?)\]>]+$', '', url)
                base_url = clean_url.split('?')[0]
                
                if base_url not in seen_urls:
                    seen_urls.add(base_url)
                    results.append({
                        "url": clean_url,
                        "platform": platform,
                    })
    
    return results


def extract_sender_from_email(email_data: dict) -> dict:
    """Extract sender info from email metadata."""
    # Handle different possible formats from Gmail API
    sender = email_data.get("from", email_data.get("sender", ""))
    
    # Parse "Name <email@domain.com>" format
    match = re.match(r'^([^<]*)<([^>]+)>$', sender.strip())
    if match:
        name = match.group(1).strip().strip('"')
        email = match.group(2).strip()
    else:
        name = ""
        email = sender.strip()
    
    return {
        "name": name,
        "email": email,
    }


def process_emails(emails: list[dict]) -> list[dict]:
    """Process list of emails and extract event data."""
    detected = []
    
    for email in emails:
        # Get email body/snippet
        body = email.get("body", email.get("snippet", email.get("text", "")))
        subject = email.get("subject", "")
        
        # Combine for URL extraction
        full_text = f"{subject} {body}"
        
        # Extract URLs
        urls = extract_event_urls(full_text)
        if not urls:
            continue
        
        # Extract sender
        sender = extract_sender_from_email(email)
        
        # Build detection record
        detected.append({
            "sender": sender,
            "subject": subject,
            "urls": urls,
            "message_id": email.get("id", email.get("message_id", "")),
            "detected_at": datetime.now().isoformat(),
        })
    
    return detected


def save_detections(detections: list[dict], append: bool = True):
    """Save detected events to output file."""
    existing = []
    
    if append and OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                existing = json.load(f)
        except Exception:
            existing = []
    
    # Merge, avoiding duplicates by message_id
    existing_ids = {d.get("message_id") for d in existing}
    new_detections = [d for d in detections if d.get("message_id") not in existing_ids]
    
    combined = existing + new_detections
    
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(combined, f, indent=2)
    
    logger.info(f"Saved {len(new_detections)} new detections ({len(combined)} total)")
    return new_detections


def main():
    parser = argparse.ArgumentParser(description="Smart Event Detector (Tier 2)")
    parser.add_argument("--days", type=int, default=2, help="Look back N days (default: 2)")
    parser.add_argument("--dry-run", action="store_true", help="Print query only, don't process")
    parser.add_argument("--email-file", type=str, help="Process emails from JSON file instead of querying")
    parser.add_argument("--print-query", action="store_true", help="Print Gmail query to stdout")
    args = parser.parse_args()
    
    if args.print_query or args.dry_run:
        query = build_gmail_query(args.days)
        print(query)
        if args.dry_run:
            return
    
    if args.email_file:
        # Process from file (for agent integration)
        email_path = Path(args.email_file)
        if not email_path.exists():
            logger.error(f"Email file not found: {email_path}")
            return
        
        with open(email_path) as f:
            emails = json.load(f)
        
        if isinstance(emails, dict):
            # Handle wrapped response format
            emails = emails.get("messages", emails.get("result", [emails]))
        
        detections = process_emails(emails)
        new = save_detections(detections)
        
        # Summary
        platforms = {}
        for d in new:
            for url in d.get("urls", []):
                p = url.get("platform", "unknown")
                platforms[p] = platforms.get(p, 0) + 1
        
        print(f"Detected {len(new)} new event emails:")
        for platform, count in sorted(platforms.items()):
            print(f"  - {platform}: {count}")
    else:
        # Just print query for agent to use
        query = build_gmail_query(args.days)
        print(query)


if __name__ == "__main__":
    main()

