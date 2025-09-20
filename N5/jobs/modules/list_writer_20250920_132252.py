#!/usr/bin/env python3
"""
List Writer Module
Atomic append to jsonl.
"""

import json
import tempfile
import os
from typing import Dict

def append_job(job: Dict, list_name: str):
    """
    Append job to list with atomic write.
    """
    path = f"/home/workspace/N5/jobs/lists/{list_name}.jsonl"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as f:
        # Read existing
        if os.path.exists(path):
            with open(path, 'r') as existing:
                for line in existing:
                    f.write(line)
        # Add new
        f.write(json.dumps(job) + "\n")
    
    os.rename(f.name, path)

if __name__ == "__main__":
    test_job = {"title": "Test"}
    append_job(test_job, "jobs-scraped")
    print("Appended")