#!/usr/bin/env python3
"""
Inbox Poller — Lightweight daemon thread for detecting new drops.

Polls the Inbox every 60 seconds for:
1. Raw transcript files (.md, .txt, .jsonl) → triggers ingest
2. Meeting folders at 'ingested' status → triggers full pipeline processing

Designed to run as a daemon thread inside the webhook receiver service,
similar to how calendar_poller.py runs.

Usage:
    # As a daemon thread (called from webhook_receiver.py startup):
    from inbox_poller import start_inbox_poller_thread

    # Standalone (for testing):
    python3 inbox_poller.py
"""

import json
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
CLI_PATH = "/home/workspace/Skills/meeting-ingestion/scripts/meeting_cli.py"
POLL_INTERVAL = 60  # seconds
PROCESSED_MARKER = ".inbox_poller_seen"  # Tracks what we've already triggered

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _get_seen_set() -> set:
    """Load the set of already-seen items to avoid re-triggering."""
    marker_path = INBOX / PROCESSED_MARKER
    if marker_path.exists():
        try:
            return set(json.loads(marker_path.read_text()))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def _save_seen_set(seen: set):
    """Persist the seen set."""
    marker_path = INBOX / PROCESSED_MARKER
    marker_path.write_text(json.dumps(sorted(seen)))


def poll_once():
    """Run one poll cycle. Returns count of actions triggered."""
    if not INBOX.exists():
        return 0

    seen = _get_seen_set()
    actions = 0

    # 1. Check for raw transcript files
    raw_files = [
        f for f in INBOX.iterdir()
        if f.is_file()
        and f.suffix in [".md", ".txt", ".jsonl"]
        and not f.name.startswith(".")
        and f.name not in seen
    ]

    for raw_file in raw_files:
        logger.info(f"Inbox poller: found raw file {raw_file.name}, triggering ingest")
        try:
            log_path = f"/dev/shm/inbox-ingest-{raw_file.stem}.log"
            subprocess.Popen(
                [sys.executable, CLI_PATH, "ingest", str(raw_file)],
                stdout=open(log_path, "w"),
                stderr=subprocess.STDOUT,
            )
            seen.add(raw_file.name)
            actions += 1
        except Exception as e:
            logger.error(f"Inbox poller: failed to trigger ingest for {raw_file.name}: {e}")

    # 2. Check for meeting folders at 'ingested' status that haven't been triggered
    for item in INBOX.iterdir():
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue

        trigger_key = f"process:{item.name}"
        if trigger_key in seen:
            continue

        manifest_path = item / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            manifest = json.loads(manifest_path.read_text())
            status = manifest.get("status", "")
        except (json.JSONDecodeError, OSError):
            continue

        if status == "ingested":
            logger.info(f"Inbox poller: found unprocessed meeting {item.name}, triggering pipeline")
            try:
                log_path = f"/dev/shm/meeting-process-{item.name}.log"
                subprocess.Popen(
                    [sys.executable, CLI_PATH, "tick", "--auto-process", "--target", item.name],
                    stdout=open(log_path, "w"),
                    stderr=subprocess.STDOUT,
                )
                seen.add(trigger_key)
                actions += 1
            except Exception as e:
                logger.error(f"Inbox poller: failed to trigger processing for {item.name}: {e}")

    _save_seen_set(seen)
    return actions


def poll_loop():
    """Continuous polling loop. Runs forever (designed for daemon thread)."""
    logger.info(f"Inbox poller started (interval: {POLL_INTERVAL}s)")
    while True:
        try:
            actions = poll_once()
            if actions > 0:
                logger.info(f"Inbox poller: triggered {actions} action(s)")
        except Exception as e:
            logger.error(f"Inbox poller error: {e}")
        time.sleep(POLL_INTERVAL)


def start_inbox_poller_thread():
    """Start the inbox poller as a daemon thread."""
    thread = threading.Thread(target=poll_loop, daemon=True, name="inbox-poller")
    thread.start()
    logger.info("Inbox poller daemon thread started")
    return thread


if __name__ == "__main__":
    # Standalone mode for testing
    print(f"Running single poll cycle on {INBOX}...")
    actions = poll_once()
    print(f"Actions triggered: {actions}")
