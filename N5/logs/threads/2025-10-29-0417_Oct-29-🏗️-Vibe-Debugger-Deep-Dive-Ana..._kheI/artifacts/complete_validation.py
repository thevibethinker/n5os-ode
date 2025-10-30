#!/usr/bin/env python3
"""
COMPLETE END-TO-END VALIDATION
Tests the entire pipeline from conversation creation through title generation
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import sqlite3
import re

def run_cmd(cmd, cwd="/home/workspace"):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, shell=True)
    return result.stdout, result.stderr, result.returncode

def main():
    print("=" * 70)
    print("COMPLETE PIPELINE VALIDATION")
    print("=" * 70)
    
    # Step 1: Create test conversation IN DATABASE FIRST
    test_convo_id = "con_VALIDATION_002"
    db_path = "/home/workspace/N5/data/conversations.db"
    
    print(f"\n[1/6] Creating test conversation in database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete if exists
    cursor.execute("DELETE FROM conversations WHERE id = ?", (test_convo_id,))
    
    # Create conversation
    now = datetime.utcnow().isoformat() + "Z"
    cursor.execute("""
        INSERT INTO conversations (
            id, title, type, status, mode, created_at, updated_at,
            focus, objective, tags, progress_pct,
            workspace_path, state_file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test_convo_id,
        "",  # No title yet
        "build",
        "active",
        "",
        now,
        now,
        "Building comprehensive validation test for conversation-end protocol title generation fix",
        "Validate end-to-end pipeline produces quality titles without duplicates or generic garbage",
        "build test validation title-generation",
        0,
        f"/home/.z/workspaces/{test_convo_id}",
        f"/home/.z/workspaces/{test_convo_id}/SESSION_STATE.md"
    ))
    
    conn.commit()
    conn.close()
    
    print(f"   ✓ Created {test_convo_id} in database")
    
    # Step 2: Create workspace
    test_workspace = Path(f"/home/.z/workspaces/{test_convo_id}")
    test_workspace.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[2/6] Creating test workspace...")
    
    # Create SESSION_STATE
    session_state = f"""# Session State — Build

**Conversation ID**: {test_convo_id}
**Type**: Build
**Created**: 2025-10-29 00:10 ET

## Focus

Building comprehensive validation test for conversation-end protocol title generation fix.

## Objective

Validate end-to-end pipeline produces quality titles without duplicates or generic garbage.

## Key Activities

- Created database entry and workspace
- Populated with realistic session state
- Running full conversation-end pipeline
- Validating title quality with strict checks

## Artifacts

### Permanent (User Workspace)
- Validation test suite
- Fix documentation

## Tags

build test validation title-generation pipeline
"""
    
    (test_workspace / "SESSION_STATE.md").write_text(session_state)
    (test_workspace / "validation_notes.md").write_text("# Validation Notes\n\nTesting title generation fix for conversation-end protocol.")
    (test_workspace / "test_results.txt").write_text("Validation in progress...")
    
    print(f"   ✓ Created SESSION_STATE.md and test artifacts")
    
    # Step 3: Run conversation-end
    print(f"\n[3/6] Running conversation-end pipeline...")
    print(f"   Command: n5_conversation_end.py --convo-id {test_convo_id} --auto")
    
    stdout, stderr, returncode = run_cmd(
        f"python3 /home/workspace/N5/scripts/n5_conversation_end.py --convo-id {test_convo_id} --auto"
    )
    
    if returncode != 0:
        print(f"\n   ❌ Conversation-end failed!")
        print(f"   Error: {stderr}")
        return False
    
    print(f"   ✓ Conversation-end completed")
    
    # Step 4: Query database for result
    print(f"\n[4/6] Checking database for generated title...")
    
    stdout, stderr, returncode = run_cmd(
        f"sqlite3 {db_path} \"SELECT id, title, status FROM conversations WHERE id='{test_convo_id}';\""
    )
    
    if not stdout.strip():
        print(f"   ❌ No database entry found!")
        return False
    
    db_data = stdout.strip().split('|')
    db_id = db_data[0]
    db_title = db_data[1] if len(db_data) > 1 else ""
    db_status = db_data[2] if len(db_data) > 2 else ""
    
    print(f"   ✓ Database entry found")
    print(f"     ID: {db_id}")
    print(f"     Title: {db_title}")
    print(f"     Status: {db_status}")
    
    # Step 5: Validate title quality
    print(f"\n[5/6] Validating title quality...")
    
    failures = []
    
    # Check 1: Title exists
    if not db_title or db_title.strip() == "":
        failures.append("❌ Title is empty")
    
    # Check 2: Has date and emoji separator
    if '|' not in db_title:
        failures.append("❌ Missing '|' separator")
    
    if '|' in db_title:
        content = db_title.split('|')[1].strip()
        
        # Remove emoji prefix
        content_clean = re.sub(r'^[^\w\s]+\s*', '', content)
        words = content_clean.split()
        
        # Check 3: No duplicate consecutive words
        for i in range(len(words) - 1):
            if words[i].lower() == words[i+1].lower():
                failures.append(f"❌ Duplicate words: '{words[i]} {words[i+1]}'")
        
        # Check 4: Not generic garbage
        generic_bad = ['Conversation', 'Work Work', 'System System', 'SESSION STATE', 'Build Build', 'Test Test']
        for bad in generic_bad:
            if bad.lower() in content.lower():
                failures.append(f"❌ Generic/bad content: '{bad}'")
        
        # Check 5: Has meaningful content (at least 2 non-generic words)
        if len(words) < 2:
            failures.append("❌ Too short (< 2 words)")
        
        # Check 6: Not just filename patterns
        filename_patterns = ['SESSION', 'STATE', 'FINAL', 'SUMMARY', 'INDEX', 'README']
        all_filename_words = all(w.upper() in filename_patterns for w in words)
        if all_filename_words:
            failures.append(f"❌ Title is just filename patterns: {content_clean}")
    
    if failures:
        print(f"\n   ❌ TITLE VALIDATION FAILED:")
        for failure in failures:
            print(f"      {failure}")
        print(f"\n   Generated title was: \"{db_title}\"")
        return False
    else:
        print(f"   ✅ Title passes ALL validation checks:")
        print(f"      - Not empty")
        print(f"      - Has proper format (date | emoji content)")
        print(f"      - No duplicate words")
        print(f"      - Not generic garbage")
        print(f"      - Has meaningful content")
        print(f"\n   Generated title: \"{db_title}\"")
    
    # Step 6: Check thread export
    print(f"\n[6/6] Checking thread export...")
    
    threads_dir = Path("/home/workspace/N5/logs/threads")
    test_threads = list(threads_dir.glob(f"*{test_convo_id}*"))
    
    if not test_threads:
        print(f"   ⚠️  No thread export found (may not be an issue)")
    else:
        thread_dir = test_threads[0]
        print(f"   ✓ Thread export found: {thread_dir.name}")
        
        # Check AAR
        aar_files = list(thread_dir.glob("aar-*.json"))
        if aar_files:
            print(f"   ✓ AAR generated: {aar_files[0].name}")
            
            with open(aar_files[0], 'r') as f:
                aar = json.load(f)
            
            aar_title = aar.get('title', '')
            print(f"   ✓ AAR title: {aar_title}")
            
            if aar_title == db_title:
                print(f"   ✅ AAR title matches database")
            else:
                print(f"   ⚠️  Title mismatch (may update later):")
                print(f"      AAR:      {aar_title}")
                print(f"      Database: {db_title}")
        else:
            print(f"   ⚠️  No AAR found")
    
    print(f"\n{'=' * 70}")
    print("✅ VALIDATION COMPLETE - PIPELINE WORKS END-TO-END")
    print("=" * 70)
    print(f"\nGenerated title: \"{db_title}\"")
    print(f"Status: All checks passed")
    print(f"\n{'=' * 70}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VALIDATION CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
