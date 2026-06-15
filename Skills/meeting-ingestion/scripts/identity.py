"""Identity helpers for the meeting pipeline.

`is_v()` answers a simpler downstream question: does this participant identify
as the configured primary user for this workspace?

This keeps participant filtering separate from other meeting-quality concepts.
"""

from __future__ import annotations

from config_loader import load_me_config


def _identity_section() -> dict:
    return load_me_config()["identity"]


def _email_addresses() -> frozenset[str]:
    return frozenset(_norm(v) for v in _identity_section().get("email_addresses", []))


def _exact_names() -> frozenset[str]:
    return frozenset(_norm(v) for v in _identity_section().get("exact_names", []))


def _unique_tokens() -> frozenset[str]:
    return frozenset(_norm(v) for v in _identity_section().get("unique_tokens", []))


def canonical_short_name() -> str:
    return str(_identity_section().get("canonical_short_name", "V")).strip() or "V"


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def is_v(name: str | None = None, email: str | None = None) -> bool:
    """Return True if (name, email) identifies the configured primary user."""
    emails = _email_addresses()
    exact_names = _exact_names()
    unique_tokens = _unique_tokens()

    e = _norm(email)
    if e and e in emails:
        return True

    n = _norm(name)
    if not n:
        return False

    if n in exact_names:
        return True

    if n == canonical_short_name().lower() and (not e or e in emails):
        return True

    tokens = set(n.split())
    if tokens & unique_tokens:
        return True

    return False


__all__ = ["is_v", "canonical_short_name"]
