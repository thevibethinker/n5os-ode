#!/usr/bin/env python3
"""
N5 Health Check - System health monitoring
Tracks: stale files, empty files, uncommitted changes, orphaned tasks
"""
import argparse
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

BASE = Path("/home/workspace")
TELEMETRY_DIR = BASE / "N5/telemetry"


def count_stale_files(directory: str, days: int = 7) -> Dict:
    """Count files older than N days in directory"""
    try:
        target_dir = BASE / directory
        if not target_dir.exists():
            return {"count": 0, "files": [], "error": "Directory not found"}
        
        cutoff = datetime.now() - timedelta(days=days)
        stale_files = []
        
        for filepath in target_dir.rglob("*"):
            if filepath.is_file():
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff:
                    age_days = (datetime.now() - mtime).days
                    stale_files.append({
                        "path": str(filepath.relative_to(BASE)),
                        "age_days": age_days,
                        "size_kb": filepath.stat().st_size // 1024
                    })
        
        return {
            "count": len(stale_files),
            "files": sorted(stale_files, key=lambda x: x["age_days"], reverse=True)[:10],
            "directory": directory
        }
    except Exception as e:
        logger.error(f"Error counting stale files in {directory}: {e}")
        return {"count": 0, "files": [], "error": str(e)}


def find_empty_files(directories: List[str]) -> Dict:
    """Find empty files (0 bytes) in specified directories"""
    try:
        empty_files = []
        
        for directory in directories:
            target_dir = BASE / directory
            if not target_dir.exists():
                continue
            
            for filepath in target_dir.rglob("*"):
                if filepath.is_file() and filepath.stat().st_size == 0:
                    empty_files.append(str(filepath.relative_to(BASE)))
        
        return {
            "count": len(empty_files),
            "files": empty_files[:20]  # Limit to first 20
        }
    except Exception as e:
        logger.error(f"Error finding empty files: {e}")
        return {"count": 0, "files": [], "error": str(e)}


def check_uncommitted_changes() -> Dict:
    """Check for uncommitted git changes"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {"count": 0, "files": [], "error": "Git status failed"}
        
        lines = [l for l in result.stdout.strip().split("\n") if l]
        
        return {
            "count": len(lines),
            "files": lines[:15],  # First 15 files
            "has_changes": len(lines) > 0
        }
    except Exception as e:
        logger.error(f"Error checking git status: {e}")
        return {"count": 0, "files": [], "error": str(e)}


def scan_orphaned_tasks() -> Dict:
    """Scan Lists for tasks with no recent activity"""
    try:
        lists_dir = BASE / "Lists"
        if not lists_dir.exists():
            return {"count": 0, "warning": "Lists directory not found"}
        
        # Simple heuristic: count .md files in Lists
        list_files = list(lists_dir.glob("*.md"))
        
        # Count tasks (lines starting with "- [ ]")
        total_tasks = 0
        for list_file in list_files:
            try:
                content = list_file.read_text()
                total_tasks += content.count("- [ ]")
            except Exception as e:
                logger.warning(f"Could not read {list_file}: {e}")
        
        return {
            "count": total_tasks,
            "list_files": len(list_files),
            "note": "Full orphan detection requires timeline analysis"
        }
    except Exception as e:
        logger.error(f"Error scanning tasks: {e}")
        return {"count": 0, "error": str(e)}


def run_health_check(dry_run: bool = False) -> Dict:
    """Run complete health check"""
    logger.info("Starting N5 health check...")
    
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "checks": {}
    }
    
    # Check 1: Stale files in Records/Temporary
    logger.info("Checking for stale files in Records/Temporary/...")
    health_data["checks"]["stale_records"] = count_stale_files(
        "Records/Temporary", days=7
    )
    
    # Check 2: Empty files
    logger.info("Checking for empty files...")
    health_data["checks"]["empty_files"] = find_empty_files([
        "N5/scripts",
        "N5/commands",
        "Knowledge",
        "Documents/System"
    ])
    
    # Check 3: Uncommitted changes
    logger.info("Checking for uncommitted git changes...")
    health_data["checks"]["uncommitted"] = check_uncommitted_changes()
    
    # Check 4: Orphaned tasks (basic scan)
    logger.info("Scanning for orphaned tasks...")
    health_data["checks"]["orphaned_tasks"] = scan_orphaned_tasks()
    
    # Summary
    health_data["summary"] = {
        "stale_records_count": health_data["checks"]["stale_records"]["count"],
        "empty_files_count": health_data["checks"]["empty_files"]["count"],
        "uncommitted_count": health_data["checks"]["uncommitted"]["count"],
        "pending_tasks_count": health_data["checks"]["orphaned_tasks"]["count"]
    }
    
    return health_data


def save_health_data(health_data: Dict, dry_run: bool = False) -> None:
    """Save health check data to disk"""
    if dry_run:
        logger.info("[DRY RUN] Would save health data")
        return
    
    try:
        # Ensure telemetry directory exists
        TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save to history (append-only JSONL)
        history_file = TELEMETRY_DIR / "health_history.jsonl"
        with history_file.open('a') as f:
            f.write(json.dumps(health_data) + "\n")
        
        # Save latest report (overwrite)
        report_file = TELEMETRY_DIR / "daily_report.md"
        report_content = generate_markdown_report(health_data)
        report_file.write_text(report_content)
        
        logger.info(f"✓ Saved health data to {history_file}")
        logger.info(f"✓ Saved report to {report_file}")
        
    except Exception as e:
        logger.error(f"Error saving health data: {e}")
        raise


def generate_markdown_report(health_data: Dict) -> str:
    """Generate human-readable markdown report"""
    timestamp = datetime.fromisoformat(health_data["timestamp"]).strftime("%Y-%m-%d %H:%M ET")
    summary = health_data["summary"]
    checks = health_data["checks"]
    
    report = f"""# N5 Health Check Report

**Generated:** {timestamp}

---

## Summary

| Metric | Count | Status |
|--------|-------|--------|
| Stale Records (>7 days) | {summary['stale_records_count']} | {"⚠️" if summary['stale_records_count'] > 10 else "✅"} |
| Empty Files | {summary['empty_files_count']} | {"⚠️" if summary['empty_files_count'] > 5 else "✅"} |
| Uncommitted Changes | {summary['uncommitted_count']} | {"⚠️" if summary['uncommitted_count'] > 20 else "✅"} |
| Pending Tasks | {summary['pending_tasks_count']} | ℹ️ |

---

## Details

### Stale Records (Records/Temporary/)

**Count:** {checks['stale_records']['count']} files older than 7 days

"""
    
    if checks['stale_records']['files']:
        report += "**Oldest files:**\n"
        for f in checks['stale_records']['files'][:5]:
            report += f"- `{f['path']}` ({f['age_days']} days old, {f['size_kb']} KB)\n"
    else:
        report += "*No stale files found* ✅\n"
    
    report += f"""

### Empty Files

**Count:** {checks['empty_files']['count']} empty files (0 bytes)

"""
    
    if checks['empty_files']['files']:
        report += "**Files:**\n"
        for f in checks['empty_files']['files'][:10]:
            report += f"- `{f}`\n"
    else:
        report += "*No empty files found* ✅\n"
    
    report += f"""

### Uncommitted Git Changes

**Count:** {checks['uncommitted']['count']} uncommitted changes

"""
    
    if checks['uncommitted']['files']:
        report += "**Changes:**\n```\n"
        for f in checks['uncommitted']['files'][:10]:
            report += f"{f}\n"
        report += "```\n"
    else:
        report += "*Working directory clean* ✅\n"
    
    report += f"""

### Pending Tasks

**Count:** {checks['orphaned_tasks']['count']} open tasks across {checks['orphaned_tasks'].get('list_files', 0)} list files

*Note: {checks['orphaned_tasks'].get('note', 'Basic count only')}*

---

## Recommendations

"""
    
    recommendations = []
    
    if summary['stale_records_count'] > 10:
        recommendations.append("⚠️ **Process stale records:** Move or archive files in Records/Temporary/")
    
    if summary['empty_files_count'] > 5:
        recommendations.append("⚠️ **Remove empty files:** Run cleanup to delete 0-byte files")
    
    if summary['uncommitted_count'] > 20:
        recommendations.append("⚠️ **Commit changes:** Review and commit pending changes")
    
    if not recommendations:
        recommendations.append("✅ **System healthy:** No immediate actions required")
    
    for rec in recommendations:
        report += f"{rec}\n\n"
    
    report += "---\n\n*Generated by N5 Telemetry System*\n"
    
    return report


def main(dry_run: bool = False, email: bool = False) -> int:
    """Main entry point"""
    try:
        # Run health check
        health_data = run_health_check(dry_run=dry_run)
        
        # Save data
        save_health_data(health_data, dry_run=dry_run)
        
        # Print summary
        summary = health_data["summary"]
        logger.info("=" * 50)
        logger.info("HEALTH CHECK SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Stale Records: {summary['stale_records_count']}")
        logger.info(f"Empty Files: {summary['empty_files_count']}")
        logger.info(f"Uncommitted: {summary['uncommitted_count']}")
        logger.info(f"Pending Tasks: {summary['pending_tasks_count']}")
        logger.info("=" * 50)
        
        # Email if requested
        if email and not dry_run:
            logger.info("Sending email digest...")
            # Will implement after we test basic functionality
            logger.info("Email functionality: TODO (next step)")
        
        logger.info(f"✓ Health check complete")
        logger.info(f"✓ Report: N5/telemetry/daily_report.md")
        
        return 0
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="N5 Health Check - Monitor system health and flow efficiency"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving data"
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send email digest after check"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run, email=args.email))
