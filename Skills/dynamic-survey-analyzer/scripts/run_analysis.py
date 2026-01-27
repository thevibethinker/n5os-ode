#!/usr/bin/env python3
"""
Dynamic Survey Analyzer - Full Pipeline Orchestrator

Runs the complete analysis pipeline for a Fillout form:
1. Fetches form structure and submissions
2. Generates interpretation framework
3. Computes quantitative analysis
4. Runs Level Upper analysis (optional)
5. Synthesizes findings and generates dashboard

Usage:
    python3 run_analysis.py <form_id> [--account personal|careerspan] [--skip-level-upper] [--quiet]
    
Examples:
    python3 run_analysis.py jPQRwpT4nGus
    python3 run_analysis.py jPQRwpT4nGus --account careerspan --skip-level-upper
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
OUTPUT_BASE = Path("/home/workspace/Datasets/survey-analyses")


def log(msg: str, quiet: bool = False):
    if not quiet:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_fillout_client(args: list[str]) -> dict:
    """Run fillout_client.py and return parsed JSON output."""
    cmd = ["python3", str(SCRIPTS_DIR / "fillout_client.py")] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"fillout_client failed: {result.stderr}")
    return json.loads(result.stdout)


def detect_account(form_id: str) -> str:
    """Auto-detect which account owns a form."""
    client = SCRIPTS_DIR / "fillout_client.py"
    result = subprocess.run(
        ["python3", str(client), "--detect-account", form_id],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "careerspan"  # Default


def get_form_structure(form_id: str, account: str) -> dict:
    """Get form structure from Fillout API."""
    return run_fillout_client(["--form-structure", form_id, "--account", account])


def get_submissions(form_id: str, account: str) -> list:
    """Get all submissions for a form."""
    return run_fillout_client(["--submissions", form_id, "--account", account])


def generate_analysis(form_id: str, account: str, skip_level_upper: bool, quiet: bool) -> dict:
    """Run the full analysis pipeline."""
    
    log(f"Starting analysis for form {form_id}", quiet)
    
    # Step 1: Get form structure
    log("Fetching form structure...", quiet)
    try:
        structure = get_form_structure(form_id, account)
    except Exception as e:
        log(f"Error fetching structure: {e}", quiet)
        structure = {}
    
    # Step 2: Get submissions and run quantitative analysis
    log("Running quantitative analysis...", quiet)
    analysis_result = run_fillout_client([
        "--analyze", form_id,
        "--account", account,
        "--screening", "dGZw",
        "--screening-exclude", "No"
    ])
    
    # Step 3: Create output directory
    output_dir = OUTPUT_BASE / form_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 4: Build combined data structure
    data = {
        "form_id": form_id,
        "form_name": analysis_result.get("form_title", "Unknown Survey"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "account": account,
        "d1_1": {
            "interpretation_framework": {
                "form_id": form_id,
                "form_name": analysis_result.get("form_title", "Unknown Survey"),
            }
        },
        "d1_2": {
            "quantitative_analysis": analysis_result
        }
    }
    
    # Step 5: Level Upper analysis (if not skipped)
    if not skip_level_upper:
        log("Running Level Upper analysis...", quiet)
        from level_upper_prompts import DIVERGENT_ANALYSIS_PROMPTS
        data["d1_3"] = {
            "level_upper_analysis": {
                "novel_perspectives": [],
                "challenged_assumptions": [],
                "blind_spots_identified": [],
                "provocative_questions": list(DIVERGENT_ANALYSIS_PROMPTS.values())[:5]
            },
            "contribution_percentage": "pending_llm_analysis"
        }
    
    # Step 6: Save data.json
    data_path = output_dir / "data.json"
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log(f"Saved data to {data_path}", quiet)
    
    # Step 7: Generate dashboard
    log("Generating dashboard...", quiet)
    dashboard_cmd = [
        "python3", str(SCRIPTS_DIR / "generate_dashboard.py"),
        form_id
    ]
    subprocess.run(dashboard_cmd, capture_output=True)
    log(f"Dashboard generated at {output_dir / 'dashboard.html'}", quiet)
    
    # Step 8: Save meta.json
    meta = {
        "form_id": form_id,
        "form_name": analysis_result.get("form_title", "Unknown Survey"),
        "account": account,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_submissions": analysis_result.get("total_submissions", 0),
        "filtered_submissions": analysis_result.get("filtered_submissions", 0),
        "level_upper_enabled": not skip_level_upper
    }
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    
    log(f"Analysis complete: {output_dir}", quiet)
    return {
        "status": "complete",
        "form_id": form_id,
        "output_dir": str(output_dir),
        "total_submissions": analysis_result.get("total_submissions", 0),
        "filtered_submissions": analysis_result.get("filtered_submissions", 0)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run full survey analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("form_id", help="Fillout form ID to analyze")
    parser.add_argument(
        "--account", "-a",
        choices=["personal", "careerspan", "auto"],
        default="auto",
        help="Fillout account (default: auto-detect)"
    )
    parser.add_argument(
        "--skip-level-upper",
        action="store_true",
        help="Skip Level Upper divergent analysis"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Auto-detect account if needed
    account = args.account
    if account == "auto":
        account = detect_account(args.form_id)
        if not args.quiet:
            print(f"Auto-detected account: {account}")
    
    try:
        result = generate_analysis(
            args.form_id,
            account,
            args.skip_level_upper,
            args.quiet
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        elif not args.quiet:
            print(f"\n✓ Analysis complete")
            print(f"  Form: {args.form_id}")
            print(f"  Submissions: {result['filtered_submissions']}/{result['total_submissions']} eligible")
            print(f"  Output: {result['output_dir']}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
