#!/usr/bin/env python3
"""
Test Suite for Executable Manager - Fixed Version
Tests registration, search, analytics, and error handling.
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import executable_manager as em


@pytest.fixture
def temp_db():
    """Create temporary database matching exact production schema."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    original_db = em.DB_PATH
    em.DB_PATH = db_path
    
    conn = em.get_connection()
    
    # Create main table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS executables (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            description TEXT,
            category TEXT,
            tags TEXT,
            version TEXT DEFAULT '1.0',
            status TEXT DEFAULT 'active',
            frontmatter TEXT,
            entrypoint TEXT,
            dependencies TEXT,
            parent_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Create FTS table - EXACTLY as in production (no category)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS executables_fts USING fts5(
            id, name, description, tags,
            content='executables', content_rowid='rowid'
        )
    """)
    
    # Create triggers for FTS sync - EXACTLY as in production
    conn.execute("""
        CREATE TRIGGER executables_ai AFTER INSERT ON executables BEGIN
            INSERT INTO executables_fts(rowid, id, name, description, tags)
            VALUES (new.rowid, new.id, new.name, new.description, new.tags);
        END
    """)
    
    conn.execute("""
        CREATE TRIGGER executables_ad AFTER DELETE ON executables BEGIN
            DELETE FROM executables_fts WHERE rowid = old.rowid;
        END
    """)
    
    conn.execute("""
        CREATE TRIGGER executables_au AFTER UPDATE ON executables BEGIN
            UPDATE executables_fts 
            SET id = new.id, name = new.name, description = new.description, tags = new.tags
            WHERE rowid = new.rowid;
        END
    """)
    
    # Create invocations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            executable_id TEXT NOT NULL,
            invoked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            conversation_id TEXT,
            trigger_method TEXT CHECK(trigger_method IN ('incantum', 'direct', 'programmatic')),
            FOREIGN KEY (executable_id) REFERENCES executables(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    em.DB_PATH = original_db
    db_path.unlink(missing_ok=True)


@pytest.fixture
def temp_prompt_file():
    """Create temporary prompt file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
description: Test prompt for testing
category: testing
tags: [test, sample]
---

# Test Prompt

This is a test prompt.
""")
        file_path = Path(f.name)
    
    yield file_path
    
    file_path.unlink(missing_ok=True)


class TestRegistration:
    """Test executable registration."""
    
    def test_register_new_prompt(self, temp_db, temp_prompt_file):
        """Test registering a new prompt."""
        result = em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="test-prompt",
            name="Test Prompt"
        )
        
        assert result.id == "test-prompt"
        assert result.name == "Test Prompt"
        assert result.type == "prompt"
        assert result.file_path == str(temp_prompt_file)
    
    def test_register_duplicate_id_fails(self, temp_db, temp_prompt_file):
        """Test that duplicate IDs are rejected."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="dup-test"
        )
        
        with pytest.raises(Exception):
            em.register_executable(
                file_path=str(temp_prompt_file),
                exec_type="prompt",
                exec_id="dup-test"
            )
    
    def test_register_with_metadata(self, temp_db, temp_prompt_file):
        """Test registration with full metadata."""
        result = em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="meta-test",
            name="Metadata Test",
            description="A test with metadata",
            category="testing",
            tags=["test", "metadata"],
            version="2.0"
        )
        
        assert result.description == "A test with metadata"
        assert result.category == "testing"
        assert result.version == "2.0"


class TestRetrieval:
    """Test executable retrieval operations."""
    
    def test_get_existing_executable(self, temp_db, temp_prompt_file):
        """Test retrieving an existing executable."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="get-test"
        )
        
        result = em.get_executable("get-test")
        assert result is not None
        assert result.id == "get-test"
    
    def test_get_nonexistent_executable(self, temp_db):
        """Test retrieving non-existent executable returns None."""
        result = em.get_executable("does-not-exist")
        assert result is None
    
    def test_list_all_executables(self, temp_db, temp_prompt_file):
        """Test listing all executables."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="list-test-1"
        )
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="list-test-2"
        )
        
        results = em.list_executables()
        assert len(results) == 2
    
    def test_list_by_type(self, temp_db, temp_prompt_file):
        """Test filtering by type."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="prompt-1"
        )
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="script",
            exec_id="script-1"
        )
        
        prompts = em.list_executables(exec_type="prompt")
        assert len(prompts) == 1
        assert prompts[0].type == "prompt"
    
    def test_list_by_category(self, temp_db, temp_prompt_file):
        """Test filtering by category."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="cat-1",
            category="meetings"
        )
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="cat-2",
            category="analysis"
        )
        
        meetings = em.list_executables(category="meetings")
        assert len(meetings) == 1
        assert meetings[0].category == "meetings"


class TestSearch:
    """Test full-text search functionality."""
    
    def test_search_by_name(self, temp_db, temp_prompt_file):
        """Test searching by name."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="search-1",
            name="Meeting Notes"
        )
        
        results = em.search_executables("Meeting")
        assert len(results) >= 1
        assert any(r.id == "search-1" for r in results)
    
    def test_search_by_description(self, temp_db, temp_prompt_file):
        """Test searching by description."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="search-2",
            name="Test",
            description="Analyze quarterly performance metrics"
        )
        
        results = em.search_executables("quarterly")
        assert len(results) >= 1
    
    def test_search_empty_query_raises_error(self, temp_db):
        """Test that empty search raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            em.search_executables("")
    
    def test_search_no_results(self, temp_db, temp_prompt_file):
        """Test search with no matching results."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="search-3"
        )
        
        results = em.search_executables("zzzznonexistent")
        assert len(results) == 0


class TestUpdate:
    """Test update operations."""
    
    def test_update_description(self, temp_db, temp_prompt_file):
        """Test updating description."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="update-1",
            description="Old description"
        )
        
        em.update_executable("update-1", description="New description")
        
        result = em.get_executable("update-1")
        assert result.description == "New description"
    
    def test_update_multiple_fields(self, temp_db, temp_prompt_file):
        """Test updating multiple fields at once."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="update-2",
            category="old",
            version="1.0"
        )
        
        em.update_executable(
            "update-2",
            category="new",
            version="2.0"
        )
        
        result = em.get_executable("update-2")
        assert result.category == "new"
        assert result.version == "2.0"
    
    def test_update_nonexistent_returns_none(self, temp_db):
        """Test updating non-existent executable returns None."""
        result = em.update_executable("does-not-exist", description="New")
        assert result is None


class TestDelete:
    """Test deletion operations."""
    
    def test_delete_existing(self, temp_db, temp_prompt_file):
        """Test deleting an existing executable."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="delete-1"
        )
        
        result = em.delete_executable("delete-1")
        assert result is True
        
        retrieved = em.get_executable("delete-1")
        assert retrieved is None
    
    def test_delete_nonexistent(self, temp_db):
        """Test deleting non-existent executable."""
        result = em.delete_executable("does-not-exist")
        assert result is False


class TestAnalytics:
    """Test invocation tracking and analytics."""
    
    def test_track_invocation(self, temp_db, temp_prompt_file):
        """Test tracking invocations."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="track-1"
        )
        
        em.track_invocation("track-1")
        em.track_invocation("track-1")
        
        stats = em.get_usage_stats("track-1", days=30)
        assert stats["total_invocations"] == 2
    
    def test_usage_stats_all_executables(self, temp_db, temp_prompt_file):
        """Test getting stats for all executables."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="stats-1"
        )
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="stats-2"
        )
        
        em.track_invocation("stats-1")
        em.track_invocation("stats-2")
        em.track_invocation("stats-2")
        
        stats = em.get_usage_stats(days=30)
        # Stats format is {'days': N, 'top_executables': [...]}
        assert "top_executables" in stats
        exec_ids = [e["id"] for e in stats["top_executables"]]
        assert "stats-1" in exec_ids
        assert "stats-2" in exec_ids


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_database_list(self, temp_db):
        """Test listing from empty database."""
        results = em.list_executables()
        assert len(results) == 0
    
    def test_special_characters_in_id(self, temp_db, temp_prompt_file):
        """Test handling special characters in IDs."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="test-id_with.special-chars"
        )
        
        result = em.get_executable("test-id_with.special-chars")
        assert result is not None
    
    def test_long_description(self, temp_db, temp_prompt_file):
        """Test handling very long descriptions."""
        long_desc = "A" * 1000
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="long-1",
            description=long_desc
        )
        
        result = em.get_executable("long-1")
        assert result.description == long_desc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestDryRun:
    """Test dry-run functionality."""
    
    def test_dry_run_update(self, temp_db, temp_prompt_file):
        """Test dry-run for update shows preview."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="dry-update-1",
            description="Old description",
            version="1.0"
        )
        
        preview = em.update_executable(
            "dry-update-1",
            dry_run=True,
            description="New description",
            version="2.0"
        )
        
        # Verify it's a preview
        assert preview["dry_run"] is True
        assert preview["operation"] == "update"
        assert preview["exec_id"] == "dry-update-1"
        
        # Verify changes shown
        assert "description" in preview["changes"]
        assert preview["changes"]["description"]["old"] == "Old description"
        assert preview["changes"]["description"]["new"] == "New description"
        
        # Verify nothing actually changed
        actual = em.get_executable("dry-update-1")
        assert actual.description == "Old description"
        assert actual.version == "1.0"
    
    def test_dry_run_delete(self, temp_db, temp_prompt_file):
        """Test dry-run for delete shows preview."""
        em.register_executable(
            file_path=str(temp_prompt_file),
            exec_type="prompt",
            exec_id="dry-delete-1",
            name="Test Prompt"
        )
        
        preview = em.delete_executable("dry-delete-1", dry_run=True)
        
        # Verify it's a preview
        assert preview["dry_run"] is True
        assert preview["operation"] == "delete"
        assert preview["exec_id"] == "dry-delete-1"
        assert preview["found"] is True
        assert preview["name"] == "Test Prompt"
        
        # Verify nothing actually deleted
        actual = em.get_executable("dry-delete-1")
        assert actual is not None
    
    def test_dry_run_update_nonexistent(self, temp_db):
        """Test dry-run update on non-existent executable."""
        preview = em.update_executable(
            "does-not-exist",
            dry_run=True,
            description="New"
        )
        
        assert preview["dry_run"] is True
        assert "error" in preview
    
    def test_dry_run_delete_nonexistent(self, temp_db):
        """Test dry-run delete on non-existent executable."""
        preview = em.delete_executable("does-not-exist", dry_run=True)
        
        assert preview["dry_run"] is True
        assert preview["found"] is False
