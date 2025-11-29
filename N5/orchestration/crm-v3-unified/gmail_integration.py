#!/usr/bin/env python3
"""
Gmail Integration for CRM V3 Enrichment

This script is designed to be CALLED FROM the enrichment worker.
It writes a shell script that Zo can execute to perform the Gmail search.

Architecture:
1. Enrichment worker calls this script with email address
2. This script creates a temporary Zo command script
3. Returns instructions for Zo to execute
4. Zo performs actual Gmail search
5. Results are formatted and returned

This bridges the gap between standalone Python (worker) and Zo tools.
"""

import sys
import json
from pathlib import Path


def create_gmail_search_command(email: str, output_file: str) -> str:
    """
    Create a shell command that instructs Zo to search Gmail.
    
    Returns a command string that can be executed to trigger Zo's Gmail search.
    """
    # Create a request file that Zo can process
    request = {
        "action": "gmail_search",
        "email": email,
        "gmail_account": "attawar.v@gmail.com",
        "output_file": output_file
    }
    
    request_file = f"/tmp/gmail_search_request_{email.replace('@', '_at_')}.json"
    
    with open(request_file, 'w') as f:
        json.dump(request, f, indent=2)
    
    # Return the path to the request file
    # The enrichment worker will need to have Zo process this
    return request_file


def format_gmail_results(results_file: str, target_email: str) -> str:
    """
    Read Gmail search results from file and format as intelligence block.
    
    Args:
        results_file: Path to JSON file with Gmail results
        target_email: Email address being analyzed
        
    Returns:
        Formatted intelligence block
    """
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        from gmail_enrichment_module import format_gmail_intelligence
        return format_gmail_intelligence(results, target_email)
        
    except FileNotFoundError:
        return f"""**Gmail Thread Analysis:**

⚠️ Results file not found: {results_file}"""
    except Exception as e:
        return f"""**Gmail Thread Analysis:**

⚠️ Error reading results: {str(e)}"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gmail_integration.py <email> [--format results.json]")
        sys.exit(1)
    
    if "--format" in sys.argv:
        # Format mode: read existing results
        idx = sys.argv.index("--format")
        results_file = sys.argv[idx + 1]
        email = sys.argv[1]
        output = format_gmail_results(results_file, email)
        print(output)
    else:
        # Search mode: create request for Zo
        email = sys.argv[1]
        output_file = f"/tmp/gmail_results_{email.replace('@', '_at_')}.json"
        request_file = create_gmail_search_command(email, output_file)
        print(f"REQUEST_FILE:{request_file}")
        print(f"OUTPUT_FILE:{output_file}")

