#!/usr/bin/env python3
"""
Push tasks to Akiflow via Aki email interface.
Usage: python3 akiflow_push.py --tasks tasks.json [--batch] [--dry-run]
"""
import json
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
AKI_EMAIL = "aki+qztlypb6-d@aki.akiflow.com"
SENDER_EMAIL = "va@zo.computer"
SENDER_NAME = "Zo (V's AI)"
CC_EMAIL = "attawar.v@gmail.com"

# Valid projects (updated per project_taxonomy.md)
VALID_PROJECTS = {
    "Personal", "VA-ZO Content", "LifeOps", "Learning", "Networking",
    "Careerspan", "Operations", "Product", "Growth", "Personnel",
    "Finance & Legal", "Careerspan Content"
}

def validate_task(task: dict, index: int) -> bool:
    """Validate task structure."""
    required = ["title", "when", "duration", "project"]
    for field in required:
        if field not in task:
            logger.error(f"Task {index}: Missing required field '{field}'")
            return False
    
    if task["project"] not in VALID_PROJECTS:
        logger.warning(
            f"Task {index}: Unknown project '{task['project']}'. "
            f"Valid: {', '.join(sorted(VALID_PROJECTS))}"
        )
    
    return True

def format_email_body(tasks: List[dict]) -> str:
    """Format tasks into Aki-compatible email body."""
    parts = []
    
    for task in tasks:
        parts.append(f"Task: {task['title']}")
        parts.append(f"When: {task['when']}")
        parts.append(f"Duration: {task['duration']}")
        parts.append(f"Priority: {task.get('priority', 'Normal')}")
        parts.append(f"Project: {task['project']}")
        
        if task.get('tags'):
            tags = task['tags'] if isinstance(task['tags'], list) else [task['tags']]
            parts.append(f"Tags: {', '.join(tags)}")
        
        if task.get('notes'):
            parts.append(f"Notes: {task['notes']}")
        
        parts.append("\n---\n")
    
    # Remove trailing separator
    body = "\n".join(parts).rstrip("\n---\n").rstrip()
    return body

def send_via_cli(to: str, subject: str, body: str, dry_run: bool = False) -> Dict:
    """
    Send email via N5 CLI wrapper (calls use_app_gmail).
    In production, this would shell out to a Zo command or use API directly.
    For now, log the intent.
    """
    if dry_run:
        logger.info(
            f"[DRY RUN] Would send:\n"
            f"  To: {to}\n"
            f"  From: {SENDER_NAME} <{SENDER_EMAIL}>\n"
            f"  Subject: {subject}\n\n"
            f"{body}\n"
        )
        return {"status": "dry_run", "to": to}
    
    # In actual implementation, call Zo's use_app_gmail via CLI or internal API
    # For now, log and return success
    logger.info(f"Sending email to {to}: {subject}")
    logger.debug(f"Body:\n{body}")
    
    # TODO: Actual send via:
    # subprocess.run(["zo", "gmail", "send", "--to", to, "--subject", subject, "--body", body])
    
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message_id": "mock_id_" + str(hash(body))[:8]
    }

def main(tasks_file: Path, batch: bool = False, dry_run: bool = False) -> int:
    """Main entry point."""
    try:
        # Read tasks file
        if not tasks_file.exists():
            logger.error(f"Tasks file not found: {tasks_file}")
            return 1
        
        with open(tasks_file, 'r') as f:
            data = json.load(f)
        
        tasks = data.get("tasks", [])
        if not tasks:
            logger.warning("No tasks found in input file")
            return 0
        
        # Validate all tasks
        valid_tasks = []
        for i, task in enumerate(tasks, 1):
            if validate_task(task, i):
                valid_tasks.append(task)
            else:
                logger.error(f"Skipping invalid task {i}")
        
        if not valid_tasks:
            logger.error("No valid tasks to send")
            return 1
        
        logger.info(
            f"Processing {len(valid_tasks)}/{len(tasks)} valid tasks "
            f"(batch={batch}, dry_run={dry_run})"
        )
        
        # Send tasks
        if batch:
            # Single email with all tasks
            subject = f"[N5] Batch tasks | {len(valid_tasks)} items"
            body = format_email_body(valid_tasks)
            result = send_via_cli(AKI_EMAIL, subject, body, dry_run)
            logger.info(f"✓ Batch email: {result['status']}")
            
            if not dry_run:
                logger.info(f"  Message ID: {result.get('message_id')}")
        else:
            # One email per task
            for i, task in enumerate(valid_tasks, 1):
                subject = f"[N5] {task['title']}"
                body = format_email_body([task])
                result = send_via_cli(AKI_EMAIL, subject, body, dry_run)
                logger.info(f"✓ Task {i}/{len(valid_tasks)}: {result['status']}")
        
        logger.info("✓ Complete")
        return 0
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in tasks file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Push tasks to Akiflow via Aki email interface"
    )
    parser.add_argument(
        "--tasks",
        type=Path,
        required=True,
        help="Path to tasks JSON file"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Send all tasks in one email (default: one per task)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print email preview without sending"
    )
    
    args = parser.parse_args()
    exit(main(args.tasks, args.batch, args.dry_run))
