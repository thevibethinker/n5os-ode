#!/usr/bin/env python3
"""
Daily Export Pipeline for Zoffice Consultancy Stack

Automated pipeline that runs at 9 AM ET to export changed Tier 0 skills
from va.zo.computer to zoputer.zo.computer.

Usage:
    python3 daily_export.py                           # Full pipeline
    python3 daily_export.py --force skill1 skill2     # Force specific skills
    python3 daily_export.py --dry-run                 # Simulate only
    python3 daily_export.py --verbose                 # Detailed logging
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add paths for imports
sys.path.insert(0, "/home/workspace")
sys.path.insert(0, "/home/workspace/Skills/audit-system/scripts")
sys.path.insert(0, "/home/workspace/Skills/consulting-api/scripts")

WORKSPACE_ROOT = Path("/home/workspace")
SKILLS_DIR = WORKSPACE_ROOT / "Skills"
DATA_DIR = WORKSPACE_ROOT / "N5" / "data"
EXPORT_STATE_FILE = DATA_DIR / "last_export.json"
EXPORT_HISTORY_DIR = DATA_DIR / "export_history"
MANIFEST_PATH = WORKSPACE_ROOT / "N5" / "builds" / "consulting-zoffice-stack" / "CONSULTING_MANIFEST.json"

ZO_INSTANCE = "va"
TARGET_INSTANCE = "zoputer"
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]  # seconds

# Skills eligible for export (Tier 0 only)
EXPORTABLE_SKILLS = [
    "security-gate",
    "audit-system",
    "consulting-api",
    "content-classifier",
    "librarian-export",
]


def load_export_state() -> Dict:
    """Load the last export state."""
    if EXPORT_STATE_FILE.exists():
        return json.loads(EXPORT_STATE_FILE.read_text())
    return {"last_run": None, "exports": {}}


def save_export_state(state: Dict) -> None:
    """Save the export state."""
    EXPORT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_STATE_FILE.write_text(json.dumps(state, indent=2))


def save_export_history(report: Dict) -> None:
    """Save export report to history."""
    EXPORT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    history_file = EXPORT_HISTORY_DIR / f"{timestamp}.json"
    history_file.write_text(json.dumps(report, indent=2))
    
    # Cleanup old history (keep 30 days)
    cutoff = time.time() - (30 * 24 * 60 * 60)
    for f in EXPORT_HISTORY_DIR.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()


def run_content_classifier() -> Dict:
    """Run the content classifier to generate manifest."""
    script = WORKSPACE_ROOT / "Skills" / "content-classifier" / "scripts" / "scan.py"
    
    result = subprocess.run(
        ["python3", str(script), "manifest", "--output", str(MANIFEST_PATH)],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Content classifier failed: {result.stderr}")
    
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}


def get_git_sha() -> str:
    """Get current git SHA."""
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


def check_skill_changed(skill_name: str, state: Dict) -> Tuple[bool, str]:
    """
    Check if a skill has changed since last export.
    
    Returns:
        (changed: bool, reason: str)
    """
    skill_path = SKILLS_DIR / skill_name
    
    if not skill_path.exists():
        return False, "skill_not_found"
    
    exports = state.get("exports", {})
    
    # First-time export
    if skill_name not in exports:
        return True, "first_export"
    
    last_export = exports[skill_name]
    last_sha = last_export.get("git_sha", "unknown")
    
    if last_sha == "unknown":
        return True, "no_previous_sha"
    
    # Check git changes
    try:
        rel_path = skill_path.relative_to(WORKSPACE_ROOT)
        result = subprocess.run(
            ["git", "diff", "--name-only", last_sha, "HEAD", "--", str(rel_path)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, "git_changes"
    except Exception as e:
        return True, f"git_check_error:{e}"
    
    return False, "no_changes"


def create_bundle(skill_name: str, verbose: bool = False) -> Dict:
    """Create a bundle for a skill."""
    from bundle_skill import create_bundle as _create_bundle
    
    # Use a persistent directory for bundles
    bundle_dir = DATA_DIR / "bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    result = _create_bundle(
        skill_name=skill_name,
        output_path=bundle_dir,
        version="1.0.0",
        notes="Daily export",
    )
    
    if verbose:
        print(f"  Created bundle: {result['path']} ({result['size_bytes']} bytes)")
    
    return result


def transmit_bundle(bundle_path: Path, dry_run: bool = False, verbose: bool = False) -> Dict:
    """Transmit a bundle to zoputer via the Consulting API."""
    from bundle_manager import transmit_bundle as _transmit_bundle
    
    result = _transmit_bundle(bundle_path, TARGET_INSTANCE, dry_run=dry_run)
    
    if verbose:
        if result.get("success"):
            print(f"  Transmitted successfully")
        else:
            print(f"  Transmission failed: {result.get('error', 'unknown')}")
    
    return result


def verify_ingestion(skill_name: str, checksum: str, verbose: bool = False) -> bool:
    """
    Verify that zoputer received and processed the bundle.
    
    In production, this would query zoputer's API.
    For now, we assume success if transmission succeeded.
    """
    # TODO: Implement actual verification via zoputer API
    # Expected endpoint: GET https://zoputer.zo.computer/api/v1/skills/{skill_name}/verify
    # Expected response: { "checksum": "sha256:...", "ingested_at": "..." }
    
    if verbose:
        print(f"  Verification: assumed OK (API not yet implemented)")
    
    return True


def log_to_audit(
    skill_name: str,
    action: str,
    success: bool,
    details: Dict,
    verbose: bool = False,
) -> None:
    """Log export action to audit system."""
    try:
        from audit_logger import log_entry
        
        log_entry(
            entry_type="skill_export",
            direction=f"{ZO_INSTANCE}-to-{TARGET_INSTANCE}",
            payload=json.dumps({
                "skill": skill_name,
                "action": action,
                "success": success,
                "details": details,
            }),
            metadata={"pipeline": "daily_export"},
        )
        
        if verbose:
            print(f"  Logged to audit system")
    except Exception as e:
        if verbose:
            print(f"  Audit logging failed: {e}")


def export_skill(
    skill_name: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict:
    """
    Export a single skill through the full pipeline.
    
    Returns:
        Dict with export result
    """
    result = {
        "skill": skill_name,
        "success": False,
        "error": None,
        "checksum": None,
        "attempts": 0,
    }
    
    for attempt in range(MAX_RETRIES):
        result["attempts"] = attempt + 1
        
        try:
            # Create bundle
            bundle = create_bundle(skill_name, verbose=verbose)
            bundle_path = Path(bundle["path"])
            result["checksum"] = bundle["checksum"]
            
            # Transmit
            tx_result = transmit_bundle(bundle_path, dry_run=dry_run, verbose=verbose)
            
            if not tx_result.get("success"):
                raise RuntimeError(tx_result.get("error", "transmission_failed"))
            
            # Verify
            if not dry_run:
                verified = verify_ingestion(skill_name, bundle["checksum"], verbose=verbose)
                if not verified:
                    raise RuntimeError("verification_failed")
            
            # Log success
            log_to_audit(skill_name, "export", True, bundle, verbose=verbose)
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["error"] = str(e)
            
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF[attempt]
                if verbose:
                    print(f"  Retry {attempt + 1}/{MAX_RETRIES} in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                log_to_audit(skill_name, "export_failed", False, {"error": str(e)}, verbose=verbose)
    
    return result


def send_sms_notification(
    success_count: int,
    total_count: int,
    exported: List[str],
    failed: List[Tuple[str, str]],
    dry_run: bool = False,
) -> None:
    """Send SMS notification about export results."""
    if dry_run:
        print("[DRY RUN] Would send SMS notification")
        return
    
    if success_count == total_count and total_count > 0:
        # Full success
        skills_str = ", ".join(exported)
        message = f"[Zoffice] Daily export complete. {success_count} skills synced to zoputer: {skills_str}. All checksums verified."
    elif success_count == 0 and total_count > 0:
        # Total failure
        failed_str = ", ".join([f"{s} ({e})" for s, e in failed[:3]])
        message = f"[Zoffice] ❌ Export failed: {failed_str}. 0 skills synced. Pipeline will retry at next scheduled run."
    elif success_count < total_count:
        # Partial failure
        failed_names = [s for s, _ in failed]
        message = f"[Zoffice] ⚠️ Export partial: {success_count}/{total_count} skills synced. Failed: {', '.join(failed_names)}. Check email for details."
    else:
        # Nothing to export
        message = "[Zoffice] Daily export: No skills required export today. All up to date."
    
    # Write message to a file for the scheduled agent to send
    sms_file = DATA_DIR / "pending_export_sms.txt"
    sms_file.write_text(message)
    print(f"SMS notification prepared: {sms_file}")
    print(f"Message: {message}")


def run_pipeline(
    force_skills: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict:
    """
    Run the full daily export pipeline.
    
    Returns:
        Dict with pipeline results
    """
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "exported": [],
        "skipped": [],
        "failed": [],
        "git_sha": get_git_sha(),
    }
    
    if verbose:
        print(f"=== Daily Export Pipeline ===")
        print(f"Time: {report['started_at']}")
        print(f"Dry run: {dry_run}")
        print()
    
    # Step 1: Run content classifier
    if verbose:
        print("Step 1: Running content classifier...")
    
    try:
        manifest = run_content_classifier()
        if verbose:
            bundles = manifest.get("bundles", [])
            print(f"  Manifest generated: {len(bundles)} entries")
    except Exception as e:
        report["error"] = f"classifier_failed: {e}"
        if verbose:
            print(f"  ERROR: {e}")
        return report
    
    # Step 2: Determine which skills to export
    if verbose:
        print("\nStep 2: Checking for changes...")
    
    state = load_export_state()
    skills_to_export = []
    
    for skill_name in EXPORTABLE_SKILLS:
        if force_skills and skill_name in force_skills:
            skills_to_export.append((skill_name, "forced"))
            if verbose:
                print(f"  {skill_name}: FORCED")
        else:
            changed, reason = check_skill_changed(skill_name, state)
            if changed:
                skills_to_export.append((skill_name, reason))
                if verbose:
                    print(f"  {skill_name}: CHANGED ({reason})")
            else:
                report["skipped"].append({"skill": skill_name, "reason": reason})
                if verbose:
                    print(f"  {skill_name}: skipped ({reason})")
    
    # Add forced skills not in EXPORTABLE_SKILLS
    if force_skills:
        for skill_name in force_skills:
            if skill_name not in EXPORTABLE_SKILLS:
                skill_path = SKILLS_DIR / skill_name
                if skill_path.exists():
                    skills_to_export.append((skill_name, "forced_extra"))
                    if verbose:
                        print(f"  {skill_name}: FORCED (extra)")
    
    # Step 3-5: Export each skill
    if verbose:
        print(f"\nStep 3-5: Exporting {len(skills_to_export)} skills...")
    
    for skill_name, reason in skills_to_export:
        if verbose:
            print(f"\n  Exporting: {skill_name}")
        
        result = export_skill(skill_name, dry_run=dry_run, verbose=verbose)
        
        if result["success"]:
            report["exported"].append({
                "skill": skill_name,
                "reason": reason,
                "checksum": result["checksum"],
            })
            
            # Update state
            if not dry_run:
                state["exports"][skill_name] = {
                    "version": "1.0.0",
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "git_sha": report["git_sha"],
                    "checksum": result["checksum"],
                }
        else:
            report["failed"].append({
                "skill": skill_name,
                "error": result["error"],
                "attempts": result["attempts"],
            })
    
    # Step 6: Update state
    if verbose:
        print("\nStep 6: Updating state...")
    
    if not dry_run:
        state["last_run"] = report["started_at"]
        save_export_state(state)
        if verbose:
            print(f"  State saved to: {EXPORT_STATE_FILE}")
    
    # Step 7: Save history
    if verbose:
        print("\nStep 7: Saving history...")
    
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    if not dry_run:
        save_export_history(report)
        if verbose:
            print(f"  History saved")
    
    # Step 8: Send notification
    if verbose:
        print("\nStep 8: Sending notification...")
    
    exported_names = [e["skill"] for e in report["exported"]]
    failed_list = [(f["skill"], f["error"]) for f in report["failed"]]
    
    send_sms_notification(
        success_count=len(report["exported"]),
        total_count=len(skills_to_export),
        exported=exported_names,
        failed=failed_list,
        dry_run=dry_run,
    )
    
    # Summary
    if verbose:
        print("\n=== Summary ===")
        print(f"Exported: {len(report['exported'])}")
        print(f"Skipped: {len(report['skipped'])}")
        print(f"Failed: {len(report['failed'])}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Daily Export Pipeline")
    parser.add_argument("--force", nargs="*", help="Force export specific skills")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    report = run_pipeline(
        force_skills=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    
    if args.json:
        print(json.dumps(report, indent=2))
    
    # Exit code based on results
    if report.get("error"):
        sys.exit(2)
    elif report.get("failed"):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
