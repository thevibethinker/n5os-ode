#!/usr/bin/env python3
"""
SessionStart hook for N5OS integration.

Fires when Claude Code session begins (and after compaction).
- Creates/updates session-context.md with core N5OS context
- Loads critical architectural principles and safety rules
- Provides on-demand context loading guidance

This hook INFORMS Claude Code about N5OS, it doesn't override its planning.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from config import (
    log, emit_hook_result, get_session_context_path,
    get_timestamp, WORKSPACE
)

# Core principles to always load (IDs map to N5/prefs/principles/*.yaml)
CORE_PRINCIPLES = [
    "P02",  # Single Source of Truth
    "P05",  # Safety, Determinism, Anti-Overwrite
    "P08",  # Minimal Context, Maximal Clarity
    "P15",  # Complete Before Claiming
    "P16",  # Accuracy Over Sophistication
    "P22",  # Language Selection
]


def load_core_principles() -> str:
    """Load and format core architectural principles."""
    principles_dir = WORKSPACE / "N5/prefs/principles"
    loaded = []

    for pid in CORE_PRINCIPLES:
        # Find matching file
        matches = list(principles_dir.glob(f"{pid}_*.yaml"))
        if not matches:
            continue

        principle_file = matches[0]
        try:
            import yaml
            with open(principle_file) as f:
                p = yaml.safe_load(f)

            # Extract key info
            name = p.get("name", pid)
            purpose = p.get("purpose", "").strip()

            # Handle different principle structures
            pattern = p.get("pattern", {})
            if isinstance(pattern, dict):
                core_behavior = pattern.get("core_behavior", "").strip()
            else:
                core_behavior = str(pattern).strip() if pattern else ""

            # Some principles use 'directive' instead of 'pattern'
            if not core_behavior:
                core_behavior = p.get("directive", "").strip()

            # Format concisely
            entry = f"**{pid}: {name}**\n"
            if purpose:
                entry += f"{purpose}\n"
            if core_behavior:
                entry += f"*Behavior:* {core_behavior}\n"
            loaded.append(entry)
        except Exception as e:
            log(f"Failed to load {pid}: {e}", "WARN")

    if loaded:
        return "## Core Architectural Principles\n\n" + "\n".join(loaded)
    return ""


def load_critical_rules() -> str:
    """Load critical always-on rules from prefs."""
    rules = """## Critical Rules (Always Active)

**Safety & Consent**
- Never schedule anything without explicit consent
- Always support `--dry-run`; prefer simulation over immediate action
- Require explicit approval for side-effects (email, external API, file deletion)

**Command-First Operations**
- Check for registered prompts/workflows before improvising
- Priority: Recipe > Protocol > Script > Direct ops > Improvisation

**Approach Articulation**
Before non-trivial tasks, state: Task type, Method, Applicable principles, Key risks

**Protected Paths**
- Check before delete/move on: `N5/`, `Sites/`, `Personal/`
- Use `n5_protect_check` MCP tool for verification
"""
    return rules


def get_context_loading_guide() -> str:
    """Provide guidance on loading additional context."""
    return """## On-Demand Context Loading

Use `/load-context <context>` to load domain-specific preferences:

| Context | Use For |
|---------|---------|
| `system_ops` | System admin, file operations, git work |
| `content_generation` | Writing emails, documents, social posts |
| `crm_operations` | Contact management, stakeholder tracking |
| `code_work` | Code modifications, multi-file changes |
| `scheduling` | Creating scheduled tasks, calendar ops |
| `research` | Deep research, stakeholder analysis |
| `build` | Implementation, refactoring, engineering |
| `full` | Load all modules (use sparingly per P08) |

Or load specific files: `file 'N5/prefs/path/to/module.md'`
"""


def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())
    session_id = hook_input.get("session_id", "unknown")
    is_compact = hook_input.get("is_compact", False)

    log(f"Session {'resumed after compaction' if is_compact else 'started'}: {session_id}")

    # Check if session-context.md exists
    context_path = get_session_context_path(WORKSPACE)

    # Load core context components
    principles_section = load_core_principles()
    rules_section = load_critical_rules()
    loading_guide = get_context_loading_guide()

    if not context_path.exists():
        # Create initial session context with full N5OS context
        initial_context = f"""# Session Context

**Session ID:** {session_id}
**Started:** {get_timestamp()}

## N5OS Environment

You are working in V's N5OS environment on Zo Computer.

{principles_section}

{rules_section}

{loading_guide}

---

## Progress This Session

_Update this section as you complete work._

## Decisions Made

_Record key decisions here so they survive compaction._

## Next Steps

_What remains to be done._
"""
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(initial_context)
        log(f"Created session context with core N5OS principles: {context_path}")

    elif is_compact:
        # After compaction, the context file exists but Claude may need reminding
        # Don't overwrite - just log that it should be re-read
        log("Post-compaction: session-context.md exists, Claude should re-read it")

    # Emit result - we don't block, just inform
    emit_hook_result({
        "continue": True,
        "message": f"N5OS session {'resumed' if is_compact else 'initialized'}. Core principles loaded. Use /load-context for domain-specific prefs."
    })

if __name__ == "__main__":
    main()

