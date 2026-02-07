#!/usr/bin/env python3
"""
Skill Bundle Creator for Zoffice Consultancy Stack

Creates tarballs of skills with metadata and checksums for export to zoputer.

Usage:
    python3 bundle_skill.py --skill content-classifier --output /tmp/bundle.tar.gz
    python3 bundle_skill.py --skill security-gate --version 1.2.0 --notes "Bug fix"
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE_ROOT = Path("/home/workspace")
SKILLS_DIR = WORKSPACE_ROOT / "Skills"
ZO_INSTANCE = "va"


def compute_file_checksum(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def get_git_sha() -> str:
    """Get the current git SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def get_git_changes_since(since_sha: Optional[str], skill_path: Path) -> bool:
    """Check if skill has changes since a given git SHA."""
    if not since_sha or since_sha == "unknown":
        return True  # Assume changed if no reference
    
    try:
        rel_path = skill_path.relative_to(WORKSPACE_ROOT)
        result = subprocess.run(
            ["git", "diff", "--name-only", since_sha, "HEAD", "--", str(rel_path)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return True  # Assume changed on error


def collect_skill_files(skill_path: Path) -> List[Path]:
    """Collect all files in a skill directory."""
    files = []
    for item in skill_path.rglob("*"):
        if item.is_file():
            # Skip common excludes
            rel = item.relative_to(skill_path)
            if any(part.startswith(".") for part in rel.parts):
                continue
            if any(part in ["__pycache__", "node_modules", ".git"] for part in rel.parts):
                continue
            files.append(item)
    return sorted(files)


def create_metadata(
    skill_name: str,
    skill_path: Path,
    version: str,
    files: List[Path],
    notes: str = "",
) -> Dict:
    """Create metadata.json content for a skill bundle."""
    checksums = {}
    file_list = []
    
    for f in files:
        rel_path = str(f.relative_to(skill_path))
        file_list.append(rel_path)
        checksums[rel_path] = compute_file_checksum(f)
    
    return {
        "name": skill_name,
        "version": version,
        "exported_from": f"{ZO_INSTANCE}.zo.computer",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": get_git_sha(),
        "files": file_list,
        "checksums": checksums,
        "notes": notes,
        "bundle_checksum": "",  # Filled after tarball creation
    }


def create_bundle(
    skill_name: str,
    output_path: Path,
    version: str = "1.0.0",
    notes: str = "",
    dry_run: bool = False,
) -> Dict:
    """
    Create a skill bundle tarball.
    
    Returns:
        Dict with bundle info including path and checksum
    """
    skill_path = SKILLS_DIR / skill_name
    
    if not skill_path.exists():
        raise ValueError(f"Skill not found: {skill_path}")
    
    if not (skill_path / "SKILL.md").exists():
        raise ValueError(f"Skill missing SKILL.md: {skill_path}")
    
    # Collect files
    files = collect_skill_files(skill_path)
    
    if not files:
        raise ValueError(f"No files found in skill: {skill_path}")
    
    # Create metadata
    metadata = create_metadata(skill_name, skill_path, version, files, notes)
    
    if dry_run:
        return {
            "skill": skill_name,
            "version": version,
            "files": len(files),
            "metadata": metadata,
            "dry_run": True,
        }
    
    # Create tarball
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    tarball_name = f"{skill_name}-v{version}-{timestamp}.tar.gz"
    
    if output_path.is_dir():
        final_path = output_path / tarball_name
    else:
        final_path = output_path
    
    final_path.parent.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write metadata
        metadata_path = Path(tmpdir) / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        # Create tarball
        with tarfile.open(final_path, "w:gz") as tar:
            # Add all skill files
            for f in files:
                arcname = f.relative_to(skill_path)
                tar.add(f, arcname=arcname)
            
            # Add metadata
            tar.add(metadata_path, arcname="metadata.json")
    
    # Compute bundle checksum
    bundle_checksum = compute_file_checksum(final_path)
    
    # Update metadata in the tarball with bundle checksum
    # (We'd need to recreate the tarball for this, so just return it separately)
    
    return {
        "skill": skill_name,
        "version": version,
        "path": str(final_path),
        "size_bytes": final_path.stat().st_size,
        "files": len(files),
        "checksum": bundle_checksum,
        "metadata": metadata,
    }


def main():
    parser = argparse.ArgumentParser(description="Create skill bundle for export")
    parser.add_argument("--skill", required=True, help="Skill name to bundle")
    parser.add_argument("--output", required=True, help="Output path (file or directory)")
    parser.add_argument("--version", default="1.0.0", help="Version string")
    parser.add_argument("--notes", default="", help="Export notes")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        result = create_bundle(
            skill_name=args.skill,
            output_path=Path(args.output),
            version=args.version,
            notes=args.notes,
            dry_run=args.dry_run,
        )
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if args.dry_run:
                print(f"[DRY RUN] Would create bundle for: {args.skill}")
                print(f"  Version: {result['version']}")
                print(f"  Files: {result['files']}")
            else:
                print(f"Created bundle: {result['path']}")
                print(f"  Skill: {result['skill']} v{result['version']}")
                print(f"  Files: {result['files']}")
                print(f"  Size: {result['size_bytes']} bytes")
                print(f"  Checksum: {result['checksum']}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
