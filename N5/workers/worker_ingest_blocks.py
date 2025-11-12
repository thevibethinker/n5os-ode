#!/usr/bin/env python3
"""
Worker: worker_ingest_blocks
Task: Build block ingestion from existing B-block files
Dependencies: worker_schema, worker_settings
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys
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

def extract_block_info(file_path):
    """Extract block info from B-block file path"""
    path = Path(file_path)
    
    # Extract block code from filename (e.g., B01, B02, B31)
    match = re.search(r'(B\d{2})', path.name)
    block_code = match.group(1) if match else "UNKNOWN"
    
    # Extract date from parent folder (e.g., 2025-09-08)
    parent = path.parent
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(parent))
    date_str = date_match.group(1) if date_match else "unknown"
    
    # Generate block ID
    import uuid
    block_id = f"block_{date_str}_{block_code}_{uuid.uuid4().hex[:4]}"
    
    # Generate content ID for parent material
    content_id = f"mt_{date_str}_{uuid.uuid4().hex[:8]}"
    
    return {
        "block_id": block_id,
        "content_id": content_id,
        "block_code": block_code,
        "date": date_str,
        "file_path": str(path)
    }

def detect_block_type(block_code, content):
    """Detect block type from code and content"""
    block_type_mapping = {
        "B01": "detailed_recap",
        "B02": "commitments_context",
        "B08": "stakeholder_intelligence",
        "B21": "key_moments",
        "B25": "deliverable_content",
        "B26": "meeting_metadata",
        "B31": "stakeholder_research"
    }
    
    # Try to detect from content if code is unknown
    content_lower = content.lower()
    
    if "http" in content or "www." in content:
        return "resource"
    elif "?" in content[:100]:
        return "question"
    elif block_code in block_type_mapping:
        return block_type_mapping[block_code]
    elif "will" in content_lower or "shall" in content_lower:
        return "action"
    elif "" in content_lower:
        return "insight"
    else:
        return "note"

def ingest_block(file_path, topics=None, tags=None, confidence=None):
    """
    Ingest a B-block file into Content Library
    
    Args:
        file_path: Path to B-block file
        topics: List of topics to apply
        tags: List of tags to apply
        confidence: Confidence score
    """
    
    settings = load_settings()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read block file
    block_file = Path(file_path)
    if not block_file.exists():
        raise FileNotFoundError(f"Block file not found: {file_path}")
    
    content = block_file.read_text()
    
    # Extract block info
    block_info = extract_block_info(file_path)
    
    # Detect block type
    block_type = detect_block_type(block_info["block_code"], content)
    
    # Insert parent content if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO content (id, source_type, title, file_path, date_created)
        VALUES (?, ?, ?, ?, ?)
    """, (
        block_info["content_id"],
        "meeting",
        f"Meeting from {block_info['date']}",
        str(block_file.parent / "transcript_source.md"),
        block_info["date"]
    ))
    
    # Insert block
    cursor.execute("""
        INSERT INTO blocks (
            id, content_id, block_code, block_type, content, file_path,
            extracted_at, confidence, topics, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        block_info["block_id"],
        block_info["content_id"],
        block_info["block_code"],
        block_type,
        content,
        str(file_path),
        datetime.now().isoformat(),
        confidence or settings["ingestion_rules"]["default_confidence"],
        json.dumps(topics or []),
        json.dumps(tags or [])
    ))
    
    # Insert topics
    for topic in (topics or []):
        cursor.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic,))
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic,))
        topic_id = cursor.fetchone()[0]
        cursor.execute("INSERT OR IGNORE INTO block_topics (block_id, topic_id) VALUES (?, ?)", (block_info["block_id"], topic_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "block_id": block_info["block_id"],
        "content_id": block_info["content_id"],
        "block_code": block_info["block_code"],
        "type": block_type
    }

def batch_ingest_blocks(folder_path, topics=None, tags=None):
    """Ingest all B-block files in a folder"""
    
    folder = Path(folder_path)
    results = []
    
    # Find all B-block files
    block_files = list(folder.glob("B*.md"))
    
    for block_file in block_files:
        try:
            result = ingest_block(
                str(block_file),
                topics=topics,
                tags=tags
            )
            results.append(result)
            print(f"✓ Ingested: {result['block_id']}")
        except Exception as e:
            print(f"✗ Failed {block_file.name}: {e}")
    
    return {
        "success": True,
        "ingested_count": len(results),
        "blocks": results
    }

if __name__ == "__main__":
    # Test batch ingestion
    test_folder = "/home/workspace/N5/records/meetings/2025-09-08_Daniel-Williams_INTERNAL/"
    
    if Path(test_folder).exists():
        result = batch_ingest_blocks(
            test_folder,
            topics=["hiring", "strategy", "internal"],
            tags=["batch_ingest", "test"]
        )
        print(f"\n✓ Batch complete: {result['ingested_count']} blocks ingested")
    else:
        print(f"✗ Test folder not found: {test_folder}")
        print("  Run with: python3 worker_ingest_blocks.py <folder_path>")

