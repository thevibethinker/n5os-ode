# N5 Content Library Infrastructure - Design Specification

## Architecture Decision

**Recommendation**: Hybrid approach - SQLite for metadata/index + file system for content.

### Rationale

1. **SQLite Benefits**:
   - Fast full-text search (FTS5)
   - Structured metadata queries
   - Relationship tracking
   - Single-file portability
   - No external dependencies

2. **File System Benefits**:
   - Original content preservation
   - Easy backup/sync
   - Human-readable organization
   - Version control friendly

3. **N5 Core Integration**:
   - Separate module (`N5/content/`) to maintain modularity
   - Integration points with bulletins (new content announcements)
   - Integration with session state (content used in sessions)
   - Integration with Records (content access history)

## Database Schema

### SQLite Tables

```sql
-- Core content table
CREATE TABLE content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT UNIQUE NOT NULL,  -- hash-based or uuid
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,  -- 'article', 'pdf', 'audio', 'video', 'note'
    source_url TEXT,
    file_path TEXT,  -- relative to N5/content/files/
    ingested_at TEXT NOT NULL,  -- ISO 8601
    modified_at TEXT NOT NULL,
    content_text TEXT,  -- extracted text for search
    summary TEXT,  -- AI-generated summary
    word_count INTEGER,
    read_time_minutes INTEGER,
    status TEXT DEFAULT 'active',  -- 'active', 'archived', 'deleted'
    metadata JSON  -- flexible additional data
);

-- Full-text search index
CREATE VIRTUAL TABLE content_fts USING fts5(
    title,
    content_text,
    content='content',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER content_fts_insert AFTER INSERT ON content BEGIN
    INSERT INTO content_fts(rowid, title, content_text)
    VALUES (new.id, new.title, new.content_text);
END;

CREATE TRIGGER content_fts_update AFTER UPDATE ON content BEGIN
    UPDATE content_fts SET title = new.title, content_text = new.content_text
    WHERE rowid = old.id;
END;

CREATE TRIGGER content_fts_delete AFTER DELETE ON content BEGIN
    DELETE FROM content_fts WHERE rowid = old.id;
END;

-- Tags (many-to-many)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE content_tags (
    content_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Relationships
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_content_id INTEGER NOT NULL,
    to_content_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'related', 'references', 'supersedes'
    strength REAL DEFAULT 0.5,  -- 0.0 to 1.0
    created_at TEXT NOT NULL,
    FOREIGN KEY (from_content_id) REFERENCES content(id) ON DELETE CASCADE,
    FOREIGN KEY (to_content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Access history (for recommendations)
CREATE TABLE access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    accessed_at TEXT NOT NULL,
    conversation_id TEXT,  -- link to session
    access_type TEXT,  -- 'view', 'reference', 'search'
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Embeddings (optional, for semantic search)
CREATE TABLE embeddings (
    content_id INTEGER PRIMARY KEY,
    embedding BLOB,  -- serialized vector
    model TEXT NOT NULL,  -- embedding model used
    created_at TEXT NOT NULL,
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Indices for performance
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_ingested ON content(ingested_at);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_relationships_from ON relationships(from_content_id);
CREATE INDEX idx_relationships_to ON relationships(to_content_id);
CREATE INDEX idx_access_conversation ON access_log(conversation_id);
```

## Directory Structure

```
N5/
├── content/
│   ├── library.db              # SQLite database
│   ├── files/                  # Content storage
│   │   ├── articles/
│   │   │   ├── 2025-10/
│   │   │   │   └── content-id.md
│   │   ├── pdfs/
│   │   │   └── original-name.pdf
│   │   ├── audio/
│   │   │   ├── recording.m4a
│   │   │   └── recording.m4a.transcript.jsonl
│   │   └── notes/
│   │       └── my-note.md
│   ├── scripts/
│   │   ├── content_ingest.py   # Ingestion pipeline
│   │   ├── content_search.py   # Search interface
│   │   ├── content_relate.py   # Relationship builder
│   │   └── content_export.py   # Export utilities
│   └── docs/
│       └── content_library.md  # Documentation
```

## Implementation: Core Scripts

### 1. Ingestion Pipeline (`content_ingest.py`)

```python
#!/usr/bin/env python3
"""
Content ingestion pipeline for N5 Content Library.

Handles web articles, PDFs, audio, video, and text notes.
"""

import argparse
import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

N5_ROOT = Path("/home/workspace/N5")
CONTENT_ROOT = N5_ROOT / "content"
DB_PATH = CONTENT_ROOT / "library.db"
FILES_ROOT = CONTENT_ROOT / "files"

class ContentIngester:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        
    def generate_content_id(self, source: str) -> str:
        """Generate unique content ID from source"""
        return hashlib.sha256(source.encode()).hexdigest()[:16]
        
    def ingest_url(self, url: str, tags: list = None):
        """Ingest web article or PDF URL"""
        print(f"Ingesting URL: {url}")
        
        # Use Zo's read_webpage equivalent (curl or custom)
        # For demonstration, assume markdown saved to temp location
        temp_file = Path(f"/tmp/{self.generate_content_id(url)}.md")
        
        # In real implementation: use curl or Zo API
        # subprocess.run(['curl', url, '-o', temp_file])
        
        # Extract text content
        content_text = temp_file.read_text() if temp_file.exists() else ""
        
        # Determine content type
        parsed = urlparse(url)
        content_type = 'pdf' if parsed.path.endswith('.pdf') else 'article'
        
        # Generate summary (placeholder - use LLM in real impl)
        summary = content_text[:500] + "..." if len(content_text) > 500 else content_text
        
        # Save to library
        self._save_content(
            content_id=self.generate_content_id(url),
            title=self._extract_title(content_text),
            content_type=content_type,
            source_url=url,
            content_text=content_text,
            summary=summary,
            tags=tags or []
        )
        
    def ingest_file(self, file_path: Path, tags: list = None):
        """Ingest local file"""
        print(f"Ingesting file: {file_path}")
        
        # Determine content type by extension
        ext = file_path.suffix.lower()
        type_map = {
            '.md': 'note',
            '.txt': 'note',
            '.pdf': 'pdf',
            '.m4a': 'audio',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.mov': 'video'
        }
        content_type = type_map.get(ext, 'unknown')
        
        # Extract text
        if content_type == 'note':
            content_text = file_path.read_text()
        elif content_type == 'pdf':
            # Use pdftotext or similar
            content_text = self._extract_pdf_text(file_path)
        elif content_type in ['audio', 'video']:
            # Check for transcript
            transcript_path = Path(str(file_path) + '.transcript.jsonl')
            content_text = self._extract_transcript(transcript_path) if transcript_path.exists() else ""
        else:
            content_text = ""
            
        # Copy file to library
        dest_dir = FILES_ROOT / f"{content_type}s"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / file_path.name
        
        if not dest_file.exists():
            import shutil
            shutil.copy(file_path, dest_file)
            
        # Save to library
        self._save_content(
            content_id=self.generate_content_id(str(file_path)),
            title=file_path.stem,
            content_type=content_type,
            file_path=str(dest_file.relative_to(CONTENT_ROOT)),
            content_text=content_text,
            summary=content_text[:500] if content_text else "",
            tags=tags or []
        )
        
    def _save_content(self, content_id, title, content_type, content_text, 
                     summary, tags, source_url=None, file_path=None):
        """Save content to database"""
        now = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        
        # Insert content
        cursor.execute("""
            INSERT OR REPLACE INTO content 
            (content_id, title, content_type, source_url, file_path, 
             ingested_at, modified_at, content_text, summary, 
             word_count, read_time_minutes, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            content_id, title, content_type, source_url, file_path,
            now, now, content_text, summary,
            len(content_text.split()), max(1, len(content_text.split()) // 200),
            json.dumps({})
        ))
        
        content_db_id = cursor.lastrowid
        
        # Add tags
        for tag_name in tags:
            cursor.execute("INSERT OR IGNORE INTO tags (name, created_at) VALUES (?, ?)", 
                          (tag_name, now))
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]
            cursor.execute("INSERT OR IGNORE INTO content_tags VALUES (?, ?)",
                          (content_db_id, tag_id))
        
        self.conn.commit()
        print(f"✓ Content saved: {title} (ID: {content_id})")
        
    def _extract_title(self, text: str) -> str:
        """Extract title from markdown content"""
        for line in text.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"
        
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF"""
        # Use pdftotext if available
        try:
            result = subprocess.run(
                ['pdftotext', str(pdf_path), '-'],
                capture_output=True, text=True
            )
            return result.stdout
        except FileNotFoundError:
            return ""
            
    def _extract_transcript(self, transcript_path: Path) -> str:
        """Extract text from transcript JSONL"""
        data = json.loads(transcript_path.read_text())
        return data.get('text', '')
        
    def close(self):
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="Ingest content into N5 library")
    parser.add_argument('source', help="URL or file path to ingest")
    parser.add_argument('--tags', nargs='+', help="Tags to apply")
    args = parser.parse_args()
    
    ingester = ContentIngester()
    
    source = Path(args.source)
    if source.exists():
        ingester.ingest_file(source, args.tags)
    else:
        ingester.ingest_url(args.source, args.tags)
        
    ingester.close()

if __name__ == "__main__":
    main()
```

### 2. Search Interface (`content_search.py`)

```python
#!/usr/bin/env python3
"""
Search interface for N5 Content Library.

Supports full-text search, filtering, and semantic search.
"""

import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "content" / "library.db"

class ContentSearcher:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        
    def search(self, query: str, content_type: str = None, 
              tags: list = None, limit: int = 10):
        """Full-text search with filters"""
        
        # Build query
        sql = """
            SELECT c.*, GROUP_CONCAT(t.name) as tags
            FROM content c
            LEFT JOIN content_tags ct ON c.id = ct.content_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            WHERE c.id IN (
                SELECT rowid FROM content_fts 
                WHERE content_fts MATCH ?
            )
        """
        
        params = [query]
        
        if content_type:
            sql += " AND c.content_type = ?"
            params.append(content_type)
            
        if tags:
            sql += " AND t.name IN ({})".format(','.join('?' * len(tags)))
            params.extend(tags)
            
        sql += " GROUP BY c.id ORDER BY c.modified_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
            
        return results
        
    def recent(self, days: int = 30, limit: int = 10):
        """Get recently added content"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, GROUP_CONCAT(t.name) as tags
            FROM content c
            LEFT JOIN content_tags ct ON c.id = ct.content_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            WHERE c.ingested_at > ?
            GROUP BY c.id
            ORDER BY c.ingested_at DESC
            LIMIT ?
        """, (cutoff, limit))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def by_tag(self, tag: str, limit: int = 10):
        """Get content by tag"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, GROUP_CONCAT(t.name) as tags
            FROM content c
            JOIN content_tags ct ON c.id = ct.content_id
            JOIN tags t ON ct.tag_id = t.id
            WHERE t.name = ?
            GROUP BY c.id
            ORDER BY c.modified_at DESC
            LIMIT ?
        """, (tag, limit))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def related(self, content_id: str, limit: int = 5):
        """Find related content"""
        # Get content DB id
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM content WHERE content_id = ?", (content_id,))
        row = cursor.fetchone()
        if not row:
            return []
            
        db_id = row[0]
        
        # Find relationships
        cursor.execute("""
            SELECT c.*, r.relationship_type, r.strength
            FROM relationships r
            JOIN content c ON r.to_content_id = c.id
            WHERE r.from_content_id = ?
            ORDER BY r.strength DESC
            LIMIT ?
        """, (db_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def close(self):
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="Search N5 content library")
    parser.add_argument('query', nargs='?', help="Search query")
    parser.add_argument('--type', help="Filter by content type")
    parser.add_argument('--tags', nargs='+', help="Filter by tags")
    parser.add_argument('--recent', type=int, help="Show recent (days)")
    parser.add_argument('--tag', help="Show content by single tag")
    parser.add_argument('--limit', type=int, default=10, help="Result limit")
    args = parser.parse_args()
    
    searcher = ContentSearcher()
    
    if args.recent:
        results = searcher.recent(days=args.recent, limit=args.limit)
    elif args.tag:
        results = searcher.by_tag(args.tag, limit=args.limit)
    elif args.query:
        results = searcher.search(args.query, args.type, args.tags, args.limit)
    else:
        print("No search criteria provided")
        return
        
    # Display results
    print(f"\nFound {len(results)} results:\n")
    for r in results:
        print(f"[{r['content_type']}] {r['title']}")
        print(f"  ID: {r['content_id']}")
        if r.get('tags'):
            print(f"  Tags: {r['tags']}")
        if r.get('summary'):
            print(f"  {r['summary'][:100]}...")
        print()
        
    searcher.close()

if __name__ == "__main__":
    main()
```

## Integration Points

### With Bulletins

```python
# When new high-value content ingested
def create_content_bulletin(content_title, content_id):
    bulletin = {
        "id": f"content-{content_id}",
        "title": f"New content: {content_title}",
        "message": f"Added to library. View with: python3 N5/content/scripts/content_search.py --id {content_id}",
        "created": datetime.now().isoformat(),
        "priority": "info",
        "active": True
    }
    # Save to bulletins/
```

### With Session State

```python
# Track content accessed during session
def log_content_access(content_id, conversation_id):
    cursor.execute("""
        INSERT INTO access_log (content_id, accessed_at, conversation_id, access_type)
        VALUES (?, ?, ?, 'reference')
    """, (content_id, datetime.now().isoformat(), conversation_id))
```

### With Records

```python
# Log content ingestion to Records
def record_ingestion(content_id, title, content_type):
    record = {
        "timestamp": datetime.now().isoformat(),
        "type": "event",
        "description": f"Content ingested: {title}",
        "metadata": {
            "content_id": content_id,
            "content_type": content_type
        }
    }
    # Append to Records/content_events.jsonl
```

## Semantic Search (Optional Phase 2)

For semantic search, integrate with embedding model:

```python
def generate_embedding(text: str) -> bytes:
    """Generate embedding vector for text"""
    # Use sentence-transformers or API
    # Example with sentence-transformers:
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # embedding = model.encode(text)
    # return embedding.tobytes()
    pass

def semantic_search(query: str, limit: int = 10):
    """Search by semantic similarity"""
    query_embedding = generate_embedding(query)
    
    # Compare with stored embeddings
    # Implementation depends on chosen similarity metric
    # Could use numpy cosine similarity or FAISS for scale
    pass
```

## Use Case Examples

### Save Article for Later
```bash
python3 N5/content/scripts/content_ingest.py \
  "https://example.com/article" \
  --tags ai research
```

### Find Notes About Project
```bash
python3 N5/content/scripts/content_search.py \
  "project X" \
  --type note \
  --limit 20
```

### Semantic Retrieval
```bash
python3 N5/content/scripts/content_search.py \
  "AI developments" \
  --recent 30
```

### Related Content Discovery
```bash
python3 N5/content/scripts/content_relate.py \
  --from abc123def456 \
  --suggest
```

## Implementation Roadmap

**Phase 1 (v0.1)**: Core infrastructure
- SQLite schema setup
- Basic ingestion (URLs, files)
- Full-text search
- Tag management

**Phase 2 (v0.2)**: Enhanced features
- Semantic search with embeddings
- Automatic relationship detection
- AI-powered summarization
- Content recommendations

**Phase 3 (v0.3)**: Advanced capabilities
- Multi-modal search
- Content versioning
- Collaborative annotations
- Export/sync with external services

## Installation

Add to `n5_install.py`:

```python
def setup_content_library(self):
    """Initialize content library"""
    content_dir = N5_ROOT / "content"
    content_dir.mkdir(exist_ok=True)
    
    # Create database
    db_path = content_dir / "library.db"
    conn = sqlite3.connect(db_path)
    
    # Execute schema SQL
    conn.executescript(SCHEMA_SQL)
    conn.close()
    
    # Create directory structure
    (content_dir / "files/articles").mkdir(parents=True, exist_ok=True)
    (content_dir / "files/pdfs").mkdir(parents=True, exist_ok=True)
    (content_dir / "files/audio").mkdir(parents=True, exist_ok=True)
    (content_dir / "files/notes").mkdir(parents=True, exist_ok=True)
```

## Next Steps

1. **Implement Phase 1** components (database, ingestion, search)
2. **Test with real content** (your articles, PDFs, transcripts)
3. **Gather feedback** on search quality and UX
4. **Iterate** based on usage patterns
5. **Add Phase 2 features** as needs emerge

---

This design balances simplicity with extensibility, aligning with N5's "Simple Over Easy" principle.
