#!/usr/bin/env python3
"""Tests for promotion-task coupling module."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

_workspace_root = Path(__file__).parent.parent.parent.parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

from N5.task_system import promotion_task_coupling as ptc


class PromotionTaskCouplingTests(unittest.TestCase):
    """Behavioral tests for policy routing and report generation."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmpdir.name)
        self.coupling_db = self.base / "task_coupling.db"
        self.policy_path = self.base / "policy.json"
        self.switch_path = self.base / "switch.json"

        policy = {
            "default_domain": "Careerspan",
            "default_project": "Relationship Intelligence OS",
            "rollback_switch_path": str(self.switch_path),
            "gates": {
                "auto_launch_min_score": 75,
                "review_min_score": 50,
                "min_confidence": 0.72,
                "min_commitment_clarity_for_auto": 12,
                "hard_override_auto_reasons": ["explicit_promise", "named_deliverable"],
                "allow_candidate_types": ["deliverable_record", "org_delta"],
                "deny_statuses": ["duplicate", "blocked", "archived"],
            },
        }
        self.policy_path.write_text(json.dumps(policy))
        self.switch_path.write_text(json.dumps({"enabled": True}))

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_routing_decision_auto_launch(self) -> None:
        event = {
            "event_id": "pe_test1",
            "candidate_type": "deliverable_record",
            "score": 87,
            "score_breakdown": {"commitment_clarity": 15},
            "tier": "A",
            "status": "promoted",
            "hard_override": {"applied": True, "reason": "explicit_promise"},
            "confidence": {"overall": 0.91},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=True)
        self.assertEqual(decision.action, "auto_launch")

    def test_routing_decision_review_required_for_low_confidence(self) -> None:
        event = {
            "event_id": "pe_test2",
            "candidate_type": "deliverable_record",
            "score": 90,
            "score_breakdown": {"commitment_clarity": 15},
            "tier": "A",
            "status": "promoted",
            "confidence": {"overall": 0.3},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=True)
        self.assertEqual(decision.action, "review_required")

    def test_routing_decision_blocked_when_switch_disabled(self) -> None:
        event = {
            "event_id": "pe_test3",
            "candidate_type": "deliverable_record",
            "score": 95,
            "score_breakdown": {"commitment_clarity": 18},
            "tier": "A",
            "status": "promoted",
            "confidence": {"overall": 0.98},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=False)
        self.assertEqual(decision.action, "blocked")
        self.assertEqual(decision.reason, "rollback_switch_disabled")

    def test_routing_decision_denied_status_case_insensitive(self) -> None:
        event = {
            "event_id": "pe_test4",
            "candidate_type": "Deliverable_Record",
            "score": 95,
            "score_breakdown": {"commitment_clarity": 18},
            "tier": "A",
            "status": "Archived",
            "confidence": {"overall": 0.98},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=True)
        self.assertEqual(decision.action, "no_task")
        self.assertTrue(decision.reason.startswith("status_denied:"))

    def test_pilot_report_fp_fn(self) -> None:
        with patch.object(ptc, "COUPLING_DB_PATH", self.coupling_db):
            ptc.ensure_coupling_db()
            with sqlite3.connect(self.coupling_db) as conn:
                conn.execute(
                    """
                    INSERT INTO task_coupling_events (
                        run_id, idempotency_key, event_id, meeting_id, candidate_type,
                        decision_action, decision_reason, dry_run, processed_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("run_x", "idem_1", "pe_1", "mtg_1", "deliverable_record", "auto_launch", "test", 0, ptc.utc_now_iso(), "processed"),
                )
                conn.execute(
                    """
                    INSERT INTO task_coupling_events (
                        run_id, idempotency_key, event_id, meeting_id, candidate_type,
                        decision_action, decision_reason, dry_run, processed_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("run_x", "idem_2", "pe_2", "mtg_2", "deliverable_record", "review_required", "test", 0, ptc.utc_now_iso(), "processed"),
                )
                conn.commit()

            labels = self.base / "labels.jsonl"
            labels.write_text(
                '\n'.join(
                    [
                        json.dumps({"idempotency_key": "idem_1", "expected_action": "review_required"}),
                        json.dumps({"idempotency_key": "idem_2", "expected_action": "auto_launch"}),
                    ]
                )
            )
            out = self.base / "pilot_report.json"
            exit_code = ptc.pilot_report(out, labels)
            report = json.loads(out.read_text())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["false_positive"], 1)
            self.assertEqual(report["false_negative"], 1)

    def test_routing_decision_handles_hard_overrides_object_list(self) -> None:
        event = {
            "event_id": "pe_test3",
            "candidate_type": "deliverable_record",
            "score": 40,
            "score_breakdown": {"commitment_clarity": 3},
            "tier": "A",
            "status": "promoted",
            "hard_overrides": [{"reason": "explicit_promise"}],
            "confidence": {"overall": 0.91},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=True)
        self.assertEqual(decision.action, "auto_launch")

    def test_routing_decision_handles_non_numeric_confidence(self) -> None:
        event = {
            "event_id": "pe_test4",
            "candidate_type": "deliverable_record",
            "score": 90,
            "score_breakdown": {"commitment_clarity": 15},
            "tier": "A",
            "status": "promoted",
            "confidence": {"overall": "unknown"},
        }
        policy = json.loads(self.policy_path.read_text())
        decision = ptc.routing_decision(event, policy, switch_enabled=True)
        self.assertEqual(decision.action, "review_required")

    def test_process_events_non_dry_run_and_idempotency(self) -> None:
        events = [
            {
                "event_id": "pe_auto_nondry",
                "candidate_type": "deliverable_record",
                "candidate_id": "deliv_1",
                "source_meeting_id": "mtg_1",
                "score": 90,
                "score_breakdown": {"commitment_clarity": 18},
                "tier": "A",
                "status": "promoted",
                "confidence": 0.95,
                "idempotency_key": "idem_auto",
            },
            {
                "event_id": "pe_review_nondry",
                "candidate_type": "deliverable_record",
                "candidate_id": "deliv_2",
                "source_meeting_id": "mtg_2",
                "score": 60,
                "score_breakdown": {"commitment_clarity": 8},
                "tier": "B",
                "status": "promoted",
                "confidence": 0.9,
                "idempotency_key": "idem_review",
            },
        ]
        deliverables_by_id = {
            "deliv_1": {"deliverable_id": "deliv_1", "title": "Launch plan"},
            "deliv_2": {"deliverable_id": "deliv_2", "title": "Review queue item"},
        }
        policy = json.loads(self.policy_path.read_text())
        status_sync_path = self.base / "status_sync.jsonl"
        policy["status_sync_path"] = str(status_sync_path)

        with patch.object(ptc, "COUPLING_DB_PATH", self.coupling_db):
            ptc.ensure_coupling_db()
            with patch.object(ptc, "create_task", return_value=101), patch.object(
                ptc, "get_task_by_id", return_value={"id": 101}
            ), patch.object(ptc, "capture_staged_task", return_value=202), patch.object(
                ptc, "get_staged_task_by_id", return_value={"id": 202}
            ):
                first_stats = ptc.process_events(
                    events=events,
                    deliverables_by_id=deliverables_by_id,
                    policy=policy,
                    run_id="run_first",
                    dry_run=False,
                )
                second_stats = ptc.process_events(
                    events=events,
                    deliverables_by_id=deliverables_by_id,
                    policy=policy,
                    run_id="run_second",
                    dry_run=False,
                )

        self.assertEqual(first_stats["auto_launched"], 1)
        self.assertEqual(first_stats["review_required"], 1)
        self.assertEqual(first_stats["errors"], 0)
        self.assertEqual(second_stats["skipped_idempotent"], 2)
        self.assertTrue(status_sync_path.exists())
        self.assertEqual(len(status_sync_path.read_text().strip().splitlines()), 2)

    def test_build_parser_survives_missing_policy_file(self) -> None:
        missing_policy = self.base / "missing_policy.json"
        with patch.object(ptc, "POLICY_PATH", missing_policy):
            parser = ptc.build_parser()
            args = parser.parse_args(["run"])
            self.assertEqual(args.command, "run")

    def test_toggle_switch_uses_provided_policy_path(self) -> None:
        local_policy_path = self.base / "local_policy.json"
        local_policy_path.write_text(
            json.dumps({"rollback_switch_path": str(self.switch_path)})
        )
        rc = ptc.toggle_switch("disabled", policy_path=local_policy_path)
        switch_state = json.loads(self.switch_path.read_text())
        self.assertEqual(rc, 0)
        self.assertFalse(switch_state["enabled"])


if __name__ == "__main__":
    unittest.main()
