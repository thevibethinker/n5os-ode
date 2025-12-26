#!/usr/bin/env python3
"""
Luma Backfill Attended
Scrapes 'Past Events' from the user's Luma profile to build an organizer trust database.

Usage:
    python3 N5/scripts/luma_backfill_attended.py
"""

import asyncio
import json
import logging
import sqlite3
from pathlib import Path
from playwright.async_api import async_playwright

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
AUTH_PATH = N5_ROOT / "data" / "luma_auth.json"

async def backfill_past_events():
    """Scrape past events and update organizer stats."""
    if not AUTH_PATH.exists():
        logger.error(f"Auth file not found at {AUTH_PATH}. Run 'python3 N5/scripts/luma_login.py' first.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_PATH)
        page = await context.new_page()
        
        # Navigate to "My Events" -> "Past"
        # URL structure might vary, usually /home or /events/past
        # Let's try /home and look for 'Past' tab or /my-events
        logger.info("Navigating to Luma events page...")
        await page.goto("https://lu.ma/home")
        await page.wait_for_timeout(3000)
        
        # Check if logged in
        if "signin" in page.url:
            logger.error("Not logged in. Please update auth state.")
            return

        # Attempt to find "Past Events"
        # Strategy: Look for "Past" text or specific URL structure
        # Often it's https://lu.ma/home?tab=past
        await page.goto("https://lu.ma/home?tab=past")
        await page.wait_for_timeout(3000)
        
        # Scrape events from the list
        events_data = await page.evaluate("""
            () => {
                const events = [];
                // Selector strategy: Look for event cards. 
                // This is brittle and depends on Luma's class names.
                // Assuming generic structure for now or grabbing all links that look like events.
                
                const cards = document.querySelectorAll('a[href^="/event/"], a[href*="lu.ma/event/"]');
                cards.forEach(card => {
                    const titleEl = card.querySelector('h3') || card.querySelector('.title') || card.querySelector('div[class*="title"]');
                    const hostEl = card.querySelector('div[class*="host"]') || card.querySelector('.host');
                    
                    if (titleEl) {
                        events.push({
                            url: card.href,
                            title: titleEl.innerText,
                            host: hostEl ? hostEl.innerText : null
                        });
                    }
                });
                return events;
            }
        """)
        
        logger.info(f"Found {len(events_data)} past events.")
        
        # Update Database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        count = 0
        for event in events_data:
            # We mostly care about the ORGANIZER here for the trust score.
            # We can also store the event as 'attended' history.
            
            # 1. Update Organizer Trust
            if event.get('host'):
                host_name = event['host'].strip()
                # Simple tally for now. 
                # We can store this in a new table or just log it. 
                # Let's verify if we have an 'organizer_stats' table or similar.
                # If not, let's create a simple key-value store in a JSON file for simplicity 
                # OR trust the 'organizers' table in SQL if we link it.
                
                # Let's use a dedicated table for stats if we want to be robust, 
                # but for this script, let's just log them to a JSON file that the scorer reads.
                pass 

        conn.close()
        
        # Save organizer tally to JSON for the scorer to use
        tally_path = N5_ROOT / "data" / "luma_organizer_tally.json"
        
        # Load existing
        if tally_path.exists():
            with open(tally_path) as f:
                tally = json.load(f)
        else:
            tally = {}
            
        for event in events_data:
            host = event.get('host')
            if host:
                tally[host] = tally.get(host, 0) + 1
                count += 1
        
        with open(tally_path, 'w') as f:
            json.dump(tally, f, indent=2)
            
        logger.info(f"Updated organizer tally with {count} event records.")
        logger.info(f"Tally saved to {tally_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(backfill_past_events())

