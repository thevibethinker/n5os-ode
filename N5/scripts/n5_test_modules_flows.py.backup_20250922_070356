#!/usr/bin/env python3
"""
N5 OS Modules and Flows Test Suite

Tests for validator functionality:
- Graph validation (cycles, etc.)
- Version compatibility
- Edge cases
"""

import tempfile
import os
from pathlib import Path
from n5_validate_modules_flows import N5Validator

def test_no_cycles():
    """Test cycle detection in flows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        modules_dir = tmpdir / "modules"
        flows_dir = tmpdir / "flows"
        modules_dir.mkdir()
        flows_dir.mkdir()

        # Create a module
        (modules_dir / "test-module.md").write_text("""# Module: test-module

## Version
0.1.0

## Overview
Test module
""")

        # Create a flow with cycle
        (flows_dir / "cycle-flow.md").write_text("""# Flow: cycle-flow

## Version
0.1.0

## Steps
1. **test-module**: Step 1
2. **test-module**: Step 2 (duplicate)
""")

        validator = N5Validator(str(tmpdir))
        success = validator.run_validation()

        assert not success, "Should detect cycle"
        assert any("Cycle detected" in error for error in validator.errors), "Should report cycle error"
        print("✅ Cycle detection test passed")

def test_version_compatibility():
    """Test version compatibility checks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        modules_dir = tmpdir / "modules"
        flows_dir = tmpdir / "flows"
        modules_dir.mkdir()
        flows_dir.mkdir()

        # Create a module with version 1.0.0 (should warn)
        (modules_dir / "stable-module.md").write_text("""# Module: stable-module

## Version
1.0.0

## Overview
Stable module
""")

        # Create a flow using it
        (flows_dir / "version-flow.md").write_text("""# Flow: version-flow

## Version
0.1.0

## Steps
1. **stable-module**: Use stable module
""")

        validator = N5Validator(str(tmpdir))
        success = validator.run_validation()

        assert success, "Should succeed but warn"
        assert any("version 1.0.0 may not be compatible" in warning for warning in validator.warnings), "Should warn about version"
        print("✅ Version compatibility test passed")

def test_unknown_module():
    """Test unknown module reference."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        modules_dir = tmpdir / "modules"
        flows_dir = tmpdir / "flows"
        modules_dir.mkdir()
        flows_dir.mkdir()

        # No modules

        # Create a flow referencing unknown module
        (flows_dir / "unknown-flow.md").write_text("""# Flow: unknown-flow

## Version
0.1.0

## Steps
1. **unknown-module**: Unknown step
""")

        validator = N5Validator(str(tmpdir))
        success = validator.run_validation()

        assert not success, "Should fail with unknown module"
        assert any("unknown module" in error for error in validator.errors), "Should report unknown module"
        print("✅ Unknown module test passed")

def test_atomicity():
    """Test module atomicity check."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        modules_dir = tmpdir / "modules"
        flows_dir = tmpdir / "flows"
        modules_dir.mkdir()
        flows_dir.mkdir()

        # Create a non-atomic module
        (modules_dir / "composite-module.md").write_text("""# Module: composite-module

## Version
0.1.0

## Overview
This module does composite workflow operations.
""")

        validator = N5Validator(str(tmpdir))
        success = validator.run_validation()

        assert success, "Should succeed but warn"
        assert any("may not be atomic" in warning for warning in validator.warnings), "Should warn about atomicity"
        print("✅ Atomicity test passed")

def test_flow_chaining():
    """Test flow chaining validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        modules_dir = tmpdir / "modules"
        flows_dir = tmpdir / "flows"
        modules_dir.mkdir()
        flows_dir.mkdir()

        # Create module
        (modules_dir / "chain-module.md").write_text("""# Module: chain-module

## Version
0.1.0
""")

        # Create a single-step flow
        (flows_dir / "single-flow.md").write_text("""# Flow: single-flow

## Version
0.1.0

## Steps
1. **chain-module**: Only step
""")

        validator = N5Validator(str(tmpdir))
        success = validator.run_validation()

        assert success, "Should succeed but warn"
        assert any("only 1 steps" in warning for warning in validator.warnings), "Should warn about single step"
        print("✅ Flow chaining test passed")

def run_all_tests():
    """Run all test functions."""
    tests = [
        test_no_cycles,
        test_version_compatibility,
        test_unknown_module,
        test_atomicity,
        test_flow_chaining
    ]

    print("Running N5 Modules and Flows Test Suite...")
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            return False

    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)