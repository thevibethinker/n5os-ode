#!/usr/bin/env python3
"""
Test fixtures for ingest normalization pipeline.
Run: python3 test_ingest_normalization.py

Tests that boilerplate is properly stripped and content is preserved.
"""

import sys
from pathlib import Path

# Will be implemented when the normalization module exists
# from N5.scripts.content_normalize import (
#     classify_ingest_mode,
#     extract_with_trafilatura,
#     heuristic_strip_boilerplate,
# )

BOILERPLATE_PATTERNS = [
    "Skip to content",
    "Navigation Menu",
    "Toggle navigation",
    "Sign in",
    "Footer",
    "© 202",
    "Terms of Service",
    "Privacy Policy",
    "Cookie Policy",
    "Subscribe",
    "Newsletter",
]


def check_no_boilerplate(text: str, source_name: str) -> list[str]:
    """Check that common boilerplate patterns are absent."""
    failures = []
    for pattern in BOILERPLATE_PATTERNS:
        if pattern.lower() in text.lower():
            failures.append(f"[{source_name}] Found boilerplate: '{pattern}'")
    return failures


def check_content_preserved(text: str, required_phrases: list[str], source_name: str) -> list[str]:
    """Check that expected content phrases are preserved."""
    failures = []
    for phrase in required_phrases:
        if phrase.lower() not in text.lower():
            failures.append(f"[{source_name}] Missing expected content: '{phrase}'")
    return failures


def check_compression_ratio(original_len: int, cleaned_len: int, max_ratio: float, source_name: str) -> list[str]:
    """Check that cleaning achieved reasonable compression."""
    if original_len == 0:
        return []
    ratio = cleaned_len / original_len
    if ratio > max_ratio:
        return [f"[{source_name}] Insufficient compression: {ratio:.2%} (expected < {max_ratio:.0%})"]
    return []


def run_tests():
    """Run all normalization tests."""
    failures = []
    
    # Test 1: GitHub README fixture
    # When implemented, will test actual extraction
    print("Test 1: GitHub README - PENDING (awaiting implementation)")
    
    # Test 2: Substack article fixture
    print("Test 2: Substack Article - PENDING (awaiting implementation)")
    
    # Test 3: X/Twitter post fixture
    print("Test 3: X Post - PENDING (awaiting implementation)")
    
    # Test 4: LinkedIn profile fixture
    print("Test 4: LinkedIn Profile - PENDING (awaiting implementation)")
    
    # Summary
    if failures:
        print(f"\n❌ {len(failures)} test(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    else:
        print("\n✅ All tests passed (or pending implementation)")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
