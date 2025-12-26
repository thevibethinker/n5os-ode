#!/usr/bin/env python3
"""
Validate JSONL list files for proper structure and format.
Part of N5OS Lite list maintenance system.

Usage:
    python3 validate_list.py <list_file.jsonl>
    python3 validate_list.py <list_file.jsonl> --fix
    python3 validate_list.py --help

Validates:
- Each line is valid JSON
- Required fields present
- Field types correct
- Dates in ISO format
- Slugs properly formatted
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def validate_json_line(line, line_num):
    """Validate a single JSON line."""
    errors = []
    
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as e:
        return [f"Line {line_num}: Invalid JSON - {e}"]
    
    # Check for required fields (common across lists)
    if 'name' not in obj:
        errors.append(f"Line {line_num}: Missing 'name' field")
    
    # Validate date fields if present
    date_fields = ['created', 'updated', 'date']
    for field in date_fields:
        if field in obj:
            try:
                datetime.fromisoformat(obj[field].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append(f"Line {line_num}: Invalid date format in '{field}'")
    
    # Validate slug if present
    if 'slug' in obj:
        slug = obj['slug']
        if not isinstance(slug, str) or not slug.islower() or ' ' in slug:
            errors.append(f"Line {line_num}: Invalid slug '{slug}' (must be lowercase, no spaces)")
    
    return errors


def validate_list(filepath, fix=False):
    """Validate entire JSONL list file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    print(f"🔍 Validating: {filepath}")
    print()
    
    errors = []
    lines = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            lines.append(line)
            line_errors = validate_json_line(line, line_num)
            errors.extend(line_errors)
    
    # Report results
    if not errors:
        print(f"✅ Valid: {len(lines)} entries, no errors")
        return True
    else:
        print(f"❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"   {error}")
        print()
        
        if fix:
            print("⚠️  Auto-fix not yet implemented. Manual correction required.")
        
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate JSONL list files for proper structure and format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 validate_list.py tools.jsonl
  python3 validate_list.py tools.jsonl --fix
        '''
    )
    parser.add_argument('list_file', help='Path to JSONL list file')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues automatically')
    
    args = parser.parse_args()
    
    valid = validate_list(args.list_file, fix=args.fix)
    sys.exit(0 if valid else 1)


if __name__ == '__main__':
    main()
