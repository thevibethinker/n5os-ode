#!/usr/bin/env python3
"""
Infer meeting taxonomy using LLM with regex validation.
Regex validates structure, LLM infers semantics.
"""

import json
import re
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Tuple, Optional

TAXONOMY_PATH = Path("/home/workspace/N5/schemas/meeting_taxonomy.yaml")

def load_taxonomy() -> dict:
    """Load meeting taxonomy from schema file."""
    with open(TAXONOMY_PATH) as f:
        return yaml.safe_load(f)

def validate_b26_structure(b26_path: Path) -> bool:
    """Validate that B26 has required sections (regex validation layer)."""
    content = b26_path.read_text()
    
    required_sections = [
        "Stakeholder Classification",
        "CRM Tags",
        "Key Themes"
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"WARNING: Missing required section: {section}")
            return False
    
    # Validate Stakeholder Classification has Primary field
    if not re.search(r'Primary:', content):
        print("WARNING: Stakeholder Classification missing Primary field")
        return False
    
    return True

def infer_with_llm(b26_path: Path, taxonomy: dict) -> Optional[Tuple[str, str]]:
    """Use LLM to infer taxonomy from B26 metadata."""
    
    b26_content = b26_path.read_text()
    
    # Build JSON schema for structured output
    external_subtypes = list(taxonomy["external"].keys())
    internal_subtypes = list(taxonomy["internal"].keys())
    
    output_schema = {
        "type": "object",
        "properties": {
            "meeting_type": {
                "type": "string",
                "enum": ["internal", "external"]
            },
            "meeting_subtype": {
                "type": "string",
                "description": f"For external: {', '.join(external_subtypes)}. For internal: {', '.join(internal_subtypes)}"
            }
        },
        "required": ["meeting_type", "meeting_subtype"]
    }
    
    prompt = f"""Classify this meeting based on its B26 metadata.

TAXONOMY:
external subtypes: {', '.join(external_subtypes)}
internal subtypes: {', '.join(internal_subtypes)}

METADATA:
{b26_content}

Analyze Stakeholder Classification, CRM Tags, Key Themes to determine meeting_type (internal/external) and meeting_subtype.

Rules:
- "client", "customer", "prospect" in Stakeholder → external
- "internal", "team", "cofounder" → internal
- "stand-up", "daily" meetings → internal/standup
- Sales/demo → external/sales
- Coaching/advisory → external/coaching
- Partnership → external/partnership"""

    try:
        result = subprocess.run(
            ["zo", prompt, "--output-format", json.dumps(output_schema)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Zo CLI error: {result.stderr}")
            return None
        
        # Parse JSON response
        data = json.loads(result.stdout.strip())
        meeting_type = data["meeting_type"]
        meeting_subtype = data["meeting_subtype"]
        
        # Validate against taxonomy
        if meeting_type not in taxonomy:
            print(f"ERROR: Invalid meeting_type: {meeting_type}")
            return None
        
        if meeting_subtype not in taxonomy[meeting_type]:
            print(f"ERROR: Invalid meeting_subtype: {meeting_subtype} for type {meeting_type}")
            return None
        
        return (meeting_type, meeting_subtype)
        
    except subprocess.TimeoutExpired:
        print("ERROR: LLM call timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse LLM response as JSON: {e}")
        print(f"Response was: {result.stdout}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def infer_taxonomy(b26_path: Path) -> Optional[Tuple[str, str]]:
    """
    Infer meeting taxonomy from B26 metadata.
    Regex validates, LLM infers.
    
    Args:
        b26_path: Path to B26_metadata.md file
    
    Returns:
        (meeting_type, meeting_subtype) tuple or None
    """
    taxonomy = load_taxonomy()
    
    # Step 1: Regex validation
    if not validate_b26_structure(b26_path):
        print(f"ERROR: B26 file {b26_path} does not have required structure")
        return None
    
    # Step 2: LLM inference
    return infer_with_llm(b26_path, taxonomy)

def infer_from_folder(folder_path: Path) -> Optional[Tuple[str, str]]:
    """Infer taxonomy from meeting folder (looks for B26 file)."""
    b26_file = folder_path / "B26_metadata.md"
    
    if not b26_file.exists():
        print(f"ERROR: No B26_metadata.md found in {folder_path}")
        return None
    
    return infer_taxonomy(b26_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 infer_meeting_taxonomy_llm.py <path-to-B26_metadata.md or folder>")
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
        sys.exit(0)
    else:
        print("ERROR: Could not infer taxonomy")
        sys.exit(1)
