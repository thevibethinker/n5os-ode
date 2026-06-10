"""
Projection ledger API for Sentience CRM projection workflows.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from state import ProjectionLedger as BaseProjectionLedger
from state import build_projection_id


class ProjectionLedger(BaseProjectionLedger):
    def prepare_projection(
        self,
        candidate: dict[str, Any],
        destination: str,
        *,
        action: str,
        confidence_tier: str | None = None,
        status: str = "pending",
        reason: str | None = None,
        audit_flag: bool = False,
        queue_id: str | None = None,
        local_record_id: str | None = None,
        local_write_type: str | None = None,
    ) -> dict[str, Any]:
        candidate_id = str(candidate.get("candidate_id") or candidate.get("id") or "unknown")
        replay = self.detect_replay(candidate_id, destination)
        if replay["replay_detected"]:
            existing = dict(replay["existing"] or {})
            existing["replay_detected"] = True
            existing["outcome"] = replay["outcome"]
            return existing

        entry = {
            "projection_id": build_projection_id(candidate_id, destination),
            "candidate_id": candidate_id,
            "candidate_type": candidate.get("candidate_type") or candidate.get("type") or "unknown",
            "destination": destination,
            "action": action,
            "confidence_tier": confidence_tier or candidate.get("confidence_tier") or "unknown",
            "source_event_ids": candidate.get("source_event_ids") or [],
            "local_record_id": local_record_id or candidate.get("local_record_id"),
            "local_write_type": local_write_type,
            "rollback_data": candidate.get("rollback_data"),
            "status": status,
            "queue_id": queue_id,
            "reason": reason,
            "audit_flag": audit_flag,
        }
        created, _ = self.record_projection_once(entry)
        created["replay_detected"] = False
        created["outcome"] = "prepared"
        return created

    def mark_written(
        self,
        projection_id: str,
        *,
        rollback_data: dict[str, Any],
        written_at: str | None = None,
        local_record_id: str | None = None,
        local_write_type: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        updated = super().mark_written(
            projection_id,
            rollback_data=rollback_data,
            written_at=written_at,
            local_record_id=local_record_id,
            local_write_type=local_write_type,
            reason=reason,
        )
        updated["replay_detected"] = False
        updated["outcome"] = "written"
        return updated

    def replay_status(self, candidate_id: str, destination: str) -> dict[str, Any]:
        replay = self.detect_replay(candidate_id, destination)
        result = {
            "candidate_id": candidate_id,
            "destination": destination,
            "projection_id": build_projection_id(candidate_id, destination),
            "replay_detected": replay["replay_detected"],
            "outcome": replay["outcome"],
        }
        if replay["existing"] is not None:
            result["existing"] = replay["existing"]
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or mutate the Sentience projection ledger.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check whether a candidate was already projected.")
    check_parser.add_argument("candidate_id")
    check_parser.add_argument("destination")

    prepare_parser = subparsers.add_parser("prepare", help="Register a candidate unless it is a replay.")
    prepare_parser.add_argument("candidate_json")
    prepare_parser.add_argument("destination")
    prepare_parser.add_argument("--action", required=True)
    prepare_parser.add_argument("--status", default="pending")
    prepare_parser.add_argument("--reason")
    prepare_parser.add_argument("--queue-id")
    prepare_parser.add_argument("--local-record-id")
    prepare_parser.add_argument("--local-write-type")
    prepare_parser.add_argument("--confidence-tier")
    prepare_parser.add_argument("--audit-flag", action="store_true")

    list_parser = subparsers.add_parser("list", help="List latest projections.")
    list_parser.add_argument("--destination")
    list_parser.add_argument("--status")
    list_parser.add_argument("--time-range", dest="time_range")

    written_parser = subparsers.add_parser("mark-written", help="Mark a prepared projection as written.")
    written_parser.add_argument("projection_id")
    written_parser.add_argument("--rollback-data", required=True)
    written_parser.add_argument("--written-at")
    written_parser.add_argument("--local-record-id")
    written_parser.add_argument("--local-write-type")
    written_parser.add_argument("--reason")

    rollback_parser = subparsers.add_parser("mark-rolled-back", help="Mark a projection as rolled back.")
    rollback_parser.add_argument("projection_id")
    rollback_parser.add_argument("--reason")
    rollback_parser.add_argument("--rollback-data")

    args = parser.parse_args()
    ledger = ProjectionLedger()

    if args.command == "check":
        print(json.dumps(ledger.replay_status(args.candidate_id, args.destination), indent=2))
        return 0

    if args.command == "prepare":
        candidate = json.loads(args.candidate_json)
        prepared = ledger.prepare_projection(
            candidate,
            args.destination,
            action=args.action,
            confidence_tier=args.confidence_tier,
            status=args.status,
            reason=args.reason,
            audit_flag=args.audit_flag,
            queue_id=args.queue_id,
            local_record_id=args.local_record_id,
            local_write_type=args.local_write_type,
        )
        print(json.dumps(prepared, indent=2))
        return 0

    if args.command == "list":
        projections = ledger.get_projections(
            time_range=args.time_range,
            destination=args.destination,
            status=args.status,
        )
        print(json.dumps(projections, indent=2))
        return 0

    if args.command == "mark-written":
        rollback_data = json.loads(args.rollback_data)
        updated = ledger.mark_written(
            args.projection_id,
            rollback_data=rollback_data,
            written_at=args.written_at,
            local_record_id=args.local_record_id,
            local_write_type=args.local_write_type,
            reason=args.reason,
        )
        print(json.dumps(updated, indent=2))
        return 0

    rollback_data = json.loads(args.rollback_data) if args.rollback_data else None
    updated = ledger.mark_rolled_back(args.projection_id, rollback_data=rollback_data, reason=args.reason)
    print(json.dumps(updated, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
