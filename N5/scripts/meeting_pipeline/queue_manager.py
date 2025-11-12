#!/usr/bin/env python3
"""
Queue Manager with Safety Guards
Manages meeting ingestion queue with validation, deduplication, and size limits
"""
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

QUEUE_PATH = Path("/home/workspace/N5/data/meeting_redownload_queue.jsonl")
AUDIT_LOG = Path("/home/workspace/N5/logs/drive_ingestion_audit.jsonl")

# Safety limits
MAX_QUEUE_SIZE = 1000
REQUIRED_FIELDS = ["meeting_id", "drive_file_id", "source"]


def backup_queue():
    """Create timestamped backup of queue"""
    if not QUEUE_PATH.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = QUEUE_PATH.parent / f"meeting_redownload_queue_{timestamp}.jsonl.backup"
    shutil.copy(QUEUE_PATH, backup_path)
    logger.info(f"✓ Queue backed up: {backup_path.name}")
    return backup_path


def load_queue():
    """Load and validate queue"""
    if not QUEUE_PATH.exists():
        return []
    
    with open(QUEUE_PATH) as f:
        entries = [json.loads(line) for line in f if line.strip()]
    
    return entries


def validate_entry(entry):
    """
    Validate queue entry schema
    
    Returns:
        (bool, str): (is_valid, error_message)
    """
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            return (False, f"missing_field_{field}")
    
    # Check meeting_id format
    if not entry["meeting_id"]:
        return (False, "empty_meeting_id")
    
    # Check drive_file_id format
    if not entry["drive_file_id"]:
        return (False, "empty_drive_file_id")
    
    return (True, None)


def add_to_queue(entry, dry_run=False):
    """
    Add entry to queue with safety checks
    
    Args:
        entry: dict with meeting_id, drive_file_id, source
        dry_run: if True, preview without writing
    
    Returns:
        str: status (added|already_queued|queue_full|invalid)
    """
    # Load current queue
    queue = load_queue()
    
    # Check size limit
    if len(queue) >= MAX_QUEUE_SIZE:
        logger.error(f"🚨 Queue full: {len(queue)} entries (limit: {MAX_QUEUE_SIZE})")
        return "queue_full"
    
    # Validate entry
    is_valid, error = validate_entry(entry)
    if not is_valid:
        logger.error(f"Invalid entry: {error}")
        return f"invalid_{error}"
    
    # Check for duplicates
    if entry["meeting_id"] in [e["meeting_id"] for e in queue]:
        logger.info(f"Already queued: {entry['meeting_id']}")
        return "already_queued"
    
    # Preview mode
    if dry_run:
        logger.info(f"[DRY-RUN] Would add to queue: {entry['meeting_id']}")
        return "would_add"
    
    # Backup before modification
    backup_queue()
    
    # Add to queue
    queue.append(entry)
    
    # Write atomically (temp + rename)
    temp_file = QUEUE_PATH.parent / f".{QUEUE_PATH.name}.tmp"
    with open(temp_file, 'w') as f:
        for e in queue:
            f.write(json.dumps(e) + "\n")
    temp_file.rename(QUEUE_PATH)
    
    logger.info(f"✓ Added to queue: {entry['meeting_id']} (queue size: {len(queue)})")
    
    # Audit log
    with open(AUDIT_LOG, 'a') as f:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "queue_add",
            "meeting_id": entry["meeting_id"],
            "queue_size": len(queue)
        }
        f.write(json.dumps(log_entry) + "\n")
    
    return "added"


def clear_queue(dry_run=False):
    """Clear entire queue (with backup)"""
    if not QUEUE_PATH.exists():
        logger.info("Queue already empty")
        return
    
    queue = load_queue()
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would clear {len(queue)} entries")
        return
    
    # Backup
    backup_path = backup_queue()
    logger.info(f"Backup created: {backup_path}")
    
    # Clear
    QUEUE_PATH.unlink()
    logger.info(f"✓ Queue cleared ({len(queue)} entries removed)")


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Queue manager with safety guards")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add entry to queue")
    add_parser.add_argument("--meeting-id", required=True)
    add_parser.add_argument("--drive-file-id", required=True)
    add_parser.add_argument("--source", default="manual")
    
    # List command
    subparsers.add_parser("list", help="List queue entries")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear entire queue")
    
    # Stats command
    subparsers.add_parser("stats", help="Show queue statistics")
    
    args = parser.parse_args()
    
    if args.command == "add":
        entry = {
            "meeting_id": args.meeting_id,
            "drive_file_id": args.drive_file_id,
            "source": args.source
        }
        status = add_to_queue(entry, dry_run=args.dry_run)
        print(f"Status: {status}")
        return 0 if status in ["added", "would_add"] else 1
    
    elif args.command == "list":
        queue = load_queue()
        print(f"Queue size: {len(queue)}")
        for i, entry in enumerate(queue, 1):
            print(f"{i}. {entry['meeting_id']} ({entry['source']})")
        return 0
    
    elif args.command == "clear":
        clear_queue(dry_run=args.dry_run)
        return 0
    
    elif args.command == "stats":
        queue = load_queue()
        sources = {}
        for entry in queue:
            src = entry.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        
        print(f"Total entries: {len(queue)}")
        print(f"Max size: {MAX_QUEUE_SIZE}")
        print(f"Utilization: {len(queue)/MAX_QUEUE_SIZE*100:.1f}%")
        print(f"\nBy source:")
        for src, count in sorted(sources.items()):
            print(f"  {src}: {count}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
