#!/usr/bin/env python3
"""
Stop hook for N5OS integration.

Fires when Claude Code session is ending.
- Triggers N5 conversation close via bridge
- Prompts to update session-context.md

This ensures Claude Code sessions are properly logged to N5OS.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from config import (
    log, emit_hook_result, get_session_context_path,
    read_session_context, get_timestamp, WORKSPACE, N5_ROOT
)

def extract_summary_from_context(context: str) -> str:
    """Extract a brief summary from session context."""
    lines = context.split("\n")
    
    # Look for Progress section
    in_progress = False
    progress_lines = []
    
    for line in lines:
        if "## Progress This Session" in line:
            in_progress = True
            continue
        elif line.startswith("## ") and in_progress:
            break
        elif in_progress and line.strip() and not line.startswith("_"):
            progress_lines.append(line.strip())
    
    if progress_lines:
        return " ".join(progress_lines[:3])  # First 3 lines of progress
    
    return "Claude Code session completed"

def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())
    session_id = hook_input.get("session_id", "unknown")
    
    log(f"Session ending: {session_id}")
    
    # Read session context for summary
    context = read_session_context(WORKSPACE)
    summary = extract_summary_from_context(context) if context else "Claude Code session"
    
    # Call the close bridge to log to N5OS
    try:
        result = subprocess.run(
            [
                "python3",
                str(N5_ROOT / "scripts/close_convo_bridge.py"),
                "--summary", summary,
                "--session-id", f"claude-code_{session_id}",
                "--tier", "1"  # Quick close for Claude Code sessions
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log("Session logged to N5OS successfully")
        else:
            log(f"Warning: N5OS logging returned non-zero: {result.stderr}", "WARN")
    
    except subprocess.TimeoutExpired:
        log("Warning: N5OS logging timed out", "WARN")
    except Exception as e:
        log(f"Warning: Could not log to N5OS: {e}", "WARN")
    
    # Always allow stop - we don't block session end
    emit_hook_result({
        "continue": True,
        "message": "Session logged to N5OS"
    })

if __name__ == "__main__":
    main()

