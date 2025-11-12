#!/usr/bin/env python3
"""
Test suite for context_bundle.py module.

Tests cover:
- Context bundle creation with various parameters
- Saving and loading bundles to/from JSON files
- Error handling for file operations
- Edge cases (empty metadata, None values, special characters)
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path('/home/workspace/N5/scripts')))

from context_bundle import create_context_bundle, save_context_bundle, load_context_bundle


class TestContextBundle(unittest.TestCase):
    """Test cases for context bundle functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parent_id = 'con_test123456789'
        self.instruction = "Test worker instruction for build task"
        self.worker_type = "build"
        self.test_metadata = {
            "priority": "high",
            "estimated_time": "45 minutes",
            "dependencies": ["Worker 1", "Worker 2"]
        }
    
    def test_create_context_bundle_basic(self):
        """Test basic context bundle creation with minimal parameters."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type
        )
        
        self.assertEqual(bundle["parent_id"], self.parent_id)
        self.assertEqual(bundle["instruction"], self.instruction)
        self.assertEqual(bundle["worker_type"], self.worker_type)
        self.assertEqual(bundle["metadata"], {})
    
    def test_create_context_bundle_with_metadata(self):
        """Test context bundle creation with metadata."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type,
            metadata=self.test_metadata
        )
        
        self.assertEqual(bundle["parent_id"], self.parent_id)
        self.assertEqual(bundle["instruction"], self.instruction)
        self.assertEqual(bundle["worker_type"], self.worker_type)
        self.assertEqual(bundle["metadata"], self.test_metadata)
        self.assertEqual(bundle["metadata"]["priority"], "high")
        self.assertEqual(bundle["metadata"]["estimated_time"], "45 minutes")
        self.assertEqual(len(bundle["metadata"]["dependencies"]), 2)
    
    def test_create_context_bundle_empty_metadata(self):
        """Test context bundle with explicitly empty metadata."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type,
            metadata={}
        )
        
        self.assertEqual(bundle["metadata"], {})
        self.assertIsInstance(bundle["metadata"], dict)
    
    def test_create_context_bundle_none_metadata(self):
        """Test context bundle with None metadata (should default to empty dict)."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type,
            metadata=None
        )
        
        self.assertEqual(bundle["metadata"], {})
        self.assertIsInstance(bundle["metadata"], dict)
    
    def test_create_context_bundle_special_characters(self):
        """Test context bundle with special characters in instruction."""
        special_instruction = "Test instruction with 'quotes', \"double quotes\", and unicode: ñ, é, 中文"
        
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=special_instruction,
            worker_type=self.worker_type
        )
        
        self.assertEqual(bundle["instruction"], special_instruction)
        self.assertIn("'quotes'", bundle["instruction"])
        self.assertIn('"double quotes"', bundle["instruction"])
        self.assertIn("ñ", bundle["instruction"])
    
    def test_create_context_bundle_all_worker_types(self):
        """Test context bundle creation with different worker types."""
        worker_types = ["build", "research", "analysis", "general"]
        
        for wtype in worker_types:
            bundle = create_context_bundle(
                parent_id=self.parent_id,
                instruction=self.instruction,
                worker_type=wtype
            )
            self.assertEqual(bundle["worker_type"], wtype)
    
    def test_save_context_bundle_success(self):
        """Test saving a context bundle to a file."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type,
            metadata=self.test_metadata
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save bundle
            save_context_bundle(bundle, tmp_path)
            
            # Verify file exists and has content
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 0)
            
            # Load and verify content
            with open(tmp_path, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data["parent_id"], self.parent_id)
            self.assertEqual(saved_data["instruction"], self.instruction)
            self.assertEqual(saved_data["worker_type"], self.worker_type)
            self.assertEqual(saved_data["metadata"], self.test_metadata)
        
        finally:
            # Clean up
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_save_context_bundle_minimal(self):
        """Test saving a minimal context bundle (no metadata)."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            save_context_bundle(bundle, tmp_path)
            
            with open(tmp_path, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data["metadata"], {})
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_load_context_bundle_success(self):
        """Test loading a context bundle from a file."""
        # Create and save a bundle
        original_bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type,
            metadata=self.test_metadata
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save and then load
            save_context_bundle(original_bundle, tmp_path)
            loaded_bundle = load_context_bundle(tmp_path)
            
            # Verify loaded data matches original
            self.assertEqual(loaded_bundle["parent_id"], original_bundle["parent_id"])
            self.assertEqual(loaded_bundle["instruction"], original_bundle["instruction"])
            self.assertEqual(loaded_bundle["worker_type"], original_bundle["worker_type"])
            self.assertEqual(loaded_bundle["metadata"], original_bundle["metadata"])
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_load_context_bundle_nonexistent_file(self):
        """Test loading from a non-existent file raises appropriate error."""
        nonexistent_path = Path("/tmp/this_file_definitely_does_not_exist_12345.json")
        
        with self.assertRaises(FileNotFoundError):
            load_context_bundle(nonexistent_path)
    
    def test_load_context_bundle_invalid_json(self):
        """Test loading invalid JSON raises appropriate error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write("{invalid json content}")
        
        try:
            with self.assertRaises(json.JSONDecodeError):
                load_context_bundle(tmp_path)
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_round_trip_bundle_persistence(self):
        """Test that saving and loading preserves all data."""
        original_bundle = create_context_bundle(
            parent_id="con_roundtrip_test_987654321",
            instruction="Complex instruction with newlines and tabs",
            worker_type="research",
            metadata={
                "complex": {
                    "nested": {
                        "data": [1, 2, 3, {"key": "value"}]
                    }
                },
                "unicode": "Testing ñ, é, 中文, and emojis 🎉"
            }
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Round trip: save then load
            save_context_bundle(original_bundle, tmp_path)
            loaded_bundle = load_context_bundle(tmp_path)
            
            # Deep comparison
            self.assertEqual(loaded_bundle, original_bundle)
            self.assertEqual(loaded_bundle["metadata"]["complex"]["nested"]["data"][3]["key"], "value")
            self.assertIn("🎉", loaded_bundle["metadata"]["unicode"])
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_save_context_bundle_file_permissions(self):
        """Test that saved files have appropriate permissions."""
        bundle = create_context_bundle(
            parent_id=self.parent_id,
            instruction=self.instruction,
            worker_type=self.worker_type
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            save_context_bundle(bundle, tmp_path)
            
            # Check file is readable
            self.assertTrue(os.access(tmp_path, os.R_OK))
            
            # Verify we can read it back
            loaded = load_context_bundle(tmp_path)
            self.assertEqual(loaded["parent_id"], self.parent_id)
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_load_context_bundle_extra_fields(self):
        """Test loading a bundle with extra/unknown fields (forward compatibility)."""
        bundle_data = {
            "parent_id": self.parent_id,
            "instruction": self.instruction,
            "worker_type": self.worker_type,
            "metadata": {},
            "extra_field": "this should be preserved",
            "another_extra": {"nested": "data"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            json.dump(bundle_data, tmp_file)
        
        try:
            loaded = load_context_bundle(tmp_path)
            
            # Core fields should match
            self.assertEqual(loaded["parent_id"], self.parent_id)
            self.assertEqual(loaded["instruction"], self.instruction)
            
            # Extra fields should be preserved (forward compatibility)
            self.assertEqual(loaded.get("extra_field"), "this should be preserved")
            self.assertEqual(loaded.get("another_extra"), {"nested": "data"})
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == '__main__':
    unittest.main()



