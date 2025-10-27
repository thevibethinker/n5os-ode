#!/usr/bin/env python3
"""
System Bulletins Generator
Scans git commits and conversations.db to create bulletin entries for significant changes.
Maintains a 10-day rolling window of system changes for AI context.
"""
import argparse
import json
import logging
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
BULLETIN_FILE = WORKSPACE / "N5/data/system_bulletins.jsonl"
STATE_FILE = WORKSPACE / "N5/data/.bulletin_state.json"
CONVERSATIONS_DB = WORKSPACE / "N5/data/conversations.db"
TTL_DAYS = 10

# Significance patterns (high to low priority)
SIGNIFICANT_PATTERNS = {
    'high': [
        'N5/scripts/*.py',
        'Knowledge/architectural/principles/*.md',
        'N5/prefs/*.md',
        'N5/schemas/*.json',
        'N5/config/commands.jsonl',
    ],
    'medium': [
        'N5/orchestration/*.md',
        'Documents/System/**/*.md',
        'Recipes/*.md',
        'Knowledge/**/*.md',
    ],
    'low': [
        'N5/**/*',
        'Documents/**/*',
    ]
}


def load_state() -> Dict:
    """Load last run state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: Dict) -> None:
    """Save current run state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_git_commits(since: Optional[str] = None) -> List[Dict]:
    """Get git commits since timestamp"""
    try:
        if since:
            cmd = ['git', 'log', f'--since={since}', '--name-status', '--format=%H|%ai|%s']
        else:
            # First run: backfill 10 days
            ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=TTL_DAYS)).isoformat()
            cmd = ['git', 'log', f'--since={ten_days_ago}', '--name-status', '--format=%H|%ai|%s']
        
        result = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True, check=True)
        
        commits = []
        current_commit = None
        
        for line in result.stdout.split('\n'):
            if '|' in line and len(line.split('|')) == 3:
                # Commit line
                commit_hash, timestamp, message = line.split('|', 2)
                current_commit = {
                    'hash': commit_hash.strip(),
                    'timestamp': timestamp.strip(),
                    'message': message.strip(),
                    'files': []
                }
                commits.append(current_commit)
            elif line.strip() and current_commit:
                # File change line (e.g., "M\tpath/to/file")
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    status, filepath = parts
                    current_commit['files'].append({'status': status, 'path': filepath})
        
        return commits
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return []


def assess_significance(filepath: str) -> Optional[str]:
    """Determine significance level of file change"""
    from fnmatch import fnmatch
    
    for level in ['high', 'medium', 'low']:
        for pattern in SIGNIFICANT_PATTERNS[level]:
            if fnmatch(filepath, pattern) or fnmatch(filepath, f'**/{pattern}'):
                return level
    return None


def get_conversation_changes(since: Optional[str] = None) -> List[Dict]:
    """Query conversations.db for significant changes"""
    if not CONVERSATIONS_DB.exists():
        logger.warning("conversations.db not found")
        return []
    
    try:
        conn = sqlite3.connect(CONVERSATIONS_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        changes = []
        
        # Get conversations with decisions, learnings, or artifacts
        if since:
            timestamp_filter = f"AND created_at > '{since}'"
        else:
            ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=TTL_DAYS)).isoformat()
            timestamp_filter = f"AND created_at > '{ten_days_ago}'"
        
        # Check for artifacts
        cursor.execute(f"""
            SELECT conversation_id, artifact_type, filepath, description, created_at
            FROM artifacts
            WHERE 1=1 {timestamp_filter}
            ORDER BY created_at DESC
        """)
        
        for row in cursor.fetchall():
            changes.append({
                'type': 'artifact',
                'conversation_id': row['conversation_id'],
                'artifact_type': row['artifact_type'],
                'filepath': row['filepath'],
                'description': row['description'],
                'timestamp': row['created_at']
            })
        
        # Check for learnings
        cursor.execute(f"""
            SELECT conversation_id, type, title, description, timestamp
            FROM learnings
            WHERE status = 'active' {timestamp_filter.replace('created_at', 'timestamp')}
            ORDER BY timestamp DESC
        """)
        
        for row in cursor.fetchall():
            # Infer significance from learning type
            learning_type = row['type']
            sig = 'high' if learning_type in ['principle', 'architecture'] else 'medium'
            
            changes.append({
                'type': 'learning',
                'conversation_id': row['conversation_id'],
                'learning_type': learning_type,
                'title': row['title'],
                'description': row['description'],
                'significance': sig,
                'timestamp': row['timestamp']
            })
        
        conn.close()
        return changes
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []


def generate_bulletin_id() -> str:
    """Generate unique bulletin ID"""
    from hashlib import sha256
    from time import time_ns
    hash_input = f"{time_ns()}".encode()
    return f"bul_{sha256(hash_input).hexdigest()[:12]}"


def create_bulletin_entry(change_type: str, scope: str, summary: str, details: str,
                         significance: str, conversation_id: Optional[str] = None,
                         files_affected: Optional[List[str]] = None,
                         git_commit: Optional[str] = None) -> Dict:
    """Create a bulletin entry"""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'bulletin_id': generate_bulletin_id(),
        'change_type': change_type,
        'scope': scope,
        'summary': summary,
        'details': details,
        'conversation_id': conversation_id,
        'files_affected': files_affected or [],
        'git_commit': git_commit,
        'significance': significance
    }


def process_git_commits(commits: List[Dict], dry_run: bool = False) -> List[Dict]:
    """Process git commits into bulletin entries"""
    bulletins = []
    
    for commit in commits:
        # Group files by significance
        high_files = []
        medium_files = []
        low_files = []
        
        for file_change in commit['files']:
            filepath = file_change['path']
            sig = assess_significance(filepath)
            
            if sig == 'high':
                high_files.append(filepath)
            elif sig == 'medium':
                medium_files.append(filepath)
            elif sig == 'low':
                low_files.append(filepath)
        
        # Create bulletin if significant files changed
        if high_files:
            bulletins.append(create_bulletin_entry(
                change_type='architecture' if any('architectural' in f or 'scripts' in f for f in high_files) else 'breaking_change',
                scope=', '.join(set(Path(f).parent.as_posix() for f in high_files[:3])),
                summary=commit['message'][:100],
                details=commit['message'],
                significance='high',
                files_affected=high_files,
                git_commit=commit['hash'][:8]
            ))
        elif medium_files:
            bulletins.append(create_bulletin_entry(
                change_type='workflow_changed' if any('orchestration' in f or 'Recipes' in f for f in medium_files) else 'documentation',
                scope=', '.join(set(Path(f).parent.as_posix() for f in medium_files[:3])),
                summary=commit['message'][:100],
                details=commit['message'],
                significance='medium',
                files_affected=medium_files,
                git_commit=commit['hash'][:8]
            ))
    
    return bulletins


def process_conversation_changes(changes: List[Dict], dry_run: bool = False) -> List[Dict]:
    """Process conversation changes into bulletin entries"""
    bulletins = []
    
    for change in changes:
        if change['type'] == 'learning':
            bulletins.append(create_bulletin_entry(
                change_type='learning_captured',
                scope='Knowledge',
                summary=f"Learning ({change['learning_type']}): {change['title'][:60]}",
                details=f"{change['title']}\n\n{change['description']}",
                significance=change.get('significance', 'medium'),
                conversation_id=change['conversation_id']
            ))
        elif change['type'] == 'artifact':
            bulletins.append(create_bulletin_entry(
                change_type='artifact_created',
                scope=change.get('artifact_type', 'unknown'),
                summary=f"Artifact: {Path(change['filepath']).name}",
                details=(change.get('description') or change['filepath'])[:200],
                significance='medium',
                conversation_id=change['conversation_id']
            ))
    
    return bulletins


def prune_old_entries(dry_run: bool = False) -> int:
    """Remove entries older than TTL_DAYS"""
    if not BULLETIN_FILE.exists():
        return 0
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=TTL_DAYS)
    kept = []
    pruned_count = 0
    
    with open(BULLETIN_FILE) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if entry_time >= cutoff:
                    kept.append(entry)
                else:
                    pruned_count += 1
    
    if not dry_run and kept:
        with open(BULLETIN_FILE, 'w') as f:
            for entry in kept:
                f.write(json.dumps(entry) + '\n')
    
    return pruned_count


def write_bulletins(bulletins: List[Dict], dry_run: bool = False) -> int:
    """Append bulletins to file"""
    if dry_run:
        logger.info(f"[DRY RUN] Would write {len(bulletins)} bulletins")
        for b in bulletins[:3]:
            logger.info(f"  - [{b['significance']}] {b['change_type']}: {b['summary']}")
        if len(bulletins) > 3:
            logger.info(f"  ... and {len(bulletins) - 3} more")
        return len(bulletins)
    
    BULLETIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(BULLETIN_FILE, 'a') as f:
        for bulletin in bulletins:
            f.write(json.dumps(bulletin) + '\n')
    
    return len(bulletins)


def main(dry_run: bool = False) -> int:
    """Main bulletin generation logic"""
    try:
        logger.info("Starting bulletin generation")
        
        # Load state
        state = load_state()
        last_run = state.get('last_run')
        
        if last_run:
            logger.info(f"Last run: {last_run}")
        else:
            logger.info("First run: backfilling 10 days")
        
        # Get changes
        git_commits = get_git_commits(since=last_run)
        conversation_changes = get_conversation_changes(since=last_run)
        
        logger.info(f"Found {len(git_commits)} git commits")
        logger.info(f"Found {len(conversation_changes)} conversation changes")
        
        # Process into bulletins
        git_bulletins = process_git_commits(git_commits, dry_run=dry_run)
        conv_bulletins = process_conversation_changes(conversation_changes, dry_run=dry_run)
        
        all_bulletins = git_bulletins + conv_bulletins
        
        # Write bulletins
        written = write_bulletins(all_bulletins, dry_run=dry_run)
        logger.info(f"Wrote {written} bulletins")
        
        # Prune old entries
        pruned = prune_old_entries(dry_run=dry_run)
        logger.info(f"Pruned {pruned} old entries")
        
        # Update state
        if not dry_run:
            state['last_run'] = datetime.now(timezone.utc).isoformat()
            state['last_bulletin_count'] = written
            save_state(state)
            logger.info(f"✓ State updated: {written} bulletins, {pruned} pruned")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate system bulletins from git and conversations.db")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
