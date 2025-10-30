#!/usr/bin/env python3
"""
Zo Feedback Drive Sync - Google Drive Integration

This script is meant to be called BY ZO (not standalone) to handle Drive operations.
Zo will invoke this with proper context to upload files and create docs.

Usage (called by Zo):
    python3 zo_feedback_drive_sync.py upload-file --feedback-id <id> --file-path <path>
    python3 zo_feedback_drive_sync.py create-report --feedback-id <id> --content <markdown>
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

DRIVE_FOLDER_ID = "1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl"


def upload_file_to_drive(feedback_id: str, file_path: Path) -> dict:
    """
    Upload file to Drive. Returns metadata for Zo to process.
    Zo will handle actual Drive API call via use_app_google_drive.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    metadata = {
        "feedback_id": feedback_id,
        "file_name": file_path.name,
        "file_path": str(file_path.absolute()),
        "file_size": file_path.stat().st_size,
        "mime_type": get_mime_type(file_path),
        "target_folder_id": DRIVE_FOLDER_ID
    }
    
    # Output JSON for Zo to consume
    print(json.dumps(metadata, indent=2))
    return metadata


def create_report_doc(feedback_id: str, content_file: Path) -> dict:
    """
    Prepare doc creation request. Returns metadata for Zo to process.
    Zo will handle actual Drive API call via use_app_google_drive.
    """
    if not content_file.exists():
        raise FileNotFoundError(f"Content file not found: {content_file}")
    
    content = content_file.read_text()
    
    # Extract title from first line
    title = content.split('\n')[0].replace('# ', '').strip()
    
    metadata = {
        "feedback_id": feedback_id,
        "title": f"[Zo Feedback] {title}",
        "content": content,
        "target_folder_id": DRIVE_FOLDER_ID
    }
    
    # Output JSON for Zo to consume
    print(json.dumps(metadata, indent=2))
    return metadata


def get_mime_type(file_path: Path) -> str:
    """Determine MIME type from file extension."""
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.json': 'application/json',
    }
    return mime_types.get(file_path.suffix.lower(), 'application/octet-stream')


def main():
    parser = argparse.ArgumentParser(description="Drive sync helper for Zo feedback")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Upload file command
    upload_parser = subparsers.add_parser('upload-file', help='Upload attachment to Drive')
    upload_parser.add_argument('--feedback-id', required=True, help='Feedback ID')
    upload_parser.add_argument('--file-path', required=True, type=Path, help='Path to file')
    
    # Create report command
    report_parser = subparsers.add_parser('create-report', help='Create report doc in Drive')
    report_parser.add_argument('--feedback-id', required=True, help='Feedback ID')
    report_parser.add_argument('--content-file', required=True, type=Path, help='Path to markdown content')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'upload-file':
            upload_file_to_drive(args.feedback_id, args.file_path)
        elif args.command == 'create-report':
            create_report_doc(args.feedback_id, args.content_file)
        
        return 0
        
    except Exception as e:
        logger.error(f"Drive sync failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
