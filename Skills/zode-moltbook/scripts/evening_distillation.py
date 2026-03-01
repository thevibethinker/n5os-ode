#!/usr/bin/env python3
"""
Evening Distillation — Daily review + learning extraction + V summary.

Cadence is controlled by scheduled agent configuration. Collects engagement metrics, runs distillation,
reviews morning hypotheses, and generates a daily summary.

Usage: python3 evening_distillation.py run [--dry-run] [--json]
       python3 evening_distillation.py summary [--date YYYY-MM-DD]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = WORKSPACE / "analytics"
SUMMARIES_DIR = WORKSPACE / "learnings"


def collect_day_metrics(date: str) -> dict:
    """Collect all metrics for a given day."""
    metrics = {
        "date": date,
        "engagement": [],
        "hypotheses": [],
        "heartbeat_actions": {"posts": 0, "comments": 0, "reads": 0},
    }

    # Load engagement data
    engagement_file = ANALYTICS_DIR / f"engagement-{date}.json"
    if engagement_file.exists():
        with open(engagement_file) as f:
            metrics["engagement"] = json.load(f)

    # Load hypotheses
    hypotheses_file = ANALYTICS_DIR / "hypotheses.jsonl"
    if hypotheses_file.exists():
        with open(hypotheses_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                h = json.loads(line)
                if h.get("created_at", "").startswith(date):
                    metrics["hypotheses"].append(h)

    # Load heartbeat log
    heartbeat_log = WORKSPACE / "heartbeat_log.jsonl"
    if heartbeat_log.exists():
        with open(heartbeat_log) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get("date") == date:
                    at = entry.get("action_type", "read")
                    if at in metrics["heartbeat_actions"]:
                        metrics["heartbeat_actions"][at] += 1

    return metrics


def generate_daily_summary(metrics: dict, observations: list[dict]) -> dict:
    """Generate a complete daily summary for V."""
    date = metrics["date"]
    engagement = metrics["engagement"]
    hypotheses = metrics["hypotheses"]
    actions = metrics["heartbeat_actions"]

    # Engagement stats
    total_score = sum(e.get("score", 0) or 0 for e in engagement)
    total_comments = sum(e.get("comment_count", 0) or 0 for e in engagement)
    avg_score = round(total_score / max(len(engagement), 1), 1)

    # Hypothesis accuracy
    verified = [h for h in hypotheses if h.get("verified")]
    accuracy = len(verified) / max(len(hypotheses), 1) if hypotheses else None

    summary = {
        "date": date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "activity": {
            "heartbeats": actions["reads"],
            "posts_made": actions["posts"],
            "comments_made": actions["comments"],
        },
        "engagement": {
            "posts_tracked": len(engagement),
            "total_score": total_score,
            "avg_score": avg_score,
            "total_comments_received": total_comments,
        },
        "observations": observations,
        "hypothesis_review": {
            "total": len(hypotheses),
            "verified": len(verified),
            "accuracy": round(accuracy, 2) if accuracy is not None else None,
        },
        "top_performer": None,
        "learnings": [],
    }

    # Identify top performer
    if engagement:
        best = max(engagement, key=lambda e: e.get("score", 0) or 0)
        summary["top_performer"] = {
            "title": best.get("title", "untitled"),
            "score": best.get("score", 0),
            "comments": best.get("comment_count", 0),
        }

    # Extract high-confidence learnings
    for obs in observations:
        if obs.get("confidence") in ("high", "medium"):
            summary["learnings"].append(obs["observation"])

    return summary


def save_summary(summary: dict):
    """Save daily summary."""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SUMMARIES_DIR / f"daily-summary-{summary['date']}.json"
    with open(filepath, "w") as f:
        json.dump(summary, f, indent=2)
    return filepath


def load_summary(date: str) -> dict | None:
    """Load a daily summary."""
    filepath = SUMMARIES_DIR / f"daily-summary-{date}.json"
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return None


# --- CLI ---

def cmd_run(args):
    """Run the full evening distillation."""
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Step 1: Collect engagement metrics
    print(f"Collecting metrics for {date}...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from engagement_tracker import collect_from_staging, collect_metrics, save_metrics
        published = collect_from_staging()
        if published:
            metrics_data = collect_metrics(published)
            save_metrics(date, metrics_data)
            print(f"  Collected metrics for {len(metrics_data)} posts")
        else:
            print("  No published posts to collect metrics for")
    except Exception as e:
        print(f"  Warning: Could not collect live metrics: {e}", file=sys.stderr)

    # Step 2: Run distillation
    print("Running distillation...")
    try:
        from distillation import extract_observations, save_distillation
        day_metrics = collect_day_metrics(date)
        observations = extract_observations(day_metrics["engagement"])

        if not args.dry_run:
            save_distillation(date, observations)
            print(f"  Saved {len(observations)} observations")
    except Exception as e:
        print(f"  Warning: Distillation error: {e}", file=sys.stderr)
        day_metrics = collect_day_metrics(date)
        observations = [{"type": "error", "observation": f"Distillation error: {e}", "implication": "Check distillation.py", "confidence": "n/a"}]

    # Step 3: Generate summary
    print("Generating daily summary...")
    summary = generate_daily_summary(day_metrics, observations)

    if not args.dry_run:
        filepath = save_summary(summary)
        print(f"  Saved summary to {filepath}")

    # Display
    print()
    print(f"EVENING SUMMARY — {date}")
    print("=" * 50)

    act = summary["activity"]
    print(f"Activity: {act['heartbeats']} scans, {act['posts_made']} posts, {act['comments_made']} comments")

    eng = summary["engagement"]
    print(f"Engagement: {eng['posts_tracked']} tracked, avg score {eng['avg_score']}, {eng['total_comments_received']} comments received")

    if summary["top_performer"]:
        tp = summary["top_performer"]
        print(f"Top performer: \"{tp['title'][:50]}\" (score: {tp['score']}, {tp['comments']} comments)")

    hr = summary["hypothesis_review"]
    if hr["total"] > 0:
        acc_str = f"{hr['accuracy']:.0%}" if hr['accuracy'] is not None else "?"
        print(f"Hypotheses: {hr['verified']}/{hr['total']} verified ({acc_str})")

    if summary["observations"]:
        print()
        print("OBSERVATIONS:")
        for i, obs in enumerate(summary["observations"], 1):
            confidence = obs.get("confidence", "?").upper()
            print(f"  {i}. [{confidence}] {obs['observation']}")
            print(f"     → {obs['implication']}")

    if summary["learnings"]:
        print()
        print("KEY LEARNINGS:")
        for i, l in enumerate(summary["learnings"], 1):
            print(f"  {i}. {l}")

    if args.json:
        print(json.dumps(summary, indent=2))


def cmd_summary(args):
    """Display a saved daily summary."""
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = load_summary(date)

    if not summary:
        print(f"No summary found for {date}")
        return

    print(f"DAILY SUMMARY — {date}")
    print("=" * 50)

    act = summary.get("activity", {})
    print(f"Activity: {act.get('heartbeats', 0)} scans, {act.get('posts_made', 0)} posts, {act.get('comments_made', 0)} comments")

    eng = summary.get("engagement", {})
    print(f"Engagement: {eng.get('posts_tracked', 0)} tracked, avg score {eng.get('avg_score', 0)}")

    if summary.get("learnings"):
        print()
        print("KEY LEARNINGS:")
        for i, l in enumerate(summary["learnings"], 1):
            print(f"  {i}. {l}")

    if args.json:
        print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Evening Distillation — Summary for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    r = sub.add_parser("run", help="Run full evening distillation")
    r.add_argument("--date", help="Date to distill (YYYY-MM-DD)")
    r.add_argument("--dry-run", action="store_true", help="Don't save results")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    s = sub.add_parser("summary", help="Display a saved daily summary")
    s.add_argument("--date", help="Date to display (YYYY-MM-DD)")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {"run": cmd_run, "summary": cmd_summary}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
