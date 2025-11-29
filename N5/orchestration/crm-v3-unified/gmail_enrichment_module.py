#!/usr/bin/env python3
"""
Gmail Enrichment Module for CRM V3

This module is designed to be CALLED BY ZO (not run standalone).
Zo will:
1. Call use_app_gmail to search for messages
2. Pass results to this module for formatting
3. Return formatted intelligence block

Usage pattern:
    # In Zo conversation:
    results = use_app_gmail("gmail-find-email", {"q": "from:email@example.com OR to:email@example.com"})
    formatted = format_gmail_intelligence(results, "email@example.com")
"""

from datetime import datetime
from typing import Dict, List, Optional


def format_gmail_intelligence(gmail_results: Dict, target_email: str) -> str:
    """
    Format Gmail search results into intelligence block for CRM profile.
    
    Args:
        gmail_results: Raw results from use_app_gmail("gmail-find-email")
        target_email: The email address being analyzed
        
    Returns:
        Formatted markdown intelligence block
    """
    lines = ["**Gmail Thread Analysis:**\n"]
    
    # Handle different result structures
    messages = gmail_results.get('messages', [])
    
    if not messages:
        lines.append(f"No Gmail threads found with {target_email}")
        return "\n".join(lines)
    
    total_count = len(messages)
    lines.append(f"Found {total_count} message(s) with {target_email}:\n")
    
    # Analyze and display top messages
    for i, msg in enumerate(messages[:5], 1):
        # Extract fields (structure depends on Gmail API response)
        subject = msg.get('subject', '(No subject)')
        snippet = msg.get('snippet', '')
        
        # Handle timestamp
        date_str = _format_message_date(msg)
        
        # Format message entry
        lines.append(f"  {i}. \"{subject}\" ({date_str})")
        
        if snippet:
            clean_snippet = snippet.replace('\n', ' ').strip()[:80]
            if clean_snippet:
                lines.append(f"     → {clean_snippet}...")
    
    if total_count > 5:
        lines.append(f"\n  ...and {total_count - 5} more messages")
    
    # Add summary statistics
    lines.append(f"\n**Total threads:** {total_count}")
    
    return "\n".join(lines)


def _format_message_date(message: Dict) -> str:
    """Extract and format message date from various possible fields."""
    
    # Try internalDate (milliseconds since epoch)
    if 'internalDate' in message:
        try:
            timestamp_ms = int(message['internalDate'])
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
    # Try date field (string)
    if 'date' in message:
        try:
            # Attempt to parse various date formats
            date_str = message['date']
            # Simple extraction - just take first 10 chars if looks like YYYY-MM-DD
            if len(date_str) >= 10 and date_str[4] == '-':
                return date_str[:10]
            return date_str[:20]  # Truncate long dates
        except:
            pass
    
    return "Unknown date"


def build_gmail_query(email: str, include_sent: bool = True) -> str:
    """
    Build Gmail search query for a specific email address.
    
    Args:
        email: Target email address
        include_sent: If True, search both from: and to:
        
    Returns:
        Gmail query string
    """
    if include_sent:
        return f"from:{email} OR to:{email}"
    else:
        return f"from:{email}"


# Test function for standalone validation
def _test_formatting():
    """Test the formatting with mock data."""
    mock_results = {
        'messages': [
            {
                'subject': 'Project Discussion',
                'snippet': 'Thanks for the great discussion about the project timeline',
                'internalDate': '1700000000000'  # Nov 2023
            },
            {
                'subject': 'Follow-up',
                'snippet': 'Just following up on our conversation from last week',
                'internalDate': '1699000000000'
            }
        ]
    }
    
    output = format_gmail_intelligence(mock_results, 'test@example.com')
    print(output)
    print("\n✓ Formatting test complete")


if __name__ == "__main__":
    print("Gmail Enrichment Module - Test Mode")
    print("=" * 50)
    _test_formatting()

