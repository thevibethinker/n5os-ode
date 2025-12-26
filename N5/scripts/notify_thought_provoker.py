#!/usr/bin/env python3
"""
Thought Provoker Notification Script

Sends an SMS to V if there are new provocation candidates.
"""

import json
import sys
from pathlib import Path

# Mock or real send_sms_to_user tool access
# In a real Zo context, we would use the tool.
# Since this is a script, we'll output a command string or log.

CANDIDATES_PATH = Path("/home/workspace/N5/data/provocation_candidates.json")

def notify():
    if not CANDIDATES_PATH.exists():
        return

    with open(CANDIDATES_PATH, 'r') as f:
        data = json.load(f)
        provocations = data.get("provocations", [])
        
    if provocations:
        count = len(provocations)
        message = f"🧠 {count} thought-provokers ready from your inbox. Type '@Thought Provoker Session' when you're ready to engage."
        
        # Output for Zo-Agent to see and act on
        print(f"NOTIFICATION_READY: {message}")

if __name__ == "__main__":
    notify()

