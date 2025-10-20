#!/usr/bin/env python3
"""
Meeting Duplicate Detector
Identifies duplicate transcripts from Fireflies by date + stakeholder matching.

Fireflies sometimes stores multiple versions of the same meeting.
This script prevents reprocessing of duplicates.
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

WORKSPACE = Path("/home/workspace")
PROCESSED_LOG = WORKSPACE / "N5" / "logs" / "meeting-processing" / "processed_transcripts.jsonl"


def extract_meeting_signature(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract date and stakeholder from filename for duplicate detection.
    
    Returns:
        (date, stakeholder) tuple or (None, None) if parsing fails
    
    Examples:
        "Alex x Vrijen - Coaching-transcript-2025-10-09..." -> ("2025-10-09", "alex")
        "Jane and Vrijen - Sales-2025-10-10..." -> ("2025-10-10", "jane")
    """
    # Extract date (YYYY-MM-DD)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    date = date_match.group(1) if date_match else None
    
    # Extract stakeholder (first name before 'x', 'and', or '-')
    stakeholder_patterns = [
        r'^([A-Z][a-z]+)\s+x\s+',      # "Alex x Vrijen"
        r'^([A-Z][a-z]+)\s+and\s+',    # "Alex and Vrijen"
        r'^([A-Z][a-z]+)\s+-\s+',      # "Alex - Meeting"
    ]
    
    stakeholder = None
    for pattern in stakeholder_patterns:
        match = re.search(pattern, filename)
        if match:
            stakeholder = match.group(1).lower()
            break
    
    return (date, stakeholder)


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_processed_signatures() -> Dict[str, Dict]:
    """
    Load signatures of already-processed transcripts.
    
    Returns:
        Dict mapping (date, stakeholder) -> record info
    """
    if not PROCESSED_LOG.exists():
        return {}
    
    signatures = {}
    with open(PROCESSED_LOG, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            
            record = json.loads(line)
            filename = record.get('file_name', '')
            date, stakeholder = extract_meeting_signature(filename)
            
            if date and stakeholder:
                key = f"{date}_{stakeholder}"
                if key not in signatures:
                    signatures[key] = record
    
    return signatures


def is_duplicate(
    filename: str,
    file_id: str,
    processed_signatures: Dict[str, Dict]
) -> Tuple[bool, Optional[str]]:
    """
    Check if a transcript is a duplicate.
    
    Returns:
        (is_duplicate: bool, original_file_id: str or None)
    """
    date, stakeholder = extract_meeting_signature(filename)
    
    if not date or not stakeholder:
        # Can't determine - assume not duplicate
        return (False, None)
    
    key = f"{date}_{stakeholder}"
    
    if key in processed_signatures:
        original_record = processed_signatures[key]
        original_file_id = original_record.get('file_id')
        
        # Don't mark as duplicate if it's the same file
        if original_file_id == file_id:
            return (False, None)
        
        return (True, original_file_id)
    
    return (False, None)


def log_duplicate(
    file_id: str,
    file_name: str,
    duplicate_of: str
):
    """Log a duplicate transcript to the processing log."""
    record = {
        'file_id': file_id,
        'file_name': file_name,
        'status': 'duplicate_skipped',
        'duplicate_of': duplicate_of,
        'discovered_at': datetime.utcnow().isoformat() + 'Z',
        'duplicate_checked': True
    }
    
    with open(PROCESSED_LOG, 'a') as f:
        f.write(json.dumps(record) + '\n')


def main():
    """CLI for duplicate detection."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: meeting_duplicate_detector.py <filename>")
        print("\nChecks if a transcript filename is a duplicate.")
        sys.exit(1)
    
    filename = sys.argv[1]
    processed_signatures = load_processed_signatures()
    
    is_dup, original_id = is_duplicate(filename, "test-id", processed_signatures)
    
    if is_dup:
        print(f"DUPLICATE: {filename}")
        print(f"Original: {original_id}")
        sys.exit(1)
    else:
        print(f"NOT DUPLICATE: {filename}")
        sys.exit(0)


if __name__ == "__main__":
    main()
