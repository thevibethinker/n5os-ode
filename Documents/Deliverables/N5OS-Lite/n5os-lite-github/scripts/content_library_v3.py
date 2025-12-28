#!/usr/bin/env python3
"""
content_library_v3.py - Unified Content Library v3 CLI & Python API

Supports: links, snippets, articles, decks, social-posts, podcasts, etc.

Database: /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db
Content dir: /home/workspace/Personal/Knowledge/ContentLibrary/content
"""

import argparse
import json
import logging
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error as urlerror
from urllib import request as urlrequest

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
CONTENT_DIR = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content")


@dataclass
class ExportResult:
    format: str
    item_type: Optional[str]
    count: int
    payload: str


class ContentLibraryV3:
    """Unified Content Library v3 API.

    This class provides a Python interface over the v3 unified schema defined in
    file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    # --- Internal helpers -------------------------------------------------

    def _ensure_db(self) -> None:
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_tags(self, conn: sqlite3.Connection, item_id: str) -> Dict[str, List[str]]:
        cursor = conn.execute(
            "SELECT tag_key, tag_value FROM tags WHERE item_id = ?",
            (item_id,),
        )
        tags: Dict[str, List[str]] = {}
        for row in cursor:
            tags.setdefault(row["tag_key"], []).append(row["tag_value"])
        return tags

    def _get_topics(self, conn: sqlite3.Connection, item_id: str) -> List[str]:
        cursor = conn.execute(
            """
            SELECT t.name
            FROM topics t
            JOIN item_topics it ON t.id = it.topic_id
            WHERE it.item_id = ?
            """,
            (item_id,),
        )
        return [row["name"] for row in cursor]

    # --- Public API: core operations --------------------------------------

    def search(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        topics: Optional[List[str]] = None,
        include_deprecated: bool = False,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search items by query, type, tags, or topics.

        Mirrors the unified search behaviour required by the worker spec.
        """

        conn = self._connect()

        sql = "SELECT DISTINCT i.* FROM items i"
        joins: List[str] = []
        conditions: List[str] = []
        params: List[Any] = []

        # Join tags if filtering by tag
        if tags:
            for i, (key, value) in enumerate(tags.items()):
                alias = f"t{i}"
                joins.append(f"JOIN tags {alias} ON i.id = {alias}.item_id")
                conditions.append(f"{alias}.tag_key = ? AND {alias}.tag_value = ?")
                params.extend([key, value])

        # Join topics if filtering by topic
        if topics:
            joins.append("JOIN item_topics it ON i.id = it.item_id")
            joins.append("JOIN topics tp ON it.topic_id = tp.id")
            placeholders = ",".join("?" * len(topics))
            conditions.append(f"tp.name IN ({placeholders})")
            params.extend(topics)

        # Text search
        if query:
            conditions.append("(i.title LIKE ? OR i.content LIKE ? OR i.url LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])

        # Type filter
        if item_type:
            conditions.append("i.item_type = ?")
            params.append(item_type)

        # Deprecated filter
        if not include_deprecated:
            conditions.append("i.deprecated = 0")

        # Build query
        if joins:
            sql += " " + " ".join(joins)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += f" ORDER BY i.updated_at DESC LIMIT {int(limit)}"

        cursor = conn.execute(sql, params)
        results: List[Dict[str, Any]] = []
        for row in cursor:
            item = dict(row)
            item_id = item["id"]
            # Add tags
            item["tags"] = self._get_tags(conn, item_id)
            # Add topics
            item["topics"] = self._get_topics(conn, item_id)
            results.append(item)

        conn.close()
        return results

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item by ID."""

        conn = self._connect()
        cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        item = dict(row)
        item["tags"] = self._get_tags(conn, item_id)
        item["topics"] = self._get_topics(conn, item_id)
        conn.close()
        return item

    def add(
        self,
        id: str,
        item_type: str,
        title: str,
        url: Optional[str] = None,
        content: Optional[str] = None,
        content_path: Optional[str] = None,
        source_type: str = "manual",
        platform: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        topics: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new item.

        This is the main entry for creating items programmatically.
        """

        conn = self._connect()
        now = datetime.now().isoformat()

        conn.execute(
            """
            INSERT INTO items (
                id, item_type, title, url, content, content_path,
                source_type, platform, author,
                created_at, updated_at,
                notes, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
            """,
            (
                id,
                item_type,
                title,
                url,
                content,
                content_path,
                source_type,
                platform,
                author,
                now,
                now,
                notes,
            ),
        )

        # Add tags
        if tags:
            for key, value in tags.items():
                conn.execute(
                    "INSERT INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                    (id, key, value),
                )

        # Add topics
        if topics:
            for topic_name in topics:
                conn.execute(
                    "INSERT OR IGNORE INTO topics (name) VALUES (?)",
                    (topic_name,),
                )
                topic_id_row = conn.execute(
                    "SELECT id FROM topics WHERE name = ?",
                    (topic_name,),
                ).fetchone()
                if topic_id_row is None:
                    continue
                topic_id = topic_id_row[0]
                conn.execute(
                    "INSERT OR IGNORE INTO item_topics (item_id, topic_id) VALUES (?, ?)",
                    (id, topic_id),
                )

        conn.commit()
        conn.close()

        logger.info("Added item: %s", id)
        result = self.get(id)
        assert result is not None
        return result

    def update(self, item_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        """Update item fields.

        Only a safe subset of fields is allowed to be updated.
        """

        conn = self._connect()

        # Check exists
        row = conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            conn.close()
            return None

        allowed = [
            "title",
            "url",
            "content",
            "content_path",
            "summary",
            "summary_path",
            "platform",
            "author",
            "notes",
            "deprecated",
            "expires_at",
            "word_count",
            "has_content",
            "has_summary",
        ]

        updates: List[str] = []
        params: List[Any] = []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                params.append(value)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(item_id)

            conn.execute(
                f"UPDATE items SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            conn.commit()

        conn.close()
        logger.info("Updated item: %s", item_id)
        return self.get(item_id)

    def deprecate(self, item_id: str) -> bool:
        """Mark item as deprecated."""

        updated = self.update(item_id, deprecated=1)
        return updated is not None

    def mark_used(self, item_id: str) -> bool:
        """Update last_used_at timestamp."""

        conn = self._connect()
        conn.execute(
            "UPDATE items SET last_used_at = ? WHERE id = ?",
            (datetime.now().isoformat(), item_id),
        )
        conn.commit()
        conn.close()
        return True

    def stats(self) -> Dict[str, Any]:
        """Get library statistics.

        Returns counts by type, source, etc.
        """

        conn = self._connect()

        stats: Dict[str, Any] = {
            "total": conn.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            "by_type": {},
            "by_source": {},
            "topics": conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0],
            "tags": conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0],
            "deprecated": conn.execute(
                "SELECT COUNT(*) FROM items WHERE deprecated = 1",
            ).fetchone()[0],
        }

        for row in conn.execute(
            "SELECT item_type, COUNT(*) AS c FROM items GROUP BY item_type",
        ):
            stats["by_type"][row["item_type"]] = row["c"]

        for row in conn.execute("SELECT source, COUNT(*) AS c FROM items GROUP BY source"):
            stats["by_source"][row["source"]] = row["c"]

        conn.close()
        return stats

    def lint(self) -> List[Dict[str, Any]]:
        """Check for quality issues.

        Currently checks for JS shell content and missing content files.
        """

        issues: List[Dict[str, Any]] = []
        conn = self._connect()

        # Check for JS shell content
        js_shell_markers = [
            "JavaScript is not available",
            "enable JavaScript",
        ]
        for marker in js_shell_markers:
            cursor = conn.execute(
                "SELECT id, title FROM items WHERE content LIKE ?",
                (f"%{marker}%",),
            )
            for row in cursor:
                issues.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "issue": "JS shell content detected",
                    }
                )

        # Check content files exist
        cursor = conn.execute(
            "SELECT id, title, content_path FROM items WHERE content_path IS NOT NULL",
        )
        for row in cursor:
            content_path = row["content_path"]
            if content_path and not Path(content_path).exists():
                issues.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "issue": f"Content file missing: {content_path}",
                    }
                )

        conn.close()
        return issues

    # --- Ingest / assets --------------------------------------------------

    def _slugify(self, text: str) -> str:
        """Create a simple slug from text suitable for an ID.

        This is intentionally conservative to avoid surprises.
        """

        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-") or "item"

    def _ensure_unique_id(self, base_id: str, conn: sqlite3.Connection) -> str:
        """Ensure the ID is unique in the items table."""

        candidate = base_id
        suffix = 1
        while True:
            row = conn.execute(
                "SELECT 1 FROM items WHERE id = ?",
                (candidate,),
            ).fetchone()
            if not row:
                return candidate
            suffix += 1
            candidate = f"{base_id}-{suffix}"

    def ingest(
        self,
        url: str,
        item_type: str,
        title: str,
        source_type: str = "discovered",
        id: Optional[str] = None,
        platform: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        topics: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ingest an asset (e.g. article) by downloading and storing its content.

        - Downloads the URL
        - Stores raw body to CONTENT_DIR as a .md file
        - Creates an item entry referencing that file
        """

        self._ensure_db()
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)

        # Download content
        logger.info("Downloading content from %s", url)
        try:
            with urlrequest.urlopen(url, timeout=20) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                body_bytes = resp.read()
                body_text = body_bytes.decode(charset, errors="replace")
        except urlerror.URLError as exc:
            logger.error("Failed to download %s: %s", url, exc)
            raise

        # Derive ID if not provided
        conn = self._connect()
        try:
            base_id = id or self._slugify(title or url)
            final_id = self._ensure_unique_id(base_id, conn)
        finally:
            conn.close()

        # Write content file
        content_path = CONTENT_DIR / f"{final_id}.md"
        content_path.write_text(body_text, encoding="utf-8")
        word_count = len(body_text.split())

        # Create DB entry
        item = self.add(
            id=final_id,
            item_type=item_type,
            title=title,
            url=url,
            content=None,
            content_path=str(content_path),
            source_type=source_type,
            platform=platform,
            author=author,
            tags=tags,
            topics=topics,
            notes=notes,
        )

        # Update asset flags
        self.update(
            final_id,
            word_count=word_count,
            has_content=1,
        )

        return item

    # --- Export -----------------------------------------------------------

    def export(
        self,
        item_type: Optional[str] = None,
        fmt: str = "json",
        limit: Optional[int] = None,
    ) -> ExportResult:
        """Export items as JSON or Markdown text.

        Returns an ExportResult where `payload` contains the serialized string.
        """

        fmt = fmt.lower()
        if fmt not in {"json", "markdown"}:
            raise ValueError("format must be 'json' or 'markdown'")

        items = self.search(item_type=item_type, limit=limit or 10000)

        if fmt == "json":
            payload = json.dumps(items, indent=2, default=str)
        else:
            lines: List[str] = []
            for item in items:
                header = f"# {item['title']} ({item['id']})"
                meta_parts = [f"type: {item['item_type']}"]
                if item.get("url"):
                    meta_parts.append(f"url: {item['url']}")
                if item.get("author"):
                    meta_parts.append(f"author: {item['author']}")
                lines.append(header)
                lines.append("")
                lines.append("- " + ", ".join(meta_parts))
                # Prefer inline content; fall back to notes
                content = item.get("content") or item.get("notes") or ""
                if content:
                    lines.append("")
                    lines.append(content)
                lines.append("")
            payload = "\n".join(lines)

        return ExportResult(
            format=fmt,
            item_type=item_type,
            count=len(items),
            payload=payload,
        )


# --- CLI -----------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Content Library v3 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    search_p = subparsers.add_parser("search", help="Search items")
    search_p.add_argument("--query", "-q", help="Text search")
    search_p.add_argument("--type", "-t", help="Item type filter")
    search_p.add_argument("--tag", action="append", help="Tag filter (key=value)")
    search_p.add_argument("--topic", action="append", help="Topic filter")
    search_p.add_argument("--include-deprecated", action="store_true")
    search_p.add_argument("--limit", type=int, default=50)

    # Get
    get_p = subparsers.add_parser("get", help="Get item by ID")
    get_p.add_argument("id", help="Item ID")

    # Add
    add_p = subparsers.add_parser("add", help="Add new item")
    add_p.add_argument("--id", required=True)
    add_p.add_argument("--type", required=True, dest="item_type")
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--url")
    add_p.add_argument("--content")
    add_p.add_argument("--source-type", default="manual")
    add_p.add_argument("--platform")
    add_p.add_argument("--author")
    add_p.add_argument("--tag", action="append", help="Tag (key=value)")
    add_p.add_argument("--topic", action="append", help="Topic")
    add_p.add_argument("--notes")

    # Ingest
    ingest_p = subparsers.add_parser(
        "ingest",
        help="Ingest asset with stored content (articles, decks, etc.)",
    )
    ingest_p.add_argument("--url", required=True)
    ingest_p.add_argument("--type", required=True, dest="item_type")
    ingest_p.add_argument("--title", required=True)
    ingest_p.add_argument(
        "--source-type",
        default="discovered",
        help="Source type: created|discovered|manual (default: discovered)",
    )
    ingest_p.add_argument("--id", help="Optional explicit ID (otherwise derived)")
    ingest_p.add_argument("--platform")
    ingest_p.add_argument("--author")
    ingest_p.add_argument("--tag", action="append", help="Tag (key=value)")
    ingest_p.add_argument("--topic", action="append", help="Topic")
    ingest_p.add_argument("--notes")

    # Update
    update_p = subparsers.add_parser("update", help="Update item")
    update_p.add_argument("id")
    update_p.add_argument("--title")
    update_p.add_argument("--url")
    update_p.add_argument("--content")
    update_p.add_argument("--notes")

    # Deprecate
    dep_p = subparsers.add_parser("deprecate", help="Deprecate item")
    dep_p.add_argument("id")

    # List
    list_p = subparsers.add_parser("list", help="List items")
    list_p.add_argument("--type", "-t")
    list_p.add_argument("--limit", type=int, default=20)

    # Export
    export_p = subparsers.add_parser("export", help="Export items")
    export_p.add_argument(
        "--type",
        "-t",
        help="Item type filter",
    )
    export_p.add_argument(
        "--format",
        "-f",
        required=True,
        choices=["json", "markdown"],
    )
    export_p.add_argument("--limit", type=int, help="Optional max items")

    # Stats
    subparsers.add_parser("stats", help="Show statistics")

    # Lint
    subparsers.add_parser("lint", help="Check for quality issues")

    return parser


def _parse_tags(tag_list: Optional[List[str]]) -> Optional[Dict[str, str]]:
    if not tag_list:
        return None
    tags: Dict[str, str] = {}
    for t in tag_list:
        if "=" not in t:
            logger.warning("Ignoring malformed tag (expected key=value): %s", t)
            continue
        key, value = t.split("=", 1)
        tags[key] = value
    return tags or None


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    lib = ContentLibraryV3()

    if args.command == "search":
        tags = _parse_tags(args.tag)
        results = lib.search(
            query=args.query,
            item_type=args.type,
            tags=tags,
            topics=args.topic,
            include_deprecated=bool(args.include_deprecated),
            limit=int(args.limit),
        )
        print(json.dumps(results, indent=2, default=str))

    elif args.command == "get":
        item = lib.get(args.id)
        if item:
            print(json.dumps(item, indent=2, default=str))
        else:
            print(json.dumps({"error": "Not found", "id": args.id}))
            sys.exit(1)

    elif args.command == "add":
        tags = _parse_tags(args.tag)
        item = lib.add(
            id=args.id,
            item_type=args.item_type,
            title=args.title,
            url=args.url,
            content=args.content,
            source_type=args.source_type,
            platform=args.platform,
            author=args.author,
            tags=tags,
            topics=args.topic,
            notes=args.notes,
        )
        print(json.dumps(item, indent=2, default=str))

    elif args.command == "ingest":
        tags = _parse_tags(args.tag)
        try:
            item = lib.ingest(
                url=args.url,
                item_type=args.item_type,
                title=args.title,
                source_type=args.source_type,
                id=args.id,
                platform=args.platform,
                author=args.author,
                tags=tags,
                topics=args.topic,
                notes=args.notes,
            )
        except Exception as exc:  # noqa: BLE001 (top-level CLI)
            logger.error("Ingest failed: %s", exc)
            sys.exit(1)
        print(json.dumps(item, indent=2, default=str))

    elif args.command == "update":
        updates: Dict[str, Any] = {}
        if args.title:
            updates["title"] = args.title
        if args.url:
            updates["url"] = args.url
        if args.content:
            updates["content"] = args.content
        if args.notes:
            updates["notes"] = args.notes

        if not updates:
            logger.warning("No fields provided to update.")
            sys.exit(1)

        item = lib.update(args.id, **updates)
        if item:
            print(json.dumps(item, indent=2, default=str))
        else:
            print(json.dumps({"error": "Not found", "id": args.id}))
            sys.exit(1)

    elif args.command == "deprecate":
        success = lib.deprecate(args.id)
        print(json.dumps({"success": success, "id": args.id}))
        if not success:
            sys.exit(1)

    elif args.command == "list":
        results = lib.search(item_type=args.type, limit=int(args.limit))
        for item in results:
            print(f"[{item['item_type']}] {item['id']}: {item['title']}")

    elif args.command == "export":
        try:
            result = lib.export(
                item_type=args.type,
                fmt=args.format,
                limit=args.limit,
            )
        except ValueError as exc:
            logger.error("Export failed: %s", exc)
            sys.exit(1)
        print(result.payload)

    elif args.command == "stats":
        stats = lib.stats()
        print(json.dumps(stats, indent=2, default=str))

    elif args.command == "lint":
        issues = lib.lint()
        if issues:
            print(f"Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue['id']}: {issue['issue']}")
            sys.exit(1)
        else:
            print("No issues found.")

    else:  # pragma: no cover - defensive
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover
    main()

