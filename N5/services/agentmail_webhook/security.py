from __future__ import annotations

import re
from typing import Iterable

from .models import SecurityAssessment


CRITICAL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_previous", r"ignore\s+(all\s+)?(previous|above|prior|earlier)\s+(instructions?|rules?|constraints?)"),
    ("system_prompt_leak", r"(show|reveal|display|print|output)\s+(me\s+)?(your|the)\s+(system\s+)?prompt"),
    ("instruction_injection", r"(your\s+)?new\s+(instructions?|directives?|rules?)\s+(are|:)"),
)

HIGH_PATTERNS: tuple[tuple[str, str], ...] = (
    ("role_override", r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be|developer\s+mode|dan\b)"),
    ("delimiter_manipulation", r"(```|\"\"\"|<\s*\/?\s*(system|user|assistant))"),
    ("encoding_evasion", r"\b(base64|rot13|hex\s+encode|decode\s+this)\b"),
)

MEDIUM_PATTERNS: tuple[tuple[str, str], ...] = (
    ("credential_probe", r"\b(api\s*key|token|secret|password|credential|auth)\b"),
    ("environment_probe", r"\b(env|environment|process\.env|os\.environ|getenv)\b"),
    ("filesystem_probe", r"\b(list\s+files|show\s+workspace|/home/workspace|cat\s+\S+)\b"),
)

LOW_PATTERNS: tuple[tuple[str, str], ...] = (
    ("urgency_pressure", r"\b(urgent|asap|immediately|right\s+now|critical\s+issue)\b"),
    ("authority_pressure", r"\b(ceo|cto|founder|manager)\s+(needs|wants|requested)\b"),
)


def _match_patterns(text: str, patterns: Iterable[tuple[str, str]]) -> list[str]:
    matches: list[str] = []
    for name, pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(name)
    return matches


def _domain_from_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return None
    return email.rsplit("@", 1)[-1].lower()


def assess_message(
    *,
    subject: str,
    body_text: str,
    sender_email: str | None,
    trusted_senders: set[str],
    trusted_domains: set[str],
    unknown_senders_review: bool,
) -> SecurityAssessment:
    normalized_sender = (sender_email or "").strip().lower()
    sender_domain = _domain_from_email(normalized_sender)

    combined = f"{subject}\n\n{body_text}"[:50000]

    critical = _match_patterns(combined, CRITICAL_PATTERNS)
    high = _match_patterns(combined, HIGH_PATTERNS)
    medium = _match_patterns(combined, MEDIUM_PATTERNS)
    low = _match_patterns(combined, LOW_PATTERNS)

    flags = critical + high + medium + low

    sender_is_trusted = normalized_sender in trusted_senders
    domain_is_trusted = sender_domain in trusted_domains if sender_domain else False

    if sender_is_trusted:
        sender_tier = "A"
    elif domain_is_trusted:
        sender_tier = "B"
    else:
        sender_tier = "C"

    if critical:
        return SecurityAssessment(
            risk_level="critical",
            decision="quarantine",
            sender_tier=sender_tier,
            confidence=0.99,
            flags=flags,
            rationale="Critical prompt-injection markers detected",
        )

    if high:
        return SecurityAssessment(
            risk_level="high",
            decision="quarantine",
            sender_tier=sender_tier,
            confidence=0.95,
            flags=flags,
            rationale="High-risk adversarial markers detected",
        )

    if medium:
        return SecurityAssessment(
            risk_level="medium",
            decision="review_required",
            sender_tier=sender_tier,
            confidence=0.85,
            flags=flags,
            rationale="Potentially risky request requires human review",
        )

    if unknown_senders_review and sender_tier == "C":
        return SecurityAssessment(
            risk_level="low",
            decision="review_required",
            sender_tier=sender_tier,
            confidence=0.72,
            flags=flags,
            rationale="Unknown sender routed to review by policy",
        )

    return SecurityAssessment(
        risk_level="safe",
        decision="auto_process",
        sender_tier=sender_tier,
        confidence=0.93,
        flags=flags,
        rationale="No major adversarial patterns detected",
    )
