#!/usr/bin/env python3
"""
Luma Email Discovery
Scans Gmail for Luma event links in newsletters/listservs/event emails.

Usage:
    python3 N5/scripts/luma_email_discovery.py --days 3
"""

import argparse
import asyncio
import base64
import json
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# Import luma_scraper for scraping and saving
import sys
sys.path.append(str(Path(__file__).parent))
from luma_scraper import scrape_single_event, save_events, DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Gmail search query
# Looking for emails with specific labels or content
SEARCH_QUERY = 'label:newsletters OR label:listservs OR label:events OR "lu.ma/event"'

def get_gmail_service():
    """Get authenticated Gmail service."""
    # This is a placeholder. In a real script, we'd use the N5 Gmail integration tools
    # or the gmail_monitor.py approach. 
    # Since we are an agent, we should use the `use_app_gmail` tool if running interactively,
    # but as a script, we need to use the stored credentials or the Pipedream integration.
    # For now, we will simulate the behavior or assume we can use the gmail_tracker.py logic.
    
    # Actually, the best way is to use the `gmail_monitor.py` logic if available, 
    # or rely on the `use_app_gmail` tool from the agent context. 
    # But this script needs to run standalone.
    
    # Let's assume we can use the Pipedream integration via an HTTP request 
    # if we had a webhook, but we don't.
    
    # We will use the python gmail client if credentials exist, 
    # similar to how `gmail_monitor.py` likely works.
    # Let's check `gmail_monitor.py` imports.
    pass

# Mocking Gmail service for now since I don't have direct access to 'google.oauth2' 
# inside this restricted environment without setup.
# However, I can use the 'use_app_gmail' tool in the agent to FETCH emails, 
# and pass them to this script? 
# OR, I can write this script to expect a JSON input of emails (from the agent).

# BETTER APPROACH for Agentic Workflow:
# The agent (me) calls `use_app_gmail` to get emails.
# The agent saves them to a file.
# This script reads the file and processes them.
# This avoids auth complexity inside the script.

def extract_luma_links(html_content: str) -> set[str]:
    """Extract lu.ma event links from HTML content."""
    links = set()
    # Regex for lu.ma links
    # Matches https://lu.ma/ followed by alphanumeric/dashes
    # Excludes /user, /calendar, /nyc, etc. if we can.
    
    patterns = [
        r'https?://lu\.ma/([\w-]+)',
        r'https?://www\.lu\.ma/([\w-]+)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, html_content)
        for match in matches:
            slug = match.group(1)
            full_url = f"https://lu.ma/{slug}"
            
            # Filter out known non-event pages
            if slug in ["nyc", "sf", "la", "london", "signin", "signup", "home", "create"]:
                continue
            if slug.startswith("user-") or slug.startswith("calendar-"):
                continue
                
            links.add(full_url)
            
    return links

async def process_emails(email_file: Path):
    """Process emails from a JSON file."""
    if not email_file.exists():
        logger.error(f"Email file not found: {email_file}")
        return

    with open(email_file, 'r') as f:
        emails = json.load(f)
    
    logger.info(f"Scanning {len(emails)} emails for Luma links...")
    
    found_urls = set()
    for email in emails:
        # Check body (snippet or full payload)
        content = email.get("snippet", "") + " " + email.get("body", "")
        links = extract_luma_links(content)
        found_urls.update(links)
    
    logger.info(f"Found {len(found_urls)} unique Luma URLs.")
    
    # Filter out events already in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM events")
    existing_urls = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    new_urls = found_urls - existing_urls
    logger.info(f"New events to scrape: {len(new_urls)}")
    
    scraped_events = []
    for url in new_urls:
        event = await scrape_single_event(url)
        if event:
            # Tag source
            raw = json.loads(event["raw_data"])
            raw["_discovery_source"] = "email_scan"
            event["raw_data"] = json.dumps(raw)
            scraped_events.append(event)
            logger.info(f"✓ Scraped: {event['title']}")
        else:
            logger.warning(f"✗ Failed to scrape: {url}")
            
    if scraped_events:
        save_events(scraped_events)
        logger.info(f"Saved {len(scraped_events)} new events to DB.")
    else:
        logger.info("No new events saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email-file", required=True, help="JSON file containing emails to scan")
    args = parser.parse_args()
    
    asyncio.run(process_emails(Path(args.email_file)))

