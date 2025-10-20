#!/usr/bin/env python3
"""
Plaud Meeting Transcript Processor
Checks Gmail for Plaud AutoFlow emails, extracts transcripts, processes meetings.
Designed to run via scheduled task (daily at 9 PM ET).

Usage:
    python3 plaud_meeting_processor.py --dry-run  # Test mode
    python3 plaud_meeting_processor.py            # Production
"""

import argparse
import logging
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
INBOX_TRANSCRIPTS = WORKSPACE / "N5" / "inbox" / "transcripts"
MEETINGS_DIR = WORKSPACE / "N5" / "records" / "meetings"
PROCESSING_LOG = WORKSPACE / "N5" / "logs" / "meeting-processing" / "processed_transcripts.jsonl"


def check_gmail_for_plaud_emails(dry_run: bool = False) -> List[Dict]:
    """
    Check Gmail for unread emails from Plaud with transcripts.
    Returns list of email metadata + transcript content.
    """
    logger.info("Checking Gmail for Plaud AutoFlow emails...")
    
    if dry_run:
        logger.info("[DRY RUN] Would check Gmail via use_app_gmail tool")
        return []
    
    # NOTE: This will be called via Zo's use_app_gmail tool in actual execution
    # For now, returning placeholder
    # Real implementation: call Gmail API to search for:
    # - from:no-reply@plaud.ai OR from:support@plaud.ai
    # - is:unread
    # - subject contains "transcript" or "recording"
    
    return []


def extract_meeting_metadata(email_subject: str, email_body: str, received_date: str) -> Dict:
    """
    Extract meeting metadata from Plaud email.
    
    Args:
        email_subject: Email subject line
        email_body: Full email body (contains transcript)
        received_date: ISO timestamp of email
    
    Returns:
        Dict with meeting_id, meeting_type, transcript, date
    """
    # Parse date from email
    try:
        date_obj = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
        meeting_date = date_obj.strftime("%Y-%m-%d")
    except:
        meeting_date = datetime.now().strftime("%Y-%m-%d")
    
    # Detect meeting type from subject/content
    subject_lower = email_subject.lower()
    body_lower = email_body.lower()
    
    if any(word in subject_lower or word in body_lower[:500] for word in 
           ['internal', 'team', 'standup', 'logan', 'danny', 'rockwell', 'ilsa']):
        meeting_type = "internal"
    else:
        meeting_type = "external"
    
    # Generate meeting ID
    timestamp = datetime.now().strftime("%H%M%S")
    meeting_id = f"{meeting_date}_{meeting_type}-plaud-{timestamp}"
    
    # Extract transcript from email body
    # Plaud typically includes transcript after "Transcript:" or similar marker
    transcript = email_body
    if "Transcript:" in email_body:
        transcript = email_body.split("Transcript:", 1)[1].strip()
    elif "---" in email_body:
        # Sometimes separated by horizontal rule
        parts = email_body.split("---")
        if len(parts) > 1:
            transcript = parts[-1].strip()
    
    return {
        "meeting_id": meeting_id,
        "meeting_type": meeting_type,
        "meeting_date": meeting_date,
        "transcript": transcript,
        "source_email_subject": email_subject,
        "received_at": received_date
    }


def save_transcript_to_inbox(meeting_data: Dict, dry_run: bool = False) -> Path:
    """Save transcript to N5/inbox/transcripts/ for processing."""
    filename = f"{meeting_data['meeting_id']}.txt"
    filepath = INBOX_TRANSCRIPTS / filename
    
    if dry_run:
        logger.info(f"[DRY RUN] Would save transcript to: {filepath}")
        return filepath
    
    INBOX_TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    filepath.write_text(meeting_data['transcript'])
    logger.info(f"✓ Saved transcript: {filepath}")
    
    return filepath


def process_meeting(meeting_data: Dict, dry_run: bool = False) -> Dict:
    """
    Process meeting via meeting-process command.
    Returns processing result metadata.
    """
    logger.info(f"Processing meeting: {meeting_data['meeting_id']}")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would run: meeting-process on {meeting_data['meeting_id']}")
        return {"status": "dry-run", "meeting_id": meeting_data['meeting_id']}
    
    # NOTE: In actual execution, this will call the meeting-process command
    # via Zo's command system or direct Python script invocation
    # For now, return placeholder
    
    return {
        "status": "processed",
        "meeting_id": meeting_data['meeting_id'],
        "meeting_type": meeting_data['meeting_type'],
        "processed_at": datetime.now(timezone.utc).isoformat()
    }


def log_processing(result: Dict, dry_run: bool = False) -> None:
    """Append processing result to log file."""
    if dry_run:
        logger.info(f"[DRY RUN] Would log: {result}")
        return
    
    PROCESSING_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSING_LOG, 'a') as f:
        f.write(json.dumps(result) + '\n')


def main(dry_run: bool = False) -> int:
    """
    Main orchestration function.
    
    Returns:
        0 if successful, 1 if errors occurred
    """
    try:
        logger.info("=== Starting Plaud Meeting Processor ===")
        
        # Step 1: Check Gmail for new Plaud emails
        emails = check_gmail_for_plaud_emails(dry_run)
        
        if not emails:
            logger.info("No new Plaud emails found.")
            return 0
        
        logger.info(f"Found {len(emails)} unread Plaud email(s)")
        
        processed_count = 0
        failed_count = 0
        
        # Step 2: Process each email
        for email in emails:
            try:
                # Extract metadata
                meeting_data = extract_meeting_metadata(
                    email['subject'],
                    email['body'],
                    email['received_date']
                )
                
                # Save transcript
                save_transcript_to_inbox(meeting_data, dry_run)
                
                # Process meeting
                result = process_meeting(meeting_data, dry_run)
                
                # Log result
                log_processing(result, dry_run)
                
                processed_count += 1
                logger.info(f"✓ Processed: {meeting_data['meeting_id']}")
                
            except Exception as e:
                logger.error(f"Failed to process email: {e}", exc_info=True)
                failed_count += 1
        
        # Step 3: Summary
        logger.info(f"\n=== Processing Complete ===")
        logger.info(f"Processed: {processed_count}")
        logger.info(f"Failed: {failed_count}")
        
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Plaud meeting transcripts from Gmail")
    parser.add_argument("--dry-run", action="store_true", help="Test mode - don't actually process")
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
