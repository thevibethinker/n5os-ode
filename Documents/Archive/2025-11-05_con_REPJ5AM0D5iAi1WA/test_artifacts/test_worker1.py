#!/usr/bin/env python3
"""
Unit tests for discover_meeting_blocks() function
WORKER-1: Block Discovery Function
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "/home/workspace/N5/scripts")
from meeting_intelligence_scanner import discover_meeting_blocks


class TestDiscoverMeetingBlocks(unittest.TestCase):
    """Test discover_meeting_blocks() function."""
    
    def setUp(self):
        """Create temporary meeting directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.meeting_dir = Path(self.temp_dir) / "test-meeting-2025-11-04"
        self.meeting_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_valid_processed_file(self):
        """Test with valid .processed file."""
        processed_data = {
            "processed_at": "2025-11-04T15:03:32.016188Z",
            "blocks_generated": [
                "B42_market_intel.md",
                "B41_team_coordination.md",
                "B13_plan_of_action.md",
                "B24_product_ideas.md"
            ],
            "block_count": 4
        }
        
        processed_file = self.meeting_dir / ".processed"
        with processed_file.open("w") as f:
            json.dump(processed_data, f)
        
        result = discover_meeting_blocks(self.meeting_dir)
        
        expected = ["B42", "B41", "B13", "B24"]
        self.assertEqual(result, expected)
    
    def test_missing_processed_file(self):
        """Test when .processed file doesn't exist."""
        result = discover_meeting_blocks(self.meeting_dir)
        self.assertEqual(result, [])
    
    def test_invalid_json(self):
        """Test with malformed JSON."""
        processed_file = self.meeting_dir / ".processed"
        processed_file.write_text("{ invalid json }")
        
        result = discover_meeting_blocks(self.meeting_dir)
        self.assertEqual(result, [])
    
    def test_empty_blocks_list(self):
        """Test with empty blocks_generated array."""
        processed_data = {
            "processed_at": "2025-11-04T15:03:32.016188Z",
            "blocks_generated": [],
            "block_count": 0
        }
        
        processed_file = self.meeting_dir / ".processed"
        with processed_file.open("w") as f:
            json.dump(processed_data, f)
        
        result = discover_meeting_blocks(self.meeting_dir)
        self.assertEqual(result, [])
    
    def test_missing_blocks_generated_key(self):
        """Test when blocks_generated key is missing."""
        processed_data = {
            "processed_at": "2025-11-04T15:03:32.016188Z",
            "block_count": 0
        }
        
        processed_file = self.meeting_dir / ".processed"
        with processed_file.open("w") as f:
            json.dump(processed_data, f)
        
        result = discover_meeting_blocks(self.meeting_dir)
        self.assertEqual(result, [])
    
    def test_non_md_files_filtered(self):
        """Test that non-.md files are handled gracefully."""
        processed_data = {
            "processed_at": "2025-11-04T15:03:32.016188Z",
            "blocks_generated": [
                "B42_market_intel.md",
                "README.txt",
                "B13_plan_of_action.md"
            ],
            "block_count": 3
        }
        
        processed_file = self.meeting_dir / ".processed"
        with processed_file.open("w") as f:
            json.dump(processed_data, f)
        
        result = discover_meeting_blocks(self.meeting_dir)
        
        # Should only extract from .md files
        expected = ["B42", "B13"]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
