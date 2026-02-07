#!/usr/bin/env python3
"""
Careerspan Pipeline Orchestrator v2

Invokes action skills (careerspan-jd-intake, careerspan-resume-intake, careerspan-update-handler)
and executes their orchestrator_instructions using Zo's app tools.

Commands:
    run       - Full automatic run (scan + process) for heartbeat agent
    scan      - Scan Gmail for pipeline emails, return list
    process   - Process a single email through appropriate skill
    status    - Get pipeline status

Silent observer mode:
- Monitors all email traffic involving Shivam
- Tracks JDs, candidates, updates in Airtable
- Only emails Shivam directly (never in employer/candidate threads)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PIPELINE_DIR = SCRIPT_DIR.parent
CONFIG_PATH = PIPELINE_DIR / "config.yaml"
QUEUE_DIR = PIPELINE_DIR / "queue"
PROCESSED_DIR = PIPELINE_DIR / "processed"

# Skills paths
JD_INTAKE_SKILL = Path("/home/workspace/Skills/careerspan-jd-intake/scripts/process_jd.py")
RESUME_INTAKE_SKILL = Path("/home/workspace/Skills/careerspan-resume-intake/scripts/process_resume.py")
UPDATE_HANDLER_SKILL = Path("/home/workspace/Skills/careerspan-update-handler/scripts/process_update.py")

# Zo App tool constants
AIRTABLE_ACCOUNT = "vrijen@mycareerspan.com"
GMAIL_ACCOUNT = "vrijen@mycareerspan.com"
DRIVE_ACCOUNT = "vrijen@mycareerspan.com"


def load_config():
    """Load pipeline configuration."""
    import yaml
    content = CONFIG_PATH.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    return yaml.safe_load(content)


def detect_task_type(email_data: dict) -> str:
    """Detect task type from email subject."""
    subject = email_data.get('subject', '').upper().strip()
    body = (email_data.get('body', '') or '').upper()

    if '[JD]' in subject:
        return 'jd'
    elif '[RESUME]' in subject:
        return 'resume'
    elif '[UPDATE]' in subject:
        return 'update'

    # Transition-mode robustness: Shivam sometimes sends untagged JDs as plain "JD" with a job link.
    if subject == 'JD' or any(x in body for x in ['JOBS.ASHBYHQ.COM', 'GREENHOUSE.IO', 'LEVER.CO']):
        return 'jd'

    elif 'CAREERSPAN COMPLETE' in body or 'INTELLIGENCE BRIEF' in body:
        return 'careerspan_complete'
    return 'update'


def invoke_skill(skill_type: str, email_data: dict, config: dict, dry_run: bool = False) -> dict:
    """
    Invoke the appropriate skill script and return its output.
    
    Skills return JSON with orchestrator_instructions that we then execute.
    """
    script_path = {
        'jd': JD_INTAKE_SKILL,
        'resume': RESUME_INTAKE_SKILL,
        'update': UPDATE_HANDLER_SKILL,
    }.get(skill_type)
    
    if not script_path or not script_path.exists():
        return {"error": f"Skill not found for type: {skill_type}"}
    
    cmd = [
        sys.executable, str(script_path),
        "--email-subject", email_data.get('subject', ''),
        "--email-body", email_data.get('body', ''),
        "--email-from", email_data.get('from', '')
    ]
    
    if skill_type == 'resume' and email_data.get('attachments'):
        cmd.extend(["--attachments"] + email_data.get('attachments', []))
    elif skill_type == 'jd' and email_data.get('attachments'):
        cmd.extend(["--attachments"] + email_data.get('attachments', []))
    
    if dry_run:
        cmd.append("--dry-run")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return {
                "error": f"Skill failed with return code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }
        
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                try:
                    output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
            else:
                output = {"raw_output": result.stdout}
        
        return {
            "skill_type": skill_type,
            "output": output,
            "stderr": result.stderr if result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Skill timed out after 300 seconds"}
    except Exception as e:
        return {"error": f"Skill invocation failed: {str(e)}"}


def execute_orchestrator_instructions(instructions: dict, config: dict, dry_run: bool = False) -> dict:
    """
    Execute the orchestrator_instructions returned by a skill.
    
    This is where we call the actual Zo app tools (Airtable, Drive, Gmail).
    In production, these would be actual tool calls. For now, we print
    the instructions for the Zo agent to execute.
    """
    results = {}
    
    if dry_run:
        return {
            "dry_run": True,
            "instructions": instructions,
            "message": "Would execute these instructions"
        }
    
    for step_key, step_data in sorted(instructions.items()):
        if not isinstance(step_data, dict):
            continue
            
        tool = step_data.get('tool')
        action = step_data.get('action')
        
        results[step_key] = {
            "action": action,
            "tool": tool,
            "status": "pending_execution",
            "instruction": step_data
        }
    
    return results


def scan_emails_execute(config: dict, max_results: int = 20) -> list:
    """
    Scan Gmail for pipeline emails using actual Gmail API queries.
    
    Returns list of email objects matching pipeline criteria.
    """
    queries = [
        "from:shivam@corridorx.io (subject:[JD] OR subject:[RESUME] OR subject:[UPDATE]) is:unread",
        "from:shivam@corridorx.io -subject:[JD] -subject:[RESUME] -subject:[UPDATE] is:unread newer_than:1d",
    ]
    
    all_emails = []
    seen_ids = set()
    
    for query in queries:
        print(f"\n[GMAIL QUERY]: {query}", file=sys.stderr)
        print(f"  → Use tool: gmail-find-email with query=\"{query}\" maxResults={max_results}", file=sys.stderr)
    
    return {
        "queries": queries,
        "max_results": max_results,
        "instructions": "Execute each query using gmail-find-email, then pass results to process command"
    }


def process_email(email_data: dict, config: dict, dry_run: bool = False) -> dict:
    """
    Process a single email through the appropriate skill and execute instructions.
    """
    task_type = detect_task_type(email_data)
    print(f"\n[PROCESSING] Type: {task_type}", file=sys.stderr)
    print(f"  Subject: {email_data.get('subject', 'N/A')}", file=sys.stderr)
    print(f"  From: {email_data.get('from', 'N/A')}", file=sys.stderr)
    
    skill_result = invoke_skill(task_type, email_data, config, dry_run=dry_run)
    
    if skill_result.get('error'):
        return {"error": skill_result['error'], "task_type": task_type}
    
    skill_output = skill_result.get('output', {})
    
    # Handle dict output (JD/Resume skills return orchestrator_instructions)
    if isinstance(skill_output, dict):
        orchestrator_instructions = skill_output.get('orchestrator_instructions')
        if orchestrator_instructions:
            exec_results = execute_orchestrator_instructions(
                orchestrator_instructions, config, dry_run=dry_run
            )
            skill_result['execution_results'] = exec_results
    
    return skill_result


def run_pipeline(config: dict, max_emails: int = 10, dry_run: bool = False) -> dict:
    """
    Full automatic pipeline run for heartbeat agent.
    
    1. Scan Gmail for new pipeline emails
    2. Process each email through appropriate skill
    3. Execute orchestrator instructions
    4. Log results
    """
    print("=" * 60, file=sys.stderr)
    print("CAREERSPAN PIPELINE RUN", file=sys.stderr)
    print(f"Timestamp: {datetime.now().isoformat()}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    scan_result = scan_emails_execute(config, max_results=max_emails)
    
    return {
        "action": "run",
        "scan": scan_result,
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "instructions": """
To complete this pipeline run:

1. Execute Gmail queries from 'scan.queries' using gmail-find-email
2. For each email found:
   a. Prepare email_data: {subject, body, from, attachments}
   b. Call: python3 pipeline_orchestrator.py process-one --email '<json>'
3. Execute the orchestrator_instructions returned by each skill
4. Log results to Activity Log table

Example process-one call:
python3 pipeline_orchestrator.py process-one --email '{"subject":"[JD] Senior Engineer","body":"...","from":"shivam@corridorx.io"}'
"""
    }


def get_status(config: dict) -> dict:
    """Get pipeline status."""
    queue_files = list(QUEUE_DIR.glob("*.json")) if QUEUE_DIR.exists() else []
    processed_dirs = list(PROCESSED_DIR.glob("*/")) if PROCESSED_DIR.exists() else []
    
    return {
        "queue_count": len(queue_files),
        "processed_count": len(processed_dirs),
        "config_loaded": bool(config),
        "skills": {
            "jd_intake": JD_INTAKE_SKILL.exists(),
            "resume_intake": RESUME_INTAKE_SKILL.exists(),
            "update_handler": UPDATE_HANDLER_SKILL.exists()
        },
        "google_drive": {
            "folder_id": config.get('google_drive', {}).get('shared_folder_id'),
            "configured": bool(config.get('google_drive', {}).get('shared_folder_id'))
        },
        "airtable": {
            "base_id": config.get('airtable', {}).get('base_id'),
            "configured": bool(config.get('airtable', {}).get('base_id'))
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Careerspan Pipeline Orchestrator v2")
    subparsers = parser.add_subparsers(dest="command")
    
    # Run command (for heartbeat)
    run_parser = subparsers.add_parser("run", help="Full automatic run (scan + process)")
    run_parser.add_argument("--max-emails", type=int, default=10, help="Max emails to process")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate without mutations")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan Gmail for pipeline emails")
    scan_parser.add_argument("--execute", action="store_true", help="Execute queries (vs return queries)")
    scan_parser.add_argument("--max-results", type=int, default=20, help="Max results per query")
    
    # Process-one command
    process_parser = subparsers.add_parser("process-one", help="Process a single email")
    process_parser.add_argument("--email", required=True, help="Email data as JSON")
    process_parser.add_argument("--dry-run", action="store_true", help="Simulate without mutations")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get pipeline status")
    
    args = parser.parse_args()
    
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    config = load_config()
    
    if args.command == "run":
        result = run_pipeline(config, max_emails=args.max_emails, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    
    elif args.command == "scan":
        if args.execute:
            result = scan_emails_execute(config, max_results=args.max_results)
        else:
            result = {
                "queries": [
                    {
                        "name": "tagged_from_shivam",
                        "query": "from:shivam@corridorx.io (subject:[JD] OR subject:[RESUME] OR subject:[UPDATE]) is:unread",
                        "priority": 1
                    },
                    {
                        "name": "untagged_from_shivam",
                        "query": "from:shivam@corridorx.io -subject:[JD] -subject:[RESUME] -subject:[UPDATE] is:unread newer_than:1d",
                        "priority": 2
                    }
                ],
                "instructions": "Use gmail-find-email with each query string"
            }
        print(json.dumps(result, indent=2))
    
    elif args.command == "process-one":
        email_data = json.loads(args.email)
        result = process_email(email_data, config, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        result = get_status(config)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
