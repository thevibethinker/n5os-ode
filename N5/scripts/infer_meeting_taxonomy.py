#!/usr/bin/env python3
"""
Infer meeting taxonomy (type + subtype) from B26 metadata.
Only handles NEW format with Stakeholder Classification section.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Tuple, Optional

TAXONOMY_PATH = Path("/home/workspace/N5/schemas/meeting_taxonomy.yaml")

def load_taxonomy() -> Dict:
    """Load meeting taxonomy from schema file."""
    with open(TAXONOMY_PATH) as f:
        return yaml.safe_load(f)

def extract_metadata_from_b26(b26_path: Path) -> Dict:
    """Extract relevant fields from B26 metadata file (NEW FORMAT ONLY)."""
    content = b26_path.read_text()
    
    # Check for new format
    if "Stakeholder Classification" not in content:
        raise ValueError(f"B26 file {b26_path} is old format. Only new format with Stakeholder Classification supported.")
    
    metadata = {
        "title": "",
        "primary_classification": "",
        "secondary_classification": "",
        "crm_tags": [],
        "key_themes": [],
        "full_content": content.lower()
    }
    
    # Extract meeting title/ID
    if match := re.search(r'\*\*Meeting ID:\*\*\s+(.+)', content):
        metadata["title"] = match.group(1).strip()
    
    # Extract stakeholder classification (handles ## or ###, with or without bold)
    stakeholder_section = re.search(r'##+ Stakeholder Classification\s+(.+?)(?:\n##|$)', content, re.DOTALL)
    if stakeholder_section:
        text = stakeholder_section.group(1)
        # Handle both **Primary:** and Primary: formats
        if primary := re.search(r'\*?\*?Primary:\*?\*?\s+(.+?)(?:\n|$)', text):
            metadata["primary_classification"] = primary.group(1).strip()
        if secondary := re.search(r'\*?\*?Secondary:\*?\*?\s+(.+?)(?:\n|$)', text):
            metadata["secondary_classification"] = secondary.group(1).strip()
    
    # Extract CRM tags (handles ## or ###)
    crm_section = re.search(r'##+ CRM Tags\s+(.+?)(?:\n##|$)', content, re.DOTALL)
    if crm_section:
        tags = re.findall(r'\*\*([^*]+)\*\*:', crm_section.group(1))
        metadata["crm_tags"] = [tag.strip() for tag in tags]
    
    # Extract key themes (handles ## or ###)
    themes_section = re.search(r'##+ Key Themes\s+(.+?)(?:\n##|$)', content, re.DOTALL)
    if themes_section:
        themes = re.findall(r'^\d+\.\s+\*\*([^*]+)\*\*', themes_section.group(1), re.MULTILINE)
        metadata["key_themes"] = [theme.strip() for theme in themes]
    
    return metadata

def infer_type(metadata: Dict) -> str:
    """Determine if meeting is internal or external from Stakeholder Classification."""
    
    primary = metadata["primary_classification"].lower()
    secondary = metadata["secondary_classification"].lower()
    title = metadata["title"].lower()
    
    # Strong internal signals
    internal_signals = [
        "internal", "team", "cofounder", "co-founder", 
        "employee", "staff", "careerspan team"
    ]
    
    # Strong external signals
    external_signals = [
        "client", "customer", "prospect", "vendor", "partner",
        "external", "potential", "recruiting", "greenlight", "sales"
    ]
    
    # Check primary classification first (strongest signal)
    for signal in internal_signals:
        if signal in primary:
            return "internal"
    
    for signal in external_signals:
        if signal in primary:
            return "external"
    
    # Check secondary
    for signal in internal_signals:
        if signal in secondary:
            return "internal"
    
    for signal in external_signals:
        if signal in secondary:
            return "external"
    
    # Title-based fallback
    if any(sig in title for sig in ["stand-up", "standup", "daily", "team sync", "war room"]):
        return "internal"
    
    # Default to external if ambiguous
    return "external"

def infer_subtype(meeting_type: str, metadata: Dict, taxonomy: Dict) -> str:
    """Infer meeting subtype based on type and metadata."""
    
    content = metadata["full_content"]
    title = metadata["title"].lower()
    primary = metadata["primary_classification"].lower()
    secondary = metadata["secondary_classification"].lower()
    themes = " ".join(metadata["key_themes"]).lower()
    tags = " ".join(metadata["crm_tags"]).lower()
    
    # Special case: standup detection
    if meeting_type == "internal":
        if any(sig in title for sig in ["stand-up", "standup", "daily"]):
            return "standup"
    
    # Combine all searchable text
    searchable = f"{content} {title} {themes} {tags} {primary} {secondary}"
    
    # Get subtypes for this meeting type
    subtypes = taxonomy[meeting_type]
    
    # Score each subtype by keyword matches
    scores = {}
    for subtype, config in subtypes.items():
        if subtype == "general":
            continue  # Skip general, use as fallback
        
        keywords = config.get("keywords", [])
        score = sum(1 for kw in keywords if kw in searchable)
        
        if score > 0:
            scores[subtype] = score
    
    # Return highest scoring subtype, or general if none match
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    else:
        return "general"

def infer_taxonomy(b26_path: Path) -> Tuple[str, str]:
    """
    Infer meeting taxonomy from B26 metadata.
    
    Args:
        b26_path: Path to B26_metadata.md file
    
    Returns:
        (meeting_type, meeting_subtype) tuple
    """
    taxonomy = load_taxonomy()
    metadata = extract_metadata_from_b26(b26_path)
    
    meeting_type = infer_type(metadata)
    meeting_subtype = infer_subtype(meeting_type, metadata, taxonomy)
    
    return meeting_type, meeting_subtype

def infer_from_folder(folder_path: Path) -> Optional[Tuple[str, str]]:
    """Infer taxonomy from meeting folder (looks for B26 file)."""
    b26_file = folder_path / "B26_metadata.md"
    
    if not b26_file.exists():
        return None
    
    return infer_taxonomy(b26_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 infer_meeting_taxonomy.py <path-to-B26_metadata.md or folder>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_dir():
        result = infer_from_folder(path)
    else:
        result = infer_taxonomy(path)
    
    if result:
        meeting_type, meeting_subtype = result
        print(f"Type: {meeting_type}")
        print(f"Subtype: {meeting_subtype}")
    else:
        print("ERROR: Could not find B26_metadata.md")
        sys.exit(1)
