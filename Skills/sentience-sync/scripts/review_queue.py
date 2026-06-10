#!/usr/bin/env python3
"""
Review queue management CLI for Sentience CRM enrichment.

Manages candidates that didn't pass auto-write thresholds.
Approve/reject decisions feed the calibration loop.

Usage:
    python3 review_queue.py list [--type TYPE] [--status STATUS] [--limit N]
    python3 review_queue.py show <id>
    python3 review_queue.py approve <id>
    python3 review_queue.py reject <id> --reason "false positive"
    python3 review_queue.py bulk-approve <id1> <id2> ...
    python3 review_queue.py bulk-reject <id1> <id2> ... --reason "noise"
    python3 review_queue.py stats
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from projection_ledger import ProjectionLedger
from projection_store import ProjectionStore, utc_now_iso
from projection_writer import ProjectionWriter
from state import build_projection_id

DATA_DIR = Path(__file__).parent.parent / "data"
CALIBRATION_FILE = DATA_DIR / "calibration_metrics.jsonl"


def _update_review_status(store: ProjectionStore, review_id: int, status: str) -> None:
    with store._connect() as conn:
        conn.execute(
            "UPDATE review_queue SET status = ?, resolved_at = ? WHERE id = ?",
            (status, utc_now_iso(), review_id),
        )


def _log_calibration_event(
    event_type: str,
    review_id: int,
    candidate_type: str,
    details: dict[str, Any] | None = None,
) -> None:
    entry = {
        "timestamp": utc_now_iso(),
        "event_type": event_type,
        "review_id": review_id,
        "candidate_type": candidate_type,
        **(details or {}),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CALIBRATION_FILE, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def _update_ledger_projection(ledger: ProjectionLedger, candidate_id: str, status: str, reason: str) -> None:
    projection_id = build_projection_id(candidate_id, "review_queue")
    try:
        ledger.update_status(projection_id, status, reason=reason)
    except KeyError:
        pass  # no ledger entry for this candidate yet — not an error


def _approve_item(
    store: ProjectionStore,
    writer: ProjectionWriter,
    ledger: ProjectionLedger,
    item: dict[str, Any],
) -> dict[str, Any]:
    review_id = item["id"]
    candidate_data = item["candidate_data"]
    signal = candidate_data.get("signal", {})
    resolutions = candidate_data.get("resolutions", [])
    candidate_id = candidate_data.get("candidate_id", "")
    confidence_tier = candidate_data.get("confidence_tier", "uncertain")

    candidate = {
        "candidate_id": candidate_id,
        "id": candidate_id,
        "candidate_type": signal.get("signal_type", item["candidate_type"]),
        "type": signal.get("signal_type", item["candidate_type"]),
        "confidence_tier": confidence_tier,
        "source_event_ids": signal.get("source_event_ids", []),
    }

    decision = {
        "action": "auto_write",
        "destination": "interactions",
        "audit_flag": False,
        "reason": f"Manually approved from review queue (id={review_id})",
    }

    result = writer._auto_write(signal, resolutions, candidate, decision)

    _update_review_status(store, review_id, "approved")
    _update_ledger_projection(
        ledger,
        candidate_id,
        "review_approved",
        f"Approved from review queue (id={review_id})",
    )
    _log_calibration_event("review_approved", review_id, item["candidate_type"], {
        "candidate_id": candidate_id,
        "confidence_tier": confidence_tier,
        "write_status": result.status,
        "interaction_id": result.interaction_id,
    })

    return {
        "id": review_id,
        "status": result.status,
        "interaction_id": result.interaction_id,
        "reason": result.reason,
    }


def _reject_item(
    store: ProjectionStore,
    ledger: ProjectionLedger,
    item: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    review_id = item["id"]
    candidate_data = item.get("candidate_data", {})
    candidate_id = candidate_data.get("candidate_id", "")

    _update_review_status(store, review_id, "rejected")
    _update_ledger_projection(
        ledger,
        candidate_id,
        "review_rejected",
        reason,
    )
    _log_calibration_event("review_rejected", review_id, item["candidate_type"], {
        "candidate_id": candidate_id,
        "confidence_tier": candidate_data.get("confidence_tier", ""),
        "rejection_reason": reason,
    })

    return {"id": review_id, "status": "rejected", "reason": reason}


def cmd_list(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    status_filter = args.status if args.status != "all" else None
    items = store.list_review_queue(status=status_filter, limit=args.limit)
    if args.type:
        items = [i for i in items if i["candidate_type"] == args.type]

    if not items:
        print("No items in review queue.")
        return

    print(f"{'ID':>5}  {'Type':<25}  {'Status':<10}  {'Created':<20}  Reason")
    print("-" * 95)
    for item in items:
        reason_short = (item.get("reason") or "")[:35]
        print(
            f"{item['id']:>5}  {item['candidate_type']:<25}  "
            f"{item['status']:<10}  {item['created_at'][:19]:<20}  {reason_short}"
        )
    print(f"\nTotal: {len(items)} items")


def cmd_show(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    item = store.get_review_item(args.id)
    if not item:
        print(f"Review item {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(item, indent=2, default=str))


def cmd_approve(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    item = store.get_review_item(args.id)
    if not item:
        print(f"Review item {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    if item["status"] != "pending":
        print(f"Item {args.id} is already '{item['status']}'.", file=sys.stderr)
        sys.exit(1)

    ledger = ProjectionLedger()
    writer = ProjectionWriter(store=store, ledger=ledger)
    result = _approve_item(store, writer, ledger, item)

    print(f"Approved item {args.id}")
    print(f"  Write status: {result['status']}")
    if result.get("interaction_id"):
        print(f"  Interaction ID: {result['interaction_id']}")


def cmd_reject(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    item = store.get_review_item(args.id)
    if not item:
        print(f"Review item {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    if item["status"] != "pending":
        print(f"Item {args.id} is already '{item['status']}'.", file=sys.stderr)
        sys.exit(1)

    ledger = ProjectionLedger()
    result = _reject_item(store, ledger, item, args.reason)
    print(f"Rejected item {result['id']}: {result['reason']}")


def cmd_bulk_approve(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    ledger = ProjectionLedger()
    writer = ProjectionWriter(store=store, ledger=ledger)

    results: list[dict[str, Any]] = []
    for raw_id in args.ids:
        rid = int(raw_id)
        item = store.get_review_item(rid)
        if not item:
            results.append({"id": rid, "status": "not_found"})
            continue
        if item["status"] != "pending":
            results.append({"id": rid, "status": f"already_{item['status']}"})
            continue
        result = _approve_item(store, writer, ledger, item)
        results.append(result)

    written = sum(1 for r in results if r["status"] in ("written", "dry_run"))
    skipped = len(results) - written
    print(f"Bulk approve: {written} written, {skipped} skipped")
    for r in results:
        icon = "+" if r["status"] in ("written", "dry_run") else "-"
        print(f"  [{icon}] ID {r['id']}: {r['status']}")


def cmd_bulk_reject(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    ledger = ProjectionLedger()

    results: list[dict[str, Any]] = []
    for raw_id in args.ids:
        rid = int(raw_id)
        item = store.get_review_item(rid)
        if not item:
            results.append({"id": rid, "status": "not_found"})
            continue
        if item["status"] != "pending":
            results.append({"id": rid, "status": f"already_{item['status']}"})
            continue
        result = _reject_item(store, ledger, item, args.reason)
        results.append(result)

    rejected = sum(1 for r in results if r["status"] == "rejected")
    skipped = len(results) - rejected
    print(f"Bulk reject: {rejected} rejected, {skipped} skipped")
    for r in results:
        icon = "x" if r["status"] == "rejected" else "-"
        print(f"  [{icon}] ID {r['id']}: {r['status']}")


def cmd_stats(args: argparse.Namespace) -> None:
    store = ProjectionStore()
    pending = store.list_review_queue(status="pending")
    approved = store.list_review_queue(status="approved")
    rejected = store.list_review_queue(status="rejected")

    type_counts: dict[str, dict[str, int]] = {}
    for status_label, items in [("pending", pending), ("approved", approved), ("rejected", rejected)]:
        for item in items:
            ct = item["candidate_type"]
            type_counts.setdefault(ct, {"pending": 0, "approved": 0, "rejected": 0})
            type_counts[ct][status_label] += 1

    total = len(pending) + len(approved) + len(rejected)

    print("Review Queue Stats")
    print("=" * 60)
    print(f"  Pending:  {len(pending)}")
    print(f"  Approved: {len(approved)}")
    print(f"  Rejected: {len(rejected)}")
    print(f"  Total:    {total}")

    if type_counts:
        print(f"\n  By Type:")
        print(f"  {'Type':<25}  {'Pend':>5}  {'Appr':>5}  {'Rej':>5}")
        print("  " + "-" * 45)
        for ct in sorted(type_counts):
            c = type_counts[ct]
            print(f"  {ct:<25}  {c['pending']:>5}  {c['approved']:>5}  {c['rejected']:>5}")

    resolved = len(approved) + len(rejected)
    if resolved > 0:
        rate = len(approved) / resolved
        print(f"\n  Approval rate: {rate:.0%} ({len(approved)}/{resolved})")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review queue management for Sentience CRM enrichment.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    lp = sub.add_parser("list", help="List review queue items")
    lp.add_argument("--type", help="Filter by candidate_type")
    lp.add_argument("--status", default="pending", help="Status filter (default: pending, use 'all' for everything)")
    lp.add_argument("--limit", type=int, help="Max items")

    sp = sub.add_parser("show", help="Show item detail")
    sp.add_argument("id", type=int)

    ap = sub.add_parser("approve", help="Approve (triggers write through projection_writer)")
    ap.add_argument("id", type=int)

    rp = sub.add_parser("reject", help="Reject with reason")
    rp.add_argument("id", type=int)
    rp.add_argument("--reason", required=True)

    ba = sub.add_parser("bulk-approve", help="Approve multiple items")
    ba.add_argument("ids", nargs="+")

    br = sub.add_parser("bulk-reject", help="Reject multiple items")
    br.add_argument("ids", nargs="+")
    br.add_argument("--reason", required=True)

    sub.add_parser("stats", help="Queue statistics")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "show": cmd_show,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "bulk-approve": cmd_bulk_approve,
        "bulk-reject": cmd_bulk_reject,
        "stats": cmd_stats,
    }
    handlers[args.command](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
