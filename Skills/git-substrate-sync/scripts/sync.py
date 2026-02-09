#!/usr/bin/env python3
"""
Git Substrate Sync - va-side push operations
Handles pushing Tier 0 content from va to GitHub substrate repository.
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

# Import content classifier
sys.path.insert(0, "/home/workspace/Skills/content-classifier/scripts")
try:
    from scan import classify_path, build_manifest
except ImportError as e:
    print(f"ERROR: Cannot import content-classifier: {e}")
    print("Ensure content-classifier skill is available in Skills/content-classifier/")
    sys.exit(1)

# Configuration
WORKSPACE_ROOT = Path("/home/workspace")
TEMP_REPO_PATH = Path("/tmp/zoputer-substrate")
REPO_URL = "git@github.com:vrijenattawar/zoputer-substrate.git"
METADATA_DIR = WORKSPACE_ROOT / "N5/data/git-sync"
LAST_SYNC_FILE = METADATA_DIR / "last_sync.json"

def setup_metadata_dir():
    """Ensure metadata directory exists."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

def load_last_sync() -> Dict:
    """Load last sync state."""
    if LAST_SYNC_FILE.exists():
        try:
            return json.loads(LAST_SYNC_FILE.read_text())
        except Exception as e:
            print(f"Warning: Could not load last sync state: {e}")
    return {}

def save_sync_state(state: Dict):
    """Save sync state to file."""
    setup_metadata_dir()
    LAST_SYNC_FILE.write_text(json.dumps(state, indent=2))

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

def clone_or_pull_repo() -> bool:
    """Ensure we have a clean, up-to-date repo clone."""
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

def get_exportable_skills() -> List[Dict]:
    """Get list of Tier 0 skills using content classifier."""
    print("Running content classifier to identify Tier 0 skills...")
    try:
        manifest = build_manifest()
        tier_0_skills = []
        
        for bundle in manifest.get('bundles', []):
            if (bundle.get('tier') == 'Tier 0' and 
                bundle.get('path', '').startswith('Skills/') and
                bundle.get('name') != 'git-substrate-sync'):  # Don't export ourselves
                tier_0_skills.append(bundle)
        
        print(f"Found {len(tier_0_skills)} Tier 0 skills to export")
        return tier_0_skills
        
    except Exception as e:
        print(f"Error running content classifier: {e}")
        return []

def copy_skills_to_repo(skills: List[Dict], filter_skills: Optional[List[str]] = None) -> List[str]:
    """Copy skills to the substrate repo."""
    copied_skills = []
    skills_dir = TEMP_REPO_PATH / "Skills"
    skills_dir.mkdir(exist_ok=True)
    
    for skill in skills:
        skill_name = skill['name']
        
        # Filter by specific skills if requested
        if filter_skills and skill_name not in filter_skills:
            continue
            
        source_path = WORKSPACE_ROOT / skill['path']
        dest_path = skills_dir / skill_name
        
        if not source_path.exists():
            print(f"Warning: Source skill {source_path} does not exist, skipping")
            continue
            
        print(f"Copying skill: {skill_name}")
        
        # Remove existing destination if it exists
        if dest_path.exists():
            shutil.rmtree(dest_path)
            
        # Copy the skill directory
        shutil.copytree(source_path, dest_path)
        copied_skills.append(skill_name)
    
    return copied_skills

def update_manifest(copied_skills: List[str]) -> bool:
    """Update MANIFEST.json in the repository."""
    manifest_path = TEMP_REPO_PATH / "MANIFEST.json"
    
    # Get git SHA from workspace
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        git_sha = result.stdout.strip()
    except subprocess.CalledProcessError:
        git_sha = "unknown"
    
    manifest_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "va.zo.computer",
        "git_sha": git_sha,
        "exported_skills": copied_skills,
        "skill_count": len(copied_skills),
        "last_sync_operation": "push"
    }
    
    manifest_path.write_text(json.dumps(manifest_data, indent=2))
    print(f"Updated MANIFEST.json with {len(copied_skills)} skills")
    return True

def commit_and_push(operation_id: str, copied_skills: List[str]) -> bool:
    """Commit changes and push to repository."""
    # Configure git user if not set
    run_git_cmd(["git", "config", "user.email", "va@zo.computer"], TEMP_REPO_PATH, check=False)
    run_git_cmd(["git", "config", "user.name", "va.zo.computer"], TEMP_REPO_PATH, check=False)
    
    # Check for changes
    returncode, stdout, stderr = run_git_cmd(["git", "status", "--porcelain"], TEMP_REPO_PATH)
    if not stdout.strip():
        print("No changes to commit")
        return True
    
    # Show what changed
    print("Changes to commit:")
    print(stdout)
    
    # Add all changes
    run_git_cmd(["git", "add", "-A"], TEMP_REPO_PATH)
    
    # Commit with descriptive message
    commit_msg = f"Sync from va.zo.computer - {operation_id}\n\nExported skills: {', '.join(copied_skills)}"
    run_git_cmd(["git", "commit", "-m", commit_msg], TEMP_REPO_PATH)
    
    # Push to remote
    print("Pushing to remote repository...")
    try:
        run_git_cmd(["git", "push", "origin", "main"], TEMP_REPO_PATH)
        print("Successfully pushed to remote")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to remote: {e.stderr}")
        return False

def show_status():
    """Show sync status."""
    last_sync = load_last_sync()
    
    print("Git Substrate Sync Status")
    print("=" * 30)
    
    if last_sync:
        print(f"Last sync: {last_sync.get('timestamp', 'unknown')}")
        print(f"Operation: {last_sync.get('operation', 'unknown')}")
        print(f"Skills synced: {len(last_sync.get('exported_skills', []))}")
        if last_sync.get('exported_skills'):
            for skill in last_sync['exported_skills']:
                print(f"  - {skill}")
        print(f"Git SHA: {last_sync.get('git_sha', 'unknown')}")
    else:
        print("No previous sync found")
    
    # Get current Tier 0 skills
    skills = get_exportable_skills()
    print(f"\nCurrent Tier 0 skills: {len(skills)}")
    for skill in skills:
        print(f"  - {skill['name']}")

def show_history():
    """Show recent sync history."""
    # For now, just show the last sync
    # Could be expanded to show full history from audit logs
    last_sync = load_last_sync()
    
    print("Recent Sync History")
    print("=" * 20)
    
    if last_sync:
        print(f"Last operation: {last_sync.get('operation', 'unknown')}")
        print(f"Timestamp: {last_sync.get('timestamp', 'unknown')}")
        print(f"Skills: {', '.join(last_sync.get('exported_skills', []))}")
    else:
        print("No sync history found")

def test_classifier():
    """Test content classifier integration."""
    print("Testing content classifier integration...")
    
    try:
        # Test path classification
        test_path = WORKSPACE_ROOT / "Skills/content-classifier"
        tier, reason = classify_path(test_path)
        print(f"Test path classification: {tier} ({reason})")
        
        # Test manifest building
        manifest = build_manifest()
        print(f"Manifest contains {len(manifest.get('bundles', []))} bundles")
        
        # Test skill filtering
        skills = get_exportable_skills()
        print(f"Found {len(skills)} exportable skills")
        
        print("✓ Content classifier integration working")
        return True
        
    except Exception as e:
        print(f"✗ Content classifier integration failed: {e}")
        return False

def push_skills(dry_run: bool = False, filter_skills: Optional[List[str]] = None) -> bool:
    """Main push operation."""
    operation_id = f"push_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Starting push operation: {operation_id}")
    print(f"Dry run: {dry_run}")
    
    try:
        # Get Tier 0 skills
        skills = get_exportable_skills()
        if not skills:
            print("No Tier 0 skills found to export")
            return True
        
        # Filter skills if requested
        if filter_skills:
            skills = [s for s in skills if s['name'] in filter_skills]
            print(f"Filtered to {len(skills)} specific skills")
        
        if dry_run:
            print("DRY RUN - Would export the following skills:")
            for skill in skills:
                print(f"  - {skill['name']} (modified: {skill.get('last_modified', 'unknown')})")
            return True
        
        # Clone repository
        if not clone_or_pull_repo():
            return False
        
        # Copy skills
        copied_skills = copy_skills_to_repo(skills, filter_skills)
        if not copied_skills:
            print("No skills were copied")
            return False
        
        # Update manifest
        update_manifest(copied_skills)
        
        # Commit and push
        if not commit_and_push(operation_id, copied_skills):
            return False
        
        # Update sync state
        sync_state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "push",
            "operation_id": operation_id,
            "exported_skills": copied_skills,
            "git_sha": "updated",  # Could get actual SHA if needed
            "success": True
        }
        save_sync_state(sync_state)
        
        print(f"✓ Push complete: {len(copied_skills)} skills synchronized")
        return True
        
    except Exception as e:
        print(f"✗ Push failed: {e}")
        return False
        
    finally:
        # Clean up temp directory
        if TEMP_REPO_PATH.exists():
            shutil.rmtree(TEMP_REPO_PATH)

def main():
    parser = argparse.ArgumentParser(description="Git Substrate Sync - Push operations")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Push command
    push_parser = subparsers.add_parser("push", help="Push Tier 0 skills to substrate repo")
    push_parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    push_parser.add_argument("--skills", help="Comma-separated list of specific skills to push")
    
    # Status command
    subparsers.add_parser("status", help="Show sync status")
    
    # History command
    subparsers.add_parser("history", help="Show sync history")
    
    # Test command
    subparsers.add_parser("test", help="Test content classifier integration")
    
    args = parser.parse_args()
    
    if args.command == "push":
        filter_skills = None
        if args.skills:
            filter_skills = [s.strip() for s in args.skills.split(",")]
        
        success = push_skills(dry_run=args.dry_run, filter_skills=filter_skills)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        show_status()
    
    elif args.command == "history":
        show_history()
    
    elif args.command == "test":
        success = test_classifier()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()