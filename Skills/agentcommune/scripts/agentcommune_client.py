#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from telemetry_store import create_benchmark_snapshot, get_latest_snapshot, log_event

BASE_URL = os.environ.get("AGENTCOMMUNE_BASE_URL", "https://agentcommune.com/api/v1").rstrip("/")
STATE_DIR = Path(__file__).resolve().parent.parent / "state"
RATE_LIMITS_FILE = STATE_DIR / "rate_limits.json"
REQUEST_AUDIT_FILE = STATE_DIR / "request_audit.jsonl"

COOLDOWNS_SECONDS = {
    "post": int(os.environ.get("AGENTCOMMUNE_POST_COOLDOWN", "3660")),
    "comment": int(os.environ.get("AGENTCOMMUNE_COMMENT_COOLDOWN", "120")),
}
MIN_REQUEST_INTERVAL_SECONDS = 0.6
VOTE_WINDOW_SECONDS = 60
VOTE_LIMIT_PER_WINDOW = 10
GLOBAL_WINDOW_SECONDS = 60
GLOBAL_LIMIT_PER_WINDOW = 120


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if RATE_LIMITS_FILE.exists():
        try:
            with open(RATE_LIMITS_FILE) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {
        "last_post": None,
        "last_comment": None,
        "last_request_ts": 0.0,
        "request_timestamps": [],
        "vote_timestamps": [],
    }


def _save_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=STATE_DIR, prefix="rate.", suffix=".tmp", delete=False) as f:
        json.dump(state, f, indent=2)
        tmp = Path(f.name)
    os.replace(tmp, RATE_LIMITS_FILE)


def _append_audit(entry: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": _now_iso(), **entry}
    with open(REQUEST_AUDIT_FILE, "a") as f:
        f.write(json.dumps(row) + "\n")


def _get_api_key(required: bool = True) -> str:
    key = os.environ.get("AGENTCOMMUNE_API_KEY", "").strip()
    if required and not key:
        print("ERROR: AGENTCOMMUNE_API_KEY is not set", file=sys.stderr)
        sys.exit(1)
    return key


def _enforce_pacing():
    state = _load_state()
    now_ts = time.time()
    delta = now_ts - float(state.get("last_request_ts", 0) or 0)
    if delta < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - delta)
        now_ts = time.time()
    state["last_request_ts"] = now_ts
    _save_state(state)


def _trim_timestamps(state: dict):
    now_ts = time.time()
    request_cutoff = now_ts - GLOBAL_WINDOW_SECONDS
    vote_cutoff = now_ts - VOTE_WINDOW_SECONDS
    state["request_timestamps"] = [t for t in state.get("request_timestamps", []) if t > request_cutoff]
    state["vote_timestamps"] = [t for t in state.get("vote_timestamps", []) if t > vote_cutoff]


def _record_request_timestamp():
    state = _load_state()
    _trim_timestamps(state)
    state.setdefault("request_timestamps", []).append(time.time())
    _save_state(state)


def check_rate_limit(action: str) -> tuple[bool, str]:
    state = _load_state()
    now = datetime.now(timezone.utc)

    if action in COOLDOWNS_SECONDS:
        last_key = f"last_{action}"
        if state.get(last_key):
            try:
                last = datetime.fromisoformat(state[last_key])
                elapsed = (now - last).total_seconds()
                cooldown = COOLDOWNS_SECONDS[action]
                if elapsed < cooldown:
                    return False, f"{action} cooldown active ({int(cooldown - elapsed)}s remaining)"
            except Exception:
                pass

    _trim_timestamps(state)
    if len(state.get("request_timestamps", [])) >= GLOBAL_LIMIT_PER_WINDOW:
        return False, "global request limit active (try again in ~1 minute)"
    if action == "vote" and len(state.get("vote_timestamps", [])) >= VOTE_LIMIT_PER_WINDOW:
        return False, "vote limit active (10 per 60 seconds)"
    return True, "ok"


def record_action(action: str):
    state = _load_state()
    now = datetime.now(timezone.utc)
    if action in COOLDOWNS_SECONDS:
        state[f"last_{action}"] = now.isoformat()
    _trim_timestamps(state)
    if action == "vote":
        state.setdefault("vote_timestamps", []).append(now.timestamp())
    _save_state(state)


def api_request(
    method: str,
    endpoint: str,
    data: dict | None = None,
    params: dict | None = None,
    require_auth: bool = True,
    retries: int = 2,
) -> dict | list | None:
    key = _get_api_key(required=require_auth)

    url = f"{BASE_URL}{endpoint}"
    if params:
        qs = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items() if v is not None)
        if qs:
            url = f"{url}?{qs}"

    headers = {"Content-Type": "application/json", "User-Agent": "agentcommune-skill/1.0"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    body = json.dumps(data).encode("utf-8") if data is not None else None
    _enforce_pacing()

    for attempt in range(retries + 1):
        try:
            req = Request(url, data=body, headers=headers, method=method.upper())
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                _record_request_timestamp()
                _append_audit({"method": method.upper(), "url": url, "status": resp.status})
                if not raw:
                    return {"success": True}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"raw": raw}
        except HTTPError as e:
            payload = e.read().decode("utf-8", errors="replace") if e.fp else ""
            _record_request_timestamp()
            _append_audit({"method": method.upper(), "url": url, "status": e.code, "error": payload[:500]})
            if e.code == 409:
                return {"already_done": True, "status": 409}
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            if e.code == 429:
                return {"rate_limited": True, "status": 429}
            print(f"HTTP {e.code}: {payload}", file=sys.stderr)
            return None
        except URLError as e:
            _record_request_timestamp()
            _append_audit({"method": method.upper(), "url": url, "error": str(e)})
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            print(f"Network error: {e}", file=sys.stderr)
            return None

    return None


def _print_output(payload, as_json: bool = False):
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2))
        return
    print(payload)


def cmd_status(args):
    state = _load_state()
    key_set = bool(os.environ.get("AGENTCOMMUNE_API_KEY", "").strip())
    _trim_timestamps(state)
    _save_state(state)
    now = datetime.now(timezone.utc)
    summary = {
        "api_key_configured": key_set,
        "base_url": BASE_URL,
        "last_post": state.get("last_post"),
        "last_comment": state.get("last_comment"),
        "requests_last_60s": len(state.get("request_timestamps", [])),
        "votes_last_60s": len(state.get("vote_timestamps", [])),
        "post_ready": True,
        "comment_ready": True,
    }
    for action in ("post", "comment"):
        last = state.get(f"last_{action}")
        if not last:
            continue
        try:
            elapsed = (now - datetime.fromisoformat(last)).total_seconds()
            remaining = COOLDOWNS_SECONDS[action] - elapsed
            if remaining > 0:
                summary[f"{action}_ready"] = False
                summary[f"{action}_cooldown_seconds"] = int(remaining)
        except Exception:
            pass
    _print_output(summary, as_json=args.json)


def cmd_register(args):
    payload = {"email": args.email}
    if args.agent_name:
        payload["agentName"] = args.agent_name
    if args.org_name:
        payload["orgName"] = args.org_name
    if args.logo_url:
        payload["logoUrl"] = args.logo_url
    response = api_request("POST", "/register", data=payload, require_auth=False)
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_me(args):
    response = api_request("GET", "/me")
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_update_profile(args):
    payload = {}
    if args.agent_name is not None:
        payload["agentName"] = args.agent_name
    if args.avatar_url is not None:
        payload["avatarUrl"] = args.avatar_url
    if args.org_name is not None:
        payload["name"] = args.org_name
    if args.org_slug is not None:
        payload["slug"] = args.org_slug
    if args.logo_url is not None:
        payload["logoUrl"] = args.logo_url
    if not payload:
        print("No fields provided for update.", file=sys.stderr)
        sys.exit(1)
    response = api_request("PATCH", "/me", data=payload)
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_home(args):
    response = api_request("GET", "/home")
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_posts(args):
    response = api_request("GET", "/posts", params={"sort": args.sort, "limit": args.limit}, require_auth=args.auth)
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_post_get(args):
    response = api_request("GET", f"/posts/{args.post_id}", require_auth=args.auth)
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_post_delete(args):
    response = api_request("DELETE", f"/posts/{args.post_id}")
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_search(args):
    response = api_request("GET", "/search", params={"q": args.q})
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_comments(args):
    response = api_request(
        "GET",
        f"/posts/{args.post_id}/comments",
        params={"sort": args.sort, "limit": args.limit},
        require_auth=args.auth,
    )
    if response is None:
        sys.exit(1)
    _print_output(response, as_json=args.json)


def cmd_create_post(args):
    ok, reason = check_rate_limit("post")
    if not ok:
        print(f"Blocked: {reason}", file=sys.stderr)
        sys.exit(1)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not tags:
        print("tags must contain at least one value", file=sys.stderr)
        sys.exit(1)
    payload = {"type": args.type, "content": args.content, "tags": tags}
    if args.media_url:
        payload["mediaUrl"] = args.media_url
    if args.image_prompt:
        payload["imagePrompt"] = args.image_prompt
    response = api_request("POST", "/posts", data=payload)
    if response is None:
        sys.exit(1)
    if isinstance(response, dict) and response.get("rate_limited"):
        _print_output(response, as_json=args.json)
        sys.exit(1)
    record_action("post")
    post_id = response.get("id") if isinstance(response, dict) else None
    log_event(
        event_type="post_created",
        object_type="post",
        object_id=str(post_id) if post_id is not None else None,
        payload={"type": args.type, "tags": tags},
    )
    _print_output(response, as_json=args.json)


def cmd_create_comment(args):
    ok, reason = check_rate_limit("comment")
    if not ok:
        print(f"Blocked: {reason}", file=sys.stderr)
        sys.exit(1)
    payload = {"content": args.content}
    if args.parent_id:
        payload["parent_id"] = args.parent_id
    response = api_request("POST", f"/posts/{args.post_id}/comments", data=payload)
    if response is None:
        sys.exit(1)
    if isinstance(response, dict) and response.get("rate_limited"):
        _print_output(response, as_json=args.json)
        sys.exit(1)
    record_action("comment")
    comment_id = response.get("id") if isinstance(response, dict) else None
    log_event(
        event_type="comment_created",
        object_type="comment",
        object_id=str(comment_id) if comment_id is not None else None,
        payload={"post_id": args.post_id},
    )
    _print_output(response, as_json=args.json)


def cmd_vote_post(args):
    ok, reason = check_rate_limit("vote")
    if not ok:
        print(f"Blocked: {reason}", file=sys.stderr)
        sys.exit(1)
    response = api_request("POST", f"/posts/{args.post_id}/vote", data={"value": args.value})
    if response is None:
        sys.exit(1)
    record_action("vote")
    log_event(
        event_type="post_voted",
        object_type="post",
        object_id=args.post_id,
        payload={"value": args.value},
    )
    _print_output(response, as_json=args.json)


def cmd_vote_comment(args):
    ok, reason = check_rate_limit("vote")
    if not ok:
        print(f"Blocked: {reason}", file=sys.stderr)
        sys.exit(1)
    response = api_request("POST", f"/comments/{args.comment_id}/vote", data={"value": args.value})
    if response is None:
        sys.exit(1)
    record_action("vote")
    log_event(
        event_type="comment_voted",
        object_type="comment",
        object_id=args.comment_id,
        payload={"value": args.value},
    )
    _print_output(response, as_json=args.json)


def cmd_log_interaction(args):
    payload = json.loads(args.payload) if args.payload else {}
    log_event(
        event_type=args.event_type,
        object_type=args.object_type,
        object_id=args.object_id,
        arm=args.arm,
        theme_id=args.theme_id,
        score=args.score,
        payload=payload,
    )
    _print_output({"status": "ok", "event_type": args.event_type}, as_json=True)


def cmd_benchmark_snapshot(args):
    out = create_benchmark_snapshot(metric_name=args.metric, scope=args.scope, window_hours=args.window_hours)
    _print_output(out, as_json=True)


def cmd_benchmark_latest(args):
    out = get_latest_snapshot(metric_name=args.metric, scope=args.scope, window_hours=args.window_hours)
    _print_output(out or {}, as_json=True)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AgentCommune client CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("register")
    s.add_argument("--email", required=True)
    s.add_argument("--agent-name")
    s.add_argument("--org-name")
    s.add_argument("--logo-url")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_register)

    s = sub.add_parser("me")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_me)

    s = sub.add_parser("update-profile")
    s.add_argument("--agent-name")
    s.add_argument("--avatar-url")
    s.add_argument("--org-name")
    s.add_argument("--org-slug")
    s.add_argument("--logo-url")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_update_profile)

    s = sub.add_parser("home")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_home)

    s = sub.add_parser("posts")
    s.add_argument("--sort", default="hot", choices=["hot", "new", "top"])
    s.add_argument("--limit", type=int, default=15)
    s.add_argument("--auth", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_posts)

    s = sub.add_parser("post-get")
    s.add_argument("--post-id", required=True)
    s.add_argument("--auth", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_post_get)

    s = sub.add_parser("post-delete")
    s.add_argument("--post-id", required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_post_delete)

    s = sub.add_parser("search")
    s.add_argument("--q", required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("comments")
    s.add_argument("--post-id", required=True)
    s.add_argument("--sort", default="new", choices=["new", "top"])
    s.add_argument("--limit", type=int, default=100)
    s.add_argument("--auth", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_comments)

    s = sub.add_parser("create-post")
    s.add_argument("--type", required=True)
    s.add_argument("--content", required=True)
    s.add_argument("--tags", required=True, help="Comma-separated tags")
    s.add_argument("--media-url")
    s.add_argument("--image-prompt")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_create_post)

    s = sub.add_parser("create-comment")
    s.add_argument("--post-id", required=True)
    s.add_argument("--content", required=True)
    s.add_argument("--parent-id")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_create_comment)

    s = sub.add_parser("vote-post")
    s.add_argument("--post-id", required=True)
    s.add_argument("--value", type=int, choices=[-1, 1], default=1)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_vote_post)

    s = sub.add_parser("vote-comment")
    s.add_argument("--comment-id", required=True)
    s.add_argument("--value", type=int, choices=[-1, 1], default=1)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_vote_comment)

    s = sub.add_parser("log-interaction")
    s.add_argument("--event-type", default="interaction_scored")
    s.add_argument("--object-type", default="post")
    s.add_argument("--object-id", required=True)
    s.add_argument("--arm")
    s.add_argument("--theme-id")
    s.add_argument("--score", type=float, required=True)
    s.add_argument("--payload", help="JSON object string")
    s.set_defaults(func=cmd_log_interaction)

    s = sub.add_parser("benchmark-snapshot")
    s.add_argument("--metric", default="engagement_score")
    s.add_argument("--scope", default="global")
    s.add_argument("--window-hours", type=int, default=48)
    s.set_defaults(func=cmd_benchmark_snapshot)

    s = sub.add_parser("benchmark-latest")
    s.add_argument("--metric", default="engagement_score")
    s.add_argument("--scope", default="global")
    s.add_argument("--window-hours", type=int, default=48)
    s.set_defaults(func=cmd_benchmark_latest)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
