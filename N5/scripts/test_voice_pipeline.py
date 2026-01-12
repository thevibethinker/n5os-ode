#!/usr/bin/env python3
"""
Test the Voice Library V2 forward pipeline.

Validates that new meetings will flow correctly through:
1. Meeting Intelligence Generator (generates B35)
2. extract_voice_primitives.py (parses B35)
3. Review queue or direct import
4. retrieve_primitives.py (pulls for generation)

Usage:
  python3 test_voice_pipeline.py
"""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "N5/data/voice_library.db"

def test_database():
    """Test database connectivity and schema."""
    print("=" * 60)
    print("TEST 1: Database Schema")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print("❌ FAIL: Database not found")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    
    required = ['primitives', 'sources']
    missing = [t for t in required if t not in tables]
    
    if missing:
        print(f"❌ FAIL: Missing tables: {missing}")
        return False
    
    # Check primitives count
    cursor.execute("SELECT COUNT(*) FROM primitives WHERE status='approved'")
    count = cursor.fetchone()[0]
    print(f"✅ PASS: Database OK ({count} approved primitives)")
    
    conn.close()
    return True


def test_retrieval():
    """Test primitive retrieval."""
    print("\n" + "=" * 60)
    print("TEST 2: Primitive Retrieval")
    print("=" * 60)
    
    result = subprocess.run(
        ["python3", str(WORKSPACE / "N5/scripts/retrieve_primitives.py"),
         "--topic", "career", "--count", "3", "--no-update", "--json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"❌ FAIL: Retrieval failed\n{result.stderr}")
        return False
    
    try:
        primitives = json.loads(result.stdout)
        if len(primitives) >= 1:
            print(f"✅ PASS: Retrieved {len(primitives)} primitives")
            return True
        else:
            print("❌ FAIL: No primitives retrieved")
            return False
    except json.JSONDecodeError:
        print(f"❌ FAIL: Invalid JSON output")
        return False


def test_extraction_prompt():
    """Test extraction prompt generation."""
    print("\n" + "=" * 60)
    print("TEST 3: Extraction Prompt Generation")
    print("=" * 60)
    
    # Find a recent meeting
    meetings_dir = WORKSPACE / "Personal/Meetings"
    transcript = None
    
    for week in meetings_dir.iterdir():
        if not week.is_dir():
            continue
        for meeting in week.iterdir():
            if not meeting.is_dir():
                continue
            t = meeting / "transcript.md"
            if t.exists():
                transcript = t
                break
        if transcript:
            break
    
    if not transcript:
        print("⚠️ SKIP: No transcripts found for testing")
        return True
    
    result = subprocess.run(
        ["python3", str(WORKSPACE / "N5/scripts/extract_voice_primitives.py"),
         "--transcript", str(transcript), "--dry-run", "--no-score"],
        capture_output=True, text=True
    )
    
    if "B35 EXTRACTION PROMPT GENERATED" in result.stdout:
        print(f"✅ PASS: Extraction prompt generated for {transcript.parent.name}")
        return True
    else:
        print(f"❌ FAIL: Prompt generation failed\n{result.stdout}\n{result.stderr}")
        return False


def test_b35_prompt_exists():
    """Test B35 block prompt exists and is valid."""
    print("\n" + "=" * 60)
    print("TEST 4: B35 Block Prompt")
    print("=" * 60)
    
    b35_path = WORKSPACE / "Prompts/Blocks/Generate_B35.prompt.md"
    
    if not b35_path.exists():
        print("❌ FAIL: B35 prompt not found")
        return False
    
    content = b35_path.read_text()
    
    required_sections = [
        "Extraction Rules",
        "Capture Signal Detection",
        "Domain Tagging",
        "Output Format"
    ]
    
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        print(f"❌ FAIL: B35 missing sections: {missing}")
        return False
    
    print("✅ PASS: B35 prompt valid")
    return True


def test_meeting_generator_wired():
    """Test that B35 is wired into Meeting Intelligence Generator."""
    print("\n" + "=" * 60)
    print("TEST 5: B35 Wired to Meeting Pipeline")
    print("=" * 60)
    
    generator_path = WORKSPACE / "Prompts/Meeting Intelligence Generator.prompt.md"
    
    if not generator_path.exists():
        print("⚠️ SKIP: Meeting Intelligence Generator not found")
        return True
    
    content = generator_path.read_text()
    
    if "B35_LINGUISTIC_PRIMITIVES" in content:
        print("✅ PASS: B35 wired to Meeting Intelligence Generator")
        return True
    else:
        print("❌ FAIL: B35 NOT wired to Meeting Intelligence Generator")
        return False


def test_postcheck():
    """Test voice postcheck flow."""
    print("\n" + "=" * 60)
    print("TEST 6: Post-Check Flow")
    print("=" * 60)
    
    postcheck_path = WORKSPACE / "N5/scripts/voice_postcheck.py"
    
    if not postcheck_path.exists():
        print("❌ FAIL: voice_postcheck.py not found")
        return False
    
    result = subprocess.run(
        ["python3", str(postcheck_path), "--help"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0 and "--threshold" in result.stdout:
        print("✅ PASS: Post-check script functional")
        return True
    else:
        print("❌ FAIL: Post-check script error")
        return False


def test_novelty_prompts():
    """Test novelty injection prompts exist."""
    print("\n" + "=" * 60)
    print("TEST 7: Novelty Injection Prompts")
    print("=" * 60)
    
    novelty_path = WORKSPACE / "N5/prefs/communication/style-guides/novelty-injection-prompts.md"
    
    if not novelty_path.exists():
        print("❌ FAIL: novelty-injection-prompts.md not found")
        return False
    
    content = novelty_path.read_text()
    
    strategies = ["Strategy 1", "Strategy 2", "Strategy 3", "Strategy 4", "Strategy 5"]
    missing = [s for s in strategies if s not in content]
    
    if missing:
        print(f"❌ FAIL: Missing strategies: {missing}")
        return False
    
    print("✅ PASS: All 5 novelty strategies documented")
    return True


def main():
    print("\n" + "=" * 60)
    print("VOICE LIBRARY V2 PIPELINE TEST")
    print("=" * 60)
    
    tests = [
        ("Database", test_database),
        ("Retrieval", test_retrieval),
        ("Extraction Prompt", test_extraction_prompt),
        ("B35 Prompt", test_b35_prompt_exists),
        ("Meeting Pipeline", test_meeting_generator_wired),
        ("Post-Check", test_postcheck),
        ("Novelty Prompts", test_novelty_prompts),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ FAIL: {name} raised exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✅" if p else "❌"
        print(f"  {status} {name}")
    
    print(f"\n  {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Voice Library V2 pipeline is operational!")
        return 0
    else:
        print("\n⚠️ Some tests failed — review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

