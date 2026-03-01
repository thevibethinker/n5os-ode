"""
Ingestion Capability — Content Classifier

Keyword-based classification for v1 (Layer 1). No LLM calls.
Returns type, urgency, and topics for any text input.
"""

import re
from pathlib import Path

import yaml

_config_cache: dict | None = None


def _load_config() -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    config_path = Path(__file__).resolve().parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            _config_cache = yaml.safe_load(f)
    else:
        _config_cache = {}
    return _config_cache


def classify_content(text: str) -> dict:
    """
    Classify inbound content by type, urgency, and topics.

    Args:
        text: The content text to classify.

    Returns:
        dict with keys: type (str), urgency (str), topics (list[str])
    """
    cfg = _load_config()
    classification = cfg.get("classification", {})
    text_lower = text.lower()

    # Determine urgency
    urgency = "normal"
    urgency_keywords = classification.get("urgency_keywords", {})
    for level in ("critical", "high", "low"):
        keywords = urgency_keywords.get(level, [])
        for kw in keywords:
            if kw.lower() in text_lower:
                urgency = level
                break
        if urgency != "normal":
            break

    # Determine type
    content_type = "inquiry"  # default
    type_keywords = classification.get("type_keywords", {})
    for ctype in ("escalation", "complaint", "request", "information"):
        keywords = type_keywords.get(ctype, [])
        for kw in keywords:
            if kw.lower() in text_lower:
                content_type = ctype
                break
        if content_type != "inquiry":
            break

    # Extract topics (simple: significant words > 4 chars, deduped, max 5)
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text_lower)
    stop_words = {"about", "after", "again", "being", "between", "could",
                  "every", "from", "have", "their", "there", "these",
                  "those", "through", "under", "where", "which", "while",
                  "would", "should", "please", "think", "really", "other"}
    topics = []
    seen = set()
    for w in words:
        if w not in stop_words and w not in seen:
            seen.add(w)
            topics.append(w)
        if len(topics) >= 5:
            break

    return {
        "type": content_type,
        "urgency": urgency,
        "topics": topics,
    }


def reset_config_cache() -> None:
    global _config_cache
    _config_cache = None
