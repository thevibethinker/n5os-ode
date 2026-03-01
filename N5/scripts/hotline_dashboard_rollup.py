#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import duckdb

ZO_DB = "/home/workspace/Datasets/zo-hotline-calls/data.duckdb"
CAREER_DB = "/home/workspace/Datasets/career-hotline-calls/data.duckdb"
PILL_DB = "/home/workspace/Datasets/vibe-pill-calls/data.duckdb"


def run(days: int) -> dict:
    con = duckdb.connect()
    con.execute(f"ATTACH '{ZO_DB}' AS zo")
    con.execute(f"ATTACH '{CAREER_DB}' AS career")
    con.execute(f"ATTACH '{PILL_DB}' AS pill")

    query = """
WITH unified AS (
  SELECT 'zo-hotline' AS hotline, started_at, duration_seconds FROM zo.calls
  UNION ALL
  SELECT 'career-hotline' AS hotline, started_at, duration_seconds FROM career.calls
  UNION ALL
  SELECT 'vibe-pill' AS hotline, started_at, duration_seconds FROM pill.calls
),
windowed AS (
  SELECT
    hotline,
    started_at,
    duration_seconds,
    CAST(started_at - INTERVAL 5 HOUR AS DATE) AS date_et
  FROM unified
  WHERE started_at >= (NOW() - (? * INTERVAL 1 DAY))
),
per_hotline AS (
  SELECT
    hotline,
    COUNT(*) AS calls,
    COALESCE(SUM(duration_seconds), 0) AS total_seconds,
    ROUND(COALESCE(AVG(duration_seconds), 0), 1) AS avg_seconds
  FROM windowed
  GROUP BY hotline
),
per_day AS (
  SELECT
    date_et,
    hotline,
    COUNT(*) AS calls,
    ROUND(COALESCE(AVG(duration_seconds), 0), 1) AS avg_seconds
  FROM windowed
  GROUP BY date_et, hotline
),
totals AS (
  SELECT
    COUNT(*) AS calls,
    COALESCE(SUM(duration_seconds), 0) AS total_seconds,
    ROUND(COALESCE(AVG(duration_seconds), 0), 1) AS avg_seconds
  FROM windowed
)
SELECT
  (SELECT json_group_array(json_object('hotline', hotline, 'calls', calls, 'total_seconds', total_seconds, 'avg_seconds', avg_seconds)) FROM per_hotline) AS by_hotline,
  (
    SELECT json_group_array(
      json_object('date_et', CAST(date_et AS VARCHAR), 'hotline', hotline, 'calls', calls, 'avg_seconds', avg_seconds)
    )
    FROM (
      SELECT date_et, hotline, calls, avg_seconds
      FROM per_day
      ORDER BY date_et DESC, hotline
    )
  ) AS by_day_et,
  (SELECT json_object('calls', calls, 'total_seconds', total_seconds, 'avg_seconds', avg_seconds) FROM totals) AS totals
"""
    row = con.execute(query, [days]).fetchone()
    con.close()

    by_hotline = json.loads(row[0]) if row and row[0] else []
    by_day_et = json.loads(row[1]) if row and row[1] else []
    totals = json.loads(row[2]) if row and row[2] else {"calls": 0, "total_seconds": 0, "avg_seconds": 0}

    return {
        "days": days,
        "timezone_reporting": "ET (UTC-5 for current period)",
        "canonical_sources": [
            "Datasets/zo-hotline-calls/data.duckdb",
            "Datasets/career-hotline-calls/data.duckdb",
            "Datasets/vibe-pill-calls/data.duckdb",
        ],
        "excluded_sources": [
            "Datasets/vapi-calls/data.duckdb",
        ],
        "totals": totals,
        "by_hotline": by_hotline,
        "by_day_et": by_day_et,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical hotline dashboard rollup")
    parser.add_argument("--days", type=int, default=14, help="Rolling window in days")
    parser.add_argument("--out", type=str, default="", help="Optional output JSON path")
    args = parser.parse_args()

    payload = run(args.days)
    text = json.dumps(payload, indent=2)
    print(text)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n")
        print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
