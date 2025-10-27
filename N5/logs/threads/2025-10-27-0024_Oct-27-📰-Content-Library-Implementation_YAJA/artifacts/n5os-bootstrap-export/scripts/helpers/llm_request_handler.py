#!/usr/bin/env python3
"""
LLM Request Handler

Checks for pending LLM requests and formats them for Zo LLM to respond to.
This script is called by Zo during scheduled task execution.
"""

import json
import sys
from pathlib import Path

LLM_DIR = Path('/home/workspace/N5/.llm_requests')


def get_pending_requests():
    """Get all pending LLM requests."""
    if not LLM_DIR.exists():
        return []
    
    requests = []
    for req_file in LLM_DIR.glob("*.request.json"):
        try:
            with open(req_file, 'r') as f:
                req_data = json.load(f)
                requests.append({
                    'file': req_file,
                    'request_id': req_data['request_id'],
                    'prompt': req_data['prompt'],
                    'timestamp': req_data['timestamp']
                })
        except Exception as e:
            print(f"Error reading {req_file}: {e}", file=sys.stderr)
    
    return requests


def display_request(request):
    """Display a request for Zo LLM to respond to."""
    print(f"\n{'='*80}")
    print(f"LLM REQUEST: {request['request_id']}")
    print(f"Timestamp: {request['timestamp']}")
    print(f"{'='*80}")
    print(f"\nPROMPT:\n{request['prompt']}")
    print(f"\n{'='*80}")
    print(f"Response file: {request['file'].parent / (request['request_id'] + '.response.txt')}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    pending = get_pending_requests()
    
    if not pending:
        print("No pending LLM requests")
        sys.exit(0)
    
    print(f"Found {len(pending)} pending LLM request(s)")
    
    for req in pending:
        display_request(req)
    
    print("\n⚠️  ZO LLM: Please respond to the above request(s) by creating response files.")
