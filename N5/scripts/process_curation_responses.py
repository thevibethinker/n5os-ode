#!/usr/bin/env python3
"""
Knowledge System V4 - Process Curation Responses
Parses V's A/R/M/S responses from curation report and executes actions.

Input: Knowledge/intelligence/WEEKLY_CURATION_REPORT_{date}.md (with V's responses)
Output: Executes knowledge_integrator.py, moves files, updates metadata, logs decisions
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

WORKSPACE = Path("/home/workspace")
INTELLIGENCE_DIR = WORKSPACE / "Knowledge" / "intelligence"
EXTRACTS_DIR = INTELLIGENCE_DIR / "extracts"
PROCESSED_DIR = INTELLIGENCE_DIR / "processed"
REJECTED_DIR = INTELLIGENCE_DIR / "rejected"
CURATION_LOG = INTELLIGENCE_DIR / "curation_log.jsonl"

INTEGRATOR_SCRIPT = WORKSPACE / "N5" / "scripts" / "knowledge_integrator.py"


def find_latest_report() -> Optional[Path]:
    """Find most recent curation report."""
    reports = list(INTELLIGENCE_DIR.glob("WEEKLY_CURATION_REPORT_*.md"))
    if not reports:
        return None
    return max(reports, key=lambda p: p.stat().st_mtime)


def parse_responses(report_path: Path) -> Dict[int, Tuple[str, str]]:
    """
    Parse V's responses from report.
    
    Returns dict of {item_number: (decision, target)}.
    Decision is one of: A, R, M, S
    Target is file path for M decisions, empty otherwise.
    """
    content = report_path.read_text()
    responses = {}
    
    # Pattern 1: Inline responses (Response: A)
    inline_pattern = r"### Item (\d+):.*?Response:\s*([ARMS])(?:\s+(.+?))?(?:\n|$)"
    for match in re.finditer(inline_pattern, content, re.DOTALL):
        item_num = int(match.group(1))
        decision = match.group(2).strip()
        target = match.group(3).strip() if match.group(3) else ""
        responses[item_num] = (decision, target)
    
    # Pattern 2: Summary format (1: A)
    summary_pattern = r"^(\d+):\s*([ARMS])(?:\s+(.+?))?$"
    for match in re.finditer(summary_pattern, content, re.MULTILINE):
        item_num = int(match.group(1))
        decision = match.group(2).strip()
        target = match.group(3).strip() if match.group(3) else ""
        
        # Don't overwrite if already found inline
        if item_num not in responses:
            responses[item_num] = (decision, target)
    
    return responses


def get_extract_files() -> Dict[int, Path]:
    """
    Map item numbers to extract YAML files.
    
    Uses same sorting logic as generate_curation_report.py.
    """
    extracts = []
    
    for yaml_file in EXTRACTS_DIR.glob("*.yaml"):
        try:
            with yaml_file.open() as f:
                data = yaml.safe_load(f)
            
            if data.get("status") == "pending_review":
                extracts.append((data, yaml_file))
        except Exception as e:
            logging.error(f"Failed to load {yaml_file}: {e}")
    
    # Sort same as report generation
    priority_map = {"high": 3, "medium": 2, "low": 1}
    
    def sort_key(item):
        data, _ = item
        tags = data.get("tags", {})
        priority = tags.get("priority", "medium")
        confidence = data.get("confidence", 0)
        captured_at = data.get("captured_at", "")
        
        return (
            -priority_map.get(priority, 2),
            -confidence,
            -ord(captured_at[0]) if captured_at else 0,
        )
    
    sorted_extracts = sorted(extracts, key=sort_key)
    
    # Map item numbers (1-indexed)
    return {i + 1: yaml_file for i, (_, yaml_file) in enumerate(sorted_extracts)}


def process_approval(yaml_file: Path, target_override: str = "") -> bool:
    """
    Process approved item by calling knowledge_integrator.py.
    
    Returns True on success, False on failure.
    """
    try:
        cmd = [sys.executable, str(INTEGRATOR_SCRIPT), str(yaml_file)]
        
        if target_override:
            cmd.extend(["--target", target_override])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logging.info(f"✓ Integrated: {yaml_file.name}")
            return True
        else:
            logging.error(f"Integration failed for {yaml_file.name}: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"Failed to integrate {yaml_file.name}: {e}")
        return False


def process_rejection(yaml_file: Path, reason: str = "") -> bool:
    """
    Move rejected item to rejected/ directory.
    
    Returns True on success, False on failure.
    """
    try:
        REJECTED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Update YAML metadata
        with yaml_file.open() as f:
            data = yaml.safe_load(f)
        
        data["status"] = "rejected"
        data["metadata"]["curator_reviewed"] = True
        data["metadata"]["reviewed_at"] = datetime.now().isoformat()
        if reason:
            data["metadata"]["rejection_reason"] = reason
        
        # Write to rejected directory
        rejected_path = REJECTED_DIR / yaml_file.name
        with rejected_path.open("w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Remove from extracts
        yaml_file.unlink()
        
        logging.info(f"✓ Rejected: {yaml_file.name}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to reject {yaml_file.name}: {e}")
        return False


def process_skip(yaml_file: Path) -> bool:
    """
    Skip item (leave in pending for next week).
    
    Returns True on success.
    """
    logging.info(f"⊙ Skipped: {yaml_file.name}")
    return True


def update_processed_metadata(yaml_file: Path, decision: str, target: str = "") -> bool:
    """
    Update YAML metadata after processing and move to processed/.
    
    Returns True on success, False on failure.
    """
    try:
        with yaml_file.open() as f:
            data = yaml.safe_load(f)
        
        data["status"] = "approved" if decision == "A" else "modified"
        data["metadata"]["curator_reviewed"] = True
        data["metadata"]["reviewed_at"] = datetime.now().isoformat()
        data["metadata"]["internalized"] = True
        
        if target:
            data["knowledge_routing"]["target"] = target
        
        # Create monthly processed directory
        year_month = datetime.now().strftime("%Y-%m")
        monthly_dir = PROCESSED_DIR / year_month
        monthly_dir.mkdir(parents=True, exist_ok=True)
        
        # Write to processed directory
        processed_path = monthly_dir / yaml_file.name
        with processed_path.open("w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Remove from extracts
        yaml_file.unlink()
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to update metadata for {yaml_file.name}: {e}")
        return False


def log_decision(item_num: int, yaml_file: Path, decision: str, target: str = "", success: bool = True) -> None:
    """Append decision to curation log."""
    try:
        with yaml_file.open() as f:
            data = yaml.safe_load(f)
        
        log_entry = {
            "item_id": data.get("source_id", "unknown"),
            "item_number": item_num,
            "filename": yaml_file.name,
            "decision": decision,
            "reviewed_by": "V",
            "reviewed_at": datetime.now().isoformat(),
            "success": success,
        }
        
        if decision == "A":
            log_entry["action"] = "approved"
            log_entry["target"] = data.get("knowledge_routing", {}).get("target", "")
        elif decision == "R":
            log_entry["action"] = "rejected"
        elif decision == "M":
            log_entry["action"] = "modified"
            log_entry["target"] = target
        elif decision == "S":
            log_entry["action"] = "skipped"
        
        CURATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CURATION_LOG.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        logging.error(f"Failed to log decision for {yaml_file.name}: {e}")


def main(report_path: Optional[Path] = None, dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logging.info(f"Starting curation response processing (dry_run={dry_run})")
        
        # Find report
        if not report_path:
            report_path = find_latest_report()
        
        if not report_path or not report_path.exists():
            logging.error("No curation report found")
            return 1
        
        logging.info(f"Processing report: {report_path}")
        
        # Parse responses
        responses = parse_responses(report_path)
        if not responses:
            logging.warning("No responses found in report")
            return 0
        
        logging.info(f"Found {len(responses)} responses")
        
        # Map item numbers to files
        extract_files = get_extract_files()
        
        if dry_run:
            logging.info("DRY RUN: Would process the following:")
            for item_num, (decision, target) in responses.items():
                yaml_file = extract_files.get(item_num)
                if yaml_file:
                    action_str = f"{decision}"
                    if target:
                        action_str += f" → {target}"
                    logging.info(f"  Item {item_num}: {action_str} ({yaml_file.name})")
            return 0
        
        # Process each response
        stats = {"approved": 0, "rejected": 0, "modified": 0, "skipped": 0, "errors": 0}
        
        for item_num, (decision, target) in responses.items():
            yaml_file = extract_files.get(item_num)
            
            if not yaml_file or not yaml_file.exists():
                logging.error(f"Item {item_num}: File not found")
                stats["errors"] += 1
                continue
            
            logging.info(f"Processing Item {item_num}: {decision} ({yaml_file.name})")
            
            success = False
            
            if decision == "A":
                # Approve
                success = process_approval(yaml_file)
                if success:
                    success = update_processed_metadata(yaml_file, "A")
                    stats["approved"] += 1
                
            elif decision == "R":
                # Reject
                success = process_rejection(yaml_file)
                if success:
                    stats["rejected"] += 1
                
            elif decision == "M":
                # Modify routing then approve
                if not target:
                    logging.error(f"Item {item_num}: M decision requires target")
                    stats["errors"] += 1
                    continue
                
                success = process_approval(yaml_file, target_override=target)
                if success:
                    success = update_processed_metadata(yaml_file, "M", target=target)
                    stats["modified"] += 1
                
            elif decision == "S":
                # Skip
                success = process_skip(yaml_file)
                if success:
                    stats["skipped"] += 1
            
            else:
                logging.error(f"Item {item_num}: Unknown decision '{decision}'")
                stats["errors"] += 1
                continue
            
            # Log decision
            log_decision(item_num, yaml_file, decision, target, success)
            
            if not success:
                stats["errors"] += 1
        
        # Report summary
        logging.info("="*60)
        logging.info(f"✓ Processing complete:")
        logging.info(f"  Approved: {stats['approved']}")
        logging.info(f"  Rejected: {stats['rejected']}")
        logging.info(f"  Modified: {stats['modified']}")
        logging.info(f"  Skipped: {stats['skipped']}")
        logging.info(f"  Errors: {stats['errors']}")
        logging.info("="*60)
        
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process curation report responses")
    parser.add_argument("report", nargs="?", type=Path, help="Path to curation report (default: latest)")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions but don't execute")
    
    args = parser.parse_args()
    sys.exit(main(report_path=args.report, dry_run=args.dry_run))
