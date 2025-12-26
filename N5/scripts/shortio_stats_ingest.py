#!/usr/bin/env python3
"""Fetch daily engagement stats for every Short.io link we've created."""
import argparse
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from shortio_link_service import load_secret

# Logging
logging.basicConfig(format="%(asctime)sZ %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path("/home/workspace/N5/data")
LINKS_LOG = DATA_DIR / "shortio_links.jsonl"
STATS_LOG = DATA_DIR / "shortio_clicks.jsonl"
STATS_URL = "https://statistics.short.io/statistics/link/{link_id}"


def ensure_data_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LINKS_LOG.touch(exist_ok=True)
    STATS_LOG.touch(exist_ok=True)


def load_links() -> list[dict]:
    if not LINKS_LOG.exists():
        return []

    links = []
    with LINKS_LOG.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                record = json.loads(line)
                links.append(record)
            except json.JSONDecodeError:
                continue
    return links


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def build_time_window(days: int, start: str | None, end: str | None) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    window_end = parse_date(end) if end else now
    if start:
        window_start = parse_date(start)
    else:
        window_start = window_end - timedelta(days=days)
    return window_start.isoformat(), window_end.isoformat()


def read_existing_stat_entries() -> set[tuple[str, str]]:
    if not STATS_LOG.exists():
        return set()

    seen = set()
    with STATS_LOG.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                entry = json.loads(line)
                seen.add((entry.get("link_id"), entry.get("period_end")))
            except json.JSONDecodeError:
                continue
    return seen


def fetch_stats(api_key: str, link: dict, period_start: str, period_end: str) -> dict | None:
    link_id = link.get("link_id")
    if not link_id:
        logger.warning("Link record missing ID, skipping.")
        return None

    url = STATS_URL.format(link_id=link_id)
    headers = {"Authorization": api_key}
    params = {"startDate": period_start, "endDate": period_end}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch stats for %s: %s", link_id, exc)
        return None


def summarize_metrics(stats: dict) -> dict:
    if not isinstance(stats, dict):
        return {}
    
    clicks = stats.get("clicks")
    if clicks is None:
        clicks = stats.get("totalClicks")
    if clicks is None:
        clicks = stats.get("sum_clicks")
        
    return {
        "clicks": clicks,
        "unique_clicks": stats.get("uniqueClicks"),
        "visits": stats.get("visits"),
        "payload": stats,
    }


def persist_stats(link: dict, stats: dict, start: str, end: str) -> None:
    ensure_data_files()
    entry = {
        "link_id": link.get("link_id"),
        "short_url": link.get("short_url"),
        "domain": link.get("domain"),
        "path": link.get("path"),
        "title": link.get("title"),
        "period_start": start,
        "period_end": end,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        **summarize_metrics(stats),
    }
    with STATS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Short.io analytics for recorded links")
    parser.add_argument("--days", type=int, default=1, help="Look back this many days from `--end` (default 1)")
    parser.add_argument("--start", help="ISO 8601 start timestamp (overrides --days)")
    parser.add_argument("--end", help="ISO 8601 end timestamp (defaults to now)")
    parser.add_argument("--link-id", help="Limit stats fetch to a specific link_id")
    args = parser.parse_args()

    key = load_secret()
    if not key:
        logger.error("SHORT_IO_KEY is missing; aborting stats ingestion.")
        return 1

    ensure_data_files()
    links = load_links()
    if not links:
        logger.info("No recorded Short.io links found; nothing to ingest.")
        return 0

    period_start, period_end = build_time_window(args.days, args.start, args.end)
    seen_entries = read_existing_stat_entries()

    targets = links
    if args.link_id:
        targets = [link for link in links if link.get("link_id") == args.link_id]
        if not targets:
            logger.warning("No link found with link_id %s", args.link_id)

    for link in targets:
        summary_key = (link.get("link_id"), period_end)
        if summary_key in seen_entries:
            logger.debug("Stats already recorded for %s @ %s, skipping.", link.get("link_id"), period_end)
            continue

        stats = fetch_stats(key, link, period_start, period_end)
        if stats is not None:
            persist_stats(link, stats, period_start, period_end)
            logger.info("Stats recorded for %s (%s clicks)", link.get("link_id"), summary_key)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



