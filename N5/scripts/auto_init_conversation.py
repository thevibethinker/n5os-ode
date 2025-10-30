#!/usr/bin/env python3
"""
Automatic Conversation Initialization Hook
Ensures every conversation gets properly initialized with SESSION_STATE and database entry

This runs automatically when a conversation workspace is detected without initialization.
"""

import sys
import subprocess
from pathlib import Path

def check_and_init_conversation(workspace_path: Path) -> bool:
    """
    Check if conversation needs initialization and do it
    
    Args:
        workspace_path: Path to conversation workspace
        
    Returns:
        True if initialized or already initialized, False if failed
    """
    session_state = workspace_path / "SESSION_STATE.md"
    
    # Already initialized
    if session_state.exists():
        return True
    
    # Extract conversation ID
    convo_id = workspace_path.name
    if not convo_id.startswith("con_"):
        return False
    
    # Run initialization
    try:
        cmd = [
            sys.executable,
            "/home/workspace/N5/scripts/session_state_manager.py",
            "init",
            "--convo-id", convo_id,
            "--load-system"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✓ Auto-initialized conversation: {convo_id}")
            return True
        else:
            print(f"⚠️  Failed to initialize {convo_id}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing {convo_id}: {e}")
        return False


def scan_and_init_all_conversations():
    """Scan all conversation workspaces and initialize any that need it"""
    workspaces_dir = Path("/home/.z/workspaces")
    
    if not workspaces_dir.exists():
        return
    
    initialized = 0
    failed = 0
    
    for workspace in workspaces_dir.iterdir():
        if not workspace.is_dir():
            continue
            
        if not workspace.name.startswith("con_"):
            continue
        
        session_state = workspace / "SESSION_STATE.md"
        if session_state.exists():
            continue
        
        # Needs initialization
        if check_and_init_conversation(workspace):
            initialized += 1
        else:
            failed += 1
    
    if initialized > 0 or failed > 0:
        print(f"\n✓ Initialized: {initialized}")
        if failed > 0:
            print(f"❌ Failed: {failed}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Initialize specific conversation
        workspace = Path(sys.argv[1])
        if workspace.exists():
            success = check_and_init_conversation(workspace)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Workspace not found: {workspace}")
            sys.exit(1)
    else:
        # Scan all
        scan_and_init_all_conversations()
