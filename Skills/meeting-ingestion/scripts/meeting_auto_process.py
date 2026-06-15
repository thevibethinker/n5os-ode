#!/usr/bin/env python3
"""
Bounded meeting auto-processor for trigger-based Krisp imports and backlog sweeps.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- D1 sys.path injection for paths.py ---
from pathlib import Path as _D1Path
sys.path.insert(0, str(_D1Path(__file__).parent))

WORKSPACE = Path("/home/workspace")
from paths import ACTIVE_DIR as INBOX  # noqa: E402
MEETING_CLI = WORKSPACE / "Skills" / "meeting-ingestion" / "scripts" / "meeting_cli.py"
STATE_PATH = Path("/dev/shm/meeting-auto-process-state.json")
LOCK_PATH = Path("/dev/shm/meeting-auto-process.lock")
RUN_LOG_PATH = Path("/dev/shm/meeting-auto-process.log")

DEFAULT_MAX_CONCURRENT = 3
DEFAULT_POLL_SECONDS = 5
DEFAULT_WAIT_TIMEOUT_SECONDS = 4 * 60 * 60


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _resolve_target(raw_target: str) -> tuple[str, Path]:
    target_path = Path(raw_target).expanduser()
    if not target_path.is_absolute():
        target_path = INBOX / raw_target
    target_path = target_path.resolve()
    if not target_path.exists() or not target_path.is_dir():
        raise FileNotFoundError(f"Meeting folder not found: {target_path}")
    return target_path.name, target_path


def _read_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"running": []}
    try:
        payload = json.loads(STATE_PATH.read_text())
    except json.JSONDecodeError:
        return {"running": []}
    if not isinstance(payload, dict):
        return {"running": []}
    running = payload.get("running")
    if not isinstance(running, list):
        payload["running"] = []
    return payload


def _write_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2))


def _prune_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pruned: list[dict[str, Any]] = []
    for entry in entries:
        pid = entry.get("pid")
        target = entry.get("target")
        if not isinstance(pid, int) or not isinstance(target, str):
            continue
        if _pid_alive(pid):
            pruned.append(entry)
    return pruned


def _acquire_slot(target: str, max_concurrent: int, poll_seconds: int, wait_timeout: int) -> dict[str, Any]:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    started_waiting = time.time()

    with LOCK_PATH.open("a+", encoding="utf-8") as lock_file:
        while True:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                state = _read_state()
                running = _prune_entries(state.get("running", []))
                state["running"] = running

                if any(entry.get("target") == target for entry in running):
                    _write_state(state)
                    return {"status": "duplicate_running", "running": len(running)}

                if len(running) < max_concurrent:
                    entry = {
                        "pid": os.getpid(),
                        "target": target,
                        "started_at": _ts(),
                    }
                    running.append(entry)
                    state["running"] = running
                    _write_state(state)
                    return {"status": "acquired", "running": len(running)}

                _write_state(state)
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

            if time.time() - started_waiting > wait_timeout:
                return {"status": "timeout", "running": max_concurrent}
            time.sleep(poll_seconds)


def _release_slot(target: str) -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            state = _read_state()
            running = _prune_entries(state.get("running", []))
            running = [
                entry for entry in running
                if not (entry.get("pid") == os.getpid() and entry.get("target") == target)
            ]
            state["running"] = running
            _write_state(state)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run meeting auto-processing with bounded concurrency.")
    parser.add_argument("meeting", help="Meeting folder name in Inbox or absolute path to the meeting folder")
    parser.add_argument("--max-concurrent", type=int, default=DEFAULT_MAX_CONCURRENT, help=f"Max concurrent meeting processors (default: {DEFAULT_MAX_CONCURRENT})")
    parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS, help=f"Seconds between slot checks while waiting (default: {DEFAULT_POLL_SECONDS})")
    parser.add_argument("--wait-timeout", type=int, default=DEFAULT_WAIT_TIMEOUT_SECONDS, help=f"Max seconds to wait for a free slot (default: {DEFAULT_WAIT_TIMEOUT_SECONDS})")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    target_name, target_path = _resolve_target(args.meeting)
    slot = _acquire_slot(target_name, args.max_concurrent, args.poll_seconds, args.wait_timeout)
    if slot["status"] == "duplicate_running":
        payload = {"meeting": target_name, "path": str(target_path), **slot}
        print(json.dumps(payload, indent=2) if args.json else f"Skipping {target_name}: already running")
        return 0
    if slot["status"] == "timeout":
        payload = {"meeting": target_name, "path": str(target_path), **slot}
        print(json.dumps(payload, indent=2) if args.json else f"Timed out waiting for slot for {target_name}")
        return 1

    cmd = [
        sys.executable,
        str(MEETING_CLI),
        "tick",
        "--target",
        target_name,
        "--auto-process",
    ]

    try:
        RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG_PATH.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"[{_ts()}] start {target_name}\n")
            log_handle.flush()
            proc = subprocess.run(
                cmd,
                cwd=str(WORKSPACE),
                check=False,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            log_handle.write(f"[{_ts()}] end {target_name} rc={proc.returncode}\n")
            log_handle.flush()
        payload = {
            "meeting": target_name,
            "path": str(target_path),
            "status": "completed" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode,
            "log_path": str(RUN_LOG_PATH),
        }
        print(json.dumps(payload, indent=2) if args.json else f"{payload['status']}: {target_name} (rc={proc.returncode})")
        return proc.returncode
    finally:
        _release_slot(target_name)


if __name__ == "__main__":
    raise SystemExit(main())
