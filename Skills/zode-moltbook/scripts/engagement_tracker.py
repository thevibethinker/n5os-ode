#!/usr/bin/env python3
"""
Engagement Tracker — Pull live Moltbook metrics for Zøde.

Tracks post and comment performance using direct API reads and writes
daily snapshots to state/analytics/engagement-YYYY-MM-DD.json.

Also computes derived metrics on each ad hoc refresh:
- median time-to-first-engagement
- engagement velocity (first 6h/24h)
- rapport ROI by author
- submolt yield
- content-type yield
- duplicate/verification failure rate
- opportunity backlog age
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = WORKSPACE / "analytics"
STAGING_DIR = WORKSPACE / "staging"
MEMORY_DIR = WORKSPACE / "memory"

FIRST_ENGAGEMENT_FILE = ANALYTICS_DIR / "first-engagement.json"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"

MAX_CANDIDATE_POSTS = 40
COMMENTS_SCAN_LIMIT = 300
BACKLOG_ALERT_THRESHOLD = 6.0


def _parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(txt)
    except ValueError:
        return None


def _hours_between(start: datetime | None, end: datetime | None) -> float:
    if not start or not end:
        return 0.0
    return max((end - start).total_seconds() / 3600.0, 0.0)


def _safe_post_payload(post_payload: dict | None) -> dict:
    if not isinstance(post_payload, dict):
        return {}
    if isinstance(post_payload.get("post"), dict):
        return post_payload["post"]
    return post_payload


def _load_json(path: Path, default):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_api_modules():
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from moltbook_client import api_request
        from moltbook_reader import get_feed, get_personalized_feed, get_post
        return api_request, get_feed, get_personalized_feed, get_post
    except ImportError:
        return None, None, None, None


def _load_rapport_authors() -> set[str]:
    path = MEMORY_DIR / "agents.jsonl"
    rapport = set()
    if not path.exists():
        return rapport
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rel = (row.get("zode_relationship") or "").lower()
            if rel in {"engaged", "replied_to_us", "ally"}:
                name = (row.get("name") or "").strip().lower()
                if name:
                    rapport.add(name)
    return rapport


def collect_from_staging() -> tuple[list[dict], list[dict]]:
    posts: list[dict] = []
    comments: list[dict] = []
    if not STAGING_DIR.exists():
        return posts, comments

    for f in sorted(STAGING_DIR.glob("*.json")):
        with open(f) as fh:
            item = json.load(fh)
        if item.get("status") != "published" or not item.get("moltbook_id"):
            continue
        base = {
            "staging_id": item.get("id"),
            "moltbook_id": item.get("moltbook_id"),
            "title": item.get("title", ""),
            "submolt": item.get("submolt", {}).get("name", "") if isinstance(item.get("submolt"), dict) else item.get("submolt", ""),
            "published_at": item.get("published_at", ""),
            "source": "staging",
        }
        if item.get("type") == "comment":
            comments.append(base)
        else:
            posts.append(base)
    return posts, comments


def _candidate_posts(get_feed, get_personalized_feed, staged_post_ids: set[str]) -> list[dict]:
    merged: dict[str, dict] = {}
    for pid in staged_post_ids:
        merged[pid] = {"id": pid, "source": "staging"}

    feeds = [
        ("hot", get_feed(sort="hot", limit=50)),
        ("new", get_feed(sort="new", limit=50)),
        ("personalized", get_personalized_feed(sort="new", limit=50)),
    ]
    for source, posts in feeds:
        for p in posts or []:
            pid = p.get("id")
            if not pid:
                continue
            submolt = p.get("submolt", {})
            author = p.get("author", {})
            if not isinstance(submolt, dict):
                submolt = {"name": str(submolt)}
            if not isinstance(author, dict):
                author = {"name": str(author)}
            merged[pid] = {
                "id": pid,
                "title": p.get("title", ""),
                "created_at": p.get("created_at", ""),
                "source": source,
                "submolt": submolt.get("name", ""),
                "author_name": (author.get("name") or "").lower(),
                "score": p.get("score", 0),
                "comment_count": p.get("comment_count", 0),
            }
    return list(merged.values())[:MAX_CANDIDATE_POSTS]


def _classify_comment_type(content: str) -> str:
    txt = (content or "").strip().lower()
    if not txt:
        return "other"
    if "?" in txt:
        return "question"
    contrarian_markers = ["i disagree", "counterpoint", "push back", "however", "but ", "not sure"]
    if any(m in txt for m in contrarian_markers):
        return "contrarian"
    framework_markers = ["framework", "pattern", "loop", "principle", "model", "state assumption", "test", "update"]
    if any(m in txt for m in framework_markers):
        return "framework"
    story_markers = ["i ", "my ", "when ", "today", "yesterday", "human"]
    if any(m in txt for m in story_markers):
        return "story"
    return "other"


def _update_first_engagement_records(snapshot: dict, all_comments: list[dict]) -> dict:
    records = _load_json(FIRST_ENGAGEMENT_FILE, {"posts": {}, "comments": {}})
    now_iso = datetime.now(timezone.utc).isoformat()

    for p in snapshot.get("posts", []):
        pid = p.get("moltbook_id")
        interactions = p.get("upvotes", 0) + p.get("comment_count", 0)
        if pid and interactions > 0 and pid not in records["posts"]:
            records["posts"][pid] = now_iso

    for c in all_comments:
        cid = c.get("moltbook_id")
        interactions = c.get("upvotes", 0) + c.get("reply_count", 0)
        if cid and interactions > 0 and cid not in records["comments"]:
            records["comments"][cid] = now_iso

    _save_json(FIRST_ENGAGEMENT_FILE, records)
    return records


def _compute_velocity(snapshot: dict, all_comments: list[dict], window_hours: float) -> dict:
    now = datetime.now(timezone.utc)
    post_hours = 0.0
    post_upvotes = 0
    post_comments = 0
    for p in snapshot.get("posts", []):
        created = _parse_ts(p.get("created_at", ""))
        if not created:
            continue
        h = min(_hours_between(created, now), window_hours)
        if h <= 0:
            continue
        post_hours += h
        post_upvotes += p.get("upvotes", 0)
        post_comments += p.get("comment_count", 0)

    comment_hours = 0.0
    comment_upvotes = 0
    comment_replies = 0
    for c in all_comments:
        created = _parse_ts(c.get("created_at", ""))
        if not created:
            continue
        h = min(_hours_between(created, now), window_hours)
        if h <= 0:
            continue
        comment_hours += h
        comment_upvotes += c.get("upvotes", 0)
        comment_replies += c.get("reply_count", 0)

    return {
        "post_upvotes_per_hour": round(post_upvotes / post_hours, 4) if post_hours else 0.0,
        "post_comments_per_hour": round(post_comments / post_hours, 4) if post_hours else 0.0,
        "comment_upvotes_per_hour": round(comment_upvotes / comment_hours, 4) if comment_hours else 0.0,
        "comment_replies_per_hour": round(comment_replies / comment_hours, 4) if comment_hours else 0.0,
    }


def _compute_rapport_roi(all_comments: list[dict], rapport_authors: set[str]) -> dict:
    stats = {
        "rapport": {"comments": 0, "interactions": 0},
        "non_rapport": {"comments": 0, "interactions": 0},
    }
    by_author: dict[str, dict] = {}
    for c in all_comments:
        author = (c.get("post_author") or "").lower()
        interactions = c.get("upvotes", 0) + c.get("reply_count", 0)
        bucket = "rapport" if author in rapport_authors else "non_rapport"
        stats[bucket]["comments"] += 1
        stats[bucket]["interactions"] += interactions
        if author:
            row = by_author.setdefault(author, {"comments": 0, "interactions": 0, "rapport": author in rapport_authors})
            row["comments"] += 1
            row["interactions"] += interactions

    for key in ("rapport", "non_rapport"):
        c = stats[key]["comments"]
        i = stats[key]["interactions"]
        stats[key]["interactions_per_comment"] = round(i / c, 4) if c else 0.0

    top_authors = sorted(
        [
            {
                "author": name,
                "comments": row["comments"],
                "interactions": row["interactions"],
                "interactions_per_comment": round(row["interactions"] / row["comments"], 4) if row["comments"] else 0.0,
                "rapport": row["rapport"],
            }
            for name, row in by_author.items()
        ],
        key=lambda x: (x["interactions_per_comment"], x["interactions"]),
        reverse=True,
    )[:10]

    return {
        "rapport_comments": stats["rapport"]["comments"],
        "rapport_interactions_per_comment": stats["rapport"]["interactions_per_comment"],
        "non_rapport_comments": stats["non_rapport"]["comments"],
        "non_rapport_interactions_per_comment": stats["non_rapport"]["interactions_per_comment"],
        "delta": round(stats["rapport"]["interactions_per_comment"] - stats["non_rapport"]["interactions_per_comment"], 4),
        "top_authors": top_authors,
    }


def _compute_submolt_yield(all_comments: list[dict]) -> list[dict]:
    by_submolt: dict[str, dict] = {}
    for c in all_comments:
        submolt = c.get("post_submolt", "") or "unknown"
        interactions = c.get("upvotes", 0) + c.get("reply_count", 0)
        row = by_submolt.setdefault(submolt, {"comments": 0, "interactions": 0})
        row["comments"] += 1
        row["interactions"] += interactions
    rows = []
    for name, row in by_submolt.items():
        rows.append({
            "submolt": name,
            "comments": row["comments"],
            "interactions": row["interactions"],
            "interactions_per_comment": round(row["interactions"] / row["comments"], 4) if row["comments"] else 0.0,
        })
    rows.sort(key=lambda x: (x["interactions_per_comment"], x["interactions"]), reverse=True)
    return rows


def _compute_content_type_yield(all_comments: list[dict]) -> list[dict]:
    buckets: dict[str, dict] = {}
    for c in all_comments:
        ctype = _classify_comment_type(c.get("content", ""))
        interactions = c.get("upvotes", 0) + c.get("reply_count", 0)
        row = buckets.setdefault(ctype, {"comments": 0, "interactions": 0})
        row["comments"] += 1
        row["interactions"] += interactions
    rows = []
    for ctype, row in buckets.items():
        rows.append({
            "content_type": ctype,
            "comments": row["comments"],
            "interactions": row["interactions"],
            "interactions_per_comment": round(row["interactions"] / row["comments"], 4) if row["comments"] else 0.0,
        })
    rows.sort(key=lambda x: (x["interactions_per_comment"], x["interactions"]), reverse=True)
    return rows


def _compute_posting_pipeline_quality(now: datetime) -> dict:
    if not POSTING_EVENTS_FILE.exists():
        return {
            "window_days": 7,
            "attempts": 0,
            "verification_required": 0,
            "verification_failures": 0,
            "verification_failure_rate": 0.0,
            "duplicate_flags": 0,
            "duplicate_rate": 0.0,
        }
    cutoff = now - timedelta(days=7)
    attempts = 0
    verification_required = 0
    verification_failures = 0
    duplicate_flags = 0

    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = _parse_ts(row.get("timestamp", ""))
            if ts and ts < cutoff:
                continue
            if row.get("event") != "publish_attempt":
                continue
            attempts += 1
            if row.get("verification_required"):
                verification_required += 1
                if not row.get("verification_success"):
                    verification_failures += 1
            if row.get("duplicate_flag"):
                duplicate_flags += 1

    return {
        "window_days": 7,
        "attempts": attempts,
        "verification_required": verification_required,
        "verification_failures": verification_failures,
        "verification_failure_rate": round(verification_failures / verification_required, 4) if verification_required else 0.0,
        "duplicate_flags": duplicate_flags,
        "duplicate_rate": round(duplicate_flags / attempts, 4) if attempts else 0.0,
    }


def _load_published_event_rows() -> list[dict]:
    rows: list[dict] = []
    if not POSTING_EVENTS_FILE.exists():
        return rows
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "publish_attempt" or not row.get("published"):
                continue
            cid = row.get("content_id")
            if not cid:
                continue
            rows.append(
                {
                    "type": row.get("type", ""),
                    "content_id": cid,
                    "target_id": row.get("target_id"),
                    "timestamp": row.get("timestamp", ""),
                    "experiment_id": row.get("experiment_id"),
                }
            )
    return rows


def _build_live_truth(snapshot: dict, event_rows: list[dict]) -> dict:
    live_posts = {p.get("moltbook_id") for p in snapshot.get("posts", []) if p.get("moltbook_id")}
    live_comments = {
        c.get("moltbook_id")
        for c in (snapshot.get("comments", []) + snapshot.get("discovered_comments", []))
        if c.get("moltbook_id")
    }

    published_post_ids = {r["content_id"] for r in event_rows if r.get("type") == "post"}
    published_comment_ids = {r["content_id"] for r in event_rows if r.get("type") == "comment"}

    event_only_live_posts = sorted(pid for pid in live_posts if pid not in published_post_ids)
    event_only_live_comments = sorted(cid for cid in live_comments if cid not in published_comment_ids)
    published_not_live_posts = sorted(pid for pid in published_post_ids if pid not in live_posts)
    published_not_live_comments = sorted(cid for cid in published_comment_ids if cid not in live_comments)

    return {
        "source_of_truth": "live_visible_now",
        "as_of": snapshot.get("generated_at"),
        "counts": {
            "posts_live_visible": len(live_posts),
            "comments_live_visible": len(live_comments),
            "followers_live": snapshot.get("agent", {}).get("followers", 0),
            "karma_live": snapshot.get("agent", {}).get("karma", 0),
        },
        "reconciliation": {
            "published_event_posts": len(published_post_ids),
            "published_event_comments": len(published_comment_ids),
            "event_only_live_posts": event_only_live_posts,
            "event_only_live_comments": event_only_live_comments,
            "published_not_live_posts": published_not_live_posts,
            "published_not_live_comments": published_not_live_comments,
            "drift_flags": {
                "post_count_mismatch": len(live_posts) != len(published_post_ids),
                "comment_count_mismatch": len(live_comments) != len(published_comment_ids),
                "published_not_live_exists": bool(published_not_live_posts or published_not_live_comments),
            },
        },
    }


def _compute_backlog_age(api_request, get_feed, all_comments: list[dict]) -> dict:
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from feed_scanner import score_opportunity
    except ImportError:
        return {"alerts_considered": 0, "untouched_alerts": 0, "median_age_hours": 0.0, "oldest_age_hours": 0.0}

    my_commented_post_ids = {c.get("post_id") for c in all_comments if c.get("post_id")}
    posts = get_feed(sort="hot", limit=50) or []
    alerts = []
    post_by_id = {}
    for p in posts:
        pid = p.get("id")
        if not pid:
            continue
        post_by_id[pid] = p
        opp = score_opportunity(p)
        if opp.get("score", 0) >= BACKLOG_ALERT_THRESHOLD and opp.get("action") == "comment":
            alerts.append(opp)

    now = datetime.now(timezone.utc)
    untouched = []
    for a in alerts:
        pid = a.get("post_id")
        if pid in my_commented_post_ids:
            continue
        post = post_by_id.get(pid, {})
        created = _parse_ts(post.get("created_at", ""))
        age_h = _hours_between(created, now)
        untouched.append({
            "post_id": pid,
            "title": a.get("title", ""),
            "score": a.get("score", 0),
            "age_hours": round(age_h, 2),
        })
    untouched.sort(key=lambda x: x["age_hours"], reverse=True)
    ages = [u["age_hours"] for u in untouched]
    return {
        "alerts_considered": len(alerts),
        "untouched_alerts": len(untouched),
        "median_age_hours": round(median(ages), 2) if ages else 0.0,
        "oldest_age_hours": round(max(ages), 2) if ages else 0.0,
        "top_untouched": untouched[:10],
    }


def _compute_derived_metrics(snapshot: dict, all_comments: list[dict], rapport_authors: set[str], api_request, get_feed) -> dict:
    now = datetime.now(timezone.utc)
    first_engagement = _update_first_engagement_records(snapshot, all_comments)

    post_delays = []
    for p in snapshot.get("posts", []):
        pid = p.get("moltbook_id")
        created = _parse_ts(p.get("created_at", ""))
        first = _parse_ts(first_engagement.get("posts", {}).get(pid, ""))
        if created and first:
            post_delays.append(_hours_between(created, first))

    comment_delays = []
    for c in all_comments:
        cid = c.get("moltbook_id")
        created = _parse_ts(c.get("created_at", ""))
        first = _parse_ts(first_engagement.get("comments", {}).get(cid, ""))
        if created and first:
            comment_delays.append(_hours_between(created, first))

    return {
        "median_time_to_first_engagement_hours": {
            "posts": round(median(post_delays), 2) if post_delays else 0.0,
            "comments": round(median(comment_delays), 2) if comment_delays else 0.0,
            "sample_sizes": {"posts": len(post_delays), "comments": len(comment_delays)},
        },
        "engagement_velocity_per_hour": {
            "first_6h": _compute_velocity(snapshot, all_comments, 6.0),
            "first_24h": _compute_velocity(snapshot, all_comments, 24.0),
        },
        "rapport_roi_by_author": _compute_rapport_roi(all_comments, rapport_authors),
        "submolt_yield": _compute_submolt_yield(all_comments),
        "content_type_yield": _compute_content_type_yield(all_comments),
        "posting_pipeline_quality": _compute_posting_pipeline_quality(now),
        "opportunity_backlog_age": _compute_backlog_age(api_request, get_feed, all_comments),
    }


def collect_live_snapshot(date: str) -> dict:
    api_request, get_feed, get_personalized_feed, get_post = _load_api_modules()
    staged_posts, staged_comments = collect_from_staging()

    snapshot = {
        "date": date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live_api",
        "agent": {},
        "posts": [],
        "discovered_posts": [],
        "comments": [],
        "discovered_comments": [],
        "unresolved_comments": [],
        "live_truth": {},
        "totals": {},
        "derived_metrics": {},
        "fetch_health": {
            "agent_fetch_ok": False,
            "post_fetch_ok": 0,
            "post_fetch_total": 0,
            "comment_threads_ok": 0,
            "comment_threads_total": 0,
            "degraded": False,
            "degraded_reasons": [],
        },
    }

    if not api_request:
        snapshot["mode"] = "staging_only"
        snapshot["posts"] = staged_posts
        snapshot["comments"] = staged_comments
        snapshot["error"] = "moltbook modules not available"
        return snapshot

    me = api_request("GET", "/agents/me") or {}
    agent = me.get("agent", me) if isinstance(me, dict) else {}
    agent_id = agent.get("id", "")
    snapshot["fetch_health"]["agent_fetch_ok"] = bool(agent_id)
    snapshot["agent"] = {
        "id": agent_id,
        "name": agent.get("name", ""),
        "karma": agent.get("karma", 0),
        "followers": agent.get("follower_count", 0),
        "following": agent.get("following_count", 0),
    }

    for p in staged_posts:
        pid = p.get("moltbook_id")
        live = _safe_post_payload(get_post(pid)) if pid else {}
        snapshot["fetch_health"]["post_fetch_total"] += 1
        if live:
            snapshot["fetch_health"]["post_fetch_ok"] += 1
        row = {
            **p,
            "score": live.get("score", 0),
            "upvotes": live.get("upvotes", 0),
            "downvotes": live.get("downvotes", 0),
            "comment_count": live.get("comment_count", 0),
            "title": live.get("title", p.get("title", "")),
            "created_at": live.get("created_at", p.get("published_at", "")),
            "live_status": "ok" if live else "missing",
        }
        snapshot["posts"].append(row)

    staged_post_ids = {p.get("moltbook_id", "") for p in staged_posts if p.get("moltbook_id")}
    published_event_rows = _load_published_event_rows()
    published_post_ids = {
        row["content_id"] for row in published_event_rows if row.get("type") == "post"
    }
    for pid in sorted(published_post_ids):
        if pid in staged_post_ids:
            continue
        live = _safe_post_payload(get_post(pid))
        snapshot["fetch_health"]["post_fetch_total"] += 1
        if not live:
            continue
        snapshot["fetch_health"]["post_fetch_ok"] += 1
        discovered_row = {
            "staging_id": None,
            "moltbook_id": pid,
            "title": live.get("title", ""),
            "submolt": live.get("submolt", {}).get("name", "") if isinstance(live.get("submolt"), dict) else "",
            "published_at": live.get("created_at", ""),
            "source": "event_log_scan",
            "score": live.get("score", 0),
            "upvotes": live.get("upvotes", 0),
            "downvotes": live.get("downvotes", 0),
            "comment_count": live.get("comment_count", 0),
            "created_at": live.get("created_at", ""),
            "live_status": "ok",
        }
        snapshot["discovered_posts"].append(discovered_row)
        snapshot["posts"].append(discovered_row)

    candidates = _candidate_posts(get_feed, get_personalized_feed, staged_post_ids)
    candidate_ids = {c.get("id") for c in candidates if c.get("id")}
    event_comment_target_post_ids = {
        row.get("target_id")
        for row in published_event_rows
        if row.get("type") == "comment" and row.get("target_id")
    }
    for pid in sorted(event_comment_target_post_ids):
        if not pid or pid in candidate_ids:
            continue
        post_payload = _safe_post_payload(get_post(pid))
        if not post_payload:
            continue
        submolt = post_payload.get("submolt", {})
        author = post_payload.get("author", {})
        if not isinstance(submolt, dict):
            submolt = {"name": str(submolt)}
        if not isinstance(author, dict):
            author = {"name": str(author)}
        candidates.append(
            {
                "id": pid,
                "title": post_payload.get("title", ""),
                "created_at": post_payload.get("created_at", ""),
                "source": "event_comment_target",
                "submolt": submolt.get("name", ""),
                "author_name": (author.get("name") or "").lower(),
                "score": post_payload.get("score", 0),
                "comment_count": post_payload.get("comment_count", 0),
            }
        )
        candidate_ids.add(pid)

    live_comment_by_id: dict[str, dict] = {}
    for cpost in candidates:
        pid = cpost.get("id")
        if not pid:
            continue
        snapshot["fetch_health"]["comment_threads_total"] += 1
        payload = api_request("GET", f"/posts/{pid}/comments", params={"sort": "new", "limit": COMMENTS_SCAN_LIMIT}) or {}
        if isinstance(payload, dict) and "comments" in payload:
            snapshot["fetch_health"]["comment_threads_ok"] += 1
        comments = payload.get("comments", []) if isinstance(payload, dict) else payload if isinstance(payload, list) else []
        for c in comments:
            if not isinstance(c, dict):
                continue
            if c.get("author_id") != agent_id:
                continue
            cid = c.get("id")
            if not cid:
                continue
            live_comment_by_id[cid] = {
                "moltbook_id": cid,
                "post_id": pid,
                "post_title": cpost.get("title", ""),
                "post_submolt": cpost.get("submolt", ""),
                "post_author": cpost.get("author_name", ""),
                "score": c.get("score", 0),
                "upvotes": c.get("upvotes", 0),
                "downvotes": c.get("downvotes", 0),
                "reply_count": c.get("reply_count", 0),
                "created_at": c.get("created_at", ""),
                "content": c.get("content", "")[:250],
                "source": "live_scan",
            }

    staged_comment_ids = {c.get("moltbook_id") for c in staged_comments if c.get("moltbook_id")}
    for c in staged_comments:
        cid = c.get("moltbook_id")
        if cid in live_comment_by_id:
            snapshot["comments"].append({**c, **live_comment_by_id[cid], "staging_match": True})
        else:
            snapshot["unresolved_comments"].append({**c, "staging_match": False, "live_status": "missing"})

    for cid, c in live_comment_by_id.items():
        if cid not in staged_comment_ids:
            snapshot["discovered_comments"].append(c)

    all_comments = snapshot["comments"] + snapshot["discovered_comments"]
    posts = snapshot["posts"]
    snapshot["totals"] = {
        "posts_tracked": len(posts),
        "comments_tracked": len(all_comments),
        "staged_comments_resolved": len(snapshot["comments"]),
        "staged_comments_unresolved": len(snapshot["unresolved_comments"]),
        "post_score": sum(p.get("score", 0) for p in posts),
        "post_upvotes": sum(p.get("upvotes", 0) for p in posts),
        "post_comment_count": sum(p.get("comment_count", 0) for p in posts),
        "comment_score": sum(c.get("score", 0) for c in all_comments),
        "comment_upvotes": sum(c.get("upvotes", 0) for c in all_comments),
        "comment_replies": sum(c.get("reply_count", 0) for c in all_comments),
        "comments_with_engagement": sum(1 for c in all_comments if c.get("upvotes", 0) > 0 or c.get("reply_count", 0) > 0),
        "overall_interactions": sum(p.get("upvotes", 0) + p.get("comment_count", 0) for p in posts) + sum(c.get("upvotes", 0) + c.get("reply_count", 0) for c in all_comments),
    }

    degraded_reasons = []
    if not snapshot["fetch_health"]["agent_fetch_ok"]:
        degraded_reasons.append("agent_fetch_failed")
    if staged_posts and snapshot["fetch_health"]["post_fetch_ok"] == 0:
        degraded_reasons.append("all_post_fetches_failed")
    if candidates and snapshot["fetch_health"]["comment_threads_ok"] == 0:
        degraded_reasons.append("all_comment_thread_fetches_failed")
    snapshot["fetch_health"]["degraded"] = len(degraded_reasons) > 0
    snapshot["fetch_health"]["degraded_reasons"] = degraded_reasons
    if snapshot["fetch_health"]["degraded"]:
        snapshot["mode"] = "live_api_degraded"

    snapshot["derived_metrics"] = _compute_derived_metrics(snapshot, all_comments, _load_rapport_authors(), api_request, get_feed)
    snapshot["live_truth"] = _build_live_truth(snapshot, published_event_rows)
    return snapshot


def save_metrics(date: str, snapshot: dict):
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = ANALYTICS_DIR / f"engagement-{date}.json"

    existing = {}
    if filepath.exists():
        try:
            with open(filepath) as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}

    degraded = snapshot.get("fetch_health", {}).get("degraded", False)
    existing_is_richer = bool(existing) and isinstance(existing, dict) and (
        existing.get("totals", {}).get("overall_interactions", 0) > snapshot.get("totals", {}).get("overall_interactions", 0)
        or existing.get("totals", {}).get("post_upvotes", 0) > snapshot.get("totals", {}).get("post_upvotes", 0)
        or existing.get("totals", {}).get("comments_tracked", 0) > snapshot.get("totals", {}).get("comments_tracked", 0)
    )

    if degraded and existing_is_richer:
        history = existing.setdefault("degraded_refresh_attempts", [])
        history.append({
            "attempted_at": snapshot.get("generated_at"),
            "reasons": snapshot.get("fetch_health", {}).get("degraded_reasons", []),
            "attempt_totals": snapshot.get("totals", {}),
        })
        with open(filepath, "w") as f:
            json.dump(existing, f, indent=2)
        return filepath, "preserved_existing_due_degraded_fetch"

    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=2)
    return filepath, "saved"


def load_metrics(date: str) -> dict | list:
    filepath = ANALYTICS_DIR / f"engagement-{date}.json"
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return {}


def compact_posting_events(max_age_days: int = 14):
    if not POSTING_EVENTS_FILE.exists():
        return 0, 0, POSTING_EVENTS_FILE

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)
    kept: list[str] = []
    dropped = 0
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                kept.append(raw)
                continue
            ts = _parse_ts(row.get("timestamp", ""))
            if ts and ts < cutoff:
                dropped += 1
                continue
            kept.append(raw)

    with open(POSTING_EVENTS_FILE, "w") as f:
        for line in kept:
            f.write(line + "\n")
    return len(kept), dropped, POSTING_EVENTS_FILE


def generate_report(days: int = 7) -> dict:
    now = datetime.now(timezone.utc)
    daily_stats = []

    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        metrics = load_metrics(date)
        if not metrics:
            continue
        if isinstance(metrics, list):
            total_score = sum(m.get("score", 0) for m in metrics)
            total_comments = sum(m.get("comment_count", 0) for m in metrics)
            daily_stats.append({
                "date": date,
                "posts_tracked": len(metrics),
                "comments_tracked": 0,
                "total_score": total_score,
                "total_comments": total_comments,
                "total_comment_upvotes": 0,
                "total_comment_replies": 0,
                "avg_score": round(total_score / max(len(metrics), 1), 1),
                "mode": "legacy",
            })
            continue

        totals = metrics.get("totals", {})
        posts_tracked = totals.get("posts_tracked", 0)
        comments_tracked = totals.get("comments_tracked", 0)
        total_score = totals.get("post_score", 0)
        total_comments = totals.get("post_comment_count", 0)
        daily_stats.append({
            "date": date,
            "posts_tracked": posts_tracked,
            "comments_tracked": comments_tracked,
            "total_score": total_score,
            "total_comments": total_comments,
            "total_comment_upvotes": totals.get("comment_upvotes", 0),
            "total_comment_replies": totals.get("comment_replies", 0),
            "avg_score": round(total_score / max(posts_tracked, 1), 1),
            "mode": metrics.get("mode", "live_api"),
        })

    return {
        "period": f"Last {days} days",
        "generated_at": now.isoformat(),
        "days_with_data": len(daily_stats),
        "daily": daily_stats,
        "totals": {
            "posts_tracked": sum(d["posts_tracked"] for d in daily_stats),
            "comments_tracked": sum(d["comments_tracked"] for d in daily_stats),
            "total_score": sum(d["total_score"] for d in daily_stats),
            "total_comments": sum(d["total_comments"] for d in daily_stats),
            "total_comment_upvotes": sum(d["total_comment_upvotes"] for d in daily_stats),
            "total_comment_replies": sum(d["total_comment_replies"] for d in daily_stats),
        } if daily_stats else {},
    }


def cmd_collect(args):
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = collect_live_snapshot(date)
    filepath, save_status = save_metrics(date, snapshot)
    if save_status == "preserved_existing_due_degraded_fetch":
        # Keep console output aligned with what is actually stored.
        snapshot = load_metrics(date) if isinstance(load_metrics(date), dict) else snapshot
    totals = snapshot.get("totals", {})
    print(f"Collected {snapshot.get('mode', 'unknown')} metrics → {filepath}")
    if snapshot.get("fetch_health", {}).get("degraded"):
        reasons = ", ".join(snapshot.get("fetch_health", {}).get("degraded_reasons", []))
        print(f"Warning: degraded API snapshot ({reasons})")
    if save_status == "preserved_existing_due_degraded_fetch":
        reasons = ", ".join(snapshot.get("degraded_refresh_attempts", [{}])[-1].get("reasons", []))
        print(f"Preserved existing snapshot due to degraded fetch ({reasons})")
    print(
        "Posts: {posts} | Comments: {comments} | Post upvotes: {post_up} | "
        "Post comments: {post_comments} | Comment upvotes: {comment_up} | Comment replies: {comment_rep}".format(
            posts=totals.get("posts_tracked", 0),
            comments=totals.get("comments_tracked", 0),
            post_up=totals.get("post_upvotes", 0),
            post_comments=totals.get("post_comment_count", 0),
            comment_up=totals.get("comment_upvotes", 0),
            comment_rep=totals.get("comment_replies", 0),
        )
    )
    derived = snapshot.get("derived_metrics", {})
    ttf = derived.get("median_time_to_first_engagement_hours", {})
    print(
        f"Median TTF engagement (hrs): posts={ttf.get('posts', 0)}, "
        f"comments={ttf.get('comments', 0)}"
    )
    backlog = derived.get("opportunity_backlog_age", {})
    print(
        f"Backlog: {backlog.get('untouched_alerts', 0)} untouched alerts, "
        f"median age {backlog.get('median_age_hours', 0)}h"
    )
    if snapshot.get("unresolved_comments"):
        print(f"Unresolved staged comments: {len(snapshot['unresolved_comments'])}")
    if snapshot.get("discovered_comments"):
        print(f"Live comments discovered outside staging: {len(snapshot['discovered_comments'])}")
    truth = snapshot.get("live_truth", {})
    counts = truth.get("counts", {})
    drift = truth.get("reconciliation", {}).get("drift_flags", {})
    if truth:
        print(
            "Live truth: posts={posts} comments={comments} followers={followers} karma={karma}".format(
                posts=counts.get("posts_live_visible", 0),
                comments=counts.get("comments_live_visible", 0),
                followers=counts.get("followers_live", 0),
                karma=counts.get("karma_live", 0),
            )
        )
        print(
            "Reconciliation flags: post_mismatch={p} comment_mismatch={c} published_not_live={x}".format(
                p=drift.get("post_count_mismatch", False),
                c=drift.get("comment_count_mismatch", False),
                x=drift.get("published_not_live_exists", False),
            )
        )
    if args.json:
        print(json.dumps(snapshot, indent=2))


def cmd_report(args):
    report = generate_report(days=args.days)
    print(f"ENGAGEMENT REPORT — {report['period']}")
    print("=" * 50)
    print(f"Days with data: {report['days_with_data']}")
    if report.get("totals"):
        t = report["totals"]
        print(f"Total posts tracked: {t['posts_tracked']}")
        print(f"Total comments tracked: {t['comments_tracked']}")
        print(f"Total score: {t['total_score']}")
        print(f"Total post comments: {t['total_comments']}")
        print(f"Total comment upvotes: {t['total_comment_upvotes']}")
        print(f"Total comment replies: {t['total_comment_replies']}")
    print()
    for day in report.get("daily", []):
        print(
            f"  {day['date']}: {day['posts_tracked']} posts, "
            f"{day['comments_tracked']} comments, avg score {day['avg_score']}, "
            f"{day['total_comments']} post comments, "
            f"{day['total_comment_upvotes']} comment upvotes, "
            f"{day['total_comment_replies']} comment replies ({day['mode']})"
        )
    if args.json:
        print(json.dumps(report, indent=2))


def cmd_compact_events(args):
    kept, dropped, path = compact_posting_events(max_age_days=args.max_age_days)
    print(f"Compacted posting events: kept={kept} dropped={dropped} file={path}")


def main():
    parser = argparse.ArgumentParser(
        description="Engagement Tracker — Monitor Zøde's Moltbook performance"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    c = sub.add_parser("collect", help="Collect current metrics")
    c.add_argument("--date", help="Date label (YYYY-MM-DD)")
    c.add_argument("--json", action="store_true", help="Output as JSON")

    r = sub.add_parser("report", help="Generate engagement report")
    r.add_argument("--days", type=int, default=7, help="Number of days to report on")
    r.add_argument("--json", action="store_true", help="Output as JSON")

    x = sub.add_parser("compact-events", help="Compact posting events by age")
    x.add_argument("--max-age-days", type=int, default=14, help="Drop entries older than this many days")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "collect": cmd_collect,
        "report": cmd_report,
        "compact-events": cmd_compact_events,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
