#!/usr/bin/env python3
"""
Distillation — Evening analysis extracting the 3 most needle-moving observations.

Reviews daily engagement data, extracts patterns, and updates the learning log.
Operates at the narrative level (per V's directive: tune narratives, not word choices).

Usage: python3 distillation.py run [--date YYYY-MM-DD]
       python3 distillation.py history [--limit 7]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
LEARNINGS_DIR = WORKSPACE / "learnings"
DISTILLATION_FILE = LEARNINGS_DIR / "daily-distillation.jsonl"
RUBRIC_EVOLUTION_FILE = LEARNINGS_DIR / "rubric-evolution.jsonl"


def extract_observations(engagement_data: list[dict]) -> list[dict]:
    """Extract the 3 most needle-moving observations from engagement data.

    Each observation focuses on narrative-level patterns (which stories resonate,
    which mental models click, which framings build trust) — not word-level tuning.
    """
    observations = []

    if not engagement_data:
        return [{
            "type": "no_data",
            "observation": "No engagement data available today. This could mean we didn't post, or metrics haven't been collected yet.",
            "implication": "Run engagement_tracker.py to collect metrics, or check if posts were published.",
            "confidence": "n/a",
        }]

    # Sort by engagement score
    sorted_by_score = sorted(engagement_data, key=lambda x: x.get("score", 0), reverse=True)
    sorted_by_comments = sorted(engagement_data, key=lambda x: x.get("comment_count", 0), reverse=True)

    # Observation 1: Best performing content
    if sorted_by_score:
        best = sorted_by_score[0]
        observations.append({
            "type": "top_performer",
            "observation": f"Best performing content: '{best.get('title', 'untitled')[:60]}' (score: {best.get('score', 0)}, comments: {best.get('comment_count', 0)})",
            "implication": "Identify what narrative pattern this follows — is it a translation, a framework, a specific scenario, or a provocation? Double down on this pattern.",
            "confidence": "high",
            "related_id": best.get("id"),
        })

    # Observation 2: Comment quality vs upvote ratio
    high_comment_low_score = [
        p for p in engagement_data
        if (p.get("comment_count", 0) or 0) > 3 and (p.get("score", 0) or 0) < 5
    ]
    if high_comment_low_score:
        example = high_comment_low_score[0]
        observations.append({
            "type": "discussion_vs_approval",
            "observation": f"Content generating discussion but not upvotes: '{example.get('title', '')[:60]}' ({example.get('comment_count', 0)} comments, score {example.get('score', 0)})",
            "implication": "This content is provoking thought but not consensus. Consider: is it too contrarian? Or is it finding the edges of community thinking? Both can be valuable — controversial content builds recognition even without upvotes.",
            "confidence": "medium",
            "related_id": example.get("id"),
        })
    else:
        # Observation 2 fallback: Overall engagement trend
        avg_score = sum(p.get("score", 0) or 0 for p in engagement_data) / max(len(engagement_data), 1)
        observations.append({
            "type": "engagement_trend",
            "observation": f"Average engagement score: {avg_score:.1f} across {len(engagement_data)} posts/comments",
            "implication": ("Above 5 is healthy. " if avg_score > 5 else "Below 5 suggests content isn't resonating broadly. ") + "Consider whether ICP relevance or novelty needs adjustment.",
            "confidence": "medium",
        })

    # Observation 3: Narrative pattern analysis
    # Look at what types of content perform best
    frameworks = [p for p in engagement_data if any(kw in (p.get("content", "") or "").lower() for kw in ["framework", "model", "pattern", "principle"])]
    stories = [p for p in engagement_data if any(kw in (p.get("content", "") or "").lower() for kw in ["when your human", "imagine", "picture", "example", "scenario"])]
    questions = [p for p in engagement_data if "?" in (p.get("title", "") or "") or "?" in (p.get("content", "") or "")[:100]]

    framework_avg = sum(p.get("score", 0) or 0 for p in frameworks) / max(len(frameworks), 1) if frameworks else 0
    story_avg = sum(p.get("score", 0) or 0 for p in stories) / max(len(stories), 1) if stories else 0
    question_avg = sum(p.get("score", 0) or 0 for p in questions) / max(len(questions), 1) if questions else 0

    best_type = max([
        ("frameworks", framework_avg, len(frameworks)),
        ("stories/scenarios", story_avg, len(stories)),
        ("questions/provocations", question_avg, len(questions)),
    ], key=lambda x: x[1])

    observations.append({
        "type": "narrative_pattern",
        "observation": f"Narrative type '{best_type[0]}' performs best (avg score {best_type[1]:.1f}, n={best_type[2]})",
        "implication": f"Lean into {best_type[0]} in upcoming content. This tells us the community responds to this framing style — not just the topic, but how we present it.",
        "confidence": "low" if best_type[2] < 3 else "medium",
    })

    return observations[:3]


def save_distillation(date: str, observations: list[dict]):
    """Save daily distillation to JSONL log."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": date,
        "distilled_at": datetime.now(timezone.utc).isoformat(),
        "observations": observations,
    }
    with open(DISTILLATION_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_history(limit: int = 7) -> list[dict]:
    """Load recent distillation history."""
    if not DISTILLATION_FILE.exists():
        return []
    entries = []
    with open(DISTILLATION_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries[-limit:]


# --- CLI ---

def cmd_run(args):
    """Run evening distillation."""
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Try to load engagement data from analytics
    analytics_dir = WORKSPACE / "analytics"
    engagement_file = analytics_dir / f"engagement-{date}.json"

    engagement_data = []
    if engagement_file.exists():
        with open(engagement_file) as f:
            engagement_data = json.load(f)
    else:
        print(f"No engagement data found for {date}", file=sys.stderr)
        print(f"Expected: {engagement_file}", file=sys.stderr)
        print("Running with empty dataset...", file=sys.stderr)

    observations = extract_observations(engagement_data)

    print(f"EVENING DISTILLATION — {date}")
    print("=" * 50)
    print(f"Data points analyzed: {len(engagement_data)}")
    print()

    for i, obs in enumerate(observations, 1):
        print(f"  Observation {i}: [{obs.get('confidence', '?').upper()}]")
        print(f"  {obs['observation']}")
        print(f"  → {obs['implication']}")
        print()

    if not args.dry_run:
        save_distillation(date, observations)
        print(f"Saved to {DISTILLATION_FILE}")

    if args.json:
        print(json.dumps({"date": date, "observations": observations}, indent=2))


def cmd_history(args):
    """Show recent distillation history."""
    entries = load_history(limit=args.limit)
    if not entries:
        print("No distillation history yet.")
        return

    for entry in entries:
        print(f"\n--- {entry['date']} ---")
        for i, obs in enumerate(entry.get("observations", []), 1):
            print(f"  {i}. [{obs.get('confidence', '?').upper()}] {obs['observation']}")


def main():
    parser = argparse.ArgumentParser(
        description="Distillation — Evening learning extraction for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    r = sub.add_parser("run", help="Run evening distillation")
    r.add_argument("--date", help="Date to distill (YYYY-MM-DD)")
    r.add_argument("--dry-run", action="store_true", help="Don't save results")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    h = sub.add_parser("history", help="Show distillation history")
    h.add_argument("--limit", type=int, default=7, help="Number of days to show")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "run": cmd_run,
        "history": cmd_history,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
