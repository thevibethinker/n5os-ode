#!/usr/bin/env python3
"""
N5 Meeting Approve — Enhanced Implementation

Approve meeting outputs and trigger downstream actions:
- Review generated deliverables
- Send follow-up emails  
- Update CRM
- Schedule follow-up meetings
- Auto-generate email drafts for external meetings

Version: 3.0.0
Date: 2025-10-13
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "N5/records/meetings"
EMAIL_GENERATOR_SCRIPT = WORKSPACE / "N5/scripts/n5_follow_up_email_generator.py"


def find_meeting_folder(meeting_name: str) -> Optional[Path]:
    """Find meeting folder by name or partial match"""
    meeting_path = MEETINGS_DIR / meeting_name
    
    if meeting_path.exists():
        return meeting_path
    
    # Try partial match
    matches = list(MEETINGS_DIR.glob(f"*{meeting_name}*"))
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        logger.warning(f"Multiple meetings match '{meeting_name}':")
        for m in matches:
            logger.warning(f"  - {m.name}")
        return None
    
    return None


def check_meeting_deliverables(meeting_dir: Path) -> Dict:
    """Check which deliverables have been generated"""
    deliverables_dir = meeting_dir / "DELIVERABLES"
    
    status = {
        "follow_up_email": False,
        "blurb": False,
        "one_pager": False,
        "proposal": False
    }
    
    if not deliverables_dir.exists():
        return status
    
    # Check for email
    if (deliverables_dir / "follow_up_email_draft.md").exists():
        status["follow_up_email"] = True
    
    # Check for other deliverables
    if (deliverables_dir / "blurbs").exists():
        status["blurb"] = len(list((deliverables_dir / "blurbs").glob("*.md"))) > 0
    
    if (deliverables_dir / "one_pagers").exists():
        status["one_pager"] = len(list((deliverables_dir / "one_pagers").glob("*.md"))) > 0
    
    if (deliverables_dir / "proposals_pricing").exists():
        status["proposal"] = len(list((deliverables_dir / "proposals_pricing").glob("*.md"))) > 0
    
    return status


def generate_missing_deliverables(
    meeting_dir: Path,
    deliverables: List[str],
    dry_run: bool = False
) -> bool:
    """Generate requested deliverables if missing"""
    
    if dry_run:
        logger.info("[DRY RUN] Would generate: %s", ", ".join(deliverables))
        return True
    
    logger.info("Generating deliverables: %s", ", ".join(deliverables))
    
    try:
        result = subprocess.run(
            [
                "python3",
                str(WORKSPACE / "N5/scripts/generate_deliverables.py"),
                meeting_dir.name,
                "--deliverables", ",".join(deliverables)
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(WORKSPACE)
        )
        
        logger.info("✓ Deliverables generated successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate deliverables: {e.stderr}")
        return False


def is_external_meeting(meeting_dir: Path) -> bool:
    """
    Determine if meeting is with external stakeholder.
    
    Checks:
    1. Meeting ID contains '_external-' prefix
    2. stakeholder_profile.md exists in meeting folder
    
    Returns:
        bool: True if external stakeholder meeting
    """
    # Check folder name pattern
    if "_external-" in meeting_dir.name:
        return True
    
    # Check for stakeholder profile
    profile_path = meeting_dir / "stakeholder_profile.md"
    if profile_path.exists():
        return True
    
    # Check _metadata.json for classification
    metadata_path = meeting_dir / "_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            classification = metadata.get("stakeholder_classification", "")
            return classification == "external"
        except Exception as e:
            logger.debug(f"Could not read metadata: {e}")
    
    return False


def generate_follow_up_email(
    meeting_dir: Path,
    dry_run: bool = False
) -> Dict:
    """
    Generate follow-up email draft using email generator script.
    
    Args:
        meeting_dir: Path to meeting folder
        dry_run: If True, preview without executing
        
    Returns:
        dict: Result with status, output_files, and any errors
    """
    result = {
        "status": "pending",
        "output_files": [],
        "errors": []
    }
    
    # Check if generator script exists
    if not EMAIL_GENERATOR_SCRIPT.exists():
        result["status"] = "error"
        result["errors"].append(f"Email generator script not found: {EMAIL_GENERATOR_SCRIPT}")
        return result
    
    # Check if email already exists
    deliverables_dir = meeting_dir / "DELIVERABLES"
    existing_draft = deliverables_dir / "follow_up_email_copy_paste.txt"
    
    if existing_draft.exists():
        logger.info("✓ Email draft already exists: %s", existing_draft)
        result["status"] = "exists"
        result["output_files"].append(str(existing_draft))
        return result
    
    if dry_run:
        logger.info("[DRY RUN] Would generate email for: %s", meeting_dir.name)
        result["status"] = "dry_run"
        return result
    
    # Execute email generator
    logger.info("Generating follow-up email for: %s", meeting_dir.name)
    
    try:
        cmd = [
            "python3",
            str(EMAIL_GENERATOR_SCRIPT),
            str(meeting_dir),
            "--output-dir", str(deliverables_dir)
        ]
        
        proc_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(WORKSPACE)
        )
        
        if proc_result.returncode == 0:
            logger.info("✓ Email generated successfully")
            result["status"] = "success"
            
            # Find generated files
            if deliverables_dir.exists():
                for file in deliverables_dir.glob("follow_up_email*"):
                    result["output_files"].append(str(file))
        else:
            logger.error("Email generation failed: %s", proc_result.stderr)
            result["status"] = "error"
            result["errors"].append(proc_result.stderr)
        
    except subprocess.TimeoutExpired:
        logger.error("Email generation timed out after 5 minutes")
        result["status"] = "error"
        result["errors"].append("Generation timeout (>5 min)")
    except Exception as e:
        logger.error("Email generation error: %s", e)
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result


def send_notification_sms(
    meeting_name: str,
    email_files: List[str],
    success: bool = True
) -> bool:
    """
    Send SMS notification about email draft generation.
    
    Creates a notification file that triggers Zo to send SMS via send_sms_to_user.
    
    Args:
        meeting_name: Name of the meeting
        email_files: List of generated email file paths
        success: Whether generation was successful
        
    Returns:
        bool: True if notification queued successfully
    """
    try:
        # Create notification queue directory
        notification_queue = WORKSPACE / "N5/inbox/notifications"
        notification_queue.mkdir(parents=True, exist_ok=True)
        
        # Build message
        if success:
            message = f"✓ Follow-up email draft ready: {meeting_name}\n\n"
            if email_files:
                # Extract just the filename for brevity
                filename = Path(email_files[0]).name
                message += f"Location: DELIVERABLES/{filename}"
            else:
                message += f"Location: N5/records/meetings/{meeting_name}/DELIVERABLES/"
        else:
            message = f"⚠️ Email generation failed: {meeting_name}\n\nCheck N5/logs/ for details."
        
        # Create notification payload
        import time
        timestamp = int(time.time())
        notification = {
            "type": "sms",
            "message": message,
            "timestamp": timestamp,
            "priority": "normal",
            "source": "n5_meeting_approve",
            "meeting": meeting_name
        }
        
        # Write to queue
        notification_file = notification_queue / f"sms_{timestamp}_{meeting_name[:30]}.json"
        notification_file.write_text(json.dumps(notification, indent=2))
        
        logger.info("✓ SMS notification queued: %s", notification_file)
        logger.info("   Message: %s", message.replace("\n", " | "))
        
        return True
        
    except Exception as e:
        logger.error("Failed to queue SMS notification: %s", e)
        return False


def approve_and_process(
    meeting_dir: Path,
    actions: List[str],
    dry_run: bool = False,
    auto_generate_email: bool = True
) -> Dict:
    """Approve meeting and trigger downstream actions"""
    
    results = {
        "meeting": meeting_dir.name,
        "actions_requested": actions,
        "actions_completed": [],
        "actions_failed": [],
        "email_generation": None
    }
    
    # Check if external meeting
    is_external = is_external_meeting(meeting_dir)
    logger.info("Meeting type: %s", "EXTERNAL" if is_external else "INTERNAL")
    
    # Auto-generate email for external meetings
    if is_external and auto_generate_email:
        logger.info("🔄 Auto-generating follow-up email (external stakeholder)...")
        email_result = generate_follow_up_email(meeting_dir, dry_run)
        results["email_generation"] = email_result
        
        if email_result["status"] == "success":
            logger.info("✓ Email draft generated successfully")
            
            # Send SMS notification
            if not dry_run:
                send_notification_sms(
                    meeting_dir.name,
                    email_result["output_files"],
                    success=True
                )
        elif email_result["status"] == "exists":
            logger.info("✓ Email draft already exists")
        elif email_result["status"] == "error":
            logger.warning("⚠️ Email generation failed: %s", email_result["errors"])
            if not dry_run:
                send_notification_sms(
                    meeting_dir.name,
                    [],
                    success=False
                )
    elif not is_external:
        logger.info("⏭️  Skipping email generation (internal meeting)")
        results["email_generation"] = {"status": "skipped", "reason": "internal meeting"}
    
    # Check stakeholder profile for backwards compatibility
    profile_path = meeting_dir / "stakeholder_profile.md"
    
    if not is_external and "send_email" in actions:
        logger.warning("⚠️  No stakeholder profile found - skipping email send")
        results["actions_failed"].append({
            "action": "send_email",
            "reason": "No stakeholder profile (internal meeting?)"
        })
        actions = [a for a in actions if a != "send_email"]
    
    # Process each action
    for action in actions:
        logger.info(f"Processing action: {action}")
        
        if action == "send_email":
            # Check if email draft exists
            email_draft = meeting_dir / "DELIVERABLES" / "follow_up_email_copy_paste.txt"
            
            if not email_draft.exists():
                # Should have been auto-generated above
                logger.warning("Email draft missing after auto-generation")
                results["actions_failed"].append({
                    "action": "send_email",
                    "reason": "Email draft not found"
                })
                continue
            
            if dry_run:
                logger.info("[DRY RUN] Would display email for review and send")
            else:
                # Display email for review
                email_content = email_draft.read_text()
                print("\n" + "="*70)
                print("EMAIL DRAFT READY FOR SEND")
                print("="*70)
                print(email_content)
                print("="*70)
                print("\n📋 Copy the above and paste into Gmail")
                print("   Or use: cat", email_draft)
            
            results["actions_completed"].append("send_email")
        
        elif action == "update_crm":
            if dry_run:
                logger.info("[DRY RUN] Would update CRM with meeting intelligence")
            else:
                logger.info("CRM update not yet implemented")
                results["actions_failed"].append({
                    "action": "update_crm",
                    "reason": "Not implemented yet"
                })
        
        elif action == "schedule_followup":
            if dry_run:
                logger.info("[DRY RUN] Would check for follow-up meeting scheduling")
            else:
                logger.info("Follow-up scheduling not yet implemented")
                results["actions_failed"].append({
                    "action": "schedule_followup",
                    "reason": "Not implemented yet"
                })
        
        else:
            logger.warning(f"Unknown action: {action}")
            results["actions_failed"].append({
                "action": action,
                "reason": "Unknown action type"
            })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="N5 Meeting Approve - Review and trigger downstream actions"
    )
    parser.add_argument(
        "meeting_folder",
        help="Name of the meeting folder in N5/records/meetings/"
    )
    parser.add_argument(
        "--actions",
        nargs="+",
        default=["send_email"],
        choices=["send_email", "update_crm", "schedule_followup", "all"],
        help="Actions to trigger (default: send_email)"
    )
    parser.add_argument(
        "--no-auto-email",
        action="store_true",
        help="Skip automatic email generation for external meetings"
    )
    parser.add_argument(
        "--generate-missing",
        action="store_true",
        help="Auto-generate missing deliverables"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without executing"
    )
    
    args = parser.parse_args()
    
    # Find meeting folder
    meeting_dir = find_meeting_folder(args.meeting_folder)
    
    if not meeting_dir:
        print(f"❌ Meeting not found: {args.meeting_folder}")
        return 1
    
    logger.info(f"Processing meeting: {meeting_dir.name}")
    
    # Check deliverables status
    deliverables_status = check_meeting_deliverables(meeting_dir)
    
    print("\n" + "="*70)
    print(f"MEETING: {meeting_dir.name}")
    print("="*70)
    print("\n📦 Deliverables Status:")
    for deliverable, exists in deliverables_status.items():
        status_icon = "✅" if exists else "❌"
        print(f"  {status_icon} {deliverable}")
    
    # Process actions
    actions = args.actions
    if "all" in actions:
        actions = ["send_email", "update_crm", "schedule_followup"]
    
    print(f"\n🎯 Requested Actions: {', '.join(actions)}")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]")
    
    # Execute
    results = approve_and_process(
        meeting_dir, 
        actions, 
        args.dry_run,
        auto_generate_email=not args.no_auto_email
    )
    
    # Summary
    print("\n" + "="*70)
    print("APPROVAL SUMMARY")
    print("="*70)
    
    # Email generation status
    if results.get("email_generation"):
        email_status = results["email_generation"]["status"]
        if email_status == "success":
            print(f"\n✅ Email Draft Generated")
            for f in results["email_generation"]["output_files"]:
                print(f"   📄 {f}")
        elif email_status == "exists":
            print(f"\n✅ Email Draft Already Exists")
        elif email_status == "skipped":
            print(f"\n⏭️  Email Generation Skipped: {results['email_generation']['reason']}")
        elif email_status == "error":
            print(f"\n❌ Email Generation Failed:")
            for err in results["email_generation"]["errors"]:
                print(f"   {err}")
    
    if results["actions_completed"]:
        print(f"\n✅ Completed: {', '.join(results['actions_completed'])}")
    
    if results["actions_failed"]:
        print(f"\n❌ Failed:")
        for failure in results["actions_failed"]:
            print(f"  - {failure['action']}: {failure['reason']}")
    
    print()
    
    return 0 if not results["actions_failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
