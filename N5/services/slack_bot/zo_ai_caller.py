#!/usr/bin/env python3
"""
Zo AI Caller - Direct integration with Zo Computer's AI via `zo` CLI
Uses subprocess to call the `zo` command and get real AI responses
"""
import subprocess
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def call_zo_ai(
    message: str,
    conversation_id: Optional[str] = None,
    timeout: int = 120
) -> Dict[str, str]:
    """
    Call Zo AI via the `zo` CLI command.
    
    Args:
        message: The user's question/message
        conversation_id: Optional conversation ID to continue existing conversation
        timeout: Maximum time to wait for response (seconds)
    
    Returns:
        Dict with 'output' (AI response) and 'conversation_id'
    
    Raises:
        subprocess.TimeoutExpired: If AI takes too long
        Exception: For other errors
    """
    try:
        cmd = ["zo", message]
        
        if conversation_id:
            cmd.extend(["--conversation-id", conversation_id])
        
        logger.info(f"Calling Zo AI: {message[:100]}...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        
        # Parse JSON response
        response = json.loads(result.stdout)
        
        logger.info(f"Got AI response (conversation: {response.get('conversation_id', 'unknown')})")
        
        return {
            "output": response.get("output", ""),
            "conversation_id": response.get("conversation_id", "")
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"Zo AI timeout after {timeout}s")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Zo AI command failed: {e.stderr}")
        raise Exception(f"AI command failed: {e.stderr}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {result.stdout}")
        raise Exception(f"Invalid AI response format: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling Zo AI: {e}")
        raise


def ask_zo(message: str, user_id: str, context: Dict) -> str:
    """
    Simplified interface for Slack bot.
    
    Args:
        message: User's message
        user_id: Slack user ID
        context: Additional context (channel, event_type, etc.)
    
    Returns:
        AI's response text
    """
    try:
        # Add context to the message
        enhanced_message = f"{message}"
        
        # Optionally add context info
        if context.get("event_type") == "dm":
            enhanced_message = f"[Slack DM from user {user_id}]: {message}"
        
        # Call Zo AI
        response = call_zo_ai(enhanced_message, timeout=120)
        
        # Extract just the output text
        output = response.get("output", "")
        
        # Clean up any extra formatting if needed
        # (The zo command returns markdown, which Slack can handle)
        
        return output if output else "I received your message but didn't generate a response."
        
    except subprocess.TimeoutExpired:
        logger.error("AI timeout")
        return "Sorry, that request took too long to process. Please try a simpler question."
    except Exception as e:
        logger.error(f"Error in ask_zo: {e}")
        return "Sorry, I encountered an error processing your request. Please try again."


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        response = ask_zo(question, "test_user", {"event_type": "dm"})
        print(response)
    else:
        # Default test
        response = ask_zo("What is 2+2?", "test_user", {"event_type": "dm"})
        print(response)

