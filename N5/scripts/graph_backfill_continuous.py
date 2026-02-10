#!/usr/bin/env python3
"""Continuous Graph Backfill — runs until complete."""

import subprocess
import time
import sys
import json
from datetime import datetime
from pathlib import Path

BATCH_SIZE = 500
DELAY_BETWEEN_BATCHES = 30  # seconds
MAX_BACKOFF = 900
BASE_BACKOFF = 30
CONTROL_FILE = Path("/home/workspace/N5/config/backfill_control.json")

CONSECUTIVE_FAILURES = 0

def get_status():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/graph_backfill.py", "--status"],
        capture_output=True, text=True
    )
    for line in result.stdout.split('
'):
        if 'Remaining:' in line:
            return int(line.split(':')[1].strip().replace(',', ''))
    return 0

def should_stop():
    if CONTROL_FILE.exists():
        control = json.loads(CONTROL_FILE.read_text())
        return control.get('state') in ['stopped', 'paused']
    return False

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def main():
    global CONSECUTIVE_FAILURES
    log(f"Starting continuous backfill (batch_size={BATCH_SIZE})")
    CONTROL_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_FILE.write_text(json.dumps({"state": "active", "started": datetime.now().isoformat()}))
    batch_num = 0

    while True:
        if should_stop():
            log("Stop signal received. Exiting.")
            break
        remaining = get_status()
        if remaining == 0:
            log("✅ BACKFILL COMPLETE — all blocks processed!")
            CONTROL_FILE.write_text(json.dumps({"state": "complete", "finished": datetime.now().isoformat()}))
            break
        batch_num += 1
        log(f"Batch {batch_num}: Processing {min(BATCH_SIZE, remaining)} blocks ({remaining} remaining)")
        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/graph_backfill.py", "--batch", str(BATCH_SIZE)],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            CONSECUTIVE_FAILURES += 1
            backoff = min(BASE_BACKOFF * (2 ** CONSECUTIVE_FAILURES), MAX_BACKOFF)
            log(f"⚠️ Batch error: {result.stderr.strip()[:200]}")
            log(f"⚠️ Failure streak: {CONSECUTIVE_FAILURES}. Backing off {backoff}s before retrying.")
            time.sleep(backoff)
            continue

        CONSECUTIVE_FAILURES = 0
        log(f"Batch {batch_num} complete. Cooling down {DELAY_BETWEEN_BATCHES}s...")
        time.sleep(DELAY_BETWEEN_BATCHES)

    return 0

if __name__ == "__main__":
    sys.exit(main())
