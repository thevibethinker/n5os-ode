#!/usr/bin/env python3
"""
N5 OS Safety Layer Tests

Tests for permissions, approvals, and dry-run functionality.
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse

# Add the scripts directory to the path so we can import n5_safety
sys.path.insert(0, str(Path(__file__).parent))

from n5_safety import (
    check_permissions,
    is_dry_run,
    execute_with_safety,
    load_command_spec,
    send_email_approval_request
)

class TestSafetyLayer(unittest.TestCase):
    """Test cases for the N5 safety layer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_command_spec = {
            "name": "test-command",
            "permissions_required": ["email_approval"],
            "flags": {"dry_run": False}
        }

    def test_load_command_spec(self):
        """Test loading command specifications."""
        spec = load_command_spec("lists-promote")
        self.assertIsNotNone(spec)
        self.assertEqual(spec["name"], "lists-promote")
        self.assertIn("email_approval", spec.get("permissions_required", []))

    def test_dry_run_detection_explicit(self):
        """Test explicit dry-run flag detection."""
        args = argparse.Namespace()
        args.dry_run = True

        result = is_dry_run(args, self.test_command_spec)
        self.assertTrue(result)

    def test_dry_run_detection_environment(self):
        """Test environment-based dry-run detection."""
        args = argparse.Namespace()
        args.dry_run = False

        # Set environment variable
        original_env = os.environ.get('N5_DRY_RUN')
        os.environ['N5_DRY_RUN'] = 'true'

        try:
            result = is_dry_run(args, self.test_command_spec)
            self.assertTrue(result)
        finally:
            # Restore environment
            if original_env is not None:
                os.environ['N5_DRY_RUN'] = original_env
            else:
                os.environ.pop('N5_DRY_RUN', None)

    def test_dry_run_detection_none(self):
        """Test no dry-run detection."""
        args = argparse.Namespace()
        args.dry_run = False

        result = is_dry_run(args, self.test_command_spec)
        self.assertFalse(result)

    @patch('n5_safety.send_email_approval_request')
    def test_permission_check_approved(self, mock_send_email):
        """Test permission check with approval."""
        mock_send_email.return_value = True

        args = argparse.Namespace()
        result = check_permissions(self.test_command_spec, args)

        self.assertTrue(result)
        mock_send_email.assert_called_once()

    @patch('n5_safety.send_email_approval_request')
    def test_permission_check_denied(self, mock_send_email):
        """Test permission check with denial."""
        mock_send_email.return_value = False

        args = argparse.Namespace()
        result = check_permissions(self.test_command_spec, args)

        self.assertFalse(result)
        mock_send_email.assert_called_once()

    def test_permission_check_no_permissions(self):
        """Test permission check with no required permissions."""
        spec_no_perms = {
            "name": "test-command",
            "permissions_required": []
        }

        args = argparse.Namespace()
        result = check_permissions(spec_no_perms, args)

        self.assertTrue(result)

    @patch('n5_safety.send_email_approval_request')
    @patch('n5_safety.check_permissions')
    @patch('n5_safety.is_dry_run')
    def test_execute_with_safety_dry_run(self, mock_is_dry_run, mock_check_perms, mock_send_email):
        """Test execution with safety in dry-run mode."""
        mock_check_perms.return_value = True
        mock_is_dry_run.return_value = True
        mock_send_email.return_value = True

        args = argparse.Namespace()
        args.dry_run = True

        def dummy_execute(args):
            return "executed"

        result = execute_with_safety(self.test_command_spec, args, dummy_execute)

        self.assertEqual(result, "executed")
        mock_check_perms.assert_called_once()
        mock_is_dry_run.assert_called_once()

    @patch('n5_safety.send_email_approval_request')
    @patch('n5_safety.check_permissions')
    def test_execute_with_safety_permission_denied(self, mock_check_perms, mock_send_email):
        """Test execution with safety when permissions are denied."""
        mock_check_perms.return_value = False
        mock_send_email.return_value = False

        args = argparse.Namespace()

        def dummy_execute(args):
            return "executed"

        result = execute_with_safety(self.test_command_spec, args, dummy_execute)

        self.assertIsNone(result)
        mock_check_perms.assert_called_once()

    @patch('builtins.input', return_value='y')
    def test_send_email_approval_request_approved(self, mock_input):
        """Test email approval request with user approval."""
        details = {"command": "test", "args": {}}
        result = send_email_approval_request("test-command", details)

        self.assertTrue(result)
        mock_input.assert_called_once_with("✅ Approve this action? (y/N): ")

    @patch('builtins.input', return_value='n')
    def test_send_email_approval_request_denied(self, mock_input):
        """Test email approval request with user denial."""
        details = {"command": "test", "args": {}}
        result = send_email_approval_request("test-command", details)

        self.assertFalse(result)
        mock_input.assert_called_once_with("✅ Approve this action? (y/N): ")

class TestIntegration(unittest.TestCase):
    """Integration tests for safety layer."""

    def test_safety_script_execution(self):
        """Test running the safety script directly."""
        # This test would run the n5_safety.py script with test flag
        # For now, we'll mock the execution
        pass

def run_safety_tests():
    """Run all safety layer tests."""
    print("🧪 Running N5 Safety Layer Tests...")

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSafetyLayer)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("✅ All safety tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == "__main__":
    success = run_safety_tests()
    sys.exit(0 if success else 1)