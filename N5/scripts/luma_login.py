#!/usr/bin/env python3
"""
Luma Login Helper
Runs an interactive browser session to let the user log in to Luma.
Saves storage state to N5/data/luma_auth.json for subsequent headless scripts.

Usage:
    python3 N5/scripts/luma_login.py
"""

import asyncio
import logging
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
AUTH_PATH = N5_ROOT / "data" / "luma_auth.json"

async def login_interactive():
    """Launch browser for interactive login."""
    logger.info("Launching interactive browser for Luma login...")
    
    async with async_playwright() as p:
        # Launch persistent context if possible, or just standard with saving state
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(viewport={"width": 1280, "height": 1024})
        
        # If we have existing state, load it first
        if AUTH_PATH.exists():
            try:
                # Playwright context.storage_state is only for *returning* state usually,
                # to *load* it we pass storage_state to new_context.
                # Since we already created context, we might need to recreate it if we want to load.
                # But actually, let's just try to load if it exists to see if we are already logged in.
                await context.close()
                context = await browser.new_context(
                    storage_state=AUTH_PATH,
                    viewport={"width": 1280, "height": 1024}
                )
                logger.info("Loaded existing session state.")
            except Exception as e:
                logger.warning(f"Could not load existing state (might be expired or invalid): {e}")
                # Fallback to fresh context
                context = await browser.new_context(viewport={"width": 1280, "height": 1024})

        page = await context.new_page()
        
        logger.info("Navigating to https://lu.ma/signin ...")
        await page.goto("https://lu.ma/signin")
        
        print("\n" + "="*60)
        print("ACTION REQUIRED: Please log in to Luma in the browser window.")
        print("Once you are logged in and see your home/events page, press ENTER in this terminal.")
        print("="*60 + "\n")
        
        input("Press Enter to save session state...")
        
        # Save state
        await context.storage_state(path=AUTH_PATH)
        logger.info(f"Session state saved to {AUTH_PATH}")
        
        await browser.close()

if __name__ == "__main__":
    AUTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(login_interactive())

