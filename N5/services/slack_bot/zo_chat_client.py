#!/usr/bin/env python3
"""
Simple Zo Chat Client for Slack Bot
Calls Zo's conversation API and waits for response
"""
import sys
import os
import subprocess
import json
import tempfile
from pathlib import Path

# Add N5 to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def ask_zo(question: str, context: dict = None) -> str:
    """
    Ask Zo a question and get a response.
    Uses the conversation workspace to create a temporary conversation.
    """
    try:
        # Create a temporary script that calls Zo via subprocess
        # This simulates what happens when you send a message in the Zo UI
        
        # For now, use a simple approach: write to a temp file and call Zo CLI
        # Or use the internal API if available
        
        # Actually, the simplest approach: use environment to call Zo's chat endpoint
        # via the internal HTTP API that Zo Computer uses
        
        # Let me try calling the actual Zo Computer API
        import aiohttp
        import asyncio
        
        async def _ask():
            # Zo Computer's internal API endpoint for chat
            # This is how the Zo UI communicates with the AI
            url = "http://localhost:6969/api/chat"
            
            payload = {
                "message": question,
                "context": context or {}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "No response from Zo")
                    else:
                        return f"Error: Zo API returned status {resp.status}"
        
        return asyncio.run(_ask())
        
    except Exception as e:
        return f"Error communicating with Zo: {str(e)}"


if __name__ == "__main__":
    # Test
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        response = ask_zo(question)
        print(response)
    else:
        print("Usage: python3 zo_chat_client.py <question>")

