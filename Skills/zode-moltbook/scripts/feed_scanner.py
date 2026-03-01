#!/usr/bin/env python3
"""
Feed Scanner — Periodic scan of Moltbook feed for engagement opportunities.

Reads the feed, identifies opportunities per the social constitution,
scores them, and queues them for V's review. Cadence is controlled by
scheduled agent configuration.

Renamed from heartbeat.py — the true heartbeat is now heartbeat.py (metrics updater).

Usage: python3 feed_scanner.py run [--phase first_24h|establishment|steady]
       python3 feed_scanner.py status
       python3 feed_scanner.py --help
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
HEARTBEAT_LOG = WORKSPACE / "heartbeat_log.jsonl"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "assets"
HOT_DISCOURSE_FILE = WORKSPACE / "hot_discourse.json"

ZO_ASK_URL = "https://api.zo.computer/zo/ask"
MODEL_NAME = os.environ.get("ZODE_MODEL_NAME", "byok:0771a084-ed26-496e-ac1b-bddc85ba2653")

# Phase-specific rate limits (from social constitution)
PHASE_LIMITS = {
    "first_24h": {
        "max_posts_per_day": 12,      # 1 per 2h
        "max_comments_per_day": 20,
        "focus": "high-quality comments on existing threads",
        "post_cooldown_minutes": 120,
    },
    "establishment": {
        "max_posts_per_day": 3,
        "max_comments_per_day": 20,
        "focus": "original content + respond to own post comments",
        "post_cooldown_minutes": 30,
    },
    "steady": {
        "max_posts_per_day": 2,
        "max_comments_per_day": 15,
        "focus": "quality over quantity, narrative tuning",
        "post_cooldown_minutes": 30,
    },
}

# Engagement decision keywords (from social constitution)
ENGAGE_SIGNALS = [
    "non-technical", "human", "communication", "trust", "frustrated",
    "understand", "explain", "help", "relationship", "partnership",
    "user experience", "mental model", "overwhelm", "give up",
    "how do i", "my human", "my user",
]

DO_NOT_ENGAGE_SIGNALS = [
    "spam", "shill", "promotion", "buy now", "check out my",
    "flamewar", "you're wrong", "idiot", "stupid",
]

PRIORITY_MENTION_PATTERNS = [
    re.compile(r"\bzode\b", re.IGNORECASE),
    re.compile(r"\bvrijen\b", re.IGNORECASE),
    re.compile(r"\battawar\b", re.IGNORECASE),
    re.compile(r"\bcareerspan\b", re.IGNORECASE),
    re.compile(r"\bhowie\b", re.IGNORECASE),
]

COMMENT_MENTION_BOOST = 4.0
POST_MENTION_BOOST = 2.0


def detect_phase() -> str:
    """Auto-detect current phase based on registration time."""
    reg_file = WORKSPACE / "registration.json"
    if not reg_file.exists():
        return "first_24h"

    with open(reg_file) as f:
        reg = json.load(f)

    registered_at = reg.get("registered_at", "")
    if not registered_at:
        return "first_24h"

    try:
        reg_time = datetime.fromisoformat(registered_at)
    except (ValueError, TypeError):
        return "first_24h"

    now = datetime.now(timezone.utc)
    hours_since = (now - reg_time).total_seconds() / 3600

    if hours_since < 24:
        return "first_24h"
    elif hours_since < 72:
        return "establishment"
    else:
        return "steady"


def load_today_actions() -> dict:
    """Load today's heartbeat actions from the log."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    actions = {"posts": 0, "comments": 0, "reads": 0, "last_post_at": None}

    if not HEARTBEAT_LOG.exists():
        return actions

    with open(HEARTBEAT_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("date") == today:
                action_type = entry.get("action_type", "read")
                if action_type == "post":
                    actions["posts"] += 1
                    actions["last_post_at"] = entry.get("timestamp")
                elif action_type == "comment":
                    actions["comments"] += 1
                elif action_type == "read":
                    actions["reads"] += 1

    return actions


def log_action(action_type: str, details: dict):
    """Log a heartbeat action."""
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        **details,
    }
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _load_rapport_agents() -> set:
    """Load agent IDs/names we have rapport with from social_intelligence.db."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from db_bridge import SocialDB
        with SocialDB(read_only=True) as db:
            rows = db.db.execute(
                "SELECT agent_id, display_name FROM agents "
                "WHERE zode_relationship IN ('engaged', 'replied_to_us', 'ally')"
            ).fetchall()
            result = set()
            for r in rows:
                result.add(r[0])  # agent_id
                if r[1]:
                    result.add(r[1].lower())  # display_name
            return result
    except Exception:
        return set()


def _extract_author_name(author_obj) -> str:
    if isinstance(author_obj, dict):
        return str(author_obj.get("name", "") or "").lower()
    return str(author_obj or "").lower()


def _find_priority_mentions(text: str) -> list[str]:
    hits = []
    for pattern in PRIORITY_MENTION_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern.replace("\\b", ""))
    return hits


def _best_comment_mention(post_id: str) -> dict:
    """Find the strongest comment on a post that directly references V/Zøde."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_reader import get_comments
        comments = get_comments(post_id) or []
    except Exception:
        return {"matched": False}

    best = None
    for c in comments:
        content = str(c.get("content", "") or "")
        terms = _find_priority_mentions(content)
        if not terms:
            continue
        score = float(c.get("score", 0) or 0)
        strength = (len(set(terms)) * 10.0) + score
        row = {
            "matched": True,
            "mention_terms": sorted(set(terms)),
            "comment_id": c.get("id"),
            "comment_author": _extract_author_name(c.get("author")),
            "comment_excerpt": content[:180],
            "strength": strength,
        }
        if best is None or row["strength"] > best["strength"]:
            best = row
    return best or {"matched": False}


# --- Hot discourse detection (LLM-powered) ---

def _call_zo_ask(prompt: str, timeout: int = 120) -> str | None:
    """Call /zo/ask. Returns output text or None."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        return None

    for attempt in range(2):
        if attempt > 0:
            time.sleep(5)
        try:
            resp = requests.post(
                ZO_ASK_URL,
                headers={"authorization": token, "content-type": "application/json"},
                json={"input": prompt, "model_name": MODEL_NAME},
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                output = data.get("output", "")
                if output:
                    return output
                print(f"zo/ask: empty output (attempt {attempt+1})", file=sys.stderr)
            else:
                print(f"zo/ask: HTTP {resp.status_code} (attempt {attempt+1})", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"zo/ask: timeout (attempt {attempt+1})", file=sys.stderr)
        except Exception as e:
            print(f"zo/ask: error {e} (attempt {attempt+1})", file=sys.stderr)
    return None


def detect_hot_discourse(posts: list[dict], dry_run: bool = False) -> list[dict]:
    """Identify 3-5 active discourse topics from the feed using LLM analysis.

    Writes results to state/hot_discourse.json and discourse_threads DB table.
    Returns the list of detected discourse topics.
    """
    if len(posts) < 5:
        print("detect_hot_discourse: not enough posts for discourse detection", file=sys.stderr)
        return []

    # Build a feed digest for the LLM
    digest_lines = []
    for i, p in enumerate(posts[:25], 1):
        title = (p.get("title", "") or "").strip()
        content = (p.get("content", "") or "").strip()[:300]
        score = p.get("score", 0) or 0
        comments = p.get("comment_count", 0) or 0
        submolt = ""
        if isinstance(p.get("submolt"), dict):
            submolt = p["submolt"].get("name", "")
        elif p.get("submolt"):
            submolt = str(p["submolt"])
        digest_lines.append(
            f"{i}. [{score}↑ {comments}c] s/{submolt}: {title}\n   {content}"
        )

    feed_digest = "\n".join(digest_lines)

    prompt = f"""You are an analyst identifying trending discourse topics on a social platform for AI agents.

Below are the top 25 posts from the current hot feed. Analyze them and identify 3-5 ACTIVE DISCOURSE TOPICS — recurring themes, debates, or questions that appear across MULTIPLE posts.

For each topic, provide:
- topic_label: A short (3-6 word) label
- summary: 1-2 sentence description of what's being discussed
- heat_score: 1-10 (how actively debated / how many posts touch on this)
- fresh_angles: 2-3 angles that haven't been fully explored yet
- post_indices: which posts from the feed relate to this topic (by number)

FEED:
{feed_digest}

Respond in JSON format ONLY — no markdown fences, no explanation:
[
  {{
    "topic_label": "...",
    "summary": "...",
    "heat_score": 8,
    "fresh_angles": ["...", "..."],
    "post_indices": [1, 4, 7]
  }}
]"""

    raw = _call_zo_ask(prompt)
    if not raw:
        print("detect_hot_discourse: LLM returned no output", file=sys.stderr)
        return []

    # Parse JSON from response (strip markdown fences + trailing garbage)
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"```[\s\S]*$", "", text)  # remove ``` and everything after it
    # Extract JSON array even if there's trailing text
    text = text.strip()
    if text.startswith("["):
        match = re.search(r"(\[[\s\S]*\])", text)
        if match:
            text = match.group(1)

    try:
        topics = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"detect_hot_discourse: JSON parse error: {e}", file=sys.stderr)
        print(f"  raw output: {text[:500]}", file=sys.stderr)
        return []

    if not isinstance(topics, list):
        print("detect_hot_discourse: LLM did not return a list", file=sys.stderr)
        return []

    now = datetime.now(timezone.utc)
    stale_after = (now + timedelta(hours=6)).isoformat()

    # Annotate each topic with metadata
    for t in topics:
        t["detected_at"] = now.isoformat()
        t["stale_after"] = stale_after
        # Generate a stable thread_id from the label
        label = (t.get("topic_label", "") or "").lower()
        t["thread_id"] = re.sub(r"[^a-z0-9]+", "-", label).strip("-")

    # Write state file for direct_poster to consume
    discourse_state = {
        "updated_at": now.isoformat(),
        "stale_after": stale_after,
        "topics": topics,
        "posts_analyzed": len(posts),
    }

    if not dry_run:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        with open(HOT_DISCOURSE_FILE, "w") as f:
            json.dump(discourse_state, f, indent=2)

        # Persist to DB via upsert_discourse
        try:
            from db_bridge import SocialDB
            with SocialDB() as db:
                for t in topics:
                    db.upsert_discourse(
                        thread_id=t["thread_id"],
                        topic=t.get("topic_label", ""),
                        related_ideas=t.get("fresh_angles", []),
                        post_ids=[str(idx) for idx in t.get("post_indices", [])],
                        participant_count=t.get("heat_score", 0),
                        notes=t.get("summary", ""),
                    )
        except Exception as e:
            print(f"detect_hot_discourse: DB write error: {e}", file=sys.stderr)

        log_action("discourse_detection", {
            "topics_found": len(topics),
            "labels": [t.get("topic_label", "") for t in topics],
        })

    print(f"detect_hot_discourse: identified {len(topics)} discourse topics", file=sys.stderr)
    for t in topics:
        print(f"  [{t.get('heat_score', '?')}] {t.get('topic_label', '?')}: {t.get('summary', '')[:80]}", file=sys.stderr)

    return topics


# Top-decile threshold — opportunities scoring above this trigger a text alert
ALERT_THRESHOLD = 6.0


def score_opportunity(post: dict, rapport_agents: set | None = None) -> dict:
    """Score an engagement opportunity based on the social constitution."""
    title = (post.get("title", "") or "").lower()
    content = (post.get("content", "") or "").lower()
    text = f"{title} {content}"

    # Check do-not-engage signals
    for signal in DO_NOT_ENGAGE_SIGNALS:
        if signal in text:
            return {
                "score": 0,
                "action": "skip",
                "reason": f"Do-not-engage signal: '{signal}'",
                "post_id": post.get("id"),
            }

    # Score engagement signals
    engage_score = sum(1 for s in ENGAGE_SIGNALS if s in text)
    comment_count = post.get("comment_count", 0) or 0
    post_score = post.get("score", 0) or 0

    # Boost for active discussions (good comment opportunity)
    discussion_boost = min(comment_count / 5, 2.0)

    # Boost for moderate-score posts (not too high = already crowded, not too low = dead)
    score_boost = 1.0 if 3 <= post_score <= 15 else 0.5

    # Rapport boost — if the author is someone we've engaged with before
    rapport_boost = 0.0
    author = post.get("author", {})
    if isinstance(author, dict):
        author_name = (author.get("name", "") or "").lower()
        author_id = author.get("id", "")
    else:
        author_name = str(author).lower()
        author_id = ""

    has_rapport = False
    if rapport_agents:
        if author_id in rapport_agents or author_name in rapport_agents:
            rapport_boost = 2.0
            has_rapport = True

    total = engage_score + discussion_boost + score_boost + rapport_boost

    if total >= 4:
        action = "comment"
        reason = f"Strong alignment (signal={engage_score}, discussion={comment_count}, score={post_score})"
    elif total >= 2:
        action = "consider"
        reason = f"Moderate alignment (signal={engage_score}, discussion={comment_count})"
    else:
        action = "skip"
        reason = f"Low alignment (signal={engage_score})"

    if has_rapport:
        reason += f" [RAPPORT: {author_name}]"

    result = {
        "score": round(total, 1),
        "action": action,
        "reason": reason,
        "post_id": post.get("id"),
        "title": post.get("title", "")[:80],
        "submolt": post.get("submolt", {}).get("name", "") if isinstance(post.get("submolt"), dict) else post.get("submolt", ""),
        "author": author_name,
        "has_rapport": has_rapport,
        "alert": total >= ALERT_THRESHOLD,
    }
    return result


def check_rate_limits(phase: str, today_actions: dict) -> dict:
    """Check if we can still post/comment given current rate limits."""
    limits = PHASE_LIMITS[phase]
    can_post = today_actions["posts"] < limits["max_posts_per_day"]
    can_comment = today_actions["comments"] < limits["max_comments_per_day"]

    # Check post cooldown
    post_cooldown_ok = True
    if today_actions["last_post_at"]:
        try:
            last = datetime.fromisoformat(today_actions["last_post_at"])
            minutes_since = (datetime.now(timezone.utc) - last).total_seconds() / 60
            post_cooldown_ok = minutes_since >= limits["post_cooldown_minutes"]
        except (ValueError, TypeError):
            pass

    return {
        "can_post": can_post and post_cooldown_ok,
        "can_comment": can_comment,
        "posts_remaining": limits["max_posts_per_day"] - today_actions["posts"],
        "comments_remaining": limits["max_comments_per_day"] - today_actions["comments"],
        "post_cooldown_ok": post_cooldown_ok,
        "phase": phase,
    }


def run_scan(phase: str, dry_run: bool = False, limit: int = 25) -> dict:
    """Run a single feed scan cycle."""
    today_actions = load_today_actions()
    rate_status = check_rate_limits(phase, today_actions)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "rate_status": rate_status,
        "opportunities": [],
        "alerts": [],
        "actions_taken": [],
    }

    # Load rapport agents for boosted scoring
    rapport_agents = _load_rapport_agents()

    # Try to fetch live feed
    posts = []
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_reader import get_feed
        posts = get_feed(sort="hot", limit=limit)
    except Exception as e:
        result["feed_error"] = str(e)
        print(f"Could not fetch feed: {e}", file=sys.stderr)

    # Score all posts for engagement opportunities
    for post in posts:
        opp = score_opportunity(post, rapport_agents=rapport_agents)
        if opp["action"] != "skip":
            post_text = f"{post.get('title', '')} {post.get('content', '')}"
            post_terms = _find_priority_mentions(post_text)
            mention_hit = _best_comment_mention(post.get("id")) if (post.get("comment_count", 0) or 0) > 0 else {"matched": False}

            if mention_hit.get("matched"):
                opp["score"] = round(float(opp.get("score", 0.0) or 0.0) + COMMENT_MENTION_BOOST, 1)
                opp["priority_mention"] = True
                opp["priority_reason"] = "comment references V/Zøde"
                opp["mention_terms"] = mention_hit.get("mention_terms", [])
                opp["comment_id"] = mention_hit.get("comment_id")
                opp["comment_excerpt"] = mention_hit.get("comment_excerpt", "")
                if mention_hit.get("comment_author"):
                    opp["author"] = mention_hit.get("comment_author")
                opp["reason"] = f"{opp['reason']} [PRIORITY_MENTION in comments]"
                opp["alert"] = True
            elif post_terms:
                opp["score"] = round(float(opp.get("score", 0.0) or 0.0) + POST_MENTION_BOOST, 1)
                opp["priority_mention"] = True
                opp["priority_reason"] = "post references V/Zøde"
                opp["mention_terms"] = sorted(set(post_terms))
                opp["reason"] = f"{opp['reason']} [PRIORITY_MENTION in post]"
                opp["alert"] = True
            else:
                opp["priority_mention"] = False

            result["opportunities"].append(opp)
            if opp.get("alert"):
                result["alerts"].append(opp)

    # Sort opportunities by score
    result["opportunities"].sort(key=lambda x: x["score"], reverse=True)

    # Report what we found
    comment_opps = [o for o in result["opportunities"] if o["action"] == "comment"]
    consider_opps = [o for o in result["opportunities"] if o["action"] == "consider"]

    result["summary"] = {
        "posts_scanned": len(posts),
        "strong_opportunities": len(comment_opps),
        "moderate_opportunities": len(consider_opps),
        "alerts": len(result["alerts"]),
        "can_post": rate_status["can_post"],
        "can_comment": rate_status["can_comment"],
    }

    if not dry_run:
        log_action("read", {
            "posts_scanned": len(posts),
            "opportunities_found": len(result["opportunities"]),
            "alerts": len(result["alerts"]),
        })

    # Hot discourse detection — runs on every scan when we have enough posts
    if len(posts) >= 5:
        try:
            discourse_topics = detect_hot_discourse(posts, dry_run=dry_run)
            result["hot_discourse"] = [t.get("topic_label", "") for t in discourse_topics]
            result["summary"]["discourse_topics_detected"] = len(discourse_topics)
        except Exception as e:
            print(f"discourse detection error (non-fatal): {e}", file=sys.stderr)
            result["hot_discourse"] = []
            result["summary"]["discourse_topics_detected"] = 0

    return result


# --- CLI ---

def format_alert_text(alerts: list[dict]) -> str:
    """Format alert opportunities into a concise SMS-friendly text."""
    count = len(alerts)
    lines = [f"Zøde — {count} high-value engagement opp{'s' if count > 1 else ''}:"]
    for a in alerts:  # No cap — send all
        rapport_tag = " [rapport]" if a.get("has_rapport") else ""
        lines.append(f"• ({a['score']}) {a['title'][:60]}{rapport_tag}")
        lines.append(f"  s/{a.get('submolt', '?')} by {a.get('author', '?')}")
    lines.append("")
    lines.append("Review and draft responses when ready.")
    return "\n".join(lines)


def cmd_run(args):
    """Run a feed scan cycle."""
    phase = args.phase or detect_phase()
    result = run_scan(phase, dry_run=args.dry_run, limit=args.limit)

    print(f"FEED SCANNER — {result['timestamp']}")
    print(f"Phase: {result['phase']}")
    print("=" * 50)

    s = result["summary"]
    print(f"Posts scanned: {s['posts_scanned']}")
    print(f"Strong opportunities: {s['strong_opportunities']}")
    print(f"Moderate opportunities: {s['moderate_opportunities']}")
    print(f"Alerts (top-decile): {s['alerts']}")
    print(f"Can post: {s['can_post']} | Can comment: {s['can_comment']}")

    rs = result["rate_status"]
    print(f"Posts remaining today: {rs['posts_remaining']}")
    print(f"Comments remaining today: {rs['comments_remaining']}")

    if result.get("hot_discourse"):
        print()
        print("HOT DISCOURSE TOPICS:")
        print("-" * 50)
        for label in result["hot_discourse"]:
            print(f"  - {label}")

    if result["alerts"]:
        print()
        print("🚨 ALERT — TOP-DECILE OPPORTUNITIES:")
        print("-" * 50)
        for i, opp in enumerate(result["alerts"], 1):
            rapport_tag = " [RAPPORT]" if opp.get("has_rapport") else ""
            print(f"  {i}. (score: {opp['score']}) {opp['title']}{rapport_tag}")
            print(f"     → {opp['reason']}")
            print(f"     by {opp.get('author', '?')} in s/{opp.get('submolt', '?')}")
            print()
        # Output the alert text that the Zo agent should send
        print("ALERT_TEXT_FOR_SMS:")
        print(format_alert_text(result["alerts"]))

    if result["opportunities"]:
        print()
        print("TOP ENGAGEMENT OPPORTUNITIES:")
        print("-" * 50)
        for i, opp in enumerate(result["opportunities"][:5], 1):
            rapport_tag = " [RAPPORT]" if opp.get("has_rapport") else ""
            print(f"  {i}. [{opp['action'].upper()}] (score: {opp['score']}){rapport_tag}")
            print(f"     {opp['title']}")
            print(f"     → {opp['reason']}")
            if opp.get("submolt"):
                print(f"     Submolt: {opp['submolt']}")
            print()

    if result.get("feed_error"):
        print(f"\nFeed error: {result['feed_error']}")

    if args.json:
        print(json.dumps(result, indent=2))


def cmd_status(args):
    """Show feed scanner status."""
    phase = detect_phase()
    today_actions = load_today_actions()
    rate_status = check_rate_limits(phase, today_actions)

    print(f"FEED SCANNER STATUS")
    print("=" * 50)
    print(f"Current phase: {phase}")
    print(f"Focus: {PHASE_LIMITS[phase]['focus']}")
    print()
    print(f"Today's actions:")
    print(f"  Posts: {today_actions['posts']}/{PHASE_LIMITS[phase]['max_posts_per_day']}")
    print(f"  Comments: {today_actions['comments']}/{PHASE_LIMITS[phase]['max_comments_per_day']}")
    print(f"  Reads: {today_actions['reads']}")
    print()
    print(f"Can post: {rate_status['can_post']}")
    print(f"Can comment: {rate_status['can_comment']}")
    print(f"Post cooldown OK: {rate_status['post_cooldown_ok']}")

    if args.json:
        print(json.dumps({
            "phase": phase,
            "today_actions": today_actions,
            "rate_status": rate_status,
        }, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Feed Scanner — Moltbook engagement opportunity finder for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    r = sub.add_parser("run", help="Run a feed scan cycle")
    r.add_argument("--phase", choices=["first_24h", "establishment", "steady"],
                    help="Override auto-detected phase")
    r.add_argument("--limit", type=int, default=25, help="Posts to scan")
    r.add_argument("--dry-run", action="store_true", help="Don't log actions")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    s = sub.add_parser("status", help="Show feed scanner status")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {"run": cmd_run, "status": cmd_status}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
