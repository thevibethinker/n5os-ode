"""
Zo2Zo — Parent Link Protocol

Structured escalation to parent Zo instance.
Prepares escalation requests (does not send — rice-integration wires the actual API call).
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def prepare_escalation(
    summary: str,
    context: dict | None = None,
    options: list | None = None,
    recommendation: str | None = None,
) -> dict:
    """
    Package an escalation request for the parent instance.

    Returns:
        EscalationRequest dict with: message, decision_id, parent_instance, context, options.
    """
    cfg = _load_config()
    parent = cfg.get("parent_instance")
    decision_id = str(uuid.uuid4())

    # Format message
    msg_parts = [f"Escalation from child office:\n\n**Summary:** {summary}"]
    if context:
        ctx_str = "\n".join(f"  - {k}: {v}" for k, v in context.items())
        msg_parts.append(f"\n**Context:**\n{ctx_str}")
    if options:
        opt_str = "\n".join(f"  {i+1}. {o}" for i, o in enumerate(options))
        msg_parts.append(f"\n**Options:**\n{opt_str}")
    if recommendation:
        msg_parts.append(f"\n**Recommendation:** {recommendation}")

    message = "\n".join(msg_parts)

    # Create decision in memory if available
    try:
        from Zoffice.capabilities.memory.decision_queue import create_decision
        create_decision(
            summary=summary,
            origin_employee="zo2zo-parent-link",
            full_context=context,
            options=options,
            recommendation=recommendation,
        )
    except Exception:
        pass

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="zo2zo",
            employee=None,
            action="parent_escalation_prepared",
            metadata={"decision_id": decision_id, "parent": parent, "summary": summary},
        )
    except Exception:
        pass

    return {
        "message": message,
        "decision_id": decision_id,
        "parent_instance": parent,
        "context": context,
        "options": options,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def parse_response(response_text: str) -> dict:
    """Extract resolution from parent response."""
    return {
        "resolution": response_text.strip(),
        "parsed_at": datetime.now(timezone.utc).isoformat(),
    }
