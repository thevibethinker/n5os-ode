#!/usr/bin/env python3
"""
Pull new memories from Sentience that didn't originate from Zo.
Uses per-stream seen tracking (won't collide with activity_feed).
Filters Zo-originated memories by source AND content marker.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from state import SeenStore, WatermarkStore

API_URL = "https://audiosummarizer-production.up.railway.app/v1/memories"
API_KEY = os.environ.get("SENTIENCE_API_KEY")
STREAM = "pull"
ZO_CONTENT_MARKERS = ["[Zo Journal:", "[Zo Learning:", "[V's Framework", "[External Insight", "[Communication Style:", "[Building Principle:", "[Zo's Self-Model:"]


def is_zo_originated(memory: dict) -> bool:
    if memory.get("source") == "api":
        return True
    content = memory.get("content") or ""
    return any(marker in content for marker in ZO_CONTENT_MARKERS)


def pull(hours: int, dry_run: bool = False):
    if not API_KEY:
        print("ERROR: SENTIENCE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    seen = SeenStore()
    watermarks = WatermarkStore()

    last = watermarks.get(STREAM)
    if last:
        start_dt = datetime.fromisoformat(last.replace("Z", "+00:00")) - timedelta(minutes=5)
        start = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        start = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

    end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Pulling memories from {start} to {end}")

    try:
        resp = requests.get(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"start": start, "end": end},
            timeout=60,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    memories = resp.json().get("memories", [])

    new_memories = []
    zo_skipped = 0
    for m in memories:
        mid = m.get("id", "")

        if seen.is_seen(STREAM, mid):
            continue

        if is_zo_originated(m):
            seen.mark_seen(STREAM, mid)
            zo_skipped += 1
            continue

        new_memories.append(m)
        seen.mark_seen(STREAM, mid)

    if not dry_run:
        seen.prune()
        seen.save()
        watermarks.set(STREAM, end)
        watermarks.save()

    print(f"\nTotal fetched: {len(memories)}")
    print(f"New (non-Zo): {len(new_memories)}")
    print(f"Zo-originated skipped: {zo_skipped}")
    print(f"Already seen skipped: {len(memories) - len(new_memories) - zo_skipped}")

    if new_memories:
        print(f"\n{'='*60}")
        print("NEW MEMORIES:")
        print(f"{'='*60}")
        for m in new_memories:
            content = (m.get("content") or "")[:300].replace("\n", " ").strip()
            ts = m.get("timestamp", "?")
            src = m.get("source", "?")
            print(f"\n[{ts}] ({src}) {m.get('id', '?')}")
            print(f"  {content}")
    else:
        print("\nNo new memories to surface.")

    output = {
        "pulled_at": end,
        "window_start": start,
        "total_fetched": len(memories),
        "new_count": len(new_memories),
        "new_memories": [
            {
                "id": m.get("id"),
                "source": m.get("source"),
                "type": m.get("type"),
                "timestamp": m.get("timestamp"),
                "preview": (m.get("content") or "")[:500]
            }
            for m in new_memories
        ]
    }
    print(f"\n{json.dumps(output)}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull new memories from Sentience")
    parser.add_argument("--hours", type=int, default=6, help="Lookback window (default 6, first run only)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    pull(args.hours, args.dry_run)
