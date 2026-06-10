#!/usr/bin/env python3
"""
End-to-end Sentience CRM enrichment pipeline.

Stages:
  1. Pull — fetch raw memories from Sentience API (via pull_memories)
  2. Normalize — convert to canonical event schema
  3. Classify — bucket events by relevance domain
  4. Dedup — noise suppression, adjacency collapse, cross-source merge
  5. Extract — pull typed relationship signals from clusters
  6. Resolve — identity-resolve entities against local contact index
  7. Project — route through guardrails and write to projection store

CLI:
  python3 pipeline.py --start 2026-04-08T00:00:00Z --end 2026-04-09T00:00:00Z --dry-run
  python3 pipeline.py --start 2026-04-08T00:00:00Z --end 2026-04-09T00:00:00Z
  python3 pipeline.py --start 2026-04-08T00:00:00Z --end 2026-04-09T00:00:00Z --stats-only
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import os
import requests

sys.path.insert(0, str(Path(__file__).parent))

from classify_events import LayeredClassifier
from dedup_consolidate import dedup_consolidate, adapt_raw_feed_event
from extract_signals import extract_signals, adapt_raw_activity, RelationshipSignal
from guardrail_engine import GuardrailEngine
from identity_resolver import IdentityResolver
from normalize import normalize
from projection_ledger import ProjectionLedger
from projection_store import ProjectionStore
from projection_writer import ProjectionWriter, ProjectionBatch

SENTIENCE_API_URL = "https://audiosummarizer-production.up.railway.app/v1/memories"
SENTIENCE_API_KEY = os.environ.get("SENTIENCE_API_KEY")
CONTACT_INDEX_PATH = "Skills/sentience-sync/data/local_contact_index.json"


def _parse_iso(ts: str) -> datetime:
    text = ts.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


class PipelineStats:
    def __init__(self) -> None:
        self.started_at: str = ""
        self.finished_at: str = ""
        self.raw_memories: int = 0
        self.normalized_events: int = 0
        self.classified_events: int = 0
        self.dedup_input: int = 0
        self.dedup_output: int = 0
        self.noise_suppressed: int = 0
        self.signals_extracted: int = 0
        self.signals_by_type: dict[str, int] = {}
        self.resolutions_attempted: int = 0
        self.projection_total: int = 0
        self.projection_auto_written: int = 0
        self.projection_review_queued: int = 0
        self.projection_skipped: int = 0
        self.projection_replay_blocked: int = 0
        self.projection_errors: int = 0
        self.stage_durations: dict[str, float] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "raw_memories": self.raw_memories,
            "normalized_events": self.normalized_events,
            "classified_events": self.classified_events,
            "dedup_input": self.dedup_input,
            "dedup_output": self.dedup_output,
            "noise_suppressed": self.noise_suppressed,
            "signals_extracted": self.signals_extracted,
            "signals_by_type": self.signals_by_type,
            "resolutions_attempted": self.resolutions_attempted,
            "projection_total": self.projection_total,
            "projection_auto_written": self.projection_auto_written,
            "projection_review_queued": self.projection_review_queued,
            "projection_skipped": self.projection_skipped,
            "projection_replay_blocked": self.projection_replay_blocked,
            "projection_errors": self.projection_errors,
            "stage_durations": self.stage_durations,
        }


def run_pipeline(
    *,
    start: str,
    end: str,
    dry_run: bool = False,
    stats_only: bool = False,
    db_path: str | None = None,
    contact_index_path: str = CONTACT_INDEX_PATH,
    feed_path: str | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    stats = PipelineStats()
    stats.started_at = datetime.now(timezone.utc).isoformat()

    start_dt = _parse_iso(start)
    end_dt = _parse_iso(end)

    store = ProjectionStore(db_path) if db_path else ProjectionStore()
    ledger = ProjectionLedger()
    engine = GuardrailEngine(ledger=ledger)
    writer = ProjectionWriter(store=store, ledger=ledger, engine=engine, dry_run=dry_run)

    # ── Stage 1: Pull / Load ────────────────────────────────────────
    t0 = time.monotonic()

    if feed_path:
        raw_memories = _load_feed_file(feed_path, start_dt, end_dt)
    else:
        raw_memories = _pull_from_sentience(start, end)

    stats.raw_memories = len(raw_memories)
    stats.stage_durations["pull"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(f"[pull] {stats.raw_memories} raw memories", file=sys.stderr)

    if not raw_memories:
        stats.finished_at = datetime.now(timezone.utc).isoformat()
        return _build_output(stats, [], stats_only)

    # ── Stage 2: Normalize ──────────────────────────────────────────
    t0 = time.monotonic()
    normalized = []
    for mem in raw_memories:
        event = normalize(mem)
        if event is not None:
            normalized.append(event)
        else:
            adapted = adapt_raw_feed_event(mem) if "app" in mem else None
            if adapted:
                normalized.append(adapted)

    stats.normalized_events = len(normalized)
    stats.stage_durations["normalize"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(f"[normalize] {stats.normalized_events} events", file=sys.stderr)

    if not normalized:
        stats.finished_at = datetime.now(timezone.utc).isoformat()
        return _build_output(stats, [], stats_only)

    # ── Stage 3: Classify ───────────────────────────────────────────
    t0 = time.monotonic()
    classifier = LayeredClassifier()
    classified = []
    for event in normalized:
        result = classifier.classify(event)
        event["_classification"] = classifier.to_dict(result)
        event["_classified_bucket"] = result.bucket
        event["_classified_confidence"] = result.confidence
        classified.append(event)

    stats.classified_events = len(classified)
    stats.stage_durations["classify"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(f"[classify] {stats.classified_events} events classified", file=sys.stderr)

    # ── Stage 4: Dedup ──────────────────────────────────────────────
    t0 = time.monotonic()
    dedup_result = dedup_consolidate(classified)
    clusters = dedup_result["clusters"]

    stats.dedup_input = dedup_result["stats"]["input_count"]
    stats.dedup_output = dedup_result["stats"]["output_count"]
    stats.noise_suppressed = dedup_result["stats"]["noise_suppressed"]
    stats.stage_durations["dedup"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(
            f"[dedup] {stats.dedup_input} → {stats.dedup_output} "
            f"({stats.noise_suppressed} noise suppressed)",
            file=sys.stderr,
        )

    if not clusters:
        stats.finished_at = datetime.now(timezone.utc).isoformat()
        return _build_output(stats, [], stats_only)

    # ── Stage 5: Extract signals ────────────────────────────────────
    t0 = time.monotonic()
    all_signals: list[dict[str, Any]] = []
    for cluster in clusters:
        primary = cluster.get("primary_event", {})
        signals = extract_signals(primary)
        for sig in signals:
            sig_dict = sig.to_dict()
            sig_dict["_cluster_id"] = cluster.get("cluster_id", "")
            sig_dict["_source_memory_ids"] = cluster.get("source_memory_ids", [])
            all_signals.append(sig_dict)

    stats.signals_extracted = len(all_signals)
    for sig in all_signals:
        st = sig.get("signal_type", "unknown")
        stats.signals_by_type[st] = stats.signals_by_type.get(st, 0) + 1
    stats.stage_durations["extract"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(f"[extract] {stats.signals_extracted} signals: {stats.signals_by_type}", file=sys.stderr)

    if not all_signals:
        stats.finished_at = datetime.now(timezone.utc).isoformat()
        return _build_output(stats, [], stats_only)

    # ── Stage 6: Identity resolution ────────────────────────────────
    t0 = time.monotonic()
    resolver = _init_resolver(contact_index_path)
    pairs: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []

    for signal in all_signals:
        entities = signal.get("extracted_entities", {})
        if resolver:
            resolutions_raw = resolver.resolve_entities(entities)
            resolutions = [r.to_dict() for r in resolutions_raw]
        else:
            resolutions = _stub_resolutions(entities)
        stats.resolutions_attempted += len(resolutions)
        pairs.append((signal, resolutions))

    stats.stage_durations["resolve"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(f"[resolve] {stats.resolutions_attempted} resolutions for {len(pairs)} signals", file=sys.stderr)

    # ── Stage 7: Project ────────────────────────────────────────────
    t0 = time.monotonic()
    batch = writer.process_batch(pairs)

    stats.projection_total = batch.total
    stats.projection_auto_written = batch.auto_written
    stats.projection_review_queued = batch.review_queued
    stats.projection_skipped = batch.skipped
    stats.projection_replay_blocked = batch.replay_blocked
    stats.projection_errors = batch.errors
    stats.stage_durations["project"] = round(time.monotonic() - t0, 3)

    if verbose:
        print(
            f"[project] {batch.auto_written} written, "
            f"{batch.review_queued} queued, "
            f"{batch.replay_blocked} replay-blocked, "
            f"{batch.skipped} skipped, "
            f"{batch.errors} errors",
            file=sys.stderr,
        )

    stats.finished_at = datetime.now(timezone.utc).isoformat()
    return _build_output(stats, batch.results, stats_only)


def _load_feed_file(path: str, start_dt: datetime, end_dt: datetime) -> list[dict[str, Any]]:
    memories: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = obj.get("timestamp", "")
            if ts_str:
                try:
                    ts = _parse_iso(ts_str)
                    if ts < start_dt or ts > end_dt:
                        continue
                except (ValueError, TypeError):
                    pass
            memories.append(obj)
    return memories


def _pull_from_sentience(start: str, end: str) -> list[dict[str, Any]]:
    if not SENTIENCE_API_KEY:
        print("[pull] SENTIENCE_API_KEY not set, skipping API pull", file=sys.stderr)
        return []
    try:
        resp = requests.get(
            SENTIENCE_API_URL,
            headers={"Authorization": f"Bearer {SENTIENCE_API_KEY}"},
            params={"start": start, "end": end},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("memories", [])
    except Exception as exc:
        print(f"[pull] Sentience API error: {exc}", file=sys.stderr)
        return []


def _init_resolver(index_path: str) -> IdentityResolver | None:
    try:
        return IdentityResolver(index_path=index_path)
    except Exception as exc:
        print(f"[resolve] Could not load local contact index: {exc}", file=sys.stderr)
        return None


def _stub_resolutions(entities: dict[str, Any]) -> list[dict[str, Any]]:
    stubs = []
    for person in entities.get("people", []):
        stubs.append({
            "entity_type": "person",
            "query": person if isinstance(person, str) else str(person),
            "tier": "unmatched",
            "local_record_id": None,
            "confidence_score": 0.0,
            "candidates": [],
            "reason": "no resolver available",
        })
    for company in entities.get("companies", []):
        stubs.append({
            "entity_type": "company",
            "query": company if isinstance(company, str) else str(company),
            "tier": "unmatched",
            "local_record_id": None,
            "confidence_score": 0.0,
            "candidates": [],
            "reason": "no resolver available",
        })
    return stubs


def _build_output(
    stats: PipelineStats,
    results: list[Any],
    stats_only: bool,
) -> dict[str, Any]:
    output: dict[str, Any] = {"stats": stats.to_dict()}
    if not stats_only:
        output["results"] = [
            r.to_dict() if hasattr(r, "to_dict") else r
            for r in results
        ]
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="End-to-end Sentience CRM enrichment pipeline."
    )
    parser.add_argument(
        "--start",
        required=True,
        help="Window start (ISO 8601, e.g. 2026-04-08T00:00:00Z).",
    )
    parser.add_argument(
        "--end",
        required=True,
        help="Window end (ISO 8601, e.g. 2026-04-09T00:00:00Z).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written without writing.",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print pipeline statistics only (no per-result detail).",
    )
    parser.add_argument(
        "--feed",
        help="Path to local JSONL feed file (skip Sentience API pull).",
    )
    parser.add_argument(
        "--db",
        help="Override projection store DB path.",
    )
    parser.add_argument(
        "--contact-index",
        default=CONTACT_INDEX_PATH,
        help="Path to local contact index JSON.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-stage progress to stderr.",
    )
    args = parser.parse_args()

    output = run_pipeline(
        start=args.start,
        end=args.end,
        dry_run=args.dry_run,
        stats_only=args.stats_only,
        db_path=args.db,
        contact_index_path=args.contact_index,
        feed_path=args.feed,
        verbose=args.verbose,
    )

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
