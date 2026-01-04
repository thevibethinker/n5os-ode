#!/usr/bin/env python3
"""
Shared utilities for N5OS Claude Code hooks.
Adapted from Meridian patterns, customized for N5OS.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE = Path("/home/workspace")
N5_ROOT = WORKSPACE / "N5"
INTEGRATIONS_ROOT = WORKSPACE / "Integrations/claude-code"

# Session state file (lives in project root, tracked per-project)
def get_session_context_path(project_root: Path = WORKSPACE) -> Path:
    """Get path to session-context.md for current project."""
    return project_root / ".claude" / "session-context.md"

def get_timestamp() -> str:
    """ISO timestamp in ET."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")

def log(message: str, level: str = "INFO"):
    """Log to stderr (doesn't interfere with hook JSON output)."""
    print(f"[N5-HOOK] {level}: {message}", file=sys.stderr)

def emit_hook_result(result: dict):
    """Emit JSON result for Claude Code hooks."""
    print(json.dumps(result))
    sys.stdout.flush()

def read_session_context(project_root: Path = WORKSPACE) -> str:
    """Read current session context if it exists."""
    path = get_session_context_path(project_root)
    if path.exists():
        return path.read_text()
    return ""

def update_session_context(content: str, project_root: Path = WORKSPACE):
    """Update session context file."""
    path = get_session_context_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def get_protected_paths() -> list[str]:
    """Get list of N5-protected paths."""
    # Could call n5_protect.py here, but keeping it simple
    return [
        "/home/workspace/N5",
        "/home/workspace/Sites",
        "/home/workspace/Personal",
    ]

def is_path_protected(path: str) -> tuple[bool, str]:
    """Check if a path is protected. Returns (is_protected, reason)."""
    import subprocess
    result = subprocess.run(
        ["python3", str(N5_ROOT / "scripts/n5_protect.py"), "check", path],
        capture_output=True,
        text=True
    )
    if "PROTECTED" in result.stdout:
        # Extract reason from output
        lines = result.stdout.strip().split("\n")
        reason = lines[1].replace("Reason:", "").strip() if len(lines) > 1 else "Protected"
        return True, reason
    return False, ""

