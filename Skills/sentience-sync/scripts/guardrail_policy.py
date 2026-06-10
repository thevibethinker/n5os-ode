"""
Backward-compatible wrapper around guardrail_engine.
"""

from __future__ import annotations

from guardrail_engine import GuardrailEngine
from guardrail_engine import GuardrailPolicy
from guardrail_engine import evaluate_candidate
from guardrail_engine import main
from guardrail_engine import normalize_candidate_type
from guardrail_engine import normalize_confidence_tier

__all__ = [
    "GuardrailEngine",
    "GuardrailPolicy",
    "evaluate_candidate",
    "main",
    "normalize_candidate_type",
    "normalize_confidence_tier",
]


if __name__ == "__main__":
    raise SystemExit(main())
