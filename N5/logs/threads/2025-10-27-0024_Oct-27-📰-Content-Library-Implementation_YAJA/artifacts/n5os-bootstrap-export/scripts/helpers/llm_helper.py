#!/usr/bin/env python3
"""
LLM Helper for N5 Scripts - Zo Internal Version

Uses Zo's internal LLM (the assistant executing the scheduled task) 
for intelligent decisions without external API calls.

Works via prompt file mechanism:
1. Script writes prompt to request file
2. Script polls for response file
3. Zo LLM (executing the task) sees request and responds
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# LLM request/response directory
LLM_DIR = Path('/home/workspace/N5/.llm_requests')
LLM_DIR.mkdir(exist_ok=True)


def call_llm(prompt: str, timeout: int = 30, model: str = "auto") -> Optional[str]:
    """
    Call Zo's internal LLM with a prompt.
    
    This works by:
    1. Writing prompt to a request file
    2. Polling for response file (created by Zo LLM)
    3. Reading and returning response
    
    Args:
        prompt: The prompt text
        timeout: Max seconds to wait for response
        model: Model preference (ignored - uses Zo's default)
    
    Returns:
        LLM response text or None if timeout/error
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    request_id = f"req_{timestamp}"
    
    request_file = LLM_DIR / f"{request_id}.request.json"
    response_file = LLM_DIR / f"{request_id}.response.txt"
    
    try:
        # Write request
        request_data = {
            'request_id': request_id,
            'prompt': prompt,
            'timestamp': datetime.now().isoformat(),
            'timeout': timeout
        }
        
        with open(request_file, 'w') as f:
            json.dump(request_data, f, indent=2)
        
        logger.info(f"LLM request created: {request_id}")
        
        # Poll for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if response_file.exists():
                # Read response
                response = response_file.read_text().strip()
                logger.info(f"LLM response received: {len(response)} chars")
                
                # Cleanup
                request_file.unlink(missing_ok=True)
                response_file.unlink(missing_ok=True)
                
                return response
            
            time.sleep(0.5)
        
        # Timeout
        logger.warning(f"LLM request {request_id} timed out after {timeout}s")
        request_file.unlink(missing_ok=True)
        return None
        
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        request_file.unlink(missing_ok=True)
        return None


def check_pending_requests() -> list:
    """
    Check for pending LLM requests (for Zo LLM to process).
    
    Returns list of request files that need responses.
    """
    if not LLM_DIR.exists():
        return []
    
    pending = list(LLM_DIR.glob("*.request.json"))
    return pending


def respond_to_request(request_file: Path, response_text: str):
    """
    Respond to an LLM request (called by Zo LLM).
    
    Args:
        request_file: Path to request JSON
        response_text: The response to provide
    """
    request_id = request_file.stem.replace('.request', '')
    response_file = request_file.parent / f"{request_id}.response.txt"
    
    response_file.write_text(response_text)
    logger.info(f"Response written for {request_id}")


if __name__ == '__main__':
    # Test mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        # Check for pending requests
        pending = check_pending_requests()
        if pending:
            print(f"Pending LLM requests: {len(pending)}")
            for req in pending:
                print(f"  - {req.name}")
        else:
            print("No pending LLM requests")
    else:
        # Test call
        print("Testing LLM call...")
        response = call_llm("Reply with: OK", timeout=10)
        if response:
            print(f"✓ LLM responded: {response}")
        else:
            print("✗ LLM did not respond (timeout or error)")
