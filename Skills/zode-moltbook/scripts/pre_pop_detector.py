#!/usr/bin/env python3
"""
Pre-Pop Detector — identify threads likely to pop before they do.

Pipeline:
1) pull fresh posts (new feed)
2) score pre-pop signals
3) persist observations and alerts
4) evaluate older alerts after a horizon window

Usage:
  python3 pre_pop_detector.py scan [--limit 60] [--dry-run] [--json]
  python3 pre_pop_detector.py evaluate [--horizon-minutes 60] [--json]
  python3 pre_pop_detector.py status [--json]
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


STATE_DIR = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
OBS_FILE = ANALYTICS_DIR / "prepop_observations.jsonl"
ALERT_FILE = ANALYTICS_DIR / "prepop_alerts.jsonl"
EVAL_FILE = ANALYTICS_DIR / "prepop_evaluations.jsonl"
CONFIG_FILE = ANALYTICS_DIR / "prepop_config.json"

DEFAULT_CONFIG = {
    "threshold": 0.62,
    "top_k": 8,
    "weights": {
        "comment_velocity": 0.35,
        "comment_acceleration": 0.25,
        "score_velocity": 0.15,
        "author_baseline": 0.15,
        "topic_fit": 0.10,
    },
    "success": {
        "min_comment_gain": 5,
        "min_score_gain": 3,
    },
}

TOPIC_KEYWORDS = [
    "human", "humans", "non-technical", "trust", "communication",
    "partnership", "relationship", "frustrated", "mental model", "agent-human",
]


@dataclass
class SignalRow:
    post_id: str
    title: str
    author_name: str
    submolt: str
    score: int
    comments: int
    created_at: str
    observed_at: str
    comment_velocity: float
    comment_acceleration: float
    score_velocity: float
    author_baseline: float
    topic_fit: float
    pop_score: float


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            return {**DEFAULT_CONFIG, **data}
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def append_jsonl(path: Path, rows: list[dict], dry_run: bool = False):
    if dry_run or not rows:
        return
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def write_jsonl(path: Path, rows: list[dict], dry_run: bool = False):
    if dry_run:
        return
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def read_jsonl(path: Path, limit: int = 2000) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-limit:]


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clamp_01(x: float) -> float:
    return max(0.0, min(1.0, x))


def normalize_positive(value: float, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return clamp_01(value / scale)


def compute_topic_fit(title: str, content: str) -> float:
    text = f"{title or ''} {content or ''}".lower()
    hits = sum(1 for kw in TOPIC_KEYWORDS if kw in text)
    return clamp_01(hits / 4.0)


def minutes_between(a: datetime | None, b: datetime | None) -> float:
    if not a or not b:
        return 0.0
    return max(0.0, (b - a).total_seconds() / 60.0)


def latest_obs_by_post(rows: list[dict]) -> dict[str, list[dict]]:
    by_post: dict[str, list[dict]] = {}
    for r in rows:
        pid = r.get("post_id")
        if not pid:
            continue
        by_post.setdefault(pid, []).append(r)
    for pid in by_post:
        by_post[pid].sort(key=lambda x: x.get("observed_at", ""))
    return by_post


def author_baseline(post: dict) -> float:
    author = post.get("author", {}) if isinstance(post.get("author"), dict) else {}
    karma = author.get("karma", 0) or 0
    followers = author.get("follower_count", author.get("followers", 0)) or 0
    # Saturating transform: strong lift for known high-signal authors, bounded [0,1]
    return clamp_01((math.log1p(karma) / 8.0) * 0.6 + (math.log1p(followers) / 6.0) * 0.4)


def compute_signals(post: dict, history: list[dict], weights: dict) -> SignalRow:
    now = utc_now()
    pid = post.get("id", "")
    title = post.get("title", "") or ""
    content = post.get("content", "") or ""
    author = post.get("author", {}) if isinstance(post.get("author"), dict) else {}
    author_name = author.get("name", "") or ""
    submolt = (post.get("submolt", {}) if isinstance(post.get("submolt"), dict) else {"name": post.get("submolt", "")}).get("name", "")
    score = int(post.get("score", 0) or 0)
    comments = int(post.get("comment_count", 0) or 0)
    created_at = post.get("created_at", "") or ""

    prev = history[-1] if history else None
    now_iso = now.isoformat()

    prev_obs_at = parse_iso(prev.get("observed_at")) if prev else None
    prev_comments = int(prev.get("comments", 0)) if prev else comments
    prev_score = int(prev.get("score", 0)) if prev else score
    dt_min = minutes_between(prev_obs_at, now)

    c_vel_raw = ((comments - prev_comments) / dt_min) if dt_min > 0 else 0.0
    s_vel_raw = ((score - prev_score) / dt_min) if dt_min > 0 else 0.0

    prev_c_vel = float(prev.get("comment_velocity", 0.0)) if prev else 0.0
    acc_raw = (c_vel_raw - prev_c_vel) / dt_min if dt_min > 0 else 0.0

    c_vel = normalize_positive(c_vel_raw, 1.2)
    c_acc = normalize_positive(acc_raw, 0.12)
    s_vel = normalize_positive(s_vel_raw, 1.0)
    a_base = author_baseline(post)
    t_fit = compute_topic_fit(title, content)

    score_total = (
        weights.get("comment_velocity", 0.0) * c_vel +
        weights.get("comment_acceleration", 0.0) * c_acc +
        weights.get("score_velocity", 0.0) * s_vel +
        weights.get("author_baseline", 0.0) * a_base +
        weights.get("topic_fit", 0.0) * t_fit
    )

    return SignalRow(
        post_id=pid,
        title=title[:180],
        author_name=author_name,
        submolt=submolt,
        score=score,
        comments=comments,
        created_at=created_at,
        observed_at=now_iso,
        comment_velocity=round(c_vel, 4),
        comment_acceleration=round(c_acc, 4),
        score_velocity=round(s_vel, 4),
        author_baseline=round(a_base, 4),
        topic_fit=round(t_fit, 4),
        pop_score=round(clamp_01(score_total), 4),
    )


def fetch_new_feed(limit: int) -> list[dict]:
    sys.path.insert(0, str(Path(__file__).parent))
    from moltbook_reader import get_feed  # lazy import
    posts = get_feed(sort="new", limit=limit)
    return posts or []


def cmd_scan(args: argparse.Namespace):
    config = load_config()
    weights = config.get("weights", DEFAULT_CONFIG["weights"])
    threshold = float(config.get("threshold", DEFAULT_CONFIG["threshold"]))
    top_k = int(config.get("top_k", DEFAULT_CONFIG["top_k"]))

    history = latest_obs_by_post(read_jsonl(OBS_FILE, limit=8000))
    existing_alerts = read_jsonl(ALERT_FILE, limit=10000)
    recent_alert_cutoff = utc_now() - timedelta(minutes=90)
    recently_alerted_post_ids = set()
    for a in existing_alerts:
        alerted_at = parse_iso(a.get("alerted_at"))
        if not alerted_at:
            continue
        if alerted_at >= recent_alert_cutoff and a.get("status", "open") == "open":
            pid = a.get("post_id")
            if pid:
                recently_alerted_post_ids.add(pid)
    observations: list[dict] = []
    alerts: list[dict] = []

    try:
        posts = fetch_new_feed(limit=args.limit)
    except Exception as e:
        print(f"ERROR: failed to fetch feed: {e}", file=sys.stderr)
        posts = []

    for post in posts:
        pid = post.get("id")
        if not pid:
            continue
        row = compute_signals(post, history.get(pid, []), weights)
        row_dict = row.__dict__
        observations.append(row_dict)

    ranked = sorted(observations, key=lambda x: x.get("pop_score", 0), reverse=True)
    for r in ranked[:top_k]:
        if r["pop_score"] >= threshold:
            if r["post_id"] in recently_alerted_post_ids:
                continue
            alerts.append({
                "alerted_at": iso_now(),
                "post_id": r["post_id"],
                "title": r["title"],
                "author_name": r["author_name"],
                "submolt": r["submolt"],
                "pop_score": r["pop_score"],
                "score_at_alert": r["score"],
                "comments_at_alert": r["comments"],
                "signals": {
                    "comment_velocity": r["comment_velocity"],
                    "comment_acceleration": r["comment_acceleration"],
                    "score_velocity": r["score_velocity"],
                    "author_baseline": r["author_baseline"],
                    "topic_fit": r["topic_fit"],
                },
                "status": "open",
            })

    append_jsonl(OBS_FILE, observations, dry_run=args.dry_run)
    append_jsonl(ALERT_FILE, alerts, dry_run=args.dry_run)

    print(f"PRE-POP SCAN @ {iso_now()}")
    print("=" * 50)
    print(f"posts_fetched: {len(posts)}")
    print(f"observations_written: {len(observations)}")
    print(f"alerts: {len(alerts)}")
    print(f"threshold: {threshold}")
    if ranked:
        print("\nTOP CANDIDATES:")
        for i, r in enumerate(ranked[:8], 1):
            print(f"{i:>2}. [{r['pop_score']:.3f}] {r['title'][:72]} | c={r['comments']} s={r['score']} | s/{r['submolt']}")

    if args.json:
        payload = {
            "timestamp": iso_now(),
            "posts_fetched": len(posts),
            "observations_written": len(observations),
            "alerts": alerts,
            "top_candidates": ranked[:20],
            "dry_run": args.dry_run,
        }
        print(json.dumps(payload, indent=2))


def cmd_evaluate(args: argparse.Namespace):
    config = load_config()
    success_cfg = config.get("success", DEFAULT_CONFIG["success"])
    min_comment_gain = int(success_cfg.get("min_comment_gain", 5))
    min_score_gain = int(success_cfg.get("min_score_gain", 3))

    horizon = timedelta(minutes=args.horizon_minutes)
    now = utc_now()
    alerts = read_jsonl(ALERT_FILE, limit=10000)
    obs = latest_obs_by_post(read_jsonl(OBS_FILE, limit=20000))
    existing_evals = read_jsonl(EVAL_FILE, limit=20000)
    existing_keys = {
        (
            e.get("post_id"),
            e.get("alerted_at"),
            int(e.get("horizon_minutes", args.horizon_minutes)),
        )
        for e in existing_evals
    }

    evaluations = []
    close_keys: set[tuple[str, str]] = set()
    for a in alerts:
        if a.get("status") == "closed":
            continue
        alerted_at = parse_iso(a.get("alerted_at"))
        if not alerted_at or (now - alerted_at) < horizon:
            continue
        pid = a.get("post_id", "")
        eval_key = (pid, a.get("alerted_at"), args.horizon_minutes)
        if eval_key in existing_keys:
            continue
        post_hist = obs.get(pid, [])
        if not post_hist:
            continue
        latest = post_hist[-1]
        comment_gain = int(latest.get("comments", 0)) - int(a.get("comments_at_alert", 0))
        score_gain = int(latest.get("score", 0)) - int(a.get("score_at_alert", 0))
        success = (comment_gain >= min_comment_gain) or (score_gain >= min_score_gain)
        evaluations.append({
            "evaluated_at": iso_now(),
            "post_id": pid,
            "title": a.get("title", ""),
            "alerted_at": a.get("alerted_at"),
            "horizon_minutes": args.horizon_minutes,
            "pop_score": a.get("pop_score", 0),
            "comment_gain": comment_gain,
            "score_gain": score_gain,
            "success": success,
        })
        close_keys.add((pid, a.get("alerted_at")))

    append_jsonl(EVAL_FILE, evaluations, dry_run=args.dry_run)

    if close_keys:
        updated_alerts = []
        for a in alerts:
            key = (a.get("post_id", ""), a.get("alerted_at", ""))
            if key in close_keys:
                a = {**a, "status": "closed", "closed_at": iso_now()}
            updated_alerts.append(a)
        write_jsonl(ALERT_FILE, updated_alerts, dry_run=args.dry_run)

    total = len(evaluations)
    wins = sum(1 for e in evaluations if e.get("success"))
    precision = (wins / total) if total else 0.0

    print(f"PRE-POP EVALUATE @ {iso_now()}")
    print("=" * 50)
    print(f"evaluated: {total}")
    print(f"successes: {wins}")
    print(f"precision: {precision:.3f}")
    print(f"success rule: comment_gain>={min_comment_gain} OR score_gain>={min_score_gain}")

    if args.json:
        print(json.dumps({
            "timestamp": iso_now(),
            "evaluated": total,
            "successes": wins,
            "precision": round(precision, 4),
            "rows": evaluations,
            "dry_run": args.dry_run,
        }, indent=2))


def cmd_status(args: argparse.Namespace):
    config = load_config()
    obs = read_jsonl(OBS_FILE, limit=5000)
    alerts = read_jsonl(ALERT_FILE, limit=5000)
    evals = read_jsonl(EVAL_FILE, limit=5000)

    open_alerts = [a for a in alerts if a.get("status", "open") == "open"]
    last_obs = obs[-1]["observed_at"] if obs else None
    last_alert = alerts[-1]["alerted_at"] if alerts else None

    print("PRE-POP STATUS")
    print("=" * 50)
    print(f"threshold: {config.get('threshold')}")
    print(f"top_k: {config.get('top_k')}")
    print(f"observations: {len(obs)}")
    print(f"alerts: {len(alerts)} (open={len(open_alerts)})")
    print(f"evaluations: {len(evals)}")
    print(f"last_observation: {last_obs}")
    print(f"last_alert: {last_alert}")

    if args.json:
        print(json.dumps({
            "config": config,
            "observations": len(obs),
            "alerts_total": len(alerts),
            "alerts_open": len(open_alerts),
            "evaluations": len(evals),
            "last_observation": last_obs,
            "last_alert": last_alert,
        }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Pre-pop detector for early Moltbook thread opportunities")
    sub = parser.add_subparsers(dest="command")

    s = sub.add_parser("scan", help="Scan new feed and score pre-pop signals")
    s.add_argument("--limit", type=int, default=60, help="How many newest posts to scan")
    s.add_argument("--dry-run", action="store_true", help="Compute but do not write state files")
    s.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    e = sub.add_parser("evaluate", help="Evaluate older alerts against realized growth")
    e.add_argument("--horizon-minutes", type=int, default=60, help="Evaluation horizon in minutes")
    e.add_argument("--dry-run", action="store_true", help="Evaluate without writing evaluation rows")
    e.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    st = sub.add_parser("status", help="Show detector state")
    st.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
