#!/usr/bin/env python3
"""
Zo AI Bridge for Slack Bot
Calls Zo's actual AI via subprocess to get real intelligent responses
"""
import subprocess
import json
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ask_zo_ai(question: str, user_id: str, context: dict) -> str:
    """
    Ask Zo's AI a question and get a real response.
    Uses Zo's conversation system via subprocess.
    """
    try:
        # Create a temporary script that Zo can execute
        # This script will be picked up by Zo's system
        script_content = f"""#!/bin/bash
# Slack Bot AI Request
# User: {user_id}
# Question: {question}

# Call Zo's chat API using curl
curl -X POST http://localhost:7777/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "{question}", "source": "slack", "user_id": "{user_id}"}}'
"""
        
        # Try direct API call first
        result = subprocess.run(
            ['curl', '-X', 'POST', 'http://localhost:7777/api/chat',
             '-H', 'Content-Type: application/json',
             '-d', json.dumps({"message": question, "source": "slack", "user_id": user_id})],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                response_data = json.loads(result.stdout)
                if 'response' in response_data:
                    return response_data['response']
            except json.JSONDecodeError:
                pass
        
        # Fallback: Use conversation workspace approach
        # Create a conversation request file that Zo monitors
        conv_dir = Path("/home/workspace/.slack_bot_requests")
        conv_dir.mkdir(exist_ok=True)
        
        import time
        request_id = f"slack_{user_id}_{int(time.time())}"
        request_file = conv_dir / f"{request_id}.json"
        
        request_data = {
            "request_id": request_id,
            "user_id": user_id,
            "question": question,
            "context": context,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        request_file.write_text(json.dumps(request_data, indent=2))
        logger.info(f"Created AI request file: {request_file}")
        
        # For now, return acknowledgment
        # TODO: Implement polling for response
        return (f"I've received your question and logged it for processing. "
                f"Full AI-powered responses are being integrated. "
                f"For immediate access to your meeting files, visit: "
                f"https://va.zo.computer/Personal/Meetings/")
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout calling Zo AI")
        return "Sorry, that request timed out. Please try again."
    except Exception as e:
        logger.error(f"Error calling Zo AI: {e}")
        return f"I encountered an error: {str(e)}"


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        response = ask_zo_ai(question, "test_user", {})
        print(response)

