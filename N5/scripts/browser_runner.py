#!/usr/bin/env python3
"""
Playwright-driven browser runner for Luma tasks.
Executes distinct tasks: discovery, inspection, and registration (form interaction).
"""
import argparse
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page, BrowserContext

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("luma_runner")

# Common selectors
EVENT_CARD_SELECTOR = "a[href^='/']"  # Broad, we filter later
REGISTER_BUTTON_TEXTS = ["Register", "Join Waitlist", "Request to Join", "Get Tickets"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Playwright task for Luma automation")
    parser.add_argument("--job-file", required=True, help="Path to a JSON file describing the task")
    parser.add_argument("--output", required=True, help="Path to write the JSON result")
    parser.add_argument("--cookies-file", help="Path to playwright storage state (cookies)")
    return parser.parse_args()


def load_job(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Job file not found: {path}")
    with path.open() as handle:
        return json.load(handle)


def sanitize_url(url: str) -> str:
    """Ensure URL is absolute."""
    if url.startswith("/"):
        return f"https://lu.ma{url}"
    return url


def is_event_url(url: str) -> bool:
    """Heuristic to check if a URL looks like a Luma event."""
    if not url:
        return False
    # Exclude common non-event paths
    exclude = ["/signin", "/create", "/discover", "/calendar", "/explore", "/home", "/me"]
    for ex in exclude:
        if url.startswith(ex):
            return False
    # Luma events are often /slug or /event/slug
    # But /sf is a city.
    # Heuristic: simple slugs are hard to distinguish from cities without visiting.
    # We will trust the extraction logic to filter obviously wrong ones.
    return True


async def list_city_events(page: Page, city: str) -> List[Dict[str, Any]]:
    """Scrape event cards from a city discovery page."""
    url = f"https://lu.ma/{city}"
    logger.info(f"Navigating to {url}")
    
    await page.goto(url, wait_until="networkidle", timeout=45_000)
    await page.wait_for_timeout(2_000)
    
    # Scroll to load more
    for _ in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1_000)

    # Extract data using evaluation for speed and access to DOM props
    events = await page.evaluate("""
        () => {
            const cards = [];
            // Luma usually puts event info in anchor tags or divs wrapping them
            // We look for any anchor that seems to be an event
            const links = Array.from(document.querySelectorAll('a'));
            
            links.forEach(a => {
                const href = a.getAttribute('href');
                if (!href || href.startsWith('/signin') || href.startsWith('/create')) return;
                
                // Try to find title and time inside
                const titleEl = a.querySelector('h3') || a.querySelector('div[class*="title"]');
                const timeEl = a.querySelector('time') || a.querySelector('div[class*="time"]');
                
                if (titleEl) {
                    cards.push({
                        url: href,
                        title: titleEl.innerText,
                        time: timeEl ? timeEl.innerText : null
                    });
                }
            });
            return cards;
        }
    """)
    
    # Post-process
    results = []
    seen_urls = set()
    for e in events:
        full_url = sanitize_url(e['url'])
        if full_url not in seen_urls:
            e['url'] = full_url
            results.append(e)
            seen_urls.add(full_url)
            
    logger.info(f"Found {len(results)} events")
    return results


async def inspect_event(page: Page, url: str) -> Dict[str, Any]:
    """Extract detailed metadata from an event page."""
    logger.info(f"Inspecting event: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    # Wait for hydration
    await page.wait_for_timeout(2_000)
    
    metadata = await page.evaluate("""
        () => {
            const getTxt = (sel) => document.querySelector(sel)?.innerText?.trim() || null;
            return {
                title: getTxt('h1'),
                host: getTxt('[data-id="event-host"]'), // Hypothetical selector, fallback needed
                location: getTxt('.location-name') || getTxt('[data-id="location-row"]'),
                time: getTxt('.time-row') || getTxt('[data-id="time-row"]'),
                description: getTxt('.description') || getTxt('[data-id="event-description"]'),
                price: getTxt('.price') || "Free"
            };
        }
    """)
    
    # Check registration status button
    button_text = "Unknown"
    for text in REGISTER_BUTTON_TEXTS:
        btn = page.get_by_role("button", name=text)
        if await btn.count() > 0 and await btn.is_visible():
            button_text = text
            break
            
    return {
        "url": url,
        "metadata": metadata,
        "action_button": button_text
    }


async def register_for_event(page: Page, url: str, answers: Dict[str, str]) -> Dict[str, Any]:
    """Attempt to register or fetch form questions."""
    logger.info(f"Attempting registration for {url}")
    await page.goto(url, wait_until="networkidle", timeout=45_000)
    await page.wait_for_timeout(2_000)

    # 1. Find and Click Register Button
    clicked = False
    for text in REGISTER_BUTTON_TEXTS:
        btn = page.get_by_role("button", name=text)
        if await btn.count() > 0 and await btn.is_visible():
            logger.info(f"Clicking button: {text}")
            await btn.first.click()
            clicked = True
            break
    
    if not clicked:
        return {"status": "failed", "reason": "no_register_button_found"}

    # 2. Wait for Modal or Navigation
    await page.wait_for_timeout(3_000)
    
    # 3. Check for Login Wall
    # Luma often shows a modal "Sign in to register" or redirects to /signin
    if "/signin" in page.url:
        return {"status": "halted", "reason": "login_required", "url": page.url}
    
    signin_header = page.get_by_text("Sign in")
    if await signin_header.count() > 0 and await signin_header.is_visible():
         return {"status": "halted", "reason": "login_required_modal"}

    # 4. Scrape Form Questions
    # Look for label elements and their associated inputs
    form_data = await page.evaluate("""
        () => {
            const fields = [];
            document.querySelectorAll('div[class*="field"], div.input-group').forEach(div => {
                const label = div.querySelector('label')?.innerText;
                const input = div.querySelector('input, textarea, select');
                if (label && input) {
                    fields.push({
                        label: label,
                        name: input.name || input.id,
                        type: input.type || input.tagName.toLowerCase(),
                        required: input.required
                    });
                }
            });
            return fields;
        }
    """)
    
    missing_info = []
    filled_fields = []

    # 5. Attempt to Fill
    for field in form_data:
        label = field['label']
        # Simple fuzzy match for answer key
        # In production, this would be an LLM call or fuzzy matcher
        answer = None
        for key, val in answers.items():
            if key.lower() in label.lower():
                answer = val
                break
        
        if answer:
            # Mechanical fill
            # Simplified: just fill text inputs for now
            if field['type'] in ['text', 'email', 'tel', 'textarea']:
                selector = f"[name='{field['name']}']" if field['name'] else "input" # fallback unsafe
                await page.fill(selector, answer)
                filled_fields.append(label)
        elif field['required']:
            missing_info.append(field)

    if missing_info:
        return {
            "status": "needs_info",
            "missing_fields": missing_info,
            "filled_fields": filled_fields
        }

    # 6. Submit (Dry Run for now)
    # We won't actually click the final submit in this version until we trust it.
    # submit_btn = page.get_by_role("button", name="Complete")
    # await submit_btn.click()
    
    return {
        "status": "ready_to_submit",
        "filled_fields": filled_fields,
        "note": "Submission disabled in dry-run mode"
    }


async def main() -> None:
    args = parse_args()
    job = load_job(Path(args.job_file))
    task = job.get("task")
    params = job.get("params", {})
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        # Load storage state if provided (cookies)
        context_args = {}
        if args.cookies_file and Path(args.cookies_file).exists():
            context_args["storage_state"] = args.cookies_file
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        
        result = {}
        try:
            if task == "luma_list_city_events":
                city = params.get("city", "sf")
                result = await list_city_events(page, city)
            elif task == "luma_inspect_event":
                url = params.get("url")
                result = await inspect_event(page, url)
            elif task == "luma_register_for_event":
                url = params.get("url")
                answers = params.get("answers", {})
                result = await register_for_event(page, url, answers)
            else:
                raise ValueError(f"Unknown task: {task}")
        except Exception as e:
            logger.exception("Task failed")
            result = {"error": str(e)}
        finally:
            await browser.close()

    with Path(args.output).open("w") as handle:
        json.dump({"task": task, "result": result}, handle, indent=2)


if __name__ == "__main__":
    asyncio.run(main())


