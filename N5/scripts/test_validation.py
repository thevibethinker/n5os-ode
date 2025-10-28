#!/usr/bin/env python3
"""
Test suite for validation module.
Creates sample problematic code and validates detection.
"""

import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from validation import Validator


def create_test_project() -> Path:
    """Create temporary project with known issues."""
    tmpdir = Path(tempfile.mkdtemp(prefix="test_validation_"))
    
    # File with stubs
    stub_file = tmpdir / "stub_module.py"
    stub_file.write_text("""
def implemented_function():
    return 42

def stub_function():
    raise NotImplementedError

def another_stub():
    pass
""")
    
    # File with placeholders
    placeholder_file = tmpdir / "placeholder_module.py"
    placeholder_file.write_text("""
def work_in_progress():
    # TODO: implement this later
    pass

def needs_fix():
    # FIXME: this is broken
    return None
""")
    
    # File with broken imports
    broken_import_file = tmpdir / "broken_imports.py"
    broken_import_file.write_text("""
import os
import nonexistent_module
from fake_package import something

def use_imports():
    return os.path.exists('/')
""")
    
    # File with missing contracts
    no_contracts_file = tmpdir / "no_contracts.py"
    no_contracts_file.write_text("""
def public_function(x, y):
    return x + y

def _private_function(x):
    return x * 2
""")
    
    return tmpdir


def main():
    print("Creating test project...")
    project = create_test_project()
    print(f"Test project: {project}")
    
    print("\nRunning validation...")
    validator = Validator(project)
    report = validator.scan_all()
    
    print("\n" + "="*60)
    print(report.summary())
    print("="*60)
    
    # Verify expected issues found
    expected_stubs = 2
    expected_placeholders = 2
    expected_broken_imports = 2
    
    found_stubs = len([i for i in report.issues if i.category == "stub"])
    found_placeholders = len([i for i in report.issues if i.category == "placeholder"])
    found_broken_imports = len([i for i in report.issues if i.category == "broken_import"])
    
    print(f"\n✓ Test Results:")
    print(f"  Stubs: {found_stubs}/{expected_stubs} {'✓' if found_stubs >= expected_stubs else '✗'}")
    print(f"  Placeholders: {found_placeholders}/{expected_placeholders} {'✓' if found_placeholders >= expected_placeholders else '✗'}")
    print(f"  Broken imports: {found_broken_imports}/{expected_broken_imports} {'✓' if found_broken_imports >= expected_broken_imports else '✗'}")
    
    # Cleanup
    import shutil
    shutil.rmtree(project)
    print(f"\n✓ Cleaned up test project")
    
    return 0


if __name__ == "__main__":
    exit(main())
