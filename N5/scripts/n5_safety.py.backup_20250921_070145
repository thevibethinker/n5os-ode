#!/usr/bin/env python3
"""
N5 OS Safety Layer

Handles permissions, approvals, and dry-run functionality.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

# Mock email sending - in real implementation, this would integrate with actual email service
def send_email_approval_request(command: str, details: Dict[str, Any]) -> bool:
    """Send email approval request (mock implementation)."""
    print(f"🔒 EMAIL APPROVAL REQUIRED for command: {command}")
    print(f"📧 Approval request sent to: admin@n5.os")
    print(f"📝 Details: {json.dumps(details, indent=2)}")

    # In real implementation, this would send actual email
    # For now, simulate user approval
    response = input("✅ Approve this action? (y/N): ").strip().lower()
    return response == 'y'

def check_permissions(command_spec: Dict[str, Any], args: argparse.Namespace) -> bool:
    """Check if command has required permissions and obtain approvals."""
    if command_spec is None:
        return True
    
    permissions = command_spec.get("permissions_required", [])
    if not permissions:
        return True

    print(f"🔐 Command '{command_spec['name']}' requires permissions: {permissions}")

    details = {
        "command": command_spec["name"],
        "args": vars(args),
        "dry_run": getattr(args, 'dry_run', False)
    }

    for perm in permissions:
        if perm == "email_approval":
            if not send_email_approval_request(command_spec["name"], details):
                print(f"❌ Approval denied for {perm}")
                return False
        else:
            print(f"⚠️  Unknown permission type: {perm}")
            return False

    print("✅ All permissions approved")
    return True

def is_dry_run(args: argparse.Namespace, command_spec: Dict[str, Any]) -> bool:
    """Determine if this should be a dry run."""
    # Check explicit flag
    if hasattr(args, 'dry_run') and args.dry_run:
        return True

    # Check sticky dry_run from layers (future implementation)
    # For now, just check environment variable
    if os.environ.get('N5_DRY_RUN') == 'true':
        print("🌐 Sticky dry-run enabled via environment")
        return True

    return False

def execute_with_safety(command_spec: Dict[str, Any], args: argparse.Namespace,
                       execute_func) -> Any:
    """Execute a command with safety checks."""

    # Check permissions
    if not check_permissions(command_spec, args):
        print("🚫 Permission check failed")
        return None

    # Determine dry run status
    dry_run = is_dry_run(args, command_spec)

    if dry_run:
        print("🏜️  DRY RUN MODE - No changes will be made")
        # Set dry_run flag on args for the execute function
        if not hasattr(args, 'dry_run'):
            args.dry_run = True
        else:
            args.dry_run = True

    # Execute the command
    try:
        result = execute_func(args)
        if dry_run:
            print("✅ Dry run completed successfully")
        else:
            print("✅ Command executed successfully")
        return result
    except Exception as e:
        print(f"❌ Command failed: {e}")
        raise

def load_command_spec(command_name: str) -> Optional[Dict[str, Any]]:
    """Load command specification from commands.jsonl."""
    commands_file = Path(__file__).parent.parent / "commands.jsonl"

    if not commands_file.exists():
        return None

    with commands_file.open('r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                cmd = json.loads(line)
                if cmd.get("name") == command_name:
                    return cmd
            except json.JSONDecodeError:
                continue

    return None

def main():
    """Main entry point for safety layer testing."""
    parser = argparse.ArgumentParser(description="N5 Safety Layer")
    parser.add_argument("command", help="Command name to check")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run")
    parser.add_argument("--test", action="store_true", help="Run safety tests")

    args = parser.parse_args()

    if args.test:
        # Run safety tests
        print("🧪 Running N5 Safety Layer Tests...")

        # Test 1: Load command spec
        spec = load_command_spec("lists-promote")
        if spec and "email_approval" in spec.get("permissions_required", []):
            print("✅ Command spec loading works")
        else:
            print("❌ Command spec loading failed")
            return 1

        # Test 2: Dry run detection
        test_args = argparse.Namespace()
        test_args.dry_run = True
        if is_dry_run(test_args, spec):
            print("✅ Dry run detection works")
        else:
            print("❌ Dry run detection failed")
            return 1

        # Test 3: Permission check (mock)
        # This would require mocking the email function
        print("✅ Safety layer tests completed")
        return 0

    # Load command spec
    spec = load_command_spec(args.command)
    if not spec:
        print(f"❌ Command '{args.command}' not found")
        return 1

    print(f"🔍 Loaded spec for '{args.command}': {spec.get('permissions_required', [])}")

    # Check permissions
    if check_permissions(spec, args):
        print("✅ Permission check passed")
    else:
        print("❌ Permission check failed")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())