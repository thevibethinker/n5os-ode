#!/usr/bin/env python3
"""
init_db.py — Initialize the Career Coaching Hotline DuckDB database.

Creates all tables idempotently (safe to run multiple times).
Tables: calls, escalations, feedback, daily_analysis, caller_profiles, caller_insights.

Usage:
    python3 Skills/career-coaching-hotline/scripts/init_db.py
    python3 Skills/career-coaching-hotline/scripts/init_db.py --dry-run
    python3 Skills/career-coaching-hotline/scripts/init_db.py --verify
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

DB_PATH = Path("/home/workspace/Datasets/career-coaching-calls/data.duckdb")

TABLES: dict[str, str] = {
    "calls": """
        CREATE TABLE IF NOT EXISTS calls (
            id VARCHAR PRIMARY KEY,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            duration_seconds INTEGER,
            caller_phone VARCHAR,
            caller_profile_id VARCHAR,
            topics_discussed TEXT,
            career_stage_assessed VARCHAR,
            escalation_requested BOOLEAN,
            raw_data JSON
        )
    """,
    "escalations": """
        CREATE TABLE IF NOT EXISTS escalations (
            id VARCHAR PRIMARY KEY,
            call_id VARCHAR,
            name VARCHAR,
            contact VARCHAR,
            career_stage VARCHAR,
            reason TEXT,
            booking_link_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP
        )
    """,
    "feedback": """
        CREATE TABLE IF NOT EXISTS feedback (
            id VARCHAR PRIMARY KEY,
            call_id VARCHAR,
            caller_name VARCHAR,
            satisfaction INTEGER,
            comment TEXT,
            created_at TIMESTAMP
        )
    """,
    "daily_analysis": """
        CREATE TABLE IF NOT EXISTS daily_analysis (
            id VARCHAR PRIMARY KEY,
            analysis_date DATE,
            period_start TIMESTAMP,
            period_end TIMESTAMP,
            total_calls INTEGER,
            substantive_calls INTEGER,
            dropoff_calls INTEGER,
            avg_duration DOUBLE,
            avg_satisfaction DOUBLE,
            career_stages_json JSON,
            topics_json JSON,
            careerspan_conversions INTEGER,
            patterns_json JSON,
            improvements_json JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "caller_profiles": """
        CREATE TABLE IF NOT EXISTS caller_profiles (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            phone VARCHAR NOT NULL,
            email VARCHAR,
            linkedin_url VARCHAR,
            career_stage VARCHAR,
            help_topic TEXT,
            resume_text TEXT,
            caller_brief TEXT,
            source VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_call_at TIMESTAMP,
            call_count INTEGER DEFAULT 0
        )
    """,
    "caller_insights": """
        CREATE TABLE IF NOT EXISTS caller_insights (
            id VARCHAR PRIMARY KEY,
            first_name VARCHAR,
            phone VARCHAR,
            topics_discussed TEXT,
            career_stage VARCHAR,
            total_calls INTEGER DEFAULT 0,
            avg_satisfaction DOUBLE,
            first_call_at TIMESTAMP,
            last_call_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
}

INDEXES: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_caller_phone ON caller_profiles(phone)",
    "CREATE INDEX IF NOT EXISTS idx_calls_started ON calls(started_at)",
    "CREATE INDEX IF NOT EXISTS idx_calls_career_stage ON calls(career_stage_assessed)",
    "CREATE INDEX IF NOT EXISTS idx_escalations_call ON escalations(call_id)",
    "CREATE INDEX IF NOT EXISTS idx_feedback_call ON feedback(call_id)",
    "CREATE INDEX IF NOT EXISTS idx_daily_analysis_date ON daily_analysis(analysis_date)",
    "CREATE INDEX IF NOT EXISTS idx_insights_phone ON caller_insights(phone)",
]


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", file=sys.stderr)


def init_database(dry_run: bool = False) -> int:
    """Create all tables and indexes. Returns 0 on success, 1 on failure."""
    log(f"Database path: {DB_PATH}")

    if dry_run:
        log("[DRY RUN] Would create the following tables:")
        for name in TABLES:
            log(f"  - {name}")
        log(f"  + {len(INDEXES)} indexes")
        return 0

    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(str(DB_PATH))

        for name, ddl in TABLES.items():
            log(f"Creating table: {name}")
            conn.execute(ddl)

        for idx_sql in INDEXES:
            idx_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ON")[0]
            log(f"Creating index: {idx_name}")
            conn.execute(idx_sql)

        conn.close()
        log("Database initialized successfully.")
        return 0

    except duckdb.Error as e:
        log(f"ERROR: DuckDB error: {e}")
        return 1
    except OSError as e:
        log(f"ERROR: File system error: {e}")
        return 1


def verify_database() -> int:
    """Verify all tables and indexes exist. Returns 0 if valid, 1 if issues."""
    if not DB_PATH.exists():
        log(f"ERROR: Database not found at {DB_PATH}")
        return 1

    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)
        existing = {r[0] for r in conn.execute("SHOW TABLES").fetchall()}
        expected = set(TABLES.keys())

        missing = expected - existing
        if missing:
            log(f"ERROR: Missing tables: {', '.join(sorted(missing))}")
            conn.close()
            return 1

        for table in sorted(expected):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            cols = conn.execute(f"DESCRIBE {table}").fetchall()
            log(f"  ✓ {table}: {len(cols)} columns, {count} rows")

        conn.close()
        log("All tables verified.")
        return 0

    except duckdb.Error as e:
        log(f"ERROR: Verification failed: {e}")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize Career Coaching Hotline DuckDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Create database and tables
  %(prog)s --dry-run    # Preview without creating
  %(prog)s --verify     # Check existing database
""",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--verify", action="store_true", help="Verify existing database")

    args = parser.parse_args()

    if args.verify:
        sys.exit(verify_database())
    else:
        rc = init_database(dry_run=args.dry_run)
        if rc == 0 and not args.dry_run:
            log("Running verification...")
            verify_database()
        sys.exit(rc)


if __name__ == "__main__":
    main()
