#!/usr/bin/env python3
"""Quick-add and view for the Zo Promo Codes list."""

import argparse
import json
import uuid
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from N5.lib.paths import N5_ROOT
    JSONL_PATH = N5_ROOT / "lists" / "zo-promo-codes.jsonl"
except ImportError:
    JSONL_PATH = Path(__file__).resolve().parent.parent / "lists" / "zo-promo-codes.jsonl"

def add_entry(name: str, context: str, offer: str, code: str = "",
              date_offered: str = "", status: str = "offered", notes: str = "",
              dry_run: bool = False):
    today = datetime.now(timezone.utc)
    if not date_offered:
        date_offered = today.strftime("%Y-%m-%d")

    entry = {
        "id": str(uuid.uuid4()),
        "created_at": today.isoformat(),
        "name": name,
        "context": context,
        "promo_code": code,
        "offer": offer,
        "date_offered": date_offered,
        "status": status,
        "notes": notes,
    }

    if dry_run:
        print("[DRY RUN] Would append:")
        print(json.dumps(entry, indent=2))
        return

    with open(JSONL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Added: {name} — {offer} (status: {status})")


def list_entries():
    if not JSONL_PATH.exists() or JSONL_PATH.stat().st_size == 0:
        print("No promo code entries yet.")
        return

    entries = []
    for line in JSONL_PATH.read_text().strip().splitlines():
        if line.strip():
            entries.append(json.loads(line))

    if not entries:
        print("No promo code entries yet.")
        return

    print(f"{'Name':<25} {'Offer':<30} {'Code':<15} {'Date':<12} {'Status':<10}")
    print("-" * 92)
    for e in entries:
        print(f"{e['name']:<25} {e['offer']:<30} {e.get('promo_code',''):<15} {e['date_offered']:<12} {e['status']:<10}")


def main():
    parser = argparse.ArgumentParser(description="Zo Promo Codes quick-add")
    parser.add_argument("name", nargs="?", help="Person's name")
    parser.add_argument("context", nargs="?", help="How you know them / where offered")
    parser.add_argument("offer", nargs="?", help="What was promised")
    parser.add_argument("--code", default="", help="Specific promo code")
    parser.add_argument("--date", default="", help="Date offered (YYYY-MM-DD, default today)")
    parser.add_argument("--status", default="offered", choices=["offered", "redeemed", "expired"])
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument("--list", action="store_true", help="List all entries")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")

    args = parser.parse_args()

    if args.list:
        list_entries()
        return

    if not all([args.name, args.context, args.offer]):
        parser.error("name, context, and offer are required (or use --list)")

    add_entry(
        name=args.name,
        context=args.context,
        offer=args.offer,
        code=args.code,
        date_offered=args.date,
        status=args.status,
        notes=args.notes,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
