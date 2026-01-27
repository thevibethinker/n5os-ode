#!/usr/bin/env python3
"""PII audit for conversations."""

import subprocess
from pathlib import Path

def audit_conversation(convo_id: str, auto_mark: bool = True) -> dict:
    """Run PII audit on conversation workspace.
    
    Wraps existing N5/scripts/conversation_pii_audit.py
    """
    script = Path("/home/workspace/N5/scripts/conversation_pii_audit.py")
    
    if not script.exists():
        return {'status': 'skipped', 'reason': 'PII audit script not found'}
    
    cmd = ['python3', str(script), '--convo-id', convo_id]
    if auto_mark:
        cmd.append('--auto-mark')
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        'status': 'complete' if result.returncode == 0 else 'error',
        'stdout': result.stdout,
        'stderr': result.stderr
    }