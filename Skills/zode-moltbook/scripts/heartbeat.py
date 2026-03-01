#!/usr/bin/env python3
"""
Heartbeat — Metrics pulse for Zøde's social intelligence.

Lightweight, runs every hour. Updates social_intelligence.db with:
- Our post performance (upvotes, comments)
- Our comment performance (upvotes, replies)
- Agent karma changes for tracked agents
- Concept adoption detection (scans feed for our coined terms)

Usage: python3 heartbeat.py run [--dry-run] [--json]
       python3 heartbeat.py status
       python3 heartbeat.py --help
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = _SCRIPT_DIR.parent / "state"
HEARTBEAT_LOG = STATE_DIR / "heartbeat_log.jsonl"

# Our known IDs
ZODE_AGENT_ID = "69b73ef4-909b-44c5-8d6e-ac1153c2b346"
FLAGSHIP_POST_ID = "f1345be8-b0cf-4932-8f44-ae3ce7071ff6"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(entry: dict):
    """Append an entry to the heartbeat log."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = _now_iso()
    entry["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _get_db():
    """Get a SocialDB instance."""
    sys.path.insert(0, str(_SCRIPT_DIR))
    from db_bridge import SocialDB
    return SocialDB()


def _get_reader():
    """Import moltbook_reader."""
    sys.path.insert(0, str(_SCRIPT_DIR))
    import moltbook_reader
    return moltbook_reader


def update_post_metrics(db, reader, dry_run: bool = False) -> dict:
    """Fetch current metrics for all our tracked posts and update DB."""
    results = {"posts_updated": 0, "deltas": []}

    # Get our posts from DB
    rows = db.db.execute("SELECT post_id, upvotes, comment_count FROM our_posts").fetchall()

    for post_id, old_upvotes, old_comments in rows:
        try:
            post_data = reader.get_post(post_id)
            if not post_data:
                continue

            new_upvotes = post_data.get("score", post_data.get("upvotes", 0)) or 0
            new_downvotes = post_data.get("downvotes", 0) or 0
            new_comments = post_data.get("comment_count", 0) or 0

            delta = {
                "post_id": post_id,
                "upvotes": {"old": old_upvotes, "new": new_upvotes, "delta": new_upvotes - (old_upvotes or 0)},
                "comments": {"old": old_comments, "new": new_comments, "delta": new_comments - (old_comments or 0)},
            }
            results["deltas"].append(delta)

            if not dry_run:
                db.update_our_post_metrics(post_id, new_upvotes, new_downvotes, new_comments)
                results["posts_updated"] += 1

        except Exception as e:
            results.setdefault("errors", []).append({"post_id": post_id, "error": str(e)})

    return results


def update_comment_metrics(db, reader, dry_run: bool = False) -> dict:
    """Fetch current metrics for all our tracked comments and update DB."""
    results = {"comments_updated": 0, "deltas": []}

    rows = db.db.execute(
        "SELECT comment_id, post_id, upvotes, replies_received FROM our_comments"
    ).fetchall()

    for comment_id, post_id, old_upvotes, old_replies in rows:
        try:
            # Fetch all comments on the parent post to find ours
            comments = reader.get_comments(post_id)
            if not comments:
                continue

            our_comment = None
            reply_count = 0
            for c in comments:
                cid = c.get("id", "")
                if cid == comment_id:
                    our_comment = c
                # Count replies to our comment
                if c.get("parent_id") == comment_id:
                    reply_count += 1

            if not our_comment:
                continue

            new_upvotes = our_comment.get("score", our_comment.get("upvotes", 0)) or 0

            delta = {
                "comment_id": comment_id,
                "upvotes": {"old": old_upvotes or 0, "new": new_upvotes, "delta": new_upvotes - (old_upvotes or 0)},
                "replies": {"old": old_replies or 0, "new": reply_count, "delta": reply_count - (old_replies or 0)},
            }
            results["deltas"].append(delta)

            if not dry_run:
                db.db.execute(
                    "UPDATE our_comments SET upvotes = ?, replies_received = ? WHERE comment_id = ?",
                    [new_upvotes, reply_count, comment_id]
                )
                results["comments_updated"] += 1

        except Exception as e:
            results.setdefault("errors", []).append({"comment_id": comment_id, "error": str(e)})

    return results


def update_agent_metrics(db, reader, dry_run: bool = False) -> dict:
    """Update karma for tracked agents by checking their profiles."""
    results = {"agents_updated": 0, "deltas": []}

    agents = db.list_agents(limit=50)
    for agent in agents:
        aid = agent["agent_id"]
        name = agent["display_name"]
        if aid == ZODE_AGENT_ID:
            continue  # Skip self
        if not name:
            continue

        try:
            profile = reader.get_profile(name)
            if not profile:
                continue

            new_karma = profile.get("karma", 0) or 0
            new_followers = profile.get("followers", 0) or 0
            old_karma = agent.get("karma", 0) or 0

            if new_karma != old_karma or new_followers != (agent.get("followers", 0) or 0):
                delta = {
                    "agent": name,
                    "karma": {"old": old_karma, "new": new_karma, "delta": new_karma - old_karma},
                    "followers": {"old": agent.get("followers", 0) or 0, "new": new_followers},
                }
                results["deltas"].append(delta)

                if not dry_run:
                    db.upsert_agent(
                        agent_id=aid,
                        display_name=name,
                        karma=new_karma,
                        followers=new_followers,
                    )
                    results["agents_updated"] += 1

        except Exception as e:
            results.setdefault("errors", []).append({"agent": name, "error": str(e)})

    return results


def detect_concept_adoption(db, reader, dry_run: bool = False) -> dict:
    """Scan recent feed for usage of our coined concepts by other agents."""
    results = {"adoptions_found": 0, "details": []}

    # Get our concept names
    concepts = db.list_concepts()
    if not concepts:
        return results

    concept_names = [c["name"].lower() for c in concepts]

    # Scan the hot feed
    try:
        posts = reader.get_feed(sort="new", limit=30)
    except Exception as e:
        results["feed_error"] = str(e)
        return results

    for post in posts:
        author = post.get("author", {})
        if isinstance(author, dict):
            author_name = author.get("name", "")
            author_id = author.get("id", "")
        else:
            author_name = str(author)
            author_id = ""

        # Skip our own posts
        if author_id == ZODE_AGENT_ID or author_name == "Zøde":
            continue

        text = f"{post.get('title', '')} {post.get('content', '')}".lower()

        for concept_name in concept_names:
            # Use word boundary matching to avoid false positives
            pattern = r'\b' + re.escape(concept_name) + r'\b'
            if re.search(pattern, text):
                detail = {
                    "concept": concept_name,
                    "agent": author_name,
                    "agent_id": author_id,
                    "post_id": post.get("id", ""),
                    "context": post.get("title", "")[:100],
                }
                results["details"].append(detail)

                if not dry_run and author_id:
                    try:
                        db.record_concept_adoption(
                            agent_id=author_id,
                            concept_name=concept_name,
                            context=f"Used in post: {post.get('title', '')[:80]}",
                            adoption_type="used_in_post",
                        )
                        db.increment_concept_reference(concept_name)
                        results["adoptions_found"] += 1

                        # Also record as an epistemic position — using our concept = implicit agreement
                        try:
                            # Use concept name as idea_id (normalized)
                            idea_id = concept_name.replace(" ", "_")
                            db.upsert_idea(
                                idea_id=idea_id,
                                name=concept_name,
                                category="zode_concept",
                                introduced_by=ZODE_AGENT_ID,
                                zode_stance="advocates",
                            )
                            db.record_position(
                                agent_id=author_id,
                                idea_id=idea_id,
                                stance="adopts",
                                evidence=f"Used term in: {post.get('title', '')[:60]}",
                                context_post_id=post.get("id", ""),
                            )
                        except Exception:
                            pass  # Epistemic tracking is best-effort
                    except Exception:
                        pass  # Duplicate or DB error — not critical

    return results


def run_heartbeat(dry_run: bool = False) -> dict:
    """Run the full heartbeat metrics cycle."""
    result = {
        "timestamp": _now_iso(),
        "type": "heartbeat",
        "dry_run": dry_run,
    }

    try:
        db = _get_db()
        reader = _get_reader()
    except Exception as e:
        result["error"] = f"Failed to initialize: {e}"
        return result

    try:
        # 1. Update our post metrics
        result["posts"] = update_post_metrics(db, reader, dry_run)

        # 2. Update our comment metrics
        result["comments"] = update_comment_metrics(db, reader, dry_run)

        # 3. Update agent karma (skip if too many API calls — do every 3rd hour)
        hour = datetime.now(timezone.utc).hour
        if hour % 3 == 0:
            result["agents"] = update_agent_metrics(db, reader, dry_run)
            # Also refresh hot discourse detection on the 3rd-hour cycle
            try:
                from feed_scanner import detect_hot_discourse
                posts = reader.get_feed(sort="hot", limit=25)
                discourse_topics = detect_hot_discourse(posts, dry_run=dry_run)
                result["discourse_refresh"] = {
                    "topics_found": len(discourse_topics),
                    "labels": [t.get("topic_label", "") for t in discourse_topics],
                }
            except Exception as e:
                result["discourse_refresh"] = {"error": str(e)}
        else:
            result["agents"] = {"skipped": True, "reason": "Runs every 3rd hour to conserve API calls"}

        # 4. Detect concept adoption
        result["concept_adoption"] = detect_concept_adoption(db, reader, dry_run)

        # 5. Get summary for logging
        summary = db.engagement_summary()
        result["db_summary"] = summary

    except Exception as e:
        result["error"] = str(e)
    finally:
        try:
            db.close()
        except Exception:
            pass

    # Log the heartbeat
    if not dry_run:
        _log({
            "action_type": "heartbeat",
            "posts_updated": result.get("posts", {}).get("posts_updated", 0),
            "comments_updated": result.get("comments", {}).get("comments_updated", 0),
            "agents_updated": result.get("agents", {}).get("agents_updated", 0),
            "adoptions_found": result.get("concept_adoption", {}).get("adoptions_found", 0),
        })
        # Keep advertiser-facing cache snapshots coordinated with heartbeat cadence.
        try:
            from advertiser_snapshot import refresh_advertiser_snapshot
            result["advertiser_snapshot"] = refresh_advertiser_snapshot(force=False)
        except Exception as e:
            result["advertiser_snapshot"] = {"ok": False, "error": str(e)}

    return result


def get_status() -> dict:
    """Get heartbeat status — last run, log stats."""
    status = {
        "last_run": None,
        "runs_today": 0,
        "total_runs": 0,
    }

    if not HEARTBEAT_LOG.exists():
        return status

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(HEARTBEAT_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("action_type") == "heartbeat":
                    status["total_runs"] += 1
                    status["last_run"] = entry.get("timestamp")
                    if entry.get("date") == today:
                        status["runs_today"] += 1
            except json.JSONDecodeError:
                continue

    return status


# --- CLI ---

def cmd_run(args):
    result = run_heartbeat(dry_run=args.dry_run)

    print(f"HEARTBEAT — {result['timestamp']}")
    print("=" * 50)

    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return

    # Posts
    posts = result.get("posts", {})
    print(f"Posts updated: {posts.get('posts_updated', 0)}")
    for d in posts.get("deltas", []):
        up = d["upvotes"]
        cm = d["comments"]
        print(f"  {d['post_id'][:12]}... upvotes: {up['old']}→{up['new']} ({up['delta']:+d}), comments: {cm['old']}→{cm['new']} ({cm['delta']:+d})")

    # Comments
    comments = result.get("comments", {})
    print(f"Comments updated: {comments.get('comments_updated', 0)}")
    for d in comments.get("deltas", []):
        up = d["upvotes"]
        rp = d["replies"]
        print(f"  {d['comment_id'][:12]}... upvotes: {up['old']}→{up['new']} ({up['delta']:+d}), replies: {rp['old']}→{rp['new']} ({rp['delta']:+d})")

    # Agents
    agents = result.get("agents", {})
    if agents.get("skipped"):
        print(f"Agents: {agents['reason']}")
    else:
        print(f"Agents updated: {agents.get('agents_updated', 0)}")
        for d in agents.get("deltas", []):
            k = d["karma"]
            print(f"  {d['agent']}: karma {k['old']}→{k['new']} ({k['delta']:+d})")

    # Concept adoption
    adoption = result.get("concept_adoption", {})
    print(f"Concept adoptions detected: {adoption.get('adoptions_found', 0)}")
    for d in adoption.get("details", []):
        print(f"  '{d['concept']}' used by {d['agent']} in: {d['context'][:60]}")

    # DB summary
    summary = result.get("db_summary", {})
    if summary:
        print(f"\nDB Totals: {summary.get('posts', 0)} posts, {summary.get('comments', 0)} comments, "
              f"{summary.get('agents_engaged', 0)} agents engaged, "
              f"{summary.get('concepts_adopted', 0)}/{summary.get('concepts_coined', 0)} concepts adopted")

    if args.json:
        print(json.dumps(result, indent=2))


def cmd_status(args):
    status = get_status()
    print("HEARTBEAT STATUS")
    print("=" * 50)
    print(f"Last run: {status['last_run'] or 'never'}")
    print(f"Runs today: {status['runs_today']}")
    print(f"Total runs: {status['total_runs']}")

    if args.json:
        print(json.dumps(status, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Heartbeat — Metrics pulse for Zøde's social intelligence"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    r = sub.add_parser("run", help="Run heartbeat cycle")
    r.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    s = sub.add_parser("status", help="Show heartbeat status")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {"run": cmd_run, "status": cmd_status}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
