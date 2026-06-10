"""
Guardrail engine for Sentience CRM projection routing.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from projection_ledger import ProjectionLedger
from state import GuardrailState, build_projection_id

CONFIDENCE_ORDER = {
    "unknown": -1,
    "unmatched": 0,
    "uncertain": 1,
    "strong": 2,
    "exact": 3,
}

POLICY_MATRIX: dict[str, dict[str, dict[str, Any]]] = {
    "interaction_record": {
        "exact": {"action": "auto_write", "destination": "interactions", "audit_flag": False},
        "strong": {"action": "auto_write", "destination": "interactions", "audit_flag": True},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
    "contact_context_enrichment": {
        "exact": {"action": "auto_write", "destination": "contact_context", "audit_flag": False},
        "strong": {"action": "auto_write", "destination": "contact_context", "audit_flag": True},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
    "new_contact_creation": {
        "exact": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "strong": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
    "new_company_creation": {
        "exact": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "strong": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
    "identity_merge": {
        "exact": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "strong": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
    "semantic_memory_summary": {
        "exact": {"action": "auto_write", "destination": "semantic_memory", "audit_flag": False},
        "strong": {"action": "auto_write", "destination": "semantic_memory", "audit_flag": False},
        "uncertain": {"action": "skip", "destination": "semantic_memory", "audit_flag": False},
        "unmatched": {"action": "skip", "destination": "semantic_memory", "audit_flag": False},
    },
    "follow_up_commitment": {
        "exact": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "strong": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "uncertain": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
        "unmatched": {"action": "review_queue", "destination": "review_queue", "audit_flag": False},
    },
}


def normalize_candidate_type(candidate_type: str | None) -> str:
    raw = (candidate_type or "unknown").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "timeline_event": "interaction_record",
        "timeline": "interaction_record",
        "interaction": "interaction_record",
        "contact_enrichment": "contact_context_enrichment",
        "contact_context": "contact_context_enrichment",
        "new_contact": "new_contact_creation",
        "new_company": "new_company_creation",
        "company_enrichment": "new_company_creation",
        "identity_mutation": "identity_merge",
        "identity_creation": "identity_merge",
        "semantic_summary": "semantic_memory_summary",
        "followup": "follow_up_commitment",
        "follow_up": "follow_up_commitment",
        "commitment": "follow_up_commitment",
    }
    return aliases.get(raw, raw)


def normalize_confidence_tier(confidence_tier: str | None) -> str:
    raw = (confidence_tier or "unknown").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "high": "strong",
        "matched": "strong",
        "none": "unmatched",
    }
    normalized = aliases.get(raw, raw)
    if normalized in {"exact", "strong", "uncertain", "unmatched"}:
        return normalized
    return "unmatched" if CONFIDENCE_ORDER.get(normalized, -1) == 0 else "unknown"


def _decision(
    candidate: dict[str, Any],
    *,
    candidate_type: str,
    confidence_tier: str,
    action: str,
    destination: str,
    audit_flag: bool,
    reason: str,
    paused_override: bool = False,
) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or candidate.get("id") or "unknown")
    decision = {
        "candidate_type": candidate_type,
        "confidence_tier": confidence_tier,
        "action": action,
        "destination": destination,
        "audit_flag": audit_flag,
        "reason": reason,
        "paused_override": paused_override,
    }
    if action != "skip":
        decision["projection_id"] = build_projection_id(candidate_id, destination)
    return decision


def evaluate_candidate(candidate: dict[str, Any], *, auto_writes_paused: bool = False) -> dict[str, Any]:
    candidate_type = normalize_candidate_type(candidate.get("candidate_type") or candidate.get("type"))
    confidence_tier = normalize_confidence_tier(candidate.get("confidence_tier"))

    if auto_writes_paused:
        return _decision(
            candidate,
            candidate_type=candidate_type,
            confidence_tier=confidence_tier,
            action="review_queue",
            destination="review_queue",
            audit_flag=False,
            reason="Circuit breaker paused auto-writes; route to review queue until recalibration is confirmed.",
            paused_override=True,
        )

    policy = POLICY_MATRIX.get(candidate_type)
    if policy is None:
        return _decision(
            candidate,
            candidate_type=candidate_type,
            confidence_tier=confidence_tier,
            action="review_queue",
            destination="review_queue",
            audit_flag=False,
            reason=f"Unhandled candidate type '{candidate_type}' defaults to review queue.",
        )

    tier_key = confidence_tier if confidence_tier in policy else "unmatched"
    rule = policy[tier_key]
    return _decision(
        candidate,
        candidate_type=candidate_type,
        confidence_tier=confidence_tier,
        action=rule["action"],
        destination=rule["destination"],
        audit_flag=rule["audit_flag"],
        reason=(
            f"{candidate_type} routed via {confidence_tier} confidence policy "
            f"to {rule['action']}:{rule['destination']}."
        ),
    )


class GuardrailEngine:
    def __init__(
        self,
        ledger: ProjectionLedger | None = None,
        state: GuardrailState | None = None,
        *,
        correction_rate_threshold: float = 0.10,
        window_hours: int = 24,
    ):
        self.ledger = ledger or ProjectionLedger()
        self.state = state or self.ledger.guardrail_state
        self.correction_rate_threshold = correction_rate_threshold
        self.window_hours = window_hours

    def check_circuit_breaker(self, stderr: Any = sys.stderr) -> tuple[bool, dict[str, Any]]:
        triggered, snapshot = self.ledger.evaluate_circuit_breaker(
            correction_rate_threshold=self.correction_rate_threshold,
            window_hours=self.window_hours,
        )
        if triggered:
            print(snapshot["pause_reason"], file=stderr)
        return triggered, snapshot

    def evaluate(self, candidate: dict[str, Any], *, refresh_circuit_breaker: bool = False) -> dict[str, Any]:
        if refresh_circuit_breaker:
            self.check_circuit_breaker()
        return evaluate_candidate(candidate, auto_writes_paused=self.state.is_paused())


GuardrailPolicy = GuardrailEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Sentience CRM guardrail routing.")
    parser.add_argument("candidate_json", help="JSON object for the candidate to evaluate.")
    parser.add_argument("--respect-circuit-breaker", action="store_true")
    parser.add_argument("--correction-rate-threshold", type=float, default=0.10)
    parser.add_argument("--window-hours", type=int, default=24)
    args = parser.parse_args()

    candidate = json.loads(args.candidate_json)
    engine = GuardrailEngine(
        correction_rate_threshold=args.correction_rate_threshold,
        window_hours=args.window_hours,
    )
    decision = engine.evaluate(candidate, refresh_circuit_breaker=args.respect_circuit_breaker)
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
