#!/usr/bin/env python3
"""
Luma Registration Worker
Auto-registers for approved events with Human-in-the-Loop drafting.

Usage:
    # 1. Analyze and create draft
    python3 N5/scripts/luma_register.py --event-id <ID> --analyze

    # 2. Approve and submit (after reviewing draft)
    python3 N5/scripts/luma_register.py --event-id <ID> --submit

    # 3. Process all approved events (generates drafts for review)
    python3 N5/scripts/luma_register.py --process-queue
"""

import argparse
import asyncio
import json
import logging
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
DRAFTS_DIR = N5_ROOT / "data" / "registration_drafts"
USER_DATA_DIR = N5_ROOT / "data" / "playwright_luma_context"

DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

async def get_event_url(event_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def update_registration_status(event_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE events SET registration_status = ? WHERE id = ?", (status, event_id))
    conn.commit()
    conn.close()

async def ensure_login(page):
    """Check if logged in, prompt if not."""
    try:
        # Check for avatar or 'You' in nav
        await page.wait_for_selector('img[alt*="Avatar"]', timeout=3000)
        logger.info("✓ Logged in")
        return True
    except:
        logger.warning("! Not logged in. Please run with --login-interactive to set up session.")
        return False

async def generate_answers(questions: list[str]) -> dict:
    """
    Generate answers for form questions using Content Library.
    """
    import sys
    sys.path.append("/home/workspace/N5/scripts")
    try:
        from content_library import ContentLibrary
        lib = ContentLibrary()
    except ImportError:
        lib = None
        logger.warning("ContentLibrary not available, using fallbacks.")

    answers = {}
    for q in questions:
        q_lower = q.lower()
        answer = None
        
        # 1. Hardcoded Semantic Matches (High Confidence)
        if "linkedin" in q_lower:
            answer = "https://www.linkedin.com/in/vrijen/"
        elif "company" in q_lower or "organization" in q_lower:
            answer = "Careerspan"
        elif "role" in q_lower or "title" in q_lower:
            answer = "Founder"
        elif "twitter" in q_lower or "x.com" in q_lower:
            answer = "https://x.com/vrijen"
        elif "email" in q_lower:
            answer = "attawar.v@gmail.com"
        elif "name" in q_lower:
            answer = "Vrijen Attawar"
        
        # 2. Content Library Search (Medium Confidence)
        if not answer and lib:
            # Search for keywords in question
            # e.g. "Why do you want to attend?" -> search "attend goals", "bio"
            search_terms = q
            if "why" in q_lower:
                search_terms = "bio mission networking"
            
            results = lib.search(query=search_terms, limit=1)
            if results:
                # Use the content of the first result
                # Assuming result has 'content' or 'text'
                item = results[0]
                # Adjust based on actual dictionary structure of item
                content = item.get('content') or item.get('text') or str(item)
                if content:
                    answer = f"[Draft from Content Library]: {content[:200]}..."

        # 3. Fallback
        if not answer:
            answer = "[DRAFT] Excited to connect with fellow founders and builders in NYC!"
            
        answers[q] = answer
        
    return answers

async def analyze_event(event_id: str, headless: bool = True):
    """Analyze event form and generate a draft."""
    url = await get_event_url(event_id)
    if not url:
        logger.error(f"Event {event_id} not found.")
        return

    logger.info(f"Analyzing event: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless
        )
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Click Register/Request
            # Try different selectors
            button = page.locator("button:has-text('Register')").first
            if not await button.is_visible():
                button = page.locator("button:has-text('Request to Join')").first
            if not await button.is_visible():
                button = page.locator("button:has-text('Get Tickets')").first
            
            if not await button.is_visible():
                logger.error("Could not find registration button.")
                return

            await button.click()
            
            # Wait for form or completion
            # Heuristic: Look for inputs or specific modal headers
            try:
                await page.wait_for_selector("form input, form textarea", timeout=5000)
            except:
                logger.info("No inputs found immediately. Might be 1-click or login required.")
                if await ensure_login(page):
                    # If logged in and no inputs, it might be 1-click. 
                    # We should be careful not to submit in analysis mode.
                    # But often Luma shows a "Review" modal first.
                    pass
            
            # Extract questions
            labels = await page.locator("label").all_inner_texts()
            inputs = await page.locator("input, textarea").all()
            
            # Filter standard fields if already filled (Luma pre-fills name/email)
            # This is a simplification.
            
            questions = [l for l in labels if l.strip()]
            answers = await generate_answers(questions)
            
            # Create Draft
            draft_path = DRAFTS_DIR / f"{event_id}.md"
            draft_content = f"""---
event_id: {event_id}
url: {url}
status: draft
generated_at: {datetime.now().isoformat()}
---

# Registration Draft for {event_id}

## Questions & Proposed Answers

"""
            for q, a in answers.items():
                draft_content += f"### {q}\n{a}\n\n"
            
            if not questions:
                draft_content += "**No custom questions detected.** Form may be Name/Email only or 1-click.\n"

            draft_content += "\n---\nTo approve, verify answers and run:\n"
            draft_content += f"`python3 N5/scripts/luma_register.py --event-id {event_id} --submit`"
            
            with open(draft_path, "w") as f:
                f.write(draft_content)
            
            logger.info(f"Draft saved to {draft_path}")
            update_registration_status(event_id, "draft_created")

        except Exception as e:
            logger.error(f"Error analyzing event: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

async def submit_event(event_id: str, headless: bool = True):
    """Submit registration using info from draft."""
    draft_path = DRAFTS_DIR / f"{event_id}.md"
    if not draft_path.exists():
        logger.error("Draft not found. Please run --analyze first.")
        return

    # Load answers from draft (simple parsing)
    with open(draft_path) as f:
        content = f.read()
    
    # Parse markdown to get answers map (Quick & Dirty)
    answers_map = {}
    current_q = None
    for line in content.splitlines():
        if line.startswith("### "):
            current_q = line.replace("### ", "").strip()
        elif current_q and line.strip() and not line.startswith("-") and not line.startswith("`"):
            answers_map[current_q] = line.strip()
            current_q = None # Reset

    url = await get_event_url(event_id)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless
        )
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Click Register (Same logic as analyze)
            button = page.locator("button:has-text('Register')").first
            if not await button.is_visible():
                button = page.locator("button:has-text('Request to Join')").first
            if not await button.is_visible():
                button = page.locator("button:has-text('Get Tickets')").first
            
            await button.click()
            await page.wait_for_timeout(2000) # Wait for animation
            
            # Fill Form
            # Iterate inputs and try to match labels
            # This is complex because labels might not map 1:1 in DOM structure easily
            # Strategy: Find label, get associated input ID, fill it.
            
            for q, a in answers_map.items():
                try:
                    # Try exact label match
                    # Luma often wraps input inside label or uses 'for'
                    inp = page.get_by_label(q)
                    if await inp.is_visible():
                        await inp.fill(a)
                        continue
                    
                    # Try searching for text and finding nearby input
                    # ... implementation detail ...
                    # Fallback: Just fill visible empty textareas for long answers
                    if len(a) > 50:
                        tas = await page.locator("textarea").all()
                        for ta in tas:
                            if not await ta.input_value():
                                await ta.fill(a)
                                break
                except Exception as ex:
                    logger.warning(f"Could not fill field '{q}': {ex}")

            # Submit
            submit_btn = page.locator("button[type='submit']").first
            if not await submit_btn.is_visible():
                 submit_btn = page.locator("button:has-text('Register')").last # Sometimes modal button has same name
            
            if await submit_btn.is_enabled():
                await submit_btn.click()
                logger.info("Clicked submit.")
                
                # Wait for success
                # Look for "You're in" or "Request Sent"
                try:
                    await page.wait_for_selector("text=You're in|text=Request Sent|text=Ticket", timeout=15000)
                    logger.info("✓ Registration successful")
                    
                    # Update DB
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("UPDATE events SET registered_at = ?, registration_status = 'submitted' WHERE id = ?", 
                                (datetime.now().isoformat(), event_id))
                    conn.commit()
                    conn.close()
                    
                    # Send SMS
                    try:
                        import sys
                        sys.path.append(str(N5_ROOT / "scripts"))
                        from send_sms_notification import send_sms_via_zo
                        send_sms_via_zo(f"✅ Luma Registration Submitted for {event_id}. Check email for confirmation.")
                    except ImportError:
                        logger.error("Could not import send_sms_notification")

                except PlaywrightTimeoutError:
                    logger.error("Timed out waiting for confirmation.")
                    page.screenshot(path=str(DRAFTS_DIR / f"{event_id}_error.png"))
            else:
                logger.error("Submit button disabled.")

        except Exception as e:
            logger.error(f"Error submitting event: {e}")
            page.screenshot(path=str(DRAFTS_DIR / f"{event_id}_error.png"))
        finally:
            await browser.close()

async def process_queue():
    """Find approved events without registration and create drafts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE approved_at IS NOT NULL AND (registration_status IS NULL OR registration_status = 'pending')")
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    for ev in events:
        await analyze_event(ev['id'])

async def login_interactive():
    """Launch browser to let user log in."""
    logger.info("Launching interactive browser for login. Close window when done.")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False # Visible
        )
        page = await browser.new_page()
        await page.goto("https://lu.ma/signin")
        
        # Wait indefinitely until closed
        try:
            await page.wait_for_timeout(300000) # 5 mins
        except:
            pass
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-id", help="Event ID")
    parser.add_argument("--analyze", action="store_true", help="Analyze form and create draft")
    parser.add_argument("--submit", action="store_true", help="Submit registration from draft")
    parser.add_argument("--process-queue", action="store_true", help="Process all approved events")
    parser.add_argument("--login-interactive", action="store_true", help="Open browser to log in")
    
    args = parser.parse_args()
    
    if args.login_interactive:
        asyncio.run(login_interactive())
    elif args.process_queue:
        asyncio.run(process_queue())
    elif args.event_id and args.analyze:
        asyncio.run(analyze_event(args.event_id))
    elif args.event_id and args.submit:
        asyncio.run(submit_event(args.event_id))
    else:
        parser.print_help()


