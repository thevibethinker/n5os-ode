from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

EVENTS_BASE_DIR = Path("/home/workspace/Personal/Integrations/fillout/events").resolve()


def iter_events_for_date(d: date) -> Iterable[Dict[str, Any]]:
    path = EVENTS_BASE_DIR / f"{d.isoformat()}.jsonl"
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    return _gen()


def filter_events(events: Iterable[Dict[str, Any]], form_id: str | None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for ev in events:
        payload = ev.get("payload", {})
        if form_id is not None and payload.get("formId") != form_id:
            continue
        results.append(ev)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Fillout webhook events stored as JSONL.")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date in YYYY-MM-DD format (defaults to today in UTC)",
    )
    parser.add_argument(
        "--form-id",
        type=str,
        default=None,
        help="Optional formId to filter by",
    )
    args = parser.parse_args()

    if args.date is None:
        d = datetime.utcnow().date()
    else:
        d = date.fromisoformat(args.date)

    events_iter = iter_events_for_date(d)
    events = filter_events(events_iter, args.form_id)

    print(f"Found {len(events)} event(s) on {d.isoformat()}" + (f" for formId={args.form_id}" if args.form_id else ""))
    for idx, ev in enumerate(events, start=1):
        received_at = ev.get("received_at", "?")
        payload = ev.get("payload", {})
        form_id = payload.get("formId")
        submission_id = payload.get("submissionId") or payload.get("submission_id")
        print("-" * 60)
        print(f"[{idx}] received_at={received_at} formId={form_id} submissionId={submission_id}")
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()

