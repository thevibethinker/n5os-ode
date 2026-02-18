#!/usr/bin/env python3
"""
Agent Conflict Gate — checks for duplicate or overlapping scheduled agents.

Returns exit codes:
  0 — No conflicts, proceed
  1 — Block: duplicate or hard-conflicting agents found
  2 — Warn: possible time overlap detected

Usage:
  python3 agent_conflict_gate.py --summary
  python3 agent_conflict_gate.py --check-log
  python3 agent_conflict_gate.py --summary --check-log --no-cache
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check for duplicate/overlapping scheduled agents before creating or reactivating one.",
        epilog="Exit codes: 0=proceed, 1=block (conflicts), 2=warn (overlap)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of all active agents and their schedules",
    )
    parser.add_argument(
        "--check-log",
        action="store_true",
        help="Check the conflict log for recent events",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force fresh scan, bypass any cached results",
    )
    parser.add_argument(
        "--agent-name",
        type=str,
        default=None,
        help="Name of the agent being created/reactivated (for targeted conflict check)",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        help="RRULE or cron expression of the proposed agent (for overlap detection)",
    )
    return parser.parse_args()


CONFLICT_LOG_PATH = Path(os.environ.get(
    "CONFLICT_LOG",
    os.path.expanduser("~/.n5/agent_conflict_log.jsonl"),
))


def load_agents_from_env():
    """
    Discover active agents.

    Strategy (in priority order):
      1. ZO_AGENTS_JSON env var pointing to a JSON file
      2. ~/.n5/agents.json
      3. Empty list (no agents discovered)

    Each agent dict should have at minimum: {name, schedule, active}
    """
    agents_file = os.environ.get("ZO_AGENTS_JSON")
    if agents_file and Path(agents_file).exists():
        with open(agents_file) as f:
            return json.load(f)

    fallback = Path(os.path.expanduser("~/.n5/agents.json"))
    if fallback.exists():
        with open(fallback) as f:
            return json.load(f)

    return []


def normalize_name(name: str) -> str:
    """Lowercase, strip whitespace, collapse separators."""
    return re.sub(r"[\s_-]+", "-", name.strip().lower())


def find_duplicate_names(agents: list, proposed_name: str = None) -> list:
    """Find agents with duplicate or near-duplicate names."""
    seen = {}
    duplicates = []
    for agent in agents:
        key = normalize_name(agent.get("name", ""))
        if key in seen:
            duplicates.append((agent["name"], seen[key]))
        else:
            seen[key] = agent["name"]

    if proposed_name:
        norm = normalize_name(proposed_name)
        if norm in seen:
            duplicates.append((proposed_name, seen[norm]))

    return duplicates


def parse_rrule_hour(schedule: str) -> int | None:
    """Extract hour from RRULE string if present."""
    m = re.search(r"BYHOUR=(\d+)", schedule, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def parse_cron_hour(schedule: str) -> int | None:
    """Extract hour from cron expression (minute hour ...)."""
    parts = schedule.strip().split()
    if len(parts) >= 2:
        try:
            return int(parts[1])
        except ValueError:
            return None
    return None


def get_hour(schedule: str) -> int | None:
    """Best-effort hour extraction from schedule string."""
    if not schedule:
        return None
    if "RRULE" in schedule.upper() or "FREQ" in schedule.upper():
        return parse_rrule_hour(schedule)
    return parse_cron_hour(schedule)


def find_time_overlaps(agents: list, proposed_schedule: str = None) -> list:
    """Find agents that run at the same hour."""
    by_hour = {}
    for agent in agents:
        h = get_hour(agent.get("schedule", ""))
        if h is not None:
            by_hour.setdefault(h, []).append(agent["name"])

    overlaps = []
    for hour, names in by_hour.items():
        if len(names) > 1:
            overlaps.append((hour, names))

    if proposed_schedule:
        ph = get_hour(proposed_schedule)
        if ph is not None and ph in by_hour:
            overlaps.append((ph, by_hour[ph] + ["[PROPOSED]"]))

    return overlaps


def log_conflict(event: dict):
    """Append a conflict event to the log file."""
    CONFLICT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(CONFLICT_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def read_conflict_log(n: int = 20) -> list:
    """Read the last n entries from the conflict log."""
    if not CONFLICT_LOG_PATH.exists():
        return []
    lines = CONFLICT_LOG_PATH.read_text().strip().splitlines()
    entries = []
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def print_summary(agents: list):
    """Print a human-readable summary of agents."""
    active = [a for a in agents if a.get("active", True)]
    inactive = [a for a in agents if not a.get("active", True)]

    print(f"Active agents: {len(active)}")
    print(f"Inactive agents: {len(inactive)}")
    print()

    if active:
        print("ACTIVE AGENTS:")
        for a in active:
            sched = a.get("schedule", "(no schedule)")
            print(f"  • {a.get('name', '(unnamed)')}: {sched}")
    else:
        print("No active agents found.")


def main():
    args = parse_args()
    agents = load_agents_from_env()
    exit_code = 0

    if args.summary:
        print_summary(agents)
        print()

    active_agents = [a for a in agents if a.get("active", True)]

    # Check for duplicate names
    dupes = find_duplicate_names(active_agents, args.agent_name)
    if dupes:
        print("⛔ DUPLICATE AGENTS DETECTED:")
        for proposed, existing in dupes:
            print(f"  \"{proposed}\" conflicts with existing \"{existing}\"")
        log_conflict({"type": "duplicate", "details": dupes})
        exit_code = 1

    # Check for time overlaps
    overlaps = find_time_overlaps(active_agents, args.schedule)
    if overlaps:
        print("⚠️  TIME OVERLAPS DETECTED:")
        for hour, names in overlaps:
            print(f"  Hour {hour:02d}:00 — {', '.join(names)}")
        if exit_code == 0:
            exit_code = 2
        log_conflict({"type": "overlap", "details": [(h, n) for h, n in overlaps]})

    if exit_code == 0:
        print("✅ No conflicts detected. Proceed.")

    if args.check_log:
        print()
        entries = read_conflict_log()
        if entries:
            print(f"RECENT CONFLICT LOG ({len(entries)} entries):")
            for e in entries:
                ts = e.get("timestamp", "?")
                t = e.get("type", "?")
                print(f"  [{ts}] {t}: {json.dumps(e.get('details', ''))}")
        else:
            print("No conflict log entries found.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
