#!/usr/bin/env python3
"""
Single-writer projection engine for Sentience CRM enrichment.

Takes identity-resolved, confidence-gated signal candidates and writes
them to the local SQLite projection store (interactions + contact_context).
All writes go through the guardrail engine which determines auto-write
vs review queue routing. The projection ledger ensures idempotency.

This is the ONLY module that writes to interactions/contact_context.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, __import__("os").path.dirname(__file__))

from guardrail_engine import GuardrailEngine, normalize_candidate_type, normalize_confidence_tier
from identity_resolver import IdentityResolver, Resolution
from projection_ledger import ProjectionLedger
from projection_store import ProjectionStore, utc_now_iso


SIGNAL_TO_CANDIDATE_TYPE = {
    "new_contact": "new_contact_creation",
    "renewed_contact": "interaction_record",
    "introduction": "interaction_record",
    "follow_up_commitment": "follow_up_commitment",
    "company_intelligence": "interaction_record",
    "meeting_scheduled": "interaction_record",
}

SIGNAL_TO_INTERACTION_TYPE = {
    "new_contact": "new_contact",
    "renewed_contact": "renewed_contact",
    "introduction": "introduction",
    "follow_up_commitment": "follow_up_commitment",
    "company_intelligence": "company_intelligence",
    "meeting_scheduled": "meeting_scheduled",
}


def _build_candidate_id(signal: dict[str, Any]) -> str:
    event_ids = signal.get("source_event_ids") or []
    signal_type = signal.get("signal_type", "")
    payload = f"{signal_type}:{'|'.join(sorted(event_ids))}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _build_projection_key(signal: dict[str, Any], resolutions: list[dict[str, Any]]) -> str:
    event_ids = signal.get("source_event_ids") or []
    signal_type = signal.get("signal_type", "")
    person_ids = sorted(
        r.get("local_record_id") or r.get("query", "")
        for r in resolutions
        if r.get("entity_type") == "person"
    )
    payload = f"{signal_type}:{'|'.join(sorted(event_ids))}:{'|'.join(person_ids)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _resolution_confidence_tier(resolutions: list[dict[str, Any]]) -> str:
    tier_order = {"exact": 3, "strong": 2, "uncertain": 1, "unmatched": 0}
    best = "unmatched"
    best_score = 0
    for r in resolutions:
        tier = r.get("tier", "unmatched")
        score = tier_order.get(tier, 0)
        if score > best_score:
            best_score = score
            best = tier
    return best


@dataclass
class WriteResult:
    candidate_id: str
    signal_type: str
    action: str
    destination: str
    status: str
    interaction_id: str | None = None
    review_id: int | None = None
    ledger_projection_id: str | None = None
    reason: str = ""
    skipped: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "candidate_id": self.candidate_id,
            "signal_type": self.signal_type,
            "action": self.action,
            "destination": self.destination,
            "status": self.status,
            "reason": self.reason,
            "skipped": self.skipped,
        }
        if self.interaction_id:
            d["interaction_id"] = self.interaction_id
        if self.review_id is not None:
            d["review_id"] = self.review_id
        if self.ledger_projection_id:
            d["ledger_projection_id"] = self.ledger_projection_id
        return d


@dataclass
class ProjectionBatch:
    total: int = 0
    auto_written: int = 0
    review_queued: int = 0
    skipped: int = 0
    replay_blocked: int = 0
    errors: int = 0
    results: list[WriteResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "auto_written": self.auto_written,
            "review_queued": self.review_queued,
            "skipped": self.skipped,
            "replay_blocked": self.replay_blocked,
            "errors": self.errors,
            "results": [r.to_dict() for r in self.results],
        }


class ProjectionWriter:
    def __init__(
        self,
        store: ProjectionStore | None = None,
        ledger: ProjectionLedger | None = None,
        engine: GuardrailEngine | None = None,
        *,
        dry_run: bool = False,
    ):
        self.store = store or ProjectionStore()
        self.ledger = ledger or ProjectionLedger()
        self.engine = engine or GuardrailEngine(ledger=self.ledger)
        self.dry_run = dry_run

    def process_signal(
        self,
        signal: dict[str, Any],
        resolutions: list[dict[str, Any]],
    ) -> WriteResult:
        candidate_id = _build_candidate_id(signal)
        signal_type = signal.get("signal_type", "unknown")
        candidate_type = SIGNAL_TO_CANDIDATE_TYPE.get(signal_type, "interaction_record")
        confidence_tier = _resolution_confidence_tier(resolutions)

        candidate = {
            "candidate_id": candidate_id,
            "id": candidate_id,
            "candidate_type": candidate_type,
            "type": candidate_type,
            "confidence_tier": confidence_tier,
            "source_event_ids": signal.get("source_event_ids", []),
        }

        decision = self.engine.evaluate(candidate)
        action = decision.get("action", "review_queue")
        destination = decision.get("destination", "review_queue")

        if action == "skip":
            return WriteResult(
                candidate_id=candidate_id,
                signal_type=signal_type,
                action=action,
                destination=destination,
                status="skipped",
                reason=decision.get("reason", ""),
                skipped=True,
            )

        if action == "auto_write":
            return self._auto_write(signal, resolutions, candidate, decision)

        return self._review_queue(signal, resolutions, candidate, decision)

    def _auto_write(
        self,
        signal: dict[str, Any],
        resolutions: list[dict[str, Any]],
        candidate: dict[str, Any],
        decision: dict[str, Any],
    ) -> WriteResult:
        candidate_id = candidate["candidate_id"]
        signal_type = signal.get("signal_type", "unknown")
        projection_key = _build_projection_key(signal, resolutions)
        confidence_tier = candidate.get("confidence_tier", "unmatched")

        if self.dry_run:
            return WriteResult(
                candidate_id=candidate_id,
                signal_type=signal_type,
                action="auto_write",
                destination="interactions",
                status="dry_run",
                reason="Dry run — would auto-write",
            )

        ledger_entry = self.ledger.prepare_projection(
            candidate,
            "interactions",
            action="auto_write",
            confidence_tier=confidence_tier,
            status="pending",
            reason=decision.get("reason", ""),
            audit_flag=decision.get("audit_flag", False),
        )

        if ledger_entry.get("replay_detected"):
            return WriteResult(
                candidate_id=candidate_id,
                signal_type=signal_type,
                action="auto_write",
                destination="interactions",
                status="replay_blocked",
                ledger_projection_id=ledger_entry.get("projection_id"),
                reason=f"Replay blocked: {ledger_entry.get('outcome', 'already_recorded')}",
                skipped=True,
            )

        person_ids = [
            r.get("local_record_id") or ""
            for r in resolutions
            if r.get("entity_type") == "person" and r.get("tier") != "unmatched"
        ]
        company_ids = [
            r.get("local_record_id") or ""
            for r in resolutions
            if r.get("entity_type") == "company" and r.get("tier") != "unmatched"
        ]

        interaction_type = SIGNAL_TO_INTERACTION_TYPE.get(signal_type, signal_type)
        interaction_id = candidate_id
        now = utc_now_iso()

        interaction_record = {
            "id": interaction_id,
            "candidate_id": candidate_id,
            "event_ids": signal.get("source_event_ids", []),
            "timestamp": signal.get("timestamp", now),
            "interaction_type": interaction_type,
            "summary": signal.get("context", ""),
            "person_ids": [pid for pid in person_ids if pid],
            "company_ids": [cid for cid in company_ids if cid],
            "confidence": confidence_tier,
            "projection_key": projection_key,
            "rollback_data": {
                "action": "delete",
                "table": "interactions",
                "id": interaction_id,
                "projection_key": projection_key,
            },
        }

        result = self.store.insert_interaction(interaction_record)

        if result.get("status") == "blocked":
            self.ledger.mark_rolled_back(
                ledger_entry["projection_id"],
                rollback_data={
                    "action": "none",
                    "table": "interactions",
                    "id": result.get("record_id"),
                    "projection_key": projection_key,
                },
                reason="Blocked by existing projection_key in local store",
            )
            return WriteResult(
                candidate_id=candidate_id,
                signal_type=signal_type,
                action="auto_write",
                destination="interactions",
                status="replay_blocked",
                interaction_id=result.get("record_id"),
                ledger_projection_id=ledger_entry.get("projection_id"),
                reason="Blocked by projection_key uniqueness",
                skipped=True,
            )

        rollback_data = {
            "action": "delete",
            "table": "interactions",
            "id": interaction_id,
            "projection_key": projection_key,
            "contact_context_updates": [],
        }

        self._upsert_contact_contexts(signal, resolutions, now, rollback_data)

        self.ledger.mark_written(
            ledger_entry["projection_id"],
            rollback_data=rollback_data,
        )

        return WriteResult(
            candidate_id=candidate_id,
            signal_type=signal_type,
            action="auto_write",
            destination="interactions",
            status="written",
            interaction_id=interaction_id,
            ledger_projection_id=ledger_entry.get("projection_id"),
            reason=decision.get("reason", ""),
        )

    def _upsert_contact_contexts(
        self,
        signal: dict[str, Any],
        resolutions: list[dict[str, Any]],
        timestamp: str,
        rollback_data: dict[str, Any],
    ) -> None:
        for resolution in resolutions:
            if resolution.get("entity_type") != "person":
                continue
            if resolution.get("tier") == "unmatched":
                continue

            person_id = resolution.get("local_record_id")
            if not person_id:
                continue

            existing = self.store.get_contact_context(person_id)
            prev_count = existing["interaction_count"] if existing else 0
            prev_last = existing["last_interaction_at"] if existing else None
            prev_notes = existing.get("context_notes", []) if existing else []
            if isinstance(prev_notes, str):
                try:
                    prev_notes = json.loads(prev_notes)
                except (json.JSONDecodeError, TypeError):
                    prev_notes = []

            person_name = resolution.get("query", "")
            if not person_name and resolution.get("candidates"):
                first_candidate = resolution["candidates"][0]
                person_name = first_candidate.get("name", person_id)

            context_note = {
                "signal_type": signal.get("signal_type", ""),
                "context": signal.get("context", ""),
                "timestamp": signal.get("timestamp", timestamp),
            }

            new_notes = list(prev_notes) + [context_note]

            self.store.upsert_contact_context({
                "person_id": person_id,
                "name": person_name or person_id,
                "last_interaction_at": signal.get("timestamp", timestamp),
                "interaction_count": prev_count + 1,
                "context_notes": new_notes,
                "created_at": existing["created_at"] if existing else timestamp,
                "updated_at": timestamp,
            })

            rollback_data.setdefault("contact_context_updates", []).append({
                "person_id": person_id,
                "prev_interaction_count": prev_count,
                "prev_last_interaction_at": prev_last,
                "prev_context_notes": prev_notes,
            })

    def _review_queue(
        self,
        signal: dict[str, Any],
        resolutions: list[dict[str, Any]],
        candidate: dict[str, Any],
        decision: dict[str, Any],
    ) -> WriteResult:
        candidate_id = candidate["candidate_id"]
        signal_type = signal.get("signal_type", "unknown")
        confidence_tier = candidate.get("confidence_tier", "unmatched")

        if self.dry_run:
            return WriteResult(
                candidate_id=candidate_id,
                signal_type=signal_type,
                action="review_queue",
                destination="review_queue",
                status="dry_run",
                reason="Dry run — would enqueue for review",
            )

        candidate_data = {
            "signal": signal,
            "resolutions": resolutions,
            "candidate_id": candidate_id,
            "confidence_tier": confidence_tier,
        }

        review_result = self.store.enqueue_review_item({
            "candidate_type": signal_type,
            "candidate_data": candidate_data,
            "reason": decision.get("reason", "Routed to review queue"),
            "suggested_action": f"review_{signal_type}",
            "source_event_ids": signal.get("source_event_ids", []),
        })

        self.ledger.prepare_projection(
            candidate,
            "review_queue",
            action="queued_for_review",
            confidence_tier=confidence_tier,
            status="review_pending",
            reason=decision.get("reason", ""),
            queue_id=str(review_result.get("id", "")),
        )

        return WriteResult(
            candidate_id=candidate_id,
            signal_type=signal_type,
            action="review_queue",
            destination="review_queue",
            status="queued",
            review_id=review_result.get("id"),
            reason=decision.get("reason", ""),
        )

    def process_batch(
        self,
        signals_with_resolutions: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    ) -> ProjectionBatch:
        batch = ProjectionBatch(total=len(signals_with_resolutions))

        for signal, resolutions in signals_with_resolutions:
            try:
                result = self.process_signal(signal, resolutions)
                batch.results.append(result)

                if result.skipped:
                    if result.status == "replay_blocked":
                        batch.replay_blocked += 1
                    else:
                        batch.skipped += 1
                elif result.status == "written":
                    batch.auto_written += 1
                elif result.status == "queued":
                    batch.review_queued += 1
                elif result.status == "dry_run":
                    if result.action == "auto_write":
                        batch.auto_written += 1
                    else:
                        batch.review_queued += 1
            except Exception as exc:
                batch.errors += 1
                batch.results.append(WriteResult(
                    candidate_id=_build_candidate_id(signal),
                    signal_type=signal.get("signal_type", "unknown"),
                    action="error",
                    destination="none",
                    status="error",
                    reason=str(exc),
                ))

        return batch


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project resolved signals into the local SQLite store."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="JSONL file of {signal, resolutions} pairs, or '-' for stdin.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written without writing.")
    parser.add_argument("--db", help="Override projection store DB path.")
    parser.add_argument("--summary", action="store_true", help="Print batch summary only.")
    args = parser.parse_args()

    store = ProjectionStore(args.db) if args.db else ProjectionStore()
    writer = ProjectionWriter(store=store, dry_run=args.dry_run)

    if args.input == "-":
        lines = sys.stdin.readlines()
    else:
        with open(args.input, encoding="utf-8") as f:
            lines = f.readlines()

    pairs: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        signal = obj.get("signal", obj)
        resolutions = obj.get("resolutions", [])
        pairs.append((signal, resolutions))

    batch = writer.process_batch(pairs)

    if args.summary:
        summary = {k: v for k, v in batch.to_dict().items() if k != "results"}
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(batch.to_dict(), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
