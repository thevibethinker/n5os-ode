#!/usr/bin/env python3
"""
Live Refresh — On-demand Moltbook refresh for Zøde.

Runs a full live refresh cycle and prints a concise status summary:
1) Pre-pop scan
2) Feed scanner opportunities/alerts
3) Engagement tracker live snapshot
4) Pre-pop evaluation
5) Short report output

Usage:
  python3 live_refresh.py run
"""

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def cmd_run(_: argparse.Namespace):
    steps = [
        ["python3", str(SCRIPTS_DIR / "pre_pop_detector.py"), "scan", "--limit", "80"],
        ["python3", str(SCRIPTS_DIR / "feed_scanner.py"), "run"],
        ["python3", str(SCRIPTS_DIR / "engagement_tracker.py"), "collect"],
        ["python3", str(SCRIPTS_DIR / "pre_pop_detector.py"), "evaluate", "--horizon-minutes", "60"],
        ["python3", str(SCRIPTS_DIR / "engagement_tracker.py"), "report", "--days", "1"],
    ]
    for step in steps:
        code, out, err = _run(step)
        print(f"\n$ {' '.join(step)}")
        if out.strip():
            print(out.rstrip())
        if err.strip():
            print(err.rstrip(), file=sys.stderr)
        if code != 0:
            raise SystemExit(code)


def main():
    parser = argparse.ArgumentParser(description="On-demand live refresh for Zøde Moltbook analytics")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Run full live refresh cycle")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
