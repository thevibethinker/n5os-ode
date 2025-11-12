#!/usr/bin/env python3
"""
Comprehensive test suite for validation.py
Tests structured SESSION_STATE.md parsing, credential scanning, and all validation features.

This test suite provides 15+ comprehensive tests covering:
1. SESSION_STATE.md structured parsing with YAML frontmatter
2. Credential and security scanning
3. Stub and placeholder detection
4. Broken import detection
5. Contract validation
6. Integration with Validator class
"""

import unittest
import tempfile
import json
import shutil # Import shutil for rmtree
from pathlib import Path
import sys
import yaml
import frontmatter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validation import Validator, ValidationReport, ValidationIssue


class TestSessionStateStructuredParsing(unittest.TestCase):
    """Tests for structured YAML parsing of SESSION_STATE.md files."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_session_state_file(self, filename: str, content: str) -> Path:
        file_path = self.test_dir / filename
        file_path.write_text(content)
        return file_path

    def test_valid_session_state(self):
        content = """
---
conversation_id: con_test123
type: build
focus: Test focus
objective: Test objective
---
# SESSION STATE
## Metadata
- **Type:** Build
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertEqual(len(validator.report.errors), 0, "Should not have errors for valid SESSION_STATE.md")
        self.assertEqual(len(validator.report.issues), 0, "Should not have any issues for valid SESSION_STATE.md")

    def test_missing_frontmatter_separator(self):
        content = """
conversation_id: con_test123
type: build
focus: Test focus
objective: Test objective
---
# SESSION STATE
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertTrue(len(validator.report.errors) > 0, "Should have errors for missing frontmatter separator")
        self.assertIn("Missing required field: conversation_id", validator.report.issues[0].message)

    def test_invalid_yaml_frontmatter(self):
        content = """
---
conversation_id: con_test123
type: build:
    - invalid_key
focus: Test focus
objective: Test objective
---
# SESSION STATE
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertTrue(len(validator.report.errors) > 0, "Should have errors for invalid YAML frontmatter")
        self.assertIn("Error parsing SESSION_STATE.md frontmatter:", validator.report.issues[0].message)

    def test_missing_required_frontmatter_fields(self):
        content = """
---
conversation_id: con_test123
focus: Test focus
objective: Test objective
---
# SESSION STATE
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertTrue(len(validator.report.errors) > 0, "Should have errors for missing required fields")
        self.assertIn("Missing required field: type", validator.report.issues[0].message)

    def test_invalid_type_field(self):
        content = """
---
conversation_id: con_test123
focus: Test focus
objective: Test objective
---
# SESSION STATE
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertTrue(len(validator.report.errors) > 0, "Should have errors for missing type field (now required)")
        self.assertIn("Missing required field: type", validator.report.issues[0].message)

    def test_missing_focus_or_objective(self):
        content = """
---
conversation_id: con_test123
type: build
---
# SESSION STATE
"""
        self._create_session_state_file("SESSION_STATE.md", content)
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        self.assertTrue(len(validator.report.errors) > 0, "Should have errors for missing focus/objective (now required)")
        self.assertIn("Missing required field: focus", validator.report.issues[0].message)


class TestCredentialScanning(unittest.TestCase):
    """Tests for credential scanning in various files."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_file(self, filename: str, content: str) -> Path:
        file_path = self.test_dir / filename
        file_path.write_text(content)
        return file_path

    def test_aws_access_key_id(self):
        content = "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE"
        self._create_file("test_credentials.py", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect AWS Access Key ID")
        self.assertIn("Potential aws_key found: hardcoded credential", validator.report.issues[0].message)

    def test_aws_secret_access_key(self):
        content = "AWS_SECRET_ACCESS_KEY = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        self._create_file("test_credentials.py", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect AWS Secret Access Key")
        self.assertIn("Potential aws_secret_key found: hardcoded credential", validator.report.issues[0].message)

    def test_github_token(self):
        content = "GITHUB_TOKEN = ghp_abcdefghijklmnopqrstuvwxyz0123456789ABCDEF"
        self._create_file("test_credentials.py", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect GitHub Token")
        self.assertIn("Potential token found: hardcoded credential", validator.report.issues[0].message)

    def test_generic_api_key(self):
        content = "API_KEY = sk-ABC123DEF456GHI789JKL012MNO345PQR678STU901"
        self._create_file("test_credentials.py", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect generic API key")
        self.assertIn("Potential api_key found: hardcoded credential", validator.report.issues[0].message)

    def test_no_credentials(self):
        content = "This file contains no sensitive information."
        self._create_file("safe_file.txt", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertEqual(len(validator.report.errors), 0, "Should not detect credentials in safe file")
        self.assertEqual(len(validator.report.issues), 0, "Should not have any issues in safe file")

    def test_multiple_credentials_single_file(self):
        content = (
            "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE\n"
            "GITHUB_TOKEN = ghp_abcdefghijklmnopqrstuvwxyz0123456789ABCDEF"
        )
        self._create_file("multiple_creds.py", content)
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect multiple credentials")
        self.assertEqual(len(validator.report.issues), 2, "Should report two issues")

    def test_credentials_in_different_files(self):
        self._create_file("file1.py", "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE")
        self._create_file("file2.txt", "API_KEY = sk-ABC123DEF456GHI789JKL012MNO345PQR678STU901")
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect credentials across files")
        self.assertEqual(len(validator.report.issues), 2, "Should report two issues")


class TestStubAndPlaceholderDetection(unittest.TestCase):
    """Tests for detecting stubs and placeholders."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_file(self, filename: str, content: str) -> Path:
        file_path = self.test_dir / filename
        file_path.write_text(content)
        return file_path

    def test_stub_function(self):
        content = """
def my_stub_function():
    # TODO: Implement this
    pass
"""
        self._create_file("stub_code.py", content)
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        self.assertTrue(len(validator.report.warnings) > 0, "Should detect stub function")
        self.assertIn("Stub implementation detected", validator.report.issues[0].message)

    def test_placeholder_variable(self):
        content = "PLACEHOLDER_VALUE = 'TEMP_VALUE'"
        self._create_file("placeholder_vars.py", content)
        validator = Validator(self.test_dir)
        validator.scan_placeholders()
        self.assertTrue(len(validator.report.warnings) > 0, "Should detect placeholder variable")
        self.assertIn("Placeholder comment found", validator.report.issues[0].message)


class TestBrokenImportDetection(unittest.TestCase):
    """Tests for detecting broken imports."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_file(self, filename: str, content: str) -> Path:
        file_path = self.test_dir / filename
        file_path.write_text(content)
        return file_path

    def test_broken_import(self):
        content = "import non_existent_module"
        self._create_file("broken_imports.py", content)
        validator = Validator(self.test_dir)
        validator.scan_broken_imports()
        self.assertTrue(len(validator.report.errors) > 0, "Should detect broken import")
        self.assertIn("Cannot resolve import: non_existent_module", validator.report.issues[0].message)


class TestContractValidation(unittest.TestCase):
    """Tests for contract validation (e.g., missing docstrings)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_file(self, filename: str, content: str) -> Path:
        file_path = self.test_dir / filename
        file_path.write_text(content)
        return file_path

    def test_missing_docstring(self):
        content = """
def my_function(arg1, arg2):
    pass
"""
        self._create_file("no_docstring.py", content)
        validator = Validator(self.test_dir)
        validator.scan_contracts()
        self.assertTrue(len(validator.report.warnings) > 0, "Should warn for missing docstring")
        self.assertIn("Public function 'my_function' missing docstring", validator.report.issues[0].message)

    def test_valid_docstring(self):
        content = """
def my_function():
    \"\"\"This is a docstring.\"\"\"
    pass
"""
        self._create_file("with_docstring.py", content)
        validator = Validator(self.test_dir)
        validator.scan_contracts()
        self.assertEqual(len(validator.report.warnings), 0, "Should not warn for valid docstring")


def run_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestSessionStateStructuredParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestCredentialScanning))
    suite.addTests(loader.loadTestsFromTestCase(TestStubAndPlaceholderDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestBrokenImportDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestContractValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # This allows running individual tests if needed, but run_tests() is for the full suite
    # unittest.main(verbosity=2)
    exit(run_tests())








