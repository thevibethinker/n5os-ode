#!/usr/bin/env python3
"""
Validate B00_ZO_TAKE_HEED.jsonl against schema.

Usage:
    python3 zth_validate_b00.py <path_to_b00.jsonl>
    python3 zth_validate_b00.py --test  # Run built-in tests
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Schema validation rules (simplified, no external deps)
VALID_TASK_TYPES = {"directive", "blurb", "follow_up_email", "warm_intro", "research", "custom"}
VALID_EXECUTION_POLICIES = {"inline", "auto_execute", "queue"}
VALID_STATUSES = {"pending", "applied", "executed", "queued", "failed"}
ID_PATTERN = re.compile(r"^ZTH-\d{3}$")

def validate_entry(entry: dict, line_num: int) -> list[str]:
    """Validate a single B00 entry. Returns list of errors."""
    errors = []
    
    # Required fields
    required = ["id", "timestamp", "raw_cue", "instruction", "task_type", "execution_policy", "scope"]
    for field in required:
        if field not in entry:
            errors.append(f"Line {line_num}: Missing required field '{field}'")
    
    # ID format
    if "id" in entry and not ID_PATTERN.match(entry["id"]):
        errors.append(f"Line {line_num}: Invalid ID format '{entry['id']}' (expected ZTH-NNN)")
    
    # Task type
    if "task_type" in entry and entry["task_type"] not in VALID_TASK_TYPES:
        errors.append(f"Line {line_num}: Invalid task_type '{entry['task_type']}'")
    
    # Execution policy
    if "execution_policy" in entry and entry["execution_policy"] not in VALID_EXECUTION_POLICIES:
        errors.append(f"Line {line_num}: Invalid execution_policy '{entry['execution_policy']}'")
    
    # Scope must be non-empty array
    if "scope" in entry:
        if not isinstance(entry["scope"], list) or len(entry["scope"]) == 0:
            errors.append(f"Line {line_num}: scope must be non-empty array")
    
    # Status if present
    if "status" in entry and entry["status"] not in VALID_STATUSES:
        errors.append(f"Line {line_num}: Invalid status '{entry['status']}'")
    
    # Instruction should be non-trivial
    if "instruction" in entry and len(entry["instruction"]) < 3:
        errors.append(f"Line {line_num}: instruction too short")
    
    return errors


def validate_file(filepath: Path) -> tuple[bool, list[str], list[dict]]:
    """Validate B00 JSONL file. Returns (valid, errors, entries)."""
    errors = []
    entries = []
    
    if not filepath.exists():
        return False, [f"File not found: {filepath}"], []
    
    content = filepath.read_text().strip()
    
    # Empty file or comment-only is valid
    if not content or content.startswith("#"):
        return True, [], []
    
    for line_num, line in enumerate(content.split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        try:
            entry = json.loads(line)
            entries.append(entry)
            errors.extend(validate_entry(entry, line_num))
        except json.JSONDecodeError as e:
            errors.append(f"Line {line_num}: Invalid JSON - {e}")
    
    # Check sequential IDs
    ids = [e.get("id") for e in entries if "id" in e]
    expected_ids = [f"ZTH-{i:03d}" for i in range(1, len(ids) + 1)]
    if ids != expected_ids:
        errors.append(f"IDs not sequential. Got {ids}, expected {expected_ids}")
    
    return len(errors) == 0, errors, entries


def run_tests():
    """Run built-in validation tests."""
    print("Running B00 validation tests...\n")
    
    test_cases = [
        # (name, jsonl_content, expected_valid, expected_error_substring)
        (
            "Valid single directive",
            '{"id":"ZTH-001","timestamp":"mid","raw_cue":"Zo take heed, omit pricing","instruction":"omit pricing","task_type":"directive","execution_policy":"inline","scope":["B01"]}',
            True,
            None
        ),
        (
            "Valid follow-up email",
            '{"id":"ZTH-001","timestamp":"00:45:00","raw_cue":"Zo take heed, prep follow-up","instruction":"prep follow-up email","task_type":"follow_up_email","execution_policy":"auto_execute","scope":["follow_up_email"]}',
            True,
            None
        ),
        (
            "Empty file (no cues)",
            "# No Zo Take Heed cues detected",
            True,
            None
        ),
        (
            "Invalid task type",
            '{"id":"ZTH-001","timestamp":"mid","raw_cue":"test","instruction":"test","task_type":"invalid_type","execution_policy":"inline","scope":["B01"]}',
            False,
            "Invalid task_type"
        ),
        (
            "Missing required field",
            '{"id":"ZTH-001","timestamp":"mid","raw_cue":"test","instruction":"test","task_type":"directive","scope":["B01"]}',
            False,
            "Missing required field"
        ),
        (
            "Invalid ID format",
            '{"id":"ZTH-1","timestamp":"mid","raw_cue":"test","instruction":"test","task_type":"directive","execution_policy":"inline","scope":["B01"]}',
            False,
            "Invalid ID format"
        ),
        (
            "Non-sequential IDs",
            '{"id":"ZTH-001","timestamp":"mid","raw_cue":"test","instruction":"test","task_type":"directive","execution_policy":"inline","scope":["B01"]}\n{"id":"ZTH-003","timestamp":"mid","raw_cue":"test2","instruction":"test2","task_type":"directive","execution_policy":"inline","scope":["B01"]}',
            False,
            "not sequential"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for name, content, expected_valid, expected_error in test_cases:
        # Write temp file
        tmp = Path("/tmp/b00_test.jsonl")
        tmp.write_text(content)
        
        valid, errors, _ = validate_file(tmp)
        
        if valid == expected_valid:
            if expected_error is None or any(expected_error in e for e in errors):
                print(f"  ✓ {name}")
                passed += 1
            else:
                print(f"  ✗ {name}: Expected error containing '{expected_error}', got {errors}")
                failed += 1
        else:
            print(f"  ✗ {name}: Expected valid={expected_valid}, got valid={valid}")
            if errors:
                print(f"    Errors: {errors}")
            failed += 1
    
    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 zth_validate_b00.py <path_to_b00.jsonl>")
        print("       python3 zth_validate_b00.py --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        success = run_tests()
        sys.exit(0 if success else 1)
    
    filepath = Path(sys.argv[1])
    valid, errors, entries = validate_file(filepath)
    
    if valid:
        print(f"✓ Valid B00 file: {len(entries)} entries")
        for entry in entries:
            print(f"  - {entry['id']}: {entry['task_type']} ({entry['execution_policy']})")
    else:
        print(f"✗ Invalid B00 file:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
