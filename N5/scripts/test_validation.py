#!/usr/bin/env python3
"""
Comprehensive test suite for validation.py
Tests structured parsing, credential scanning, and all validation features.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validation import Validator, ValidationIssue


class TestValidation(unittest.TestCase):
    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_file(self, path: str, content: str):
        """Helper to create test files."""
        file_path = self.test_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def test_stub_detection_not_implemented(self):
        """Test detection of NotImplementedError stubs."""
        content = '''
def process_data():
    raise NotImplementedError("TODO: implement")

class TestClass:
    def method(self):
        raise NotImplementedError
'''
        self.create_file("test_stubs.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        self.assertEqual(len(validator.report.errors), 2)
        self.assertTrue(all(issue.category == "stub" for issue in validator.report.errors))
    
    def test_stub_detection_pass(self):
        """Test detection of pass statement stubs."""
        content = '''
def empty_function():
    pass

def another_empty():
    pass  # This should be flagged
'''
        self.create_file("test_pass.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        self.assertEqual(len(validator.report.errors), 2)
    
    def test_placeholder_detection_todo(self):
        """Test detection of TODO placeholders."""
        content = '''
# TODO: Implement this function
def foo():
    pass

# FIXME: This is broken
def bar():
    pass

# XXX: Review this code
def baz():
    pass
'''
        self.create_file("test_placeholders.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_placeholders()
        
        self.assertEqual(len(validator.report.warnings), 3)
        self.assertTrue(all(issue.category == "placeholder" for issue in validator.report.warnings))
    
    def test_broken_import_resolution(self):
        """Test detection of broken imports."""
        content = '''
import nonexistent_module
from fake_package import something
'''
        self.create_file("test_imports.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_broken_imports()
        
        self.assertEqual(len(validator.report.errors), 2)
        self.assertTrue(all(issue.category == "broken_import" for issue in validator.report.errors))
    
    def test_valid_import_stdlib(self):
        """Test that standard library imports pass."""
        content = '''
import os
import sys
import json
from pathlib import Path
'''
        self.create_file("test_valid_imports.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_broken_imports()
        
        self.assertEqual(len(validator.report.errors), 0)
    
    def test_contract_missing_return_type(self):
        """Test detection of missing return type hints."""
        content = '''
def public_function(x):
    """This is a public function."""
    return x

def _private_function(x):
    return x  # Should not check private functions
'''
        self.create_file("test_contracts.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_contracts()
        
        # Should find one info-level issue for missing return type
        contract_issues = [i for i in validator.report.issues if i.category == "contract"]
        self.assertTrue(any("missing return type hint" in i.message for i in contract_issues))
    
    def test_contract_missing_docstring(self):
        """Test detection of missing docstrings."""
        content = '''
def public_without_docstring(x: int) -> int:
    return x

def _private_without_docstring(x: int) -> int:
    return x  # Should not check private functions
'''
        self.create_file("test_docstrings.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_contracts()
        
        # Should find one info-level issue for missing docstring
        contract_issues = [i for i in validator.report.issues if i.category == "contract"]
        self.assertTrue(any("missing docstring" in i.message for i in contract_issues))
    
    def test_session_state_valid_structure(self):
        """Test validation of well-formed SESSION_STATE.md."""
        content = '''---
conversation_id: con_test12345
type: build
focus: Testing validation
objective: Create comprehensive test suite
mode: implementation
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
---

# SESSION STATE

## Metadata
- Build task

## Progress
- Session initialized

## Artifacts
- None yet

## Covered
- Initial setup
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should have no errors
        errors = [i for i in validator.report.issues if i.category == "session_state" and i.severity == "error"]
        self.assertEqual(len(errors), 0)
    
    def test_session_state_missing_required_fields(self):
        """Test detection of missing required fields in SESSION_STATE.md."""
        content = '''---
conversation_id: con_test12345
type: build
# Missing status and timestamps
---

# SESSION STATE
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect missing required fields
        session_errors = [i for i in validator.report.issues if i.category == "session_state" and i.severity == "error"]
        self.assertTrue(any("Missing required fields" in i.message for i in session_errors))
    
    def test_session_state_invalid_conversation_id(self):
        """Test detection of invalid conversation_id format."""
        content = '''---
conversation_id: invalid_id_without_prefix
type: build
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
---

# SESSION STATE
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect invalid conversation_id
        session_errors = [i for i in validator.report.issues if i.category == "session_state" and "conversation_id" in i.message]
        self.assertGreater(len(session_errors), 0)
    
    def test_session_state_invalid_type(self):
        """Test detection of invalid conversation type."""
        content = '''---
conversation_id: con_test12345
type: invalid_type
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
---

# SESSION STATE
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect unknown conversation type
        session_warnings = [i for i in validator.report.issues if i.category == "session_state" and "Unknown conversation type" in i.message]
        self.assertGreater(len(session_warnings), 0)
    
    def test_session_state_yaml_syntax_error(self):
        """Test detection of YAML syntax errors in SESSION_STATE.md."""
        content = '''---
conversation_id: con_test12345
type: build
status: [unclosed list
created: 2025-11-11T12:00:00+00:00
---

# SESSION STATE
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect YAML parsing error
        session_errors = [i for i in validator.report.issues if i.category == "session_state" and "YAML parsing error" in i.message]
        self.assertGreater(len(session_errors), 0)
    
    def test_session_state_missing_sections(self):
        """Test detection of missing sections in SESSION_STATE.md content."""
        content = '''---
conversation_id: con_test12345
type: build
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
---

# SESSION STATE

## Metadata
Some metadata

## Progress
No progress documented

# Missing Artifacts section
'''
        self.create_file("test_workspace/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect missing Artifacts section
        session_warnings = [i for i in validator.report.issues if i.category == "session_state" and "Missing 'Artifacts'" in i.message]
        self.assertGreater(len(session_warnings), 0)
    
    def test_credential_scanning_api_key(self):
        """Test detection of exposed API keys."""
        content = '''
api_key = "sk_test_1234567890abcdefABCDEF"
x_api_key = "x_api_key_value_12345"
'''
        self.create_file("config.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        # Should detect exposed API keys
        security_errors = [i for i in validator.report.issues if i.category == "security" and "api" in i.message.lower()]
        self.assertGreater(len(security_errors), 0)
    
    def test_credential_scanning_aws_keys(self):
        """Test detection of exposed AWS credentials."""
        content = '''
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
'''
        self.create_file("aws_config.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        # Should detect AWS credentials
        security_errors = [i for i in validator.report.issues if i.category == "security"]
        self.assertGreater(len(security_errors), 0)
    
    def test_credential_scanning_github_token(self):
        """Test detection of exposed GitHub tokens."""
        content = '''
github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
'''
        self.create_file("github.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        # Should detect GitHub token
        security_errors = [i for i in validator.report.issues if i.category == "security"]
        self.assertGreater(len(security_errors), 0)
    
    def test_credential_scanning_database_url(self):
        """Test detection of database URLs with credentials."""
        content = '''
DATABASE_URL = "postgres://user:password@localhost:5432/mydb"
'''
        self.create_file("config.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        # Should detect database URL with credentials
        security_errors = [i for i in validator.report.issues if i.category == "security" and "database" in i.message.lower()]
        self.assertGreater(len(security_errors), 0)
    
    def test_credential_scanning_skips_comments(self):
        """Test that credential scanning skips commented lines."""
        content = '''
# api_key = "should_not_be_flagged"
# This is a comment: password = "secret"
"""
multi-line comment with token = "xyz"
"""
# github_token = "ghp_12345"  # commented out
'''
        self.create_file("comments.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        # Should not flag any credentials in comments
        security_errors = [i for i in validator.report.issues if i.category == "security"]
        self.assertEqual(len(security_errors), 0)
    
    def test_full_scan_integration(self):
        """Test full scan integration."""
        # Create multiple test files
        self.create_file("stub.py", "def foo(): raise NotImplementedError")
        self.create_file("placeholder.py", "# TODO: fix this")
        self.create_file("config.py", 'api_key = "sk_test_secret12345678"')  # At least 15 chars
        
        validator = Validator(self.test_dir)
        validator.scan_all()
        
        # Should find issues across multiple categories
        categories = set(issue.category for issue in validator.report.issues)
        self.assertIn("stub", categories)
        self.assertIn("placeholder", categories)
        self.assertIn("security", categories)
    
    def test_report_summary_format(self):
        """Test that report summary is properly formatted."""
        self.create_file("test.py", "def foo(): pass")
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        summary = validator.report.summary()
        self.assertIn("Validation Report:", summary)
        self.assertIn("Files scanned:", summary)
        self.assertIn("Errors:", summary)
        self.assertIn("Warnings:", summary)
    
    def test_json_output_format(self):
        """Test JSON output format."""
        self.create_file("test.py", "def foo(): pass")
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        # Verify report structure can be JSON serialized
        import json
        data = {
            "project": str(validator.report.project_path),
            "files_scanned": validator.report.files_scanned,
            "errors": len(validator.report.errors),
            "warnings": len(validator.report.warnings),
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "file": str(i.file_path),
                    "line": i.line_number,
                    "message": i.message,
                    "context": i.context
                }
                for i in validator.report.issues
            ]
        }
        
        json_str = json.dumps(data)
        self.assertIsInstance(json_str, str)
    
    def test_stub_detection_ellipsis(self):
        """Test detection of ellipsis (...) stubs."""
        content = '''
def process_data():
    ...

def another_function(x, y):
    ...
'''
        self.create_file("test_ellipsis.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        self.assertEqual(len(validator.report.errors), 2)
        self.assertTrue(all(issue.category == "stub" for issue in validator.report.errors))
    
    def test_jwt_token_detection(self):
        """Test detection of JWT tokens."""
        content = '''
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
'''
        self.create_file("jwt.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        security_errors = [i for i in validator.report.issues if i.category == "security" and "jwt" in i.message.lower()]
        self.assertEqual(len(security_errors), 1)
    
    def test_aws_access_key_detection(self):
        """Test detection of AWS access key IDs."""
        content = '''
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
'''
        self.create_file("aws.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        security_errors = [i for i in validator.report.issues if i.category == "security" and "aws" in i.message.lower()]
        self.assertEqual(len(security_errors), 1)
    
    def test_password_detection(self):
        """Test detection of hardcoded passwords."""
        content = '''
db_password = "my_secret_password_123"
'''
        self.create_file("password.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_credentials()
        
        security_errors = [i for i in validator.report.issues if i.category == "security"]
        self.assertGreater(len(security_errors), 0)
    
    def test_session_state_tags_validation(self):
        """Test validation of tags field in SESSION_STATE.md."""
        # Test with valid tags (list)
        content_valid = '''---
conversation_id: con_test12345
type: build
focus: Testing tags
objective: Validate tags field
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
tags: [build, testing, validation]
---

# SESSION STATE
'''
        self.create_file("test_workspace_valid/SESSION_STATE.md", content_valid)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should have no tag-related errors
        tag_errors = [i for i in validator.report.issues if "tags" in i.message.lower()]
        self.assertEqual(len(tag_errors), 0)
        
        # Test with invalid tags (string instead of list)
        self.create_file("test_workspace_invalid/SESSION_STATE.md", content_valid.replace("tags: [build, testing, validation]", 'tags: "build testing"'))
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should detect invalid tags type
        tag_errors = [i for i in validator.report.issues if "tags should be a list" in i.message]
        self.assertEqual(len(tag_errors), 1)
    
    def test_session_state_yaml_edge_cases(self):
        """Test edge cases in YAML parsing."""
        # Test with nested structure
        content = '''---
conversation_id: con_test12345
type: research
focus: Complex YAML
objective: Test edge cases
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
custom_field:
  nested:
    value: test
    another: 123
---

# SESSION STATE
'''
        self.create_file("test_workspace_complex/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should handle nested structures without errors
        yaml_errors = [i for i in validator.report.issues if "YAML" in i.message]
        self.assertEqual(len(yaml_errors), 0)
    
    def test_ellipsis_stub_with_comment(self):
        """Test detection of ellipsis stubs even with comments."""
        content = '''
def process():
    ...  # Will implement later

def another():
    ...  # TODO
'''
        self.create_file("test_ellipsis_comment.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_stubs()
        
        self.assertEqual(len(validator.report.errors), 2)
    
    def test_mixed_content_validation(self):
        """Test validation with mixed valid and invalid content."""
        # Create a file with both valid and invalid patterns
        content = '''
import os  # Valid
import nonexistent  # Invalid

def good_function():
    return "valid"

def stub_function():
    pass  # Invalid - stub

# TODO: fix this  # Invalid - placeholder
'''
        self.create_file("mixed.py", content)
        
        validator = Validator(self.test_dir)
        validator.scan_all()
        
        categories = set(issue.category for issue in validator.report.issues)
        self.assertIn("stub", categories)
        self.assertIn("broken_import", categories)
        self.assertIn("placeholder", categories)
    
    def test_yaml_parsing_robustness(self):
        """Test YAML parsing handles various data types."""
        content = '''---
conversation_id: con_test12345
type: planning
focus: Data types
objective: Test YAML robustness
status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
bool_field: true
int_field: 42
float_field: 3.14
none_field: null
list_field: [item1, item2, item3]
multiline: |
  This is a
  multiline string
  for testing
---

# SESSION STATE
## Metadata
- Test
'''
        self.create_file("test_workspace_robust/SESSION_STATE.md", content)
        
        validator = Validator(self.test_dir)
        validator.scan_session_state_files()
        
        # Should parse various data types without errors
        yaml_errors = [i for i in validator.report.issues if "YAML" in i.message]
        self.assertEqual(len(yaml_errors), 0)


class TestStructuredVsRegexParsing(unittest.TestCase):
    def test_structured_parsing_advantage(self):
        """Demonstrate that structured parsing catches issues regex misses."""
        # This test shows why structured parsing (YAML + markdown) is better than regex
        
        # Create a malformed SESSION_STATE.md that would fool simple regex
        malformed_content = '''---
conversation_id: con_test12345
type: build
  # Indented field that breaks YAML structure
  status: active
created: 2025-11-11T12:00:00+00:00
last_updated: 2025-11-11T12:30:00+00:00
---

# SESSION STATE
'''
        
        import tempfile
        import shutil
        test_dir = Path(tempfile.mkdtemp())
        try:
            session_file = test_dir / "SESSION_STATE.md"
            session_file.write_text(malformed_content)
            
            validator = Validator(test_dir)
            validator.scan_session_state_files()
            
            # Structured parsing will catch the YAML error
            yaml_errors = [i for i in validator.report.issues 
                          if i.category == "session_state" and "YAML" in i.message]
            self.assertGreater(len(yaml_errors), 0, 
                             "Structured parsing should catch YAML syntax errors that regex would miss")
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredVsRegexParsing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())







