#!/usr/bin/env python3
"""
enhance.py.new - Enhance Content Library v3 items with topics, tags, and metadata.

This script works directly against the v3 SQLite schema:
- Adds topics (creating them if needed) and item_topics links
- Adds tags as key=value pairs
- Updates confidence and notes fields
"""

import argparse
import logging
import sqlite3
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_v3_enhance")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enhance a Content Library v3 item")
    parser.add_argument("id", help="Item ID to enhance")
    parser.add_argument(
        "--add-topic",
        action="append",
        dest="topics",
        default=[],
        help="Topic name to add (can be repeated)",
    )
    parser.add_argument(
        "--add-tag",
        action="append",
        dest="tags",
        default=[],
        help="Tag in key=value form (can be repeated)",
    )
    parser.add_argument(
        "--set-confidence",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Set confidence score (1-5)",
    )
    parser.add_argument("--set-notes", dest="notes", help="Set/replace notes field")

    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    try:
        # Check item exists
        if not conn.execute("SELECT 1 FROM items WHERE id = ?", (args.id,)).fetchone():
            print(f"Error: Item '{args.id}' not found")
            return 1

        # Add topics
        for topic_name in args.topics:  # type: ignore[arg-type]
            conn.execute(
                "INSERT OR IGNORE INTO topics (name) VALUES (?)",
                (topic_name,),
            )
            topic_id_row = conn.execute(
                "SELECT id FROM topics WHERE name = ?",
                (topic_name,),
            ).fetchone()
            if not topic_id_row:
                logger.warning("Topic row missing after insert for name=%s", topic_name)
                continue
            topic_id = topic_id_row[0]
            conn.execute(
                "INSERT OR IGNORE INTO item_topics (item_id, topic_id) VALUES (?, ?)",
                (args.id, topic_id),
            )
            print(f"Added topic: {topic_name}")

        # Add tags
        for tag in args.tags:  # type: ignore[arg-type]
            if "=" not in tag:
                logger.warning("Ignoring malformed tag (expected key=value): %s", tag)
                continue
            key, value = tag.split("=", 1)
            conn.execute(
                "INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                (args.id, key, value),
            )
            print(f"Added tag: {key}={value}")

        # Update item fields
        updates: List[str] = []
        params: List[object] = []

        if args.set_confidence is not None:
            updates.append("confidence = ?")
            params.append(int(args.set_confidence))
        if args.notes is not None:
            updates.append("notes = ?")
            params.append(args.notes)

        if updates:
            updates.append("updated_at = ?")
            from datetime import datetime

            params.append(datetime.now().isoformat())
            params.append(args.id)
            conn.execute(
                f"UPDATE items SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            print("Updated metadata")

        conn.commit()

    finally:
        conn.close()

    print(f"✓ Enhanced: {args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

