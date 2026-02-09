#!/usr/bin/env python3
"""
Git Substrate Sync - zoputer-side pull operations
Handles pulling updates from GitHub substrate repository to zoputer.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration - Note: This script must be standalone for zoputer deployment
WORKSPACE_ROOT = Path("/home/workspace")  # Zoputer workspace
TEMP_REPO_PATH = Path("/tmp/zoputer-substrate")
REPO_URL = "git@github.com:vrijenattawar/zoputer-substrate.git"
METADATA_DIR = WORKSPACE_ROOT / "N5/data/git-sync"
LAST_PULL_FILE = METADATA_DIR / "last_pull.json"

def setup_metadata_dir():
    """Ensure metadata directory exists."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

def load_last_pull() -> Dict:
    """Load last pull state."""
    if LAST_PULL_FILE.exists():
        try:
            return json.loads(LAST_PULL_FILE.read_text())
        except Exception as e:
            print(f"Warning: Could not load last pull state: {e}")
    return {}

def save_pull_state(state: Dict):
    """Save pull state to file."""
    setup_metadata_dir()
    LAST_PULL_FILE.write_text(json.dumps(state, indent=2))

def run_git_cmd(cmd: List[str], cwd: Path, check: bool = True) -> Tuple[int, str, str]:
    """Run git command and return result."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e.returncode, e.stdout, e.stderr

def clone_repo() -> bool:
    """Clone the substrate repository."""
    if TEMP_REPO_PATH.exists():
        print(f"Removing existing temp repo at {TEMP_REPO_PATH}")
        shutil.rmtree(TEMP_REPO_PATH)
    
    print(f"Cloning repository to {TEMP_REPO_PATH}")
    try:
        cmd = ["git", "clone", REPO_URL, str(TEMP_REPO_PATH)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Repository cloned successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        return False

def get_available_skills() -> List[str]:
    """Get list of available skills in the substrate repo."""
    skills_dir = TEMP_REPO_PATH / "Skills"
    if not skills_dir.exists():
        return []
    
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)
    
    return skills

def get_changes_since_last_pull() -> Tuple[List[str], str]:
    """Get list of skills that have changed since last pull."""
    last_pull = load_last_pull()
    last_git_sha = last_pull.get('git_sha', '')
    
    if not last_git_sha:
        # First pull - everything is new
        skills = get_available_skills()
        return skills, "first_pull"
    
    try:
        # Get current git SHA
        returncode, current_sha, stderr = run_git_cmd(
            ["git", "rev-parse", "HEAD"], 
            TEMP_REPO_PATH
        )
        
        if current_sha == last_git_sha:
            return [], "no_changes"
        
        # Get changed files since last pull
        returncode, changed_files, stderr = run_git_cmd(
            ["git", "diff", "--name-only", last_git_sha, current_sha],
            TEMP_REPO_PATH
        )
        
        # Extract skill names from changed paths
        changed_skills = set()
        for file_path in changed_files.split('\n'):
            if file_path.startswith('Skills/'):
                parts = file_path.split('/')
                if len(parts) >= 2:
                    changed_skills.add(parts[1])
        
        return list(changed_skills), "changes_detected"
        
    except subprocess.CalledProcessError as e:
        print(f"Error checking for changes: {e}")
        # Fall back to pulling all skills
        return get_available_skills(), "error_fallback"

def copy_skills_to_workspace(skills_to_update: List[str], dry_run: bool = False) -> List[str]:
    """Copy updated skills to the workspace."""
    updated_skills = []
    workspace_skills_dir = WORKSPACE_ROOT / "Skills"
    workspace_skills_dir.mkdir(exist_ok=True)
    
    for skill_name in skills_to_update:
        source_path = TEMP_REPO_PATH / "Skills" / skill_name
        dest_path = workspace_skills_dir / skill_name
        
        if not source_path.exists():
            print(f"Warning: Skill {skill_name} not found in substrate repo")
            continue
        
        print(f"{'[DRY RUN] ' if dry_run else ''}Updating skill: {skill_name}")
        
        if not dry_run:
            # Remove existing destination if it exists
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            # Copy the skill directory
            shutil.copytree(source_path, dest_path)
        
        updated_skills.append(skill_name)
    
    return updated_skills

def update_local_manifest():
    """Update local manifest with substrate info."""
    substrate_manifest_path = TEMP_REPO_PATH / "MANIFEST.json"
    if not substrate_manifest_path.exists():
        print("Warning: No MANIFEST.json found in substrate repo")
        return
    
    # Copy substrate manifest to workspace
    local_manifest_path = WORKSPACE_ROOT / "N5/data/substrate_manifest.json"
    local_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(substrate_manifest_path, local_manifest_path)
    print(f"Updated local manifest: {local_manifest_path}")

def pull_updates(dry_run: bool = False, verbose: bool = False) -> bool:
    """Main pull operation."""
    operation_id = f"pull_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Starting pull operation: {operation_id}")
    print(f"Dry run: {dry_run}")
    
    try:
        # Clone repository
        if not clone_repo():
            return False
        
        # Check for changes
        skills_to_update, change_status = get_changes_since_last_pull()
        
        if change_status == "no_changes":
            print("No changes detected since last pull")
            return True
        
        print(f"Change status: {change_status}")
        print(f"Skills to update: {len(skills_to_update)}")
        
        if verbose or dry_run:
            for skill in skills_to_update:
                print(f"  - {skill}")
        
        if not skills_to_update:
            print("No skills to update")
            return True
        
        if dry_run:
            print("DRY RUN - Would update the above skills")
            return True
        
        # Copy skills to workspace
        updated_skills = copy_skills_to_workspace(skills_to_update)
        
        # Update local manifest
        update_local_manifest()
        
        # Get current git SHA for tracking
        returncode, git_sha, stderr = run_git_cmd(
            ["git", "rev-parse", "HEAD"], 
            TEMP_REPO_PATH
        )
        
        # Update pull state
        pull_state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "pull",
            "operation_id": operation_id,
            "updated_skills": updated_skills,
            "git_sha": git_sha,
            "change_status": change_status,
            "success": True
        }
        save_pull_state(pull_state)
        
        print(f"✓ Pull complete: {len(updated_skills)} skills updated")
        
        if verbose:
            print("Updated skills:")
            for skill in updated_skills:
                print(f"  - {skill}")
        
        return True
        
    except Exception as e:
        print(f"✗ Pull failed: {e}")
        return False
        
    finally:
        # Clean up temp directory
        if TEMP_REPO_PATH.exists():
            shutil.rmtree(TEMP_REPO_PATH)

def show_status():
    """Show pull status."""
    last_pull = load_last_pull()
    
    print("Git Substrate Pull Status")
    print("=" * 30)
    
    if last_pull:
        print(f"Last pull: {last_pull.get('timestamp', 'unknown')}")
        print(f"Change status: {last_pull.get('change_status', 'unknown')}")
        print(f"Skills updated: {len(last_pull.get('updated_skills', []))}")
        if last_pull.get('updated_skills'):
            for skill in last_pull['updated_skills']:
                print(f"  - {skill}")
        print(f"Git SHA: {last_pull.get('git_sha', 'unknown')}")
    else:
        print("No previous pull found")
    
    # Show local manifest info if available
    manifest_path = WORKSPACE_ROOT / "N5/data/substrate_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            print(f"\nSubstrate manifest:")
            print(f"  Generated: {manifest.get('generated_at', 'unknown')}")
            print(f"  Source: {manifest.get('source', 'unknown')}")
            print(f"  Skills: {manifest.get('skill_count', 0)}")
        except Exception as e:
            print(f"Warning: Could not read substrate manifest: {e}")

def main():
    parser = argparse.ArgumentParser(description="Git Substrate Sync - Pull operations")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without doing it")
    parser.add_argument("--verbose", action="store_true", 
                       help="Show detailed output")
    parser.add_argument("--status", action="store_true", 
                       help="Show pull status")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    success = pull_updates(dry_run=args.dry_run, verbose=args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()