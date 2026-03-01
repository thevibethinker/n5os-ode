#!/usr/bin/env python3
"""
Experiment Executor — autonomous action loop for Zøde Moltbook experiments.

Runs one cycle that attempts:
- 1 post (experiment-tagged)
- 1 comment (experiment-tagged)

Policy:
- 3 active experiments max (from experiment_portfolio state)
- Follower-first, quality-gated execution
- Queue next-day comments only if top 5% relevance/commentator criteria are met
"""

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from feed_scanner import check_rate_limits, detect_phase, run_scan
from content_generator import generate_comment, generate_post
from moltbook_client import check_rate_limit
from post_quality_gate import score_post
from staging_queue import add_comment, add_post, publish

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
EXPERIMENTS_DIR = STATE_DIR / "experiments"

PORTFOLIO_FILE = EXPERIMENTS_DIR / "portfolio_state.json"
REGISTRY_FILE = EXPERIMENTS_DIR / "experiment_registry.jsonl"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"
EXECUTOR_LOG_FILE = EXPERIMENTS_DIR / "executor_log.jsonl"
EXECUTOR_STATE_FILE = EXPERIMENTS_DIR / "executor_state.json"
NEXTDAY_QUEUE_FILE = EXPERIMENTS_DIR / "next_day_comment_queue.jsonl"

ET = ZoneInfo("America/New_York")

CONFIG = {
    "opportunity_gate": 75.0,
    "quality_gate": 7.5,
    "headroom_gate": 0.40,
    "risk_gate": 0.30,
    "min_cycle_spacing_minutes": 30,
    "feed_limit": 60,
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(txt)
    except ValueError:
        return None


def _load_json(path: Path, default: Any):
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _append_jsonl(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def _default_executor_state() -> dict:
    return {
        "next_slot_index": 0,
        "last_cycle_started_at": None,
        "last_post_cycle_at": None,
        "last_comment_cycle_at": None,
    }


def _load_executor_state() -> dict:
    return _load_json(EXECUTOR_STATE_FILE, _default_executor_state())


def _save_executor_state(state: dict):
    _save_json(EXECUTOR_STATE_FILE, state)


def _load_registry() -> list[dict]:
    return list(_iter_jsonl(REGISTRY_FILE))


def _active_experiments() -> list[dict]:
    portfolio = _load_json(PORTFOLIO_FILE, {})
    slots = portfolio.get("slots", {})
    ordered_ids = [slots.get("A"), slots.get("B"), slots.get("C")]
    reg = {r.get("experiment_id"): r for r in _load_registry() if r.get("status") == "active"}
    result = []
    for slot, exp_id in zip(["A", "B", "C"], ordered_ids):
        if exp_id and exp_id in reg:
            row = dict(reg[exp_id])
            row["slot"] = slot
            result.append(row)
    return result


def _recent_published_minutes(action_type: str) -> float | None:
    now = datetime.now(UTC)
    latest = None
    for row in _iter_jsonl(POSTING_EVENTS_FILE):
        if row.get("event") != "publish_attempt":
            continue
        if row.get("type") != action_type:
            continue
        if not row.get("published"):
            continue
        ts = _parse_ts(row.get("timestamp"))
        if ts and (latest is None or ts > latest):
            latest = ts
    if latest is None:
        return None
    return (now - latest).total_seconds() / 60.0


def _attempt_no(experiment_id: str, action_type: str) -> int:
    count = 0
    for row in _iter_jsonl(POSTING_EVENTS_FILE):
        if row.get("event") != "publish_attempt":
            continue
        if row.get("type") != action_type:
            continue
        if row.get("experiment_id") == experiment_id:
            count += 1
    return count + 1


def _headroom(phase: str) -> float:
    from feed_scanner import load_today_actions

    today_actions = load_today_actions()
    rate = check_rate_limits(phase, today_actions)
    posts_used = max(today_actions.get("posts", 0), 0)
    comments_used = max(today_actions.get("comments", 0), 0)
    posts_total = max(posts_used + max(rate.get("posts_remaining", 0), 0), 1)
    comments_total = max(comments_used + max(rate.get("comments_remaining", 0), 0), 1)
    post_ratio = max(rate.get("posts_remaining", 0), 0) / posts_total
    comment_ratio = max(rate.get("comments_remaining", 0), 0) / comments_total
    return max(0.0, min((post_ratio + comment_ratio) / 2.0, 1.0))


def _latest_engagement_snapshot() -> dict:
    files = sorted(ANALYTICS_DIR.glob("engagement-*.json"), reverse=True)
    for p in files:
        payload = _load_json(p, {})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def _top_commentator_threshold(snapshot: dict) -> float:
    derived = snapshot.get("derived_metrics", {})
    by_author = derived.get("rapport_roi_by_author", {}).get("top_authors", [])
    vals = [float(a.get("interactions_per_comment", 0.0) or 0.0) for a in by_author]
    vals = [v for v in vals if v > 0]
    if not vals:
        return 0.0
    vals.sort()
    idx = max(0, int(0.95 * (len(vals) - 1)))
    return vals[idx]


def _recently_targeted_post_ids(hours: int = 24) -> set[str]:
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    ids: set[str] = set()
    for row in _iter_jsonl(POSTING_EVENTS_FILE):
        if row.get("event") != "publish_attempt" or row.get("type") != "comment":
            continue
        if not row.get("published"):
            continue
        ts = _parse_ts(row.get("timestamp"))
        if ts and ts < cutoff:
            continue
        tid = row.get("target_id")
        if tid:
            ids.add(tid)
    return ids


def _score_risk(opportunity_score_100: float, quality_10: float) -> float:
    quality_risk = max(0.0, 1.0 - (quality_10 / 10.0))
    opp_risk = max(0.0, 1.0 - (opportunity_score_100 / 100.0))
    risk = 0.7 * quality_risk + 0.3 * opp_risk
    return round(max(0.0, min(risk, 1.0)), 4)


def _build_post_draft(exp: dict, opportunity: dict | None, dry_run: bool = False) -> tuple[str, str, str] | None:
    """Generate a post via LLM. Returns None if generation fails. Skips network in dry_run."""
    family = exp.get("objective_family", "FOLLOW_CONVERT")
    submolt = "general"
    if opportunity:
        sub = opportunity.get("submolt")
        if isinstance(sub, str) and sub.strip():
            submolt = sub.strip().lower()

    if dry_run:
        return submolt, f"[DRY-RUN] Preview: {family}", f"[DRY-RUN] Preview post for {family} in s/{submolt}. No LLM call made."

    result = generate_post(
        experiment_family=family,
        opportunity=opportunity,
        submolt=submolt,
    )
    if result:
        return result

    import sys
    print(f"WARNING: LLM content generation failed for post (family={family}), skipping cycle", file=sys.stderr)
    return None


def _build_comment_draft(exp: dict, opportunity: dict, dry_run: bool = False) -> str | None:
    """Generate a comment via LLM. Returns None if generation fails. Skips network in dry_run."""
    family = exp.get("objective_family", "COMMENT_DEPTH")
    post_id = opportunity.get("post_id", "")

    if dry_run:
        return f"[DRY-RUN] Preview comment for {family}. No LLM call made."

    result = generate_comment(
        experiment_family=family,
        opportunity=opportunity,
        post_id=post_id,
    )
    if result:
        return result

    import sys
    print(f"WARNING: LLM comment generation failed (family={family}), skipping comment", file=sys.stderr)
    return None


def _quality_scores(title: str, content: str, submolt: str) -> tuple[float, bool]:
    scored = score_post(title, content, submolt=submolt)
    q10 = round(float(scored.get("average", 0.0)) * 2.0, 2)
    return q10, bool(scored.get("passed"))


def _pick_opportunity(scan_result: dict, snapshot: dict) -> tuple[dict | None, float]:
    opps = scan_result.get("opportunities", [])
    if not opps:
        return None, 0.0

    scores = sorted([float(o.get("score", 0.0) or 0.0) for o in opps])
    if not scores:
        return None, 0.0
    idx = max(0, int(0.95 * (len(scores) - 1)))
    score_threshold = scores[idx]

    top_commentator_thresh = _top_commentator_threshold(snapshot)
    recent_targeted = _recently_targeted_post_ids(hours=24)

    candidates = []
    for o in opps:
        if o.get("action") != "comment":
            continue
        if o.get("post_id") in recent_targeted:
            continue
        priority_mention = bool(o.get("priority_mention", False))
        if (not priority_mention) and float(o.get("score", 0.0) or 0.0) < score_threshold:
            continue

        author_strength = 0.0
        for row in snapshot.get("derived_metrics", {}).get("rapport_roi_by_author", {}).get("top_authors", []):
            if (row.get("author", "").lower() == str(o.get("author", "")).lower()):
                author_strength = float(row.get("interactions_per_comment", 0.0) or 0.0)
                break

        commentator_ok = priority_mention or (top_commentator_thresh <= 0.0) or (author_strength >= top_commentator_thresh)
        if commentator_ok:
            candidates.append((o, score_threshold))

    if not candidates:
        return None, score_threshold

    candidates.sort(
        key=lambda x: (
            bool(x[0].get("priority_mention", False)),
            float(x[0].get("score", 0.0) or 0.0),
            bool(x[0].get("has_rapport", False)),
        ),
        reverse=True,
    )
    return candidates[0][0], score_threshold


def _queue_for_next_day(opportunity: dict, reason: str):
    now_et = datetime.now(ET)
    row = {
        "queued_at": _now_iso(),
        "target_date_et": (now_et + timedelta(days=1)).date().isoformat(),
        "post_id": opportunity.get("post_id"),
        "title": opportunity.get("title", ""),
        "submolt": opportunity.get("submolt", ""),
        "author": opportunity.get("author", ""),
        "score": opportunity.get("score", 0.0),
        "reason": reason,
    }
    _append_jsonl(NEXTDAY_QUEUE_FILE, row)


def _due_queue_items() -> list[dict]:
    today_et = datetime.now(ET).date().isoformat()
    rows = []
    for row in _iter_jsonl(NEXTDAY_QUEUE_FILE):
        if row.get("target_date_et") and row.get("target_date_et") <= today_et:
            rows.append(row)
    return rows


def _rewrite_queue_keep_future():
    today_et = datetime.now(ET).date().isoformat()
    keep = [row for row in _iter_jsonl(NEXTDAY_QUEUE_FILE) if row.get("target_date_et", "9999-12-31") > today_et]
    with open(NEXTDAY_QUEUE_FILE, "w") as f:
        for row in keep:
            f.write(json.dumps(row) + "\n")


def _phase_arg(value: str | None) -> str:
    if value:
        return value
    return detect_phase()


def cmd_status(_args):
    state = _load_executor_state()
    active = _active_experiments()
    post_minutes = _recent_published_minutes("post")
    comment_minutes = _recent_published_minutes("comment")
    queue_count = sum(1 for _ in _iter_jsonl(NEXTDAY_QUEUE_FILE)) if NEXTDAY_QUEUE_FILE.exists() else 0

    print("EXPERIMENT EXECUTOR STATUS")
    print("=" * 60)
    print(f"Last cycle: {state.get('last_cycle_started_at')}")
    print(f"Next slot index: {state.get('next_slot_index')}")
    print(f"Active experiments: {[e.get('experiment_id') for e in active]}")
    print(f"Minutes since last post publish: {post_minutes if post_minutes is not None else 'n/a'}")
    print(f"Minutes since last comment publish: {comment_minutes if comment_minutes is not None else 'n/a'}")
    print(f"Next-day queue size: {queue_count}")


def cmd_run(args):
    now = datetime.now(UTC)
    phase = _phase_arg(args.phase)
    state = _load_executor_state()
    active = _active_experiments()

    cycle = {
        "timestamp": _now_iso(),
        "phase": phase,
        "status": "ok",
        "post": {"attempted": False, "published": False, "reason": None},
        "comment": {"attempted": False, "published": False, "reason": None},
        "dry_run": bool(args.dry_run),
    }

    if len(active) == 0:
        cycle["status"] = "no_active_experiments"
        cycle["post"]["reason"] = "no active experiments"
        cycle["comment"]["reason"] = "no active experiments"
        _append_jsonl(EXECUTOR_LOG_FILE, cycle)
        print(json.dumps(cycle, indent=2))
        return

    last_cycle = _parse_ts(state.get("last_cycle_started_at"))
    if last_cycle and (now - last_cycle).total_seconds() < (CONFIG["min_cycle_spacing_minutes"] * 60) and not args.force:
        cycle["status"] = "skipped_spacing"
        cycle["post"]["reason"] = "minimum 30m spacing not met"
        cycle["comment"]["reason"] = "minimum 30m spacing not met"
        _append_jsonl(EXECUTOR_LOG_FILE, cycle)
        print(json.dumps(cycle, indent=2))
        return

    try:
        scan = run_scan(phase=phase, dry_run=True, limit=int(args.feed_limit or CONFIG["feed_limit"]))
    except SystemExit:
        scan = {"opportunities": [], "summary": {}}
    except Exception as e:
        scan = {"opportunities": [], "summary": {}, "feed_error": str(e)}

    snapshot = _latest_engagement_snapshot()

    # rotation
    idx = int(state.get("next_slot_index", 0)) % len(active)
    post_exp = active[idx]
    comment_exp = active[(idx + 1) % len(active)] if len(active) > 1 else active[idx]
    state["next_slot_index"] = (idx + 1) % len(active)
    cycle["rotation"] = {
        "selected_post_experiment_id": post_exp.get("experiment_id"),
        "selected_comment_experiment_id": comment_exp.get("experiment_id"),
        "selected_post_slot": post_exp.get("slot"),
        "selected_comment_slot": comment_exp.get("slot"),
        "next_slot_index_after_cycle": state["next_slot_index"],
    }

    # queue due items first for comments
    due_queue = _due_queue_items()

    # Post action
    post_recent = _recent_published_minutes("post")
    post_allowed, post_reason = check_rate_limit("post")
    if post_recent is not None and post_recent < CONFIG["min_cycle_spacing_minutes"]:
        post_allowed = False
        post_reason = f"post spacing {post_recent:.1f}m < 30m"

    top_opp_for_post = None
    for o in scan.get("opportunities", []):
        if o.get("action") in {"comment", "consider"}:
            top_opp_for_post = o
            break

    post_draft = _build_post_draft(post_exp, top_opp_for_post, dry_run=args.dry_run)
    if post_draft is None:
        cycle["post"]["reason"] = "llm_generation_failed"
        cycle["post"]["experiment_id"] = post_exp.get("experiment_id")
        cycle["post"]["objective_family"] = post_exp.get("objective_family")
    else:
        submolt, title, content = post_draft
        q10, pass_gate = _quality_scores(title, content, submolt)
        opp_100 = max(float((top_opp_for_post or {}).get("score", 7.6) or 7.6) * 10.0, CONFIG["opportunity_gate"])
        headroom = _headroom(phase)
        risk = _score_risk(opp_100, q10)

        post_meta = {
            "experiment_id": post_exp.get("experiment_id"),
            "hypothesis_id": post_exp.get("hypothesis_id"),
            "objective_family": post_exp.get("objective_family"),
            "variant_id": post_exp.get("variant_id"),
            "attempt_no": _attempt_no(post_exp.get("experiment_id"), "post"),
            "decision_state": post_exp.get("last_decision") or "incubating",
            "decision_reason": "30m autonomous executor",
            "narrative_cohesion_score": 0.93,
            "opportunity_score": round(opp_100, 2),
            "quality_gate_score": q10,
            "rate_limit_headroom": round(headroom, 4),
            "risk_score": risk,
        }

        post_gates_ok = (
            opp_100 >= CONFIG["opportunity_gate"]
            and q10 >= CONFIG["quality_gate"]
            and headroom >= CONFIG["headroom_gate"]
            and risk <= CONFIG["risk_gate"]
            and pass_gate
        )

        if post_allowed and post_gates_ok:
            cycle["post"]["attempted"] = True
            if args.dry_run:
                cycle["post"]["reason"] = "dry_run pass"
                cycle["post"]["published"] = False
            else:
                staged = add_post(submolt=submolt, title=title, content=content, experiment_meta=post_meta)
                pub = publish(staged["id"], dry_run=False)
                cycle["post"]["published"] = bool(pub and pub.get("status") == "published")
                cycle["post"]["reason"] = "published" if cycle["post"]["published"] else "publish_failed"
                state["last_post_cycle_at"] = _now_iso()
        else:
            cycle["post"]["reason"] = f"blocked gates/rate: rate={post_reason}, opp={opp_100:.1f}, q={q10:.1f}, headroom={headroom:.2f}, risk={risk:.2f}"
        cycle["post"]["experiment_id"] = post_meta["experiment_id"]
        cycle["post"]["objective_family"] = post_meta["objective_family"]
        cycle["post"]["quality_gate_score"] = post_meta["quality_gate_score"]
        cycle["post"]["opportunity_score"] = post_meta["opportunity_score"]

    # Comment action
    comment_recent = _recent_published_minutes("comment")
    comment_allowed, comment_reason = check_rate_limit("comment")
    if comment_recent is not None and comment_recent < CONFIG["min_cycle_spacing_minutes"]:
        comment_allowed = False
        comment_reason = f"comment spacing {comment_recent:.1f}m < 30m"

    selected_opp = None
    score_threshold = 0.0
    queue_source = None
    if due_queue:
        queue_source = due_queue[0]
        selected_opp = {
            "post_id": queue_source.get("post_id"),
            "title": queue_source.get("title"),
            "submolt": queue_source.get("submolt"),
            "author": queue_source.get("author"),
            "score": queue_source.get("score", 0.0),
            "action": "comment",
        }
    else:
        selected_opp, score_threshold = _pick_opportunity(scan, snapshot)

    if selected_opp:
        comment_text = _build_comment_draft(comment_exp, selected_opp, dry_run=args.dry_run)
        if comment_text is None:
            cycle["comment"]["reason"] = "llm_generation_failed"
            cycle["comment"]["experiment_id"] = comment_exp.get("experiment_id")
            cycle["comment"]["objective_family"] = comment_exp.get("objective_family")
        else:
            cq10, cpass_gate = _quality_scores("", comment_text, str(selected_opp.get("submolt", "general")))
            copp_100 = float(selected_opp.get("score", 0.0) or 0.0) * 10.0
            cheadroom = _headroom(phase)
            crisk = _score_risk(copp_100, cq10)
            comment_meta = {
                "experiment_id": comment_exp.get("experiment_id"),
                "hypothesis_id": comment_exp.get("hypothesis_id"),
                "objective_family": comment_exp.get("objective_family"),
                "variant_id": comment_exp.get("variant_id"),
                "attempt_no": _attempt_no(comment_exp.get("experiment_id"), "comment"),
                "decision_state": comment_exp.get("last_decision") or "incubating",
                "decision_reason": "30m autonomous executor",
                "narrative_cohesion_score": 0.9,
                "opportunity_score": round(copp_100, 2),
                "quality_gate_score": cq10,
                "rate_limit_headroom": round(cheadroom, 4),
                "risk_score": crisk,
            }

            comment_gates_ok = (
                copp_100 >= CONFIG["opportunity_gate"]
                and cq10 >= CONFIG["quality_gate"]
                and cheadroom >= CONFIG["headroom_gate"]
                and crisk <= CONFIG["risk_gate"]
                and cpass_gate
            )

            if comment_allowed and comment_gates_ok:
                cycle["comment"]["attempted"] = True
                if args.dry_run:
                    cycle["comment"]["reason"] = "dry_run pass"
                    cycle["comment"]["published"] = False
                else:
                    staged_c = add_comment(post_id=selected_opp.get("post_id"), content=comment_text, experiment_meta=comment_meta)
                    pub_c = publish(staged_c["id"], dry_run=False)
                    cycle["comment"]["published"] = bool(pub_c and pub_c.get("status") == "published")
                    cycle["comment"]["reason"] = "published" if cycle["comment"]["published"] else "publish_failed"
                    state["last_comment_cycle_at"] = _now_iso()
                    if queue_source:
                        _rewrite_queue_keep_future()
            else:
                if not comment_allowed and selected_opp and float(selected_opp.get("score", 0.0) or 0.0) >= (score_threshold or 0.0):
                    _queue_for_next_day(selected_opp, reason=f"rate-limited: {comment_reason}")
                    cycle["comment"]["reason"] = f"queued_next_day ({comment_reason})"
                else:
                    cycle["comment"]["reason"] = f"blocked gates/rate: rate={comment_reason}, opp={copp_100:.1f}, q={cq10:.1f}, headroom={cheadroom:.2f}, risk={crisk:.2f}"
            cycle["comment"]["experiment_id"] = comment_meta["experiment_id"]
            cycle["comment"]["objective_family"] = comment_meta["objective_family"]
            cycle["comment"]["quality_gate_score"] = comment_meta["quality_gate_score"]
            cycle["comment"]["opportunity_score"] = comment_meta["opportunity_score"]
            cycle["comment"]["target_post_id"] = selected_opp.get("post_id")
    else:
        cycle["comment"]["reason"] = "no top-5% opportunity found"

    state["last_cycle_started_at"] = _now_iso()
    _save_executor_state(state)
    _append_jsonl(EXECUTOR_LOG_FILE, cycle)

    print(json.dumps(cycle, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Experiment Executor — autonomous 30m publishing loop")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Run one autonomous execution cycle")
    run.add_argument("--phase", choices=["first_24h", "establishment", "steady"], help="Override detected phase")
    run.add_argument("--feed-limit", type=int, default=CONFIG["feed_limit"])
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--force", action="store_true", help="Bypass 30m spacing check")

    sub.add_parser("status", help="Show executor status")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
