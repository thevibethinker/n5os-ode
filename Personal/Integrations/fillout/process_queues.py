#!/usr/bin/env python3
"""
Process queued Gmail drafts and SMS notifications from the Marvin pipeline.

This script is meant to be run by a Zo agent/scheduled task that has access
to the Gmail and SMS tools.

It reads from:
- draft_queue.jsonl (Gmail drafts to create)
- sms_queue.jsonl (SMS messages to send)

And outputs instructions for Zo to execute.
"""

import json
from pathlib import Path
from datetime import datetime

QUEUE_DIR = Path("/home/workspace/Personal/Integrations/fillout")
DRAFT_QUEUE = QUEUE_DIR / "draft_queue.jsonl"
SMS_QUEUE = QUEUE_DIR / "sms_queue.jsonl"
PROCESSED_DIR = QUEUE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def process_draft_queue():
    """Read and return pending Gmail drafts."""
    if not DRAFT_QUEUE.exists():
        return []
    
    drafts = []
    with open(DRAFT_QUEUE) as f:
        for line in f:
            if line.strip():
                drafts.append(json.loads(line))
    
    return drafts


def process_sms_queue():
    """Read and return pending SMS messages."""
    if not SMS_QUEUE.exists():
        return []
    
    messages = []
    with open(SMS_QUEUE) as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    
    return messages


def archive_queues():
    """Move processed queues to archive."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if DRAFT_QUEUE.exists():
        archive_path = PROCESSED_DIR / f"draft_queue_{timestamp}.jsonl"
        DRAFT_QUEUE.rename(archive_path)
        print(f"Archived draft queue to {archive_path}")
    
    if SMS_QUEUE.exists():
        archive_path = PROCESSED_DIR / f"sms_queue_{timestamp}.jsonl"
        SMS_QUEUE.rename(archive_path)
        print(f"Archived SMS queue to {archive_path}")


def main():
    """Output pending actions for Zo to execute."""
    drafts = process_draft_queue()
    sms_messages = process_sms_queue()
    
    if not drafts and not sms_messages:
        print("No pending actions in queue.")
        return
    
    output = {
        "pending_drafts": drafts,
        "pending_sms": sms_messages,
        "total_actions": len(drafts) + len(sms_messages)
    }
    
    print(json.dumps(output, indent=2))
    
    # Don't archive yet - let Zo confirm execution first
    # archive_queues()


if __name__ == "__main__":
    main()

