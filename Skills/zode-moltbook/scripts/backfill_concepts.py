#!/usr/bin/env python3
"""
One-time backfill — extract concepts for existing posts in our_posts table.

Sends each post to /zo/ask for concept extraction, rate-limited at 2s between calls.

Usage: python3 backfill_concepts.py [--dry-run]
"""

import argparse
import json
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from db_bridge import SocialDB
from direct_poster import _extract_concepts


def backfill(dry_run: bool = False):
    db = SocialDB()
    try:
        rows = db.db.execute(
            "SELECT post_id, title, content, concepts_introduced FROM our_posts ORDER BY posted_at ASC"
        ).fetchall()

        total = len(rows)
        already = 0
        updated = 0
        failed = 0

        print(f"Backfill: {total} posts to process")
        print("=" * 50)

        for i, (post_id, title, content, existing) in enumerate(rows, 1):
            # Skip if already has concepts
            if existing and existing != "[]" and existing != "":
                already += 1
                print(f"  [{i}/{total}] SKIP (has concepts): {title[:60]}")
                continue

            print(f"  [{i}/{total}] Extracting: {title[:60]}...", end="", flush=True)

            if dry_run:
                print(" [DRY-RUN]")
                continue

            concepts = _extract_concepts(title or "", content or "")
            if concepts:
                try:
                    db.db.execute(
                        "UPDATE our_posts SET concepts_introduced = ? WHERE post_id = ?",
                        [json.dumps(concepts), post_id]
                    )
                    updated += 1
                    print(f" -> {concepts}")
                except Exception as e:
                    failed += 1
                    print(f" DB ERROR: {e}")
            else:
                failed += 1
                print(" -> no concepts returned")

            # Rate limit: 2s between LLM calls
            if i < total:
                time.sleep(2)

        print()
        print(f"Done: {updated} updated, {already} already had concepts, {failed} failed")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill concepts for existing posts")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()
    backfill(dry_run=args.dry_run)
