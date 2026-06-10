#!/usr/bin/env python3
"""
Stream Sentience desktop screenshots to a rolling local activity feed.
Pulls screenshot memories, parses structured data, writes to activity_feed.jsonl.
Maintains a 48-hour rolling window.
Uses per-stream seen tracking (won't collide with pull_memories).
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from state import SeenStore, WatermarkStore, atomic_write

API_URL = "https://audiosummarizer-production.up.railway.app/v1/memories"
API_KEY = os.environ.get("SENTIENCE_API_KEY")
DATA_DIR = Path(__file__).parent.parent / "data"
FEED_FILE = DATA_DIR / "activity_feed.jsonl"
STREAM = "activity_feed"
ROLLING_HOURS = 48


def pull_screenshots(start: str, end: str) -> list[dict]:
    resp = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        params={"start": start, "end": end},
        timeout=60,
    )
    resp.raise_for_status()
    memories = resp.json().get("memories", [])
    return [m for m in memories if m.get("source") == "Sentience Desktop App"]


def parse_screenshot(memory: dict) -> dict | None:
    raw = memory.get("content") or ""
    if isinstance(raw, dict):
        content = raw
    else:
        try:
            content = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    sig_score = content.get("significance_score", 0)
    if sig_score < 0.3:
        return None

    category = content.get("category", "unknown")
    if category in ("System", "Lock Screen"):
        return None

    return {
        "id": memory["id"],
        "timestamp": memory["timestamp"],
        "app": content.get("appName", "unknown"),
        "window": content.get("windowTitle", ""),
        "title": content.get("title", ""),
        "summary": content.get("summary", ""),
        "category": category,
        "significance": sig_score,
        "sentiment": content.get("sentiment", {}).get("overall", ""),
        "people": content.get("facts", {}).get("people", []),
        "companies": content.get("facts", {}).get("companies", []),
        "tools": content.get("facts", {}).get("tools", []),
        "actions": content.get("facts", {}).get("actions", []),
        "urls": content.get("facts", {}).get("urls", []),
        "emails": [],
        "dates": content.get("facts", {}).get("dates", []),
    }


def prune_feed(max_age_hours: int = ROLLING_HOURS):
    if not FEED_FILE.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    lines = FEED_FILE.read_text().strip().split("\n")
    kept = []
    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            ts_str = entry.get("timestamp", "")
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts >= cutoff:
                kept.append(line)
        except (json.JSONDecodeError, ValueError):
            continue

    atomic_write(FEED_FILE, "\n".join(kept) + "\n" if kept else "")


def main():
    parser = argparse.ArgumentParser(description="Stream Sentience screenshots to activity feed")
    parser.add_argument("--hours", type=float, default=1, help="Hours to look back (default: 1)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: SENTIENCE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    seen = SeenStore()
    watermarks = WatermarkStore()

    last = watermarks.get(STREAM)
    if last and not args.dry_run:
        start_dt = datetime.fromisoformat(last.replace("Z", "+00:00")) - timedelta(minutes=5)
    else:
        start_dt = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    end_dt = datetime.now(timezone.utc)
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Pulling screenshots from {start_str} to {end_str}")

    try:
        screenshots = pull_screenshots(start_str, end_str)
    except requests.RequestException as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(screenshots)} screenshots")

    new_entries = []
    for s in screenshots:
        if seen.is_seen(STREAM, s["id"]):
            continue
        parsed = parse_screenshot(s)
        if parsed:
            new_entries.append(parsed)
            seen.mark_seen(STREAM, s["id"])

    print(f"New entries after dedup + filter: {len(new_entries)}")

    if new_entries and not args.dry_run:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(FEED_FILE, "a") as f:
            for entry in new_entries:
                f.write(json.dumps(entry) + "\n")
        seen.prune()
        seen.save()
        watermarks.set(STREAM, end_str)
        watermarks.save()
        prune_feed()
        print(f"Wrote {len(new_entries)} entries to {FEED_FILE}")
    elif new_entries and args.dry_run:
        for entry in new_entries[:5]:
            print(f"  [{entry['app']}] {entry['title']}")
    else:
        print("No new screenshots to process")

    if FEED_FILE.exists() and not args.dry_run:
        lines = [l for l in FEED_FILE.read_text().strip().split("\n") if l.strip()]
        print(f"Feed total: {len(lines)} entries")

    print(f"Seen IDs tracked (this stream): {seen.count(STREAM)}")


if __name__ == "__main__":
    main()
