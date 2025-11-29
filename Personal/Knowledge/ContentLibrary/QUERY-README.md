---
created: 2025-11-12
last_edited: 2025-11-12
version: 1.0
---

# Content Library Query Interface

## Overview

Query and search interface for the Content Library system. Built to enable fast, flexible querying of ingested content and blocks.

## ✅ Completion Status: COMPLETE

**Worker:** `worker_query`  
**Priority:** P1  
**Time Spent:** ~2 hours  
**Build Date:** 2025-11-12  

## 📦 Deliverables

### 1. Core Query Scripts (`query/search.py`)

**Module:** `ContentSearch` class with the following methods:

- `search_content(query, limit)` - Full-text search across content titles and notes
- `search_blocks(query, limit)` - Full-text search across block content and context
- `filter_by_block_type(block_code, limit)` - Filter by block code (B01, B08, B21, etc.)
- `filter_by_topic(topic, content_type, limit)` - Filter by taxonomy topic
- `get_recent_content(days, limit)` - Get recently added content
- `get_content_stats()` - Database statistics

**Usage Example:**
```python
from query.search import search_content, filter_by_block_type, get_stats

# Search across all content
results = search_content("product strategy", limit=10)

# Filter by block type
blocks = filter_by_block_type("B08", limit=50)

# Get database stats
stats = get_stats()
```

### 2. CLI Tool (`query/cli.py`)

**Commands:**

#### 🔍 Search
```bash
# Search everything
python cli.py search "advisory"

# Search only content
python cli.py search --type content "strategy"

# Search only blocks
python cli.py search --type blocks "customer"

# Verbose output with full content
python cli.py search "hiring" --verbose

# JSON output
python cli.py search "fundraising" --format json
```

#### 🔎 Filter
```bash
# Filter by block type
python cli.py filter --block-type B08

# Filter by topic (both content and blocks)
python cli.py filter --topic internal

# Filter by topic (only blocks)
python cli.py filter --topic advisory --content-type blocks

# Limit results
python cli.py filter --topic strategy --limit 20
```

#### 🏷️ Topics
```bash
# List all topics
python cli.py topics --list

# Search topics
python cli.py topics --search "hire"
```

#### 📊 Statistics
```bash
# Show database stats
python cli.py stats

# JSON output
python cli.py stats --format json
```

#### 💾 Export
```bash
# Export search results to JSON
python cli.py search "product" --format json --output results.json

# Export filtered results
python cli.py filter --block-type B25 --format json --output blocks_b25.json
```

## 📊 Test Data Results

**Database Stats:**
- Total Content: 16 entries (all meetings)
- Total Blocks: 14 blocks
- Total Topics: 8 topics

**Block Distribution:**
- B01 (deliverable_content): 2 blocks
- B02 (detailed_recap): 2 blocks
- B08 (stakeholder_intelligence): 2 blocks
- B21 (key_moments): 2 blocks
- B25 (deliverable_content): 2 blocks
- B26 (meeting_metadata): 2 blocks
- B31 (meeting_metadata): 2 blocks

**Topics Available:**
advisory, fundraising, hiring, internal, pitch, positioning, product, strategy

## 🚀 Getting Started

1. **Navigate to the Content Library directory:**
```bash
cd /home/workspace/Personal/Content-Library/query
```

2. **Test basic search:**
```bash
python cli.py stats
```

3. **Try a search query:**
```bash
python cli.py search "product strategy"
```

4. **Filter by block type:**
```bash
python cli.py filter --block-type B08
```

## 🛠️ Architecture

```
Content-Library/
├── cli.py                      # Main CLI entry point
├── query/
│   ├── __init__.py
│   ├── search.py              # Core search functions
│   └── cli.py                 # CLI implementation
├── content-library.db         # SQLite database
└── QUERY-README.md           # This file
```

## 📋 Dependencies Met

✅ **worker_ingest_raw** - Complete (test data: 2 content entries)  
✅ **worker_ingest_blocks** - Complete (test data: 14 blocks)  
✅ **SQLite database** - Ready and populated  

## 🎯 Next Steps

This worker is now complete and ready for:
1. **worker_knowledge_bridge** - Append-only promotion to Knowledge Base
2. Full production batch ingestion (613 B-block files available)
3. Real-world usage and query optimization

## 💡 Usage Examples

### Example 1: Find all stakeholder intelligence blocks
```bash
python cli.py filter --block-type B08
```

### Example 2: Search for mentions of "product strategy"
```bash
python cli.py search "product strategy" --verbose
```

### Example 3: Get all advisory blocks and export to JSON
```bash
python cli.py filter --topic advisory --format json --output advisory.json
```

### Example 4: List all available topics
```bash
python cli.py topics --list
```

## ✅ Validation Checklist

- [x] Query scripts created and tested
- [x] CLI tool implemented with multiple commands
- [x] Full-text search working
- [x] Filter by block type working
- [x] Filter by topic working
- [x] JSON export functional
- [x] Statistics command working
- [x] Topics listing working
- [x] Tested with test data
- [x] Documentation complete

## 📝 Notes

- CLI supports both human-readable text output and machine-readable JSON
- All queries use parameterized SQL to prevent injection
- Test data includes 2 meetings with full block coverage
- Ready for production batch processing of remaining 613 B-block files
- Architecture supports easy extension for additional query types

---

**Built by:** Vibe Architect (worker_query)  
**Status:** ✅ COMPLETE - Ready for production use

