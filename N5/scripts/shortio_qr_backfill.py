#!/usr/bin/env python3
"""
Backfill QR codes for existing Short.io links.
"""
import json
import logging
import requests
import sqlite3
import time
from pathlib import Path
from shortio_link_service import load_secret, CONTENT_LIB_DB

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

LINKS_LOG = Path("/home/workspace/N5/data/shortio_links.jsonl")
QR_DIR = Path("/home/workspace/N5/assets/qr_codes")

def main():
    key = load_secret()
    if not key:
        logger.error("No API key.")
        return

    QR_DIR.mkdir(parents=True, exist_ok=True)

    if not LINKS_LOG.exists():
        logger.info("No links log found.")
        return

    links = []
    with LINKS_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                links.append(json.loads(line))

    logger.info(f"Found {len(links)} links to check.")

    with sqlite3.connect(CONTENT_LIB_DB) as conn:
        cursor = conn.cursor()
        
        for link in links:
            link_id = link.get("link_id") or link.get("id")
            if not link_id:
                continue

            qr_filename = f"{link_id}_qr.png"
            qr_path = QR_DIR / qr_filename

            # 1. Generate/Download if missing
            if not qr_path.exists():
                logger.info(f"Generating QR for {link_id}...")
                try:
                    qr_url = f"https://api.short.io/links/qr/{link_id}"
                    resp = requests.post(qr_url, headers={
                        "Authorization": key,
                        "Content-Type": "application/json",
                        "Accept": "image/png"
                    }, json={"type": "png"}, timeout=10)

                    if resp.status_code in [200, 201]:
                        qr_path.write_bytes(resp.content)
                        logger.info(f"Saved {qr_path}")
                        time.sleep(0.5) # Rate limit politeness
                    else:
                        logger.error(f"Failed to fetch QR for {link_id}: {resp.status_code}")
                        continue
                except Exception as e:
                    logger.error(f"Error fetching QR for {link_id}: {e}")
                    continue
            else:
                logger.debug(f"QR exists for {link_id}")

            # 2. Update DB Tag
            # Find item by short_url (source of truth in log)
            short_url = link.get("short_url")
            cursor.execute("SELECT id FROM items WHERE url = ?", (short_url,))
            row = cursor.fetchone()
            
            if row:
                item_id = row[0]
                # Insert tag
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value) 
                        VALUES (?, ?, ?)
                    """, (item_id, "qr_code_path", str(qr_path)))
                    if cursor.rowcount > 0:
                        logger.info(f"Tagged item {item_id} with QR path.")
                except sqlite3.Error as e:
                    logger.error(f"DB Error for {short_url}: {e}")
            else:
                logger.warning(f"Link {short_url} not found in DB.")
        
        conn.commit()

if __name__ == "__main__":
    main()


