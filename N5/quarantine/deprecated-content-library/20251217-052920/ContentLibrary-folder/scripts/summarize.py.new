#!/usr/bin/env python3
"""
summarize.py.new - Generate and optionally store summaries for Content Library v3 items.

This script is intentionally deterministic and LLM-free. It:
- Loads item content from the v3 SQLite database (inline or content_path)
- Builds a simple summary from the first N words
- Optionally writes the summary back to the DB and marks has_summary=1
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from content_library_v3 import ContentLibraryV3

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_v3_summarize")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")


def _strip_frontmatter(text: str) -> str:
    """Remove leading YAML frontmatter if present.

    Looks for a leading '---' line and the next '---' line, and strips
    everything up to and including that block.
    """

    lines = text.splitlines()
    if not lines:
        return text
    if lines[0].strip() != "---":
        return text

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return text

    # Drop frontmatter and any single blank line that immediately follows
    body_lines = lines[end_idx + 1 :]
    if body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]
    return "\n".join(body_lines)


def _load_content_for_item(item: dict) -> str:
    """Return text content for an item or raise ValueError if none available."""

    # Prefer inline content if present
    content = item.get("content")
    if content:
        return str(content)

    content_path = item.get("content_path")
    if not content_path:
        raise ValueError("Item has no content or content_path set")

    path = Path(content_path)
    if not path.is_absolute():
        # Fall back to treating it as absolute relative to workspace root
        path = Path("/home/workspace") / path

    if not path.exists():
        raise FileNotFoundError(f"Content file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    return _strip_frontmatter(raw)


def _make_summary(text: str, max_words: int) -> str:
    """Create a naive summary by truncating to the first N words."""

    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    truncated = " ".join(words[:max_words]).strip()
    return truncated + " …"  # indicate truncation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a simple summary for a Content Library v3 item",
    )
    parser.add_argument("id", help="Item ID to summarize")
    parser.add_argument(
        "--max-words",
        type=int,
        default=200,
        help="Maximum words in summary (default: 200)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist summary back to DB and set has_summary=1",
    )

    args = parser.parse_args()

    lib = ContentLibraryV3(DB_PATH)
    item = lib.get(args.id)
    if not item:
        print(f"Error: Item '{args.id}' not found")
        return 1

    try:
        content = _load_content_for_item(item)
    except Exception as exc:  # noqa: BLE001 - top-level CLI
        logger.error("Unable to load content for %s: %s", args.id, exc)
        print(f"Error: unable to load content for '{args.id}': {exc}")
        return 1

    word_count = len(content.split())
    summary = _make_summary(content, max_words=args.max_words)

    print(f"Generated summary for {args.id} (source words: {word_count})")
    print("=" * 60)
    print(summary)

    if args.save:
        update_fields = {
            "summary": summary,
            "has_summary": 1,
            "word_count": word_count,
        }
        updated = lib.update(args.id, **update_fields)
        if not updated:
            print(f"Error: failed to update item '{args.id}' with summary")
            return 1
        print("\n✓ Summary saved to DB (has_summary=1, word_count updated)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


