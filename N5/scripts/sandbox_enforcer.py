#!/usr/bin/env python3
"""
Sandbox Enforcer - Validates file creation follows sandbox-first protocol

Principles: P5 (Anti-Overwrite), P7 (Dry-Run), P18 (Verify State), P21 (Document Assumptions)

Usage:
    from sandbox_enforcer import validate_file_path, get_sandbox_path
    
    # Check if path is valid for creation
    is_valid, message = validate_file_path(target_path, convo_id, declared_artifacts)
    if not is_valid:
        raise ValueError(message)
"""

import logging
import sys
from pathlib import Path
from typing import Tuple, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
SANDBOX_ROOT = Path("/home/.z/workspaces")

# Exceptions: paths that can always be written without declaration
EXCEPTION_PATHS = [
    "/home/workspace/N5/logs/",
    "/home/workspace/N5/data/",
    "/tmp/",
]


def get_sandbox_path(convo_id: str) -> Path:
    """Get sandbox path for conversation."""
    return SANDBOX_ROOT / convo_id


def is_exception_path(path: Path) -> bool:
    """Check if path is in exception list (always writable)."""
    path_str = str(path.resolve())
    return any(path_str.startswith(exc) for exc in EXCEPTION_PATHS)


def is_in_sandbox(path: Path, convo_id: str) -> bool:
    """Check if path is within conversation sandbox."""
    sandbox = get_sandbox_path(convo_id)
    try:
        path.resolve().relative_to(sandbox.resolve())
        return True
    except ValueError:
        return False


def is_in_workspace(path: Path) -> bool:
    """Check if path is within user workspace."""
    try:
        path.resolve().relative_to(WORKSPACE_ROOT.resolve())
        return True
    except ValueError:
        return False


def validate_file_path(
    target_path: str,
    convo_id: str,
    declared_permanent: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Validate if file path follows sandbox-first protocol.
    
    Rules:
    1. Exception paths (logs, data, tmp) → ALLOW
    2. Sandbox paths → ALLOW
    3. Workspace paths NOT declared as permanent → DENY with error
    4. Workspace paths declared as permanent → ALLOW
    
    Args:
        target_path: Path to validate
        convo_id: Current conversation ID
        declared_permanent: List of paths declared as permanent artifacts
    
    Returns:
        (is_valid, message): Tuple of validation result and explanation
    """
    path = Path(target_path)
    declared_permanent = declared_permanent or []
    
    # Rule 1: Exception paths always allowed
    if is_exception_path(path):
        logger.debug(f"✓ Exception path: {path}")
        return True, "Exception path (logs/data/tmp)"
    
    # Rule 2: Sandbox paths always allowed
    if is_in_sandbox(path, convo_id):
        logger.debug(f"✓ Sandbox path: {path}")
        return True, "Sandbox file (temporary by default)"
    
    # Rule 3 & 4: Workspace paths require declaration
    if is_in_workspace(path):
        path_str = str(path.resolve())
        
        # Check if declared
        for declared in declared_permanent:
            declared_resolved = str((WORKSPACE_ROOT / declared).resolve())
            if path_str == declared_resolved or path_str.startswith(declared_resolved + "/"):
                logger.info(f"✓ Declared permanent: {path}")
                return True, "Declared as permanent artifact"
        
        # Not declared → DENY
        error_msg = f"""
⛔ SANDBOX VIOLATION ⛔

Attempted to create file outside sandbox without declaration:
  Path: {path}
  
RULE: All files must be created in sandbox unless explicitly declared as permanent.

Sandbox: {get_sandbox_path(convo_id)}

To create this file in workspace:
1. Declare it first:
   python3 /home/workspace/N5/scripts/session_state_manager.py declare-artifact \\
     --convo-id {convo_id} \\
     --path "{path.relative_to(WORKSPACE_ROOT) if path.is_relative_to(WORKSPACE_ROOT) else path}" \\
     --classification permanent \\
     --rationale "Why this file needs to be permanent"

2. Then create the file

OR: Create in sandbox instead (recommended for iterative work)

Declared permanent artifacts: {len(declared_permanent)}
{chr(10).join(f"  - {d}" for d in declared_permanent) if declared_permanent else "  (none)"}
"""
        logger.error(f"✗ Sandbox violation: {path}")
        return False, error_msg.strip()
    
    # Unknown location (not sandbox, not workspace)
    logger.warning(f"? Unknown location: {path}")
    return True, "Path outside standard locations (allowing)"


def check_file_creation(
    target_path: str,
    convo_id: str,
    declared_permanent: Optional[List[str]] = None,
    dry_run: bool = False
) -> bool:
    """
    Check if file creation is allowed. Raises ValueError if not.
    
    Args:
        target_path: Path to check
        convo_id: Current conversation ID
        declared_permanent: List of declared permanent artifacts
        dry_run: If True, only log, don't raise
    
    Returns:
        True if allowed
    
    Raises:
        ValueError: If path violates sandbox-first protocol
    """
    is_valid, message = validate_file_path(target_path, convo_id, declared_permanent)
    
    if not is_valid:
        if dry_run:
            logger.warning(f"DRY RUN: Would reject: {target_path}")
            logger.warning(message)
            return False
        else:
            raise ValueError(message)
    
    return True


def main() -> int:
    """CLI for testing validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate file paths against sandbox-first protocol")
    parser.add_argument("path", help="Path to validate")
    parser.add_argument("--convo-id", required=True, help="Conversation ID")
    parser.add_argument("--declared", nargs="*", default=[], help="List of declared permanent paths")
    parser.add_argument("--dry-run", action="store_true", help="Test mode")
    
    args = parser.parse_args()
    
    try:
        is_valid = check_file_creation(
            args.path,
            args.convo_id,
            declared_permanent=args.declared,
            dry_run=args.dry_run
        )
        
        if is_valid:
            print(f"✓ Valid: {args.path}")
            return 0
        else:
            print(f"✗ Invalid: {args.path}")
            return 1
            
    except ValueError as e:
        print(str(e))
        return 1
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
