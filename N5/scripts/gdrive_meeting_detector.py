#!/usr/bin/env python3
"""
Google Drive Meeting Transcript Detector
Scans Fireflies/Transcripts folder, detects unprocessed transcripts,
and creates processing requests for Zo.

Uses filename prefix [ZO-PROCESSED] to track processed state.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# This script is designed to be called by Zo with Google Drive integration
# It expects Zo to pass in the list of files from Google Drive

def parse_transcript_filename(filename: str) -> dict:
    """Extract meeting info from Fireflies transcript filename."""
    import re
    
    # Remove [ZO-PROCESSED] prefix if present
    clean_name = filename.replace('[ZO-PROCESSED] ', '')
    
    # Pattern: "Name x Name-transcript-2025-09-23T21-04-28.138Z.docx"
    match = re.search(r'(.+?)-transcript-(\\d{4}-\\d{2}-\\d{2})', clean_name)
    
    if match:
        participants = match.group(1).strip()
        date_str = match.group(2)
        
        # Create clean ID
        participants_clean = participants.replace(' x ', '-').replace(' ', '-').lower()
        participants_clean = re.sub(r'[^a-z0-9-]', '', participants_clean)[:50]
        
        meeting_id = f"{date_str}_{participants_clean}"
        
        return {
            "meeting_id": meeting_id,
            "participants": participants,
            "date": date_str,
            "original_filename": filename,
            "is_processed": filename.startswith('[ZO-PROCESSED]')
        }
    
    # Fallback for non-standard names
    return {
        "meeting_id": f"meeting-{clean_name[:40]}",
        "participants": "unknown",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "original_filename": filename,
        "is_processed": filename.startswith('[ZO-PROCESSED]')
    }

def filter_unprocessed(files_list: list) -> list:
    """
    Filter out processed transcripts.
    
    Args:
        files_list: List of dicts with 'name' and 'id' keys from Google Drive
    
    Returns:
        List of unprocessed file dicts with parsed metadata
    """
    unprocessed = []
    
    for file_info in files_list:
        filename = file_info.get('name', '')
        
        # Skip if already processed
        # ALL files in this folder are transcripts, no need for additional filtering
        if filename.startswith('[ZO-PROCESSED]'):
            continue
        
        # Parse and add metadata
        parsed = parse_transcript_filename(filename)
        parsed['gdrive_id'] = file_info.get('id')
        parsed['gdrive_link'] = file_info.get('webViewLink')
        parsed['modified_time'] = file_info.get('modifiedTime')
        
        unprocessed.append(parsed)
    
    return unprocessed

def create_processing_request(meeting_info: dict, output_dir: Path):
    """Create a JSON request file for meeting processing."""
    request_file = output_dir / f"{meeting_info['meeting_id']}_request.json"
    
    request_data = {
        "meeting_id": meeting_info['meeting_id'],
        "participants": meeting_info['participants'],
        "date": meeting_info['date'],
        "gdrive_id": meeting_info['gdrive_id'],
        "gdrive_link": meeting_info.get('gdrive_link'),
        "original_filename": meeting_info['original_filename'],
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    request_file.write_text(json.dumps(request_data, indent=2))
    return request_file

if __name__ == "__main__":
    # For testing
    print("This script is designed to be called by Zo with Google Drive file data.")
    print("Use: command 'meeting-detect' instead")
