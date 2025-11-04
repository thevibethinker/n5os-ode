#!/usr/bin/env python3
"""
Comprehensive unit tests for Agentic Reliability System.
Tests Phases 1, 2, 3 components.
"""

import sys
import subprocess
from pathlib import Path
import tempfile
import json

# Test counters
tests_run = 0
tests_passed = 0
tests_failed = 0

def test(name):
    """Decorator to track test execution"""
    def decorator(func):
        def wrapper():
            global tests_run, tests_passed, tests_failed
            tests_run += 1
            try:
                func()
                tests_passed += 1
                print(f"✓ {name}")
                return True
            except AssertionError as e:
                tests_failed += 1
                print(f"✗ {name}: {e}")
                return False
            except Exception as e:
                tests_failed += 1
                print(f"✗ {name}: Unexpected error - {e}")
                return False
        return wrapper
    return decorator

## PHASE 1 TESTS: Critical Rule Reminder System

@test("Critical reminders file exists and is readable")
def test_reminders_file_exists():
    reminders_file = Path("/home/workspace/N5/prefs/system/critical_reminders.txt")
    assert reminders_file.exists(), "critical_reminders.txt not found"
    content = reminders_file.read_text()
    assert len(content) > 500, "File suspiciously short"
    assert "CRITICAL BEHAVIORAL REMINDERS" in content, "Missing header"

@test("Critical reminders contain all 5 required rules")
def test_reminders_content():
    reminders_file = Path("/home/workspace/N5/prefs/system/critical_reminders.txt")
    content = reminders_file.read_text()
    
    required = [
        "COMPLETE BEFORE CLAIMING",
        "DILIGENCE",
        "PERSONA RETURN",
        "SAFETY",
        "AMBIGUITY"
    ]
    
    for rule in required:
        assert rule in content, f"Missing rule: {rule}"

@test("inject_reminders.py script is executable")
def test_inject_script_executable():
    script = Path("/home/workspace/N5/scripts/inject_reminders.py")
    assert script.exists(), "inject_reminders.py not found"
    assert script.stat().st_mode & 0o111, "Script not executable"

@test("inject_reminders.py runs without errors (under threshold)")
def test_inject_under_threshold():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/inject_reminders.py",
         "/home/.z/workspaces/con_UggYKLJKXXeCMMeW"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    # Under 8K threshold should return empty
    assert len(result.stdout.strip()) == 0, "Should return empty under threshold"

@test("inject_reminders.py returns reminder text above threshold")
def test_inject_above_threshold():
    # Create temp SESSION_STATE with high token count
    with tempfile.TemporaryDirectory() as tmpdir:
        session_file = Path(tmpdir) / "SESSION_STATE.md"
        session_file.write_text("estimated_tokens: 10000\n")
        
        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/inject_reminders.py", tmpdir],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert len(result.stdout) > 100, "Should return reminder text"
        assert "CRITICAL BEHAVIORAL REMINDERS" in result.stdout

## PHASE 1 TESTS: Work Manifest System

@test("work_manifest.py script is executable")
def test_manifest_script_executable():
    script = Path("/home/workspace/N5/scripts/work_manifest.py")
    assert script.exists(), "work_manifest.py not found"
    assert script.stat().st_mode & 0o111, "Script not executable"

@test("work_manifest.py generates example manifest")
def test_manifest_generation():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/work_manifest.py",
         "/tmp/dummy.md", "--example"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    output = result.stdout
    
    # Check key sections present
    assert "Work Manifest" in output
    assert "Active Work Stream" in output
    assert "Thread Map" in output
    assert "Completion Criteria" in output
    assert "Progress:" in output

@test("work_manifest.py shows correct status symbols")
def test_manifest_status_symbols():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/work_manifest.py",
         "/tmp/dummy.md", "--example"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout
    # Check status symbols
    assert "✓" in output, "Missing COMPLETE symbol"
    assert "→" in output, "Missing IN_PROGRESS symbol"
    assert "○" in output, "Missing PLANNED symbol"

@test("work_manifest.py calculates progress percentage")
def test_manifest_progress_calculation():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/work_manifest.py",
         "/tmp/dummy.md", "--example"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout
    # Should show progress as fraction and percentage
    assert "complete (" in output.lower()
    assert "%" in output

## PHASE 3 TESTS: Confidence Calibration

@test("confidence_framework exists and is valid")
def test_confidence_framework_exists():
    framework_file = Path("/home/workspace/N5/prefs/system/confidence_framework.md")
    assert framework_file.exists(), "confidence_framework.md not found"
    content = framework_file.read_text()
    assert len(content) > 1000, "Framework suspiciously short"

@test("confidence_framework defines all three levels")
def test_confidence_levels():
    framework_file = Path("/home/workspace/N5/prefs/system/confidence_framework.md")
    content = framework_file.read_text()
    
    levels = ["HIGH", "MEDIUM", "LOW"]
    for level in levels:
        assert level in content, f"Missing confidence level: {level}"

## PHASE 3 TESTS: Context Structure

@test("context_structure_optimized.md exists")
def test_context_structure_exists():
    doc_file = Path("/home/workspace/N5/prefs/system/context_structure_optimized.md")
    assert doc_file.exists(), "context_structure_optimized.md not found"
    content = doc_file.read_text()
    assert len(content) > 1000, "Document suspiciously short"

@test("context_structure references research")
def test_context_structure_citations():
    doc_file = Path("/home/workspace/N5/prefs/system/context_structure_optimized.md")
    content = doc_file.read_text()
    
    # Should reference research
    assert "Lost in the Middle" in content or "U-shaped" in content
    assert "20-30%" in content or "20%" in content  # Performance drop stat

## PHASE 3 TESTS: Pre-Flight Check System

@test("pre_flight_check.py script is executable")
def test_preflight_script_executable():
    script = Path("/home/workspace/N5/scripts/pre_flight_check.py")
    assert script.exists(), "pre_flight_check.py not found"
    assert script.stat().st_mode & 0o111, "Script not executable"

@test("pre_flight_check.py catches ambiguous 'delete'")
def test_preflight_delete_ambiguity():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/pre_flight_check.py",
         "delete meetings"],
        capture_output=True,
        text=True
    )
    
    # Should return 1 for clarification needed
    assert result.returncode == 1, "Should flag for clarification"
    assert "AMBIGUITY" in result.stdout or "Ambiguous" in result.stdout
    assert "delete" in result.stdout.lower()

@test("pre_flight_check.py catches destructive operations")
def test_preflight_destructive():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/pre_flight_check.py",
         "delete meetings"],
        capture_output=True,
        text=True
    )
    
    assert "DESTRUCTIVE" in result.stdout or "Destructive" in result.stdout

@test("pre_flight_check.py allows clear operations")
def test_preflight_clear_request():
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/pre_flight_check.py",
         "create a new markdown file"],
        capture_output=True,
        text=True
    )
    
    # Should proceed (exit code 0)
    assert result.returncode == 0, "Should allow clear request"

## PHASE 3 TESTS: System Upgrades Backlog

@test("system_upgrades.md exists")
def test_upgrades_backlog_exists():
    upgrades_file = Path("/home/workspace/N5/lists/system_upgrades.md")
    assert upgrades_file.exists(), "system_upgrades.md not found"
    content = upgrades_file.read_text()
    assert len(content) > 2000, "Backlog suspiciously short"

@test("system_upgrades.md contains future phases")
def test_upgrades_phases():
    upgrades_file = Path("/home/workspace/N5/lists/system_upgrades.md")
    content = upgrades_file.read_text()
    
    # Should have tiers/phases
    assert "Tier" in content or "Phase" in content
    # Should have multiple items
    assert content.count("###") >= 5, "Should have multiple items"

## INTEGRATION TESTS

@test("All phase documentation files exist")
def test_all_docs_exist():
    required_docs = [
        "/home/workspace/PHASE_2_COMPLETE.md",
        "/home/workspace/PHASE_3_COMPLETE.md",
        "/home/workspace/N5/docs/agentic_reliability_system.md"
    ]
    
    for doc in required_docs:
        assert Path(doc).exists(), f"Missing documentation: {doc}"

@test("No placeholder TODOs in implemented code")
def test_no_todos():
    scripts = [
        "/home/workspace/N5/scripts/inject_reminders.py",
        "/home/workspace/N5/scripts/work_manifest.py",
        "/home/workspace/N5/scripts/pre_flight_check.py"
    ]
    
    for script_path in scripts:
        content = Path(script_path).read_text()
        # Check for comment-based placeholders only (not legitimate uses)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for comment-based TODOs
            if '# TODO' in line or '# FIXME' in line or '# STUB' in line:
                assert False, f"Placeholder comment found in {script_path}:{i}"
            if '// TODO' in line or '// FIXME' in line or '// STUB' in line:
                assert False, f"Placeholder comment found in {script_path}:{i}"

def run_all_tests():
    """Execute all tests and report results"""
    print("=" * 60)
    print("AGENTIC RELIABILITY SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 60)
    print()
    
    # Phase 1 tests
    print("PHASE 1: Critical Rule Reminder System")
    print("-" * 60)
    test_reminders_file_exists()
    test_reminders_content()
    test_inject_script_executable()
    test_inject_under_threshold()
    test_inject_above_threshold()
    print()
    
    # Phase 1 tests (continued)
    print("PHASE 1: Work Manifest System")
    print("-" * 60)
    test_manifest_script_executable()
    test_manifest_generation()
    test_manifest_status_symbols()
    test_manifest_progress_calculation()
    print()
    
    # Phase 3 tests
    print("PHASE 3: Confidence Calibration")
    print("-" * 60)
    test_confidence_framework_exists()
    test_confidence_levels()
    print()
    
    print("PHASE 3: Context Structure")
    print("-" * 60)
    test_context_structure_exists()
    test_context_structure_citations()
    print()
    
    print("PHASE 3: Pre-Flight Check System")
    print("-" * 60)
    test_preflight_script_executable()
    test_preflight_delete_ambiguity()
    test_preflight_destructive()
    test_preflight_clear_request()
    print()
    
    print("PHASE 3: System Upgrades Backlog")
    print("-" * 60)
    test_upgrades_backlog_exists()
    test_upgrades_phases()
    print()
    
    # Integration tests
    print("INTEGRATION TESTS")
    print("-" * 60)
    test_all_docs_exist()
    test_no_todos()
    print()
    
    # Summary
    print("=" * 60)
    print(f"TESTS RUN: {tests_run}")
    print(f"PASSED: {tests_passed} ({100*tests_passed//tests_run if tests_run > 0 else 0}%)")
    print(f"FAILED: {tests_failed}")
    print("=" * 60)
    
    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
