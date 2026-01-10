#!/usr/bin/env python3
"""
Daily Resonance Maintenance: Regenerate resonance index and archive reports.

Usage:
    python3 daily_maintenance.py regenerate
    python3 daily_maintenance.py regenerate --verbose
    python3 daily_maintenance.py status
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/home/workspace")
N5_ROOT = WORKSPACE / "N5"
DATA_DIR = N5_ROOT / "data"
INSIGHTS_DIR = N5_ROOT / "insights/resonance"

# Ensure imports work
sys.path.insert(0, str(N5_ROOT / "scripts/resonance"))


def regenerate_index(verbose: bool = False) -> dict:
    """Regenerate resonance index and save daily report."""
    from pattern_surfacer import generate_resonance_index, generate_report
    
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps": []
    }
    
    # Step 1: Regenerate index
    if verbose:
        print("Regenerating resonance index...")
    
    index = generate_resonance_index()
    result["steps"].append({
        "action": "regenerate_index",
        "status": "success",
        "total_ideas": index.get("total_ideas", 0),
        "summary": index.get("summary", {})
    })
    
    # Step 2: Generate and save daily report
    if verbose:
        print("Generating daily report...")
    
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = INSIGHTS_DIR / f"{report_date}_resonance_report.md"
    
    report = generate_report(index)
    report_path.write_text(report)
    
    result["steps"].append({
        "action": "save_report",
        "status": "success",
        "path": str(report_path)
    })
    
    # Step 3: Check for notable changes (optional comparison with yesterday)
    yesterday_path = INSIGHTS_DIR / f"{(datetime.now().replace(day=datetime.now().day-1)).strftime('%Y-%m-%d')}_resonance_report.md"
    if yesterday_path.exists():
        result["steps"].append({
            "action": "compare_yesterday",
            "status": "available",
            "yesterday_report": str(yesterday_path)
        })
    
    result["status"] = "success"
    return result


def get_status() -> dict:
    """Get current resonance system status."""
    index_path = DATA_DIR / "resonance_index.json"
    evolution_log_path = DATA_DIR / "evolution_log.jsonl"
    
    status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "index": {},
        "evolution_log": {},
        "recent_reports": []
    }
    
    # Check index
    if index_path.exists():
        try:
            with open(index_path) as f:
                index = json.load(f)
            status["index"] = {
                "exists": True,
                "generated_at": index.get("generated_at"),
                "total_ideas": index.get("total_ideas", 0),
                "summary": index.get("summary", {})
            }
        except Exception as e:
            status["index"] = {"exists": True, "error": str(e)}
    else:
        status["index"] = {"exists": False}
    
    # Check evolution log
    if evolution_log_path.exists():
        try:
            event_count = sum(1 for _ in open(evolution_log_path))
            status["evolution_log"] = {
                "exists": True,
                "event_count": event_count
            }
        except Exception as e:
            status["evolution_log"] = {"exists": True, "error": str(e)}
    else:
        status["evolution_log"] = {"exists": False}
    
    # List recent reports
    if INSIGHTS_DIR.exists():
        reports = sorted(INSIGHTS_DIR.glob("*_resonance_report.md"), reverse=True)[:5]
        status["recent_reports"] = [r.name for r in reports]
    
    return status


def main():
    parser = argparse.ArgumentParser(description="Daily resonance maintenance")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Regenerate command
    regen_parser = subparsers.add_parser("regenerate", help="Regenerate index and reports")
    regen_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "regenerate":
            result = regenerate_index(verbose=args.verbose)
            print(json.dumps(result, indent=2))
        
        elif args.command == "status":
            status = get_status()
            print(json.dumps(status, indent=2))
    
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


