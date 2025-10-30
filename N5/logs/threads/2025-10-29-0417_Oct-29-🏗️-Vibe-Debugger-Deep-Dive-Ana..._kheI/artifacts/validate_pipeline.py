#!/usr/bin/env python3
"""
END-TO-END PIPELINE VALIDATION
Creates test conversation, runs conversation-end, validates title quality
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import re

def main():
    print("=" * 70)
    print("END-TO-END PIPELINE VALIDATION")
    print("=" * 70)

    # Step 1: Create test conversation workspace
    test_convo_id = "con_TEST_VALIDATION_001"
    test_workspace = Path(f"/home/.z/workspaces/{test_convo_id}")
    test_workspace.mkdir(parents=True, exist_ok=True)

    print(f"\n✓ Created test workspace: {test_workspace}")

    # Step 2: Create realistic SESSION_STATE.md
    session_state = """# Session State — Build

**Conversation ID**: con_TEST_VALIDATION_001
**Type**: Build
**Created**: 2025-10-29 00:10 ET

## Focus

Building comprehensive test validation for conversation-end title generation pipeline fix.

## Objective

Validate end-to-end that title generator produces specific, meaningful titles when conversation-end protocol executes.

## Key Activities

- Created test conversation workspace
- Populated with session state
- Running full conversation-end pipeline
- Validating title quality

## Artifacts

### Permanent (User Workspace)
- Test validation script
- Documentation of fix

## Tags

build test validation title-generation
"""

    session_file = test_workspace / "SESSION_STATE.md"
    session_file.write_text(session_state)
    print(f"✓ Created SESSION_STATE.md")

    # Step 3: Create some test artifacts
    (test_workspace / "test_notes.md").write_text("# Test Notes\n\nValidation of title generation fix.")
    (test_workspace / "validation_results.txt").write_text("Title generation validation in progress...")
    print(f"✓ Created test artifacts")

    # Step 4: Run conversation-end on test conversation
    print(f"\n{'=' * 70}")
    print("RUNNING CONVERSATION-END PIPELINE")
    print("=" * 70)

    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/n5_conversation_end.py", "--convo-id", test_convo_id, "--auto"],
        capture_output=True,
        text=True,
        cwd="/home/workspace"
    )

    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    # Step 5: Check database
    print(f"\n{'=' * 70}")
    print("VALIDATING DATABASE")
    print("=" * 70)

    db_result = subprocess.run(
        ["sqlite3", "/home/workspace/N5/data/conversations.db", 
         f"SELECT id, title, status FROM conversations WHERE id='{test_convo_id}';"],
        capture_output=True,
        text=True
    )

    if not db_result.stdout:
        print(f"❌ FAIL: No database entry found for {test_convo_id}")
        return False

    db_data = db_result.stdout.strip().split('|')
    db_title = db_data[1] if len(db_data) > 1 else ""

    print(f"✓ Database entry found")
    print(f"  ID: {db_data[0]}")
    print(f"  Title: {db_title}")
    print(f"  Status: {db_data[2] if len(db_data) > 2 else 'unknown'}")

    # Step 6: Validate title quality
    print(f"\n{'=' * 70}")
    print("VALIDATING TITLE QUALITY")
    print("=" * 70)

    failures = []

    # Check 1: Title exists
    if not db_title or db_title == "":
        failures.append("Title is empty")

    # Check 2: No duplicate words
    if '|' in db_title:
        content = db_title.split('|')[1].strip()
        # Remove emoji
        content_clean = re.sub(r'^[^\w\s]+\s*', '', content)
        words = content_clean.split()
        for i in range(len(words) - 1):
            if words[i].lower() == words[i+1].lower():
                failures.append(f"Duplicate words detected: '{words[i]} {words[i+1]}'")

    # Check 3: Not generic
    generic_bad = ['Conversation', 'Work Work', 'System System', 'SESSION STATE', 'Build Build']
    for bad in generic_bad:
        if bad.lower() in db_title.lower():
            failures.append(f"Generic/bad title detected: contains '{bad}'")

    # Check 4: Has meaningful content
    if '|' in db_title:
        content = db_title.split('|')[1].strip()
        content_clean = re.sub(r'^[^\w\s]+\s*', '', content)
        if len(content_clean.split()) < 2:
            failures.append("Title too short, needs at least 2 words")

    if failures:
        print("\n❌ VALIDATION FAILED:")
        for failure in failures:
            print(f"   - {failure}")
        return False
    else:
        print("\n✅ ALL VALIDATION CHECKS PASSED")
        print(f"\n   Generated title: {db_title}")
        print(f"   - No duplicates")
        print(f"   - Not generic")
        print(f"   - Meaningful content")

    # Step 7: Check thread export
    print(f"\n{'=' * 70}")
    print("CHECKING THREAD EXPORT")
    print("=" * 70)

    threads_dir = Path("/home/workspace/N5/logs/threads")
    test_threads = list(threads_dir.glob(f"*{test_convo_id}*"))

    if test_threads:
        print(f"✓ Thread export found: {test_threads[0].name}")
        
        # Check for AAR
        aar_files = list(test_threads[0].glob("aar-*.json"))
        if aar_files:
            print(f"✓ AAR generated: {aar_files[0].name}")
            
            # Load and check AAR title
            with open(aar_files[0], 'r') as f:
                aar = json.load(f)
            
            aar_title = aar.get('title', '')
            print(f"✓ AAR title: {aar_title}")
            
            if aar_title == db_title:
                print(f"✅ AAR title matches database")
            else:
                print(f"⚠️  AAR title differs from database")
                print(f"   AAR:      {aar_title}")
                print(f"   Database: {db_title}")
        else:
            print(f"⚠️  No AAR found in thread export")
    else:
        print(f"⚠️  No thread export found")

    print(f"\n{'=' * 70}")
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print("\n✅ END-TO-END PIPELINE VALIDATED SUCCESSFULLY\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
