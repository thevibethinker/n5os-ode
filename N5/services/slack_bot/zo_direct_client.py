#!/usr/bin/env python3
"""
Direct Zo Integration for Slack Bot - Simple File-Based Approach
Creates conversation files that Zo can process and respond to
"""
import json
import uuid
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Slack bot conversation directory
SLACK_CONVOS_DIR = Path("/home/workspace/N5/data/slack_conversations")
SLACK_CONVOS_DIR.mkdir(parents=True, exist_ok=True)

def ask_zo_via_file(message: str, user_id: str, context: dict = None) -> str:
    """
    Simple approach: Log the question and return immediate acknowledgment.
    The actual response will be handled async by checking the conversation later.
    
    For now, we'll just provide helpful immediate responses.
    """
    try:
        # Log the conversation
        conv_id = f"slack_{user_id}_{int(time.time())}"
        conv_file = SLACK_CONVOS_DIR / f"{conv_id}.json"
        
        conv_data = {
            "conversation_id": conv_id,
            "user_id": user_id,
            "timestamp": time.time(),
            "message": message,
            "context": context or {},
            "status": "pending"
        }
        
        conv_file.write_text(json.dumps(conv_data, indent=2))
        logger.info(f"Logged Slack conversation: {conv_id}")
        
        # For V1, return helpful immediate response
        return generate_immediate_response(message)
        
    except Exception as e:
        logger.error(f"Error in ask_zo_via_file: {e}")
        return "I've received your message, but encountered an error logging it. Please try again."


def generate_immediate_response(message: str) -> str:
    """
    Generate helpful immediate responses based on message content.
    This is a stopgap until we have proper Zo integration.
    """
    message_lower = message.lower()
    
    # Meeting-related queries
    if any(word in message_lower for word in ["meeting", "discussed", "talked about", "conversation"]):
        return ("I can help you find meeting information! However, I'm still learning to access "
                "your meeting files directly. For now, you can find your meetings in "
                "`/home/workspace/Personal/Meetings/` organized by date and participant. "
                "I'm working on getting full access to search and summarize them for you!")
    
    # General queries
    elif any(word in message_lower for word in ["hello", "hi", "hey"]):
        return ("Hi! I'm your Slack bot connected to Zo. I can help you with questions about "
                "your workspace, meetings, and files. I'm still in early setup phase, so some "
               "features are being added. What would you like to know?")
    
    # Help queries
    elif any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
        return ("I'm your personal AI assistant via Slack! I can:\n"
                "• Answer questions about your workspace\n"
                "• Search through your meetings and documents\n"
                "• Help you find information quickly\n\n"
                "I'm still being set up, so more capabilities are coming soon!")
    
    # Default
    else:
        return ("I've received your question! I'm still being connected to the full Zo system. "
                "For now, you can access your files directly at https://va.zo.computer. "
                "Full AI responses via Slack are coming very soon!")


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        response = ask_zo_via_file(msg, "test_user")
        print(response)

