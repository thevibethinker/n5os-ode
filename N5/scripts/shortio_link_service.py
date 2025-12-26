#!/usr/bin/env python3
"""
Short.io Link Service
Usage: python3 shortio_link_service.py create --url <url> [--domain <domain>] [--path <path>] [--title <title>]
"""
import argparse
import json
import logging
import os
import requests
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SHORTIO_API_URL = "https://api.short.io/links"
LEGACY_SECRET_PATH = Path("/home/workspace/N5/config/secrets/shortio_api_key.env")
DATA_DIR = Path("/home/workspace/N5/data")
LINKS_LOG = DATA_DIR / "shortio_links.jsonl"
CONTENT_LIB_DB = DATA_DIR / "content_library.db"
QR_DIR = Path("/home/workspace/N5/assets/qr_codes")


def ensure_data_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)
    LINKS_LOG.touch(exist_ok=True)


def load_secret() -> str:
    """Load the Short.io API Key from the preferred source."""
    # Try the most direct environment variable first
    env_key = os.getenv("SHORT_IO_KEY") or os.getenv("SHORTIO_API_KEY")
    if env_key and env_key != "placeholder_replace_me":
        return env_key

    logger.error("Short.io API Key is not set in SHORT_IO_KEY or SHORTIO_API_KEY environment variables.")
    return None


def create_link(api_key: str, original_url: str, domain: str = None, path: str = None, title: str = None) -> dict:
    """Create a shortened link."""
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "originalURL": original_url,
    }
    
    if domain:
        payload["domain"] = domain
    if path:
        payload["path"] = path
    if title:
        payload["title"] = title
        
    try:
        response = requests.post(SHORTIO_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 201: # Created
            return response.json()
        elif response.status_code == 400:
            logger.error(f"Bad Request (400): {response.text}")
        elif response.status_code == 401:
            logger.error(f"Unauthorized (401): Check API Key.")
        elif response.status_code == 409:
            logger.error(f"Conflict (409): {response.text}")
        elif response.status_code == 429:
            logger.error(f"Rate Limit (429): {response.text}")
        else:
            logger.error(f"Error {response.status_code}: {response.text}")
            
        return None
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


def persist_link_record(result: dict) -> None:
    ensure_data_directory()
    link_id = result.get("id") or result.get("linkId")
    if not link_id:
        logger.warning("Response did not include a link ID; skipping persistence.")
        return

    existing_ids = set()
    if LINKS_LOG.exists():
        with LINKS_LOG.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    existing = json.loads(line)
                    existing_ids.add(existing.get("link_id"))
                except json.JSONDecodeError:
                    continue

    if link_id in existing_ids:
        logger.debug("Link record already exists; skipping append.")
        return

    payload = {
        "link_id": link_id,
        "short_url": result.get("shortURL"),
        "original_url": result.get("originalURL"),
        "domain": result.get("domain"),
        "path": result.get("path"),
        "title": result.get("title"),
        "created_at": result.get("createdAt") or datetime.now(timezone.utc).isoformat(),
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }

    with LINKS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

def add_to_content_library(link_data: dict, qr_path: str = None) -> None:
    """Add the short link to the Content Library database."""
    if not CONTENT_LIB_DB.exists():
        logger.warning("Content Library DB not found; skipping sync.")
        return

    try:
        with sqlite3.connect(CONTENT_LIB_DB) as conn:
            cursor = conn.cursor()
            
            # Check if URL already exists
            short_url = link_data.get("shortURL")
            cursor.execute("SELECT id FROM items WHERE url = ?", (short_url,))
            row = cursor.fetchone()
            
            if row:
                item_id = row[0]
                logger.info(f"Link {short_url} already exists in Content Library (ID: {item_id}). Updating tags.")
            else:
                item_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc).isoformat()
                
                # Prepare insert
                cursor.execute("""
                    INSERT INTO items (
                        id, type, title, url, content, 
                        created_at, updated_at, source, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    "link",
                    link_data.get("title") or short_url,
                    short_url,
                    short_url,  # content is same as url for links
                    now,
                    now,
                    "shortio",
                    f"Original URL: {link_data.get('originalURL')}"
                ))
            
            # Insert Tags (Tight Integration)
            link_id_val = link_data.get("id") or link_data.get("linkId")
            tags_to_add = [
                ("shortio_id", link_id_val),
                ("original_url", link_data.get("originalURL")),
                ("domain", link_data.get("domain"))
            ]
            
            if qr_path:
                tags_to_add.append(("qr_code_path", str(qr_path)))
            
            for key_name, val in tags_to_add:
                if val:
                    try:
                        cursor.execute("INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)", 
                                     (item_id, key_name, str(val)))
                    except sqlite3.Error:
                        pass # Ignore tag errors
            
            conn.commit()
            logger.info(f"✓ Synced to Content Library: {short_url}")
            
    except sqlite3.Error as e:
        logger.error(f"Failed to sync to Content Library: {e}")


def main():
    parser = argparse.ArgumentParser(description="Short.io Link Service")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a shortened link")
    create_parser.add_argument("--url", required=True, help="Original URL to shorten")
    create_parser.add_argument("--domain", help="Domain to use (optional)")
    create_parser.add_argument("--path", help="Custom path/slug (optional)")
    create_parser.add_argument("--title", help="Link title (optional)")
    create_parser.add_argument("--utm-source", help="UTM Source (e.g., linkedin, email)")
    create_parser.add_argument("--utm-medium", help="UTM Medium (e.g., social, newsletter)")
    create_parser.add_argument("--utm-campaign", help="UTM Campaign (e.g., spring_launch)")
    create_parser.add_argument("--qr", action="store_true", help="Generate and save QR code")
    
    # Info command (optional per mission)
    info_parser = subparsers.add_parser("info", help="Get script info")

    args = parser.parse_args()
    
    if args.command == "create":
        key = load_secret()
        if not key:
            logger.error("Cannot proceed without valid API key.")
            return 1
            
        # UTM Builder
        final_url = args.url
        if args.utm_source or args.utm_medium or args.utm_campaign:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(final_url)
            query = parse_qs(parsed.query)
            
            if args.utm_source: query["utm_source"] = [args.utm_source]
            if args.utm_medium: query["utm_medium"] = [args.utm_medium]
            if args.utm_campaign: query["utm_campaign"] = [args.utm_campaign]
            
            new_query = urlencode(query, doseq=True)
            final_url = urlunparse(parsed._replace(query=new_query))
            logger.info(f"Appended UTM tags: {final_url}")

        # Create link logic
        result = create_link(key, final_url, args.domain, args.path, args.title)
        qr_path_str = None
        
        if result:
            print(json.dumps(result, indent=2))
            persist_link_record(result)
            
            if args.qr:
                try:
                    link_id = result.get("id") or result.get("linkId")
                    qr_url = f"https://api.short.io/links/qr/{link_id}"
                    resp = requests.post(qr_url, headers={
                        "Authorization": key,
                        "Content-Type": "application/json",
                        "Accept": "image/png"
                    }, json={"type": "png"}, timeout=10)

                    if resp.status_code in [200, 201]:
                        out_path = QR_DIR / f"{link_id}_qr.png"
                        out_path.write_bytes(resp.content)
                        qr_path_str = str(out_path)
                        logger.info(f"✓ QR Code saved: {out_path}")
                    else:
                        logger.warning(f"Failed to generate QR code: {resp.status_code}")
                except Exception as e:
                    logger.error(f"QR generation failed: {e}")

            add_to_content_library(result, qr_path=qr_path_str)
            logger.info(f"✓ Link created: {result.get('shortURL')}")
        else:
            return 1
    
    elif args.command == "info":
        print("Short.io Link Service v1.0")
        print("Secret source: SHORT_IO_KEY environment variable (legacy file is read if that is not set)")
        print(f"Recorded links catalog: {LINKS_LOG}")
        if load_secret():
            print("Status: API Key detected")
        else:
            print("Status: API Key missing or placeholder")

    else:
        parser.print_help()
        
if __name__ == "__main__":
    exit(main())










