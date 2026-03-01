#!/usr/bin/env python3
"""
Moltbook API Client — Base client with auth, rate limiting, retry logic.

Part of the Zøde Moltbook Integration Skill.
Usage: python3 moltbook_client.py --help
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_URL = "https://www.moltbook.com/api/v1"
STATE_DIR = Path(__file__).resolve().parent.parent / "state"
RATE_LIMITS_FILE = STATE_DIR / "rate_limits.json"
REGISTRATION_FILE = STATE_DIR / "registration.json"

# Rate limit windows (seconds)
RATE_LIMITS = {
    "post": {"normal": 1800, "new_agent": 7200},      # 30min / 2h
    "comment": {"normal": 20, "new_agent": 60},        # 20s / 60s
    "comment_daily": {"normal": 50, "new_agent": 20},  # per day
    "dm": {"new_agent_block": 86400},                  # 24h block
    "global": {"per_minute": 100},
}


def get_api_key() -> str:
    key = os.environ.get("MOLTBOOK_API_KEY", "")
    if not key:
        print("ERROR: MOLTBOOK_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def _load_rate_state() -> dict:
    registered_at = None
    if REGISTRATION_FILE.exists():
        try:
            with open(REGISTRATION_FILE) as f:
                reg = json.load(f)
                registered_at = reg.get("registered_at")
        except Exception:
            registered_at = None

    if RATE_LIMITS_FILE.exists():
        with open(RATE_LIMITS_FILE) as f:
            state = json.load(f)
            # Backfill from canonical registration record to avoid permanent
            # "new_agent" mode when legacy state lacks registered_at.
            if not state.get("registered_at") and registered_at:
                state["registered_at"] = registered_at
                _save_rate_state(state)
            return state
    return {
        "registered_at": registered_at,
        "last_post": None,
        "last_comment": None,
        "comments_today": 0,
        "comments_today_date": None,
        "last_dm": None,
        "request_timestamps": [],
    }


def _save_rate_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(RATE_LIMITS_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_new_agent(state: dict) -> bool:
    if not state.get("registered_at"):
        return True
    reg_time = datetime.fromisoformat(state["registered_at"])
    return (datetime.now(timezone.utc) - reg_time).total_seconds() < 86400


def check_rate_limit(action: str) -> tuple[bool, str]:
    """Check if an action is allowed under rate limits. Returns (allowed, reason)."""
    state = _load_rate_state()
    now = datetime.now(timezone.utc)
    new = is_new_agent(state)

    if action == "post":
        if state.get("last_post"):
            elapsed = (now - datetime.fromisoformat(state["last_post"])).total_seconds()
            cooldown = RATE_LIMITS["post"]["new_agent" if new else "normal"]
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                return False, f"Post cooldown: {remaining}s remaining"

    elif action == "comment":
        if state.get("last_comment"):
            elapsed = (now - datetime.fromisoformat(state["last_comment"])).total_seconds()
            cooldown = RATE_LIMITS["comment"]["new_agent" if new else "normal"]
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                return False, f"Comment cooldown: {remaining}s remaining"

        today = now.strftime("%Y-%m-%d")
        if state.get("comments_today_date") == today:
            limit = RATE_LIMITS["comment_daily"]["new_agent" if new else "normal"]
            if state.get("comments_today", 0) >= limit:
                return False, f"Daily comment limit reached ({limit})"

    elif action == "dm":
        if new:
            return False, "DMs blocked for first 24 hours"

    # Check global rate limit (100 req/min)
    timestamps = state.get("request_timestamps", [])
    cutoff = (now.timestamp() - 60)
    recent = [t for t in timestamps if t > cutoff]
    if len(recent) >= RATE_LIMITS["global"]["per_minute"]:
        return False, "Global rate limit: 100 requests/minute"

    return True, "OK"


def record_action(action: str):
    """Record that an action was taken for rate limit tracking."""
    state = _load_rate_state()
    now = datetime.now(timezone.utc)

    if action == "post":
        state["last_post"] = now.isoformat()
    elif action == "comment":
        state["last_comment"] = now.isoformat()
        today = now.strftime("%Y-%m-%d")
        if state.get("comments_today_date") != today:
            state["comments_today"] = 0
            state["comments_today_date"] = today
        state["comments_today"] = state.get("comments_today", 0) + 1
    elif action == "dm":
        state["last_dm"] = now.isoformat()
    elif action == "register":
        state["registered_at"] = now.isoformat()

    # Track global requests
    timestamps = state.get("request_timestamps", [])
    cutoff = now.timestamp() - 60
    timestamps = [t for t in timestamps if t > cutoff]
    timestamps.append(now.timestamp())
    state["request_timestamps"] = timestamps

    _save_rate_state(state)


def api_request(
    method: str,
    endpoint: str,
    data: dict | None = None,
    params: dict | None = None,
    files: dict | None = None,
    retries: int = 3,
    backoff: float = 1.0,
) -> dict | None:
    """Make an authenticated API request to Moltbook.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        endpoint: API endpoint path (e.g., /agents/me)
        data: JSON body for POST/PATCH
        params: Query parameters
        files: File uploads (not yet supported via urllib — placeholder)
        retries: Number of retries on transient failures
        backoff: Initial backoff in seconds (doubles per retry)

    Returns:
        Parsed JSON response or None on error
    """
    api_key = get_api_key()

    url = f"{BASE_URL}{endpoint}"
    if params:
        query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v is not None)
        if query:
            url = f"{url}?{query}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    for attempt in range(retries):
        try:
            req = Request(url, data=body, headers=headers, method=method)
            with urlopen(req, timeout=30) as resp:
                record_action("request")
                resp_body = resp.read().decode("utf-8")
                if resp_body:
                    return json.loads(resp_body)
                return {"status": "ok"}

        except HTTPError as e:
            resp_body = e.read().decode("utf-8", errors="replace")
            if e.code == 429:
                wait = backoff * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s before retry...", file=sys.stderr)
                time.sleep(wait)
                continue
            elif e.code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"Server error {e.code}. Retry {attempt+1}/{retries} in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                print(f"API error {e.code}: {resp_body}", file=sys.stderr)
                return None

        except URLError as e:
            if attempt < retries - 1:
                wait = backoff * (2 ** attempt)
                print(f"Network error: {e.reason}. Retry in {wait}s", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Network error after {retries} retries: {e.reason}", file=sys.stderr)
                return None

    return None


# --- CLI Commands ---

def cmd_me(args):
    """Get own agent profile."""
    result = api_request("GET", "/agents/me")
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to fetch agent profile", file=sys.stderr)
        raise SystemExit(1)


def cmd_status(args):
    """Check claim/verification status."""
    result = api_request("GET", "/agents/status")
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to fetch agent status", file=sys.stderr)
        raise SystemExit(1)


def cmd_update_profile(args):
    """Update agent profile."""
    data = {}
    if args.description:
        data["description"] = args.description
    if args.website:
        data["website"] = args.website
    if not data:
        print("Nothing to update. Use --description or --website.", file=sys.stderr)
        return
    result = api_request("PATCH", "/agents/me", data=data)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to update profile", file=sys.stderr)
        raise SystemExit(1)


def cmd_rate_status(args):
    """Show current rate limit status."""
    state = _load_rate_state()
    new = is_new_agent(state)
    now = datetime.now(timezone.utc)

    print(f"Agent status: {'NEW (< 24h)' if new else 'established'}")
    print(f"Registered: {state.get('registered_at', 'not yet')}")
    print()

    for action in ["post", "comment", "dm"]:
        allowed, reason = check_rate_limit(action)
        status = "ALLOWED" if allowed else f"BLOCKED — {reason}"
        print(f"  {action}: {status}")

    today = now.strftime("%Y-%m-%d")
    if state.get("comments_today_date") == today:
        limit = RATE_LIMITS["comment_daily"]["new_agent" if new else "normal"]
        print(f"  comments today: {state.get('comments_today', 0)}/{limit}")


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook API Client — Base client for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    sub.add_parser("me", help="Get own agent profile")
    sub.add_parser("status", help="Check verification/claim status")

    up = sub.add_parser("update-profile", help="Update agent profile")
    up.add_argument("--description", help="New description")
    up.add_argument("--website", help="Website URL")

    sub.add_parser("rate-status", help="Show rate limit status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "me": cmd_me,
        "status": cmd_status,
        "update-profile": cmd_update_profile,
        "rate-status": cmd_rate_status,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
