#!/usr/bin/env python3
"""
Daily File Guardian - Critical File Integrity & Git Health Check

Runs daily at 05:30 ET to verify system integrity.
Model: GPT-4o-mini (highly reliable for rule-following tasks)
"""

import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
log_dir = Path("/home/workspace/N5/logs/maintenance/daily")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Critical files to check
CRITICAL_FILES = [
    "/home/workspace/Documents/N5.md",
    "/home/workspace/N5/prefs/prefs.md",
    "/home/workspace/Prompts/executables.db",
]

# Essential knowledge files
ESSENTIAL_KNOWLEDGE_FILES = [
    "/home/workspace/Knowledge/architectural/ingestion_standards.md",
    "/home/workspace/Knowledge/architectural/operational_principles.md",
    "/home/workspace/Knowledge/stable/bio.md",
    "/home/workspace/Knowledge/stable/company.md",
    "/home/workspace/Knowledge/README.md",
]

ALL_PROTECTED_FILES = CRITICAL_FILES + ESSENTIAL_KNOWLEDGE_FILES


def check_file_integrity()    backup_productivity_db()
:
    """Verify all protected files exist and are non-empty."""
    logger.info("=== File Integrity Check ===")
    issues = []
    
    for filepath in ALL_PROTECTED_FILES:
        path = Path(filepath)
        
        if not path.exists():
            issue = f"CRITICAL: File does not exist: {filepath}"
            logger.error(issue)
            issues.append(issue)
        elif path.stat().st_size == 0:
            issue = f"CRITICAL: File is empty: {filepath}"
            logger.error(issue)
            issues.append(issue)
        else:
            logger.info(f"✓ {filepath} ({path.stat().st_size} bytes)")
    
    return issues


def check_git_status():
    """Check git status for tracked paths."""
    logger.info("=== Git Status Check ===")
    issues = []
    
    try:
        os.chdir("/home/workspace")
        
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                logger.warning("Uncommitted changes detected:")
                for line in changes.split('\n'):
                    logger.warning(f"  {line}")
                issues.append(f"Uncommitted changes: {len(changes.split(chr(10)))} files")
            else:
                logger.info("✓ Git working tree is clean")
        else:
            issue = f"Git status check failed: {result.stderr}"
            logger.error(issue)
            issues.append(issue)
            
    except subprocess.TimeoutExpired:
        issue = "Git status check timed out"
        logger.error(issue)
        issues.append(issue)
    except Exception as e:
        issue = f"Git status check error: {str(e)}"
        logger.error(issue)
        issues.append(issue)
    
    return issues


def check_backups():
    """Verify recent backups exist for protected files."""
    logger.info("=== Backup Verification ===")
    issues = []
    backup_dir = Path("/home/workspace/N5/backups")
    
    if not backup_dir.exists():
        issue = "CRITICAL: Backup directory does not exist"
        logger.error(issue)
        issues.append(issue)
        return issues
    
    # Check for backups within last 24 hours
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for filepath in CRITICAL_FILES:
        filename = Path(filepath).name
        # Look for backups with this filename
        recent_backups = []
        
        for backup_file in backup_dir.rglob(f"*{filename}*"):
            if backup_file.is_file():
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime > cutoff_time:
                    recent_backups.append((backup_file, mtime))
        
        if recent_backups:
            most_recent = max(recent_backups, key=lambda x: x[1])
            logger.info(f"✓ {filename}: backup at {most_recent[1].strftime('%Y-%m-%d %H:%M')}")
        else:
            issue = f"WARNING: No recent backup (<24h) for {filename}"
            logger.warning(issue)
            issues.append(issue)
    
    return issues


def check_meeting_folder_names():
    """Validate meeting folder naming conventions."""
    logger.info("=== Meeting Folder Name Validation ===")
    issues = []
    
    try:
        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/validate_meeting_folder_names.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/workspace"
        )
        
        if result.returncode == 0:
            # Parse output for validation results
            output = result.stderr + result.stdout
            if "Invalid folders: 0" in output:
                logger.info("✓ All meeting folders follow correct naming convention")
            else:
                # Extract number of invalid folders
                for line in output.split('\n'):
                    if "Invalid folders:" in line and not "Invalid folders: 0" in line:
                        issue = f"Meeting folder naming violations detected"
                        logger.warning(issue)
                        logger.warning(f"  Run: validate-meeting-folders --fix")
                        issues.append(issue)
                        break
        else:
            issue = f"Meeting folder validation failed: {result.stderr}"
            logger.error(issue)
            issues.append(issue)
            
    except subprocess.TimeoutExpired:
        issue = "Meeting folder validation timed out"
        logger.error(issue)
        issues.append(issue)
    except Exception as e:
        issue = f"Meeting folder validation error: {str(e)}"
        logger.error(issue)
        issues.append(issue)
    
    return issues


def generate_report(file_issues, git_issues, backup_issues, meeting_issues):
    """Generate summary report."""
    logger.info("=== Daily Guardian Report ===")
    
    total_issues = len(file_issues) + len(git_issues) + len(backup_issues) + len(meeting_issues)
    
    if total_issues == 0:
        logger.info("✅ ALL CHECKS PASSED - System is healthy")
        return True
    else:
        logger.warning(f"⚠️  {total_issues} issue(s) detected")
        
        if file_issues:
            logger.warning(f"File Integrity Issues: {len(file_issues)}")
            for issue in file_issues:
                logger.warning(f"  - {issue}")
        
        if git_issues:
            logger.warning(f"Git Issues: {len(git_issues)}")
            for issue in git_issues:
                logger.warning(f"  - {issue}")
        
        if backup_issues:
            logger.warning(f"Backup Issues: {len(backup_issues)}")
            for issue in backup_issues:
                logger.warning(f"  - {issue}")
        
        if meeting_issues:
            logger.warning(f"Meeting Folder Issues: {len(meeting_issues)}")
            for issue in meeting_issues:
                logger.warning(f"  - {issue}")
        
        return False


def main():
    """Run daily guardian checks."""
    logger.info("=== Daily File Guardian Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Coverage: Previous 24 hours")
    
    file_issues = check_file_integrity()
    git_issues = check_git_status()
    backup_issues = check_backups()
    meeting_issues = check_meeting_folder_names()
    
    success = generate_report(file_issues, git_issues, backup_issues, meeting_issues)
    
    logger.info(f"=== Daily File Guardian Completed ===")
    logger.info(f"Log saved to: {log_file}")
    
    return 0 if success else 1


def backup_productivity_db():
    """Backup productivity tracker database."""
    backup_script = "/home/workspace/N5/scripts/backup_productivity_db.sh"
    try:
        result = subprocess.run([backup_script], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logger.info("✅ Productivity database backed up successfully")
        else:
            logger.error(f"❌ Productivity backup failed: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Productivity backup error: {e}")

if __name__ == "__main__":
    exit(main())
