#!/usr/bin/env python3
"""
Cleanup Stale Headless Workers

Safely reconciles or abandons old "running" headless worker conversations.

Default behavior (dry-run):
- Lists stale headless workers (type=headless_worker, status=running)

When --execute is set:
- If a deposit already exists at N5/builds/<build_slug>/deposits/<drop_id>.json:
  - Default: SKIP (deposit exists)
  - If --reconcile: mark the conversation as "complete" (bookkeeping only)
  - Never marks the build drop as dead in this case

- If no deposit exists:
  - Mark conversation status as "abandoned"
  - If build_slug/drop_id are present: mark the build drop status as "dead"

Usage:
  python3 N5/scripts/cleanup_stale_workers.py                 # Dry run
  python3 N5/scripts/cleanup_stale_workers.py --execute       # Execute (safe)
  python3 N5/scripts/cleanup_stale_workers.py --execute --reconcile
  python3 N5/scripts/cleanup_stale_workers.py --hours 4       # Custom threshold
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/home/workspace")
CONVERSATIONS_DB = WORKSPACE / "N5" / "data" / "conversations.db"
BUILDS_DIR = WORKSPACE / "N5" / "builds"

DEFAULT_STALE_HOURS = 2


def get_stale_workers(hours: int) -> list[dict]:
    """Find headless workers that have been 'running' longer than threshold."""
    stale = []

    if not CONVERSATIONS_DB.exists():
        return stale

    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, build_slug, drop_id, created_at, updated_at 
        FROM conversations 
        WHERE type = 'headless_worker' AND status = 'running'
    """)

    now = datetime.now(timezone.utc)
    threshold = timedelta(hours=hours)

    for row in cursor.fetchall():
        conv_id, build_slug, drop_id, created_at, updated_at = row

        try:
            ts = updated_at or created_at
            ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            elapsed = now - ts_dt

            if elapsed > threshold:
                stale.append({
                    "conversation_id": conv_id,
                    "build_slug": build_slug,
                    "drop_id": drop_id,
                    "elapsed_hours": round(elapsed.total_seconds() / 3600, 1),
                    "created_at": created_at,
                    "updated_at": updated_at
                })
        except Exception as e:
            print(f"Error parsing timestamp for {conv_id}: {e}")

    conn.close()
    return stale


def deposit_exists(build_slug: str, drop_id: str) -> bool:
    if not build_slug or not drop_id:
        return False
    deposit_path = BUILDS_DIR / build_slug / "deposits" / f"{drop_id}.json"
    return deposit_path.exists()


def update_conversation_status(conv_id: str, new_status: str):
    """Update conversation status in database."""
    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE conversations 
        SET status = ?, updated_at = ?, completed_at = ?
        WHERE id = ?
    """, (new_status, now, now, conv_id))

    conn.commit()
    conn.close()


def update_build_drop_status(build_slug: str, drop_id: str, new_status: str):
    """Update drop status in build's meta.json."""
    if not build_slug or not drop_id:
        return False

    meta_path = BUILDS_DIR / build_slug / "meta.json"
    if not meta_path.exists():
        return False

    try:
        with open(meta_path) as f:
            meta = json.load(f)

        drops = meta.get("drops", {})
        if drop_id in drops:
            drops[drop_id]["status"] = new_status
            drops[drop_id]["abandoned_at"] = datetime.now(timezone.utc).isoformat()
            drops[drop_id]["abandonment_reason"] = "Stale worker cleanup"

            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
            return True
    except Exception as e:
        print(f"Error updating build {build_slug}: {e}")

    return False


def main():
    parser = argparse.ArgumentParser(description="Cleanup stale headless workers")
    parser.add_argument("--execute", action="store_true", help="Actually execute cleanup (default is dry run)")
    parser.add_argument("--reconcile", action="store_true", help="If a deposit exists, mark conversation complete instead of skipping")
    parser.add_argument("--hours", type=int, default=DEFAULT_STALE_HOURS, help=f"Stale threshold in hours (default: {DEFAULT_STALE_HOURS})")
    args = parser.parse_args()

    stale = get_stale_workers(args.hours)

    if not stale:
        print(f"No stale workers found (threshold: {args.hours}h)")
        return

    print(f"Found {len(stale)} stale workers (threshold: {args.hours}h):\n")

    for w in stale:
        has_deposit = deposit_exists(w["build_slug"], w["drop_id"])
        tag = "DEPOSIT" if has_deposit else "NO_DEPOSIT"
        print(f"  {w['conversation_id'][:20]}... [{tag}]")
        print(f"    Build: {w['build_slug'] or '(none)'}")
        print(f"    Drop: {w['drop_id'] or '(none)'}")
        print(f"    Stale: {w['elapsed_hours']}h")
        print()

    if not args.execute:
        print("Dry run - use --execute to actually cleanup")
        return

    print("Executing cleanup...")

    for w in stale:
        has_deposit = deposit_exists(w["build_slug"], w["drop_id"])

        if has_deposit:
            if args.reconcile:
                update_conversation_status(w["conversation_id"], "complete")
                print(f"  ✓ Reconciled conversation {w['conversation_id'][:20]}... as complete (deposit exists)")
            else:
                print(f"  - SKIP {w['conversation_id'][:20]}... (deposit exists)")
            continue

        update_conversation_status(w["conversation_id"], "abandoned")
        print(f"  ✓ Marked conversation {w['conversation_id'][:20]}... as abandoned")

        if w["build_slug"] and w["drop_id"]:
            if update_build_drop_status(w["build_slug"], w["drop_id"], "dead"):
                print(f"  ✓ Marked {w['build_slug']}/{w['drop_id']} as dead")

    print(f"\nCleanup complete: {len(stale)} workers processed")


if __name__ == "__main__":
    main()
