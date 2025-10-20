#!/usr/bin/env python3
"""
N5 Deployment Packager
Scans N5 directory tree and generates atomic deployment manifest.

Principles: P2 (SSOT), P5 (Anti-Overwrite), P7 (Dry-Run), P18 (State Verification)
"""

import argparse
import base64
import hashlib
import json
import logging
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    ".git",
    "*.log",
    "zobridge.db",  # Don't overwrite existing database
    "data/*.json",  # Don't overwrite state files
    "node_modules",  # Exclude npm dependencies (run npm install on target)
    "logs/",  # Don't copy old logs
    "inbox/",  # Don't copy inbox data
    "backups/",  # Don't copy backups
    "*.db",  # Don't copy any database files
]


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of file content."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_mode(file_path: Path) -> str:
    """Get file permissions in octal format (e.g., '0755')."""
    return oct(stat.S_IMODE(os.stat(file_path).st_mode))


def scan_directory(
    source_dir: Path,
    exclude_patterns: Optional[List[str]] = None
) -> Dict:
    """
    Scan directory and generate deployment manifest.
    
    Returns dict with:
    - files: List of file entries with content, hash, mode
    - directories: List of directory paths to create
    - metadata: Summary stats
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Add default exclusions
    default_exclusions = [
        "__pycache__",
        "*.pyc",
        ".git",
    ]
    exclude_patterns = list(set(exclude_patterns + default_exclusions))
    
    files = []
    directories = set()
    total_size = 0
    
    logger.info(f"Scanning {source_dir}...")
    logger.info(f"Excluding patterns: {exclude_patterns}")
    
    for root, dirs, filenames in os.walk(source_dir):
        # Filter out excluded directories (must modify dirs in-place)
        original_dirs = dirs[:]
        dirs[:] = []
        for d in original_dirs:
            # Check if directory name matches any exclusion pattern
            excluded = False
            for pattern in exclude_patterns:
                pattern_clean = pattern.rstrip('/')
                if d == pattern_clean or d.startswith(pattern_clean):
                    excluded = True
                    break
            if not excluded:
                dirs.append(d)
        
        rel_root = Path(root).relative_to(source_dir)
        
        # Track directories
        if rel_root != Path('.'):
            directories.add(str(rel_root))
        
        for filename in filenames:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(source_dir)
            
            # Skip excluded file patterns
            excluded = False
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    # Wildcard pattern
                    if str(rel_path).endswith(pattern[1:]):
                        excluded = True
                        break
                elif '/' not in pattern and filename == pattern:
                    # Exact filename match
                    excluded = True
                    break
            
            if excluded:
                logger.debug(f"Skipping excluded: {rel_path}")
                continue
            
            try:
                # Read file content
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Encode as base64
                content_b64 = base64.b64encode(content).decode('utf-8')
                
                # Calculate hash
                sha256 = calculate_sha256(file_path)
                
                # Get permissions
                mode = get_file_mode(file_path)
                
                file_entry = {
                    "path": str(rel_path),
                    "content": content_b64,
                    "mode": mode,
                    "sha256": sha256,
                    "size_bytes": len(content)
                }
                
                files.append(file_entry)
                total_size += len(content)
                
                logger.debug(f"Added: {rel_path} ({len(content)} bytes)")
                
            except Exception as e:
                logger.error(f"Failed to process {rel_path}: {e}")
                raise
    
    # Sort for determinism
    files.sort(key=lambda x: x['path'])
    directories = sorted(directories)
    
    logger.info(f"✓ Scanned {len(files)} files, {len(directories)} directories")
    logger.info(f"  Total size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    
    return {
        "files": files,
        "directories": directories,
        "metadata": {
            "total_files": len(files),
            "total_directories": len(directories),
            "total_size_bytes": total_size
        }
    }


def generate_manifest(
    source_dir: Path,
    deployment_id: str,
    source_system: str,
    target_path: str = "/home/workspace/N5",
    exclude_patterns: Optional[List[str]] = None
) -> Dict:
    """Generate complete deployment manifest."""
    
    logger.info(f"Generating manifest: {deployment_id}")
    
    # Scan directory
    scan_result = scan_directory(source_dir, exclude_patterns)
    
    # Build manifest
    manifest = {
        "manifest_version": "1.0.0",
        "deployment_id": deployment_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_system": source_system,
        "target_path": target_path,
        "files": scan_result["files"],
        "directories": scan_result["directories"],
        "metadata": scan_result["metadata"]
    }
    
    return manifest


def save_manifest(manifest: Dict, output_path: Path, dry_run: bool = False) -> bool:
    """Save manifest to JSON file with verification."""
    
    if dry_run:
        logger.info(f"[DRY RUN] Would save manifest to: {output_path}")
        logger.info(f"[DRY RUN] Manifest size: {len(json.dumps(manifest)):,} bytes")
        return True
    
    try:
        # Write manifest
        logger.info(f"Writing manifest to: {output_path}")
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Verify (P18 - State Verification)
        if not output_path.exists():
            logger.error(f"Verification failed: {output_path} does not exist")
            return False
        
        if output_path.stat().st_size == 0:
            logger.error(f"Verification failed: {output_path} is empty")
            return False
        
        # Validate JSON structure
        with open(output_path, 'r') as f:
            loaded = json.load(f)
        
        if loaded.get("manifest_version") != manifest["manifest_version"]:
            logger.error("Verification failed: manifest_version mismatch")
            return False
        
        logger.info(f"✓ Manifest saved and verified: {output_path}")
        logger.info(f"  Size: {output_path.stat().st_size:,} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save manifest: {e}", exc_info=True)
        return False


def main(
    source_dir: str,
    output_file: str,
    deployment_id: str,
    source_system: str,
    target_path: str = "/home/workspace/N5",
    exclude: Optional[List[str]] = None,
    dry_run: bool = False
) -> int:
    """Main entry point."""
    
    try:
        source_path = Path(source_dir).resolve()
        output_path = Path(output_file).resolve()
        
        # Validate source
        if not source_path.exists():
            logger.error(f"Source directory does not exist: {source_path}")
            return 1
        
        if not source_path.is_dir():
            logger.error(f"Source is not a directory: {source_path}")
            return 1
        
        # Anti-overwrite check (P5)
        if output_path.exists() and not dry_run:
            logger.warning(f"Output file exists: {output_path}")
            logger.info("Use --force to overwrite (not implemented yet)")
            return 1
        
        # Generate manifest
        manifest = generate_manifest(
            source_path,
            deployment_id,
            source_system,
            target_path,
            exclude
        )
        
        # Save manifest
        if not save_manifest(manifest, output_path, dry_run):
            return 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("Manifest Generation Complete")
        logger.info(f"  Deployment ID: {deployment_id}")
        logger.info(f"  Files: {manifest['metadata']['total_files']}")
        logger.info(f"  Directories: {manifest['metadata']['total_directories']}")
        logger.info(f"  Total size: {manifest['metadata']['total_size_bytes']:,} bytes")
        if not dry_run:
            logger.info(f"  Output: {output_path}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate N5 deployment manifest"
    )
    parser.add_argument(
        "source_dir",
        help="Source N5 directory to package"
    )
    parser.add_argument(
        "output_file",
        help="Output manifest JSON file"
    )
    parser.add_argument(
        "--deployment-id",
        default="n5_bootstrap_001",
        help="Deployment identifier (default: n5_bootstrap_001)"
    )
    parser.add_argument(
        "--source-system",
        default="va",
        help="Source system identifier (default: va)"
    )
    parser.add_argument(
        "--target-path",
        default="/home/workspace/N5",
        help="Target path on destination system"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Patterns to exclude (can be used multiple times)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files"
    )
    
    args = parser.parse_args()
    
    exit(main(
        args.source_dir,
        args.output_file,
        args.deployment_id,
        args.source_system,
        args.target_path,
        args.exclude,
        args.dry_run
    ))
