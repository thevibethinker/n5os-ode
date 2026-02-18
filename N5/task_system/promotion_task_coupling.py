#!/usr/bin/env python3
"""Couple relationship-intelligence promotion outputs into the task system."""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Ensure workspace root imports resolve in direct CLI usage
_workspace_root = Path(__file__).parent.parent.parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

from N5.task_system.staging import capture_staged_task, get_staged_task_by_id
from N5.task_system.task_registry import create_task, get_task_by_id


LOGGER = logging.getLogger("promotion_task_coupling")
POLICY_PATH = Path("/home/workspace/N5/config/task_coupling_policy.json")
COUPLING_DB_PATH = Path("/home/workspace/N5/task_system/task_coupling.db")


@dataclass
class CouplingDecision:
    """Decision object returned by policy routing."""

    action: str
    reason: str
    priority: str


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def read_json_file(path: Path) -> Dict[str, Any]:
    """Read a JSON file and return dict content."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise ValueError(f"Missing required file: {path}") from exc


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read JSONL records. Missing file returns empty list."""
    if not path.exists():
        LOGGER.warning("Input file does not exist: %s", path)
        return []
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL line {line_number} in {path}: {exc}") from exc
            if isinstance(parsed, dict):
                records.append(parsed)
    return records


def ensure_coupling_db() -> None:
    """Ensure coupling DB and tables exist."""
    COUPLING_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(COUPLING_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_coupling_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL UNIQUE,
                event_id TEXT NOT NULL,
                meeting_id TEXT,
                candidate_type TEXT,
                decision_action TEXT NOT NULL,
                decision_reason TEXT NOT NULL,
                task_id INTEGER,
                staged_id INTEGER,
                dry_run INTEGER NOT NULL DEFAULT 0,
                processed_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_coupling_status_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                task_state TEXT NOT NULL,
                sync_payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def parse_hard_override_reasons(event: Dict[str, Any]) -> List[str]:
    """Normalize hard override reasons across schema variants."""
    hard_override = event.get("hard_override")
    if isinstance(hard_override, dict):
        reason = hard_override.get("reason")
        return [reason] if isinstance(reason, str) and reason else []

    hard_overrides = event.get("hard_overrides")
    if isinstance(hard_overrides, list):
        normalized: List[str] = []
        for item in hard_overrides:
            if isinstance(item, dict):
                reason = item.get("reason")
                if isinstance(reason, str) and reason:
                    normalized.append(reason)
            elif isinstance(item, str) and item:
                normalized.append(item)
        return normalized
    return []


def extract_overall_confidence(event: Dict[str, Any]) -> float:
    """Extract confidence from either object or float schema variants."""
    def _safe_float(value: Any, fallback: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    confidence = event.get("confidence")
    if isinstance(confidence, dict):
        value = confidence.get("overall")
        return _safe_float(value) if value is not None else 0.0
    if isinstance(confidence, (int, float)):
        return _safe_float(confidence)
    if isinstance(confidence, str):
        return _safe_float(confidence)
    return 0.0


def extract_candidate_type(event: Dict[str, Any]) -> str:
    """Get candidate type from either canonical or legacy naming."""
    candidate_type = event.get("candidate_type")
    if candidate_type:
        return str(candidate_type)
    memory_type = event.get("memory_type")
    if memory_type:
        return str(memory_type)
    return "general_intelligence"


def extract_event_id(event: Dict[str, Any]) -> str:
    """Get event identifier from either canonical or legacy naming."""
    event_id = event.get("event_id") or event.get("promotion_id")
    if event_id:
        return str(event_id)
    return f"pe_{uuid.uuid4().hex[:8]}"


def extract_meeting_id(event: Dict[str, Any]) -> str:
    """Get meeting identifier from either canonical or legacy naming."""
    meeting_id = event.get("source_meeting_id") or event.get("meeting_id") or "unknown_meeting"
    return str(meeting_id)


def extract_idempotency_key(event: Dict[str, Any], event_id: str) -> str:
    """Get idempotency key from canonical fields or fallback to event_id."""
    provenance = event.get("provenance")
    if isinstance(provenance, dict):
        key = provenance.get("idempotency_key")
        if key:
            return str(key)
    key = event.get("idempotency_key")
    if key:
        return str(key)
    return event_id


def routing_decision(event: Dict[str, Any], policy: Dict[str, Any], switch_enabled: bool) -> CouplingDecision:
    """Apply policy gates and return final action."""
    gates = policy.get("gates", {})
    tier = str(event.get("tier", "")).upper()
    status = str(event.get("status", "unknown")).lower()
    candidate_type = extract_candidate_type(event).lower()
    try:
        score = float(event.get("score", 0))
    except (TypeError, ValueError):
        score = 0.0
    confidence = extract_overall_confidence(event)
    breakdown = event.get("score_breakdown", {}) if isinstance(event.get("score_breakdown"), dict) else {}
    try:
        commitment_clarity = float(breakdown.get("commitment_clarity", 0))
    except (TypeError, ValueError):
        commitment_clarity = 0.0
    hard_reasons = parse_hard_override_reasons(event)

    if not switch_enabled:
        return CouplingDecision("blocked", "rollback_switch_disabled", "normal")

    deny_statuses = {str(item).lower() for item in gates.get("deny_statuses", [])}
    if status in deny_statuses:
        return CouplingDecision("no_task", f"status_denied:{status}", "normal")

    allow_types = {str(item).lower() for item in gates.get("allow_candidate_types", [])}
    if allow_types and candidate_type not in allow_types:
        return CouplingDecision("no_task", f"candidate_type_not_allowed:{candidate_type}", "normal")

    if confidence < float(gates.get("min_confidence", 0.0)):
        return CouplingDecision("review_required", "low_confidence", "normal")

    if tier == "C":
        return CouplingDecision("no_task", "tier_c_archival", "normal")

    override_reasons = {str(item) for item in gates.get("hard_override_auto_reasons", [])}
    has_auto_override = any(reason in override_reasons for reason in hard_reasons)
    meets_auto_score = score >= float(gates.get("auto_launch_min_score", 75))
    meets_auto_clarity = commitment_clarity >= float(gates.get("min_commitment_clarity_for_auto", 12))

    if tier == "A" and (has_auto_override or (meets_auto_score and meets_auto_clarity)):
        return CouplingDecision("auto_launch", "tier_a_and_confident", "strategic")

    if score >= float(gates.get("review_min_score", 50)):
        return CouplingDecision("review_required", "needs_human_review", "normal")

    return CouplingDecision("no_task", "insufficient_signal", "normal")


def build_task_payload(
    event: Dict[str, Any],
    decision: CouplingDecision,
    policy: Dict[str, Any],
    deliverables_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Build task metadata payload for create/stage actions."""
    event_id = extract_event_id(event)
    candidate_type = extract_candidate_type(event)
    meeting_id = extract_meeting_id(event)
    candidate_id = str(event.get("candidate_id") or event.get("deliverable_id") or event_id)
    score = float(event.get("score", 0))
    tier = str(event.get("tier", "U"))
    confidence = extract_overall_confidence(event)

    deliverable = deliverables_by_id.get(candidate_id, {})
    title = str(deliverable.get("title") or f"[{candidate_type}] Follow-up from {meeting_id}")
    description = str(
        deliverable.get("description")
        or f"Generated from promotion event {event_id} (tier={tier}, score={score:.1f}, confidence={confidence:.2f})."
    )

    due_at: Optional[str] = None
    timeline = deliverable.get("timeline")
    if isinstance(timeline, dict):
        due_candidate = timeline.get("due_date")
        if isinstance(due_candidate, str) and due_candidate:
            due_at = f"{due_candidate}T17:00:00"

    return {
        "title": title,
        "description": description,
        "domain": str(policy.get("default_domain", "Careerspan")),
        "project": str(policy.get("default_project", "Relationship Intelligence OS")),
        "priority_bucket": decision.priority,
        "source_type": "meeting",
        "source_id": f"{meeting_id}:{event_id}",
        "due_at": due_at,
        "context": (
            f"promotion_event={event_id}; candidate_type={candidate_type}; "
            f"candidate_id={candidate_id}; decision={decision.action}; reason={decision.reason}"
        ),
    }


def find_existing_coupled_event(idempotency_key: str) -> Optional[Dict[str, Any]]:
    """Return existing coupling record for idempotency checks."""
    with sqlite3.connect(COUPLING_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT idempotency_key, event_id, decision_action, status, task_id, staged_id
            FROM task_coupling_events
            WHERE idempotency_key = ?
            """,
            (idempotency_key,),
        ).fetchone()
        return dict(row) if row else None


def record_coupling_event(
    run_id: str,
    idempotency_key: str,
    event_id: str,
    meeting_id: str,
    candidate_type: str,
    decision: CouplingDecision,
    dry_run: bool,
    status: str,
    task_id: Optional[int] = None,
    staged_id: Optional[int] = None,
) -> None:
    """Persist coupling result record and verify write."""
    with sqlite3.connect(COUPLING_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO task_coupling_events (
                run_id, idempotency_key, event_id, meeting_id, candidate_type,
                decision_action, decision_reason, task_id, staged_id, dry_run,
                processed_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(idempotency_key) DO UPDATE SET
                run_id=excluded.run_id,
                decision_action=excluded.decision_action,
                decision_reason=excluded.decision_reason,
                task_id=excluded.task_id,
                staged_id=excluded.staged_id,
                dry_run=excluded.dry_run,
                processed_at=excluded.processed_at,
                status=excluded.status
            """,
            (
                run_id,
                idempotency_key,
                event_id,
                meeting_id,
                candidate_type,
                decision.action,
                decision.reason,
                task_id,
                staged_id,
                int(dry_run),
                utc_now_iso(),
                status,
            ),
        )
        conn.commit()
        verify = conn.execute(
            "SELECT id FROM task_coupling_events WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        if not verify:
            raise RuntimeError(f"Failed to verify coupling write for {idempotency_key}")


def record_status_sync(
    run_id: str,
    event_id: str,
    idempotency_key: str,
    task_state: str,
    payload: Dict[str, Any],
) -> None:
    """Persist task status sync signal for memory/graph consumers."""
    with sqlite3.connect(COUPLING_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO task_coupling_status_sync (
                run_id, event_id, idempotency_key, task_state, sync_payload, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                event_id,
                idempotency_key,
                task_state,
                json.dumps(payload),
                utc_now_iso(),
            ),
        )
        conn.commit()
        verify = conn.execute(
            """
            SELECT id FROM task_coupling_status_sync
            WHERE run_id = ? AND event_id = ? AND idempotency_key = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (run_id, event_id, idempotency_key),
        ).fetchone()
        if not verify:
            raise RuntimeError(f"Failed to verify status sync write for {idempotency_key}")


def append_status_jsonl(status_sync_path: Path, payload: Dict[str, Any]) -> None:
    """Append status sync payload to JSONL for downstream consumers."""
    status_sync_path.parent.mkdir(parents=True, exist_ok=True)
    with status_sync_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_deliverables_by_id(path: Path) -> Dict[str, Dict[str, Any]]:
    """Build deliverable lookup map from JSONL records."""
    result: Dict[str, Dict[str, Any]] = {}
    for record in read_jsonl(path):
        deliverable_id = record.get("deliverable_id")
        if isinstance(deliverable_id, str) and deliverable_id:
            result[deliverable_id] = record
    return result


def process_events(
    events: Iterable[Dict[str, Any]],
    deliverables_by_id: Dict[str, Dict[str, Any]],
    policy: Dict[str, Any],
    run_id: str,
    dry_run: bool,
) -> Dict[str, int]:
    """Main processing loop for coupling events into tasks."""
    switch_path = Path(str(policy.get("rollback_switch_path", "/home/workspace/N5/config/task_coupling_switch.json")))
    switch = read_json_file(switch_path)
    switch_enabled = bool(switch.get("enabled", True))
    status_sync_path = Path(
        str(
            policy.get(
                "status_sync_path",
                "/home/workspace/N5/data/relationship_intelligence/task_coupling_status.jsonl",
            )
        )
    )

    stats = {
        "events_total": 0,
        "auto_launched": 0,
        "review_required": 0,
        "no_task": 0,
        "blocked": 0,
        "skipped_idempotent": 0,
        "errors": 0,
    }

    for event in events:
        stats["events_total"] += 1
        event_id = extract_event_id(event)
        meeting_id = extract_meeting_id(event)
        candidate_type = extract_candidate_type(event)
        idempotency_key = extract_idempotency_key(event, event_id)

        existing = find_existing_coupled_event(idempotency_key) if not dry_run else None
        if existing:
            LOGGER.info("Skipping idempotent event %s (%s)", event_id, idempotency_key)
            stats["skipped_idempotent"] += 1
            continue

        try:
            decision = routing_decision(event, policy, switch_enabled)
            payload = build_task_payload(event, decision, policy, deliverables_by_id)

            task_id: Optional[int] = None
            staged_id: Optional[int] = None
            status = "processed"

            if decision.action == "auto_launch":
                if dry_run:
                    stats["auto_launched"] += 1
                else:
                    task_id = create_task(
                        title=payload["title"],
                        description=payload["description"],
                        domain=payload["domain"],
                        project=payload["project"],
                        priority_bucket=payload["priority_bucket"],
                        source_type=payload["source_type"],
                        source_id=payload["source_id"],
                        due_at=payload["due_at"],
                        plan_json={
                            "origin": "promotion_task_coupling",
                            "event_id": event_id,
                            "candidate_type": candidate_type,
                            "decision_reason": decision.reason,
                        },
                    )
                    verification = get_task_by_id(task_id)
                    if not verification:
                        raise RuntimeError(f"Task creation verification failed for event {event_id}")
                    stats["auto_launched"] += 1

            elif decision.action == "review_required":
                if dry_run:
                    stats["review_required"] += 1
                else:
                    staged_id = capture_staged_task(
                        title=payload["title"],
                        source_type=payload["source_type"],
                        source_id=payload["source_id"],
                        context=payload["context"],
                        description=payload["description"],
                        suggestions={
                            "domain": payload["domain"],
                            "project": payload["project"],
                            "priority": payload["priority_bucket"],
                        },
                    )
                    verification = get_staged_task_by_id(staged_id)
                    if not verification:
                        raise RuntimeError(f"Staged task verification failed for event {event_id}")
                    stats["review_required"] += 1

            elif decision.action == "blocked":
                stats["blocked"] += 1
                status = "blocked"
            else:
                stats["no_task"] += 1
                status = "no_task"

            sync_payload = {
                "event_id": event_id,
                "meeting_id": meeting_id,
                "candidate_type": candidate_type,
                "decision_action": decision.action,
                "decision_reason": decision.reason,
                "task_id": task_id,
                "staged_id": staged_id,
                "status": status,
                "timestamp": utc_now_iso(),
            }

            if not dry_run:
                record_coupling_event(
                    run_id=run_id,
                    idempotency_key=idempotency_key,
                    event_id=event_id,
                    meeting_id=meeting_id,
                    candidate_type=candidate_type,
                    decision=decision,
                    dry_run=False,
                    status=status,
                    task_id=task_id,
                    staged_id=staged_id,
                )
                record_status_sync(
                    run_id=run_id,
                    event_id=event_id,
                    idempotency_key=idempotency_key,
                    task_state=decision.action,
                    payload=sync_payload,
                )
                append_status_jsonl(status_sync_path, sync_payload)
            else:
                LOGGER.info(
                    "[DRY RUN] %s -> %s (%s)",
                    event_id,
                    decision.action,
                    decision.reason,
                )

        except (sqlite3.DatabaseError, ValueError, RuntimeError) as exc:
            LOGGER.error("Event processing failed: %s", exc)
            stats["errors"] += 1

    return stats


def write_report(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON report and verify the write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    if not path.exists():
        raise RuntimeError(f"Failed to verify report write at {path}")


def toggle_switch(state: str, policy_path: Path = POLICY_PATH) -> int:
    """Set rollback switch enabled/disabled."""
    policy = read_json_file(policy_path)
    switch_path = Path(str(policy.get("rollback_switch_path", "/home/workspace/N5/config/task_coupling_switch.json")))
    value = state == "enabled"
    payload = {
        "enabled": value,
        "updated_at": utc_now_iso(),
        "updated_by": "promotion_task_coupling.py",
    }
    switch_path.write_text(json.dumps(payload, indent=2))
    verify = read_json_file(switch_path)
    if bool(verify.get("enabled")) != value:
        LOGGER.error("Failed to verify switch update")
        return 1
    LOGGER.info("Rollback switch set to %s", state)
    return 0


def pilot_report(output_path: Path, label_path: Optional[Path] = None) -> int:
    """Generate pilot report with false-positive/false-negative counts."""
    ensure_coupling_db()
    with sqlite3.connect(COUPLING_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT event_id, idempotency_key, decision_action, status
            FROM task_coupling_events
            ORDER BY id ASC
            """
        ).fetchall()

    decisions = [dict(row) for row in rows]
    labels: Dict[str, str] = {}
    if label_path:
        for record in read_jsonl(label_path):
            key = record.get("idempotency_key") or record.get("event_id")
            expected = record.get("expected_action")
            if isinstance(key, str) and isinstance(expected, str):
                labels[key] = expected

    false_positive = 0
    false_negative = 0
    compared = 0
    for decision in decisions:
        key = str(decision.get("idempotency_key"))
        expected = labels.get(key)
        if not expected:
            continue
        compared += 1
        actual = str(decision.get("decision_action"))
        if actual == "auto_launch" and expected != "auto_launch":
            false_positive += 1
        if actual != "auto_launch" and expected == "auto_launch":
            false_negative += 1

    report = {
        "generated_at": utc_now_iso(),
        "total_decisions": len(decisions),
        "labeled_comparisons": compared,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "notes": "FP/FN are measured only on labeled records.",
    }
    write_report(output_path, report)
    LOGGER.info("Pilot report written: %s", output_path)
    return 0


def run_coupling(args: argparse.Namespace) -> int:
    """CLI entrypoint for coupling run mode."""
    policy = read_json_file(Path(args.policy))
    ensure_coupling_db()
    run_id = args.run_id or f"run_{uuid.uuid4().hex[:10]}"
    events_path = Path(args.promotion_events)
    deliverables_path = Path(args.deliverables)
    report_path = Path(args.report_out)

    events = read_jsonl(events_path)
    deliverables_by_id = load_deliverables_by_id(deliverables_path)
    stats = process_events(
        events=events,
        deliverables_by_id=deliverables_by_id,
        policy=policy,
        run_id=run_id,
        dry_run=args.dry_run,
    )

    output = {
        "run_id": run_id,
        "dry_run": args.dry_run,
        "inputs": {
            "promotion_events": str(events_path),
            "deliverable_records": str(deliverables_path),
        },
        "stats": stats,
        "generated_at": utc_now_iso(),
    }
    write_report(report_path, output)
    LOGGER.info("Run report written: %s", report_path)
    LOGGER.info("Stats: %s", json.dumps(stats))
    return 0 if stats["errors"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    """Create CLI parser."""
    try:
        defaults = read_json_file(POLICY_PATH)
    except ValueError as exc:
        LOGGER.warning("Using empty parser defaults because policy could not be loaded: %s", exc)
        defaults = {}
    input_defaults = defaults.get("input_defaults", {})

    parser = argparse.ArgumentParser(
        description="Map promotion events into auto-launched tasks or review-queue staged tasks."
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute event-to-task coupling")
    run_parser.add_argument(
        "--policy",
        default=str(POLICY_PATH),
        help="Policy JSON path",
    )
    run_parser.add_argument(
        "--promotion-events",
        default=str(input_defaults.get("promotion_events_path", "")),
        help="Promotion events JSONL path",
    )
    run_parser.add_argument(
        "--deliverables",
        default=str(input_defaults.get("deliverable_records_path", "")),
        help="Deliverable records JSONL path",
    )
    run_parser.add_argument(
        "--report-out",
        default="/home/workspace/N5/task_system/reports/task_coupling_run_report.json",
        help="Run report output JSON path",
    )
    run_parser.add_argument(
        "--run-id",
        default="",
        help="Optional deterministic run id",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate all decisions without writing tasks, coupling DB rows, or status sync files",
    )

    switch_parser = subparsers.add_parser("toggle", help="Set rollback switch state")
    switch_parser.add_argument(
        "--policy",
        default=str(POLICY_PATH),
        help="Policy JSON path",
    )
    switch_parser.add_argument(
        "--state",
        required=True,
        choices=["enabled", "disabled"],
        help="Switch state",
    )
    switch_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended switch action without writing",
    )

    pilot_parser = subparsers.add_parser("pilot-report", help="Generate pilot FP/FN report")
    pilot_parser.add_argument(
        "--output",
        default="/home/workspace/N5/task_system/reports/task_coupling_pilot_report.json",
        help="Pilot report output path",
    )
    pilot_parser.add_argument(
        "--labels",
        default="",
        help="Optional labeled expectations JSONL path",
    )
    pilot_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute metrics only and still write report",
    )

    return parser


def main() -> int:
    """Main CLI wrapper with explicit exit codes."""
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        if args.command == "run":
            return run_coupling(args)
        if args.command == "toggle":
            if args.dry_run:
                LOGGER.info("[DRY RUN] Would set rollback switch to %s", args.state)
                return 0
            return toggle_switch(args.state, policy_path=Path(args.policy))
        if args.command == "pilot-report":
            label_path = Path(args.labels) if args.labels else None
            return pilot_report(Path(args.output), label_path=label_path)
        LOGGER.error("Unknown command: %s", args.command)
        return 1
    except (ValueError, RuntimeError, sqlite3.DatabaseError) as exc:
        LOGGER.error("Fatal error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
