#!/usr/bin/env python3
"""
Digest Output Validator

Scans meeting prep digest markdown files to detect forbidden placeholder text.
Rejects files with placeholders before write.

Usage:
    validate_digest_output.py <digest_file>

Returns 0 on clean, 1 if placeholder detected.
"""

import sys
import re

# Forbidden placeholder regex patterns
PLACEHOLDER_PATTERNS = [
    re.compile(r"Last 3 email interactions \(max returned by API\):"),
    re.compile(r"\(Earlier history may exist but not returned by Gmail API\)"),
    re.compile(r"API limits"),
    re.compile(r"max returned by"),
    re.compile(r"\([^)]*placeholder[^)]*\)", re.IGNORECASE),
]


def check_for_placeholders(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(content):
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_digest_output.py <digest_file>")
        sys.exit(2)

    digest_file = sys.argv[1]
    if check_for_placeholders(digest_file):
        print(f"[ERROR] Placeholder text detected in {digest_file}")
        sys.exit(1)
    else:
        print(f"[OK] No placeholder text found in {digest_file}")
        sys.exit(0)


if __name__ == '__main__':
    main()
