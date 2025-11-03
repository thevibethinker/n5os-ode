#!/usr/bin/env python3
"""
Pipedream Helper - Bridge for Google Drive operations

IMPORTANT: This module cannot directly call Zo's Google Drive integration from
subprocess context. Scripts that need Google Drive access must be orchestrated
by Zo directly, not run as standalone subprocesses.

For meeting pipeline Google Drive operations, use the main pipeline orchestrator
that calls Zo tools directly rather than subprocess execution.
"""

def call_google_drive_tool(tool_name, configured_props):
    """
    Placeholder that documents the pattern
    
    This function exists to maintain compatibility with existing code but
    cannot actually execute in subprocess context.
    """
    raise NotImplementedError(
        "Google Drive operations must be orchestrated by Zo directly.\n"
        f"Attempted tool: {tool_name}\n"
        "Solution: Refactor to use Zo-orchestrated pipeline."
    )

if __name__ == "__main__":
    print("This helper requires Zo orchestration for Google Drive operations.")
    print("See N5/scripts/meeting_pipeline/README.md for architecture details.")
