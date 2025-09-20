import argparse

#!/usr/bin/env python3
import re
from typing import List, Tuple

def classify_list(content: str, available_slugs: List[str]) -> Tuple[str, str]:
    """
    Classify content to determine target list.
    Returns (list_slug, rationale)
    """
    content_lower = content.lower()

    # Rules for system-upgrades
    system_keywords = ["system", "upgrade", "config", "audit", "workflow", "prefs", "management", "enhance", "improve"]
    if any(kw in content_lower for kw in system_keywords):
        slug = "system-upgrades"
        rationale = "Contains system/upgrade related keywords"
    else:
        slug = "ideas"
        rationale = "Default fallback"

    # Check if slug is available, fallback if not
    if slug not in available_slugs:
        if "ideas" in available_slugs:
            slug = "ideas"
            rationale += "; fallback to ideas (system-upgrades not available)"
        elif available_slugs:
            slug = available_slugs[0]
            rationale += f"; fallback to {slug} (not available)"

    return slug, rationale

def extract_tags(content: str, max_tags: int = 3) -> List[str]:
    """
    Extract tags from content using simple token-based approach.
    Returns list of up to max_tags tags.
    """
    # Split by whitespace and punctuation
    tokens = re.split(r'[\s\W]+', content.lower())
    # Filter tokens: length > 3, no numbers, alphabetic
    candidates = [t for t in tokens if len(t) > 3 and t.isalpha()]
    # Take unique, up to max_tags
    tags = list(dict.fromkeys(candidates))[:max_tags]
    return tags