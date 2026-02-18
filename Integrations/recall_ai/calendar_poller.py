#!/usr/bin/env python3
"""
Calendar Poller — Background thread that runs inside the recall webhook service.

Every POLL_INTERVAL_SECONDS, fetches upcoming calendar events via /zo/ask,
compares against recall_bots table in meeting_pipeline.db, and schedules/
updates/cancels Recall bots accordingly.

Eliminates the need for a separate Zo scheduled agent.
"""

import importlib.util
import json
import logging
import os
import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

import requests

try:
    from .config import (
        CALENDAR_ACCOUNTS,
        DEFAULT_BOT_CONFIG,
        RECALL_DB_PATH,
    )
    from .recall_client import RecallClient
    from .calendar_scheduler import CalendarScheduler
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from config import CALENDAR_ACCOUNTS, DEFAULT_BOT_CONFIG, RECALL_DB_PATH
    from recall_client import RecallClient
    from calendar_scheduler import CalendarScheduler

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 300  # 5 minutes
SYNC_WINDOW_HOURS = 48
ZO_ASK_URL = "https://api.zo.computer/zo/ask"
ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
DB_PATH = RECALL_DB_PATH

SANITIZER_PATH = "/home/workspace/Integrations/zoputer-sync/sanitizer.py"

def _load_sanitizer():
    try:
        import sys as _sys
        spec = importlib.util.spec_from_file_location("sanitizer", str(SANITIZER_PATH))
        mod = importlib.util.module_from_spec(spec)
        _sys.modules["sanitizer"] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

_sanitizer = _load_sanitizer()


def ensure_db_schema() -> None:
    """Ensure calendar poller compatibility tables exist."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recall_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_event_id TEXT NOT NULL,
                calendar_account TEXT,
                meeting_url TEXT NOT NULL,
                meeting_title TEXT,
                meeting_start TEXT NOT NULL,
                join_at TEXT NOT NULL,
                bot_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(calendar_event_id, meeting_start)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recall_sync_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_sync TEXT,
                events_hash TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO recall_sync_state (id, last_sync, events_hash, updated_at)
            VALUES (1, NULL, NULL, CURRENT_TIMESTAMP)
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_recall_bots_status ON recall_bots(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_recall_bots_event_id ON recall_bots(calendar_event_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_recall_bots_start ON recall_bots(meeting_start)"
        )
        conn.commit()
    finally:
        conn.close()


def _extract_json_from_text(raw_text: str) -> Any:
    """Extract the first JSON object/array from a mixed-content text response."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Attempt direct parse first.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for idx, char in enumerate(cleaned):
        if char not in "[{":
            continue
        try:
            parsed, _ = decoder.raw_decode(cleaned[idx:])
            return parsed
        except json.JSONDecodeError:
            continue
    return None


def _sanitize_event_fields(events: List[Dict]) -> List[Dict]:
    """Redact suspicious content from user-generated event fields (titles, descriptions)."""
    if not _sanitizer or not events:
        return events
    for event in events:
        for field in ("summary", "description", "location"):
            val = event.get(field)
            if not val or not isinstance(val, str):
                continue
            result = _sanitizer.sanitize_message(val, source="calendar-event-field")
            if result.blocked or result.redacted:
                event[field] = result.sanitized_text
                logger.warning("Sanitized event field '%s': %s", field, _sanitizer.summarize_sanitization(result))
    return events


def fetch_calendar_events_via_zo(
    account: str,
    time_min: str,
    time_max: str,
) -> Optional[List[Dict]]:
    """
    Fetch calendar events using /zo/ask → use_app_google_calendar.

    Returns list of event dicts or None on failure.
    """
    if not ZO_TOKEN:
        logger.error("ZO_CLIENT_IDENTITY_TOKEN not available — cannot fetch calendar")
        return None

    prompt = (
        f"Use the google_calendar-list-events tool with these exact parameters:\n"
        f"- email: {account}\n"
        f"- timeMin: {time_min}\n"
        f"- timeMax: {time_max}\n"
        f"- singleEvents: true\n"
        f"- orderBy: startTime\n"
        f"- maxResults: 50\n\n"
        f"Return JSON ONLY in this exact shape:\n"
        f'{{"events": [/* raw event objects */]}}\n'
        f"If no events, return: {{\"events\": []}}"
    )

    try:
        resp = requests.post(
            ZO_ASK_URL,
            headers={
                "authorization": ZO_TOKEN,
                "content-type": "application/json",
            },
            json={"input": prompt},
            timeout=120,
        )
        if resp.status_code != 200:
            logger.error(f"Zo API returned {resp.status_code}: {resp.text[:200]}")
            return None

        output = resp.json().get("output", "")

        parsed = _extract_json_from_text(output)
        events = None
        if isinstance(parsed, list):
            events = parsed
        elif isinstance(parsed, dict):
            if isinstance(parsed.get("events"), list):
                events = parsed["events"]
            elif isinstance(parsed.get("items"), list):
                events = parsed["items"]
            elif isinstance(parsed.get("data"), list):
                events = parsed["data"]
            elif "id" in parsed and "start" in parsed:
                events = [parsed]

        if events is None:
            logger.error(f"Failed to extract calendar events from Zo response")
            logger.debug(f"Raw output: {output[:500]}")
            return None

        if not isinstance(events, list):
            logger.warning(f"Unexpected response format from Zo: {type(events)}")
            return []

        logger.info(f"Fetched {len(events)} events from {account}")
        return events

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse calendar response as JSON: {e}")
        logger.debug(f"Raw output: {output[:500]}")
        return None
    except requests.RequestException as e:
        logger.error(f"Zo API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching calendar: {e}")
        return None


def get_sync_state() -> Dict[str, Any]:
    """Get last sync state from DB."""
    ensure_db_schema()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM recall_sync_state WHERE id = 1").fetchone()
        if row:
            return dict(row)
        return {"last_sync": None, "events_hash": None}
    finally:
        conn.close()


def update_sync_state(events_hash: str):
    """Update sync state after successful sync."""
    ensure_db_schema()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE recall_sync_state SET last_sync = ?, events_hash = ?, updated_at = ? WHERE id = 1",
            (datetime.now(timezone.utc).isoformat(), events_hash, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_active_recall_bots() -> List[Dict]:
    """Get all non-terminal recall bots from DB."""
    ensure_db_schema()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM recall_bots WHERE status NOT IN ('done', 'fatal', 'cancelled') ORDER BY join_at"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def upsert_recall_bot(
    calendar_event_id: str,
    calendar_account: str,
    meeting_url: str,
    meeting_title: str,
    meeting_start: str,
    join_at: str,
    bot_id: Optional[str] = None,
    status: str = "pending",
) -> int:
    """Insert or update a recall bot record. Returns row id."""
    ensure_db_schema()
    conn = sqlite3.connect(DB_PATH)
    try:
        existing = conn.execute(
            "SELECT id FROM recall_bots WHERE calendar_event_id = ? AND meeting_start = ?",
            (calendar_event_id, meeting_start),
        ).fetchone()

        now = datetime.now(timezone.utc).isoformat()

        if existing:
            conn.execute(
                """UPDATE recall_bots
                   SET meeting_url = ?, meeting_title = ?, join_at = ?,
                       bot_id = COALESCE(?, bot_id), status = ?, updated_at = ?,
                       calendar_account = ?
                   WHERE id = ?""",
                (meeting_url, meeting_title, join_at, bot_id, status, now, calendar_account, existing[0]),
            )
            conn.commit()
            return existing[0]
        else:
            cursor = conn.execute(
                """INSERT INTO recall_bots
                   (calendar_event_id, calendar_account, meeting_url, meeting_title,
                    meeting_start, join_at, bot_id, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (calendar_event_id, calendar_account, meeting_url, meeting_title,
                 meeting_start, join_at, bot_id, status, now, now),
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        logger.debug(f"Duplicate bot entry for event {calendar_event_id}, skipping")
        return -1
    finally:
        conn.close()


def cancel_recall_bot(row_id: int):
    """Mark a recall bot as cancelled in DB."""
    ensure_db_schema()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE recall_bots SET status = 'cancelled', updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), row_id),
        )
        conn.commit()
    finally:
        conn.close()


def run_sync_cycle():
    """
    One complete sync cycle:
    1. Fetch events from all calendar accounts
    2. Determine which need bots
    3. Schedule new bots, update changed ones, cancel orphaned ones
    """
    ensure_db_schema()
    scheduler = CalendarScheduler()
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(hours=SYNC_WINDOW_HOURS)).isoformat()

    all_events = []
    for account in CALENDAR_ACCOUNTS:
        events = fetch_calendar_events_via_zo(account, time_min, time_max)
        if events is not None:
            for e in events:
                e["_calendar_account"] = account
            all_events.extend(events)

    if not all_events:
        logger.info("No upcoming events found across all accounts")
        # Still update sync state so we know poller ran
        update_sync_state("empty")
        return

    logger.info(f"Total events across all accounts: {len(all_events)}")

    all_events = _sanitize_event_fields(all_events)

    # Use existing CalendarScheduler for the heavy lifting
    results = scheduler.sync(all_events, dry_run=False)

    # Update sync state
    events_hash = str(hash(json.dumps([e.get("id", "") for e in all_events])))
    update_sync_state(events_hash)

    # Persist scheduled bots to meeting_pipeline.db
    for key, record in scheduler.state.get("synced_events", {}).items():
        event_match = next((e for e in all_events if scheduler.get_event_key(e) == key), None)
        account = event_match.get("_calendar_account", "") if event_match else ""

        upsert_recall_bot(
            calendar_event_id=key,
            calendar_account=account,
            meeting_url=record.get("meeting_url", ""),
            meeting_title=record.get("event_title", ""),
            meeting_start=record.get("event_start", ""),
            join_at=record.get("join_at", ""),
            bot_id=record.get("recall_bot_id"),
            status="scheduled" if record.get("recall_bot_id") else "pending",
        )

    logger.info(f"Sync cycle complete: {json.dumps(results)}")


def poller_loop():
    """
    Main poller loop. Runs forever, sleeping POLL_INTERVAL_SECONDS between cycles.
    Designed to run as a daemon thread.
    """
    logger.info(f"Calendar poller started (interval={POLL_INTERVAL_SECONDS}s, accounts={CALENDAR_ACCOUNTS})")
    ensure_db_schema()

    # Wait 30s on startup to let the webhook service fully initialize
    time.sleep(30)

    while True:
        try:
            logger.info("Starting calendar sync cycle...")
            run_sync_cycle()
        except Exception as e:
            logger.error(f"Sync cycle failed: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL_SECONDS)


def start_poller_thread() -> threading.Thread:
    """
    Start the calendar poller as a daemon thread.
    Call this from webhook_receiver startup.
    """
    thread = threading.Thread(target=poller_loop, name="calendar-poller", daemon=True)
    thread.start()
    logger.info("Calendar poller thread launched")
    return thread


# CLI for manual testing
if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Calendar Poller for Recall.ai")
    parser.add_argument("--once", action="store_true", help="Run one sync cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="Fetch events but don't schedule bots")
    parser.add_argument("--account", help="Sync specific account only")
    args = parser.parse_args()

    if args.once or args.dry_run:
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(hours=SYNC_WINDOW_HOURS)).isoformat()

        accounts = [args.account] if args.account else CALENDAR_ACCOUNTS
        all_events = []
        for account in accounts:
            events = fetch_calendar_events_via_zo(account, time_min, time_max)
            if events:
                for e in events:
                    e["_calendar_account"] = account
                all_events.extend(events)

        print(f"\nFetched {len(all_events)} events:")
        for e in all_events:
            start = e.get("start", {})
            start_time = start.get("dateTime") or start.get("date") if isinstance(start, dict) else str(start)
            print(f"  - {e.get('summary', 'Untitled')} @ {start_time}")

        if not args.dry_run:
            scheduler = CalendarScheduler()
            results = scheduler.sync(all_events, dry_run=False)
            print(f"\nSync results: {json.dumps(results, indent=2)}")
        else:
            scheduler = CalendarScheduler()
            results = scheduler.sync(all_events, dry_run=True)
            print(f"\n[DRY RUN] Results: {json.dumps(results, indent=2)}")
    else:
        poller_loop()
