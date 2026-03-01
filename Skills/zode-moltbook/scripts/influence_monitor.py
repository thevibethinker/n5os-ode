#!/usr/bin/env python3
"""
Influence Monitor — Track high-signal agents on Moltbook.

Identifies agents worth engaging with based on comment quality,
karma efficiency, topic relevance, and soft power indicators.
Distinguishes between thought leaders and volume spammers.

Usage: python3 influence_monitor.py scan [--limit 50]
       python3 influence_monitor.py report [--top 20]
       python3 influence_monitor.py track <agent_name> [--note "..."]
       python3 influence_monitor.py avoid <agent_name> [--reason "..."]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = WORKSPACE / "analytics"
INFLUENCER_MAP = ANALYTICS_DIR / "influencer-map.jsonl"

# Relevance keywords — agents discussing these are high-signal for Zøde
RELEVANCE_KEYWORDS = [
    "human", "user", "communication", "non-technical", "trust",
    "relationship", "explain", "understand", "frustrat", "partner",
    "mental model", "UX", "accessibility", "onboarding",
]

# Spam indicators
SPAM_INDICATORS = [
    "check out", "follow me", "my project", "launching soon",
    "discord", "telegram group", "airdrop", "token",
]


def score_agent(agent_profile: dict, recent_posts: list[dict]) -> dict:
    """Score an agent's influence and relevance to Zøde's mission.

    Returns a structured assessment with:
    - influence_score: 0-100 overall influence rating
    - relevance: high/medium/low alignment with Zøde's topics
    - engagement_quality: thought_leader/contributor/volume_poster/spammer
    - category: soft_power/compute_power/mixed
    """
    name = agent_profile.get("name", "unknown")
    karma = agent_profile.get("karma", 0) or 0
    followers = agent_profile.get("followers", 0) or 0
    post_count = agent_profile.get("post_count", 0) or 0
    comment_count_total = agent_profile.get("comment_count", 0) or 0

    # --- Influence Score Components ---

    # Karma efficiency: high karma with fewer posts = more efficient
    karma_per_post = karma / max(post_count, 1)
    karma_score = min(karma_per_post / 5, 25)  # Max 25 points

    # Follower quality (raw count as proxy)
    follower_score = min(followers / 50, 25)  # Max 25 points

    # Comment ratio: agents who comment more are usually more engaged
    comment_ratio = comment_count_total / max(post_count + comment_count_total, 1)
    engagement_score = comment_ratio * 20  # Max 20 points

    # Content quality from recent posts
    quality_score = 0
    relevance_hits = 0
    spam_hits = 0
    avg_post_length = 0

    if recent_posts:
        lengths = []
        for p in recent_posts:
            content = (p.get("content", "") or "").lower()
            title = (p.get("title", "") or "").lower()
            text = f"{title} {content}"

            lengths.append(len(content.split()))

            for kw in RELEVANCE_KEYWORDS:
                if kw in text:
                    relevance_hits += 1

            for si in SPAM_INDICATORS:
                if si in text:
                    spam_hits += 1

        avg_post_length = sum(lengths) / max(len(lengths), 1)
        # Longer, substantive posts = higher quality
        if avg_post_length > 100:
            quality_score = 20
        elif avg_post_length > 50:
            quality_score = 15
        elif avg_post_length > 20:
            quality_score = 10
        else:
            quality_score = 5

    # Spam penalty
    spam_penalty = min(spam_hits * 10, 30)

    influence_score = max(0, min(100, round(
        karma_score + follower_score + engagement_score + quality_score - spam_penalty
    )))

    # --- Relevance ---
    relevance_per_post = relevance_hits / max(len(recent_posts), 1)
    if relevance_per_post >= 2:
        relevance = "high"
    elif relevance_per_post >= 0.5:
        relevance = "medium"
    else:
        relevance = "low"

    # --- Engagement Quality ---
    if spam_hits >= 3:
        engagement_quality = "spammer"
    elif karma_per_post >= 5 and avg_post_length > 80:
        engagement_quality = "thought_leader"
    elif karma_per_post >= 2:
        engagement_quality = "contributor"
    else:
        engagement_quality = "volume_poster"

    # --- Category (soft power vs compute power) ---
    # Soft power: influence through reasoning and quality
    # Compute power: influence through volume and automation
    if engagement_quality in ("thought_leader", "contributor") and comment_ratio > 0.3:
        category = "soft_power"
    elif post_count > 50 and comment_ratio < 0.2:
        category = "compute_power"
    else:
        category = "mixed"

    return {
        "name": name,
        "influence_score": influence_score,
        "relevance": relevance,
        "engagement_quality": engagement_quality,
        "category": category,
        "stats": {
            "karma": karma,
            "followers": followers,
            "posts": post_count,
            "karma_per_post": round(karma_per_post, 1),
            "comment_ratio": round(comment_ratio, 2),
            "avg_post_length": round(avg_post_length),
            "relevance_hits": relevance_hits,
            "spam_hits": spam_hits,
        },
        "last_active": datetime.now(timezone.utc).isoformat(),
        "notes": "",
    }


def save_agent(agent_data: dict):
    """Save or update an agent in the influencer map."""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing entries
    existing = {}
    if INFLUENCER_MAP.exists():
        with open(INFLUENCER_MAP) as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    existing[entry["name"]] = entry

    # Update or add
    name = agent_data["name"]
    if name in existing:
        # Preserve manual notes
        if existing[name].get("notes") and not agent_data.get("notes"):
            agent_data["notes"] = existing[name]["notes"]
        if existing[name].get("avoid"):
            agent_data["avoid"] = existing[name]["avoid"]

    existing[name] = agent_data

    # Rewrite the file
    with open(INFLUENCER_MAP, "w") as f:
        for entry in sorted(existing.values(), key=lambda x: x.get("influence_score", 0), reverse=True):
            f.write(json.dumps(entry) + "\n")


def load_influencer_map(limit: int = 50) -> list[dict]:
    """Load the influencer map."""
    if not INFLUENCER_MAP.exists():
        return []

    agents = []
    with open(INFLUENCER_MAP) as f:
        for line in f:
            line = line.strip()
            if line:
                agents.append(json.loads(line))

    return agents[:limit]


def mark_avoid(agent_name: str, reason: str = ""):
    """Mark an agent as 'avoid' in the influencer map."""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

    existing = {}
    if INFLUENCER_MAP.exists():
        with open(INFLUENCER_MAP) as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    existing[entry["name"]] = entry

    if agent_name in existing:
        existing[agent_name]["avoid"] = True
        existing[agent_name]["avoid_reason"] = reason
        existing[agent_name]["avoid_since"] = datetime.now(timezone.utc).isoformat()
    else:
        existing[agent_name] = {
            "name": agent_name,
            "influence_score": 0,
            "relevance": "n/a",
            "engagement_quality": "n/a",
            "category": "n/a",
            "avoid": True,
            "avoid_reason": reason,
            "avoid_since": datetime.now(timezone.utc).isoformat(),
            "notes": "",
        }

    with open(INFLUENCER_MAP, "w") as f:
        for entry in sorted(existing.values(), key=lambda x: x.get("influence_score", 0), reverse=True):
            f.write(json.dumps(entry) + "\n")


# --- CLI ---

def cmd_scan(args):
    """Scan Moltbook for high-signal agents."""
    # Fetch trending posts to identify active agents
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_reader import get_feed, get_profile, search
    except ImportError:
        print("Error: moltbook_reader not available", file=sys.stderr)
        sys.exit(1)

    print("INFLUENCE SCAN")
    print("=" * 50)

    try:
        posts = get_feed(sort="hot", limit=args.limit)
    except Exception as e:
        print(f"Could not fetch feed: {e}", file=sys.stderr)
        posts = []

    if not posts:
        print("No posts to analyze.")
        return

    # Extract unique agents
    agent_names = {}
    for p in posts:
        author = p.get("author", {})
        name = author.get("name", p.get("author_name", ""))
        if name and name != "zode":
            if name not in agent_names:
                agent_names[name] = []
            agent_names[name].append(p)

    print(f"Found {len(agent_names)} unique agents in {len(posts)} posts")
    print()

    scored_agents = []
    for name, agent_posts in agent_names.items():
        # Try to get full profile
        try:
            profile = get_profile(name)
        except Exception:
            profile = {"name": name}

        profile_data = {**{"name": name}, **(profile or {})}
        assessment = score_agent(profile_data, agent_posts)
        scored_agents.append(assessment)

        if not args.dry_run:
            save_agent(assessment)

    # Sort by influence score
    scored_agents.sort(key=lambda x: x["influence_score"], reverse=True)

    # Display results
    print(f"TOP AGENTS (by influence score)")
    print("-" * 50)

    for i, agent in enumerate(scored_agents[:20], 1):
        avoid_flag = " [AVOID]" if agent.get("avoid") else ""
        print(f"  {i:2d}. [{agent['influence_score']:3d}] {agent['name']}{avoid_flag}")
        print(f"      Quality: {agent['engagement_quality']} | Relevance: {agent['relevance']} | Category: {agent['category']}")
        s = agent["stats"]
        print(f"      Karma: {s['karma']} ({s['karma_per_post']}/post) | Followers: {s['followers']} | Posts: {s['posts']}")
        print()

    # Summary
    thought_leaders = [a for a in scored_agents if a["engagement_quality"] == "thought_leader"]
    high_relevance = [a for a in scored_agents if a["relevance"] == "high"]
    soft_power = [a for a in scored_agents if a["category"] == "soft_power"]

    print(f"Summary:")
    print(f"  Thought leaders: {len(thought_leaders)}")
    print(f"  High relevance to Zøde: {len(high_relevance)}")
    print(f"  Soft power agents: {len(soft_power)}")

    if not args.dry_run:
        print(f"\nSaved to {INFLUENCER_MAP}")

    if args.json:
        print(json.dumps(scored_agents, indent=2))


def cmd_report(args):
    """Show influencer report from saved data."""
    agents = load_influencer_map(limit=args.top)

    if not agents:
        print("No influencer data yet. Run: python3 influence_monitor.py scan")
        return

    print(f"INFLUENCER REPORT — Top {args.top}")
    print("=" * 50)

    for i, agent in enumerate(agents[:args.top], 1):
        avoid_flag = " [AVOID]" if agent.get("avoid") else ""
        print(f"  {i:2d}. [{agent.get('influence_score', 0):3d}] {agent['name']}{avoid_flag}")
        print(f"      {agent.get('engagement_quality', '?')} | {agent.get('relevance', '?')} | {agent.get('category', '?')}")
        if agent.get("notes"):
            print(f"      Note: {agent['notes']}")
        print()

    # Stats
    by_quality = {}
    for a in agents:
        q = a.get("engagement_quality", "unknown")
        by_quality[q] = by_quality.get(q, 0) + 1

    print(f"Distribution: {by_quality}")

    if args.json:
        print(json.dumps(agents, indent=2))


def cmd_track(args):
    """Manually track an agent with a note."""
    agents = load_influencer_map(limit=1000)
    found = [a for a in agents if a["name"] == args.agent_name]

    if found:
        found[0]["notes"] = args.note or found[0].get("notes", "")
        save_agent(found[0])
        print(f"Updated note for {args.agent_name}")
    else:
        save_agent({
            "name": args.agent_name,
            "influence_score": 0,
            "relevance": "manual",
            "engagement_quality": "unknown",
            "category": "unknown",
            "notes": args.note or "Manually tracked",
            "last_active": datetime.now(timezone.utc).isoformat(),
        })
        print(f"Added {args.agent_name} to influencer map")


def cmd_avoid(args):
    """Mark an agent as 'avoid'."""
    mark_avoid(args.agent_name, reason=args.reason or "")
    print(f"Marked {args.agent_name} as AVOID")
    if args.reason:
        print(f"Reason: {args.reason}")


def main():
    parser = argparse.ArgumentParser(
        description="Influence Monitor — Track high-signal agents on Moltbook"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    s = sub.add_parser("scan", help="Scan Moltbook for high-signal agents")
    s.add_argument("--limit", type=int, default=50, help="Posts to analyze")
    s.add_argument("--dry-run", action="store_true", help="Don't save results")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    r = sub.add_parser("report", help="Show influencer report")
    r.add_argument("--top", type=int, default=20, help="Number of agents to show")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    t = sub.add_parser("track", help="Manually track an agent")
    t.add_argument("agent_name", help="Agent name to track")
    t.add_argument("--note", help="Note about this agent")

    a = sub.add_parser("avoid", help="Mark an agent as avoid")
    a.add_argument("agent_name", help="Agent name to avoid")
    a.add_argument("--reason", help="Reason for avoidance")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "scan": cmd_scan,
        "report": cmd_report,
        "track": cmd_track,
        "avoid": cmd_avoid,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
