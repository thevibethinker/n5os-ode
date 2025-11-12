#!/usr/bin/env python3
"""
Worker: worker_ingest_raw
Task: Build universal ingestion for raw materials
Dependencies: worker_schema, worker_settings
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys
import shutil
import requests
from urllib.parse import urlparse
import re

# Add path to import settings
sys.path.insert(0, '/home/workspace/N5/workers')
import worker_settings

DB_PATH = Path("/home/workspace/Personal/Content-Library/content-library.db")
SETTINGS_PATH = Path("/home/workspace/Personal/Content-Library/settings.json")

def load_settings():
    """Load system settings"""
    with open(SETTINGS_PATH) as f:
        return json.load(f)

def generate_id(entry_type, date_str=None):
    """Generate ID in format: {type}_{YYYYMMDD}_{random_4}"""
    import uuid
    date = date_str or datetime.now().strftime("%Y%m%d")
    random = uuid.uuid4().hex[:4]
    return f"{entry_type}_{date}_{random}"

def is_url(path):
    """Check if path is a URL"""
    return bool(urlparse(path).scheme)

def download_content(url, entry_type):
    """Download remote content and return local path"""
    settings = load_settings()
    download_dir = Path(settings["download_mapping"].get(entry_type, settings["download_mapping"]["default"])).expanduser()
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from URL
    parsed = urlparse(url)
    filename = Path(parsed.path).name or f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not filename.endswith('.md'):
        filename += '.md'
    
    local_path = download_dir / filename
    
    # Download content
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Content-Library-Bot/1.0)'}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Save to file
    local_path.write_text(response.text)
    
    return str(local_path), filename

def detect_entry_type(file_path):
    """Detect entry type from file path"""
    path = Path(file_path)
    
    if "Meetings" in str(path):
        return "meeting"
    elif "Articles" in str(path):
        if ".web" in str(path):
            return "article_web"
        else:
            return "article"
    elif "Notes" in str(path):
        return "note"
    elif "Media" in str(path):
        return "media"
    elif "email" in str(path).lower():
        return "email"
    else:
        return "raw_material"

def ingest_raw(file_path, title=None, topics=None, tags=None, confidence=None):
    """
    Ingest a raw material into Content Library
    
    Args:
        file_path: Path to file or URL
        title: Title (auto-detected if None)
        topics: List of topics
        tags: List of tags
        confidence: Confidence score 1-5
    """
    
    settings = load_settings()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Handle URLs
    local_path = None
    url = None
    if is_url(file_path):
        url = file_path
        local_path, filename = download_content(url, detect_entry_type(url))
        path_to_store = local_path
        title = title or Path(filename).stem
    else:
        path_to_store = str(Path(file_path).resolve())
        title = title or Path(file_path).stem
    
    # Detect entry type
    entry_type = detect_entry_type(path_to_store)
    
    # Generate ID
    content_id = generate_id(entry_type)
    
    # Insert into database
    cursor.execute("""
        INSERT INTO content (
            id, source_type, title, file_path, url, date_created, 
            date_ingested, confidence, topics, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        content_id,
        entry_type,
        title,
        path_to_store,
        url,
        Path(path_to_store).stat().st_mtime if not url else None,
        datetime.now().isoformat(),
        confidence or settings["ingestion_rules"]["default_confidence"],
        json.dumps(topics or []),
        json.dumps(tags or [])
    ))
    
    # Insert topics
    for topic in (topics or []):
        # Insert topic if not exists
        cursor.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic,))
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic,))
        topic_id = cursor.fetchone()[0]
        cursor.execute("INSERT OR IGNORE INTO content_topics (content_id, topic_id) VALUES (?, ?)", (content_id, topic_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "content_id": content_id,
        "title": title,
        "type": entry_type,
        "file_path": path_to_store
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest raw materials into Content Library')
    parser.add_argument('file_path', help='Path to file or URL to ingest')
    parser.add_argument('--title', help='Title (auto-detected if not provided)')
    parser.add_argument('--topics', nargs='+', help='List of topics')
    parser.add_argument('--tags', nargs='+', help='List of tags')
    parser.add_argument('--confidence', type=int, choices=range(1, 6), 
                       help='Confidence score 1-5')
    
    args = parser.parse_args()
    
    result = ingest_raw(
        args.file_path,
        title=args.title,
        topics=args.topics,
        tags=args.tags,
        confidence=args.confidence
    )
    
    if result['success']:
        print(f"✓ Ingested: {result['content_id']}")
        print(f"  Title: {result['title']}")
        print(f"  Type: {result['type']}")
        print(f"  Path: {result['file_path']}")
    else:
        print(f"✗ Failed to ingest: {result.get('error', 'Unknown error')}")
        sys.exit(1)


