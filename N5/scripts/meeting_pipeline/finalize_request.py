#!/usr/bin/env python3
"""
Finalize an AI meeting request after AI execution.
- Updates meeting status in the pipeline DB
- Moves processed command file to processed/
- Writes/updates response JSON

Usage:
  python3 finalize_request.py --request-id <id> --meeting-id <id> --status completed \
      --output-dir <path> [--notes "..."]

Status values: completed, failed
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import argparse
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REQUESTS = WORKSPACE / "N5/inbox/ai_requests"
RESPONSES = WORKSPACE / "N5/inbox/ai_responses"
PROCESSED = REQUESTS / "processed"
LOG_FILE = WORKSPACE / "N5/logs/meeting_request_processing.log"
DB_PATH = WORKSPACE / "N5/data/meeting_pipeline.db"


def update_db(meeting_id: str, status: str, notes: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        if status == "completed":
            cur.execute(
                "UPDATE meetings SET status=?, completed_at=?, notes=COALESCE(notes,'') || ? WHERE meeting_id=?",
                ("complete", now_iso, f"\nCompleted by AI executor {now_iso}", meeting_id)
            )
        elif status == "failed":
            cur.execute(
                "UPDATE meetings SET status=?, notes=COALESCE(notes,'') || ? WHERE meeting_id=?",
                ("failed", f"\nFailed by AI executor {now_iso}: {notes or ''}", meeting_id)
            )
        else:
            raise ValueError(f"Unsupported status: {status}")
        conn.commit()
    finally:
        conn.close()


def append_log(line: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(LOG_FILE.read_text() + line + "\n") if LOG_FILE.exists() else LOG_FILE.write_text(line + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-id", required=True)
    ap.add_argument("--meeting-id", required=True)
    ap.add_argument("--status", choices=["completed", "failed"], required=True)
    ap.add_argument("--output-dir", required=False)
    ap.add_argument("--notes", required=False)
    args = ap.parse_args()

    request_id = args.request_id
    meeting_id = args.meeting_id
    status = args.status

    # Update DB first
    update_db(meeting_id, status, args.notes)

    # Ensure response dir
    RESPONSES.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # Write or update response JSON
    resp = {
        "request_id": request_id,
        "meeting_id": meeting_id,
        "status": status,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": args.output_dir,
        "notes": args.notes or ""
    }
    (RESPONSES / f"{request_id}.json").write_text(json.dumps(resp, indent=2))

    # Move command file to processed if present
    cmd = REQUESTS / f"{request_id}_command.txt"
    if cmd.exists():
        dest = PROCESSED / cmd.name
        cmd.rename(dest)
        logger.info(f"Moved command file to processed/: {dest.name}")

    append_log(f"{datetime.now(timezone.utc).isoformat()}Z {status.upper()} {meeting_id} request={request_id}")
    logger.info(f"Finalized {request_id} as {status}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
