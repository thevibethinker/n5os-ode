#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
POSTING_EVENTS_FILE = STATE_DIR / "analytics" / "posting-events.jsonl"

ERROR_PATTERNS = [
    "failed to authenticate",
    "api error: 401",
    "internal error:",
    "you're out of extra usage",
    "resets 3am",
    "unauthorized",
    "forbidden",
    "quota",
    "rate limit",
]


def classify_row(row: dict) -> str | None:
    if row.get("event") != "publish_attempt":
        return None
    if not row.get("published"):
        return None
    text = (row.get("content") or "").strip().lower()
    if not text:
        return "empty_content"
    for pattern in ERROR_PATTERNS:
        if pattern in text:
            return f"upstream_error:{pattern}"
    return None


def main():
    parser = argparse.ArgumentParser(description="Repair false-positive publish_attempt rows")
    parser.add_argument("--apply", action="store_true", help="Rewrite file with repairs")
    parser.add_argument("--limit", type=int, default=0, help="Only inspect the last N rows (0 = all)")
    args = parser.parse_args()

    if not POSTING_EVENTS_FILE.exists():
        print(json.dumps({"status": "missing", "path": str(POSTING_EVENTS_FILE)}, indent=2))
        return

    lines = POSTING_EVENTS_FILE.read_text().splitlines()
    start_idx = max(0, len(lines) - args.limit) if args.limit > 0 else 0

    repaired = 0
    inspected = 0
    new_lines = []
    findings = []

    for idx, line in enumerate(lines):
        row = json.loads(line)
        if idx >= start_idx:
            inspected += 1
            reason = classify_row(row)
            if reason:
                findings.append({
                    "line_number": idx + 1,
                    "timestamp": row.get("timestamp"),
                    "type": row.get("type"),
                    "reason": reason,
                    "content_preview": (row.get("content") or "")[:120],
                })
                if args.apply:
                    row["published"] = False
                    row["invalidated"] = True
                    row["failure_stage"] = "generation"
                    row["failure_reason"] = reason
                    repaired += 1
        new_lines.append(json.dumps(row))

    if args.apply and repaired:
        backup = POSTING_EVENTS_FILE.with_suffix('.jsonl.bak')
        backup.write_text("\n".join(lines) + "\n")
        POSTING_EVENTS_FILE.write_text("\n".join(new_lines) + "\n")

    print(json.dumps({
        "status": "ok",
        "path": str(POSTING_EVENTS_FILE),
        "inspected": inspected,
        "flagged": len(findings),
        "repaired": repaired,
        "applied": bool(args.apply),
        "findings": findings[-20:],
    }, indent=2))


if __name__ == "__main__":
    main()
