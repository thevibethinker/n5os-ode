#!/usr/bin/env python3
"""
Content Library Ingest Script
Ingests content files into the N5 Content Library database.

Usage:
    python3 N5/scripts/content_ingest.py /path/to/article.md --type article
    python3 N5/scripts/content_ingest.py /path/to/file.md --dry-run
    python3 N5/scripts/content_ingest.py /path/to/file.md --move

Part of Content Library v4.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path("/home/workspace")
DB_PATH = WORKSPACE_ROOT / "N5/data/content_library.db"
CANONICAL_ROOT = WORKSPACE_ROOT / "Knowledge/content-library"
LOG_ROOT = WORKSPACE_ROOT / "N5/runtime/runs/content-ingest"

# Content type mappings
TYPE_DIRECTORIES = {
    "article": "articles",
    "deck": "decks",
    "paper": "papers",
    "book": "books",
    "framework": "frameworks",
    "social-post": "social-posts",
    "inspiration": "inspiration",
}

# Path patterns for auto-detection
PATH_TYPE_PATTERNS = [
    (r"/articles/", "article"),
    (r"/decks/", "deck"),
    (r"/papers/", "paper"),
    (r"/books/", "book"),
    (r"/frameworks/", "framework"),
    (r"/social-posts/", "social-post"),
    (r"/inspiration/", "inspiration"),
]


def setup_logging(dry_run: bool = False) -> Path:
    """Create log directory and return log file path."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_ROOT / today
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S")
    suffix = "_dry-run" if dry_run else ""
    log_file = log_dir / f"ingest_{timestamp}{suffix}.json"
    return log_file


def log_result(log_file: Path, result: dict):
    """Append result to log file."""
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_block = parts[1].strip()
            body = parts[2].strip()
            
            # Simple YAML parsing (key: value)
            for line in yaml_block.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        frontmatter[key] = value
    
    return frontmatter, body


def extract_title_from_filename(filepath: Path) -> str:
    """Generate title from filename."""
    name = filepath.stem
    # Remove common suffixes like " :: domain.com"
    if " :: " in name:
        name = name.split(" :: ")[0]
    # Clean up
    name = name.replace("-", " ").replace("_", " ")
    return name.strip()


def count_words(content: str) -> int:
    """Count words in text content."""
    # Remove markdown formatting
    text = re.sub(r"[#*`\[\]()>]", " ", content)
    words = text.split()
    return len(words)


def detect_content_type(filepath: Path) -> str:
    """Auto-detect content type from file path."""
    path_str = str(filepath)
    
    for pattern, content_type in PATH_TYPE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return content_type
    
    # Extension-based fallback
    ext = filepath.suffix.lower()
    if ext == ".pdf":
        return "deck"
    
    return "article"  # Default


def get_relative_path(filepath: Path) -> str:
    """Get path relative to workspace root."""
    try:
        return str(filepath.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(filepath)


def get_canonical_path(content_type: str, filename: str) -> Path:
    """Get canonical storage path for content type."""
    subdir = TYPE_DIRECTORIES.get(content_type, "articles")
    return CANONICAL_ROOT / subdir / filename


def record_exists(conn: sqlite3.Connection, source_file_path: str) -> bool:
    """Check if a record with this source_file_path already exists."""
    cursor = conn.execute(
        "SELECT id FROM items WHERE source_file_path = ?",
        (source_file_path,)
    )
    return cursor.fetchone() is not None


def create_record(
    conn: sqlite3.Connection,
    title: str,
    content_type: str,
    source_file_path: str,
    content: str = None,
    tags: str = None,
    word_count: int = None,
) -> str:
    """Create a new content library record."""
    record_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO items (
            id, title, content_type, content, source_file_path,
            tags, word_count, ingested_at, created_at, updated_at,
            has_content
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id,
        title,
        content_type,
        content,
        source_file_path,
        tags,
        word_count,
        now,
        now,
        now,
        1 if content else 0,
    ))
    conn.commit()
    
    return record_id


def ingest_file(
    filepath: Path,
    content_type: str = None,
    dry_run: bool = False,
    move: bool = False,
    tags: list[str] = None,
) -> dict:
    """
    Ingest a single file into the Content Library.
    
    Returns dict with result details.
    """
    result = {
        "file": str(filepath),
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
    }
    
    # Validate file exists
    if not filepath.exists():
        result["status"] = "error"
        result["error"] = f"File not found: {filepath}"
        return result
    
    # Auto-detect content type if not specified
    if content_type is None:
        content_type = detect_content_type(filepath)
    result["content_type"] = content_type
    
    # Read file content
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Failed to read file: {e}"
        return result
    
    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)
    
    # Extract metadata
    title = frontmatter.get("title") or extract_title_from_filename(filepath)
    result["title"] = title
    
    # Tags from frontmatter + additional tags
    file_tags = frontmatter.get("tags", "")
    if tags:
        all_tags = set(file_tags.split(",") if file_tags else [])
        all_tags.update(tags)
        file_tags = ",".join(sorted(t.strip() for t in all_tags if t.strip()))
    result["tags"] = file_tags
    
    # Word count
    word_count = count_words(body)
    result["word_count"] = word_count
    
    # Determine final path
    current_path = get_relative_path(filepath)
    result["source_file_path"] = current_path
    
    if move:
        canonical = get_canonical_path(content_type, filepath.name)
        new_path = get_relative_path(canonical)
        result["target_path"] = new_path
    
    if dry_run:
        result["status"] = "dry_run"
        result["action"] = "would_create"
        return result
    
    # Database operations
    conn = sqlite3.connect(DB_PATH)
    try:
        # Check for existing record
        if record_exists(conn, current_path):
            result["status"] = "skipped"
            result["reason"] = "record_exists"
            return result
        
        # Move file if requested
        if move:
            canonical = get_canonical_path(content_type, filepath.name)
            if filepath != canonical:
                canonical.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(filepath), str(canonical))
                current_path = get_relative_path(canonical)
                result["moved_to"] = current_path
        
        # Create record
        record_id = create_record(
            conn=conn,
            title=title,
            content_type=content_type,
            source_file_path=current_path,
            content=body[:10000] if body else None,  # Store first 10k chars
            tags=file_tags,
            word_count=word_count,
        )
        
        result["status"] = "created"
        result["record_id"] = record_id
        
    finally:
        conn.close()
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Ingest content files into the Content Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s article.md --type article
  %(prog)s deck.pdf --type deck --dry-run
  %(prog)s file.md --move
  %(prog)s file.md --tags "vrijen-authored,medium"
        """
    )
    
    parser.add_argument(
        "file",
        type=Path,
        help="Path to file to ingest"
    )
    parser.add_argument(
        "--type", "-t",
        dest="content_type",
        choices=["article", "deck", "paper", "book", "framework", "social-post", 
                 "inspiration", "link", "snippet", "podcast", "video", "quote"],
        help="Content type (auto-detected if not specified)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--move", "-m",
        action="store_true",
        help="Move file to canonical location"
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated tags to add"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    
    args = parser.parse_args()
    
    # Resolve path
    filepath = args.file.resolve()
    if not filepath.is_absolute():
        filepath = (WORKSPACE_ROOT / args.file).resolve()
    
    # Parse tags
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]
    
    # Setup logging
    log_file = setup_logging(args.dry_run)
    
    # Ingest
    result = ingest_file(
        filepath=filepath,
        content_type=args.content_type,
        dry_run=args.dry_run,
        move=args.move,
        tags=tags,
    )
    
    # Log result
    log_result(log_file, result)
    
    # Output
    if not args.quiet:
        if result["status"] == "error":
            print(f"❌ Error: {result['error']}")
            exit(1)
        elif result["status"] == "skipped":
            print(f"⏭️  Skipped: {result['file']} (already exists)")
        elif result["status"] == "dry_run":
            print(f"🔍 Dry run: Would create record for '{result['title']}'")
            print(f"   Type: {result['content_type']}")
            print(f"   Words: {result['word_count']}")
            if result.get("target_path"):
                print(f"   Would move to: {result['target_path']}")
        else:
            print(f"✅ Created: '{result['title']}'")
            print(f"   ID: {result['record_id']}")
            print(f"   Type: {result['content_type']}")
            if result.get("moved_to"):
                print(f"   Moved to: {result['moved_to']}")
    
    # Return result as JSON for programmatic use
    if args.quiet:
        print(json.dumps(result))


if __name__ == "__main__":
    main()


