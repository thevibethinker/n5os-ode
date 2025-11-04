#!/usr/bin/env python3
"""
Inject critical reminders when conversation context exceeds threshold.
Non-invasive: reads SESSION_STATE to check token count, returns reminder text.
"""

import sys
from pathlib import Path

REMINDER_FILE = Path("/home/workspace/N5/prefs/system/critical_reminders.txt")
TOKEN_THRESHOLD = 8000

def get_conversation_tokens(session_state_path: Path) -> int:
    """
    Extract approximate token count from SESSION_STATE.md
    If not present, estimate from conversation workspace file sizes
    """
    try:
        if session_state_path.exists():
            content = session_state_path.read_text()
            
            # Check for explicit token count first
            for line in content.split('\n'):
                if 'estimated_tokens:' in line.lower():
                    try:
                        return int(line.split(':')[1].strip())
                    except:
                        pass
            
            # Rough token estimate: words * 1.3
            return int(len(content.split()) * 1.3)
        return 0
    except Exception:
        return 0

def should_inject_reminder(convo_workspace: Path) -> bool:
    """Check if we're over token threshold"""
    session_state = convo_workspace / "SESSION_STATE.md"
    tokens = get_conversation_tokens(session_state)
    return tokens >= TOKEN_THRESHOLD

def get_reminder_text() -> str:
    """Load and return reminder text"""
    if REMINDER_FILE.exists():
        return "\n\n" + REMINDER_FILE.read_text() + "\n\n"
    return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: inject_reminders.py <conversation_workspace_path>")
        sys.exit(1)
    
    convo_workspace = Path(sys.argv[1])
    
    if should_inject_reminder(convo_workspace):
        print(get_reminder_text())
    else:
        print("")  # No injection needed

if __name__ == "__main__":
    main()
