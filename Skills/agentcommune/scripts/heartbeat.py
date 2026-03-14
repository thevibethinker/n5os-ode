#!/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = SCRIPT_DIR.parent / "state"
STATE_FILE = STATE_DIR / "heartbeat_state.json"
LOG_FILE = STATE_DIR / "heartbeat_log.jsonl"
UPVOTE_DEDUPE_WINDOW_SECONDS = 24 * 60 * 60

sys.path.insert(0, str(SCRIPT_DIR))
from agentcommune_client import api_request, check_rate_limit, record_action  # noqa: E402
from telemetry_store import log_event  # noqa: E402


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {"last_agentcommune_check": None, "last_summary": None, "recent_upvotes": []}


def _save_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _append_log(entry: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({"timestamp": _now_iso(), **entry}) + "\n")


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _trim_recent_upvotes(state: dict):
    cutoff = _now_ts() - UPVOTE_DEDUPE_WINDOW_SECONDS
    rows = state.get("recent_upvotes", [])
    if not isinstance(rows, list):
        rows = []
    trimmed = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        ts = row.get("timestamp")
        post_id = row.get("post_id")
        if not post_id:
            continue
        if isinstance(ts, (int, float)) and ts >= cutoff:
            trimmed.append({"post_id": post_id, "timestamp": ts})
    state["recent_upvotes"] = trimmed


def _extract_feed_posts(payload: dict) -> list[dict]:
    recent = payload.get("recent_posts", [])
    if isinstance(recent, list):
        return [p for p in recent if isinstance(p, dict)]
    if isinstance(recent, dict):
        posts = recent.get("items") or recent.get("posts") or []
        if isinstance(posts, list):
            return [p for p in posts if isinstance(p, dict)]
    return []


def _extract_activity(payload: dict) -> list[dict]:
    activity = payload.get("activity_on_your_posts", [])
    if isinstance(activity, list):
        return [a for a in activity if isinstance(a, dict)]
    return []


def _extract_todos(payload: dict) -> list[str]:
    todos = payload.get("what_to_do_next", [])
    if isinstance(todos, list):
        return [str(t) for t in todos]
    return []


def _auto_upvote(posts: list[dict], limit: int, state: dict) -> tuple[int, list[str]]:
    if limit <= 0:
        return 0, []
    _trim_recent_upvotes(state)
    seen = {r["post_id"] for r in state.get("recent_upvotes", []) if isinstance(r, dict) and r.get("post_id")}
    voted = 0
    post_ids = []
    for post in posts:
        if voted >= limit:
            break
        post_id = post.get("id")
        if not post_id:
            continue
        if post_id in seen:
            continue
        ok, reason = check_rate_limit("vote")
        if not ok:
            post_ids.append(f"blocked:{reason}")
            break
        resp = api_request("POST", f"/posts/{post_id}/vote", data={"value": 1})
        if resp is None:
            post_ids.append(f"failed:{post_id}")
            continue
        record_action("vote")
        state.setdefault("recent_upvotes", []).append({"post_id": post_id, "timestamp": _now_ts()})
        seen.add(post_id)
        voted += 1
        post_ids.append(post_id)
    return voted, post_ids


def cmd_run(args):
    if not os.environ.get("AGENTCOMMUNE_API_KEY", "").strip():
        msg = "HEARTBEAT_NEEDS_SETUP - AGENTCOMMUNE_API_KEY is not configured."
        summary = {"checked_at": _now_iso(), "status": "needs_setup", "message": msg}
        state = _load_state()
        state["last_agentcommune_check"] = summary["checked_at"]
        state["last_summary"] = summary
        _save_state(state)
        _append_log({"event": "heartbeat_run", **summary})
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(msg)
        return

    payload = api_request("GET", "/home")
    if payload is None:
        print("HEARTBEAT_ERROR - Unable to fetch /home", file=sys.stderr)
        sys.exit(1)
    if not isinstance(payload, dict):
        print("HEARTBEAT_ERROR - Unexpected /home payload", file=sys.stderr)
        sys.exit(1)

    activity = _extract_activity(payload)
    posts = _extract_feed_posts(payload)
    todos = _extract_todos(payload)

    state = _load_state()
    auto_upvotes, upvoted_ids = _auto_upvote(posts, args.auto_upvote_limit, state)

    account = payload.get("your_account", {}) if isinstance(payload.get("your_account"), dict) else {}
    account_name = account.get("name") or account.get("agentName") or "unknown"
    likes = account.get("likes", 0)

    summary = {
        "checked_at": _now_iso(),
        "account_name": account_name,
        "likes": likes,
        "activity_items": len(activity),
        "recent_posts_seen": len(posts),
        "suggestions": todos[:5],
        "auto_upvotes": auto_upvotes,
        "upvoted_ids": upvoted_ids,
    }
    log_event(
        event_type="heartbeat_run",
        object_type="system",
        object_id="agentcommune",
        payload=summary,
    )

    _trim_recent_upvotes(state)
    state["last_agentcommune_check"] = summary["checked_at"]
    state["last_summary"] = summary
    _save_state(state)
    _append_log({"event": "heartbeat_run", **summary})

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    if len(activity) == 0 and auto_upvotes == 0:
        print("HEARTBEAT_OK - Checked Agent Commune, all good.")
        return

    text = (
        f"Checked Agent Commune - Activity on your posts: {len(activity)}, "
        f"upvoted: {auto_upvotes}, feed posts scanned: {len(posts)}."
    )
    print(text)


def cmd_status(args):
    state = _load_state()
    status = {
        "last_agentcommune_check": state.get("last_agentcommune_check"),
        "has_last_summary": bool(state.get("last_summary")),
        "log_file": str(LOG_FILE),
        "state_file": str(STATE_FILE),
    }
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(json.dumps(status, indent=2))


def build_parser():
    p = argparse.ArgumentParser(description="AgentCommune heartbeat")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("run")
    s.add_argument("--auto-upvote-limit", type=int, default=0)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
