#!/usr/bin/env python3
"""
BS Filter Module
Input: job dict
Output: {"verdict": "pass|fail", "score": float, "flags": []}
Pro-candidate: strict threshold 0.9, expansive rules.
"""

import json
from typing import Dict

def filter_job(job: Dict) -> Dict:
    """
    LLM-powered filter for junk jobs.
    Placeholder: use GPT-4 with prompt.
    """
    # Placeholder logic: reject if title has "unpaid" or no salary
    flags = []
    score = 1.0  # Assume good unless flagged
    
    if "unpaid" in job.get('title', '').lower():
        flags.append("unpaid")
        score -= 0.5
    if not job.get('salary'):
        flags.append("no_salary")
        score -= 0.3
    
    verdict = "pass" if score >= 0.9 else "fail"
    return {"verdict": verdict, "score": score, "flags": flags}

if __name__ == "__main__":
    test_job = {"title": "Unpaid Intern", "salary": ""}
    result = filter_job(test_job)
    print(json.dumps(result))