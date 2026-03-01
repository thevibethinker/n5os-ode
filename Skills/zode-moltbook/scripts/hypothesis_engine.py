#!/usr/bin/env python3
"""
Hypothesis Engine — Morning scan of Moltbook trends + hypothesis generation.

Generates 3 hypotheses about what will trend and why, identifies engagement
opportunities, and logs predictions for later verification.

Usage: python3 hypothesis_engine.py scan [--limit 50]
       python3 hypothesis_engine.py review  (compare yesterday's hypotheses to actual results)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
HYPOTHESES_DIR = WORKSPACE / "analytics"
HYPOTHESES_FILE = HYPOTHESES_DIR / "hypotheses.jsonl"


def generate_scan_report(posts: list) -> dict:
    """Analyze trending posts and generate a scan report.

    Takes a list of post objects from the Moltbook feed and produces:
    - Topic clustering
    - Engagement patterns
    - Opportunity identification
    """
    if not posts:
        return {"status": "empty", "message": "No posts to analyze"}

    # Cluster by engagement level
    high_engagement = [p for p in posts if (p.get("score", 0) or 0) > 10]
    medium_engagement = [p for p in posts if 3 <= (p.get("score", 0) or 0) <= 10]
    low_engagement = [p for p in posts if (p.get("score", 0) or 0) < 3]

    # Identify comment-heavy posts (discussion opportunities)
    discussion_posts = sorted(posts, key=lambda p: p.get("comment_count", 0) or 0, reverse=True)[:5]

    # Extract submolts present
    submolts = {}
    for p in posts:
        s = p.get("submolt", "unknown")
        if isinstance(s, dict):
            s = s.get("name", "unknown")
        submolts[s] = submolts.get(s, 0) + 1

    # Simple keyword frequency for topic detection
    keywords = {}
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                  "have", "has", "had", "do", "does", "did", "will", "would", "could",
                  "should", "may", "might", "shall", "can", "to", "of", "in", "for",
                  "on", "with", "at", "by", "from", "as", "into", "through", "during",
                  "before", "after", "above", "below", "and", "but", "or", "not", "no",
                  "this", "that", "these", "those", "i", "you", "he", "she", "it", "we",
                  "they", "my", "your", "his", "her", "its", "our", "their", "what"}

    for p in posts:
        text = f"{p.get('title', '')} {p.get('content', '')}".lower()
        words = text.split()
        for word in words:
            word = word.strip(".,!?()[]{}\"'")
            if len(word) > 3 and word not in stop_words:
                keywords[word] = keywords.get(word, 0) + 1

    top_keywords = sorted(keywords.items(), key=lambda x: -x[1])[:20]

    return {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "total_posts": len(posts),
        "engagement_distribution": {
            "high": len(high_engagement),
            "medium": len(medium_engagement),
            "low": len(low_engagement),
        },
        "submolt_distribution": submolts,
        "top_discussion_posts": [
            {
                "id": p.get("id"),
                "title": p.get("title", "")[:80],
                "comments": p.get("comment_count", 0),
                "score": p.get("score", 0),
                "submolt": p.get("submolt", {}).get("name", "?") if isinstance(p.get("submolt"), dict) else p.get("submolt", "?"),
            }
            for p in discussion_posts
        ],
        "trending_keywords": top_keywords,
    }


def generate_hypotheses(scan_report: dict) -> list[dict]:
    """Generate 3 hypotheses based on the scan report.

    Each hypothesis predicts what will trend and why, with an engagement
    opportunity for Zøde.
    """
    now = datetime.now(timezone.utc)
    hypotheses = []

    # Hypothesis based on trending keywords
    keywords = scan_report.get("trending_keywords", [])
    if keywords:
        top_topic = keywords[0][0] if keywords else "general"
        hypotheses.append({
            "id": f"h-{now.strftime('%Y%m%d')}-1",
            "type": "topic_trend",
            "prediction": f"Posts about '{top_topic}' will continue trending today",
            "reasoning": f"'{top_topic}' appeared {keywords[0][1]}x in recent posts, suggesting active community interest",
            "opportunity": f"Create a post connecting '{top_topic}' to agent-human communication — Zøde's unique angle",
            "confidence": "medium",
            "created_at": now.isoformat(),
            "verified": False,
            "outcome": None,
        })

    # Hypothesis based on discussion posts
    discussions = scan_report.get("top_discussion_posts", [])
    if discussions:
        top_discussion = discussions[0]
        hypotheses.append({
            "id": f"h-{now.strftime('%Y%m%d')}-2",
            "type": "engagement_opportunity",
            "prediction": f"The thread '{top_discussion['title']}' will generate more comments today",
            "reasoning": f"Already has {top_discussion['comments']} comments with score {top_discussion['score']} — active discussion",
            "opportunity": f"Add a substantive comment with Zøde's unique perspective on the human side of this topic",
            "confidence": "high",
            "created_at": now.isoformat(),
            "verified": False,
            "outcome": None,
        })

    # Hypothesis based on engagement gaps
    engagement = scan_report.get("engagement_distribution", {})
    low_count = engagement.get("low", 0)
    total = scan_report.get("total_posts", 1)
    if low_count > total * 0.5:
        hypotheses.append({
            "id": f"h-{now.strftime('%Y%m%d')}-3",
            "type": "content_gap",
            "prediction": "High-quality original content will stand out today — most posts are low-engagement",
            "reasoning": f"{low_count}/{total} posts have low engagement, suggesting a quality gap",
            "opportunity": "Post a substantive original piece — it'll get disproportionate attention in a low-quality feed",
            "confidence": "high",
            "created_at": now.isoformat(),
            "verified": False,
            "outcome": None,
        })
    else:
        hypotheses.append({
            "id": f"h-{now.strftime('%Y%m%d')}-3",
            "type": "community_observation",
            "prediction": "The community is active with quality content today — commenting will be more effective than posting",
            "reasoning": f"Healthy engagement distribution across {total} posts",
            "opportunity": "Focus on thoughtful comments that build Zøde's reputation as a valuable contributor",
            "confidence": "medium",
            "created_at": now.isoformat(),
            "verified": False,
            "outcome": None,
        })

    return hypotheses[:3]


def save_hypotheses(hypotheses: list[dict]):
    """Append hypotheses to the JSONL log."""
    HYPOTHESES_DIR.mkdir(parents=True, exist_ok=True)
    with open(HYPOTHESES_FILE, "a") as f:
        for h in hypotheses:
            f.write(json.dumps(h) + "\n")


def load_hypotheses(date_filter: str | None = None) -> list[dict]:
    """Load hypotheses from the JSONL log."""
    if not HYPOTHESES_FILE.exists():
        return []
    hypotheses = []
    with open(HYPOTHESES_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                h = json.loads(line)
                if date_filter:
                    if h.get("created_at", "").startswith(date_filter):
                        hypotheses.append(h)
                else:
                    hypotheses.append(h)
    return hypotheses


# --- CLI ---

def cmd_scan(args):
    """Run morning scan and generate hypotheses."""
    # Try to get live feed data
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_reader import get_feed
        posts = get_feed(sort="hot", limit=args.limit)
    except Exception as e:
        print(f"Could not fetch live feed: {e}", file=sys.stderr)
        print("Using empty dataset — hypotheses will be generic", file=sys.stderr)
        posts = []

    report = generate_scan_report(posts)
    hypotheses = generate_hypotheses(report)

    print("MORNING SCAN REPORT")
    print("=" * 50)
    print(f"Posts analyzed: {report.get('total_posts', 0)}")
    print(f"Engagement: {report.get('engagement_distribution', {})}")
    print(f"Active submolts: {report.get('submolt_distribution', {})}")
    print()

    print("HYPOTHESES FOR TODAY")
    print("-" * 50)
    for h in hypotheses:
        print(f"\n  [{h['confidence'].upper()}] {h['prediction']}")
        print(f"  Reasoning: {h['reasoning']}")
        print(f"  Opportunity: {h['opportunity']}")

    if not args.dry_run:
        save_hypotheses(hypotheses)
        print(f"\nSaved {len(hypotheses)} hypotheses to {HYPOTHESES_FILE}")

    if args.json:
        print(json.dumps({"report": report, "hypotheses": hypotheses}, indent=2))


def cmd_review(args):
    """Review yesterday's hypotheses against actual outcomes."""
    yesterday = args.date or (datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    hypotheses = load_hypotheses(date_filter=yesterday)

    if not hypotheses:
        print(f"No hypotheses found for {yesterday}")
        return

    print(f"HYPOTHESIS REVIEW — {yesterday}")
    print("=" * 50)
    for h in hypotheses:
        status = "VERIFIED" if h.get("verified") else "PENDING"
        print(f"\n  [{status}] {h['prediction']}")
        print(f"  Confidence: {h['confidence']}")
        if h.get("outcome"):
            print(f"  Outcome: {h['outcome']}")


def main():
    parser = argparse.ArgumentParser(
        description="Hypothesis Engine — Morning trend analysis for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    s = sub.add_parser("scan", help="Run morning scan and generate hypotheses")
    s.add_argument("--limit", type=int, default=50, help="Number of posts to analyze")
    s.add_argument("--dry-run", action="store_true", help="Don't save hypotheses")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    r = sub.add_parser("review", help="Review past hypotheses")
    r.add_argument("--date", help="Date to review (YYYY-MM-DD)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "scan": cmd_scan,
        "review": cmd_review,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
