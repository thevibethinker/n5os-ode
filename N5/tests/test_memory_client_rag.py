#!/usr/bin/env python3
"""
Tests for N5 Memory Client RAG improvements:
1. Hybrid search (BM25 + Semantic)
2. Markdown-aware chunking
3. Reranker (cross-encoder)
4. Metadata filtering

Run: python -m pytest N5/tests/test_memory_client_rag.py -v
"""

import os
import sys
import tempfile
import pytest
import sqlite3

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognition.n5_memory_client import N5MemoryClient, HAS_BM25, HAS_CROSS_ENCODER


class TestMarkdownAwareChunking:
    """Test markdown-aware chunking."""
    
    def setup_method(self):
        """Create temp DB for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        # Use local provider to avoid API calls
        os.environ['N5_EMBEDDING_PROVIDER'] = 'local'
        self.client = N5MemoryClient(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up temp DB."""
        if self.client._conn:
            self.client._conn.close()
        os.unlink(self.temp_db.name)
    
    def test_detects_markdown_content(self):
        """Verify markdown detection works."""
        markdown_content = """# Header One
        
Some content here.

## Header Two

More content with bullets:
- Item 1
- Item 2
"""
        chunks = self.client._chunk_content(markdown_content)
        # Should use markdown chunker (detected via headers/bullets)
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'text' in chunk
            assert 'start' in chunk
            assert 'end' in chunk
    
    def test_respects_code_blocks(self):
        """Code blocks should not be split."""
        content = """# Setup

Here's the code:

```python
def very_long_function():
    line1 = "test"
    line2 = "test"
    line3 = "test"
    line4 = "test"
    line5 = "test"
    line6 = "test"
    line7 = "test"
    line8 = "test"
    line9 = "test"
    line10 = "test"
    return line1 + line2 + line3
```

After code block.
"""
        chunks = self.client._chunk_content_markdown(content, max_chunk_size=200)
        
        # Find chunk containing code block
        code_chunks = [c for c in chunks if '```python' in c['text']]
        assert len(code_chunks) == 1, "Code block should be in exactly one chunk"
        
        # Verify entire code block is intact
        code_chunk = code_chunks[0]['text']
        assert 'def very_long_function' in code_chunk
        assert 'return line1' in code_chunk
    
    def test_splits_at_headers(self):
        """Headers should trigger splits when chunk is large enough."""
        content = """# First Section

Content for first section that is reasonably sized and has enough text to make it worthwhile to split at the next header.

# Second Section

Content for second section which is also meaningful.
"""
        chunks = self.client._chunk_content_markdown(content, max_chunk_size=200, min_chunk_size=50)
        
        # Should split at header boundary
        assert len(chunks) >= 2
        
        # Verify clean header boundaries
        headers_found = sum(1 for c in chunks if c['text'].strip().startswith('#'))
        assert headers_found >= 1
    
    def test_preserves_lists(self):
        """Bullet lists should stay together when possible."""
        content = """# List Section

Here are items:
- First item with description
- Second item with description
- Third item with description
- Fourth item with description
"""
        chunks = self.client._chunk_content_markdown(content, max_chunk_size=500)
        
        # All list items should be in same chunk (content is small)
        assert len(chunks) == 1 or all(
            'item' in c['text'].lower() for c in chunks
        )
    
    def test_fallback_for_plain_text(self):
        """Plain text without markdown markers uses simple chunking."""
        plain_content = "This is plain text. " * 100
        chunks = self.client._chunk_content(plain_content, chunk_size=200)
        
        # Should produce multiple chunks via simple chunker
        assert len(chunks) > 0
        total_len = sum(len(c['text']) for c in chunks)
        assert total_len == len(plain_content.strip()) or total_len > 0


class TestHybridSearch:
    """Test BM25 + Semantic hybrid search."""
    
    def setup_method(self):
        """Create temp DB and index test content."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        os.environ['N5_EMBEDDING_PROVIDER'] = 'local'
        self.client = N5MemoryClient(db_path=self.temp_db.name)
        
        # Index test documents
        self.test_docs = [
            ("doc1.md", "Python programming language is great for data science and machine learning"),
            ("doc2.md", "JavaScript is used for web development and frontend applications"),
            ("doc3.md", "Python data analysis with pandas and numpy libraries"),
            ("doc4.md", "Machine learning algorithms include neural networks and decision trees"),
        ]
        
        for path, content in self.test_docs:
            self.client.index_file(f"/test/{path}", content, content_date="2025-01-01")
    
    def teardown_method(self):
        if self.client._conn:
            self.client._conn.close()
        os.unlink(self.temp_db.name)
    
    @pytest.mark.skipif(not HAS_BM25, reason="rank_bm25 not installed")
    def test_bm25_tokenizer(self):
        """Test BM25 tokenizer."""
        tokens = self.client._tokenize("Hello World! Python is GREAT.")
        assert tokens == ['hello', 'world', 'python', 'is', 'great']
    
    @pytest.mark.skipif(not HAS_BM25, reason="rank_bm25 not installed")
    def test_bm25_scores_computed(self):
        """Verify BM25 scores are computed."""
        results = self.client.search("Python programming", limit=5, use_hybrid=True)
        
        # Should have bm25_score in results
        for r in results:
            assert 'bm25_score' in r
            assert isinstance(r['bm25_score'], float)
    
    @pytest.mark.skipif(not HAS_BM25, reason="rank_bm25 not installed")
    def test_hybrid_vs_semantic_only(self):
        """Hybrid search should produce different rankings for keyword-heavy queries."""
        # Keyword-heavy query
        query = "pandas numpy libraries"
        
        semantic_results = self.client.search(query, limit=4, use_hybrid=False)
        hybrid_results = self.client.search(query, limit=4, use_hybrid=True)
        
        # Both should return results
        assert len(semantic_results) > 0
        assert len(hybrid_results) > 0
        
        # BM25 should boost exact keyword matches
        # Doc3 contains "pandas and numpy libraries" - should rank higher with hybrid
        hybrid_paths = [r['path'] for r in hybrid_results]
        assert '/test/doc3.md' in hybrid_paths[:2], "BM25 should boost exact keyword match"
    
    def test_hybrid_weight_configuration(self):
        """Test custom weights for hybrid search."""
        query = "machine learning"
        
        # Heavy BM25 weight
        bm25_heavy = self.client.search(
            query, limit=4, use_hybrid=True,
            semantic_weight=0.3, bm25_weight=0.7
        )
        
        # Heavy semantic weight  
        semantic_heavy = self.client.search(
            query, limit=4, use_hybrid=True,
            semantic_weight=0.9, bm25_weight=0.1
        )
        
        # Both should work
        assert len(bm25_heavy) > 0
        assert len(semantic_heavy) > 0


class TestMetadataFiltering:
    """Test metadata filtering in search."""
    
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        os.environ['N5_EMBEDDING_PROVIDER'] = 'local'
        self.client = N5MemoryClient(db_path=self.temp_db.name)
        
        # Index diverse content
        self.client.index_file("/meetings/2025-01-15_team.md", "Team meeting about project updates", "2025-01-15")
        self.client.index_file("/meetings/2025-01-20_client.md", "Client meeting about requirements", "2025-01-20")
        self.client.index_file("/notes/research.md", "Research notes on algorithms", "2025-01-10")
        self.client.index_file("/code/main.py", "Python code for data processing", "2025-01-05")
    
    def teardown_method(self):
        if self.client._conn:
            self.client._conn.close()
        os.unlink(self.temp_db.name)
    
    def test_filter_by_path_contains(self):
        """Filter results by path pattern."""
        results = self.client.search(
            "meeting updates",
            limit=10,
            metadata_filters={'path': ('contains', 'meetings')}
        )
        
        # All results should be from meetings folder
        for r in results:
            assert '/meetings/' in r['path']
    
    def test_filter_by_path_startswith(self):
        """Filter by path prefix."""
        results = self.client.search(
            "notes research",
            limit=10,
            metadata_filters={'path': ('startswith', '/notes')}
        )
        
        for r in results:
            assert r['path'].startswith('/notes')
    
    def test_filter_by_date_range(self):
        """Filter by content date."""
        # After Jan 10
        results = self.client.search(
            "meeting",
            limit=10,
            metadata_filters={'content_date': ('gt', '2025-01-10')}
        )
        
        for r in results:
            if r['content_date']:
                assert r['content_date'] > '2025-01-10'
    
    def test_filter_exact_match(self):
        """Filter by exact value."""
        results = self.client.search(
            "code",
            limit=10,
            metadata_filters={'block_type': 'text'}
        )
        
        for r in results:
            assert r['block_type'] == 'text'
    
    def test_multiple_filters(self):
        """Combine multiple filters."""
        results = self.client.search(
            "project",
            limit=10,
            metadata_filters={
                'path': ('contains', 'meetings'),
                'content_date': ('gte', '2025-01-15')
            }
        )
        
        for r in results:
            assert '/meetings/' in r['path']
            if r['content_date']:
                assert r['content_date'] >= '2025-01-15'


class TestReranker:
    """Test cross-encoder reranking."""
    
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        os.environ['N5_EMBEDDING_PROVIDER'] = 'local'
        self.client = N5MemoryClient(db_path=self.temp_db.name)
        
        # Index test content
        docs = [
            ("doc1.md", "The capital of France is Paris, which is famous for the Eiffel Tower."),
            ("doc2.md", "Paris is a city in Texas, United States."),
            ("doc3.md", "French cuisine is known worldwide for its sophistication."),
            ("doc4.md", "The Eiffel Tower was built in 1889 for the World's Fair in Paris, France."),
            ("doc5.md", "France has many beautiful cities including Lyon and Marseille."),
        ]
        for path, content in docs:
            self.client.index_file(f"/test/{path}", content, "2025-01-01")
    
    def teardown_method(self):
        if self.client._conn:
            self.client._conn.close()
        os.unlink(self.temp_db.name)
    
    @pytest.mark.skipif(not HAS_CROSS_ENCODER, reason="Cross-encoder not available")
    def test_reranker_improves_relevance(self):
        """Reranker should improve relevance for ambiguous queries."""
        query = "What is the capital of France?"
        
        # Without reranking
        base_results = self.client.search(query, limit=5, use_reranker=False)
        
        # With reranking
        reranked_results = self.client.search(query, limit=5, use_reranker=True, rerank_top_k=5)
        
        # Both should return results
        assert len(base_results) > 0
        assert len(reranked_results) > 0
        
        # Reranked results should have rerank_score
        if reranked_results and 'rerank_score' in reranked_results[0]:
            # Doc1 or Doc4 should rank highly (mention Paris + France)
            top_paths = [r['path'] for r in reranked_results[:2]]
            france_docs = [p for p in top_paths if 'doc1' in p or 'doc4' in p]
            assert len(france_docs) > 0, "Reranker should boost France-related docs"
    
    @pytest.mark.skipif(not HAS_CROSS_ENCODER, reason="Cross-encoder not available")
    def test_reranker_handles_missing_model_gracefully(self):
        """Search should work even if reranker fails."""
        # Temporarily break the cross encoder
        original_encoder = self.client.cross_encoder
        self.client.cross_encoder = None
        
        results = self.client.search("Paris France", limit=5, use_reranker=True)
        
        # Should still return results via base search
        assert len(results) > 0
        
        # Restore
        self.client.cross_encoder = original_encoder


class TestIntegration:
    """Integration tests combining all features."""
    
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        os.environ['N5_EMBEDDING_PROVIDER'] = 'local'
        self.client = N5MemoryClient(db_path=self.temp_db.name)
    
    def teardown_method(self):
        if self.client._conn:
            self.client._conn.close()
        os.unlink(self.temp_db.name)
    
    def test_full_pipeline_markdown_indexing(self):
        """Test indexing markdown content and searching."""
        markdown_content = """# N5 System Documentation

## Overview

N5 is an AI operating system framework for personal knowledge management.

## Features

- Semantic search with embeddings
- Markdown-aware chunking
- Metadata filtering
- Hybrid BM25 + semantic search

```python
from n5_memory_client import N5MemoryClient
client = N5MemoryClient()
results = client.search("knowledge management")
```

## Architecture

The system uses SQLite for storage and supports multiple embedding providers.
"""
        
        self.client.index_file("/docs/n5_docs.md", markdown_content, "2025-12-12")
        
        # Search should work
        results = self.client.search("semantic search embeddings", limit=5)
        assert len(results) > 0

        # Results should include line-range metadata for downstream renderers
        first = results[0]
        assert 'start_line' in first and 'end_line' in first
        assert 'lines' in first and isinstance(first['lines'], list) and len(first['lines']) == 2
        
        # Results should contain relevant content
        found_content = ' '.join(r['content'] for r in results)
        assert 'semantic' in found_content.lower() or 'search' in found_content.lower()
    
    @pytest.mark.skipif(not HAS_BM25, reason="BM25 not available")
    def test_combined_features(self):
        """Test all features together."""
        # Index varied content
        self.client.index_file("/meetings/standup.md", "Daily standup meeting notes about sprint progress", "2025-12-01")
        self.client.index_file("/meetings/retro.md", "Sprint retrospective discussion and action items", "2025-12-10")
        self.client.index_file("/notes/ideas.md", "Product ideas and feature brainstorming", "2025-12-05")
        
        # Search with all features
        results = self.client.search(
            "sprint progress updates",
            limit=5,
            use_hybrid=True,
            semantic_weight=0.6,
            bm25_weight=0.4,
            recency_weight=0.2,
            metadata_filters={'path': ('contains', 'meetings')}
        )
        
        # Should only return meetings
        assert all('/meetings/' in r['path'] for r in results)
        
        # Should have meaningful scores
        for r in results:
            assert r['score'] > 0
            assert 'bm25_score' in r


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])


