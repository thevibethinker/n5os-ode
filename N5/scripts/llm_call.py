#!/usr/bin/env python3
"""
Simple LLM call wrapper using Zo API.
Usage: python3 llm_call.py "prompt"
"""

import os
import sys
import requests
import json


def call_llm(prompt: str) -> str:
    """Call Zo API with prompt, return response."""
    api_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not api_token:
        print("Error: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": api_token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"API error: {response.status_code}", file=sys.stderr)
            sys.exit(1)
        
        result = response.json()
        return result.get("output", "")
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 llm_call.py \"prompt\"", file=sys.stderr)
        sys.exit(1)
    
    prompt = sys.argv[1]
    result = call_llm(prompt)
    print(result)

