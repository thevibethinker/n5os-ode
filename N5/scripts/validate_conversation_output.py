#!/usr/bin/env python3
"""
Validation script for conversation-end outputs.
Checks output against template requirements.

Usage:
    python3 validate_conversation_output.py <output_file>
    
Returns:
    Exit 0 if valid
    Exit 1 with error details if invalid
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

def validate_output(output_text: str) -> Tuple[bool, List[str]]:
    """
    Validate output against template requirements.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Required headings
    required_headings = [
        "✅ Conversation Closed Successfully",
        "Summary",
        "Conversation:",
        "Title:",
        "Duration:",
        "Status:",
        "What Was Built / Accomplished",
        "Artifacts Archived",
        "Key Files Created",
        "System Status"
    ]
    
    for heading in required_headings:
        if heading not in output_text:
            errors.append(f"Missing required heading: '{heading}'")
    
    # Check for generic/placeholder titles (CRITICAL)
    title_match = re.search(r'Title:\s*(.+)', output_text)
    if title_match:
        title = title_match.group(1).strip()
        generic_patterns = [
            r'^Conversation\s+\d{4}-\d{2}-\d{2}',
            r'^Discussion Thread',
            r'^Meeting\s+\d{4}',
            r'^con_[A-Za-z0-9]+$',
            r'^Untitled',
            r'^Session',
            r'^\[.*\]$',  # Bracketed placeholder
        ]
        for pattern in generic_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                errors.append(f"Generic/placeholder title detected: '{title}' - must be specific to actual work")
    else:
        errors.append("No title found in output")
    
    # Check for conversation ID format
    if not re.search(r'Conversation:\s*con_[A-Za-z0-9]+', output_text):
        errors.append("Invalid or missing conversation ID format (should be 'con_XXXXX')")
    
    # Check for placeholder/stub filenames (CRITICAL)
    placeholder_patterns = [
        r'\bscript\.py\b',
        r'\bfile\.txt\b',
        r'\bdocument\.md\b',
        r'\bexample\.',
        r'\bsample\.',
        r'\btest\.',
        r'\btemplate\.',
        r'\bdemo\.',
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            errors.append(f"Placeholder filename detected matching pattern: {pattern} - use actual filenames")
    
    # Check for vague quantifiers
    vague_patterns = [
        r'\bseveral files\b',
        r'\bsome scripts\b',
        r'\bmultiple items\b',
        r'\bvarious\b',
        r'\bmany\b',
    ]
    
    for pattern in vague_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            errors.append(f"Vague quantifier detected: {pattern} - be specific with counts and names")
    
    # Check archive path format
    archive_match = re.search(r'📁\s*(.+)', output_text)
    if archive_match:
        archive_path = archive_match.group(1).strip()
        # Should be: Documents/Archive/YYYY-MM-DD_description_con_XXXXX/
        if not re.match(r'Documents/Archive/\d{4}-\d{2}-\d{2}_.+_con_[A-Za-z0-9]+/?', archive_path):
            errors.append(f"Archive path format incorrect: '{archive_path}' - should be Documents/Archive/YYYY-MM-DD_title_con_XXXXX/")
    else:
        errors.append("No archive path found (should start with 📁)")
    
    # Check for actual file references under "Key Files Created"
    key_files_section = re.search(r'Key Files Created(.+?)(?=\n##|\nSystem Status|$)', output_text, re.DOTALL)
    if key_files_section:
        section_text = key_files_section.group(1)
        # Should have at least one bullet with file icon and filename
        if not re.search(r'[📄📊🍳]\s+\S+\.\w+', section_text):
            errors.append("Key Files Created section has no valid file entries (need emoji + filename.ext)")
    
    # Check for completion items with checkmarks
    if output_text.count('✅') < 2:
        errors.append("Need at least 2 checkmark items (✅) showing what was accomplished")
    
    # Check status is valid
    status_match = re.search(r'Status:\s*(.+)', output_text)
    if status_match:
        status = status_match.group(1).strip()
        valid_statuses = ['Completed', 'Partially Complete', 'Blocked', 'Work in Progress', 'Ready for Testing', 'Production Ready']
        if not any(vs.lower() in status.lower() for vs in valid_statuses):
            errors.append(f"Status '{status}' not recognized - use: Completed, Partially Complete, Blocked, etc.")
    
    # Check ends with closure line
    if not output_text.strip().endswith('Conversation record updated and closed.'):
        errors.append("Output must end with: 'Conversation record updated and closed.'")
    
    return len(errors) == 0, errors


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_conversation_output.py <output_file>", file=sys.stderr)
        sys.exit(2)
    
    output_file = Path(sys.argv[1])
    
    if not output_file.exists():
        print(f"Error: File not found: {output_file}", file=sys.stderr)
        sys.exit(2)
    
    with open(output_file, 'r') as f:
        output_text = f.read()
    
    is_valid, errors = validate_output(output_text)
    
    if is_valid:
        print("✅ Output is valid and conforms to template")
        sys.exit(0)
    else:
        print("❌ Output validation failed:\n", file=sys.stderr)
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}", file=sys.stderr)
        print(f"\n{len(errors)} validation errors found.", file=sys.stderr)
        print("\nRegenerate output addressing these specific issues.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
