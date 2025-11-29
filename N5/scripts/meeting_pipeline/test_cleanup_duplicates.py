#!/usr/bin/env python3
"""
Test Suite for Meeting Folder Duplicate Cleanup

Tests the cleanup_duplicates.py script functionality.
"""

import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Import the module to test
sys.path.insert(0, str(Path(__file__).parent))
from cleanup_duplicates import DuplicateCleanup, verify_state, INBOX


class TestDuplicateDetection(unittest.TestCase):
    """Test duplicate folder detection logic."""
    
    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_inbox = INBOX
        
        # Monkey-patch INBOX for testing
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.test_dir
        
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
        
        # Restore original INBOX
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.original_inbox
    
    def test_identifies_escaped_folders(self):
        """Test that escaped folder format is detected."""
        # Create test folders with literal backslashes in name
        test_folder = self.test_dir / "2025-11-20_meeting_\\[P\\]"
        test_folder.mkdir()
        
        cleanup = DuplicateCleanup(dry_run=True)
        duplicates = cleanup.find_duplicates()
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0][0].name, "2025-11-20_meeting_\\[P\\]")
        self.assertIsNone(duplicates[0][1])
    
    def test_identifies_duplicate_pairs(self):
        """Test that duplicate pairs are correctly matched."""
        # Create both versions
        esc_folder = self.test_dir / "2025-11-20_meeting_\\[P\\]"
        cor_folder = self.test_dir / "2025-11-20_meeting_[P]"
        esc_folder.mkdir()
        cor_folder.mkdir()
        
        cleanup = DuplicateCleanup(dry_run=True)
        duplicates = cleanup.find_duplicates()
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0][0].name, "2025-11-20_meeting_\\[P\\]")
        self.assertEqual(duplicates[0][1].name, "2025-11-20_meeting_[P]")
    
    def test_no_false_positives(self):
        """Test that correct folders are not flagged."""
        # Create only correct format folders
        (self.test_dir / "2025-11-20_meeting_[P]").mkdir()
        (self.test_dir / "2025-11-19_another_[P]").mkdir()
        
        cleanup = DuplicateCleanup(dry_run=True)
        duplicates = cleanup.find_duplicates()
        
        self.assertEqual(len(duplicates), 0)


class TestMergeFunctionality(unittest.TestCase):
    """Test folder merging logic."""
    
    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_inbox = INBOX
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.test_dir
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.original_inbox
    
    def test_merge_without_conflicts(self):
        """Test merging when no file conflicts exist."""
        # Create source and dest folders
        source = self.test_dir / "source"
        dest = self.test_dir / "dest"
        source.mkdir()
        dest.mkdir()
        
        # Add files to source
        (source / "file1.md").write_text("content1")
        (source / "file2.md").write_text("content2")
        
        # Add different file to dest
        (dest / "file3.md").write_text("content3")
        
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.merge_folders(source, dest)
        
        self.assertTrue(result)
        self.assertTrue((dest / "file1.md").exists())
        self.assertTrue((dest / "file2.md").exists())
        self.assertTrue((dest / "file3.md").exists())
    
    def test_merge_detects_conflicts(self):
        """Test that conflicts are detected and merge is blocked."""
        source = self.test_dir / "source"
        dest = self.test_dir / "dest"
        source.mkdir()
        dest.mkdir()
        
        # Add same file to both
        (source / "conflict.md").write_text("source content")
        (dest / "conflict.md").write_text("dest content")
        
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.merge_folders(source, dest)
        
        self.assertFalse(result)
        # Verify dest file is unchanged
        self.assertEqual((dest / "conflict.md").read_text(), "dest content")
    
    def test_dry_run_makes_no_changes(self):
        """Test that dry-run mode doesn't actually move files."""
        source = self.test_dir / "source"
        dest = self.test_dir / "dest"
        source.mkdir()
        dest.mkdir()
        
        (source / "file.md").write_text("content")
        
        cleanup = DuplicateCleanup(dry_run=True)
        cleanup.merge_folders(source, dest)
        
        # File should still be in source
        self.assertTrue((source / "file.md").exists())
        self.assertFalse((dest / "file.md").exists())


class TestRenameFunctionality(unittest.TestCase):
    """Test folder renaming logic."""
    
    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_inbox = INBOX
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.test_dir
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.original_inbox
    
    def test_rename_escaped_to_correct(self):
        """Test renaming escaped format to correct format."""
        old_folder = self.test_dir / "meeting_\\[P\\]"
        old_folder.mkdir()
        
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.rename_folder(old_folder, "meeting_[P]")
        
        self.assertTrue(result)
        self.assertFalse(old_folder.exists())
        self.assertTrue((self.test_dir / "meeting_[P]").exists())
    
    def test_rename_blocked_if_dest_exists(self):
        """Test that rename fails if destination already exists."""
        old_folder = self.test_dir / "meeting_\\[P\\]"
        new_folder = self.test_dir / "meeting_[P]"
        old_folder.mkdir()
        new_folder.mkdir()
        
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.rename_folder(old_folder, "meeting_[P]")
        
        self.assertFalse(result)
        self.assertTrue(old_folder.exists())
    
    def test_rename_dry_run_makes_no_changes(self):
        """Test that dry-run rename doesn't actually rename."""
        old_folder = self.test_dir / "meeting_\\[P\\]"
        old_folder.mkdir()
        
        cleanup = DuplicateCleanup(dry_run=True)
        cleanup.rename_folder(old_folder, "meeting_[P]")
        
        self.assertTrue(old_folder.exists())
        self.assertFalse((self.test_dir / "meeting_[P]").exists())


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_inbox = INBOX
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.test_dir
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
        
        import cleanup_duplicates
        cleanup_duplicates.INBOX = self.original_inbox
    
    def test_complete_duplicate_cleanup(self):
        """Test full cleanup of a duplicate pair."""
        # Create duplicate folders
        esc_folder = self.test_dir / "meeting_\\[P\\]"
        cor_folder = self.test_dir / "meeting_[P]"
        esc_folder.mkdir()
        cor_folder.mkdir()
        
        # Add content to escaped folder
        (esc_folder / "transcript.md").write_text("transcript content")
        (esc_folder / "metadata.json").write_text('{"type": "meeting"}')
        
        # Add different content to correct folder
        (cor_folder / "notes.md").write_text("notes content")
        
        # Run cleanup
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.run()
        
        # Verify results
        self.assertEqual(result["duplicates_found"], 1)
        self.assertEqual(result["duplicates_fixed"], 1)
        self.assertEqual(result["errors"], 0)
        
        # Verify merged folder has all content
        self.assertTrue((cor_folder / "transcript.md").exists())
        self.assertTrue((cor_folder / "metadata.json").exists())
        self.assertTrue((cor_folder / "notes.md").exists())
        
        # Verify escaped folder is gone
        self.assertFalse(esc_folder.exists())
    
    def test_standalone_escaped_folder_rename(self):
        """Test cleanup of standalone escaped folder (no duplicate)."""
        esc_folder = self.test_dir / "meeting_\\[P\\]"
        esc_folder.mkdir()
        (esc_folder / "content.md").write_text("content")
        
        cleanup = DuplicateCleanup(dry_run=False)
        result = cleanup.run()
        
        self.assertEqual(result["duplicates_found"], 1)
        self.assertEqual(result["duplicates_fixed"], 1)
        
        # Verify renamed folder exists with correct format
        cor_folder = self.test_dir / "meeting_[P]"
        self.assertTrue(cor_folder.exists())
        self.assertTrue((cor_folder / "content.md").exists())
        self.assertFalse(esc_folder.exists())


class TestByteLevelVerification(unittest.TestCase):
    """Byte-level validation tests."""
    
    def test_folder_name_has_no_backslashes(self):
        """Verify folder names after cleanup have no backslash bytes."""
        test_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create and rename
            old_folder = test_dir / "meeting_\\[P\\]"
            old_folder.mkdir()
            new_folder = test_dir / "meeting_[P]"
            old_folder.rename(new_folder)
            
            # Check bytes
            name_bytes = new_folder.name.encode()
            self.assertNotIn(b"\\", name_bytes)
            self.assertIn(b"[P]", name_bytes)
            
        finally:
            shutil.rmtree(test_dir)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestMergeFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestRenameFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    suite.addTests(loader.loadTestsFromTestCase(TestByteLevelVerification))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)


