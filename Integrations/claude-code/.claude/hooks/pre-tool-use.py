#!/usr/bin/env python3
"""
PreToolUse hook for N5OS integration.

Fires before Claude Code executes a tool (Edit, Write, Bash, etc.)
- Warns about protected paths before destructive operations
- Does NOT block - just warns (Claude Code decides)

This is informational, not restrictive.
"""

import sys
import json
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from config import log, emit_hook_result, is_path_protected

# Tools that modify files
DESTRUCTIVE_TOOLS = {"Edit", "Write", "MultiEdit", "Bash"}

# Bash commands that are destructive
DESTRUCTIVE_BASH_PATTERNS = ["rm ", "rm -", "mv ", "rmdir", "git clean", "git reset --hard"]

def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())
    
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    
    # Only check destructive tools
    if tool_name not in DESTRUCTIVE_TOOLS:
        emit_hook_result({"continue": True})
        return
    
    # Get the path being operated on
    path = None
    warning = None
    
    if tool_name in {"Edit", "Write", "MultiEdit"}:
        path = tool_input.get("file_path") or tool_input.get("path")
    
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        # Check for destructive bash commands
        for pattern in DESTRUCTIVE_BASH_PATTERNS:
            if pattern in command:
                # Try to extract path from command
                parts = command.split()
                for part in parts:
                    if part.startswith("/home/workspace"):
                        path = part
                        break
                break
    
    # Check if path is protected
    if path:
        is_protected, reason = is_path_protected(path)
        if is_protected:
            warning = f"⚠️ N5OS: This path is protected ({reason}). Proceed with caution."
            log(f"Protected path warning: {path} - {reason}")
    
    # Emit result - we warn but don't block
    result = {"continue": True}
    if warning:
        result["message"] = warning
    
    emit_hook_result(result)

if __name__ == "__main__":
    main()

