#!/usr/bin/env python3
"""
Content Library v3 Migration Patch 001
=======================================
Fixes:
1. Links missing URLs (copy from old DB content field)
2. has_content flag incorrect for snippets
3. has_content flag incorrect for any item with content

Created: 2025-12-02
"""

import argparse
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

V3_DB = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
OLD_DB = Path("/home/workspace/N5/data/content_library.db")


def fix_missing_urls(dry_run: bool) -> int:
    """Copy URLs from old DB content field to v3 url field where missing."""
    logging.info("=== Fix 1: Links with missing URLs ===")
    
    # Get links from old DB where content looks like a URL
    old_conn = sqlite3.connect(OLD_DB)
    old_conn.row_factory = sqlite3.Row
    old_cur = old_conn.cursor()
    
    old_cur.execute("""
        SELECT id, content 
        FROM items 
        WHERE type='link' 
          AND content LIKE 'http%'
    """)
    old_links = {row['id']: row['content'] for row in old_cur.fetchall()}
    old_conn.close()
    
    # Find v3 links missing URLs
    v3_conn = sqlite3.connect(V3_DB)
    v3_conn.row_factory = sqlite3.Row
    v3_cur = v3_conn.cursor()
    
    v3_cur.execute("""
        SELECT id, url 
        FROM items 
        WHERE item_type='link' 
          AND source='n5_links'
          AND (url IS NULL OR url='')
    """)
    missing = v3_cur.fetchall()
    
    fixed = 0
    for row in missing:
        item_id = row['id']
        if item_id in old_links:
            url = old_links[item_id]
            if dry_run:
                logging.info(f"  [DRY-RUN] Would set url for {item_id}: {url[:60]}...")
            else:
                v3_cur.execute(
                    "UPDATE items SET url=?, updated_at=datetime('now') WHERE id=?",
                    (url, item_id)
                )
                logging.info(f"  Fixed url for {item_id}: {url[:60]}...")
            fixed += 1
        else:
            logging.warning(f"  No URL found in old DB for {item_id}")
    
    if not dry_run:
        v3_conn.commit()
    v3_conn.close()
    
    logging.info(f"  Total: {fixed} links fixed")
    return fixed


def fix_has_content_flags(dry_run: bool) -> int:
    """Set has_content=1 for any item with non-empty content."""
    logging.info("=== Fix 2: has_content flags ===")
    
    v3_conn = sqlite3.connect(V3_DB)
    v3_cur = v3_conn.cursor()
    
    # Find items with content but has_content=0
    v3_cur.execute("""
        SELECT id, item_type, length(content) as len
        FROM items
        WHERE content IS NOT NULL 
          AND length(content) > 0
          AND has_content = 0
    """)
    wrong_flags = v3_cur.fetchall()
    
    if dry_run:
        for row in wrong_flags:
            logging.info(f"  [DRY-RUN] Would set has_content=1 for {row[0]} ({row[1]}, {row[2]} chars)")
    else:
        v3_cur.execute("""
            UPDATE items 
            SET has_content = 1, updated_at = datetime('now')
            WHERE content IS NOT NULL 
              AND length(content) > 0
              AND has_content = 0
        """)
        v3_conn.commit()
        for row in wrong_flags:
            logging.info(f"  Fixed has_content for {row[0]} ({row[1]}, {row[2]} chars)")
    
    v3_conn.close()
    
    logging.info(f"  Total: {len(wrong_flags)} items fixed")
    return len(wrong_flags)


def fix_has_summary_flags(dry_run: bool) -> int:
    """Set has_summary=1 for any item with non-empty summary."""
    logging.info("=== Fix 3: has_summary flags ===")
    
    v3_conn = sqlite3.connect(V3_DB)
    v3_cur = v3_conn.cursor()
    
    # Find items with summary but has_summary=0
    v3_cur.execute("""
        SELECT id, item_type, length(summary) as len
        FROM items
        WHERE summary IS NOT NULL 
          AND length(summary) > 0
          AND has_summary = 0
    """)
    wrong_flags = v3_cur.fetchall()
    
    if dry_run:
        for row in wrong_flags:
            logging.info(f"  [DRY-RUN] Would set has_summary=1 for {row[0]} ({row[1]}, {row[2]} chars)")
    else:
        v3_cur.execute("""
            UPDATE items 
            SET has_summary = 1, updated_at = datetime('now')
            WHERE summary IS NOT NULL 
              AND length(summary) > 0
              AND has_summary = 0
        """)
        v3_conn.commit()
        for row in wrong_flags:
            logging.info(f"  Fixed has_summary for {row[0]} ({row[1]}, {row[2]} chars)")
    
    v3_conn.close()
    
    logging.info(f"  Total: {len(wrong_flags)} items fixed")
    return len(wrong_flags)


def verify_fixes():
    """Run verification queries after fixes."""
    logging.info("=== Verification ===")
    
    v3_conn = sqlite3.connect(V3_DB)
    v3_cur = v3_conn.cursor()
    
    # Check for remaining missing URLs
    v3_cur.execute("""
        SELECT COUNT(*) FROM items 
        WHERE item_type='link' AND source='n5_links' AND (url IS NULL OR url='')
    """)
    missing_urls = v3_cur.fetchone()[0]
    
    # Check for remaining wrong has_content
    v3_cur.execute("""
        SELECT COUNT(*) FROM items
        WHERE content IS NOT NULL AND length(content) > 0 AND has_content = 0
    """)
    wrong_content = v3_cur.fetchone()[0]
    
    # Check for remaining wrong has_summary
    v3_cur.execute("""
        SELECT COUNT(*) FROM items
        WHERE summary IS NOT NULL AND length(summary) > 0 AND has_summary = 0
    """)
    wrong_summary = v3_cur.fetchone()[0]
    
    v3_conn.close()
    
    all_good = missing_urls == 0 and wrong_content == 0 and wrong_summary == 0
    
    logging.info(f"  Links still missing URLs: {missing_urls}")
    logging.info(f"  Items with wrong has_content: {wrong_content}")
    logging.info(f"  Items with wrong has_summary: {wrong_summary}")
    logging.info(f"  All checks passed: {all_good}")
    
    return all_good


def main():
    parser = argparse.ArgumentParser(description="Content Library v3 Migration Patch 001")
    parser.add_argument("--execute", action="store_true", help="Actually apply fixes (default: dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        logging.info("Running in DRY-RUN mode. Use --execute to apply fixes.")
    else:
        logging.warning("EXECUTE mode: applying fixes to database.")
    
    print()
    
    # Run fixes
    fix_missing_urls(dry_run)
    print()
    fix_has_content_flags(dry_run)
    print()
    fix_has_summary_flags(dry_run)
    print()
    
    if not dry_run:
        verify_fixes()


if __name__ == "__main__":
    main()

