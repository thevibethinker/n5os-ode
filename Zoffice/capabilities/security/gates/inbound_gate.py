"""
Security Capability — Inbound Gate

Validates inbound content before it reaches any employee.
Pattern-based (deterministic) for v1 — no LLM calls.

Components:
  - Adversarial prompt injection detection
  - PII detection and redaction
  - Sensitivity-aware behavior (strict / standard / low)
"""

import re
from pathlib import Path

import yaml


_config_cache: dict | None = None


def _load_config(config_path: str | None = None) -> dict:
    """Load and cache the security capability config."""
    global _config_cache
    if _config_cache is not None and config_path is None:
        return _config_cache
    if config_path is None:
        config_path = str(Path(__file__).resolve().parents[1] / "config.yaml")
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    if config_path is None or config_path == str(Path(__file__).resolve().parents[1] / "config.yaml"):
        _config_cache = cfg
    return cfg


def _check_adversarial(content: str, patterns: list[str]) -> list[str]:
    """Check content against adversarial patterns. Returns list of matched flag names."""
    flags = []
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            flags.append("adversarial_prompt_injection")
            break  # One match is enough to flag
    return flags


def _filter_pii(content: str, pii_patterns: dict, pii_labels: dict, sensitivity: str) -> tuple[list[str], str]:
    """
    Detect and optionally redact PII.

    Returns (flags, filtered_content).
    - strict: redact PII
    - standard: flag but don't redact
    - low: skip PII entirely
    """
    if sensitivity == "low":
        return [], content

    flags = []
    filtered = content
    for name, pattern in pii_patterns.items():
        if re.search(pattern, content):
            flags.append("pii_detected")
            if sensitivity == "strict":
                label = pii_labels.get(name, "[REDACTED]")
                filtered = re.sub(pattern, label, filtered)
            break  # One PII flag is enough (but we still redact all types)

    # If flagged, redact all PII types in strict mode
    if "pii_detected" in flags and sensitivity == "strict":
        filtered = content
        for name, pattern in pii_patterns.items():
            label = pii_labels.get(name, "[REDACTED]")
            filtered = re.sub(pattern, label, filtered)

    return flags, filtered


def _try_audit(action: str, metadata: dict | None = None) -> None:
    """Attempt to log via audit writer. Silently skip if not available."""
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="security",
            employee=None,
            action=action,
            metadata=metadata,
        )
    except Exception:
        pass  # Audit writer may not be initialized yet


def validate(content: str, config_path: str | None = None) -> dict:
    """
    Validate inbound content through security gates.

    Args:
        content: The text content to validate.
        config_path: Optional path to config.yaml override.

    Returns:
        dict with keys:
          - allowed (bool): Whether the content is safe to process.
          - flags (list[str]): Any security flags raised.
          - filtered_content (str | None): Content with PII redacted (if applicable).
            None if content is blocked.
    """
    cfg = _load_config(config_path)
    sensitivity = cfg.get("sensitivity", "strict")
    adversarial_patterns = cfg.get("adversarial_patterns", [])
    pii_patterns = cfg.get("pii_patterns", {})
    pii_labels = cfg.get("pii_labels", {})

    all_flags = []

    # Step 1: Adversarial detection (always active except if no patterns)
    adv_flags = _check_adversarial(content, adversarial_patterns)
    all_flags.extend(adv_flags)

    if adv_flags:
        _try_audit("inbound_gate_check", {"result": "blocked", "flags": adv_flags})
        return {
            "allowed": False,
            "flags": all_flags,
            "filtered_content": None,
        }

    # Step 2: PII detection + filtering
    pii_flags, filtered = _filter_pii(content, pii_patterns, pii_labels, sensitivity)
    all_flags.extend(pii_flags)

    _try_audit("inbound_gate_check", {
        "result": "allowed",
        "flags": all_flags,
        "pii_redacted": "pii_detected" in pii_flags and sensitivity == "strict",
    })

    return {
        "allowed": True,
        "flags": all_flags,
        "filtered_content": filtered,
    }


def reset_config_cache() -> None:
    """Reset the config cache (useful for testing)."""
    global _config_cache
    _config_cache = None
