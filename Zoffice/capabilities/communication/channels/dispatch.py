"""
Communication — Dispatch

Multi-channel dispatcher. Prepares outbound messages through the approval gate,
template rendering, and rate limiting pipeline. Does NOT actually send — returns
a SendRequest for rice-integration to wire.
"""

import hashlib
import re
from pathlib import Path

import yaml

from Zoffice.capabilities.communication.channels.approval import check_approval
from Zoffice.capabilities.communication.channels.rate_limiter import check_rate_limit, record_send


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def _template_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "templates"


def render_template(template_name: str, variables: dict) -> str:
    """
    Render a markdown template with {{variable}} substitution.

    Args:
        template_name: Name of the template (without .md extension).
        variables: Dict of variable names to values.

    Returns:
        Rendered markdown string.
    """
    template_path = _template_dir() / f"{template_name}.md"
    with open(template_path) as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))

    return content


def list_templates() -> list[str]:
    """List available template names (without .md extension)."""
    tdir = _template_dir()
    if not tdir.exists():
        return []
    return [p.stem for p in tdir.glob("*.md")]


def prepare_send(
    recipient: str,
    content: str,
    channel: str,
    employee: str,
    confidence: float = 0.9,
    template: str | None = None,
    template_vars: dict | None = None,
) -> dict:
    """
    Prepare an outbound message through the full pipeline.

    Flow: check approval → render template → check rate limit → audit log → return

    Args:
        recipient: Recipient identifier (email, phone, etc.).
        content: Message content (or overridden by template if provided).
        channel: Outbound channel (email, sms, voice, zo2zo).
        employee: Employee slug requesting the send.
        confidence: Confidence score for approval gate.
        template: Optional template name to render.
        template_vars: Variables for template rendering.

    Returns:
        SendRequest dict.
    """
    # Step 1: Approval gate
    action = f"send_{channel}"
    approval = check_approval(action=action, confidence=confidence, employee=employee)

    # Step 2: Template rendering
    template_used = None
    if template:
        try:
            content = render_template(template, template_vars or {})
            template_used = template
        except FileNotFoundError:
            pass  # Fall back to raw content

    # Step 3: Rate limit check
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    rate_result = check_rate_limit(recipient, content_hash)

    # Determine if ready to send
    ready = (
        approval["decision"] == "auto_act"
        and rate_result["allowed"]
    )

    # Step 4: Audit log
    audit_id = None
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        audit_id = log_audit(
            capability="communication",
            employee=employee,
            action="outbound_prepare",
            channel=channel,
            counterparty=recipient,
            metadata={
                "approval": approval["decision"],
                "rate_limited": not rate_result["allowed"],
                "template": template_used,
                "ready_to_send": ready,
            },
        )
    except Exception:
        pass

    # Record send if ready (for future rate limiting)
    if ready:
        record_send(recipient, content_hash)

    return {
        "recipient": recipient,
        "content": content,
        "channel": channel,
        "employee": employee,
        "template_used": template_used,
        "approval_decision": approval,
        "rate_limit_result": rate_result,
        "ready_to_send": ready,
        "audit_id": audit_id,
    }
