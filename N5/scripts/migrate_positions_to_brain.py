#!/usr/bin/env python3
"""Migrate Positions semantic embeddings into the canonical brain.db layer.

- Source of truth for *position metadata* remains: N5/data/positions.db
- Canonical embedding store becomes: N5/cognition/brain.db (resources/blocks/vectors)
- This script ONLY writes into brain.db (no changes to positions.db)

Safety:
- Default is --dry-run (no writes)
- Use --execute to perform migration

Usage:
  python3 N5/scripts/migrate_positions_to_brain.py --dry-run
  python3 N5/scripts/migrate_positions_to_brain.py --execute
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/positions.db")
RESOURCE_PATH_PREFIX = "n5://positions/"
BRAIN_TAG = "positions"


def _get_memory_client():
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from N5.cognition.n5_memory_client import N5MemoryClient
    return N5MemoryClient()


def _position_resource_path(position_id: str) -> str:
    return f"{RESOURCE_PATH_PREFIX}{position_id}"


def _position_body(position_id: str, domain: str, title: str, insight: str) -> str:
    return f"[Position]\nDomain: {domain}\nID: {position_id}\n\n# {title}\n\n{insight}".strip()


def iter_positions(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id, domain, title, insight, formed_date FROM positions ORDER BY updated_at DESC")
    for row in cur.fetchall():
        yield row[0], row[1], row[2], row[3], row[4]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="Perform writes into brain.db")
    ap.add_argument("--dry-run", action="store_true", help="Alias for default behavior (no writes)")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of positions migrated (0 = all)")
    args = ap.parse_args()

    do_write = bool(args.execute)

    if not DB_PATH.exists():
        raise SystemExit(f"positions.db not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    rows = list(iter_positions(conn))
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    preview = [{"id": r[0], "domain": r[1], "title": r[2]} for r in rows[:10]]

    if not do_write:
        print(json.dumps({
            "mode": "dry-run",
            "count": len(rows),
            "top10": preview,
            "note": "Run with --execute to write into brain.db",
        }, indent=2))
        return

    client = _get_memory_client()

    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    migrated = 0

    for position_id, domain, title, insight, formed_date in rows:
        body = _position_body(position_id, domain, title, insight)
        file_hash = hashlib.md5(body.encode("utf-8")).hexdigest()
        path = _position_resource_path(position_id)

        resource_id = client.store_resource(path=path, file_hash=file_hash, content_date=formed_date)
        client.delete_resource_blocks(resource_id)
        client.add_block(resource_id, body, block_type="position", start_line=1, end_line=1, content_date=formed_date)
        client.tag_resource(path, BRAIN_TAG)
        migrated += 1

        if migrated % 50 == 0:
            print(f"{migrated}/{len(rows)} migrated...")

    finished = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print(json.dumps({
        "mode": "execute",
        "started": started,
        "finished": finished,
        "migrated": migrated,
    }, indent=2))


if __name__ == "__main__":
    main()

