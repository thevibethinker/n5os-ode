"""
Gmail Enricher for CRM V3

This module provides async enrichment via Gmail thread analysis.
NOTE: This is orchestration code - actual Gmail tool calls happen via LLM worker.
"""

import json
from typing import Optional, Dict, Any
from pathlib import Path

class GmailEnricher:
    """
    Gmail enrichment coordinator.
    
    This class provides the interface for Gmail enrichment, but delegates
    actual tool calls to the LLM worker (Zo) who has access to use_app_gmail.
    """
    
    def __init__(self, worker_callback=None):
        """
        Initialize enricher.
        
        Args:
            worker_callback: Function to request LLM worker to perform tool calls
        """
        self.worker_callback = worker_callback
    
    async def enrich(self, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrich profile using Gmail thread analysis.
        
        This method returns a structured enrichment request that the worker
        can execute using actual tool access.
        
        Returns:
            {
                "success": bool,
                "threads_found": int,
                "markdown": str,
                "error": str or None
            }
        """
        return {
            "action": "gmail_enrichment",
            "params": {
                "email": email,
                "name": name or "Unknown"
            },
            "instructions": [
                f"1. Search Gmail for threads: use_app_gmail('gmail-find-email', {{'q': 'from:{email} OR to:{email}', 'maxResults': 20}})",
                "2. Extract thread IDs from results",
                "3. For each thread (max 20), fetch content: use_app_gmail('gmail-list-thread-messages', {'threadId': thread_id})",
                "4. Load prompt: N5/workflows/gmail_thread_analyzer.prompt.md",
                "5. Invoke prompt with contact_email, contact_name, and threads JSON",
                "6. Return formatted markdown intelligence block"
            ]
        }

async def enrich_via_gmail(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Legacy async interface for Gmail enrichment.
    
    Returns enrichment instructions for the worker to execute.
    """
    enricher = GmailEnricher()
    return await enricher.enrich(email, name)

def format_no_threads_message(email: str) -> str:
    """Format message when no Gmail threads are found."""
    return f"""**Gmail Thread Intelligence:**

No Gmail history found with {email}."""

def format_error_message(email: str, error: str) -> str:
    """Format error message for Gmail enrichment."""
    return f"""**Gmail Thread Intelligence:**

Error retrieving Gmail data: {error}"""

