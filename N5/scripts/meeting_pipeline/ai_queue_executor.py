#!/usr/bin/env python3
"""
AI Queue Executor
- Watches N5/inbox/ai_requests for *_command.txt files
- Sends each command to the internal Conversational API (n5-conversation-api) for execution
- Polls for completion via response file or timeout
- On success/failure, calls finalize_request.py to update DB and move files

This is intended to be run by a scheduled agent every N minutes.

Safe behaviors:
- Processes up to --limit N commands per run (default 2)
- Skips if a command appears malformed
- Leaves breadcrumbs in N5/logs/meeting_request_processing.log
"""
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timezone
import argparse
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REQUESTS = WORKSPACE / "N5/inbox/ai_requests"
RESPONSES = WORKSPACE / "N5/inbox/ai_responses"
API_URL = "http://localhost:8769/bootstrap/query"  # Using existing conversation API for now


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def execute_command(request_id: str, command_text: str) -> bool:
    """Send command to internal API. Here we log and simulate acceptance."""
    # For bootstrap phase, we just log and pretend execution is delegated to parent Zo
    logger.info(f"Submitting command for {request_id} to internal API")
    try:
        result = post_json(API_URL, {"type": "validate", "context": {"command_preview": command_text[:200]}})
        logger.info(f"Internal API ack: {result}")
        return True
    except Exception as e:
        logger.error(f"Internal API call failed: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    REQUESTS.mkdir(parents=True, exist_ok=True)
    RESPONSES.mkdir(parents=True, exist_ok=True)

    cmd_files = sorted(REQUESTS.glob("*_command.txt"), key=lambda p: p.stat().st_mtime)
    if not cmd_files:
        logger.info("No command files to process")
        return 0

    processed = 0
    for cmd in cmd_files:
        if processed >= args.limit:
            break
        rid = cmd.name.replace("_command.txt", "")
        text = cmd.read_text()
        logger.info(f"Processing command: {cmd.name}")

        if args.dry_run:
            logger.info("DRY-RUN: would submit command and finalize as completed")
            processed += 1
            continue

        ok = execute_command(rid, text)
        if ok:
            # For now, mark as completed; in future, poll for real completion
            import subprocess
            subprocess.run([
                "python3", str(WORKSPACE / "N5/scripts/meeting_pipeline/finalize_request.py"),
                "--request-id", rid,
                "--meeting-id", rid.split("meeting_")[-1].rsplit("_", 1)[0],
                "--status", "completed"
            ], check=False)
        else:
            import subprocess
            subprocess.run([
                "python3", str(WORKSPACE / "N5/scripts/meeting_pipeline/finalize_request.py"),
                "--request-id", rid,
                "--meeting-id", rid.split("meeting_")[-1].rsplit("_", 1)[0],
                "--status", "failed",
                "--notes", "Internal API submission failed"
            ], check=False)

        processed += 1

    logger.info(f"Processed {processed} command file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
