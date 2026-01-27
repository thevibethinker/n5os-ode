#!/usr/bin/env python3
"""
SMS Survey Handler for Dynamic Survey Analyzer

Handles SMS commands for survey analysis operations.

Commands:
    n5 survey analyze <form_id>     - Run full analysis on a form
    n5 survey status <form_id>      - Check analysis status
    n5 survey list                  - List all analyzed surveys
    n5 survey refresh <form_id>     - Re-run analysis with latest data

Usage:
    python3 sms_survey_handler.py --message "n5 survey analyze jPQRwpT4nGus"
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SURVEYS_DIR = Path("/home/workspace/Datasets/survey-analyses")
SCRIPTS_DIR = Path("/home/workspace/Skills/dynamic-survey-analyzer/scripts")


def parse_command(message: str) -> tuple[str, list[str]]:
    """Parse SMS message into command and arguments."""
    message = message.strip()
    
    # Match "n5 survey <command> [args...]"
    match = re.match(r"n5\s+survey\s+(\w+)\s*(.*)", message, re.IGNORECASE)
    if not match:
        return "help", []
    
    command = match.group(1).lower()
    args_str = match.group(2).strip()
    args = args_str.split() if args_str else []
    
    return command, args


def cmd_analyze(args: list[str]) -> str:
    """Run full analysis on a form."""
    if not args:
        return "❌ Missing form_id. Usage: n5 survey analyze <form_id>"
    
    form_id = args[0]
    
    # Run the analysis
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "run_analysis.py"), form_id, "--json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        return f"❌ Analysis failed: {result.stderr[:200]}"
    
    try:
        data = json.loads(result.stdout)
        return (
            f"✓ Analysis complete for {form_id}\n"
            f"Submissions: {data['filtered_submissions']}/{data['total_submissions']} eligible\n"
            f"Output: {data['output_dir']}"
        )
    except json.JSONDecodeError:
        return f"✓ Analysis complete for {form_id}"


def cmd_status(args: list[str]) -> str:
    """Check analysis status for a form."""
    if not args:
        return "❌ Missing form_id. Usage: n5 survey status <form_id>"
    
    form_id = args[0]
    survey_dir = SURVEYS_DIR / form_id
    
    if not survey_dir.exists():
        return f"❌ No analysis found for {form_id}"
    
    meta_path = survey_dir / "meta.json"
    if not meta_path.exists():
        return f"⚠️ Analysis exists but meta.json missing for {form_id}"
    
    meta = json.loads(meta_path.read_text())
    
    last_updated = meta.get("last_updated", "Unknown")
    if last_updated != "Unknown":
        try:
            dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            last_updated = dt.strftime("%Y-%m-%d %H:%M ET")
        except:
            pass
    
    return (
        f"📊 {meta.get('form_name', form_id)}\n"
        f"ID: {form_id}\n"
        f"Submissions: {meta.get('filtered_submissions', '?')}/{meta.get('total_submissions', '?')}\n"
        f"Last updated: {last_updated}\n"
        f"Level Upper: {'✓' if meta.get('level_upper_enabled') else '✗'}"
    )


def cmd_list(args: list[str]) -> str:
    """List all analyzed surveys."""
    if not SURVEYS_DIR.exists():
        return "No surveys analyzed yet."
    
    surveys = []
    for survey_dir in SURVEYS_DIR.iterdir():
        if survey_dir.is_dir():
            meta_path = survey_dir / "meta.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                name = meta.get("form_name", survey_dir.name)[:30]
                count = meta.get("filtered_submissions", "?")
                surveys.append(f"• {name} ({count} responses)")
            else:
                surveys.append(f"• {survey_dir.name} (no meta)")
    
    if not surveys:
        return "No surveys analyzed yet."
    
    return f"📊 Analyzed Surveys ({len(surveys)}):\n" + "\n".join(surveys)


def cmd_refresh(args: list[str]) -> str:
    """Re-run analysis with latest data."""
    if not args:
        return "❌ Missing form_id. Usage: n5 survey refresh <form_id>"
    
    form_id = args[0]
    survey_dir = SURVEYS_DIR / form_id
    
    if not survey_dir.exists():
        return f"❌ No existing analysis for {form_id}. Use 'n5 survey analyze {form_id}' first."
    
    # Get current meta for comparison
    meta_path = survey_dir / "meta.json"
    old_count = 0
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        old_count = meta.get("total_submissions", 0)
    
    # Run fresh analysis
    result = cmd_analyze([form_id])
    
    # Check for new submissions
    if meta_path.exists():
        new_meta = json.loads(meta_path.read_text())
        new_count = new_meta.get("total_submissions", 0)
        if new_count > old_count:
            result += f"\n📈 {new_count - old_count} new submissions since last analysis"
    
    return result


def cmd_help(args: list[str]) -> str:
    """Show help message."""
    return (
        "📊 Survey Commands:\n"
        "• n5 survey analyze <form_id> - Run analysis\n"
        "• n5 survey status <form_id> - Check status\n"
        "• n5 survey list - List all surveys\n"
        "• n5 survey refresh <form_id> - Re-run analysis"
    )


COMMANDS = {
    "analyze": cmd_analyze,
    "status": cmd_status,
    "list": cmd_list,
    "refresh": cmd_refresh,
    "help": cmd_help,
}


def handle_message(message: str) -> str:
    """Process an SMS message and return response."""
    command, args = parse_command(message)
    
    handler = COMMANDS.get(command, cmd_help)
    return handler(args)


def main():
    parser = argparse.ArgumentParser(description="SMS Survey Handler")
    parser.add_argument("--message", "-m", required=True, help="SMS message to process")
    
    args = parser.parse_args()
    
    response = handle_message(args.message)
    print(response)


if __name__ == "__main__":
    main()
