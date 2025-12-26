---
created: 2025-11-04
last_edited: 2025-12-02
version: 1.2
status: Phase 1 Complete (7/8 components)
---
# Documents & Media Intelligence System

**Purpose:** Comprehensive system for tracking, processing, and extracting intelligence from documents and media across the workspace.

**Status:** Phase 1 Complete - 7/8 components delivered (87.5%)
- ✅ Database schema (v1.1 with curation_score)
- ✅ Document/media processor
- ✅ Intelligence extractor
- ✅ Query interface
- ✅ Intelligence output directories
- ✅ Documentation
- ✅ Database init script
- ⏸️ Curation module (deferred to Phase 3)

## Overview

The Documents & Media Intelligence System provides automated ingestion, deduplication, metadata extraction, intelligence generation, and querying capabilities for all documents and media files in your workspace.

### Architecture

- **Database:** SQLite at `N5/data/documents_media.db`
- **Intelligence Output:** `Knowledge/intelligence/`
- **Processing Scripts:** `N5/scripts/document_*.py`

## Components

### 1. Database Schema (`documents_media.db`)

Three core tables:

**documents:**
- Tracks all document files (PDF, Word, MD, TXT, etc.)
- Stores metadata, checksums for deduplication
- Processing status tracking

**media:**
- Tracks audio/video files
- Links to transcript files
- Processing status and curation scores

**intelligence_extracts:**
- Links processed documents/media to intelligence files
- Tracks extraction types and dates

### 2. Document Processor (`document_processor.py`)

**Purpose:** Ingest documents and media into registry

**Usage:**
```bash
# Scan specific directory
python3 /home/workspace/N5/scripts/document_processor.py --directory /path/to/dir

# Process single file
python3 /home/workspace/N5/scripts/document_processor.py --file /path/to/file.pdf

# Auto-scan watched directories
python3 /home/workspace/N5/scripts/document_processor.py --scan

# Dry-run mode
python3 /home/workspace/N5/scripts/document_processor.py --scan --dry-run
```

**Watched Directories:**
- `/home/workspace/Articles`
- `/home/workspace/Documents`
- `/home/workspace/Personal/Meetings`
- `/home/workspace/Records`
- `/home/workspace/Reports`

> **Note (JS-heavy social sites):** Pages from x.com (X/Twitter) and similar JS-only frontends often save as a generic "JavaScript is not available" shell when fetched headlessly. These raw captures are useful for provenance and basic linking, but **must not** be treated as the canonical text of the tweet/post. For actual tweet/post content, use API-aware tools (e.g., `tool x_search`) or manual copy from a real browser, and store the canonical text in a curated location (e.g., `Personal/Knowledge/ContentLibrary/content/*.md`).

**Features:**
- SHA256 checksum-based deduplication
- Automatic metadata extraction
- Transcript detection for media files
- Supports 15+ document formats
- Supports audio (MP3, M4A, WAV) and video (MP4, MOV, AVI)

### 3. Intelligence Extractor (`intelligence_extractor.py`)

**Purpose:** Extract intelligence from ingested documents/media

**Usage:**
```bash
# Process all pending items
python3 /home/workspace/N5/scripts/intelligence_extractor.py

# Dry-run mode
python3 /home/workspace/N5/scripts/intelligence_extractor.py --dry-run
```

**Output:** Creates markdown intelligence files in `Knowledge/intelligence/`:
- `documents/` - Document intelligence files
- `media/` - Media intelligence files
- `extracts/` - Additional extracts

**Intelligence File Contents:**
- Source metadata
- Content summary (word count, structure)
- Key sections/headers extracted
- Transcript analysis for media
- Processing notes and next steps

### 4. Query Interface (`documents_media_query.py`)

**Purpose:** Search and retrieve documents/media

**Usage:**
```bash
# Show statistics
python3 /home/workspace/N5/scripts/documents_media_query.py --stats

# List all documents
python3 /home/workspace/N5/scripts/documents_media_query.py --list-docs

# List all media
python3 /home/workspace/N5/scripts/documents_media_query.py --list-media

# Search by filename
python3 /home/workspace/N5/scripts/documents_media_query.py --search "meeting"

# Search by tags
python3 /home/workspace/N5/scripts/documents_media_query.py --tags "product,strategy"

# Filter by status
python3 /home/workspace/N5/scripts/documents_media_query.py --list-docs --status processed

# JSON output
python3 /home/workspace/N5/scripts/documents_media_query.py --stats --format json
```

## Workflows

### Standard Processing Pipeline

1. **Ingest:** Scan directories for new documents/media
   ```bash
   python3 N5/scripts/document_processor.py --scan
   ```

2. **Extract:** Process pending items to generate intelligence
   ```bash
   python3 N5/scripts/intelligence_extractor.py
   ```

3. **Query:** Search and retrieve processed items
   ```bash
   python3 N5/scripts/documents_media_query.py --stats
   ```

### Manual Processing

**Single File:**
```bash
# 1. Ingest
python3 N5/scripts/document_processor.py --file /path/to/document.pdf

# 2. Extract
python3 N5/scripts/intelligence_extractor.py

# 3. Verify
python3 N5/scripts/documents_media_query.py --search "document.pdf"
```

**Directory Batch:**
```bash
# 1. Ingest directory
python3 N5/scripts/document_processor.py --directory /home/workspace/Records

# 2. Extract intelligence
python3 N5/scripts/intelligence_extractor.py

# 3. Check stats
python3 N5/scripts/documents_media_query.py --stats
```

## Integration Points

### 1. Meeting Intelligence System
- Automatically tracks meeting recordings from `Personal/Meetings/`
- Links transcripts to intelligence extracts
- Supports meeting intelligence workflow

### 2. Conversation Log System
- Documents from conversations archived to workspace
- Auto-scanned and processed for intelligence

### 3. Content Library
- Intelligence extracts can source content library items
- Quotes and snippets extracted for communication use

### 4. CRM System
- Link documents to contacts
- Track document interactions
- Source intelligence for relationship management

## Data Flow

```
Documents/Media Files
        ↓
[document_processor.py]
        ↓
documents_media.db (registry)
        ↓
[intelligence_extractor.py]
        ↓
Knowledge/intelligence/*.md
        ↓
[documents_media_query.py]
        ↓
Search Results / Stats
```

## Principles Applied

### P1: Human-Readable First
- Intelligence files in markdown format
- Human-readable before machine-processable

### P2: Single Source of Truth
- Database is SSOT for document registry
- Intelligence files derived from originals

### P5: Safety & Anti-Overwrite
- SHA256 checksums prevent duplicates
- Non-destructive processing (originals preserved)

### P7: Idempotence
- Re-processing same file yields same results
- Dry-run mode available

### P11: Failure Modes
- Graceful error handling
- Status tracking (pending/processed/error)

## Status Tracking

**Processing Statuses:**
- `pending` - Ingested, awaiting intelligence extraction
- `processed` - Intelligence extracted successfully
- `curated` - Manually reviewed and enhanced
- `error` - Processing failed (check logs)

## Maintenance

### Regular Tasks

**Weekly:**
- Run auto-scan to catch new documents
  ```bash
  python3 N5/scripts/document_processor.py --scan
  ```

**After bulk imports:**
- Process pending items
  ```bash
  python3 N5/scripts/intelligence_extractor.py
  ```

### Troubleshooting

**Database not found:**
```bash
python3 /home/workspace/N5/scripts/documents_media_db_init.py
```

**Check processing status:**
```bash
python3 N5/scripts/documents_media_query.py --list-docs --status pending
```

**View intelligence files:**
```bash
ls -la /home/workspace/Knowledge/intelligence/documents/
ls -la /home/workspace/Knowledge/intelligence/media/
```

## Future Enhancements

**Planned:**
- Automated tagging based on content analysis
- Curation scoring algorithm
- Bulk export capabilities
- Integration with scheduled tasks for auto-processing
- Advanced intelligence extraction (key insights, action items)
- Cross-document relationship mapping

## Files Reference

**Scripts:**
- `file 'N5/scripts/documents_media_db_init.py'` - Database initialization
- `file 'N5/scripts/document_processor.py'` - Document/media ingestion
- `file 'N5/scripts/intelligence_extractor.py'` - Intelligence extraction
- `file 'N5/scripts/documents_media_query.py'` - Query interface

**Database:**
- `file 'N5/data/documents_media.db'` - Registry database

**Intelligence Output:**
- `Knowledge/intelligence/documents/` - Document intelligence files
- `Knowledge/intelligence/media/` - Media intelligence files

**Architecture:**
- `file '/home/.z/workspaces/con_tQFELbaVhzMT7EAT/WORKER_2_DELIVERABLE_DOCUMENTS_MEDIA_ARCHITECTURE.md'` - Original architectural specification

## System Version

**Current Version:** 1.1  
**Schema Version:** 1.1  
**Last Updated:** 2025-11-04

**Changelog:**
- **v1.1** (2025-11-04): Schema migration - added curation_score columns, fixed query interface
- **v1.0** (2025-11-04): Initial Phase 1 implementation

---

**System Status:** Production Ready (Phase 1 - 7/8 components)  
**Debugger Verified:** 2025-11-04 (80% grade - B-)  
**Last Updated:** 2025-11-04  
**Builder:** Vibe Builder v2.0


