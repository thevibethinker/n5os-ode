"""
Zo2Zo — Trust Registry

Verifies trust between Zo instances using the security.yaml trusted_instances list.
"""

from pathlib import Path

import yaml

_SECURITY_CONFIG = str(Path(__file__).resolve().parents[3] / "config" / "security.yaml")


def _load_trusted_instances(security_config_path: str | None = None) -> list[str]:
    path = security_config_path or _SECURITY_CONFIG
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg.get("security", {}).get("trust", {}).get("trusted_instances", [])


def verify_trust(instance_id: str, security_config_path: str | None = None) -> dict:
    """
    Check if an instance is trusted.

    Returns:
        TrustResult dict: trusted (bool), level (full|untrusted), instance (str)
    """
    trusted_list = _load_trusted_instances(security_config_path)
    is_trusted = instance_id in trusted_list

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="zo2zo",
            employee=None,
            action="trust_verification",
            metadata={"instance": instance_id, "trusted": is_trusted},
        )
    except Exception:
        pass

    return {
        "trusted": is_trusted,
        "level": "full" if is_trusted else "untrusted",
        "instance": instance_id,
    }


def list_trusted(security_config_path: str | None = None) -> list[str]:
    """Return all trusted instances."""
    return _load_trusted_instances(security_config_path)


def add_trusted(instance_id: str) -> bool:
    """
    Would add to trust list — returns False.
    Modifying security.yaml requires human action.
    """
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="zo2zo",
            employee=None,
            action="trust_add_requested",
            metadata={"instance": instance_id, "result": "denied_requires_human"},
        )
    except Exception:
        pass
    return False
