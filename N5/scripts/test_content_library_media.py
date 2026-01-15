#!/usr/bin/env python3
"""
Test Suite for Content Library Media Extension
Validates schema, ingest, and query functionality.

Part of Content Library Media Extension build (Worker 3)

Usage:
    python3 test_content_library_media.py
"""

import json
import os
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


class TestContentLibraryMediaSchema(unittest.TestCase):
    """Test that the media schema columns exist."""
    
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        self.conn.close()
    
    def test_db_exists(self):
        """Database file should exist."""
        self.assertTrue(DB_PATH.exists(), f"Database not found at {DB_PATH}")
    
    def test_items_table_exists(self):
        """Items table should exist."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='items'"
        )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Items table does not exist")
    
    def test_media_columns_exist(self):
        """Media-specific columns should exist in items table."""
        self.cursor.execute("PRAGMA table_info(items)")
        columns = {row[1] for row in self.cursor.fetchall()}
        
        required_columns = {
            "file_path",
            "mime_type", 
            "duration_seconds",
            "dimensions",
            "transcript_path",
            "media_metadata"
        }
        
        for col in required_columns:
            self.assertIn(col, columns, f"Missing column: {col}")


class TestContentLibraryMediaDirectories(unittest.TestCase):
    """Test that media directories exist."""
    
    def test_audio_directory(self):
        """Audio directory should exist."""
        path = Path("/home/workspace/Knowledge/content-library/audio")
        self.assertTrue(path.exists(), f"Missing directory: {path}")
    
    def test_video_directory(self):
        """Video directory should exist."""
        path = Path("/home/workspace/Knowledge/content-library/video")
        self.assertTrue(path.exists(), f"Missing directory: {path}")
    
    def test_images_directory(self):
        """Images directory should exist."""
        path = Path("/home/workspace/Knowledge/content-library/images")
        self.assertTrue(path.exists(), f"Missing directory: {path}")
    
    def test_transcripts_directory(self):
        """Transcripts directory should exist."""
        path = Path("/home/workspace/Knowledge/content-library/transcripts")
        self.assertTrue(path.exists(), f"Missing directory: {path}")


class TestContentLibraryMediaIngest(unittest.TestCase):
    """Test media ingest functionality."""
    
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.test_id = f"test-{uuid.uuid4().hex[:8]}"
    
    def tearDown(self):
        # Clean up test records
        self.cursor.execute("DELETE FROM items WHERE id LIKE 'test-%'")
        self.conn.commit()
        self.conn.close()
    
    def test_insert_mock_audio_record(self):
        """Should be able to insert a mock audio record."""
        self.cursor.execute("""
            INSERT INTO items (
                id, title, content_type, created_at, updated_at,
                file_path, mime_type, duration_seconds, tags
            ) VALUES (?, ?, ?, datetime('now'), datetime('now'), ?, ?, ?, ?)
        """, (
            self.test_id,
            "Test Audio Recording",
            "audio",
            "/home/workspace/Knowledge/content-library/audio/test.mp3",
            "audio/mpeg",
            120,
            json.dumps(["transcribed"])
        ))
        self.conn.commit()
        
        # Verify insertion
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (self.test_id,))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Failed to insert test record")
    
    def test_query_by_content_type(self):
        """Should be able to query by content type."""
        # Insert test record
        self.cursor.execute("""
            INSERT INTO items (
                id, title, content_type, created_at, updated_at,
                file_path, mime_type
            ) VALUES (?, ?, ?, datetime('now'), datetime('now'), ?, ?)
        """, (
            self.test_id,
            "Test Video",
            "video",
            "/test/path.mp4",
            "video/mp4"
        ))
        self.conn.commit()
        
        # Query
        self.cursor.execute(
            "SELECT * FROM items WHERE content_type = ? AND id = ?",
            ("video", self.test_id)
        )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Query by content_type failed")


class TestContentLibraryQuery(unittest.TestCase):
    """Test content_query.py functionality."""
    
    def test_import_query_module(self):
        """Should be able to import content_query module."""
        import sys
        sys.path.insert(0, str(Path("/home/workspace/N5/scripts")))
        try:
            from content_query import query_items, format_duration
            self.assertTrue(callable(query_items))
            self.assertTrue(callable(format_duration))
        except ImportError as e:
            self.fail(f"Failed to import content_query: {e}")
    
    def test_format_duration(self):
        """Duration formatting should work correctly."""
        import sys
        sys.path.insert(0, str(Path("/home/workspace/N5/scripts")))
        from content_query import format_duration
        
        self.assertEqual(format_duration(None), "-")
        self.assertEqual(format_duration(30), "30s")
        self.assertEqual(format_duration(90), "1m 30s")
        self.assertEqual(format_duration(3661), "1h 1m")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)

