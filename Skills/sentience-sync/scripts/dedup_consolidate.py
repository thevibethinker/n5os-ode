#!/usr/bin/env python3
"""
Cross-source dedup, adjacency collapse, and noise suppression for
canonical Sentience events (output of normalize.py).

Pipeline order:
  1. Noise suppression  — mark low-signal events SKIP
  2. Adjacency dedup    — collapse same-source near-identical frames
  3. Cross-source merge — merge events from different sources describing
                          the same real-world interaction

Input:  list of canonical events (from normalize.py or raw activity feed)
Output: list of EventCluster dicts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

ADJACENCY_WINDOW_SEC = 300  # 5 minutes
CROSS_SOURCE_WINDOW_SEC = 1800  # 30 minutes
ADJACENCY_SIMILARITY_THRESHOLD = 0.80
CROSS_SOURCE_SIMILARITY_THRESHOLD = 0.25

NOISE_APPS = frozenset({
    "Finder",
    "Xnip Helper",
    "Preview",
    "System Preferences",
    "System Settings",
    "Activity Monitor",
    "Keychain Access",
    "Disk Utility",
    "Terminal",  # raw terminal without intent
})

NOISE_CATEGORIES = frozenset({
    "System",
    "Lock Screen",
    "Authentication",
})

BROWSING_VERBS = frozenset({
    "reviewing",
    "viewing",
    "reading",
    "browsing",
    "scanning",
    "scrolling",
})

ACTION_VERBS = frozenset({
    "sending",
    "replying",
    "drafting",
    "scheduling",
    "creating",
    "sharing",
    "confirming",
    "booking",
    "composing",
    "writing",
    "responding",
    "forwarding",
    "introducing",
    "initiating",
    "submitting",
    "discussing",
    "chatting",
    "emailing",
})

INBOX_TITLE_PATTERNS = [
    re.compile(r"reviewing\s+emails?\s+in\b", re.I),
    re.compile(r"scanning\s+(inbox|emails?|messages?)\b", re.I),
    re.compile(r"browsing\s+(inbox|emails?|feed)\b", re.I),
    re.compile(r"checking\s+(inbox|notifications?)\b", re.I),
]

CALENDAR_BROWSE_PATTERNS = [
    re.compile(r"viewing\s+calendar\b", re.I),
    re.compile(r"browsing\s+calendar\b", re.I),
    re.compile(r"reviewing\s+calendar\s+(view|layout)\b", re.I),
]


# ---------------------------------------------------------------------------
# Text similarity
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def word_jaccard(a: str, b: str) -> float:
    wa, wb = _tokenize(a), _tokenize(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _summary_overlap(a: str, b: str) -> float:
    return word_jaccard(a, b)


# ---------------------------------------------------------------------------
# Canonical event helpers — handle both normalize.py output and raw feed
# ---------------------------------------------------------------------------

def _get_people(event: dict) -> list[str]:
    entities = event.get("entities")
    if isinstance(entities, dict):
        return entities.get("people", [])
    return event.get("people", [])


def _get_companies(event: dict) -> list[str]:
    entities = event.get("entities")
    if isinstance(entities, dict):
        return entities.get("companies", [])
    return event.get("companies", [])


def _get_tools(event: dict) -> list[str]:
    entities = event.get("entities")
    if isinstance(entities, dict):
        return entities.get("tools", [])
    return event.get("tools", [])


def _get_app(event: dict) -> str | None:
    return event.get("app")


def _get_source_type(event: dict) -> str:
    return event.get("source_type", "desktop")


def _get_source_id(event: dict) -> str:
    return (
        event.get("source_memory_id")
        or event.get("event_id")
        or event.get("id")
        or ""
    )


def _get_summary(event: dict) -> str:
    return event.get("summary", "")


def _get_title(event: dict) -> str:
    return event.get("title", "")


def _get_significance(event: dict) -> float:
    try:
        return float(event.get("significance", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _get_category(event: dict) -> str | None:
    return event.get("category")


def _get_actions(event: dict) -> list[dict]:
    return event.get("actions", [])


def _get_timestamp(event: dict) -> datetime:
    ts = event.get("timestamp", "")
    if not ts:
        return datetime.now(timezone.utc)
    text = str(ts).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _people_overlap(a: dict, b: dict) -> bool:
    pa = {p.casefold() for p in _get_people(a)}
    pb = {p.casefold() for p in _get_people(b)}
    return bool(pa & pb)


def _people_overlap_set(a: dict, b: dict) -> set[str]:
    pa = {p.casefold() for p in _get_people(a)}
    pb = {p.casefold() for p in _get_people(b)}
    return pa & pb


# ---------------------------------------------------------------------------
# Noise suppression
# ---------------------------------------------------------------------------

def _is_noise_app(event: dict) -> str | None:
    app = _get_app(event)
    if app and app in NOISE_APPS:
        return f"noise_app:{app}"
    return None


def _is_noise_category(event: dict) -> str | None:
    cat = _get_category(event)
    if cat and cat in NOISE_CATEGORIES:
        return f"noise_category:{cat}"
    return None


def _is_inbox_scanning(event: dict) -> str | None:
    title = _get_title(event).lower()
    summary = _get_summary(event).lower()
    people = _get_people(event)
    actions = _get_actions(event)

    for pat in INBOX_TITLE_PATTERNS:
        if pat.search(title) or pat.search(summary):
            action_verbs = {a.get("verb", "").lower() for a in actions}
            if not action_verbs & ACTION_VERBS:
                return "inbox_scanning_no_action"

    if len(people) > 10:
        action_verbs = {a.get("verb", "").lower() for a in actions}
        has_action = bool(action_verbs & ACTION_VERBS)
        if not has_action:
            return f"many_people_no_action:{len(people)}"

    return None


def _is_calendar_browsing(event: dict) -> str | None:
    title = _get_title(event).lower()
    summary = _get_summary(event).lower()

    for pat in CALENDAR_BROWSE_PATTERNS:
        if pat.search(title) or pat.search(summary):
            actions = _get_actions(event)
            action_verbs = {a.get("verb", "").lower() for a in actions}
            scheduling = {"scheduling", "creating", "booking", "confirming", "rescheduling"}
            if not action_verbs & scheduling:
                return "calendar_browsing_no_scheduling"
    return None


def _is_auth_noise(event: dict) -> str | None:
    title = _get_title(event).lower()
    summary = _get_summary(event).lower()
    auth_signals = [
        "sign-in", "sign in", "log in", "login", "verifying",
        "verify your identity", "two-factor", "2fa", "authentication",
        "password", "captcha",
    ]
    for signal in auth_signals:
        if signal in title or signal in summary:
            if _get_category(event) == "Authentication":
                return "auth_page"
            people = _get_people(event)
            if len(people) == 0:
                return "auth_page_no_people"
    return None


def classify_noise(event: dict) -> str | None:
    for checker in [
        _is_noise_app,
        _is_noise_category,
        _is_auth_noise,
        _is_inbox_scanning,
        _is_calendar_browsing,
    ]:
        reason = checker(event)
        if reason:
            return reason
    return None


def suppress_noise(events: list[dict]) -> tuple[list[dict], list[dict]]:
    active = []
    suppressed = []
    for event in events:
        reason = classify_noise(event)
        if reason:
            suppressed.append({**event, "_suppression_reason": reason})
        else:
            active.append(event)
    return active, suppressed


# ---------------------------------------------------------------------------
# Adjacency dedup (same source)
# ---------------------------------------------------------------------------

def _adjacency_key(event: dict) -> str:
    app = _get_app(event) or ""
    source_type = _get_source_type(event)
    return f"{source_type}|{app}"


def dedup_adjacent(events: list[dict]) -> list[dict]:
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: _get_timestamp(e))
    clusters: list[dict] = []
    current_group: list[dict] = [sorted_events[0]]

    for event in sorted_events[1:]:
        prev = current_group[-1]
        same_key = _adjacency_key(event) == _adjacency_key(prev)
        delta = (_get_timestamp(event) - _get_timestamp(prev)).total_seconds()
        within_window = 0 <= delta <= ADJACENCY_WINDOW_SEC

        if same_key and within_window:
            sim = _summary_overlap(_get_summary(prev), _get_summary(event))
            if sim >= ADJACENCY_SIMILARITY_THRESHOLD:
                current_group.append(event)
                continue

        clusters.append(_collapse_group(current_group))
        current_group = [event]

    clusters.append(_collapse_group(current_group))
    return clusters


def _collapse_group(group: list[dict]) -> dict:
    if len(group) == 1:
        return _to_cluster(group[0])

    best = max(group, key=lambda e: _get_significance(e))
    source_ids = []
    source_types = set()
    all_people: list[str] = []
    all_companies: list[str] = []
    seen_people: set[str] = set()
    seen_companies: set[str] = set()

    for event in group:
        sid = _get_source_id(event)
        if sid:
            source_ids.append(sid)
        source_types.add(_get_source_type(event))
        for p in _get_people(event):
            key = p.casefold()
            if key not in seen_people:
                seen_people.add(key)
                all_people.append(p)
        for c in _get_companies(event):
            key = c.casefold()
            if key not in seen_companies:
                seen_companies.add(key)
                all_companies.append(c)

    cluster = _to_cluster(best)
    cluster["source_memory_ids"] = source_ids
    cluster["source_types"] = sorted(source_types)
    cluster["member_count"] = len(group)
    cluster["collapse_type"] = "adjacency"
    cluster["merged_people"] = all_people
    cluster["merged_companies"] = all_companies
    return cluster


def _to_cluster(event: dict) -> dict:
    sid = _get_source_id(event)
    return {
        "cluster_id": _cluster_id([sid]),
        "primary_event": event,
        "source_memory_ids": [sid] if sid else [],
        "source_types": [_get_source_type(event)],
        "member_count": 1,
        "collapse_type": "none",
        "status": "active",
        "suppression_reason": None,
        "merged_people": list(_get_people(event)),
        "merged_companies": list(_get_companies(event)),
    }


def _cluster_id(source_ids: list[str]) -> str:
    payload = "|".join(sorted(source_ids))
    return sha256(payload.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Cross-source consolidation
# ---------------------------------------------------------------------------

def consolidate_cross_source(clusters: list[dict]) -> list[dict]:
    if not clusters:
        return []

    sorted_clusters = sorted(
        clusters,
        key=lambda c: _get_timestamp(c["primary_event"]),
    )
    merged: list[dict] = []
    consumed: set[int] = set()

    for i, base in enumerate(sorted_clusters):
        if i in consumed:
            continue

        group = [base]
        group_idx = {i}

        for j in range(i + 1, len(sorted_clusters)):
            if j in consumed:
                continue

            candidate = sorted_clusters[j]
            base_ts = _get_timestamp(base["primary_event"])
            cand_ts = _get_timestamp(candidate["primary_event"])
            delta = abs((cand_ts - base_ts).total_seconds())

            if delta > CROSS_SOURCE_WINDOW_SEC:
                break

            if _should_cross_merge(base, candidate):
                group.append(candidate)
                group_idx.add(j)

        consumed |= group_idx

        if len(group) == 1:
            merged.append(group[0])
        else:
            merged.append(_merge_clusters(group))

    return merged


def _should_cross_merge(a: dict, b: dict) -> bool:
    a_types = set(a["source_types"])
    b_types = set(b["source_types"])
    if a_types == b_types and len(a_types) == 1 and a_types != {"desktop"}:
        return False

    ae, be = a["primary_event"], b["primary_event"]

    people_a = {p.casefold() for p in a.get("merged_people", _get_people(ae))}
    people_b = {p.casefold() for p in b.get("merged_people", _get_people(be))}
    if not (people_a & people_b):
        return False

    title_sim = _summary_overlap(_get_title(ae), _get_title(be))
    summary_sim = _summary_overlap(_get_summary(ae), _get_summary(be))
    content_sim = max(title_sim, summary_sim)

    return content_sim >= CROSS_SOURCE_SIMILARITY_THRESHOLD


_SOURCE_RICHNESS = {"gmail": 3, "calendar": 2, "desktop": 1}


def _merge_clusters(group: list[dict]) -> dict:
    all_source_ids: list[str] = []
    all_source_types: set[str] = set()
    total_members = 0
    all_people: list[str] = []
    all_companies: list[str] = []
    seen_people: set[str] = set()
    seen_companies: set[str] = set()

    for cluster in group:
        all_source_ids.extend(cluster["source_memory_ids"])
        all_source_types.update(cluster["source_types"])
        total_members += cluster["member_count"]
        for p in cluster.get("merged_people", []):
            key = p.casefold()
            if key not in seen_people:
                seen_people.add(key)
                all_people.append(p)
        for c in cluster.get("merged_companies", []):
            key = c.casefold()
            if key not in seen_companies:
                seen_companies.add(key)
                all_companies.append(c)

    primary = max(
        group,
        key=lambda c: _SOURCE_RICHNESS.get(c["source_types"][0], 0),
    )

    return {
        "cluster_id": _cluster_id(all_source_ids),
        "primary_event": primary["primary_event"],
        "source_memory_ids": all_source_ids,
        "source_types": sorted(all_source_types),
        "member_count": total_members,
        "collapse_type": "cross_source",
        "status": "active",
        "suppression_reason": None,
        "merged_people": all_people,
        "merged_companies": all_companies,
    }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def dedup_consolidate(
    events: list[dict],
    *,
    run_noise: bool = True,
    run_adjacency: bool = True,
    run_cross_source: bool = True,
) -> dict[str, Any]:
    stats = {
        "input_count": len(events),
        "noise_suppressed": 0,
        "adjacency_collapsed_from": 0,
        "adjacency_collapsed_to": 0,
        "cross_source_merged_from": 0,
        "cross_source_merged_to": 0,
        "output_count": 0,
    }

    suppressed: list[dict] = []
    if run_noise:
        active, suppressed = suppress_noise(events)
        stats["noise_suppressed"] = len(suppressed)
    else:
        active = list(events)

    if run_adjacency:
        pre_adj = len(active)
        clusters = dedup_adjacent(active)
        stats["adjacency_collapsed_from"] = pre_adj
        stats["adjacency_collapsed_to"] = len(clusters)
    else:
        clusters = [_to_cluster(e) for e in active]

    if run_cross_source:
        pre_cs = len(clusters)
        clusters = consolidate_cross_source(clusters)
        stats["cross_source_merged_from"] = pre_cs
        stats["cross_source_merged_to"] = len(clusters)

    skip_clusters = []
    for s in suppressed:
        sc = _to_cluster(s)
        sc["status"] = "skip"
        sc["suppression_reason"] = s.get("_suppression_reason")
        skip_clusters.append(sc)

    all_clusters = clusters + skip_clusters
    stats["output_count"] = len(clusters)
    stats["total_with_skipped"] = len(all_clusters)

    reduction = 0.0
    if stats["input_count"] > 0:
        reduction = 1.0 - (stats["output_count"] / stats["input_count"])
    stats["reduction_pct"] = round(reduction * 100, 1)

    return {
        "clusters": clusters,
        "skipped": skip_clusters,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Raw feed adapter — convert activity_feed.jsonl entries to canonical shape
# ---------------------------------------------------------------------------

def adapt_raw_feed_event(raw: dict) -> dict:
    return {
        "event_id": raw.get("id", ""),
        "source_type": "desktop",
        "source_memory_id": raw.get("id", ""),
        "timestamp": raw.get("timestamp", ""),
        "app": raw.get("app"),
        "window_title": raw.get("window"),
        "title": raw.get("title", ""),
        "summary": raw.get("summary", ""),
        "category": raw.get("category"),
        "significance": raw.get("significance", 0.0),
        "entities": {
            "people": raw.get("people", []),
            "companies": raw.get("companies", []),
            "tools": raw.get("tools", []),
            "urls": raw.get("urls", []),
        },
        "actions": raw.get("actions", []),
        "sentiment": raw.get("sentiment"),
        "raw_content_hash": "",
    }


def load_feed(path: str | Path) -> list[dict]:
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            events.append(adapt_raw_feed_event(raw))
    return events


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-source dedup + noise suppression for Sentience events",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to JSONL file (canonical events or raw activity feed)",
    )
    parser.add_argument(
        "--raw-feed",
        action="store_true",
        help="Input is raw activity_feed.jsonl (auto-adapt to canonical)",
    )
    parser.add_argument(
        "--no-noise",
        action="store_true",
        help="Skip noise suppression",
    )
    parser.add_argument(
        "--no-adjacency",
        action="store_true",
        help="Skip adjacency dedup",
    )
    parser.add_argument(
        "--no-cross-source",
        action="store_true",
        help="Skip cross-source consolidation",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout stats, clusters to file)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only print stats, skip cluster output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed cluster info",
    )
    args = parser.parse_args()

    input_path = args.input
    if not input_path:
        default = Path(__file__).parent.parent / "data" / "activity_feed.jsonl"
        if default.exists():
            input_path = str(default)
            args.raw_feed = True
        else:
            parser.error("No input file provided and default feed not found")

    if args.raw_feed:
        events = load_feed(input_path)
    else:
        events = []
        with open(input_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

    result = dedup_consolidate(
        events,
        run_noise=not args.no_noise,
        run_adjacency=not args.no_adjacency,
        run_cross_source=not args.no_cross_source,
    )

    stats = result["stats"]
    print("=== Dedup + Noise Suppression Stats ===")
    print(f"  Input events:            {stats['input_count']}")
    print(f"  Noise suppressed:        {stats['noise_suppressed']}")
    print(f"  Adjacency collapsed:     {stats['adjacency_collapsed_from']} → {stats['adjacency_collapsed_to']}")
    print(f"  Cross-source merged:     {stats['cross_source_merged_from']} → {stats['cross_source_merged_to']}")
    print(f"  Output active clusters:  {stats['output_count']}")
    print(f"  Reduction:               {stats['reduction_pct']}%")

    if args.verbose:
        print("\n=== Active Clusters ===")
        for c in result["clusters"]:
            pe = c["primary_event"]
            print(
                f"  [{c['collapse_type']}] {c['member_count']} events | "
                f"{_get_app(pe) or _get_source_type(pe)} | "
                f"{_get_title(pe)[:60]}"
            )
            if c["member_count"] > 1:
                print(f"    source_ids: {c['source_memory_ids']}")

        if result["skipped"]:
            print(f"\n=== Suppressed ({len(result['skipped'])}) ===")
            for c in result["skipped"][:10]:
                pe = c["primary_event"]
                print(
                    f"  [{c['suppression_reason']}] "
                    f"{_get_app(pe) or '?'} | {_get_title(pe)[:60]}"
                )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nFull output written to {args.output}")


if __name__ == "__main__":
    main()
