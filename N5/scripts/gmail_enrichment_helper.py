#!/usr/bin/env python3
"""
Gmail Enrichment Helper
Searches Gmail for threads with a specific email address and returns intelligence.
"""

import json
import sys
from typing import Dict, List, Optional


def analyze_gmail_threads(email: str, gmail_results: Dict) -> str:
    """
    Analyze Gmail search results and generate intelligence block.
    
    Args:
        email: The email address being analyzed
        gmail_results: Results from use_app_gmail tool
        
    Returns:
        Formatted intelligence block for YAML
    """
    lines = [f"**Gmail Thread Analysis:**\n"]
    
    # Parse results
    messages = gmail_results.get('messages', [])
    
    if not messages:
        lines.append(f"No Gmail threads found with {email}")
        return "\n".join(lines)
    
    # Analyze message patterns
    total_count = len(messages)
    lines.append(f"Found {total_count} message(s) with {email}:\n")
    
    # Show top messages
    for i, msg in enumerate(messages[:5], 1):
        subject = msg.get('subject', '(No subject)')
        snippet = msg.get('snippet', '')
        date = msg.get('internalDate', '')
        
        # Convert timestamp if present
        if date:
            try:
                from datetime import datetime
                dt = datetime.fromtimestamp(int(date) / 1000)
                date_str = dt.strftime("%Y-%m-%d")
            except:
                date_str = "Unknown date"
        else:
            date_str = "Unknown date"
        
        lines.append(f"  {i}. \"{subject}\" ({date_str})")
        if snippet:
            # Truncate snippet to 80 chars
            clean_snippet = snippet.replace('\n', ' ')[:80]
            lines.append(f"     → {clean_snippet}...")
    
    if total_count > 5:
        lines.append(f"\n  ...and {total_count - 5} more messages")
    
    return "\n".join(lines)


def format_gmail_error(email: str, error: str) -> str:
    """Format error message for Gmail enrichment."""
    return f"""**Gmail Thread Analysis:**

⚠️ Error searching Gmail for {email}: {error}"""


def format_no_gmail_connection() -> str:
    """Format message when Gmail is not connected."""
    return """**Gmail Thread Analysis:**

⚠️ Gmail not connected - install gmail app in Zo settings"""


if __name__ == "__main__":
    # CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage: gmail_enrichment_helper.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    print(f"Would search Gmail for: {email}")
    print("(This is a helper - actual search requires use_app_gmail tool)")

