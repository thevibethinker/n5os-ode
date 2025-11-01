#!/usr/bin/env python3
"""
Monthly System Audit - Comprehensive System Health Check

Runs monthly on the 1st at 20:00 ET.
Model: Claude Sonnet 4.5
"""

import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
log_dir = Path("/home/workspace/N5/logs/maintenance/monthly")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"{datetime.now().strftime('%Y-%m')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

BACKUP_RETENTION_MONTHS = 6
CRITICAL_FILES = [
    "/home/workspace/Documents/N5.md",
    "/home/workspace/N5/prefs/prefs.md",
    "/home/workspace/Prompts/executables.db",
]


def git_governance_audit():
    """Run comprehensive git governance audit."""
    logger.info("=== Git Governance Audit ===")
    issues = []
    
    try:
        os.chdir("/home/workspace")
        
        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                logger.warning(f"Uncommitted changes: {len(changes.split(chr(10)))} files")
                issues.append("uncommitted_changes")
            else:
                logger.info("✓ Git working tree is clean")
        
        # Check for untracked important files
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "N5/"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            untracked = result.stdout.strip()
            if untracked:
                # Filter for important files (not generated/temp)
                important_untracked = [
                    f for f in untracked.split('\n')
                    if f and not any(x in f for x in ['index.md', 'runtime/', 'exports/', '.backup'])
                ]
                
                if important_untracked:
                    logger.warning(f"Untracked important files detected: {len(important_untracked)}")
                    for f in important_untracked[:10]:
                        logger.warning(f"  - {f}")
                    issues.append("untracked_files")
                else:
                    logger.info("✓ No untracked important files")
            else:
                logger.info("✓ No untracked files")
        
        # Check recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Recent commits: {len(result.stdout.strip().split(chr(10)))}")
        
    except subprocess.TimeoutExpired:
        logger.error("Git audit timed out")
        issues.append("timeout")
    except Exception as e:
        logger.error(f"Git audit error: {e}")
        issues.append("error")
    
    return issues


def verify_critical_backups():
    """Verify all critical files have backups."""
    logger.info("=== Critical File Backup Verification ===")
    issues = []
    
    backup_dir = Path("/home/workspace/N5/backups")
    
    if not backup_dir.exists():
        logger.error("Backup directory does not exist")
        return ["no_backup_dir"]
    
    for filepath in CRITICAL_FILES:
        filename = Path(filepath).name
        backups = list(backup_dir.rglob(f"*{filename}*"))
        
        if backups:
            logger.info(f"✓ {filename}: {len(backups)} backup(s) found")
        else:
            logger.error(f"✗ {filename}: NO BACKUPS FOUND")
            issues.append(f"no_backup_{filename}")
    
    return issues


def index_validation():
    """Validate N5 index integrity."""
    logger.info("=== Index Validation ===")
    issues = []
    
    index_jsonl = Path("/home/workspace/Documents/N5.jsonl")
    index_md = Path("/home/workspace/Documents/N5.md")
    
    # Check if index files exist
    if not index_jsonl.exists():
        logger.warning("N5.jsonl does not exist (may need rebuild)")
        issues.append("index_jsonl_missing")
    else:
        # Validate JSONL format
        try:
            with open(index_jsonl, 'r') as f:
                entry_count = 0
                for line in f:
                    if line.strip():
                        json.loads(line)
                        entry_count += 1
            logger.info(f"✓ N5.jsonl valid ({entry_count} entries)")
        except Exception as e:
            logger.error(f"N5.jsonl validation failed: {e}")
            issues.append("index_jsonl_invalid")
    
    if not index_md.exists():
        logger.error("N5.md does not exist")
        issues.append("index_md_missing")
    else:
        size = index_md.stat().st_size
        if size == 0:
            logger.error("N5.md is empty")
            issues.append("index_md_empty")
        else:
            logger.info(f"✓ N5.md exists ({size} bytes)")
    
    return issues


def backup_rotation():
    """Remove backups older than retention period."""
    logger.info("=== Backup Rotation ===")
    
    backup_dir = Path("/home/workspace/N5/backups")
    cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_MONTHS * 30)
    
    deleted_count = 0
    space_freed = 0
    
    if not backup_dir.exists():
        logger.warning("No backup directory found")
        return deleted_count, space_freed
    
    for backup_file in backup_dir.rglob('*'):
        if backup_file.is_file():
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    size = backup_file.stat().st_size
                    backup_file.unlink()
                    deleted_count += 1
                    space_freed += size
                    
                    logger.info(f"Deleted old backup: {backup_file.name} (age: {(datetime.now() - mtime).days} days)")
                except Exception as e:
                    logger.error(f"Failed to delete {backup_file}: {e}")
    
    logger.info(f"✓ Deleted {deleted_count} old backup(s), freed {space_freed // 1024 // 1024} MB")
    return deleted_count, space_freed


def generate_system_report(git_issues, backup_issues, index_issues, rotation_stats):
    """Generate comprehensive system health report."""
    logger.info("=== Monthly System Audit Report ===")
    
    total_issues = len(git_issues) + len(backup_issues) + len(index_issues)
    
    logger.info(f"Git governance issues: {len(git_issues)}")
    logger.info(f"Backup issues: {len(backup_issues)}")
    logger.info(f"Index issues: {len(index_issues)}")
    logger.info(f"Backup rotation: {rotation_stats[0]} files deleted, {rotation_stats[1] // 1024 // 1024} MB freed")
    
    if total_issues == 0:
        logger.info("✅ SYSTEM IS HEALTHY - All checks passed")
        return True
    else:
        logger.warning(f"⚠️  {total_issues} system issue(s) detected - Review required")
        return False


def main():
    """Run monthly system audit."""
    logger.info("=== Monthly System Audit Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Backup retention policy: {BACKUP_RETENTION_MONTHS} months")
    
    git_issues = git_governance_audit()
    backup_issues = verify_critical_backups()
    index_issues = index_validation()
    rotation_stats = backup_rotation()
    
    success = generate_system_report(git_issues, backup_issues, index_issues, rotation_stats)
    
    logger.info(f"=== Monthly System Audit Completed ===")
    logger.info(f"Log saved to: {log_file}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
