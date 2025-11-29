#!/usr/bin/env python3
"""Basic helper to query Fillout JSONL event logs.

Usage examples:

  python3 query_events.py --since 2025-11-01
  python3 query_events.py --form-id my_form_id
  python3 query_events.py --limit 20

This is intentionally minimal; heavier analysis can be done via dedicated
scripts or by the AI reading its output.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

EVENTS_BASE_DIR = Path("/home/workspace/N5/Integrations/fillout/events").resolve()


@dataclass
class Filters:
    since: Optional[date] = None
    until: Optional[date] = None
    form_id: Optional[str] = None
    limit: int = 50


def parse_args() -> Filters:
    parser = argparse.ArgumentParser(description="Query Fillout JSONL event logs")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD, inclusive)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD, inclusive)")
    parser.add_argument("--form-id", help="Filter by Fillout form id (if present in payload)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of events to print")

    args = parser.parse_args()

    def parse_date(value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()

    return Filters(
        since=parse_date(args.since),
        until=parse_date(args.until),
        form_id=args.form_id,
        limit=args.limit,
    )


def iter_event_files(filters: Filters) -> Iterable[Path]:
    if not EVENTS_BASE_DIR.exists():
        return []

    files = sorted(EVENTS_BASE_DIR.glob("*.jsonl"))
    for path in files:
        try:
            day = datetime.strptime(path.stem, "%Y-%m-%d").date()
        except ValueError:
            # Skip files that do not follow the YYYY-MM-DD.jsonl pattern
            continue

        if filters.since and day < filters.since:
            continue
        if filters.until and day > filters.until:
            continue
        yield path


def event_matches(event: Dict[str, Any], filters: Filters) -> bool:
    if filters.form_id:
        payload = event.get("payload", {})
        # Fillout payloads typically have formId (or similar); we handle missing keys gracefully.
        if payload.get("formId") != filters.form_id:
            return False
    return True


def load_events(filters: Filters) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for path in iter_event_files(filters):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if not event_matches(event, filters):
                    continue

                results.append(event)
                if len(results) >= filters.limit:
                    return results

    return results


def main() -> None:
    filters = parse_args()
    events = load_events(filters)

    print(json.dumps(events, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

