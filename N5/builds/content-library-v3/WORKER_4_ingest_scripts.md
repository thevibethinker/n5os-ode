---
created: 2025-12-02
last_edited: 2025-12-02
version: 1
---
# Worker 4: Ingest & Enhancement Scripts

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Task ID:** W4-INGEST  
**Estimated Time:** 35 minutes  
**Dependencies:** Worker 2 (CLI/API must be complete)

---

## Mission

Update the Personal ContentLibrary ingest/enhance/summarize scripts to use the v3 schema and add the `ingest` command to the unified CLI.

---

## Context

The Personal Content Library has scripts for:
- `ingest.py` – Add new articles/assets with content storage
- `enhance.py` – Add topics, improve metadata
- `summarize.py` – Generate summaries

These need to be updated for the v3 schema.

---

## Dependencies

- Worker 2 complete: `content_library_v3.py` exists

---

## Deliverables

1. `Personal/Knowledge/ContentLibrary/scripts/ingest.py.new`
2. `Personal/Knowledge/ContentLibrary/scripts/enhance.py.new`
3. `Personal/Knowledge/ContentLibrary/scripts/summarize.py.new`
4. `Personal/Knowledge/ContentLibrary/scripts/content_to_knowledge.py.new`
5. Update to `content_library_v3.py` adding `ingest` command (or separate file)

---

## Requirements

### Ingest Flow (v3)

```bash
# Basic ingest
python3 ingest.py "https://url.com" "Title" --type article --source discovered

# With topics
python3 ingest.py "https://url.com" "Title" --type social-post --source discovered --topics AI productivity

# With full text file
python3 ingest.py "https://url.com" "Title" --type article --source created --full-text /path/to/content.md
```

### Schema Changes to Handle

**Old Personal CL schema:**
- Table: `content`
- Fields: `source_type` (the content type), `provenance` (created/discovered)

**New v3 schema:**
- Table: `items`
- Fields: `item_type` (the content type), `source_type` (created/discovered/manual/migration)

### Content Storage Path

Content files should be stored at:
```
Personal/Knowledge/ContentLibrary/content/<item_type>_<slugified_title>_<hash>.md
```

Example: `article_ben-lang-accelerators_fd280c59.md`

---

## Implementation Guide

### ingest.py.new

```python
#!/usr/bin/env python3
"""
ingest.py - Ingest new content items into Content Library v3
"""
import argparse
import hashlib
import logging
import re
import sqlite3
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
CONTENT_DIR = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content")

VALID_TYPES = [
    'article', 'social-post', 'podcast', 'video', 'book', 'paper',
    'framework', 'case-study', 'quote', 'resource', 'newsletter', 'deck'
]

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50]

def generate_id(item_type: str, title: str) -> str:
    """Generate unique ID for item"""
    slug = slugify(title)
    hash_input = f"{item_type}_{title}_{datetime.now().isoformat()}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"{item_type}_{slug}_{short_hash}"

def store_content(item_id: str, content: str) -> Path:
    """Store content to file and return path"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path = CONTENT_DIR / f"{item_id}.md"
    path.write_text(content, encoding='utf-8')
    return path

def main():
    parser = argparse.ArgumentParser(description="Ingest content into Content Library v3")
    parser.add_argument('url', nargs='?', help='URL of the content')
    parser.add_argument('title', help='Title of the content')
    parser.add_argument('--type', required=True, choices=VALID_TYPES, dest='item_type')
    parser.add_argument('--source', required=True, choices=['created', 'discovered'])
    parser.add_argument('--topics', nargs='+', default=[])
    parser.add_argument('--tags', nargs='+', default=[], help='Tags as key=value')
    parser.add_argument('--full-text', dest='full_text', help='Path to full text file')
    parser.add_argument('--summary', help='Summary text')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--platform', help='Platform (twitter, medium, etc.)')
    parser.add_argument('--notes', help='Additional notes')
    
    args = parser.parse_args()
    
    # Generate ID
    item_id = generate_id(args.item_type, args.title)
    
    # Read full text if provided
    content_path = None
    has_content = False
    if args.full_text:
        with open(args.full_text, 'r', encoding='utf-8') as f:
            content = f.read()
        content_path = store_content(item_id, content)
        has_content = True
        logging.info(f"Stored content: {content_path}")
    
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()
    
    # Insert item
    conn.execute("""
        INSERT INTO items (id, item_type, title, url, content_path, source_type,
                           platform, author, created_at, updated_at, has_content,
                           notes, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
    """, (
        item_id,
        args.item_type,
        args.title,
        args.url,
        str(content_path) if content_path else None,
        args.source,
        args.platform,
        args.author,
        now,
        now,
        1 if has_content else 0,
        args.notes
    ))
    
    # Add topics
    for topic_name in args.topics:
        conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
        topic_id = conn.execute("SELECT id FROM topics WHERE name = ?", (topic_name,)).fetchone()[0]
        conn.execute("INSERT INTO item_topics (item_id, topic_id) VALUES (?, ?)", (item_id, topic_id))
    
    # Add tags
    for tag in args.tags:
        if '=' in tag:
            key, value = tag.split('=', 1)
            conn.execute("INSERT INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                        (item_id, key, value))
    
    conn.commit()
    conn.close()
    
    logging.info(f"Added entry: {item_id}")
    
    print(f"\n✓ Added: {item_id}")
    print(f"  Title: {args.title}")
    print(f"  Type: {args.item_type}")
    print(f"  Source: {args.source}")
    print(f"  Content stored: {has_content}")
    print(f"  Topics: {', '.join(args.topics) if args.topics else 'none'}")

if __name__ == "__main__":
    main()
```

### enhance.py.new

```python
#!/usr/bin/env python3
"""
enhance.py - Enhance content items with topics, tags, metadata
"""
import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")

def main():
    parser = argparse.ArgumentParser(description="Enhance content item")
    parser.add_argument('id', help='Item ID to enhance')
    parser.add_argument('--add-topic', action='append', dest='topics', default=[])
    parser.add_argument('--add-tag', action='append', dest='tags', default=[], help='key=value')
    parser.add_argument('--set-confidence', type=int, choices=[1,2,3,4,5])
    parser.add_argument('--set-notes', dest='notes')
    
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    # Check item exists
    if not conn.execute("SELECT 1 FROM items WHERE id = ?", (args.id,)).fetchone():
        print(f"Error: Item '{args.id}' not found")
        return 1
    
    # Add topics
    for topic_name in args.topics:
        conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
        topic_id = conn.execute("SELECT id FROM topics WHERE name = ?", (topic_name,)).fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO item_topics (item_id, topic_id) VALUES (?, ?)",
                    (args.id, topic_id))
        print(f"Added topic: {topic_name}")
    
    # Add tags
    for tag in args.tags:
        if '=' in tag:
            key, value = tag.split('=', 1)
            conn.execute("INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                        (args.id, key, value))
            print(f"Added tag: {key}={value}")
    
    # Update fields
    updates = []
    params = []
    if args.set_confidence:
        updates.append("confidence = ?")
        params.append(args.set_confidence)
    if args.notes:
        updates.append("notes = ?")
        params.append(args.notes)
    
    if updates:
        params.append(args.id)
        conn.execute(f"UPDATE items SET {', '.join(updates)} WHERE id = ?", params)
        print(f"Updated metadata")
    
    conn.commit()
    conn.close()
    print(f"✓ Enhanced: {args.id}")

if __name__ == "__main__":
    main()
```

---

## Testing

```bash
# Test ingest
python3 ingest.py.new "https://test.com" "Test Article" --type article --source discovered --topics test AI

# Verify in DB
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db \
  "SELECT id, title, item_type FROM items WHERE id LIKE '%test-article%';"

# Test enhance
python3 enhance.py.new <item_id> --add-topic productivity --set-confidence 4

# Verify topics
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db \
  "SELECT t.name FROM topics t JOIN item_topics it ON t.id = it.topic_id WHERE it.item_id = '<item_id>';"
```

---

## Report Back

When complete, report:
1. ✅ List of `.new` files created
2. ✅ Test ingest working
3. ✅ Test enhance working
4. ✅ Any schema issues discovered
5. ✅ Ready for cutover

---

**Orchestrator Contact:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 22:04 ET

