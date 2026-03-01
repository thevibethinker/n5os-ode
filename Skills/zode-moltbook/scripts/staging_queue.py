#!/usr/bin/env python3
"""
Staging Queue — Manages post lifecycle: staged → approved → published → rejected.

All Zøde posts go through the staging queue before publication.
The publish step runs content_filter.py for final safety check.

Usage: python3 staging_queue.py add --submolt general --title "..." --content "..."
       python3 staging_queue.py list [--status staged|approved|published|rejected]
       python3 staging_queue.py approve <id>
       python3 staging_queue.py reject <id> [--reason "..."]
       python3 staging_queue.py publish <id> [--dry-run]
       python3 staging_queue.py stats
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STAGING_DIR = Path(__file__).resolve().parent.parent / "state" / "staging"


def _slug(text: str) -> str:
    """Create a filesystem-safe slug from text."""
    s = re.sub(r'[^a-z0-9]+', '-', text.lower().strip())
    return s[:40].strip('-')


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_id(submolt: str, title: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{submolt}_{_slug(title)}"


def add_post(
    submolt: str,
    title: str,
    content: str,
    rubric_scores: dict | None = None,
    post_type: str = "post",
    experiment_meta: dict | None = None,
) -> dict:
    """Add a new post to the staging queue."""
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    post_id = _gen_id(submolt, title)
    filename = f"{post_id}.json"

    post = {
        "id": post_id,
        "type": post_type,
        "submolt": submolt,
        "title": title,
        "content": content,
        "status": "staged",
        "rubric_scores": rubric_scores or {},
        "created_at": _now_iso(),
        "approved_at": None,
        "published_at": None,
        "rejected_at": None,
        "rejection_reason": None,
        "moltbook_id": None,
        "filter_result": None,
        "experiment_meta": experiment_meta or {},
    }

    filepath = STAGING_DIR / filename
    with open(filepath, "w") as f:
        json.dump(post, f, indent=2)

    return post


def add_comment(
    post_id: str,
    content: str,
    parent_comment_id: str | None = None,
    rubric_scores: dict | None = None,
    experiment_meta: dict | None = None,
) -> dict:
    """Add a comment to the staging queue."""
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    comment_id = f"{ts}_comment_{post_id[:20]}"
    filename = f"{comment_id}.json"

    comment = {
        "id": comment_id,
        "type": "comment",
        "target_post_id": post_id,
        "parent_comment_id": parent_comment_id,
        "content": content,
        "status": "staged",
        "rubric_scores": rubric_scores or {},
        "created_at": _now_iso(),
        "approved_at": None,
        "published_at": None,
        "rejected_at": None,
        "rejection_reason": None,
        "moltbook_id": None,
        "filter_result": None,
        "experiment_meta": experiment_meta or {},
    }

    filepath = STAGING_DIR / filename
    with open(filepath, "w") as f:
        json.dump(comment, f, indent=2)

    return comment


def list_posts(status: str | None = None) -> list[dict]:
    """List posts in the staging queue, optionally filtered by status."""
    if not STAGING_DIR.exists():
        return []

    posts = []
    for f in sorted(STAGING_DIR.glob("*.json")):
        with open(f) as fh:
            post = json.load(fh)
            if status is None or post.get("status") == status:
                posts.append(post)

    return posts


def _update_post(post_id: str, updates: dict) -> dict | None:
    """Update a post's fields by ID."""
    for f in STAGING_DIR.glob("*.json"):
        with open(f) as fh:
            post = json.load(fh)
        if post.get("id") == post_id:
            post.update(updates)
            with open(f, "w") as fh:
                json.dump(post, fh, indent=2)
            return post
    return None


def approve(post_id: str) -> dict | None:
    return _update_post(post_id, {"status": "approved", "approved_at": _now_iso()})


def reject(post_id: str, reason: str = "") -> dict | None:
    return _update_post(post_id, {
        "status": "rejected",
        "rejected_at": _now_iso(),
        "rejection_reason": reason,
    })


def publish(post_id: str, dry_run: bool = False) -> dict | None:
    """Publish a post — runs content filter first, then posts via moltbook_poster."""
    # Find the post
    post = None
    for f in STAGING_DIR.glob("*.json"):
        with open(f) as fh:
            p = json.load(fh)
        if p.get("id") == post_id:
            post = p
            post_file = f
            break

    if not post:
        print(f"Post {post_id} not found", file=sys.stderr)
        return None

    if post["status"] not in ("staged", "approved"):
        print(f"Post {post_id} has status '{post['status']}' — must be 'staged' or 'approved'", file=sys.stderr)
        return None

    # Run content filter
    sys.path.insert(0, str(Path(__file__).parent))
    from content_filter import check_text

    text_to_check = f"{post.get('title', '')} {post.get('content', '')}"
    filter_result = check_text(text_to_check)
    post["filter_result"] = filter_result

    if not filter_result["passed"]:
        post["status"] = "rejected"
        post["rejected_at"] = _now_iso()
        post["rejection_reason"] = f"Content filter failed: {[i['reason'] for i in filter_result['issues']]}"
        with open(post_file, "w") as fh:
            json.dump(post, fh, indent=2)
        print(f"REJECTED by content filter: {post['rejection_reason']}", file=sys.stderr)
        return post

    if dry_run:
        print(f"[DRY RUN] Content filter: PASS")
        print(f"[DRY RUN] Would publish: {post['type']} to s/{post.get('submolt', '?')}")
        print(f"[DRY RUN] Title: {post.get('title', 'N/A')}")
        print(f"[DRY RUN] Content: {post['content'][:200]}...")
        return post

    # Actually publish via moltbook_poster
    sys.path.insert(0, "/home/workspace/Skills/zode-moltbook/scripts")

    if post["type"] == "post":
        from moltbook_poster import create_post
        result = create_post(
            post["submolt"],
            post["title"],
            post["content"],
            experiment_meta=post.get("experiment_meta", {}),
        )
    elif post["type"] == "comment":
        from moltbook_poster import create_comment
        result = create_comment(
            post["target_post_id"],
            post["content"],
            parent_id=post.get("parent_comment_id"),
            experiment_meta=post.get("experiment_meta", {}),
        )
    else:
        print(f"Unknown post type: {post['type']}", file=sys.stderr)
        return None

    if result:
        post["status"] = "published"
        post["published_at"] = _now_iso()
        if post["type"] == "post":
            post["moltbook_id"] = result.get("id") or (result.get("post") or {}).get("id")
        else:
            post["moltbook_id"] = result.get("id") or (result.get("comment") or {}).get("id")
        with open(post_file, "w") as fh:
            json.dump(post, fh, indent=2)
        print(f"Published: {post['id']} → Moltbook ID: {post.get('moltbook_id')}")
    else:
        print(f"Failed to publish: {post['id']}", file=sys.stderr)

    return post


def get_stats() -> dict:
    """Get staging queue statistics."""
    posts = list_posts()
    stats = {
        "total": len(posts),
        "staged": sum(1 for p in posts if p["status"] == "staged"),
        "approved": sum(1 for p in posts if p["status"] == "approved"),
        "published": sum(1 for p in posts if p["status"] == "published"),
        "rejected": sum(1 for p in posts if p["status"] == "rejected"),
        "types": {
            "post": sum(1 for p in posts if p.get("type") == "post"),
            "comment": sum(1 for p in posts if p.get("type") == "comment"),
        },
    }
    return stats


# --- CLI ---

def cmd_add(args):
    experiment_meta = {
        "experiment_id": args.experiment_id,
        "hypothesis_id": args.hypothesis_id,
        "objective_family": args.objective_family,
        "variant_id": args.variant_id,
        "attempt_no": args.attempt_no,
        "decision_state": args.decision_state,
        "decision_reason": args.decision_reason,
        "narrative_cohesion_score": args.narrative_cohesion_score,
        "opportunity_score": args.opportunity_score,
        "quality_gate_score": args.quality_gate_score,
        "rate_limit_headroom": args.rate_limit_headroom,
        "risk_score": args.risk_score,
    }
    experiment_meta = {k: v for k, v in experiment_meta.items() if v is not None}
    if args.comment:
        post = add_comment(
            args.post_id,
            args.content,
            parent_comment_id=args.reply_to,
            experiment_meta=experiment_meta,
        )
    else:
        post = add_post(
            args.submolt,
            args.title,
            args.content,
            experiment_meta=experiment_meta,
        )
    print(f"Added to staging: {post['id']}")
    print(json.dumps(post, indent=2))


def cmd_list(args):
    posts = list_posts(status=args.status)
    if args.compact:
        for p in posts:
            status = p["status"].upper()
            ptype = p.get("type", "post")
            title = p.get("title", p.get("content", "")[:60])
            submolt = p.get("submolt", "?")
            if isinstance(submolt, dict):
                submolt = submolt.get("name", "?")
            print(f"  [{status}] ({ptype}) s/{submolt}: {title} [{p['id']}]")
    else:
        print(json.dumps(posts, indent=2))
    print(f"\nTotal: {len(posts)}")


def cmd_approve(args):
    result = approve(args.id)
    if result:
        print(f"Approved: {args.id}")
    else:
        print(f"Not found: {args.id}", file=sys.stderr)


def cmd_reject(args):
    result = reject(args.id, reason=args.reason or "")
    if result:
        print(f"Rejected: {args.id}")
    else:
        print(f"Not found: {args.id}", file=sys.stderr)


def cmd_publish(args):
    result = publish(args.id, dry_run=args.dry_run)
    if result:
        print(json.dumps(result, indent=2))


def cmd_stats(args):
    stats = get_stats()
    print(f"Staging Queue Stats:")
    print(f"  Total: {stats['total']}")
    print(f"  Staged: {stats['staged']}")
    print(f"  Approved: {stats['approved']}")
    print(f"  Published: {stats['published']}")
    print(f"  Rejected: {stats['rejected']}")
    print(f"  Posts: {stats['types']['post']}, Comments: {stats['types']['comment']}")


def main():
    parser = argparse.ArgumentParser(
        description="Staging Queue — Manage Zøde post lifecycle"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    a = sub.add_parser("add", help="Add a post/comment to staging")
    a.add_argument("--submolt", help="Submolt name (for posts)")
    a.add_argument("--title", help="Post title (for posts)")
    a.add_argument("--content", required=True, help="Content text")
    a.add_argument("--comment", action="store_true", help="Add as comment instead of post")
    a.add_argument("--post-id", help="Target post ID (for comments)")
    a.add_argument("--reply-to", help="Parent comment ID (for threaded replies)")
    a.add_argument("--experiment-id", help="Experiment ID for tracking")
    a.add_argument("--hypothesis-id", help="Hypothesis ID linked to this action")
    a.add_argument("--objective-family", help="Objective family (FOLLOW_CONVERT, etc.)")
    a.add_argument("--variant-id", help="Variant label (control/A/B/...)")
    a.add_argument("--attempt-no", type=int, help="Attempt index for the experiment")
    a.add_argument("--decision-state", help="Current decision state (incubating/active/etc.)")
    a.add_argument("--decision-reason", help="Decision reason string")
    a.add_argument("--narrative-cohesion-score", type=float, help="0-1 cohesion score")
    a.add_argument("--opportunity-score", type=float, help="0-100 opportunity score")
    a.add_argument("--quality-gate-score", type=float, help="0-10 quality gate score")
    a.add_argument("--rate-limit-headroom", type=float, help="0-1 remaining rate-limit headroom")
    a.add_argument("--risk-score", type=float, help="0-1 low-quality risk score")

    l = sub.add_parser("list", help="List staged posts")
    l.add_argument("--status", choices=["staged", "approved", "published", "rejected"])
    l.add_argument("--compact", action="store_true", help="One-line per post")

    ap = sub.add_parser("approve", help="Approve a staged post")
    ap.add_argument("id", help="Post ID")

    r = sub.add_parser("reject", help="Reject a staged post")
    r.add_argument("id", help="Post ID")
    r.add_argument("--reason", help="Rejection reason")

    p = sub.add_parser("publish", help="Publish a post to Moltbook")
    p.add_argument("id", help="Post ID")
    p.add_argument("--dry-run", action="store_true", help="Preview without publishing")

    sub.add_parser("stats", help="Show queue statistics")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "add": cmd_add,
        "list": cmd_list,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "publish": cmd_publish,
        "stats": cmd_stats,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
