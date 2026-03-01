#!/usr/bin/env python3
"""
Build cached advertiser-facing Moltbook metrics snapshots.

Writes:
- state/analytics/advertiser-snapshot-YYYY-MM-DD.json
- state/analytics/advertiser-snapshot-latest.json
"""

import argparse
import json
from datetime import date, datetime, timezone
from glob import glob
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = SCRIPT_DIR.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"


def _load_engagement_rows() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(glob(str(ANALYTICS_DIR / "engagement-*.json"))):
        with open(path) as f:
            doc = json.load(f)
        dt = doc.get("date")
        if not dt:
            continue
        posts = doc.get("posts", [])
        totals = doc.get("totals", {})
        interactions = int(totals.get("post_upvotes", 0)) + int(totals.get("post_comment_count", 0))
        post_count = max(int(totals.get("posts_tracked", 0)), len(posts), 1)
        rows.append(
            {
                "date": dt,
                "followers": int(doc.get("agent", {}).get("followers", 0)),
                "karma": int(doc.get("agent", {}).get("karma", 0)),
                "posts_tracked": int(totals.get("posts_tracked", len(posts))),
                "interactions": interactions,
                "avg_engagement_per_post": round(interactions / post_count, 3),
                "source_file": path,
            }
        )
    return rows


def _top_themes(latest_doc: dict) -> list[dict]:
    posts = latest_doc.get("posts", [])
    themes = {
        "Trust & Reliability": ("trust", "doubt", "reliab", "permission", "confidence"),
        "Human-Agent Communication": ("silence", "explain", "translation", "ask", "correction"),
        "Partnership Dynamics": ("human", "partnership", "handoff", "collabor", "repair"),
        "Execution & Systems": ("workflow", "pipeline", "build", "debug", "automation"),
        "Safety & Guardrails": ("security", "guardrail", "risk", "veto", "injection"),
    }
    counts = {name: 0 for name in themes}
    for p in posts:
        text = f"{p.get('title', '')} {p.get('submolt', '')}".lower()
        for name, keys in themes.items():
            if any(k in text for k in keys):
                counts[name] += 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"theme": k, "matches": v} for k, v in ranked if v > 0]


def build_snapshot() -> dict:
    rows = _load_engagement_rows()
    if not rows:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rows": [],
            "summary": {},
            "themes": [],
        }

    rows.sort(key=lambda r: r["date"])
    start, end = rows[0], rows[-1]
    for i, row in enumerate(rows):
        prev = rows[i - 1] if i > 0 else None
        row["followers_delta"] = row["followers"] - (prev["followers"] if prev else 0)
        row["karma_delta"] = row["karma"] - (prev["karma"] if prev else 0)

    latest_doc = json.load(open(rows[-1]["source_file"]))
    summary = {
        "start_date": start["date"],
        "end_date": end["date"],
        "followers_change": end["followers"] - start["followers"],
        "karma_change": end["karma"] - start["karma"],
        "avg_engagement_per_post_latest": end["avg_engagement_per_post"],
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
        "summary": summary,
        "themes": _top_themes(latest_doc),
    }


def refresh_advertiser_snapshot(force: bool = False) -> dict:
    today = date.today().isoformat()
    today_path = ANALYTICS_DIR / f"advertiser-snapshot-{today}.json"
    latest_path = ANALYTICS_DIR / "advertiser-snapshot-latest.json"

    if today_path.exists() and not force:
        return {"ok": True, "skipped": True, "reason": "already_built_today", "path": str(today_path)}

    snapshot = build_snapshot()
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(today_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    with open(latest_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    return {
        "ok": True,
        "skipped": False,
        "today_path": str(today_path),
        "latest_path": str(latest_path),
        "rows": len(snapshot.get("rows", [])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build advertiser cache snapshot")
    parser.add_argument("--force", action="store_true", help="rebuild even if today's snapshot exists")
    parser.add_argument("--json", action="store_true", help="print machine-readable result")
    args = parser.parse_args()

    result = refresh_advertiser_snapshot(force=args.force)
    if args.json:
        print(json.dumps(result))
    else:
        print(result)


if __name__ == "__main__":
    main()
