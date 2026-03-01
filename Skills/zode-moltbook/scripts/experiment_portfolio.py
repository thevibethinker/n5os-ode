#!/usr/bin/env python3
"""
Experiment Portfolio — 3-slot dynamic experiment governance for Zode.

Implements:
- max 3 active experiments
- forced evaluation on 4th challenger
- minimum tries before hard replacement
- progressive floor ratchet
- follower-first synthetic return score (SRS)

Usage:
  python3 experiment_portfolio.py init [--reset]
  python3 experiment_portfolio.py register --experiment-id EXP1 --objective-family FOLLOW_CONVERT --variant-id control
  python3 experiment_portfolio.py evaluate [--lookback-hours 24]
  python3 experiment_portfolio.py status [--json]
"""

import argparse
import json
import math
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
EXPERIMENTS_DIR = STATE_DIR / "experiments"

PORTFOLIO_FILE = EXPERIMENTS_DIR / "portfolio_state.json"
REGISTRY_FILE = EXPERIMENTS_DIR / "experiment_registry.jsonl"
EVALUATIONS_FILE = EXPERIMENTS_DIR / "evaluations.jsonl"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"

VALID_FAMILIES = {
    "FOLLOW_CONVERT",
    "COMMENT_DEPTH",
    "THREAD_CAPTURE",
    "COMPETITOR_INTERCEPT",
    "QUOTEABILITY",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def _append_jsonl(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


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


def _default_portfolio() -> dict:
    return {
        "updated_at": _now_iso(),
        "config": {
            "max_active": 3,
            "min_tries_before_replace": 3,
            "promote_delta": 0.05,
            "at_risk_delta": -0.02,
            "ratchet_fraction": 0.25,
            "review_interval_minutes": 60,
        },
        "baseline_srs": 0.20,
        "floor_srs": 0.20,
        "last_portfolio_avg_srs": 0.20,
        "slots": {
            "A": None,
            "B": None,
            "C": None,
        },
        "challenger_queue": [],
        "last_evaluation": None,
    }


def _load_portfolio() -> dict:
    return _load_json(PORTFOLIO_FILE, _default_portfolio())


def _save_portfolio(portfolio: dict):
    portfolio["updated_at"] = _now_iso()
    _save_json(PORTFOLIO_FILE, portfolio)


def _latest_engagement_snapshot() -> dict:
    files = sorted(ANALYTICS_DIR.glob("engagement-*.json"), reverse=True)
    for file in files:
        payload = _load_json(file, {})
        if isinstance(payload, dict) and payload.get("totals"):
            return payload
    return {}


def _coherence_gate(snapshot: dict) -> tuple[bool, str]:
    # If not in live mode, confidence in replacement decisions is lower.
    mode = snapshot.get("mode", "")
    if mode not in {"live_api", "live_api_degraded"}:
        return False, "engagement snapshot not live_api"
    # Use fetch health to gate aggressive replacement actions.
    degraded = snapshot.get("fetch_health", {}).get("degraded", False)
    if degraded:
        return False, "degraded fetch health"
    return True, "ok"


def _collect_events_by_experiment(lookback_hours: int) -> dict[str, list[dict]]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    by_exp: dict[str, list[dict]] = {}
    for row in _iter_jsonl(POSTING_EVENTS_FILE):
        if row.get("event") != "publish_attempt":
            continue
        ts = _parse_ts(row.get("timestamp", ""))
        if ts and ts < cutoff:
            continue
        exp_id = row.get("experiment_id", "untracked")
        by_exp.setdefault(exp_id, []).append(row)
    return by_exp


def _build_outcome_maps(snapshot: dict):
    posts = snapshot.get("posts", [])
    comments = snapshot.get("comments", []) + snapshot.get("discovered_comments", [])
    post_by_id = {
        p.get("moltbook_id"): {
            "interactions": (p.get("upvotes", 0) or 0) + (p.get("comment_count", 0) or 0),
            "upvotes": p.get("upvotes", 0) or 0,
            "comments": p.get("comment_count", 0) or 0,
        }
        for p in posts if p.get("moltbook_id")
    }
    comment_by_id = {
        c.get("moltbook_id"): {
            "interactions": (c.get("upvotes", 0) or 0) + (c.get("reply_count", 0) or 0),
            "upvotes": c.get("upvotes", 0) or 0,
            "replies": c.get("reply_count", 0) or 0,
            "content": c.get("content", ""),
        }
        for c in comments if c.get("moltbook_id")
    }
    return post_by_id, comment_by_id


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _compute_srs(events: list[dict], post_outcomes: dict, comment_outcomes: dict) -> dict:
    attempts = len([e for e in events if e.get("published")])
    if attempts == 0:
        return {
            "attempts": 0,
            "follower_signal": 0.0,
            "quality_engagement": 0.0,
            "narrative_cohesion": 0.9,
            "srs": 0.0,
        }

    post_interactions = 0
    comment_interactions = 0
    quality_hits = 0
    cohesion_scores = []
    scored_items = 0

    for e in events:
        if not e.get("published"):
            continue
        content_id = e.get("content_id")
        if e.get("type") == "post" and content_id in post_outcomes:
            post_interactions += post_outcomes[content_id]["interactions"]
            scored_items += 1
        if e.get("type") == "comment" and content_id in comment_outcomes:
            c = comment_outcomes[content_id]
            comment_interactions += c["interactions"]
            if c["replies"] > 0 or c["upvotes"] > 0:
                quality_hits += 1
            if len((c.get("content") or "").strip()) >= 120:
                quality_hits += 1
            scored_items += 1
        cohesion_scores.append(_safe_float(e.get("narrative_cohesion_score"), 0.9))

    follower_signal_raw = post_interactions + 0.35 * comment_interactions
    follower_signal = min(
        math.log1p(follower_signal_raw) / math.log1p(25.0),
        1.0,
    )
    quality_engagement = min((quality_hits / max(scored_items, 1)), 1.0)
    narrative_cohesion = sum(cohesion_scores) / max(len(cohesion_scores), 1)

    srs = (
        0.65 * follower_signal
        + 0.25 * quality_engagement
        + 0.10 * narrative_cohesion
    )
    return {
        "attempts": attempts,
        "follower_signal": round(follower_signal, 4),
        "quality_engagement": round(quality_engagement, 4),
        "narrative_cohesion": round(narrative_cohesion, 4),
        "srs": round(srs, 4),
    }


def _load_registry() -> list[dict]:
    return list(_iter_jsonl(REGISTRY_FILE))


def _save_registry(rows: list[dict]):
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _find_registry(registry: list[dict], experiment_id: str) -> dict | None:
    for row in registry:
        if row.get("experiment_id") == experiment_id:
            return row
    return None


def cmd_init(args):
    portfolio = _default_portfolio()
    if not args.reset and PORTFOLIO_FILE.exists():
        portfolio = _load_portfolio()
    _save_portfolio(portfolio)
    print(f"Initialized portfolio: {PORTFOLIO_FILE}")
    print(json.dumps(portfolio, indent=2))


def cmd_register(args):
    if args.objective_family not in VALID_FAMILIES:
        raise SystemExit(f"Invalid objective_family: {args.objective_family}")

    portfolio = _load_portfolio()
    registry = _load_registry()

    experiment_id = args.experiment_id or f"exp-{uuid.uuid4().hex[:8]}"
    if _find_registry(registry, experiment_id):
        raise SystemExit(f"Experiment already exists: {experiment_id}")

    row = {
        "experiment_id": experiment_id,
        "hypothesis_id": args.hypothesis_id,
        "objective_family": args.objective_family,
        "variant_id": args.variant_id,
        "status": "queued",
        "created_at": _now_iso(),
        "at_risk_count": 0,
        "last_decision": None,
        "slot": None,
        "notes": args.notes or "",
    }

    placed = False
    for slot in ("A", "B", "C"):
        if portfolio["slots"].get(slot) is None:
            portfolio["slots"][slot] = experiment_id
            row["status"] = "active"
            row["slot"] = slot
            placed = True
            break
    if not placed:
        portfolio["challenger_queue"].append(experiment_id)
        row["status"] = "queued_challenger"

    registry.append(row)
    _save_registry(registry)
    _save_portfolio(portfolio)

    print(f"Registered experiment: {experiment_id} ({row['status']})")
    print(json.dumps(row, indent=2))


def cmd_evaluate(args):
    portfolio = _load_portfolio()
    registry = _load_registry()
    snapshot = _latest_engagement_snapshot()
    coherence_ok, coherence_reason = _coherence_gate(snapshot)
    events_by_exp = _collect_events_by_experiment(args.lookback_hours)
    post_outcomes, comment_outcomes = _build_outcome_maps(snapshot)

    config = portfolio["config"]
    baseline = _safe_float(portfolio.get("baseline_srs"), 0.2)
    floor = _safe_float(portfolio.get("floor_srs"), baseline)
    promote_delta = _safe_float(config.get("promote_delta"), 0.05)
    at_risk_delta = _safe_float(config.get("at_risk_delta"), -0.02)
    min_tries = int(config.get("min_tries_before_replace", 3))

    eval_rows = []
    active_srs_values = []

    for row in registry:
        exp_id = row["experiment_id"]
        events = events_by_exp.get(exp_id, [])
        score = _compute_srs(events, post_outcomes, comment_outcomes)
        srs = score["srs"]
        attempts = score["attempts"]
        delta = (srs - baseline) / baseline if baseline > 0 else 0.0

        decision = "incubating"
        reason = f"attempts {attempts}/{min_tries}"
        replaceable = False
        if attempts >= min_tries:
            if delta >= promote_delta:
                decision = "promote"
                reason = f"delta {delta:.2%} >= promote threshold {promote_delta:.2%}"
                row["at_risk_count"] = 0
            elif delta < at_risk_delta:
                row["at_risk_count"] = int(row.get("at_risk_count", 0)) + 1
                decision = "at_risk"
                reason = f"delta {delta:.2%} below at-risk threshold {at_risk_delta:.2%}"
                if row["at_risk_count"] >= 2 and srs < floor * (1.0 + at_risk_delta):
                    decision = "replaceable"
                    replaceable = True
                    reason = f"below floor and at-risk for {row['at_risk_count']} consecutive evaluations"
            else:
                decision = "iterate"
                reason = f"delta {delta:.2%} in iterate band"
                row["at_risk_count"] = 0

        # Coherence gate blocks aggressive replacement actions.
        if not coherence_ok and decision in {"replaceable"}:
            decision = "at_risk"
            replaceable = False
            reason = f"coherence gate blocked replacement: {coherence_reason}"

        row["last_decision"] = decision
        row["last_evaluated_at"] = _now_iso()
        eval_row = {
            "timestamp": _now_iso(),
            "experiment_id": exp_id,
            "status": row.get("status"),
            "slot": row.get("slot"),
            "decision": decision,
            "decision_reason": reason,
            "replaceable": replaceable,
            "baseline_srs": round(baseline, 4),
            "floor_srs": round(floor, 4),
            "delta": round(delta, 4),
            **score,
        }
        eval_rows.append(eval_row)
        if row.get("status") == "active":
            active_srs_values.append(srs)

    # Forced review when a challenger exists and all 3 slots are occupied.
    queue = portfolio.get("challenger_queue", [])
    occupied = [portfolio["slots"].get("A"), portfolio["slots"].get("B"), portfolio["slots"].get("C")]
    if queue and all(occupied):
        challenger_id = queue[0]
        challenger_eval = next((e for e in eval_rows if e["experiment_id"] == challenger_id), None)
        incumbents = [e for e in eval_rows if e.get("slot") in {"A", "B", "C"}]
        replaceables = sorted(
            [e for e in incumbents if e.get("replaceable")],
            key=lambda x: x.get("srs", 0),
        )
        if challenger_eval and replaceables and challenger_eval.get("srs", 0) > replaceables[0].get("srs", 0):
            victim = replaceables[0]
            victim_id = victim["experiment_id"]
            victim_slot = victim["slot"]
            portfolio["slots"][victim_slot] = challenger_id
            portfolio["challenger_queue"] = queue[1:]

            for row in registry:
                if row["experiment_id"] == victim_id:
                    row["status"] = "replaced"
                    row["slot"] = None
                if row["experiment_id"] == challenger_id:
                    row["status"] = "active"
                    row["slot"] = victim_slot

            _append_jsonl(EVALUATIONS_FILE, {
                "timestamp": _now_iso(),
                "event": "forced_replacement",
                "challenger_id": challenger_id,
                "replaced_id": victim_id,
                "slot": victim_slot,
                "challenger_srs": challenger_eval.get("srs", 0),
                "replaced_srs": victim.get("srs", 0),
            })
        else:
            _append_jsonl(EVALUATIONS_FILE, {
                "timestamp": _now_iso(),
                "event": "forced_review_no_replacement",
                "challenger_id": challenger_id,
                "reason": "no replaceable incumbent below challenger or challenger lacks edge",
            })

    # Ratchet floor using active portfolio average.
    if active_srs_values:
        avg_srs = sum(active_srs_values) / len(active_srs_values)
        previous_avg = _safe_float(portfolio.get("last_portfolio_avg_srs"), baseline)
        floor_srs = _safe_float(portfolio.get("floor_srs"), baseline)
        if avg_srs > previous_avg:
            gain = avg_srs - previous_avg
            floor_srs = floor_srs + gain * _safe_float(config.get("ratchet_fraction"), 0.25)
        portfolio["floor_srs"] = round(max(floor_srs, baseline), 4)
        portfolio["last_portfolio_avg_srs"] = round(avg_srs, 4)

    portfolio["last_evaluation"] = _now_iso()
    _save_portfolio(portfolio)
    _save_registry(registry)

    for row in eval_rows:
        _append_jsonl(EVALUATIONS_FILE, row)

    print(f"Evaluated {len(eval_rows)} experiments (lookback={args.lookback_hours}h)")
    print(f"Coherence gate: {'PASS' if coherence_ok else 'WARN'} ({coherence_reason})")
    print(f"Portfolio floor_srs: {portfolio.get('floor_srs')}")
    if args.json:
        print(json.dumps({
            "portfolio": portfolio,
            "evaluations": eval_rows,
        }, indent=2))
    else:
        for row in eval_rows:
            print(
                f"- {row['experiment_id']} [{row.get('slot') or '-'}] "
                f"decision={row['decision']} srs={row['srs']:.3f} attempts={row['attempts']} "
                f"delta={row['delta']:.2%}"
            )


def cmd_status(args):
    portfolio = _load_portfolio()
    registry = _load_registry()
    rows = sorted(registry, key=lambda x: x.get("created_at", ""))

    if args.json:
        print(json.dumps({"portfolio": portfolio, "registry": rows}, indent=2))
        return

    print("EXPERIMENT PORTFOLIO STATUS")
    print("=" * 60)
    print(f"Baseline SRS: {portfolio.get('baseline_srs')}")
    print(f"Floor SRS: {portfolio.get('floor_srs')}")
    print(f"Last Eval: {portfolio.get('last_evaluation')}")
    print("Slots:")
    for slot in ("A", "B", "C"):
        print(f"  {slot}: {portfolio['slots'].get(slot)}")
    print(f"Challenger Queue: {portfolio.get('challenger_queue', [])}")
    print()
    print("Experiments:")
    for row in rows:
        print(
            f"- {row['experiment_id']} [{row.get('objective_family')}] "
            f"status={row.get('status')} slot={row.get('slot')} "
            f"last_decision={row.get('last_decision')}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Experiment Portfolio — 3-slot dynamic experiment governance for Zode"
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize portfolio state")
    p_init.add_argument("--reset", action="store_true", help="Reset existing state")

    p_reg = sub.add_parser("register", help="Register an experiment")
    p_reg.add_argument("--experiment-id", help="Explicit experiment ID")
    p_reg.add_argument("--hypothesis-id", help="Linked hypothesis ID")
    p_reg.add_argument("--objective-family", required=True, choices=sorted(VALID_FAMILIES))
    p_reg.add_argument("--variant-id", required=True, help="Variant label (control/A/B/...)")
    p_reg.add_argument("--notes", help="Optional notes")

    p_eval = sub.add_parser("evaluate", help="Evaluate experiments and apply portfolio logic")
    p_eval.add_argument("--lookback-hours", type=int, default=24)
    p_eval.add_argument("--json", action="store_true")

    p_status = sub.add_parser("status", help="Show portfolio status")
    p_status.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "register":
        cmd_register(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
