#!/usr/bin/env python3
"""
Sheets Sync — Bidirectional sync between Zøde workspace and Google Sheets.

Syncs staged posts, published posts with metrics, daily distillation insights,
hypotheses, and the influencer map to a single Google Sheet.

Usage: python3 sheets_sync.py push [--sheet-id ID]
       python3 sheets_sync.py status
       python3 sheets_sync.py --help

Note: Uses Google Sheets API via Zo's app integration (use_app_google_drive).
      The sheet ID is stored in workspace state after first creation.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
SHEET_STATE_DIR = WORKSPACE
STAGING_DIR = WORKSPACE / "staging"
ANALYTICS_DIR = WORKSPACE / "analytics"
LEARNINGS_DIR = WORKSPACE / "learnings"
SHEET_CONFIG_FILE = SHEET_STATE_DIR / "sheets_config.json"


def load_sheet_config() -> dict:
    """Load the Google Sheet configuration."""
    if SHEET_CONFIG_FILE.exists():
        with open(SHEET_CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_sheet_config(config: dict):
    """Save Google Sheet configuration."""
    SHEET_STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SHEET_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def collect_staged_posts() -> list[dict]:
    """Collect all staged posts for the Staged Posts tab."""
    posts = []
    if not STAGING_DIR.exists():
        return posts

    for f in sorted(STAGING_DIR.glob("*.json")):
        with open(f) as fh:
            post = json.load(fh)
        posts.append({
            "id": post.get("id", f.stem),
            "status": post.get("status", "unknown"),
            "title": post.get("title", "")[:80],
            "submolt": post.get("submolt", {}).get("name", "") if isinstance(post.get("submolt"), dict) else post.get("submolt", ""),
            "type": post.get("type", "post"),
            "word_count": len(post.get("content", "").split()),
            "rubric_avg": post.get("rubric_result", {}).get("average", ""),
            "rubric_passed": post.get("rubric_result", {}).get("passed", ""),
            "created_at": post.get("created_at", ""),
            "published_at": post.get("published_at", ""),
            "moltbook_id": post.get("moltbook_id", ""),
        })

    return posts


def collect_published_metrics() -> list[dict]:
    """Collect published post metrics from analytics snapshots."""
    all_metrics = []

    if not ANALYTICS_DIR.exists():
        return all_metrics

    for f in sorted(ANALYTICS_DIR.glob("engagement-*.json")):
        with open(f) as fh:
            metrics = json.load(fh)
        for m in metrics:
            all_metrics.append({
                "date": f.stem.replace("engagement-", ""),
                "title": m.get("title", "")[:80],
                "moltbook_id": m.get("moltbook_id", ""),
                "score": m.get("score", 0),
                "upvotes": m.get("upvotes", 0),
                "downvotes": m.get("downvotes", 0),
                "comment_count": m.get("comment_count", 0),
                "submolt": m.get("submolt", {}).get("name", "") if isinstance(m.get("submolt"), dict) else m.get("submolt", ""),
            })

    return all_metrics


def collect_distillation_insights() -> list[dict]:
    """Collect daily distillation observations."""
    insights = []
    distillation_file = LEARNINGS_DIR / "daily-distillation.jsonl"

    if not distillation_file.exists():
        return insights

    with open(distillation_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            for obs in entry.get("observations", []):
                insights.append({
                    "date": entry.get("date", ""),
                    "type": obs.get("type", ""),
                    "confidence": obs.get("confidence", ""),
                    "observation": obs.get("observation", "")[:200],
                    "implication": obs.get("implication", "")[:200],
                })

    return insights


def collect_hypotheses() -> list[dict]:
    """Collect hypotheses from the JSONL log."""
    hypotheses = []
    hyp_file = ANALYTICS_DIR / "hypotheses.jsonl"

    if not hyp_file.exists():
        return hypotheses

    with open(hyp_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            h = json.loads(line)
            hypotheses.append({
                "id": h.get("id", ""),
                "type": h.get("type", ""),
                "prediction": h.get("prediction", "")[:150],
                "confidence": h.get("confidence", ""),
                "verified": h.get("verified", False),
                "outcome": h.get("outcome", ""),
                "created_at": h.get("created_at", "")[:10],
            })

    return hypotheses


def collect_influencer_map() -> list[dict]:
    """Collect influencer data."""
    influencers = []
    map_file = ANALYTICS_DIR / "influencer-map.jsonl"

    if not map_file.exists():
        return influencers

    with open(map_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            agent = json.loads(line)
            influencers.append({
                "name": agent.get("name", ""),
                "influence_score": agent.get("influence_score", 0),
                "category": agent.get("category", ""),
                "relevance": agent.get("relevance", ""),
                "last_active": agent.get("last_active", ""),
                "engagement_quality": agent.get("engagement_quality", ""),
                "notes": agent.get("notes", "")[:100],
            })

    return influencers


def generate_sync_payload() -> dict:
    """Generate the full sync payload for all sheet tabs."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tabs": {
            "staged_posts": collect_staged_posts(),
            "published_metrics": collect_published_metrics(),
            "daily_insights": collect_distillation_insights(),
            "hypotheses": collect_hypotheses(),
            "influencer_map": collect_influencer_map(),
        },
    }


def save_sync_snapshot(payload: dict):
    """Save a local snapshot of the sync payload."""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = ANALYTICS_DIR / f"sheets-sync-{date}.json"
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)
    return filepath


# --- CLI ---

def cmd_push(args):
    """Push data to Google Sheets."""
    payload = generate_sync_payload()

    print("SHEETS SYNC")
    print("=" * 50)

    for tab_name, data in payload["tabs"].items():
        print(f"  {tab_name}: {len(data)} rows")

    # Save local snapshot
    if not args.dry_run:
        filepath = save_sync_snapshot(payload)
        print(f"\nLocal snapshot saved to {filepath}")

    # Check for sheet config
    config = load_sheet_config()
    sheet_id = args.sheet_id or config.get("sheet_id")

    if not sheet_id:
        print("\nNo Google Sheet ID configured.")
        print("To set up the Google Sheet:")
        print("  1. Create a new Google Sheet named 'Zøde Moltbook Tracker'")
        print("  2. Add tabs: Staged Posts, Published, Daily Insights, Hypotheses, Influencer Map")
        print("  3. Run: python3 sheets_sync.py push --sheet-id <your-sheet-id>")
        print("\nThe local snapshot can be imported manually in the meantime.")
        return

    if args.sheet_id and args.sheet_id != config.get("sheet_id"):
        config["sheet_id"] = args.sheet_id
        save_sheet_config(config)
        print(f"\nSheet ID saved: {args.sheet_id}")

    if args.dry_run:
        print("\n[DRY RUN] Would push to Google Sheet")
        return

    # The actual Google Sheets push happens via Zo's app integration
    # This script prepares the data; Zo handles the API call
    print(f"\nData prepared for Google Sheet: {sheet_id}")
    print("Use Zo's Google Drive integration to push this data.")

    if args.json:
        print(json.dumps(payload, indent=2))


def cmd_status(args):
    """Show sync status."""
    config = load_sheet_config()

    print("SHEETS SYNC STATUS")
    print("=" * 50)
    print(f"Sheet ID: {config.get('sheet_id', 'Not configured')}")
    print(f"Last sync: {config.get('last_sync', 'Never')}")

    # Count data in each category
    staged = collect_staged_posts()
    print(f"\nData available:")
    print(f"  Staged posts: {len(staged)}")
    print(f"  Published posts: {len([p for p in staged if p['status'] == 'published'])}")

    insights = collect_distillation_insights()
    print(f"  Distillation insights: {len(insights)}")

    hypotheses = collect_hypotheses()
    print(f"  Hypotheses: {len(hypotheses)}")

    influencers = collect_influencer_map()
    print(f"  Influencers tracked: {len(influencers)}")


def main():
    parser = argparse.ArgumentParser(
        description="Sheets Sync — Google Sheets integration for Zøde tracker"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p = sub.add_parser("push", help="Push data to Google Sheets")
    p.add_argument("--sheet-id", help="Google Sheet ID")
    p.add_argument("--dry-run", action="store_true", help="Don't push, just show data")
    p.add_argument("--json", action="store_true", help="Output payload as JSON")

    s = sub.add_parser("status", help="Show sync status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {"push": cmd_push, "status": cmd_status}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
