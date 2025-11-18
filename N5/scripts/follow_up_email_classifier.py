#!/usr/bin/env python3
"""
Follow-Up Email Classifier
Purpose: Extract raw meeting data for LLM semantic classification
Division of Labor: Script = mechanics (file loading), LLM = semantics (judgment)

Usage:
    python3 follow_up_email_classifier.py <meeting_folder_path>

Output: JSON with raw meeting data for LLM analysis
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def load_file_content(file_path: Path) -> Optional[str]:
    """Load file content if it exists."""
    if file_path.exists():
        return file_path.read_text()
    return None


def extract_meeting_data(meeting_folder: Path) -> Dict:
    """
    Extract raw meeting data for LLM classification.
    Returns structured data, NOT a decision - LLM makes the judgment.
    """
    
    # Try multiple naming conventions for intelligence blocks
    b26_paths = [
        meeting_folder / "B26_MEETING_METADATA.md",
        meeting_folder / "B26_metadata.md",
        meeting_folder / "B26_MEETING_TOPICS.md"
    ]
    
    b02_paths = [
        meeting_folder / "B02_COMMITMENTS.md",
        meeting_folder / "B02_commitments.md",
        meeting_folder / "B02_DELIVERABLES_COMMITMENTS.md"
    ]
    
    b08_paths = [
        meeting_folder / "B08_FOLLOW_UP_CONVERSATIONS.md",
        meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md",
        meeting_folder / "B08_stakeholder_intelligence.md"
    ]
    
    b01_paths = [
        meeting_folder / "B01_DETAILED_RECAP.md",
        meeting_folder / "B01_detailed_recap.md"
    ]
    
    b25_paths = [
        meeting_folder / "B25_DELIVERABLE_CONTENT_MAP.md",
        meeting_folder / "B25_deliverables.md"
    ]
    
    # Load first existing file for each block
    b26_content = None
    for path in b26_paths:
        b26_content = load_file_content(path)
        if b26_content:
            break
    
    b02_content = None
    for path in b02_paths:
        b02_content = load_file_content(path)
        if b02_content:
            break
    
    b08_content = None
    for path in b08_paths:
        b08_content = load_file_content(path)
        if b08_content:
            break
    
    b01_content = None
    for path in b01_paths:
        b01_content = load_file_content(path)
        if b01_content:
            break
    
    b25_content = None
    for path in b25_paths:
        b25_content = load_file_content(path)
        if b25_content:
            break
    
    # Check if FOLLOW_UP_EMAIL.md already exists
    follow_up_exists = (meeting_folder / "FOLLOW_UP_EMAIL.md").exists()
    
    return {
        "meeting_folder": str(meeting_folder),
        "meeting_name": meeting_folder.name,
        "follow_up_email_exists": follow_up_exists,
        "intelligence_blocks": {
            "b26_metadata": b26_content,
            "b02_commitments": b02_content,
            "b08_stakeholders": b08_content,
            "b01_recap": b01_content,
            "b25_deliverables": b25_content
        },
        "files_present": {
            "b26": b26_content is not None,
            "b02": b02_content is not None,
            "b08": b08_content is not None,
            "b01": b01_content is not None,
            "b25": b25_content is not None
        }
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 follow_up_email_classifier.py <meeting_folder_path>")
        sys.exit(1)
    
    meeting_folder = Path(sys.argv[1])
    
    if not meeting_folder.exists():
        print(json.dumps({"error": "Meeting folder does not exist"}))
        sys.exit(1)
    
    if not meeting_folder.is_dir():
        print(json.dumps({"error": "Path is not a directory"}))
        sys.exit(1)
    
    # Extract raw data (mechanics)
    meeting_data = extract_meeting_data(meeting_folder)
    
    # Output JSON for LLM to judge (semantics)
    print(json.dumps(meeting_data, indent=2))


if __name__ == "__main__":
    main()

