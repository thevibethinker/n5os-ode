#!/usr/bin/env python3
"""
Experiment Heartbeat — portfolio evaluation loop for Zode.

Runs:
1) engagement snapshot refresh
2) experiment portfolio evaluation

Usage:
  python3 experiment_heartbeat.py run [--lookback-hours 24]
  python3 experiment_heartbeat.py status
"""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
EXPERIMENTS_DIR = STATE_DIR / "experiments"
HEARTBEAT_LOG = EXPERIMENTS_DIR / "experiment_heartbeat_log.jsonl"
PORTFOLIO_FILE = EXPERIMENTS_DIR / "portfolio_state.json"


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _append_log(payload: dict):
    HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(json.dumps(row) + "\n")


def cmd_run(args):
    scripts_dir = Path(__file__).resolve().parent

    collect_cmd = ["python3", str(scripts_dir / "engagement_tracker.py"), "collect"]
    eval_cmd = [
        "python3",
        str(scripts_dir / "experiment_portfolio.py"),
        "evaluate",
        "--lookback-hours",
        str(args.lookback_hours),
    ]

    c_code, c_out, c_err = _run(collect_cmd)
    e_code, e_out, e_err = _run(eval_cmd)

    # Collect step can fail in shells without MOLTBOOK_API_KEY. Evaluation can still run
    # against the latest saved snapshot, so treat this as degraded-not-fatal if evaluate works.
    if e_code == 0 and c_code == 0:
        status = "ok"
    elif e_code == 0 and c_code != 0:
        status = "degraded"
    else:
        status = "error"
    _append_log({
        "event": "run",
        "status": status,
        "collect_code": c_code,
        "evaluate_code": e_code,
    })

    print(f"$ {' '.join(collect_cmd)}")
    if c_out.strip():
        print(c_out.rstrip())
    if c_err.strip():
        print(c_err.rstrip())
    print()

    print(f"$ {' '.join(eval_cmd)}")
    if e_out.strip():
        print(e_out.rstrip())
    if e_err.strip():
        print(e_err.rstrip())

    if status == "error":
        raise SystemExit(1)


def cmd_status(_):
    if not HEARTBEAT_LOG.exists():
        print("No experiment heartbeat runs logged yet.")
        return

    lines = HEARTBEAT_LOG.read_text().splitlines()
    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    last = rows[-1] if rows else {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_runs = sum(1 for r in rows if r.get("timestamp", "").startswith(today))

    print("EXPERIMENT HEARTBEAT STATUS")
    print("=" * 60)
    print(f"Total runs: {len(rows)}")
    print(f"Runs today: {today_runs}")
    print(f"Last run: {last.get('timestamp', 'n/a')} ({last.get('status', 'n/a')})")

    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE) as f:
            portfolio = json.load(f)
        print()
        print(f"Portfolio floor_srs: {portfolio.get('floor_srs')}")
        print(f"Last portfolio eval: {portfolio.get('last_evaluation')}")
        slots = portfolio.get("slots", {})
        print(f"Slots: A={slots.get('A')} | B={slots.get('B')} | C={slots.get('C')}")
        print(f"Queue: {portfolio.get('challenger_queue', [])}")


def main():
    parser = argparse.ArgumentParser(
        description="Experiment Heartbeat — portfolio evaluation loop for Zode"
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Run one experiment heartbeat cycle")
    run.add_argument("--lookback-hours", type=int, default=24)
    sub.add_parser("status", help="Show experiment heartbeat status")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
