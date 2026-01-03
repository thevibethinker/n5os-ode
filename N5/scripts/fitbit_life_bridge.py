#!/usr/bin/env python3
"""
Fitbit → Life Counter Bridge

Syncs Fitbit workouts from workouts.db to Life Counter (life_logs in wellness.db).
Maintains structured workout metrics (distance, calories, HR, duration) alongside
human-readable notes.

Usage:
    python3 fitbit_life_bridge.py sync [--days N]
    python3 fitbit_life_bridge.py backfill
    python3 fitbit_life_bridge.py status
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

from N5.lib.paths import WORKOUTS_DB, WELLNESS_DB

SOURCE_LABEL = "fitbit"


def get_workout_category_id(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT id FROM life_categories WHERE slug = 'workout'")
    row = cur.fetchone()
    if not row:
        raise ValueError("No 'workout' category found in life_categories")
    return row[0]


def get_synced_workout_ids(conn: sqlite3.Connection) -> set:
    cur = conn.execute("SELECT workout_id FROM fitbit_workout_bridge")
    return {row[0] for row in cur.fetchall()}


def format_workout_note(modality: str, duration: float, distance: float | None,
                        calories: float | None, avg_hr: float | None, peak_hr: float | None) -> str:
    parts = [f"Fitbit: {modality} ({int(duration)} min"]
    if distance:
        parts.append(f", {distance:.2f} km")
    if calories:
        parts.append(f", {int(calories)} cal")
    if avg_hr:
        parts.append(f", avg HR {int(avg_hr)}")
    if peak_hr:
        parts.append(f", peak {int(peak_hr)}")
    parts.append(")")
    return "".join(parts)


def sync_workouts(days: int = 7) -> int:
    if not WORKOUTS_DB.exists():
        print(f"Error: Workouts database not found at {WORKOUTS_DB}", file=sys.stderr)
        return 0

    if not WELLNESS_DB.exists():
        print(f"Error: Wellness database not found at {WELLNESS_DB}", file=sys.stderr)
        return 0

    try:
        workouts_conn = sqlite3.connect(WORKOUTS_DB)
        wellness_conn = sqlite3.connect(WELLNESS_DB)
    except sqlite3.Error as e:
        print(f"Error connecting to databases: {e}", file=sys.stderr)
        return 0

    try:
        category_id = get_workout_category_id(wellness_conn)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        workouts_conn.close()
        wellness_conn.close()
        return 0

    synced_ids = get_synced_workout_ids(wellness_conn)

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur = workouts_conn.execute("""
        SELECT id, date, start_time, primary_modality, duration_min, 
               distance_km, calories, avg_hr, peak_hr
        FROM workouts
        WHERE date >= ?
        ORDER BY date, start_time
    """, (cutoff,))

    synced_count = 0
    for row in cur.fetchall():
        workout_id, date, start_time, modality, duration, distance, calories, avg_hr, peak_hr = row

        if workout_id in synced_ids:
            continue

        if not duration:
            print(f"Warning: Skipping workout {workout_id} - no duration", file=sys.stderr)
            continue

        timestamp = start_time if start_time else f"{date}T00:00"
        note = format_workout_note(modality, duration, distance, calories, avg_hr, peak_hr)

        try:
            wellness_conn.execute("""
                INSERT INTO life_logs (category_id, timestamp, value, source, note,
                                       duration_min, distance_km, calories, avg_hr, peak_hr)
                VALUES (?, ?, 1.0, ?, ?, ?, ?, ?, ?, ?)
            """, (category_id, timestamp, SOURCE_LABEL, note,
                  duration, distance, calories, avg_hr, peak_hr))

            life_log_id = wellness_conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            wellness_conn.execute("""
                INSERT INTO fitbit_workout_bridge (workout_id, life_log_id)
                VALUES (?, ?)
            """, (workout_id, life_log_id))

            wellness_conn.commit()
            synced_count += 1
            print(f"✅ Synced workout #{workout_id}: {modality} on {date} → life_log #{life_log_id}")

        except sqlite3.Error as e:
            print(f"Error syncing workout {workout_id}: {e}", file=sys.stderr)
            wellness_conn.rollback()
            continue

    workouts_conn.close()
    wellness_conn.close()

    if synced_count > 0:
        print(f"\n✅ Synced {synced_count} new workout(s) to Life Counter.")
    else:
        print("No new workouts to sync.")

    return synced_count


def backfill_structured_data():
    if not WORKOUTS_DB.exists() or not WELLNESS_DB.exists():
        print("Error: Database files not found", file=sys.stderr)
        return

    try:
        workouts_conn = sqlite3.connect(WORKOUTS_DB)
        wellness_conn = sqlite3.connect(WELLNESS_DB)
    except sqlite3.Error as e:
        print(f"Error connecting to databases: {e}", file=sys.stderr)
        return

    cur = wellness_conn.execute("""
        SELECT b.workout_id, b.life_log_id
        FROM fitbit_workout_bridge b
        JOIN life_logs l ON l.id = b.life_log_id
        WHERE l.duration_min IS NULL OR l.distance_km IS NULL
    """)
    mappings = cur.fetchall()

    print(f"Backfilling {len(mappings)} workout entries...")

    updated = 0
    for workout_id, life_log_id in mappings:
        cur = workouts_conn.execute("""
            SELECT primary_modality, duration_min, distance_km, calories, avg_hr, peak_hr
            FROM workouts WHERE id = ?
        """, (workout_id,))
        row = cur.fetchone()
        if not row:
            continue

        modality, duration, distance, calories, avg_hr, peak_hr = row
        note = format_workout_note(modality, duration or 0, distance, calories, avg_hr, peak_hr)

        try:
            wellness_conn.execute("""
                UPDATE life_logs
                SET duration_min = ?, distance_km = ?, calories = ?, avg_hr = ?, peak_hr = ?,
                    note = ?, source = ?
                WHERE id = ?
            """, (duration, distance, calories, avg_hr, peak_hr, note, SOURCE_LABEL, life_log_id))
            updated += 1
        except sqlite3.Error as e:
            print(f"Error updating life_log {life_log_id}: {e}", file=sys.stderr)
            continue

    wellness_conn.commit()
    workouts_conn.close()
    wellness_conn.close()

    print(f"\n✅ Backfilled {updated} entries with structured workout data.")


def show_status():
    if not WORKOUTS_DB.exists() or not WELLNESS_DB.exists():
        print("Error: Database files not found", file=sys.stderr)
        return

    try:
        workouts_conn = sqlite3.connect(WORKOUTS_DB)
        wellness_conn = sqlite3.connect(WELLNESS_DB)
    except sqlite3.Error as e:
        print(f"Error connecting to databases: {e}", file=sys.stderr)
        return

    total_workouts = workouts_conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    synced_count = wellness_conn.execute("SELECT COUNT(*) FROM fitbit_workout_bridge").fetchone()[0]

    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = workouts_conn.execute("SELECT COUNT(*) FROM workouts WHERE date >= ?", (cutoff,)).fetchone()[0]

    synced_ids = get_synced_workout_ids(wellness_conn)
    recent_ids = {r[0] for r in workouts_conn.execute(
        "SELECT id FROM workouts WHERE date >= ?", (cutoff,)).fetchall()}
    pending = len(recent_ids - synced_ids)

    missing_data = wellness_conn.execute("""
        SELECT COUNT(*) FROM life_logs
        WHERE category_id = (SELECT id FROM life_categories WHERE slug = 'workout')
        AND (duration_min IS NULL OR distance_km IS NULL)
    """).fetchone()[0]

    workouts_conn.close()
    wellness_conn.close()

    print("Fitbit → Life Counter Bridge Status")
    print("=" * 40)
    print(f"Total workouts in Fitbit DB:     {total_workouts}")
    print(f"Workouts synced to Life Counter: {synced_count}")
    print(f"Recent workouts (last 7 days):   {recent}")
    print(f"Pending sync:                    {pending}")
    print(f"Entries missing structured data: {missing_data}")


def main():
    parser = argparse.ArgumentParser(description="Fitbit → Life Counter Bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Sync recent workouts")
    sync_parser.add_argument("--days", type=int, default=7, help="Days to look back (default: 7)")

    subparsers.add_parser("backfill", help="Backfill structured data for existing entries")
    subparsers.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    if args.command == "sync":
        sync_workouts(args.days)
    elif args.command == "backfill":
        backfill_structured_data()
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()


