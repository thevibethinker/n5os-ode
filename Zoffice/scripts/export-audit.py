#!/usr/bin/env python3
"""
Export audit trail from office.db to JSONL.

Usage:
    python export-audit.py [--since YYYY-MM-DD] [--capability CAP] [--output FILE]

Exports audit events for compliance, debugging, or archival.
"""

import argparse
import json
import os
import sys
from datetime import datetime

DB_PATH = "/home/workspace/Zoffice/data/office.db"


def export_audit(since=None, capability=None, output=None):
    try:
        import duckdb
    except ImportError:
        print("ERROR: duckdb not installed")
        sys.exit(1)

    if not os.path.isfile(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    con = duckdb.connect(DB_PATH, read_only=True)

    query = "SELECT * FROM audit WHERE 1=1"
    params = []

    if since:
        query += " AND timestamp >= ?"
        params.append(since)

    if capability:
        query += " AND capability = ?"
        params.append(capability)

    query += " ORDER BY timestamp DESC"

    rows = con.execute(query, params).fetchall()
    columns = [desc[0] for desc in con.description]
    con.close()

    records = []
    for row in rows:
        record = {}
        for col, val in zip(columns, row):
            if isinstance(val, datetime):
                val = val.isoformat()
            record[col] = val
        records.append(record)

    if output:
        with open(output, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        print(f"Exported {len(records)} events to {output}")
    else:
        for r in records:
            print(json.dumps(r))
        print(f"\n# {len(records)} events total", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Export Zoffice audit trail")
    parser.add_argument("--since", help="Export events since date (YYYY-MM-DD)")
    parser.add_argument("--capability", help="Filter by capability name")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    export_audit(since=args.since, capability=args.capability, output=args.output)


if __name__ == "__main__":
    main()
