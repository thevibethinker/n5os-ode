#!/usr/bin/env python3
"""
Migration Dry-Run Script for Meeting System v3
Build: meeting-system-v3, Drop: D5.2

Performs a comprehensive dry-run of the legacy migration plan.
CRITICAL: This script only previews changes, never modifies files.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess

# Migration targets
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
INBOX_DIR = MEETINGS_DIR / "Inbox"
CONVERTER_SCRIPT = Path("/home/workspace/Skills/meeting-ingestion/scripts/manifest_converter.py")
ARCHIVE_SCRIPT = Path("/home/workspace/Skills/meeting-ingestion/scripts/archive.py")


def scan_legacy_manifests():
    """Find all manifests that need v3 upgrade."""
    legacy_manifests = []
    
    print("🔍 Scanning for legacy manifests...")
    
    for manifest_path in MEETINGS_DIR.glob("**/manifest.json"):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check if it's already v3
            if manifest.get("$schema") == "manifest-v3":
                continue
                
            # Check if it looks like a legacy manifest
            if (manifest.get("manifest_version") or 
                "blocks_generated" in manifest or 
                "meeting_date" in manifest or 
                "date" in manifest):
                
                legacy_manifests.append({
                    "path": str(manifest_path),
                    "folder": str(manifest_path.parent),
                    "version": manifest.get("manifest_version", "unknown"),
                    "status": manifest.get("status", "unknown")
                })
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Warning: Could not read {manifest_path}: {e}")
    
    return legacy_manifests


def scan_jsonl_transcripts():
    """Find JSONL transcripts that need conversion to markdown."""
    jsonl_transcripts = []
    
    print("🔍 Scanning for JSONL transcripts...")
    
    for transcript_path in MEETINGS_DIR.glob("**/transcript.jsonl"):
        folder_path = transcript_path.parent
        md_path = folder_path / "transcript.md"
        
        # Check if MD version already exists
        md_exists = md_path.exists()
        
        # Get file sizes for comparison
        jsonl_size = transcript_path.stat().st_size
        md_size = md_path.stat().st_size if md_exists else 0
        
        jsonl_transcripts.append({
            "path": str(transcript_path),
            "folder": str(folder_path), 
            "jsonl_size_bytes": jsonl_size,
            "md_exists": md_exists,
            "md_size_bytes": md_size,
            "action": "convert" if not md_exists else "skip_md_exists"
        })
    
    return jsonl_transcripts


def scan_root_level_folders():
    """Find root-level dated folders that need archiving."""
    root_folders = []
    
    print("🔍 Scanning for root-level folders to archive...")
    
    for folder_path in MEETINGS_DIR.iterdir():
        if not folder_path.is_dir():
            continue
            
        # Skip special folders
        if folder_path.name in ["Inbox", "Week-of-2025-01-01"]:  # Add known week folders
            continue
        if folder_path.name.startswith("Week-of-"):
            continue
            
        # Check if it's a dated folder
        folder_name = folder_path.name
        if len(folder_name) >= 10 and folder_name[4] == '-' and folder_name[7] == '-':
            date_part = folder_name[:10]
            try:
                # Validate date format
                datetime.strptime(date_part, "%Y-%m-%d")
                
                # Determine target week folder
                from datetime import timedelta
                date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                monday = date_obj - timedelta(days=date_obj.weekday())
                target_week = f"Week-of-{monday.strftime('%Y-%m-%d')}"
                
                # Check for potential collisions
                target_path = MEETINGS_DIR / target_week
                collision_risk = False
                
                if target_path.exists():
                    # Check if there's already a folder with similar name
                    potential_collision_name = folder_name.replace("_", "-")
                    for suffix in ["_[P]", "_[M]", "_[B]", "_[C]", "_[R]"]:
                        potential_collision_name = potential_collision_name.replace(suffix, "")
                    
                    for existing in target_path.iterdir():
                        if existing.is_dir() and existing.name.startswith(potential_collision_name[:20]):
                            collision_risk = True
                            break
                
                # Infer meeting type
                meeting_type = "internal" if "[P]" in folder_name or "_P" in folder_name else "external"
                
                root_folders.append({
                    "path": str(folder_path),
                    "name": folder_name,
                    "date": date_part,
                    "target_week": target_week,
                    "meeting_type": meeting_type,
                    "collision_risk": collision_risk,
                    "target_path": str(target_path / meeting_type / potential_collision_name)
                })
                
            except ValueError:
                # Not a valid date, skip
                continue
    
    return root_folders


def test_manifest_converter():
    """Test manifest converter on the known legacy manifest."""
    print("🧪 Testing manifest converter...")
    
    test_folder = INBOX_DIR / "2026-01-26_Collateral-Blitz_Logan"
    if not test_folder.exists():
        return {"error": "Test folder not found"}
    
    try:
        result = subprocess.run([
            "python3", str(CONVERTER_SCRIPT),
            "--dry-run", str(test_folder)
        ], capture_output=True, text=True, timeout=30)
        
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": "Converter test timed out"}
    except Exception as e:
        return {"error": f"Converter test failed: {e}"}


def test_archive_script():
    """Test archive script dry-run."""
    print("🧪 Testing archive script...")
    
    try:
        result = subprocess.run([
            "python3", str(ARCHIVE_SCRIPT),
            "--dry-run", "--json"
        ], capture_output=True, text=True, timeout=30)
        
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": "Archive test timed out"}
    except Exception as e:
        return {"error": f"Archive test failed: {e}"}


def generate_backup_plan():
    """Generate backup plan for Personal/Meetings/."""
    print("💾 Generating backup plan...")
    
    # Calculate total size
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for item in MEETINGS_DIR.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    
    # Size in MB
    size_mb = total_size / (1024 * 1024)
    
    return {
        "source_path": str(MEETINGS_DIR),
        "backup_command": f"cp -r '{MEETINGS_DIR}' '{MEETINGS_DIR.parent}/Meetings.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}'",
        "total_size_mb": round(size_mb, 1),
        "file_count": file_count,
        "directory_count": dir_count,
        "estimated_time_minutes": max(1, int(size_mb / 100))  # Rough estimate
    }


def generate_edge_cases():
    """Identify potential edge cases and warnings."""
    edge_cases = []
    
    # Check for unusual file patterns
    unusual_patterns = []
    
    for manifest_path in MEETINGS_DIR.glob("**/manifest.json"):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            # Check for edge cases
            if not manifest.get("participants") and manifest.get("$schema") != "manifest-v3":
                unusual_patterns.append(f"No participants: {manifest_path.parent.name}")
                
            if manifest.get("status") == "unknown":
                unusual_patterns.append(f"Unknown status: {manifest_path.parent.name}")
                
            if "blocks_generated" in manifest and isinstance(manifest["blocks_generated"], list):
                unusual_patterns.append(f"List-format blocks_generated: {manifest_path.parent.name}")
                
        except Exception:
            continue
    
    # Check for potential naming collisions
    collision_risks = defaultdict(list)
    for folder_path in MEETINGS_DIR.iterdir():
        if folder_path.is_dir() and not folder_path.name.startswith("Week-of-"):
            base_name = folder_path.name.split("_")[0] if "_" in folder_path.name else folder_path.name
            collision_risks[base_name].append(folder_path.name)
    
    # Filter to actual collisions
    actual_collisions = {k: v for k, v in collision_risks.items() if len(v) > 1}
    
    return {
        "unusual_manifest_patterns": unusual_patterns,
        "potential_naming_collisions": actual_collisions,
        "quarantine_folders": len(list(MEETINGS_DIR.glob("**/*quarantine*"))),
        "orphaned_blocks_folders": len(list(MEETINGS_DIR.glob("**/*orphaned*")))
    }


def main():
    """Run complete migration dry-run analysis."""
    print("=" * 60)
    print("🚀 Meeting System v3 - Migration Dry-Run Analysis")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Meetings Directory: {MEETINGS_DIR}")
    print()
    
    # Perform all scans
    backup_plan = generate_backup_plan()
    legacy_manifests = scan_legacy_manifests()
    jsonl_transcripts = scan_jsonl_transcripts()
    root_folders = scan_root_level_folders()
    converter_test = test_manifest_converter()
    archive_test = test_archive_script()
    edge_cases = generate_edge_cases()
    
    # Generate summary counts
    manifest_upgrades = len([m for m in legacy_manifests])
    transcript_conversions = len([t for t in jsonl_transcripts if t["action"] == "convert"])
    archive_moves = len(root_folders)
    collision_count = len([f for f in root_folders if f["collision_risk"]])
    
    # Build comprehensive report
    report = {
        "dry_run_summary": {
            "timestamp": datetime.now().isoformat(),
            "backup_plan": backup_plan,
            "migration_counts": {
                "manifest_upgrades": manifest_upgrades,
                "transcript_conversions": transcript_conversions,
                "archive_moves": archive_moves,
                "estimated_collisions": collision_count
            }
        },
        
        "backup_plan": backup_plan,
        
        "manifest_upgrades": {
            "count": manifest_upgrades,
            "details": legacy_manifests
        },
        
        "transcript_conversions": {
            "count": transcript_conversions,
            "details": jsonl_transcripts
        },
        
        "archive_moves": {
            "count": archive_moves,
            "collision_count": collision_count,
            "details": root_folders
        },
        
        "tool_tests": {
            "manifest_converter": converter_test,
            "archive_script": archive_test
        },
        
        "edge_cases": edge_cases,
        
        "execution_plan": {
            "step_1": "Create backup using command from backup_plan",
            "step_2": f"Run manifest converter on {manifest_upgrades} folders",
            "step_3": f"Convert {transcript_conversions} JSONL transcripts to markdown",
            "step_4": f"Archive {archive_moves} root-level folders to Week-of-* structure",
            "step_5": f"Resolve {collision_count} naming collisions manually"
        }
    }
    
    # Print human-readable summary
    print("📊 DRY-RUN SUMMARY")
    print("-" * 40)
    print(f"Backup Required: {backup_plan['total_size_mb']} MB ({backup_plan['file_count']} files)")
    print(f"Manifest Upgrades: {manifest_upgrades}")
    print(f"Transcript Conversions: {transcript_conversions}")
    print(f"Archive Moves: {archive_moves}")
    print(f"Potential Collisions: {collision_count}")
    print()
    
    if edge_cases["unusual_manifest_patterns"]:
        print("⚠️  EDGE CASES FOUND")
        for pattern in edge_cases["unusual_manifest_patterns"][:5]:  # Show first 5
            print(f"  • {pattern}")
        if len(edge_cases["unusual_manifest_patterns"]) > 5:
            print(f"  • ... and {len(edge_cases['unusual_manifest_patterns']) - 5} more")
        print()
    
    # Tool validation
    print("🔧 TOOL VALIDATION")
    print(f"Manifest Converter: {'✅ PASS' if converter_test.get('exit_code') == 0 else '❌ FAIL'}")
    print(f"Archive Script: {'✅ PASS' if archive_test.get('exit_code') == 0 else '❌ FAIL'}")
    print()
    
    print("✅ DRY-RUN COMPLETE - NO FILES MODIFIED")
    print("📄 Full report saved to migration_dry_run_report.json")
    
    return report


if __name__ == "__main__":
    report = main()
    
    # Save detailed report
    report_file = Path("/home/workspace/N5/builds/meeting-system-v3/artifacts/migration_dry_run_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report: {report_file}")