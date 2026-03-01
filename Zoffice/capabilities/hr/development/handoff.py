"""
HR — Handoff Protocol

Structured context transfer between employees.
"""

import uuid
from datetime import datetime, timezone


def prepare_handoff(
    from_employee: str,
    to_employee: str,
    conversation_summary: str,
    caller_profile: dict | None = None,
    pending_actions: list[str] | None = None,
) -> dict:
    """
    Package a handoff with all context for the receiving employee.

    Returns:
        HandoffPackage dict.
    """
    handoff_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    package = {
        "handoff_id": handoff_id,
        "from_employee": from_employee,
        "to_employee": to_employee,
        "conversation_summary": conversation_summary,
        "caller_profile": caller_profile or {},
        "pending_actions": pending_actions or [],
        "timestamp": now,
    }

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="hr",
            employee=from_employee,
            action="handoff_prepared",
            metadata={
                "handoff_id": handoff_id,
                "from": from_employee,
                "to": to_employee,
            },
        )
    except Exception:
        pass

    return package


def format_handoff_message(package: dict) -> str:
    """Render a HandoffPackage as a readable message."""
    lines = [
        f"**Handoff from {package['from_employee']} → {package['to_employee']}**",
        f"",
        f"**Summary:** {package['conversation_summary']}",
    ]

    profile = package.get("caller_profile", {})
    if profile:
        lines.append(f"**Caller:** {profile.get('name', 'Unknown')}")
        for k, v in profile.items():
            if k != "name":
                lines.append(f"  - {k}: {v}")

    actions = package.get("pending_actions", [])
    if actions:
        lines.append(f"\n**Pending Actions:**")
        for a in actions:
            lines.append(f"  - {a}")

    return "\n".join(lines)
