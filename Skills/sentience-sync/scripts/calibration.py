#!/usr/bin/env python3
"""
Calibration metrics tracking and threshold suggestion engine.

Tracks precision/recall of auto-write decisions and generates
threshold tuning recommendations so the pipeline earns trust
for broader auto-write scope over time.

Usage:
    python3 calibration.py record [--window 7d]
    python3 calibration.py report [--window 7d]
    python3 calibration.py suggest [--window 7d]
    python3 calibration.py history [--limit 20]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from projection_ledger import ProjectionLedger
from projection_store import ProjectionStore
from state import utc_now_iso

DATA_DIR = Path(__file__).parent.parent / "data"
CALIBRATION_FILE = DATA_DIR / "calibration_metrics.jsonl"
SNAPSHOTS_FILE = DATA_DIR / "calibration_snapshots.jsonl"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return entries


def _append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def _parse_window(window_str: str) -> timedelta:
    if window_str.endswith("w"):
        return timedelta(weeks=int(window_str[:-1]))
    if window_str.endswith("d"):
        return timedelta(days=int(window_str[:-1]))
    if window_str.endswith("h"):
        return timedelta(hours=int(window_str[:-1]))
    return timedelta(days=int(window_str))


def _filter_by_window(events: list[dict[str, Any]], window: timedelta) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - window).isoformat()
    return [e for e in events if e.get("timestamp", "") >= cutoff]


def compute_metrics(window_str: str = "7d") -> dict[str, Any]:
    window = _parse_window(window_str)
    hours = max(1, int(window.total_seconds() / 3600))
    time_range = f"{hours}h"

    ledger = ProjectionLedger()
    store = ProjectionStore()

    auto_writes = ledger.auto_write_count(time_range=time_range)
    corrections = ledger.manual_correction_count(time_range=time_range)

    cal_events = _filter_by_window(_read_jsonl(CALIBRATION_FILE), window)
    review_approvals = sum(1 for e in cal_events if e.get("event_type") == "review_approved")
    review_rejections = sum(1 for e in cal_events if e.get("event_type") == "review_rejected")

    if review_approvals == 0 and review_rejections == 0:
        all_approved = store.list_review_queue(status="approved")
        all_rejected = store.list_review_queue(status="rejected")
        review_approvals = len(all_approved)
        review_rejections = len(all_rejected)

    precision = (1.0 - corrections / auto_writes) if auto_writes > 0 else None
    total_resolved = review_approvals + review_rejections
    recall = (review_approvals / total_resolved) if total_resolved > 0 else None

    type_breakdown: dict[str, dict[str, int]] = defaultdict(lambda: {"approved": 0, "rejected": 0})
    for e in cal_events:
        ct = e.get("candidate_type", "unknown")
        if e.get("event_type") == "review_approved":
            type_breakdown[ct]["approved"] += 1
        elif e.get("event_type") == "review_rejected":
            type_breakdown[ct]["rejected"] += 1

    return {
        "window": window_str,
        "computed_at": utc_now_iso(),
        "auto_write_count": auto_writes,
        "manual_correction_count": corrections,
        "review_approve_count": review_approvals,
        "review_reject_count": review_rejections,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "type_breakdown": dict(type_breakdown),
    }


def generate_suggestions(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []

    precision = metrics.get("precision")
    recall = metrics.get("recall")
    auto_writes = metrics.get("auto_write_count", 0)
    corrections = metrics.get("manual_correction_count", 0)
    approvals = metrics.get("review_approve_count", 0)
    rejections = metrics.get("review_reject_count", 0)

    if auto_writes == 0 and approvals == 0:
        suggestions.append({
            "type": "insufficient_data",
            "severity": "info",
            "message": "Not enough data to generate suggestions. Process more events and review items first.",
        })
        return suggestions

    if precision is not None and precision <= 0.80:
        suggestions.append({
            "type": "tighten_auto_write",
            "severity": "high",
            "message": (
                f"Precision is {precision:.0%} ({corrections} corrections / {auto_writes} auto-writes). "
                "Recommend tightening: move 'strong' confidence from auto_write to review_queue "
                "for affected candidate types."
            ),
            "action": "In guardrail_engine.py POLICY_MATRIX, set strong->review_queue for high-error types.",
        })
    elif precision is not None and precision < 0.90:
        suggestions.append({
            "type": "monitor_precision",
            "severity": "medium",
            "message": (
                f"Precision is {precision:.0%} — acceptable but trending. "
                f"{corrections} corrections out of {auto_writes} auto-writes."
            ),
        })
    elif precision is not None:
        suggestions.append({
            "type": "precision_healthy",
            "severity": "info",
            "message": f"Precision is {precision:.0%} — auto-write accuracy is strong.",
        })

    if recall is not None and recall > 0.70:
        suggestions.append({
            "type": "loosen_thresholds",
            "severity": "medium",
            "message": (
                f"Recall is {recall:.0%} ({approvals} approvals / {approvals + rejections} resolved). "
                "Most review items are being approved — consider auto-writing more candidates."
            ),
            "action": "In guardrail_engine.py POLICY_MATRIX, move uncertain->auto_write for interaction_record.",
        })
    elif recall is not None and recall < 0.30:
        suggestions.append({
            "type": "review_queue_effective",
            "severity": "info",
            "message": (
                f"Recall is {recall:.0%} — most review items are being rejected. "
                "Review queue is correctly filtering."
            ),
        })

    type_breakdown = metrics.get("type_breakdown", {})
    for ct, counts in type_breakdown.items():
        ct_app = counts.get("approved", 0)
        ct_rej = counts.get("rejected", 0)
        ct_total = ct_app + ct_rej
        if ct_total < 5:
            continue
        ct_rate = ct_app / ct_total
        if ct_rate > 0.80:
            suggestions.append({
                "type": "type_loosen",
                "severity": "medium",
                "message": (
                    f"Type '{ct}': {ct_rate:.0%} approval rate ({ct_app}/{ct_total}). "
                    "Consider promoting this type from review_queue to auto_write at strong confidence."
                ),
            })
        elif ct_rate < 0.20:
            suggestions.append({
                "type": "type_appropriate",
                "severity": "info",
                "message": (
                    f"Type '{ct}': {ct_rate:.0%} approval rate ({ct_app}/{ct_total}). "
                    "Current routing is appropriate."
                ),
            })

    return suggestions


def cmd_record(args: argparse.Namespace) -> None:
    metrics = compute_metrics(args.window)
    _append_jsonl(SNAPSHOTS_FILE, metrics)
    print(json.dumps(metrics, indent=2))
    print(f"\nSnapshot saved to {SNAPSHOTS_FILE}")


def cmd_report(args: argparse.Namespace) -> None:
    metrics = compute_metrics(args.window)

    print(f"Calibration Report (window: {args.window})")
    print("=" * 60)
    print(f"  Auto-writes:        {metrics['auto_write_count']}")
    print(f"  Manual corrections: {metrics['manual_correction_count']}")
    print(f"  Review approvals:   {metrics['review_approve_count']}")
    print(f"  Review rejections:  {metrics['review_reject_count']}")

    p = metrics["precision"]
    r = metrics["recall"]
    print(f"\n  Precision: {f'{p:.1%}' if p is not None else 'N/A (no auto-writes)'}")
    print(f"  Recall:    {f'{r:.1%}' if r is not None else 'N/A (no resolved reviews)'}")

    if metrics.get("type_breakdown"):
        print(f"\n  By Type:")
        for ct, counts in sorted(metrics["type_breakdown"].items()):
            total = counts["approved"] + counts["rejected"]
            rate = counts["approved"] / total if total else 0
            print(f"    {ct}: {counts['approved']} approved, {counts['rejected']} rejected ({rate:.0%})")


def cmd_suggest(args: argparse.Namespace) -> None:
    metrics = compute_metrics(args.window)
    suggestions = generate_suggestions(metrics)

    if not suggestions:
        print("No suggestions — insufficient data.")
        return

    print(f"Threshold Suggestions (window: {args.window})")
    print("=" * 60)
    for s in suggestions:
        sev = s["severity"].upper()
        print(f"\n  [{sev}] {s['type']}")
        print(f"  {s['message']}")
        if "action" in s:
            print(f"  -> {s['action']}")


def cmd_history(args: argparse.Namespace) -> None:
    snapshots = _read_jsonl(SNAPSHOTS_FILE)
    if not snapshots:
        print("No calibration snapshots. Run: calibration.py record")
        return

    snapshots = snapshots[-args.limit:]
    header = f"{'Timestamp':<20}  {'Win':<5}  {'AW':>4}  {'Cor':>4}  {'App':>4}  {'Rej':>4}  {'Prec':>6}  {'Rec':>6}"
    print(header)
    print("-" * len(header))
    for s in snapshots:
        prec = f"{s['precision']:.0%}" if s.get("precision") is not None else "N/A"
        rec = f"{s['recall']:.0%}" if s.get("recall") is not None else "N/A"
        print(
            f"{s['computed_at'][:19]:<20}  {s['window']:<5}  "
            f"{s['auto_write_count']:>4}  {s['manual_correction_count']:>4}  "
            f"{s['review_approve_count']:>4}  {s['review_reject_count']:>4}  "
            f"{prec:>6}  {rec:>6}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calibration metrics and threshold suggestions for Sentience CRM.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    rp = sub.add_parser("record", help="Record current metrics snapshot")
    rp.add_argument("--window", default="7d", help="Time window (default: 7d)")

    rep = sub.add_parser("report", help="Show precision/recall report")
    rep.add_argument("--window", default="7d", help="Time window (default: 7d)")

    sp = sub.add_parser("suggest", help="Generate threshold suggestions")
    sp.add_argument("--window", default="7d", help="Time window (default: 7d)")

    hp = sub.add_parser("history", help="Show snapshot history")
    hp.add_argument("--limit", type=int, default=20, help="Max entries")

    args = parser.parse_args()

    handlers = {
        "record": cmd_record,
        "report": cmd_report,
        "suggest": cmd_suggest,
        "history": cmd_history,
    }
    handlers[args.command](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
