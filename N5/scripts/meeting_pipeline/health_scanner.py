#!/usr/bin/env python3
"""
Meeting System Health Scanner
Detects and reports issues with meeting processing pipeline
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
PIPELINE_DB = WORKSPACE / "N5/data/meeting_pipeline.db"
HEALTH_REPORT = WORKSPACE / "N5/data/meeting_health_report.json"

def scan_meeting_directory(meeting_dir: Path) -> Dict[str, Any]:
    """Scan a single meeting directory for health issues."""
    issues = []
    
    # Get metadata
    metadata_path = meeting_dir / "_metadata.json"
    if not metadata_path.exists():
        return {
            "meeting_id": meeting_dir.name,
            "status": "CRITICAL",
            "issues": [{"type": "MISSING_METADATA", "severity": "CRITICAL", "message": "Missing metadata file"}],
            "block_count": 0,
            "expected_blocks": 0
        }
    
    metadata = json.loads(metadata_path.read_text())
    
    # Count actual blocks
    actual_blocks = list(meeting_dir.glob("B*.md"))
    block_count = len(actual_blocks)
    
    # Expected blocks from metadata
    expected_blocks = metadata.get("smart_blocks_generated", [])
    expected_count = len(expected_blocks)
    
    # Check for issues
    
    # Issue 1: False completion (P15)
    if metadata.get("processing_status") == "completed" and block_count == 0:
        issues.append({
            "type": "FALSE_COMPLETION",
            "severity": "CRITICAL",
            "message": f"Metadata claims completed but 0 blocks exist (expected {expected_count})"
        })
    
    # Issue 2: Partial completion
    elif metadata.get("processing_status") == "completed" and 0 < block_count < expected_count:
        pct = 100*block_count//expected_count if expected_count > 0 else 0
        issues.append({
            "type": "PARTIAL_COMPLETION",
            "severity": "HIGH",
            "message": f"Only {block_count}/{expected_count} blocks exist ({pct}% complete)"
        })
    
    # Issue 3: Duplicate blocks
    block_basenames = {}
    for block in actual_blocks:
        basename = block.name.split("_")[0] if "_" in block.name else block.stem
        block_basenames[basename] = block_basenames.get(basename, 0) + 1
    
    duplicates = {k: v for k, v in block_basenames.items() if v > 1}
    if duplicates:
        issues.append({
            "type": "DUPLICATE_BLOCKS",
            "severity": "MEDIUM",
            "message": f"Duplicate blocks: {', '.join(f'{k}({v}x)' for k, v in duplicates.items())}"
        })
    
    # Issue 4: Template-only blocks (very small)
    template_blocks = [b.name for b in actual_blocks if b.stat().st_size < 100]
    if template_blocks:
        issues.append({
            "type": "TEMPLATE_ONLY",
            "severity": "HIGH",
            "message": f"{len(template_blocks)} blocks appear to be templates only"
        })
    
    # Issue 5: Empty blocks
    empty_blocks = [b.name for b in actual_blocks if b.stat().st_size == 0]
    if empty_blocks:
        issues.append({
            "type": "EMPTY_BLOCKS",
            "severity": "CRITICAL",
            "message": f"{len(empty_blocks)} blocks are completely empty"
        })
    
    # Determine status
    if any(i["severity"] == "CRITICAL" for i in issues):
        status = "CRITICAL"
    elif any(i["severity"] == "HIGH" for i in issues):
        status = "HIGH"
    elif any(i["severity"] == "MEDIUM" for i in issues):
        status = "MEDIUM"
    else:
        status = "HEALTHY"
    
    return {
        "meeting_id": meeting_dir.name,
        "status": status,
        "issues": issues,
        "block_count": block_count,
        "expected_blocks": expected_count,
        "processing_status": metadata.get("processing_status", "unknown"),
        "processed_at": metadata.get("processed_at", "unknown")
    }

def scan_all_meetings(limit: int = 50):
    """Scan recent meetings."""
    results = []
    meetings = sorted(
        [d for d in MEETINGS_DIR.glob("2025-*") if d.is_dir() and d.name != "Inbox"],
        key=lambda x: x.name,
        reverse=True
    )[:limit]
    
    for meeting_dir in meetings:
        result = scan_meeting_directory(meeting_dir)
        if result["status"] != "HEALTHY":
            results.append(result)
    
    return results

def check_empty_folders(meetings_dir: Path) -> List[str]:
    """
    Scan for empty meeting folders (potential ingestion failures).
    Returns list of empty folder names.
    """
    empty = []
    
    if not meetings_dir.exists():
        return empty
    
    for folder in meetings_dir.iterdir():
        # Skip special directories
        if not folder.is_dir() or folder.name.startswith('.') or folder.name in ['Inbox', '_ARCHIVE_2024']:
            continue
        
        # Check if folder is empty
        contents = list(folder.iterdir())
        if len(contents) == 0:
            empty.append(folder.name)
    
    return empty

def generate_health_report():
    """Generate health report."""
    issues = scan_all_meetings(limit=50)
    
    critical = [i for i in issues if i["status"] == "CRITICAL"]
    high = [i for i in issues if i["status"] == "HIGH"]
    medium = [i for i in issues if i["status"] == "MEDIUM"]
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_scanned": 50,
            "critical_issues": len(critical),
            "high_issues": len(high),
            "medium_issues": len(medium),
            "healthy": 50 - len(issues)
        },
        "critical": critical,
        "high": high,
        "medium": medium
    }

def main():
    print("Meeting System Health Scanner")
    print("=" * 50)
    
    # Check for empty folders
    print("\n🗂️  Checking for empty folders...")
    empty_folders = check_empty_folders(MEETINGS_DIR)
    if empty_folders:
        print(f"   ⚠️  Found {len(empty_folders)} empty folders:")
        for folder in empty_folders:
            print(f"      - {folder}")
    else:
        print("   ✓ No empty folders found")
    
    print("\n📊 Scanning meeting health...")
    report = generate_health_report()
    
    # Add empty folders to report
    if empty_folders:
        report['empty_folders'] = empty_folders
        report['summary']['empty_folders'] = len(empty_folders)
    
    HEALTH_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_REPORT.write_text(json.dumps(report, indent=2))
    
    print(f"\nScanned: {report['summary']['total_scanned']} meetings")
    print(f"CRITICAL: {report['summary']['critical_issues']}")
    print(f"HIGH:     {report['summary']['high_issues']}")
    print(f"MEDIUM:   {report['summary']['medium_issues']}")
    print(f"HEALTHY:  {report['summary']['healthy']}")
    
    if empty_folders:
        print(f"⚠️  EMPTY FOLDERS: {len(empty_folders)}")
    
    if report['summary']['critical_issues'] > 0:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in report['critical'][:5]:
            print(f"  - {issue['meeting_id']}")
            for i in issue['issues']:
                print(f"    {i['message']}")
    
    print(f"\n✓ Report: {HEALTH_REPORT}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())


