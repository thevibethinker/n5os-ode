#!/usr/bin/env python3
"""
N5 File Protection System - Lightweight directory protection via marker files

Usage:
    n5_protect.py protect <path> --reason "description"
    n5_protect.py unprotect <path>
    n5_protect.py list
    n5_protect.py check <path>
    n5_protect.py auto-protect-services
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

MARKER_FILENAME = ".n5protected"
WORKSPACE = Path("/home/workspace")


def create_marker(directory: Path, reason: str, metadata: Optional[dict] = None) -> bool:
    """Create .n5protected marker file in directory"""
    try:
        directory = directory.resolve()
        if not directory.is_dir():
            logger.error(f"Not a directory: {directory}")
            return False
        
        marker_path = directory / MARKER_FILENAME
        
        if marker_path.exists():
            logger.warning(f"Already protected: {directory}")
            return True
        
        marker_data = {
            "protected": True,
            "reason": reason,
            "created": datetime.now(timezone.utc).isoformat(),
            "created_by": metadata.get("created_by", "user") if metadata else "user"
        }
        
        # Add optional metadata
        if metadata:
            for key, value in metadata.items():
                if key not in marker_data:
                    marker_data[key] = value
        
        marker_path.write_text(json.dumps(marker_data, indent=2) + "\n")
        logger.info(f"✓ Protected: {directory} (reason: {reason})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to protect {directory}: {e}", exc_info=True)
        return False


def remove_marker(directory: Path) -> bool:
    """Remove .n5protected marker file from directory"""
    try:
        directory = directory.resolve()
        marker_path = directory / MARKER_FILENAME
        
        if not marker_path.exists():
            logger.warning(f"Not protected: {directory}")
            return False
        
        marker_path.unlink()
        logger.info(f"✓ Unprotected: {directory}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to unprotect {directory}: {e}", exc_info=True)
        return False


def check_protected(path: Path) -> Optional[dict]:
    """
    Check if path or any parent directory is protected.
    Returns marker data if protected, None otherwise.
    """
    try:
        path = path.resolve()
        
        # Check path itself if directory
        if path.is_dir():
            marker = path / MARKER_FILENAME
            if marker.exists():
                return json.loads(marker.read_text())
        
        # Check all parent directories
        for parent in path.parents:
            marker = parent / MARKER_FILENAME
            if marker.exists():
                return json.loads(marker.read_text())
            
            # Stop at workspace root
            if parent == WORKSPACE:
                break
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to check protection for {path}: {e}", exc_info=True)
        return None


def list_protected() -> list[tuple[Path, dict]]:
    """Find all protected directories in workspace"""
    protected_dirs = []
    
    try:
        for marker_path in WORKSPACE.rglob(MARKER_FILENAME):
            directory = marker_path.parent
            try:
                marker_data = json.loads(marker_path.read_text())
                protected_dirs.append((directory, marker_data))
            except Exception as e:
                logger.warning(f"Invalid marker at {marker_path}: {e}")
        
        return protected_dirs
        
    except Exception as e:
        logger.error(f"Failed to list protected directories: {e}", exc_info=True)
        return []


def auto_protect_services() -> int:
    """
    Auto-protect all registered user service working directories.
    Returns count of newly protected directories.
    """
    protected_count = 0
    
    try:
        # Import here to avoid circular dependencies
        import subprocess
        import json as json_module
        
        # Get list of user services
        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/n5_user_services.py", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            logger.error("Failed to list user services")
            return 0
        
        # Parse service list (assuming JSON output)
        # If services script doesn't output JSON, we'll need to adjust
        logger.info("Checking user services for auto-protection...")
        
        # For now, we'll scan known service directories
        # This will be enhanced when we integrate with service registration
        service_dirs = [
            "/home/workspace/n5-waitlist",
            "/home/workspace/Projects/streaming-player-setup",
            "/home/workspace/.n5_bootstrap_server",
            "/home/workspace/N5/services/zobridge",
        ]
        
        for dir_path in service_dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                marker_path = path / MARKER_FILENAME
                if not marker_path.exists():
                    if create_marker(
                        path,
                        reason="registered_service",
                        metadata={"created_by": "system", "auto_protected": True}
                    ):
                        protected_count += 1
        
        logger.info(f"✓ Auto-protected {protected_count} service directories")
        return protected_count
        
    except Exception as e:
        logger.error(f"Failed to auto-protect services: {e}", exc_info=True)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N5 File Protection System - Lightweight directory protection"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # protect command
    protect_parser = subparsers.add_parser("protect", help="Protect a directory")
    protect_parser.add_argument("path", type=Path, help="Directory to protect")
    protect_parser.add_argument("--reason", required=True, help="Reason for protection")
    
    # unprotect command
    unprotect_parser = subparsers.add_parser("unprotect", help="Unprotect a directory")
    unprotect_parser.add_argument("path", type=Path, help="Directory to unprotect")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if path is protected")
    check_parser.add_argument("path", type=Path, help="Path to check")
    
    # list command
    subparsers.add_parser("list", help="List all protected directories")
    
    # auto-protect-services command
    subparsers.add_parser(
        "auto-protect-services",
        help="Auto-protect all registered service directories"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "protect":
            return 0 if create_marker(args.path, args.reason) else 1
            
        elif args.command == "unprotect":
            return 0 if remove_marker(args.path) else 1
            
        elif args.command == "check":
            marker_data = check_protected(args.path)
            if marker_data:
                print(f"⚠️  PROTECTED: {args.path}")
                print(f"   Reason: {marker_data.get('reason', 'unknown')}")
                print(f"   Created: {marker_data.get('created', 'unknown')}")
                return 0
            else:
                print(f"✓ Not protected: {args.path}")
                return 1
                
        elif args.command == "list":
            protected = list_protected()
            if not protected:
                print("No protected directories found.")
                return 0
            
            print(f"Found {len(protected)} protected directories:\n")
            for directory, marker_data in sorted(protected):
                rel_path = directory.relative_to(WORKSPACE) if directory.is_relative_to(WORKSPACE) else directory
                reason = marker_data.get('reason', 'unknown')
                print(f"  🔒 {rel_path}")
                print(f"     Reason: {reason}")
                print()
            return 0
            
        elif args.command == "auto-protect-services":
            count = auto_protect_services()
            return 0 if count >= 0 else 1
            
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
