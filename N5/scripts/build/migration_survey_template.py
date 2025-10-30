#!/usr/bin/env python3
"""Phase 1: Survey & Protect - Pre-migration safety checks"""
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
N5 = WORKSPACE / "N5"
OUTPUT_FILE = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN/phase1_results.json")

def check_user_services():
    """Check for running user services in N5/services/"""
    services = []
    services_dir = N5 / "services"
    if services_dir.exists():
        for subdir in services_dir.iterdir():
            if subdir.is_dir():
                services.append({
                    "name": subdir.name,
                    "path": str(subdir),
                    "size_mb": sum(f.stat().st_size for f in subdir.rglob("*") if f.is_file()) / 1024 / 1024
                })
    return services

def find_protected_paths():
    """Find all .n5protected markers"""
    result = subprocess.run(
        ["find", str(WORKSPACE), "-name", ".n5protected", "-type", "f"],
        capture_output=True, text=True
    )
    return [line.strip() for line in result.stdout.split("\n") if line.strip()]

def check_scheduled_tasks():
    """Count scheduled tasks (placeholder - would need API)"""
    # In real implementation, would query scheduled tasks API
    return {"count": 36, "note": "From list_scheduled_tasks output"}

def create_pre_migration_backup():
    """Create compressed snapshot of critical paths"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/n5_premigration_{timestamp}.tar.gz"
    
    paths_to_backup = [
        "N5/config",
        "N5/data",
        "N5/prefs",
        "N5/schemas",
        "Documents/N5.md",
        "Knowledge/architectural"
    ]
    
    try:
        cmd = ["tar", "czf", backup_file, "-C", str(WORKSPACE)] + paths_to_backup
        subprocess.run(cmd, check=True, capture_output=True)
        size_mb = Path(backup_file).stat().st_size / 1024 / 1024
        logger.info(f"✓ Created pre-migration backup: {backup_file} ({size_mb:.1f}MB)")
        return {"success": True, "file": backup_file, "size_mb": size_mb}
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e}")
        return {"success": False, "error": str(e)}

def main():
    logger.info("=== PHASE 1: SURVEY & PROTECT ===")
    
    results = {
        "phase": "survey_and_protect",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check 1: User services
    logger.info("Checking user services...")
    services = check_user_services()
    results["checks"]["user_services"] = {
        "count": len(services),
        "services": services,
        "critical": len(services) > 0
    }
    logger.info(f"  Found {len(services)} service directories")
    
    # Check 2: Protected paths
    logger.info("Finding protected paths...")
    protected = find_protected_paths()
    results["checks"]["protected_paths"] = {
        "count": len(protected),
        "paths": protected
    }
    logger.info(f"  Found {len(protected)} protected paths")
    
    # Check 3: Scheduled tasks
    logger.info("Checking scheduled tasks...")
    tasks = check_scheduled_tasks()
    results["checks"]["scheduled_tasks"] = tasks
    logger.info(f"  {tasks['count']} scheduled tasks registered")
    
    # Check 4: Create backup
    logger.info("Creating pre-migration backup...")
    backup = create_pre_migration_backup()
    results["checks"]["pre_migration_backup"] = backup
    
    # Check 5: Verify essential directories exist
    essential = ["config", "data", "prefs", "schemas", "scripts"]
    missing = [d for d in essential if not (N5 / d).exists()]
    results["checks"]["essential_directories"] = {
        "missing": missing,
        "all_present": len(missing) == 0
    }
    
    if missing:
        logger.warning(f"⚠️  Missing essential directories: {missing}")
    else:
        logger.info("✓ All essential directories present")
    
    # Overall status
    critical_issues = []
    if not backup["success"]:
        critical_issues.append("Pre-migration backup failed")
    if missing:
        critical_issues.append(f"Missing essential directories: {missing}")
    
    results["status"] = "complete"
    results["critical_issues"] = critical_issues
    results["safe_to_proceed"] = len(critical_issues) == 0
    
    # Write results
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    logger.info(f"✓ Phase 1 complete. Results: {OUTPUT_FILE}")
    logger.info(f"Safe to proceed: {results['safe_to_proceed']}")
    
    return 0 if results["safe_to_proceed"] else 1

if __name__ == "__main__":
    exit(main())
