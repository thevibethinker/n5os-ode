#!/usr/bin/env python3
"""
ingest.py.new - Ingest new content items into Content Library v3.

This script is a thin CLI wrapper around the ContentLibraryV3 API that:
- Generates a stable item ID based on type + title
- Optionally stores full-text content to the canonical content directory
- Inserts the item into the v3 SQLite database with topics and tags
"""

import argparse
import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from content_library_v3 import ContentLibraryV3

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_v3_ingest")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
CONTENT_DIR = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content")

VALID_TYPES: List[str] = [
    "article",
    "social-post",
    "podcast",
    "video",
    "book",
    "paper",
    "framework",
    "case-study",
    "quote",
    "resource",
    "newsletter",
    "deck",
]


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug (conservative, max 50 chars)."""

    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:50]


def generate_id(item_type: str, title: str) -> str:
    """Generate a unique ID of the form <type>_<slug>_<hash>.

    This matches the canonical content file naming pattern:
    <item_type>_<slugified_title>_<hash>.md
    """

    slug = slugify(title)
    hash_input = f"{item_type}_{title}_{datetime.now().isoformat()}"
    short_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:8]
    return f"{item_type}_{slug}_{short_hash}"


def store_content(item_id: str, content: str) -> Path:
    """Store content to a Markdown file and return the absolute path.

    New .md files include YAML frontmatter for created/last_edited/version.
    """

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path = CONTENT_DIR / f"{item_id}.md"

    today = datetime.now().date().isoformat()
    header = (
        "---\n"
        f"created: {today}\n"
        f"last_edited: {today}\n"
        "version: 1.0\n"
        "---\n\n"
    )

    path.write_text(header + content, encoding="utf-8")
    logger.info("Stored content at %s", path)
    return path


def parse_tags(raw_tags: Optional[List[str]]) -> Optional[Dict[str, str]]:
    """Parse ['key=value', ...] into a dict suitable for ContentLibraryV3.add."""

    if not raw_tags:
        return None

    tags: Dict[str, str] = {}
    for tag in raw_tags:
        if "=" not in tag:
            logger.warning("Ignoring malformed tag (expected key=value): %s", tag)
            continue
        key, value = tag.split("=", 1)
        tags[key] = value
    return tags or None


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest content into Content Library v3")
    parser.add_argument("url", nargs="?", help="URL of the content")
    parser.add_argument("title", help="Title of the content")
    parser.add_argument("--type", required=True, choices=VALID_TYPES, dest="item_type")
    parser.add_argument(
        "--source",
        required=True,
        choices=["created", "discovered"],
        help="Provenance of the item",
    )
    parser.add_argument("--topics", nargs="+", default=[], help="Topics to associate")
    parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags as key=value (space-separated)",
    )
    parser.add_argument(
        "--full-text",
        dest="full_text",
        help="Path to full text file (Markdown or text)",
    )
    parser.add_argument("--summary", help="Optional summary text to store on the item")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--platform", help="Platform (twitter, medium, etc.)")
    parser.add_argument("--notes", help="Additional notes")

    args = parser.parse_args()

    lib = ContentLibraryV3(DB_PATH)

    # Generate ID
    item_id = generate_id(args.item_type, args.title)

    # Read full text if provided
    content_path: Optional[Path] = None
    has_content = False
    word_count: Optional[int] = None

    if args.full_text:
        full_path = Path(args.full_text)
        if not full_path.exists():
            raise FileNotFoundError(f"Full text file not found: {full_path}")

        content = full_path.read_text(encoding="utf-8")
        word_count = len(content.split())
        content_path = store_content(item_id, content)
        has_content = True

    tags = parse_tags(args.tags)
    topics = args.topics or []

    # Insert item via unified API
    item = lib.add(
        id=item_id,
        item_type=args.item_type,
        title=args.title,
        url=args.url,
        content=None,
        content_path=str(content_path) if content_path else None,
        source_type=args.source,
        platform=args.platform,
        author=args.author,
        tags=tags,
        topics=topics,
        notes=args.notes,
    )

    # Update asset flags if we stored content / summary
    update_fields = {}
    if has_content:
        update_fields["has_content"] = 1
        if word_count is not None:
            update_fields["word_count"] = word_count
    if args.summary:
        update_fields["summary"] = args.summary
        update_fields["has_summary"] = 1

    if update_fields:
        lib.update(item_id, **update_fields)

    print(f"\n✓ Added: {item_id}")
    print(f"  Title: {args.title}")
    print(f"  Type: {args.item_type}")
    print(f"  Source: {args.source}")
    print(f"  Content stored: {has_content}")
    print(f"  Topics: {', '.join(topics) if topics else 'none'}")


if __name__ == "__main__":
    main()

