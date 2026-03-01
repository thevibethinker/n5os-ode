#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import duckdb

DATASETS = {
    "zo-hotline": ("/home/workspace/Datasets/zo-hotline-calls/data.duckdb", "general_advisory"),
    "career-hotline": ("/home/workspace/Datasets/career-hotline-calls/data.duckdb", "general"),
    "vibe-pill": ("/home/workspace/Datasets/vibe-pill-calls/data.duckdb", "general"),
}


def summarize(con: duckdb.DuckDBPyConnection) -> dict:
    row = con.execute(
        """
        SELECT
          COUNT(*) AS total_rows,
          SUM(CASE WHEN ended_at = started_at AND COALESCE(duration_seconds, 0) > 0 THEN 1 ELSE 0 END) AS zero_span_with_duration,
          SUM(CASE WHEN topics_discussed IS NULL OR TRIM(topics_discussed) = '' THEN 1 ELSE 0 END) AS null_or_blank_topics
        FROM calls
        """
    ).fetchone()
    return {
        "total_rows": int(row[0] or 0),
        "zero_span_with_duration": int(row[1] or 0),
        "null_or_blank_topics": int(row[2] or 0),
    }


def apply_backfill(con: duckdb.DuckDBPyConnection, topic_fallback: str) -> dict:
    con.execute("BEGIN TRANSACTION")
    timestamp_updates = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM calls
            WHERE ended_at = started_at
              AND COALESCE(duration_seconds, 0) > 0
            """
        ).fetchone()[0]
        or 0
    )
    con.execute(
        """
        UPDATE calls
        SET ended_at = started_at + (COALESCE(duration_seconds, 0) * INTERVAL 1 SECOND)
        WHERE ended_at = started_at
          AND COALESCE(duration_seconds, 0) > 0
        """
    )
    topic_updates = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM calls
            WHERE topics_discussed IS NULL OR TRIM(topics_discussed) = ''
            """
        ).fetchone()[0]
        or 0
    )
    con.execute(
        """
        UPDATE calls
        SET topics_discussed = ?
        WHERE topics_discussed IS NULL OR TRIM(topics_discussed) = ''
        """,
        [topic_fallback],
    )
    con.execute("COMMIT")
    return {"timestamp_updates": timestamp_updates, "topic_updates": topic_updates}


def run(apply: bool) -> dict:
    report = {"mode": "apply" if apply else "dry-run", "datasets": {}}
    for name, (db_path, fallback) in DATASETS.items():
        con = duckdb.connect(db_path)
        before = summarize(con)
        changes = {"timestamp_updates": 0, "topic_updates": 0}
        if apply:
            changes = apply_backfill(con, fallback)
        after = summarize(con)
        con.close()
        report["datasets"][name] = {
            "db_path": db_path,
            "topic_fallback": fallback,
            "before": before,
            "changes": changes,
            "after": after,
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill hotline call timestamp/topic anomalies")
    parser.add_argument("--apply", action="store_true", help="Apply updates (default is dry-run)")
    parser.add_argument("--out", type=str, default="", help="Optional output JSON path")
    args = parser.parse_args()

    report = run(apply=args.apply)
    text = json.dumps(report, indent=2)
    print(text)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n")
        print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
