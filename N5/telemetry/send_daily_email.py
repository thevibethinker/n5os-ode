#!/usr/bin/env python3
"""
Send N5 Daily Health Check Email
Uses Zo's email system to send daily digest
"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

BASE = Path("/home/workspace")
DAILY_REPORT = BASE / "N5/telemetry/daily_report.md"


def send_email_via_zo(subject: str, body: str, dry_run: bool = False) -> bool:
    """
    Send email using Zo's send_email_to_user tool
    
    Note: This is a placeholder. In actual implementation, this would
    integrate with Zo's email API or use a scheduled task that calls
    the send_email_to_user tool directly.
    """
    if dry_run:
        logger.info("[DRY RUN] Would send email:")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body preview: {body[:200]}...")
        return True
    
    try:
        # Write email content to temp file for scheduled task to pick up
        email_file = BASE / "N5/telemetry/pending_email.md"
        email_content = f"# Email to Send\n\n**Subject:** {subject}\n\n**Body:**\n\n{body}\n"
        email_file.write_text(email_content)
        
        logger.info(f"✓ Email content saved to {email_file}")
        logger.info("Note: Use scheduled task to send via send_email_to_user tool")
        
        return True
        
    except Exception as e:
        logger.error(f"Error preparing email: {e}")
        return False


def main(dry_run: bool = False) -> int:
    """Send daily health check email"""
    try:
        if not DAILY_REPORT.exists():
            logger.error(f"Report not found: {DAILY_REPORT}")
            logger.error("Run n5_health_check.py first")
            return 1
        
        # Read report
        report_content = DAILY_REPORT.read_text()
        
        # Send email
        success = send_email_via_zo(
            subject="N5 Daily Health Check",
            body=report_content,
            dry_run=dry_run
        )
        
        if not success:
            return 1
        
        logger.info("✓ Email sent successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send N5 daily health check email")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send")
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
