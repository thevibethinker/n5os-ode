#!/usr/bin/env python3
"""
Luma Event Scraper - Discovers public events from lu.ma city pages.

Usage:
    python3 N5/scripts/luma_scraper.py --city nyc
    python3 N5/scripts/luma_scraper.py --city nyc --days 14
"""

import argparse
import asyncio
import json
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"

CITY_URLS = {
    "nyc": "https://lu.ma/nyc",
    "sf": "https://lu.ma/sf",
    "la": "https://lu.ma/la",
    "austin": "https://lu.ma/austin",
    "miami": "https://lu.ma/miami",
    "london": "https://lu.ma/london",
}

def init_db():
    """Initialize SQLite database for events."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT,
            event_time TEXT,
            event_datetime TEXT,
            venue_name TEXT,
            venue_address TEXT,
            city TEXT,
            organizers TEXT,
            price TEXT,
            attendee_count INTEGER,
            status TEXT,
            cover_image_url TEXT,
            scraped_at TEXT NOT NULL,
            scored_at TEXT,
            score REAL,
            score_rationale TEXT,
            digest_sent_at TEXT,
            approved_at TEXT,
            rejected_at TEXT,
            registered_at TEXT,
            registration_status TEXT,
            gcal_event_id TEXT,
            raw_data TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS organizers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            luma_profile_url TEXT,
            event_id TEXT,
            discovered_at TEXT NOT NULL,
            enriched_at TEXT,
            crm_profile_id TEXT,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_datetime)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_city ON events(city)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

async def scrape_luma_events(city: str = "nyc", days_ahead: int = 21) -> list[dict]:
    """
    Scrape events from Luma city page using Playwright.
    
    Args:
        city: City code (nyc, sf, la, etc.)
        days_ahead: How many days ahead to look for events
        
    Returns:
        List of event dictionaries
    """
    from playwright.async_api import async_playwright
    
    url = CITY_URLS.get(city, f"https://lu.ma/{city}")
    logger.info(f"Scraping events from {url} (next {days_ahead} days)")
    
    events = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1024},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Extract from __NEXT_DATA__ script tag
            next_data = await page.evaluate("""
                () => {
                    const el = document.getElementById('__NEXT_DATA__');
                    return el ? el.textContent : null;
                }
            """)
            
            if next_data:
                import json as json_module
                data = json_module.loads(next_data)
                page_props = data.get("props", {}).get("pageProps", {})
                initial_data = page_props.get("initialData", {}).get("data", {})
                
                # Get both regular and featured events
                raw_events = initial_data.get("events", [])
                featured_events = initial_data.get("featured_events", [])
                
                logger.info(f"Found {len(raw_events)} regular events, {len(featured_events)} featured")
                
                all_raw = raw_events + featured_events
                
                for ev in all_raw:
                    parsed = parse_structured_event(ev, city)
                    if parsed:
                        events.append(parsed)
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise
        finally:
            await browser.close()
    
    # Filter to events within date range
    cutoff = datetime.now() + timedelta(days=days_ahead)
    now = datetime.now()
    filtered = []
    
    for ev in events:
        if ev.get("event_datetime"):
            try:
                ev_dt_str = ev["event_datetime"].replace("Z", "+00:00")
                ev_dt = datetime.fromisoformat(ev_dt_str)
                ev_dt_naive = ev_dt.replace(tzinfo=None)
                # Include if event is in the future and within cutoff
                if now <= ev_dt_naive <= cutoff:
                    filtered.append(ev)
            except Exception as e:
                logger.warning(f"Date parse error for {ev.get('title')}: {e}")
                filtered.append(ev)  # Include if we can't parse date
        else:
            filtered.append(ev)
    
    logger.info(f"Filtered to {len(filtered)} events within {days_ahead} days")
    return filtered

def parse_structured_event(data: dict, city: str) -> Optional[dict]:
    """Parse event from Luma's __NEXT_DATA__ structure."""
    try:
        # The structure has api_id at top level and event details nested under 'event'
        event_id = data.get("api_id", "")
        event_data = data.get("event", {})
        calendar_data = data.get("calendar", {})
        hosts_data = data.get("hosts", [])
        
        # Build event URL
        url_slug = event_data.get("url", event_id)
        event_url = f"https://lu.ma/{url_slug}"
        
        # Extract geo info
        geo_info = event_data.get("geo_address_info", {})
        venue_name = geo_info.get("full_address") or geo_info.get("place_name") or ""
        venue_city_state = geo_info.get("city_state", "")
        sublocality = geo_info.get("sublocality", "")
        
        # Build venue string
        if sublocality and venue_city_state:
            venue_display = f"{sublocality}, {venue_city_state}"
        elif venue_city_state:
            venue_display = venue_city_state
        else:
            venue_display = venue_name
        
        # Extract start time
        start_at = event_data.get("start_at", "")
        event_date = start_at[:10] if start_at else ""
        event_time = start_at[11:16] if start_at and len(start_at) > 16 else ""
        
        # Extract organizer/calendar info
        organizers = []
        
        # Add hosts if available
        for host in hosts_data:
            organizers.append({
                "name": host.get("name", ""),
                "url": host.get("username") or host.get("api_id", ""),
                "avatar": host.get("avatar_url", ""),
            })
        
        # Add calendar as organizer if no hosts
        if not organizers and calendar_data:
            organizers.append({
                "name": calendar_data.get("name", ""),
                "url": calendar_data.get("slug", ""),
                "avatar": calendar_data.get("avatar_url", ""),
            })
        
        # Determine price (Luma doesn't always include price in list view)
        price = "Free"  # Default assumption for public events
        
        # Get attendee/guest info
        attendee_count = data.get("num_guests") or data.get("guest_count") or 0
        
        # Determine status
        status = "available"
        if event_data.get("waitlist_enabled"):
            status = "waitlist"
        if event_data.get("hide_rsvp"):
            status = "rsvp_hidden"
        
        return {
            "id": event_id,
            "url": event_url,
            "title": event_data.get("name", ""),
            "description": "",  # Not in list view, needs detail fetch
            "event_date": event_date,
            "event_time": event_time,
            "event_datetime": start_at,
            "venue_name": venue_display,
            "venue_address": venue_name,
            "city": city,
            "organizers": json.dumps(organizers),
            "price": price,
            "attendee_count": attendee_count,
            "status": status,
            "cover_image_url": event_data.get("cover_url", ""),
            "scraped_at": datetime.utcnow().isoformat(),
            "raw_data": json.dumps(data),
        }
    except Exception as e:
        logger.warning(f"Error parsing structured event: {e}")
        return None

def extract_organizers(data: dict) -> list[dict]:
    """Extract organizer information from event data."""
    organizers = []
    
    # Check various possible locations for host info
    hosts = data.get("hosts") or data.get("event", {}).get("hosts") or []
    for host in hosts:
        organizers.append({
            "name": host.get("name", ""),
            "url": host.get("url") or host.get("api_id", ""),
        })
    
    # Check for single host
    host = data.get("host") or data.get("event", {}).get("host")
    if host and isinstance(host, dict):
        organizers.append({
            "name": host.get("name", ""),
            "url": host.get("url", ""),
        })
    
    return organizers

def extract_price(data: dict) -> str:
    """Extract price info from event data."""
    event = data.get("event", data)
    
    if event.get("is_free"):
        return "Free"
    
    ticket_info = event.get("ticket_info") or {}
    if ticket_info.get("price"):
        return f"${ticket_info['price']}"
    
    min_price = data.get("min_ticket_price")
    if min_price:
        return f"${min_price}" if min_price > 0 else "Free"
    
    return "Unknown"

async def parse_events_from_dom(page, city: str) -> list[dict]:
    """Parse events directly from DOM when structured data unavailable."""
    events = []
    
    # Get all event-like links
    links = await page.evaluate("""
        () => {
            const results = [];
            const seen = new Set();
            
            // Find all links that look like event URLs
            document.querySelectorAll('a').forEach(a => {
                const href = a.href;
                if (href && href.includes('lu.ma/') && !href.includes('/nyc') && !href.includes('/sf')) {
                    // Extract event slug
                    const match = href.match(/lu\\.ma\\/([a-zA-Z0-9-]+)/);
                    if (match && match[1] && !seen.has(match[1])) {
                        seen.add(match[1]);
                        
                        // Try to get surrounding context
                        const card = a.closest('[class*="event"]') || a.closest('[class*="card"]') || a;
                        const title = card.querySelector('h2, h3, [class*="title"]')?.textContent?.trim() || 
                                     a.textContent?.trim() || match[1];
                        
                        results.push({
                            id: match[1],
                            url: href,
                            title: title.substring(0, 200),
                        });
                    }
                }
            });
            
            return results;
        }
    """)
    
    for link in links[:50]:  # Limit to 50 events
        events.append({
            "id": link["id"],
            "url": link["url"],
            "title": link["title"],
            "description": "",
            "event_date": "",
            "event_time": "",
            "event_datetime": "",
            "venue_name": "",
            "venue_address": "",
            "city": city,
            "organizers": "[]",
            "price": "Unknown",
            "attendee_count": 0,
            "status": "unknown",
            "cover_image_url": "",
            "scraped_at": datetime.utcnow().isoformat(),
            "raw_data": json.dumps(link),
        })
    
    return events

def save_events(events: list[dict]):
    """Save events to database, updating existing ones."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for ev in events:
        # Check if exists
        cursor.execute("SELECT id FROM events WHERE id = ?", (ev["id"],))
        exists = cursor.fetchone()
        
        if exists:
            # Update (but preserve approval status)
            cursor.execute("""
                UPDATE events SET
                    title = ?, description = ?, event_date = ?, event_time = ?,
                    event_datetime = ?, venue_name = ?, venue_address = ?,
                    organizers = ?, price = ?, attendee_count = ?, status = ?,
                    cover_image_url = ?, scraped_at = ?, raw_data = ?
                WHERE id = ? AND approved_at IS NULL AND rejected_at IS NULL
            """, (
                ev["title"], ev["description"], ev["event_date"], ev["event_time"],
                ev["event_datetime"], ev["venue_name"], ev["venue_address"],
                ev["organizers"], ev["price"], ev["attendee_count"], ev["status"],
                ev["cover_image_url"], ev["scraped_at"], ev["raw_data"], ev["id"]
            ))
            if cursor.rowcount > 0:
                updated += 1
        else:
            cursor.execute("""
                INSERT INTO events (
                    id, url, title, description, event_date, event_time,
                    event_datetime, venue_name, venue_address, city, organizers,
                    price, attendee_count, status, cover_image_url, scraped_at, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ev["id"], ev["url"], ev["title"], ev["description"],
                ev["event_date"], ev["event_time"], ev["event_datetime"],
                ev["venue_name"], ev["venue_address"], ev["city"], ev["organizers"],
                ev["price"], ev["attendee_count"], ev["status"], ev["cover_image_url"],
                ev["scraped_at"], ev["raw_data"]
            ))
            inserted += 1
    
    # Save organizers
    for ev in events:
        try:
            organizers = json.loads(ev.get("organizers", "[]"))
            for org in organizers:
                if org.get("name"):
                    cursor.execute("""
                        INSERT OR IGNORE INTO organizers (name, luma_profile_url, event_id, discovered_at)
                        VALUES (?, ?, ?, ?)
                    """, (org["name"], org.get("url", ""), ev["id"], datetime.utcnow().isoformat()))
        except:
            pass
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved events: {inserted} inserted, {updated} updated")
    return {"inserted": inserted, "updated": updated}

async def enrich_event_details(event_id: str) -> dict:
    """Fetch full details for a single event by visiting its page."""
    from playwright.async_api import async_playwright
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Event not found"}
    
    url = row[0]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Extract detailed info from event page
            details = await page.evaluate("""
                () => {
                    const getText = (sel) => document.querySelector(sel)?.textContent?.trim() || '';
                    
                    return {
                        title: getText('h1'),
                        description: getText('[class*="description"]') || getText('article'),
                        date_time: getText('[class*="date"]') || getText('time'),
                        venue: getText('[class*="location"]') || getText('[class*="venue"]'),
                        organizer: getText('[class*="host"]') || getText('[class*="organizer"]'),
                        price: getText('[class*="price"]') || getText('[class*="ticket"]'),
                        attendees: getText('[class*="attendee"]') || getText('[class*="guest"]'),
                    };
                }
            """)
            
            return details
            
        finally:
            await browser.close()

async def scrape_single_event(url: str) -> Optional[dict]:
    """
    Scrape a single Luma event page.
    Useful for events discovered via email that aren't on the city page.
    """
    from playwright.async_api import async_playwright
    
    logger.info(f"Scraping single event: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1024},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Extract from __NEXT_DATA__ script tag
            next_data = await page.evaluate("""
                () => {
                    const el = document.getElementById('__NEXT_DATA__');
                    return el ? el.textContent : null;
                }
            """)
            
            if next_data:
                import json as json_module
                data = json_module.loads(next_data)
                page_props = data.get("props", {}).get("pageProps", {})
                
                # Try to find event data in various places
                event_data = page_props.get("initialData", {})
                
                # If initialData has 'data' key (common in some pages)
                if "data" in page_props.get("initialData", {}):
                     event_data = page_props["initialData"]["data"]

                # If we found something that looks like an event
                if event_data.get("event") or event_data.get("api_id"):
                    # Use "nyc" as default city or try to extract from geo_address_info
                    city = "nyc" # Default fallback
                    geo = event_data.get("event", {}).get("geo_address_info", {})
                    if "city" in geo:
                        city = geo["city"].lower()
                    
                    parsed = parse_structured_event(event_data, city)
                    return parsed
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping single event {url}: {e}")
            return None
        finally:
            await browser.close()

def get_pending_events(city: str = None, limit: int = 20) -> list[dict]:
    """Get events that haven't been sent in a digest yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM events
        WHERE digest_sent_at IS NULL
        AND rejected_at IS NULL
        AND event_datetime >= datetime('now')
    """
    params = []
    
    if city:
        query += " AND city = ?"
        params.append(city)
    
    query += " ORDER BY event_datetime ASC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

async def main():
    parser = argparse.ArgumentParser(description="Scrape Luma events")
    parser.add_argument("--city", default="nyc", help="City code (nyc, sf, la, etc.)")
    parser.add_argument("--days", type=int, default=21, help="Days ahead to look")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    parser.add_argument("--list-pending", action="store_true", help="List pending events")
    args = parser.parse_args()
    
    init_db()
    
    if args.init_db:
        logger.info("Database initialized. Exiting.")
        return
    
    if args.list_pending:
        events = get_pending_events(args.city)
        print(json.dumps(events, indent=2, default=str))
        return
    
    events = await scrape_luma_events(args.city, args.days)
    result = save_events(events)
    
    print(json.dumps({
        "city": args.city,
        "days_ahead": args.days,
        "events_found": len(events),
        **result
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())






