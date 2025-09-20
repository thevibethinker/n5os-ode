#!/usr/bin/env python3
"""
Dedup Module
Input: new_jobs list + existing_jsonl path
Output: list of non-duplicate jobs (URL key)
"""

import json
from typing import List, Dict

def deduplicate(new_jobs: List[Dict], existing_path: str) -> List[Dict]:
    """
    Remove duplicates based on URL.
    Early in flow to save processing.
    """
    # Read existing
    try:
        with open(existing_path, 'r') as f:
            existing = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        existing = []
    
    existing_urls = {job.get('url') for job in existing}
    return [job for job in new_jobs if job.get('url') not in existing_urls]

if __name__ == "__main__":
    # Smoke test: python -m n5.jobs.modules.dedup
    test_new = [{"url": "https://example.com/1", "title": "A"}, {"url": "https://example.com/2", "title": "B"}]
    result = deduplicate(test_new, "/dev/null")  # No existing
    print(json.dumps(result))