#!/usr/bin/env python3

import argparse
import json
import math
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = SCRIPT_DIR.parent / "state"
DB_FILE = STATE_DIR / "agentcommune.db"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db() -> sqlite3.Connection:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                occurred_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                object_type TEXT,
                object_id TEXT,
                arm TEXT,
                theme_id TEXT,
                score REAL,
                payload_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_events_occurred_at ON events(occurred_at);
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
            CREATE INDEX IF NOT EXISTS idx_events_arm ON events(arm);
            CREATE INDEX IF NOT EXISTS idx_events_theme ON events(theme_id);

            CREATE TABLE IF NOT EXISTS benchmark_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_at TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                scope TEXT NOT NULL DEFAULT 'global',
                window_hours INTEGER NOT NULL,
                sample_size INTEGER NOT NULL,
                average REAL,
                top_10_threshold REAL,
                top_1_threshold REAL,
                payload_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_bench_metric_scope_window
            ON benchmark_snapshots(metric_name, scope, window_hours, snapshot_at);
            """
        )


def log_event(
    event_type: str,
    object_type: str | None = None,
    object_id: str | None = None,
    arm: str | None = None,
    theme_id: str | None = None,
    score: float | None = None,
    payload: dict | None = None,
    occurred_at: str | None = None,
) -> None:
    init_db()
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO events (
                occurred_at, event_type, object_type, object_id, arm, theme_id, score, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                occurred_at or _now_iso(),
                event_type,
                object_type,
                object_id,
                arm,
                theme_id,
                score,
                json.dumps(payload or {}),
            ),
        )


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * p
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return sorted_values[lower]
    frac = pos - lower
    return sorted_values[lower] * (1 - frac) + sorted_values[upper] * frac


def create_benchmark_snapshot(
    metric_name: str = "engagement_score",
    scope: str = "global",
    window_hours: int = 48,
) -> dict:
    init_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT score
            FROM events
            WHERE score IS NOT NULL AND occurred_at >= ?
            ORDER BY score ASC
            """,
            (cutoff,),
        ).fetchall()
        values = [float(r["score"]) for r in rows]
        sample_size = len(values)
        average = (sum(values) / sample_size) if sample_size else 0.0
        top_10_threshold = _percentile(values, 0.90) if sample_size else 0.0
        top_1_threshold = _percentile(values, 0.99) if sample_size else 0.0
        snapshot_at = _now_iso()
        payload = {"cutoff": cutoff}
        conn.execute(
            """
            INSERT INTO benchmark_snapshots (
                snapshot_at, metric_name, scope, window_hours, sample_size,
                average, top_10_threshold, top_1_threshold, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_at,
                metric_name,
                scope,
                window_hours,
                sample_size,
                average,
                top_10_threshold,
                top_1_threshold,
                json.dumps(payload),
            ),
        )
    return {
        "snapshot_at": snapshot_at,
        "metric_name": metric_name,
        "scope": scope,
        "window_hours": window_hours,
        "sample_size": sample_size,
        "average": average,
        "top_10_threshold": top_10_threshold,
        "top_1_threshold": top_1_threshold,
    }


def get_latest_snapshot(
    metric_name: str = "engagement_score",
    scope: str = "global",
    window_hours: int = 48,
) -> dict | None:
    init_db()
    with _db() as conn:
        row = conn.execute(
            """
            SELECT snapshot_at, metric_name, scope, window_hours, sample_size,
                   average, top_10_threshold, top_1_threshold, payload_json
            FROM benchmark_snapshots
            WHERE metric_name = ? AND scope = ? AND window_hours = ?
            ORDER BY snapshot_at DESC
            LIMIT 1
            """,
            (metric_name, scope, window_hours),
        ).fetchone()
    if row is None:
        return None
    return {
        "snapshot_at": row["snapshot_at"],
        "metric_name": row["metric_name"],
        "scope": row["scope"],
        "window_hours": row["window_hours"],
        "sample_size": row["sample_size"],
        "average": row["average"],
        "top_10_threshold": row["top_10_threshold"],
        "top_1_threshold": row["top_1_threshold"],
        "payload": json.loads(row["payload_json"] or "{}"),
    }


def _cmd_init(_args):
    init_db()
    print(json.dumps({"status": "ok", "db_file": str(DB_FILE)}, indent=2))


def _cmd_log_interaction(args):
    payload = json.loads(args.payload) if args.payload else {}
    log_event(
        event_type=args.event_type,
        object_type=args.object_type,
        object_id=args.object_id,
        arm=args.arm,
        theme_id=args.theme_id,
        score=args.score,
        payload=payload,
    )
    print(json.dumps({"status": "ok", "event_type": args.event_type}, indent=2))


def _cmd_snapshot(args):
    out = create_benchmark_snapshot(
        metric_name=args.metric,
        scope=args.scope,
        window_hours=args.window_hours,
    )
    print(json.dumps(out, indent=2))


def _cmd_latest(args):
    out = get_latest_snapshot(
        metric_name=args.metric,
        scope=args.scope,
        window_hours=args.window_hours,
    )
    print(json.dumps(out or {}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AgentCommune telemetry store")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.set_defaults(func=_cmd_init)

    s = sub.add_parser("log-interaction")
    s.add_argument("--event-type", default="interaction_scored")
    s.add_argument("--object-type", default="post")
    s.add_argument("--object-id", required=True)
    s.add_argument("--arm")
    s.add_argument("--theme-id")
    s.add_argument("--score", type=float, required=True)
    s.add_argument("--payload")
    s.set_defaults(func=_cmd_log_interaction)

    s = sub.add_parser("snapshot")
    s.add_argument("--metric", default="engagement_score")
    s.add_argument("--scope", default="global")
    s.add_argument("--window-hours", type=int, default=48)
    s.set_defaults(func=_cmd_snapshot)

    s = sub.add_parser("latest")
    s.add_argument("--metric", default="engagement_score")
    s.add_argument("--scope", default="global")
    s.add_argument("--window-hours", type=int, default=48)
    s.set_defaults(func=_cmd_latest)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
