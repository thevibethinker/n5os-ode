#!/usr/bin/env python3
"""
Content Library Ingestion Script
Add new content entries to the personal content library
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
import re
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_ingest")

LIBRARY_PATH = Path("/home/workspace/Personal/Content-Library/content-library.json")
CONTENT_DIR = Path("/home/workspace/Personal/Content-Library/content")

def ensure_content_dir():
    """Ensure content storage directory exists"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def generate_id(title: str, content_type: str) -> str:
    """Generate unique ID from title"""
    if not title:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{content_type}_{uuid.uuid4().hex[:8]}_{timestamp}"
    
    # Create slug from title
    sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    sanitized = re.sub(r'[\s]+', '-', sanitized)
    sanitized = sanitized.strip('-')[:50]
    
    if sanitized:
        return f"{content_type}_{sanitized}_{uuid.uuid4().hex[:8]}"
    else:
        return f"{content_type}_{uuid.uuid4().hex[:8]}"

def store_full_text(entry_id: str, content: str, content_type: str = "txt") -> str:
    """
    Store full text content in separate file to avoid JSON bloat
    Returns path to stored file
    """
    ensure_content_dir()
    
    # Determine file extension
    ext = "md" if content_type in ["article", "summary", "transcript"] else "txt"
    content_path = CONTENT_DIR / f"{entry_id}.{ext}"
    
    # Write content
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Stored content: {content_path}")
    return str(content_path.relative_to(CONTENT_DIR.parent))

def add_to_library(url: str, title: str, content_type: str, source_type: str, 
                   topics=None, tags=None, full_text=None, summary=None) -> dict:
    """Add entry to content library"""
    
    # Load library
    try:
        with open(LIBRARY_PATH, 'r') as f:
            library = json.load(f)
    except FileNotFoundError:
        library = {
            "metadata": {
                "version": "1.0",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "total_entries": 0,
                "last_updated": ""
            },
            "entries": {}
        }
    
    # Generate ID
    entry_id = generate_id(title, content_type)
    
    # Check if exists
    if entry_id in library['entries']:
        # Generate with UUID to ensure uniqueness
        entry_id = f"{content_type}_{uuid.uuid4().hex[:8]}"
    
    # Create provenance
    provenance = {
        "source_type": source_type,
        "platform": re.sub(r'^https?://', '', url.split('/')[2]) if url else "unknown"
    }
    
    # Create entry
    entry = {
        "id": entry_id,
        "title": title,
        "url": url,
        "content_type": content_type,
        "provenance": provenance,
        "topics": topics or [],
        "key_findings": [],
        "date_discovered": datetime.now().strftime("%Y-%m-%d"),
        "date_added": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "relationships": {
            "related_to": [],
            "referenced_in": []
        },
        "tags": tags or [],
        "confidence": 3,
        "has_content": False,
        "content_path": None,
        "has_summary": False,
        "summary_path": None
    }
    
    # Add date_created if it's V's content
    if source_type == "created":
        entry['date_created'] = entry['date_discovered']
    
    # Store full text if provided
    if full_text:
        content_path = store_full_text(entry_id, full_text, "article")
        entry['has_content'] = True
        entry['content_path'] = content_path
        entry['content_word_count'] = len(full_text.split())
    
    # Store summary if provided
    if summary:
        summary_path = store_full_text(f"{entry_id}_summary", summary, "summary")
        entry['has_summary'] = True
        entry['summary_path'] = summary_path
        entry['summary_word_count'] = len(summary.split())
    
    # Add to library
    library['entries'][entry_id] = entry
    library['metadata']['total_entries'] = len(library['entries'])
    library['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # Save
    with open(LIBRARY_PATH, 'w') as f:
        json.dump(library, f, indent=2, sort_keys=True)
    
    logger.info(f"Added entry: {entry_id}")
    return entry

def main():
    parser = argparse.ArgumentParser(description='Add content to personal content library')
    parser.add_argument('url', help='Content URL', nargs='?', default="")
    parser.add_argument('title', help='Content title')
    parser.add_argument('--type', choices=['article', 'podcast', 'video', 'social-post', 'newsletter', 'framework', 'case-study', 'quote', 'resource', 'paper', 'book'], required=True, help='Content type')
    parser.add_argument('--source', choices=['created', 'discovered'], required=True, help='Source type')
    parser.add_argument('--topics', nargs='+', help='Topics (multiple)')
    parser.add_argument('--tags', nargs='+', help='Tags (multiple)')
    parser.add_argument('--full-text', help='Path to file containing full text')
    parser.add_argument('--summary', help='Path to file containing summary')
    
    args = parser.parse_args()
    
    # Read full text if provided
    full_text_content = None
    if args.full_text:
        with open(args.full_text, 'r', encoding='utf-8') as f:
            full_text_content = f.read()
    
    # Read summary if provided
    summary_content = None
    if args.summary:
        with open(args.summary, 'r', encoding='utf-8') as f:
            summary_content = f.read()
    
    result = add_to_library(
        url=args.url,
        title=args.title,
        content_type=args.type,
        source_type=args.source,
        topics=args.topics,
        tags=args.tags,
        full_text=full_text_content,
        summary=summary_content
    )
    
    print(f"\n✓ Added: {result['id']}")
    print(f"  Title: {result['title']}")
    print(f"  Type: {result['content_type']}")
    print(f"  Source: {result['provenance']['source_type']}")
    print(f"  Content stored: {result.get('has_content', False)}")
    print(f"  Summary stored: {result.get('has_summary', False)}")
    
    if result['topics']:
        print(f"  Topics: {', '.join(result['topics'])}")

if __name__ == '__main__':
    main()

