#!/usr/bin/env python3
"""
Unit tests for transcript path resolution.
Tests the fix for [IMPORTED-TO-ZO] prefix handling.
"""

import pytest
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from resolve_transcript_path import resolve_transcript_path


class TestPathResolution:
    """Test path resolution logic."""
    
    def test_resolve_file_without_prefix(self, tmp_path):
        """T1.2: Original path exists without prefix."""
        # Create file without prefix
        test_file = tmp_path / "meeting.transcript.md"
        test_file.write_text("# Meeting Transcript")
        
        # Resolve
        resolved = resolve_transcript_path(str(test_file))
        
        assert resolved is not None
        assert resolved == test_file
        assert resolved.exists()
    
    def test_resolve_file_with_prefix(self, tmp_path):
        """T1.1: Original path doesn't exist, but prefixed version does."""
        # Create file WITH prefix
        prefixed_file = tmp_path / "[IMPORTED-TO-ZO] meeting.transcript.md"
        prefixed_file.write_text("# Meeting Transcript")
        
        # Request has path WITHOUT prefix
        original_path = tmp_path / "meeting.transcript.md"
        
        # Resolve
        resolved = resolve_transcript_path(str(original_path))
        
        assert resolved is not None
        assert resolved == prefixed_file
        assert resolved.exists()
        assert "[IMPORTED-TO-ZO]" in resolved.name
    
    def test_file_not_found_either_version(self, tmp_path):
        """T1.3: Neither version exists."""
        nonexistent = tmp_path / "missing.transcript.md"
        
        resolved = resolve_transcript_path(str(nonexistent))
        
        assert resolved is None
    
    def test_prefers_original_path_if_both_exist(self, tmp_path):
        """Edge case: Both versions exist, prefer original."""
        # Create both versions
        original = tmp_path / "meeting.transcript.md"
        original.write_text("# Original")
        
        prefixed = tmp_path / "[IMPORTED-TO-ZO] meeting.transcript.md"
        prefixed.write_text("# Prefixed")
        
        # Resolve
        resolved = resolve_transcript_path(str(original))
        
        # Should prefer original (non-prefixed) version
        assert resolved == original
        assert resolved.read_text() == "# Original"


class TestCLIInterface:
    """Test command-line interface."""
    
    def test_cli_success(self, tmp_path, capsys):
        """CLI returns resolved path on success."""
        test_file = tmp_path / "test.transcript.md"
        test_file.write_text("content")
        
        # Simulate CLI call
        sys.argv = ["resolve_transcript_path.py", str(test_file)]
        
        try:
            from resolve_transcript_path import main
            main()
        except SystemExit as e:
            assert e.code == 0
        
        captured = capsys.readouterr()
        assert str(test_file) in captured.out
    
    def test_cli_not_found(self, tmp_path, capsys):
        """CLI exits with error code when file not found."""
        nonexistent = tmp_path / "missing.transcript.md"
        
        sys.argv = ["resolve_transcript_path.py", str(nonexistent)]
        
        with pytest.raises(SystemExit) as exc_info:
            from resolve_transcript_path import main
            main()
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.err


class TestRealWorldScenarios:
    """Test actual scenarios from the bug."""
    
    def test_ai_request_scenario(self, tmp_path):
        """
        Simulate actual bug scenario:
        - AI request has path without prefix
        - File was renamed with prefix
        - Resolution should find the prefixed file
        """
        # Simulate the scenario
        inbox = tmp_path / "Inbox"
        inbox.mkdir()
        
        # File exists with prefix (after processing)
        actual_file = inbox / "[IMPORTED-TO-ZO] Daily_team_stand-up-transcript-2025-10-29T14-39-25.191Z.transcript.md"
        actual_file.write_text("# Daily Standup\n\nSpeaker 1: Status update...")
        
        # AI request has path without prefix (before renaming)
        request_path = inbox / "Daily_team_stand-up-transcript-2025-10-29T14-39-25.191Z.transcript.md"
        
        # Resolution should find the prefixed version
        resolved = resolve_transcript_path(str(request_path))
        
        assert resolved is not None
        assert resolved == actual_file
        assert resolved.exists()
        assert "Daily Standup" in resolved.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
