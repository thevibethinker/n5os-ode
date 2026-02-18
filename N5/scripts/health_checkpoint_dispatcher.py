#!/usr/bin/env python3
"""Health Checkpoint Dispatcher

Single-agent dispatcher that runs on an hourly-ish schedule and fires
whichever health checkpoint(s) are due for the current hour.

Reads the schedule from regimen.json (SSOT) via health_checkpoint.py.
Delegates actual content generation to health_checkpoint.py.

Usage:
    python3 health_checkpoint_dispatcher.py              # Fire due checkpoint(s)
    python3 health_checkpoint_dispatcher.py --dry-run    # Show what would fire
    python3 health_checkpoint_dispatcher.py --list       # Show full schedule
    python3 health_checkpoint_dispatcher.py --force wake # Force a specific checkpoint
"""

import argparse
import json
import subprocess
import sys
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
CHECKPOINT_SCRIPT = SCRIPT_DIR / "health_checkpoint.py"
LOG_PATH = Path("/home/workspace/N5/logs/health_checkpoint_dispatcher.log")
ET = ZoneInfo("America/New_York")

SCHEDULE = {
    7:  [("wake", 0)],
    8:  [("post_shake", 30)],
    9:  [("one_meal", 0)],
    18: [("evening", 0)],
    22: [("presleep", 0)],
}


def get_due_checkpoints(now: datetime) -> list[tuple[str, int]]:
    """Return checkpoint names due for the current hour."""
    return SCHEDULE.get(now.hour, [])


def run_checkpoint(name: str, dry_run: bool = False) -> dict:
    """Run health_checkpoint.py for a given checkpoint name."""
    cmd = [
        sys.executable,
        str(CHECKPOINT_SCRIPT),
        "--checkpoint", name,
    ]
    if dry_run:
        logger.info(f"[DRY-RUN] Would run: {' '.join(cmd)}")
        return {"checkpoint": name, "status": "dry_run", "output": ""}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=60,
            env={"PYTHONPATH": "/home/workspace", **__import__("os").environ},
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            logger.error(f"Checkpoint {name} failed (exit {result.returncode}): {result.stderr}")
            return {"checkpoint": name, "status": "error", "output": result.stderr}
        logger.info(f"Checkpoint {name} succeeded")
        return {"checkpoint": name, "status": "ok", "output": output}
    except subprocess.TimeoutExpired:
        logger.error(f"Checkpoint {name} timed out")
        return {"checkpoint": name, "status": "timeout", "output": ""}


def append_log(checkpoint: str, status: str) -> None:
    """Append to dispatcher log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(ET).isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(f"{ts} | checkpoint={checkpoint} | status={status}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Health Checkpoint Dispatcher")
    parser.add_argument("--dry-run", action="store_true", help="Show what would fire without executing")
    parser.add_argument("--list", action="store_true", help="Show full schedule")
    parser.add_argument("--force", type=str, help="Force a specific checkpoint by name")
    args = parser.parse_args()

    if args.list:
        print("Health Checkpoint Schedule:")
        for hour in sorted(SCHEDULE.keys()):
            for name, minute in SCHEDULE[hour]:
                print(f"  {hour:02d}:{minute:02d} ET — {name}")
        return 0

    now = datetime.now(ET)

    if args.force:
        checkpoints = [(args.force, 0)]
    else:
        checkpoints = get_due_checkpoints(now)

    if not checkpoints:
        logger.info(f"No checkpoints due at {now.strftime('%H:%M')} ET")
        print(f"No checkpoints due at {now.strftime('%H:%M')} ET")
        return 0

    results = []
    for name, _minute in checkpoints:
        result = run_checkpoint(name, dry_run=args.dry_run)
        results.append(result)
        if not args.dry_run:
            append_log(name, result["status"])

    print(json.dumps(results, indent=2))

    if any(r["status"] == "error" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
