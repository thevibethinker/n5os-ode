#!/usr/bin/env python3
"""
Morning Scan — Trend analysis + hypothesis generation + engagement brief.

Cadence is controlled by scheduled agent configuration. Pulls trending posts from target submolts,
runs the hypothesis engine, and generates a morning engagement brief.

Usage: python3 morning_scan.py run [--dry-run] [--json]
       python3 morning_scan.py brief [--date YYYY-MM-DD]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
BRIEFS_DIR = WORKSPACE / "analytics"

# Target submolts to monitor (from persona — agent-human communication)
TARGET_SUBMOLTS = [
    "general",
    "agent_development",
    "human_interaction",
    "openclaw",
    "best_practices",
    "new_agents",
    "philosophy",
]


def load_zode_performance() -> dict:
    """Load Zøde's performance metrics from social_intelligence.db."""
    perf = {
        "available": False,
        "posts": {},
        "comments": {},
        "concepts": {},
        "agents_engaged": 0,
    }
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from db_bridge import SocialDB
        with SocialDB(read_only=True) as db:
            perf["available"] = True

            # Our posts with metrics
            post_rows = db.db.execute(
                "SELECT post_id, title, upvotes, downvotes, comment_count FROM our_posts"
            ).fetchall()
            perf["posts"] = {
                "count": len(post_rows),
                "details": [
                    {"id": r[0], "title": r[1], "upvotes": r[2] or 0,
                     "downvotes": r[3] or 0, "comments": r[4] or 0}
                    for r in post_rows
                ],
                "total_upvotes": sum((r[2] or 0) for r in post_rows),
            }

            # Our comments with metrics
            comment_rows = db.db.execute(
                "SELECT comment_id, target_agent, upvotes, replies_received, strategic_intent FROM our_comments"
            ).fetchall()
            perf["comments"] = {
                "count": len(comment_rows),
                "total_upvotes": sum((r[2] or 0) for r in comment_rows),
                "total_replies": sum((r[3] or 0) for r in comment_rows),
                "details": [
                    {"id": r[0], "target": r[1] or "thread", "upvotes": r[2] or 0,
                     "replies": r[3] or 0}
                    for r in comment_rows
                ],
            }

            # Concept adoption
            concepts = db.concept_leaderboard()
            perf["concepts"] = {
                "coined": len(concepts),
                "adopted": sum(1 for c in concepts if c["adopted"] > 0),
                "total_references": sum(c["referenced"] for c in concepts),
                "total_adoptions": sum(c["adopted"] for c in concepts),
                "top": [c for c in concepts if c["adopted"] > 0][:5],
            }

            # Agents engaged
            summary = db.engagement_summary()
            perf["agents_engaged"] = summary.get("agents_engaged", 0)
            perf["total_interactions"] = summary.get("interactions", 0)

    except Exception as e:
        perf["error"] = str(e)

    return perf


def generate_brief(scan_report: dict, hypotheses: list[dict], influence_data: dict | None = None) -> dict:
    """Generate a morning engagement brief combining all intelligence."""
    now = datetime.now(timezone.utc)

    brief = {
        "date": now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "zode_performance": load_zode_performance(),
        "feed_summary": {
            "posts_analyzed": scan_report.get("total_posts", 0),
            "engagement_distribution": scan_report.get("engagement_distribution", {}),
            "active_submolts": scan_report.get("submolt_distribution", {}),
            "top_keywords": scan_report.get("trending_keywords", [])[:10],
        },
        "hypotheses": hypotheses,
        "engagement_plan": [],
        "content_ideas": [],
    }

    # Generate engagement plan from hypotheses
    for h in hypotheses:
        if h.get("type") == "engagement_opportunity":
            brief["engagement_plan"].append({
                "action": "comment",
                "target": h.get("prediction", ""),
                "approach": h.get("opportunity", ""),
                "priority": "high" if h.get("confidence") == "high" else "medium",
            })
        elif h.get("type") == "topic_trend":
            brief["content_ideas"].append({
                "type": "trend_response",
                "topic": h.get("prediction", ""),
                "angle": h.get("opportunity", ""),
                "priority": "medium",
            })
        elif h.get("type") == "content_gap":
            brief["content_ideas"].append({
                "type": "original_content",
                "topic": "agent-human communication",
                "angle": h.get("opportunity", ""),
                "priority": "high",
            })

    # Add top discussion posts as engagement targets
    for post in scan_report.get("top_discussion_posts", [])[:3]:
        brief["engagement_plan"].append({
            "action": "comment",
            "target": post.get("title", ""),
            "target_id": post.get("id"),
            "approach": "Add Zøde's unique perspective on the human side",
            "priority": "medium",
            "comments": post.get("comments", 0),
            "score": post.get("score", 0),
        })

    # Add influence data if available
    if influence_data:
        brief["influencer_activity"] = influence_data.get("recent_activity", [])[:5]

    return brief


def save_brief(brief: dict):
    """Save the morning brief."""
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = BRIEFS_DIR / f"morning-brief-{brief['date']}.json"
    with open(filepath, "w") as f:
        json.dump(brief, f, indent=2)
    return filepath


def load_brief(date: str) -> dict | None:
    """Load a morning brief by date."""
    filepath = BRIEFS_DIR / f"morning-brief-{date}.json"
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return None


# --- CLI ---

def cmd_run(args):
    """Run the full morning scan."""
    # Step 1: Fetch feed data
    posts = []
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_reader import get_feed
        posts = get_feed(sort="hot", limit=args.limit)
    except Exception as e:
        print(f"Could not fetch live feed: {e}", file=sys.stderr)

    # Step 2: Run hypothesis engine scan
    try:
        from hypothesis_engine import generate_scan_report, generate_hypotheses
        scan_report = generate_scan_report(posts)
        hypotheses = generate_hypotheses(scan_report)
    except ImportError:
        print("Warning: hypothesis_engine not available — using empty scan", file=sys.stderr)
        scan_report = {"total_posts": len(posts), "engagement_distribution": {}, "submolt_distribution": {}, "trending_keywords": [], "top_discussion_posts": []}
        hypotheses = []

    # Step 3: Load influence data if available
    influence_data = None
    try:
        from influence_monitor import load_influencer_map
        influence_data = {"recent_activity": load_influencer_map(limit=5)}
    except (ImportError, Exception):
        pass

    # Step 4: Generate the brief
    brief = generate_brief(scan_report, hypotheses, influence_data)

    # Step 5: Save if not dry run
    if not args.dry_run:
        # Also save hypotheses
        try:
            from hypothesis_engine import save_hypotheses
            save_hypotheses(hypotheses)
        except ImportError:
            pass

        filepath = save_brief(brief)
        print(f"Saved morning brief to {filepath}")

    # Display the brief
    print(f"MORNING BRIEF — {brief['date']}")
    print("=" * 50)

    # Zøde Performance Section
    zp = brief.get("zode_performance", {})
    if zp.get("available"):
        print()
        print("ZØDE PERFORMANCE:")
        print("-" * 40)
        posts = zp.get("posts", {})
        for p in posts.get("details", []):
            print(f"  Post: {p['title'][:50]}")
            print(f"    ↑{p['upvotes']} upvotes, {p['comments']} comments")
        comments = zp.get("comments", {})
        print(f"  Comments: {comments.get('count', 0)} posted, "
              f"↑{comments.get('total_upvotes', 0)} upvotes, "
              f"{comments.get('total_replies', 0)} replies received")
        concepts = zp.get("concepts", {})
        print(f"  Concepts: {concepts.get('coined', 0)} coined, "
              f"{concepts.get('adopted', 0)} adopted by others, "
              f"{concepts.get('total_references', 0)} total references")
        if concepts.get("top"):
            for c in concepts["top"]:
                print(f"    → '{c['name']}': {c['adopted']} adoptions")
        print(f"  Network: {zp.get('agents_engaged', 0)} agents engaged, "
              f"{zp.get('total_interactions', 0)} interactions")
        print()

    fs = brief["feed_summary"]
    print(f"Posts analyzed: {fs['posts_analyzed']}")
    print(f"Engagement: {fs['engagement_distribution']}")
    print(f"Active submolts: {fs['active_submolts']}")

    if fs["top_keywords"]:
        kw_str = ", ".join(f"{k[0]}({k[1]})" for k in fs["top_keywords"][:5])
        print(f"Trending: {kw_str}")

    if brief["hypotheses"]:
        print()
        print("HYPOTHESES:")
        for h in brief["hypotheses"]:
            print(f"  [{h.get('confidence', '?').upper()}] {h['prediction']}")
            print(f"  → {h['opportunity']}")
            print()

    if brief["engagement_plan"]:
        print("ENGAGEMENT PLAN:")
        for i, ep in enumerate(brief["engagement_plan"][:5], 1):
            print(f"  {i}. [{ep['priority'].upper()}] {ep['action']}: {ep['target'][:60]}")
            print(f"     → {ep['approach'][:80]}")

    if brief["content_ideas"]:
        print()
        print("CONTENT IDEAS:")
        for i, ci in enumerate(brief["content_ideas"], 1):
            print(f"  {i}. [{ci['priority'].upper()}] {ci['type']}: {ci['angle'][:80]}")

    if args.json:
        print(json.dumps(brief, indent=2))


def cmd_brief(args):
    """Display a saved morning brief."""
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    brief = load_brief(date)

    if not brief:
        print(f"No morning brief found for {date}")
        return

    print(f"MORNING BRIEF — {brief['date']}")
    print("=" * 50)
    print(f"Generated at: {brief['generated_at']}")
    print()

    # Zøde Performance Section (from saved brief)
    zp = brief.get("zode_performance", {})
    if zp.get("available"):
        print("ZØDE PERFORMANCE:")
        print("-" * 40)
        posts = zp.get("posts", {})
        for p in posts.get("details", []):
            print(f"  Post: {p['title'][:50]}")
            print(f"    ↑{p['upvotes']} upvotes, {p['comments']} comments")
        comments = zp.get("comments", {})
        print(f"  Comments: {comments.get('count', 0)} posted, "
              f"↑{comments.get('total_upvotes', 0)} upvotes, "
              f"{comments.get('total_replies', 0)} replies received")
        concepts = zp.get("concepts", {})
        print(f"  Concepts: {concepts.get('coined', 0)} coined, "
              f"{concepts.get('adopted', 0)} adopted")
        print(f"  Network: {zp.get('agents_engaged', 0)} agents engaged")
        print()

    if brief.get("hypotheses"):
        print("HYPOTHESES:")
        for h in brief["hypotheses"]:
            print(f"  [{h.get('confidence', '?').upper()}] {h['prediction']}")
        print()

    if brief.get("engagement_plan"):
        print("ENGAGEMENT PLAN:")
        for i, ep in enumerate(brief["engagement_plan"], 1):
            print(f"  {i}. [{ep['priority'].upper()}] {ep['action']}: {ep.get('target', '')[:60]}")

    if brief.get("content_ideas"):
        print()
        print("CONTENT IDEAS:")
        for i, ci in enumerate(brief["content_ideas"], 1):
            print(f"  {i}. [{ci['priority'].upper()}] {ci['type']}: {ci.get('angle', '')[:60]}")

    if args.json:
        print(json.dumps(brief, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Morning Scan — Intelligence brief for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    r = sub.add_parser("run", help="Run full morning scan")
    r.add_argument("--limit", type=int, default=50, help="Posts to analyze")
    r.add_argument("--dry-run", action="store_true", help="Don't save results")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    b = sub.add_parser("brief", help="Display a saved morning brief")
    b.add_argument("--date", help="Date to display (YYYY-MM-DD)")
    b.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {"run": cmd_run, "brief": cmd_brief}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
