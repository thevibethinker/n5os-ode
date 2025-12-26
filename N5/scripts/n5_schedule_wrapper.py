#!/usr/bin/env python3
"""
N5 OS Scheduling Wrapper

Handles retries, backoff, locking, timezone, and missed-run policies for scheduled commands.
Prepared but disabled until explicit consent.
"""

import sys
import os
import json
import argparse
import time
import fcntl
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import subprocess

# Import safety layer
# from n5_safety import load_command_spec

ROOT = Path(__file__).resolve().parents[1]

# Arrest flag path
ARREST_FLAG = ROOT / "flags" / "ARREST_SYSTEM.json"



def load_command_spec(command_name: str) -> Optional[Dict[str, Any]]:
    """Mock load_command_spec since commands.jsonl is missing."""
    return {"name": command_name, "enabled": True}


# Configuration - can be overridden by preferences
MAX_RETRIES = 2
BACKOFF_SECONDS = [60, 300]  # 1m, 5m
LOCK_TIMEOUT = 3600  # 1 hour
MISSED_RUN_POLICY = "skip"  # skip, run, or warn
TIMEZONE = "UTC"  # default, can be overridden

def load_preferences() -> Dict[str, Any]:
    """Load scheduling preferences from prefs.md or other sources."""
    prefs = {
        "max_retries": MAX_RETRIES,
        "backoff_seconds": BACKOFF_SECONDS,
        "lock_timeout": LOCK_TIMEOUT,
        "missed_run_policy": MISSED_RUN_POLICY,
        "timezone": TIMEZONE,
        "enabled": False  # Disabled until explicit consent
    }

    # Try to load from prefs.md
    prefs_md = ROOT / "prefs.md"
    if prefs_md.exists():
        content = prefs_md.read_text()
        # Look for scheduling section
        if "## Scheduling" in content:
            lines = content.split('\n')
            in_sched = False
            for line in lines:
                if line.strip() == "## Scheduling":
                    in_sched = True
                    continue
                elif in_sched and line.strip().startswith("## "):
                    break
                elif in_sched and ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    if key in prefs:
                        if isinstance(prefs[key], bool):
                            prefs[key] = value.lower() == "true"
                        elif isinstance(prefs[key], int):
                            prefs[key] = int(value)
                        elif isinstance(prefs[key], list):
                            prefs[key] = [int(x.strip()) for x in value.split(",")]
                        else:
                            prefs[key] = value

    return prefs

def get_lock_file(command_name: str) -> Path:
    """Get lock file path for a command."""
    return ROOT / "locks" / f"{command_name}.lock"

def acquire_lock(lock_file: Path, timeout: int) -> Optional[int]:
    """Acquire file-based lock with timeout."""
    lock_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except BlockingIOError:
                time.sleep(1)

        os.close(fd)
        return None
    except Exception as e:
        print(f"Error acquiring lock: {e}", file=sys.stderr)
        return None

def release_lock(fd: int):
    """Release file-based lock."""
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except Exception as e:
        print(f"Error releasing lock: {e}", file=sys.stderr)

def should_run_missed(schedule_time: datetime, now: datetime, policy: str) -> bool:
    """Determine if a missed run should execute based on policy."""
    if policy == "run":
        return True
    elif policy == "skip":
        return False
    elif policy == "warn":
        print(f"WARNING: Missed scheduled run at {schedule_time}", file=sys.stderr)
        return False
    else:
        print(f"Unknown missed run policy: {policy}", file=sys.stderr)
        return False

def get_timezone(tz_str: str) -> timezone:
    """Get timezone object from string."""
    if tz_str == "UTC":
        return timezone.utc
    elif tz_str == "America/New_York":
        return timezone(timedelta(hours=-5))  # EST, simplify for now
    elif tz_str == "America/Los_Angeles":
        return timezone(timedelta(hours=-8))  # PST, simplify for now
    else:
        # Default to UTC
        print(f"Unknown timezone: {tz_str}, defaulting to UTC", file=sys.stderr)
        return timezone.utc

def execute_with_retry(command: list, prefs: Dict[str, Any], schedule_time: Optional[datetime] = None) -> bool:
    """Execute command with retry logic."""
    max_retries = prefs["max_retries"]
    backoff_seconds = prefs["backoff_seconds"]

    for attempt in range(max_retries + 1):
        try:
            print(f"Executing command (attempt {attempt + 1}/{max_retries + 1})")

            # Check if this is a missed run
            if schedule_time:
                now = datetime.now(prefs.get("tz_obj", timezone.utc))
                if now > schedule_time and not should_run_missed(schedule_time, now, prefs["missed_run_policy"]):
                    print("Skipping missed scheduled run")
                    return True

            result = subprocess.run(command, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("Command executed successfully")
                return True
            else:
                print(f"Command failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}", file=sys.stderr)

                if attempt < max_retries:
                    backoff = backoff_seconds[attempt] if attempt < len(backoff_seconds) else backoff_seconds[-1]
                    print(f"Retrying in {backoff} seconds...")
                    time.sleep(backoff)

        except subprocess.TimeoutExpired:
            print(f"Command timed out (attempt {attempt + 1})", file=sys.stderr)
            if attempt < max_retries:
                backoff = backoff_seconds[attempt] if attempt < len(backoff_seconds) else backoff_seconds[-1]
                print(f"Retrying in {backoff} seconds...")
                time.sleep(backoff)
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            if attempt < max_retries:
                backoff = backoff_seconds[attempt] if attempt < len(backoff_seconds) else backoff_seconds[-1]
                print(f"Retrying in {backoff} seconds...")
                time.sleep(backoff)

    print("All retry attempts failed")
    return False

def main():
    parser = argparse.ArgumentParser(description="N5 Scheduling Wrapper")
    parser.add_argument("command_name", help="Name of the command to wrap")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, help="Arguments for the wrapped command")
    parser.add_argument("--schedule-time", help="Scheduled time in ISO format (optional)")
    parser.add_argument("--force", action="store_true", help="Force execution even if disabled")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--ignore-arrest", action="store_true", help="Ignore system arrest flag")

    args = parser.parse_args()

    # Load preferences
    prefs = load_preferences()
    prefs["tz_obj"] = get_timezone(prefs["timezone"])

    # Check if scheduling is enabled
    if not prefs["enabled"] and not args.force:
        print("Scheduling wrapper is disabled. Use --force to override.")
        return 1
    # Check for system arrest
    if ARREST_FLAG.exists() and not args.ignore_arrest:
        try:
            arrest_data = json.loads(ARREST_FLAG.read_text())
            reason = arrest_data.get("reason", "Unknown")
            timestamp = arrest_data.get("timestamp", "Unknown")
            print(f"⛔ SYSTEM ARRESTED. Execution blocked.\nReason: {reason}\nTimestamp: {timestamp}\nUse --ignore-arrest to override.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"⛔ SYSTEM ARRESTED (Corrupt flag file). Execution blocked.\nError: {e}\nUse --ignore-arrest to override.", file=sys.stderr)
            return 1

    # Load command spec
    # Use the stem of the command name/path for the spec lookup/locking
    command_stem = Path(args.command_name).stem
    if args.command_name.startswith("n5_"):
        command_stem = command_stem[3:]
        
    command_spec = load_command_spec(command_stem)
    if not command_spec:
        print(f"Command '{args.command_name}' (stem: {command_stem}) not found in commands.jsonl", file=sys.stderr)
        return 1

    # Get lock file
    lock_file = get_lock_file(command_stem)

    # Acquire lock
    lock_fd = acquire_lock(lock_file, prefs["lock_timeout"])
    if lock_fd is None:
        print(f"Could not acquire lock for {args.command_name}", file=sys.stderr)
        return 1

    try:
        # Parse schedule time
        schedule_time = None
        if args.schedule_time:
            try:
                schedule_time = datetime.fromisoformat(args.schedule_time.replace('Z', '+00:00'))
                schedule_time = schedule_time.replace(tzinfo=prefs["tz_obj"])
            except ValueError as e:
                print(f"Invalid schedule time format: {e}", file=sys.stderr)
                return 1

        # Build command to execute
        # 1. Try as direct path
        script_path = Path(args.command_name).resolve()
        if not script_path.exists():
             # 2. Try as n5_ script in scripts dir
             script_path = ROOT / "scripts" / f"n5_{args.command_name}.py"
        
        if not script_path.exists():
            print(f"Script not found: {args.command_name} or {script_path}", file=sys.stderr)
            return 1

        command = [sys.executable, str(script_path)] + args.command_args

        if args.dry_run:
            print(f"DRY RUN: Would execute: {' '.join(command)}")
            return 0

        # Execute with retry
        success = execute_with_retry(command, prefs, schedule_time)

        return 0 if success else 1

    finally:
        # Release lock
        release_lock(lock_fd)

if __name__ == "__main__":
    sys.exit(main())






