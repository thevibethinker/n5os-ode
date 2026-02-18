#!/usr/bin/env python3
"""
Learning Logger - Log learnings from zoputer client interactions.
Commits structured markdown files to zoputer/learnings branch for va review.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
WORKSPACE_ROOT = Path("/home/workspace")
LEARNINGS_DIR = WORKSPACE_ROOT / "Learnings"
AUTONOMY_CONFIG_PATH = WORKSPACE_ROOT / "N5/config/zoputer_autonomy.yaml"
TEMP_REPO_PATH = Path("/tmp/zoputer-substrate-learnings")
REPO_URL = "git@github.com:vrijenattawar/zoputer-substrate.git"
LEARNINGS_BRANCH = "zoputer/learnings"

VALID_CATEGORIES = [
    "client-preferences",
    "domain-knowledge", 
    "workflow-improvements",
    "mistakes-to-avoid"
]


def slugify(text: str) -> str:
    """Convert text to a safe filename slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text[:50]


def load_autonomy_config() -> Dict:
    """Load zoputer autonomy configuration."""
    if not AUTONOMY_CONFIG_PATH.exists():
        print(f"Warning: Autonomy config not found at {AUTONOMY_CONFIG_PATH}")
        print("Proceeding with default permissions (Learnings/ allowed)")
        return {
            "allowed_paths": ["Learnings/"],
            "forbidden_paths": []
        }
    
    try:
        import yaml
        with open(AUTONOMY_CONFIG_PATH) as f:
            config = yaml.safe_load(f)
        return config.get("file_permissions", {})
    except ImportError:
        # Fallback if yaml not available - parse simple structure
        print("Warning: PyYAML not available, using fallback parser")
        return {
            "allowed_paths": ["Learnings/"],
            "forbidden_paths": []
        }
    except Exception as e:
        print(f"Warning: Could not load autonomy config: {e}")
        return {
            "allowed_paths": ["Learnings/"],
            "forbidden_paths": []
        }


def check_autonomy_permission(filepath: str) -> Tuple[bool, str]:
    """Check if writing to filepath is permitted by autonomy config."""
    config = load_autonomy_config()
    allowed_paths = config.get("allowed_paths", [])
    forbidden_paths = config.get("forbidden_paths", [])
    
    # Check forbidden paths first
    for forbidden in forbidden_paths:
        if filepath.startswith(forbidden):
            return False, f"Path {filepath} is in forbidden list: {forbidden}"
    
    # Check allowed paths
    for allowed in allowed_paths:
        if filepath.startswith(allowed):
            return True, f"Path {filepath} permitted under: {allowed}"
    
    # Default: not allowed if not explicitly permitted
    return False, f"Path {filepath} not in allowed paths: {allowed_paths}"


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
        return e.returncode, e.stdout if e.stdout else "", e.stderr if e.stderr else ""


def setup_learnings_repo() -> bool:
    """Clone repo and checkout/create learnings branch."""
    # Clean up existing temp dir
    if TEMP_REPO_PATH.exists():
        shutil.rmtree(TEMP_REPO_PATH)
    
    print(f"Cloning repository to {TEMP_REPO_PATH}")
    try:
        subprocess.run(
            ["git", "clone", REPO_URL, str(TEMP_REPO_PATH)],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        return False
    
    # Configure git user
    run_git_cmd(["git", "config", "user.email", "zoputer@zo.computer"], TEMP_REPO_PATH, check=False)
    run_git_cmd(["git", "config", "user.name", "zoputer"], TEMP_REPO_PATH, check=False)
    
    # Try to checkout learnings branch, create if doesn't exist
    returncode, _, _ = run_git_cmd(
        ["git", "checkout", LEARNINGS_BRANCH],
        TEMP_REPO_PATH,
        check=False
    )
    
    if returncode != 0:
        # Branch doesn't exist, create it
        print(f"Creating new branch: {LEARNINGS_BRANCH}")
        run_git_cmd(["git", "checkout", "-b", LEARNINGS_BRANCH], TEMP_REPO_PATH)
    else:
        print(f"Checked out existing branch: {LEARNINGS_BRANCH}")
    
    return True


def create_learning_file(
    learning: str,
    source: str,
    category: str,
    dry_run: bool = False
) -> Optional[Path]:
    """Create a learning markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(learning[:30])
    filename = f"{timestamp}_{slug}.md"
    relative_path = f"Learnings/{category}/{filename}"
    
    # Check autonomy permission
    allowed, reason = check_autonomy_permission(relative_path)
    if not allowed:
        print(f"Permission denied: {reason}")
        raise PermissionError(f"Cannot write to {relative_path}: {reason}")
    
    print(f"Permission granted: {reason}")
    
    content = f"""---
created: {date.today()}
source: {source}
category: {category}
logged_by: zoputer
status: pending_review
timestamp: {datetime.now(timezone.utc).isoformat()}
---

# Learning

{learning}
"""
    
    if dry_run:
        print(f"DRY RUN - Would create: {relative_path}")
        print("Content:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        return None
    
    # Create in temp repo
    target_path = TEMP_REPO_PATH / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content)
    
    print(f"Created: {relative_path}")
    return target_path


def git_commit_and_push(filepath: Path, learning_summary: str) -> bool:
    """Commit the learning file and push to remote."""
    # Add the file
    relative_path = filepath.relative_to(TEMP_REPO_PATH)
    run_git_cmd(["git", "add", str(relative_path)], TEMP_REPO_PATH)
    
    # Commit
    commit_msg = f"Learning: {learning_summary[:50]}"
    if len(learning_summary) > 50:
        commit_msg += "..."
    
    returncode, _, stderr = run_git_cmd(
        ["git", "commit", "-m", commit_msg],
        TEMP_REPO_PATH,
        check=False
    )
    
    if returncode != 0:
        if "nothing to commit" in stderr:
            print("Nothing to commit (file unchanged)")
            return True
        print(f"Commit failed: {stderr}")
        return False
    
    print(f"Committed: {commit_msg}")
    
    # Push to learnings branch
    print(f"Pushing to {LEARNINGS_BRANCH}...")
    try:
        run_git_cmd(
            ["git", "push", "-u", "origin", LEARNINGS_BRANCH],
            TEMP_REPO_PATH
        )
        print("Successfully pushed to remote")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Push failed: {e.stderr}")
        return False


def list_learnings(category: Optional[str] = None) -> None:
    """List recent learnings from local Learnings directory."""
    print("Recent Learnings")
    print("=" * 40)
    
    if not LEARNINGS_DIR.exists():
        print("No learnings directory found")
        return
    
    categories = [category] if category else VALID_CATEGORIES
    
    for cat in categories:
        cat_dir = LEARNINGS_DIR / cat
        if not cat_dir.exists():
            continue
        
        files = sorted(cat_dir.glob("*.md"), reverse=True)[:5]
        if files:
            print(f"\n{cat}:")
            for f in files:
                # Extract first line of learning
                content = f.read_text()
                lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#') and not l.startswith('---')]
                summary = lines[0][:60] if lines else "(empty)"
                print(f"  - {f.stem}: {summary}")


def log_learning(
    learning: str,
    source: str,
    category: str,
    dry_run: bool = False
) -> bool:
    """Main function to log a learning."""
    print(f"Logging learning to category: {category}")
    print(f"Source: {source}")
    print(f"Learning: {learning[:100]}{'...' if len(learning) > 100 else ''}")
    print()
    
    if dry_run:
        create_learning_file(learning, source, category, dry_run=True)
        return True
    
    # Setup repo
    if not setup_learnings_repo():
        return False
    
    try:
        # Create the file
        filepath = create_learning_file(learning, source, category)
        if not filepath:
            return False
        
        # Commit and push
        if not git_commit_and_push(filepath, learning):
            return False
        
        # Also create local copy for reference
        local_path = LEARNINGS_DIR / category / filepath.name
        local_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filepath, local_path)
        print(f"Local copy created: {local_path.relative_to(WORKSPACE_ROOT)}")
        
        print()
        print("✓ Learning logged successfully")
        print(f"  Branch: {LEARNINGS_BRANCH}")
        print(f"  Status: pending_review")
        return True
        
    finally:
        # Cleanup
        if TEMP_REPO_PATH.exists():
            shutil.rmtree(TEMP_REPO_PATH)


def main():
    parser = argparse.ArgumentParser(
        description="Log learnings from zoputer client interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log a client preference
  %(prog)s --learning "Client prefers weekly updates" --source "con_abc" --category "client-preferences"
  
  # Dry run to preview
  %(prog)s --learning "Test" --source "test" --category "domain-knowledge" --dry-run
  
  # List recent learnings
  %(prog)s --list
  
Categories:
  client-preferences    - How clients like to work
  domain-knowledge      - Industry/technical learnings
  workflow-improvements - Better ways to do things
  mistakes-to-avoid     - What not to do
"""
    )
    
    parser.add_argument(
        "--learning", "-l",
        help="The learning to log (required unless --list)"
    )
    parser.add_argument(
        "--source", "-s",
        help="Source of the learning (conversation ID, client name, etc.)"
    )
    parser.add_argument(
        "--category", "-c",
        choices=VALID_CATEGORIES,
        help="Category for the learning"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recent learnings"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_learnings(args.category)
        return
    
    # Validate required args for logging
    if not args.learning:
        parser.error("--learning is required (unless using --list)")
    if not args.source:
        parser.error("--source is required")
    if not args.category:
        parser.error("--category is required")
    
    success = log_learning(
        learning=args.learning,
        source=args.source,
        category=args.category,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
