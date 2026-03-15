#!/usr/bin/env python3
"""
Content Library Ingest Script
Ingests content files into a Content Library database with auto-detection,
metadata extraction, normalization, and deduplication.

Usage:
    python3 content_ingest.py /path/to/article.md --type article
    python3 content_ingest.py /path/to/file.md --dry-run
    python3 content_ingest.py /path/to/file.md --move
    python3 content_ingest.py /path/to/file.md --db-path ./data/library.db
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

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WORKSPACE = Path.cwd()

TYPE_DIRECTORIES = {
    "article": "articles",
    "deck": "decks",
    "paper": "papers",
    "book": "books",
    "framework": "frameworks",
    "social-post": "social-posts",
    "inspiration": "inspiration",
    "link": "links",
    "snippet": "snippets",
    "podcast": "audio",
    "video": "video",
    "quote": "quotes",
    "personal": "personal",
    "transcript": "transcripts",
}

PATH_TYPE_PATTERNS = [
    (r"/articles/", "article"),
    (r"/decks/", "deck"),
    (r"/papers/", "paper"),
    (r"/books/", "book"),
    (r"/frameworks/", "framework"),
    (r"/social-posts/", "social-post"),
    (r"/inspiration/", "inspiration"),
    (r"/links/", "link"),
    (r"/snippets/", "snippet"),
    (r"/audio/", "podcast"),
    (r"/video/", "video"),
    (r"/quotes/", "quote"),
    (r"/personal/", "personal"),
    (r"/transcripts/", "transcript"),
]


def classify_ingest_mode(filepath: Path, frontmatter: dict) -> str:
    url = frontmatter.get('url', '')
    if 'x.com' in url or 'twitter.com' in url or 'linkedin.com/posts' in url:
        return 'social'
    if 'linkedin.com/in/' in url or 'github.com/' in url:
        if '/in/' in url or url.count('/') <= 4:
            return 'profile'
    article_domains = ['substack.com', 'medium.com', 'nytimes.com', 'wsj.com',
                       'techcrunch.com', 'paulgraham.com', 'stratechery.com',
                       'hbr.org', 'forbes.com', 'wired.com', 'arstechnica.com']
    if any(d in url for d in article_domains):
        return 'article'
    if 'github.com' in url or 'docs.' in url or 'readthedocs.io' in url:
        return 'resource'
    return 'link'


def find_companion_html(md_path: Path) -> Path | None:
    html_path = md_path.with_suffix('.html')
    if html_path.exists():
        return html_path
    stem = md_path.stem
    parent = md_path.parent
    for pattern in [f"{stem}.html", f"{stem}~~*.html"]:
        matches = list(parent.glob(pattern))
        if matches:
            return matches[0]
    return None


def extract_with_trafilatura(html_path: Path) -> dict:
    try:
        import trafilatura
    except ImportError:
        return {'text': '', 'title': None, 'author': None, 'date': None, 'description': None}
    try:
        html_content = html_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return {'text': '', 'title': None, 'author': None, 'date': None, 'description': None}
    result = trafilatura.extract(
        html_content, include_comments=False, include_tables=True,
        no_fallback=False, favor_precision=True, output_format='txt'
    )
    metadata = trafilatura.extract_metadata(html_content)
    return {
        'text': result or '',
        'title': metadata.title if metadata else None,
        'author': metadata.author if metadata else None,
        'date': metadata.date if metadata else None,
        'description': metadata.description if metadata else None,
    }


def heuristic_strip_boilerplate(text: str) -> str:
    if not text:
        return text
    patterns_to_remove = [
        r'^Skip to (?:main )?content.*$',
        r'^Navigation.*$', r'^Menu.*$', r'^Search.*$', r'^Subscribe.*$',
        r'^Sign (?:in|up).*$', r'^Log (?:in|out).*$',
        r'^Follow (?:us )?on.*$', r'^Share (?:this|on).*$',
        r'^Advertisement.*$', r'^Sponsored.*$',
        r'^Related (?:articles?|posts?).*$', r'^Read (?:more|next).*$',
        r'^Comments?.*$', r'^©.*\d{4}.*$',
        r'^Privacy Policy.*$', r'^Terms (?:of (?:Service|Use)|and Conditions).*$',
        r'^Cookie (?:Policy|Settings).*$', r'^All rights reserved.*$',
        r'^\[.*\]\s*$',
    ]
    lines = text.split('\n')
    filtered = []
    for line in lines:
        stripped = line.strip()
        if any(re.match(p, stripped, re.IGNORECASE) for p in patterns_to_remove):
            continue
        filtered.append(line)
    result = '\n'.join(filtered)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result.strip()


def generate_summary(text: str, max_chars: int = 200) -> str:
    if not text or len(text) < 50:
        return ''
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for para in paragraphs:
        if len(para) > 80 and not para.startswith('#'):
            if len(para) > max_chars:
                sentences = para.split('. ')
                summary = ''
                for s in sentences:
                    if len(summary) + len(s) < max_chars:
                        summary += s + '. '
                    else:
                        break
                return summary.strip() or para[:max_chars] + '...'
            return para
    if paragraphs:
        return paragraphs[0][:max_chars] + ('...' if len(paragraphs[0]) > max_chars else '')
    return ''


def normalize_content(filepath: Path, frontmatter: dict, body: str, normalize: bool = True) -> tuple[dict, str]:
    if not normalize:
        return frontmatter, body
    mode = classify_ingest_mode(filepath, frontmatter)
    html_path = find_companion_html(filepath)
    if html_path and mode in ('article', 'resource', 'profile', 'link'):
        extracted = extract_with_trafilatura(html_path)
        if extracted['text'] and len(extracted['text']) > 100:
            body = extracted['text']
            for key in ('title', 'author', 'date', 'description'):
                if extracted.get(key) and not frontmatter.get(key):
                    frontmatter[key] = extracted[key]
    if mode != 'social':
        body = heuristic_strip_boilerplate(body)
    if not frontmatter.get('summary') and body:
        frontmatter['summary'] = generate_summary(body)
    return frontmatter, body


def setup_logging(workspace: Path, dry_run: bool = False) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = workspace / "logs" / "content-ingest" / today
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    suffix = "_dry-run" if dry_run else ""
    return log_dir / f"ingest_{timestamp}{suffix}.json"


def log_result(log_file: Path, result: dict):
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_block = parts[1].strip()
            body = parts[2].strip()
            for line in yaml_block.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        frontmatter[key] = value
    return frontmatter, body


def extract_title_from_filename(filepath: Path) -> str:
    name = filepath.stem
    if " :: " in name:
        name = name.split(" :: ")[0]
    name = name.replace("-", " ").replace("_", " ")
    return name.strip()


def count_words(content: str) -> int:
    text = re.sub(r"[#*`\[\]()>]", " ", content)
    return len(text.split())


def detect_content_type(filepath: Path) -> str:
    path_str = str(filepath)
    for pattern, content_type in PATH_TYPE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return content_type
    ext = filepath.suffix.lower()
    if ext == ".pdf":
        return "deck"
    if ext in (".mp3", ".wav", ".m4a", ".ogg"):
        return "podcast"
    if ext in (".mp4", ".mov", ".avi", ".mkv"):
        return "video"
    if ext == ".md":
        try:
            content = filepath.read_text(encoding="utf-8")[:2000]
            if content.startswith("---") and "\nurl:" in content.lower():
                return "link"
        except Exception:
            pass
    return "link"


def ensure_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT,
            content_type TEXT,
            content TEXT,
            source_file_path TEXT UNIQUE,
            tags TEXT,
            word_count INTEGER,
            ingested_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            has_content INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def record_exists(conn: sqlite3.Connection, source_file_path: str) -> bool:
    cursor = conn.execute("SELECT id FROM items WHERE source_file_path = ?", (source_file_path,))
    return cursor.fetchone() is not None


def create_record(conn, title, content_type, source_file_path, content=None, tags=None, word_count=None) -> str:
    record_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO items (id, title, content_type, content, source_file_path,
            tags, word_count, ingested_at, created_at, updated_at, has_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record_id, title, content_type, content, source_file_path,
          tags, word_count, now, now, now, 1 if content else 0))
    conn.commit()
    return record_id


def get_canonical_path(library_root: Path, content_type: str, filename: str) -> Path:
    subdir = TYPE_DIRECTORIES.get(content_type)
    if subdir is None:
        raise ValueError(f"Unknown content type '{content_type}'. Valid: {list(TYPE_DIRECTORIES.keys())}")
    return library_root / subdir / filename


def ingest_file(filepath, content_type=None, dry_run=False, move=False,
                tags=None, normalize=True, db_path=None, library_root=None, workspace=None):
    if workspace is None:
        workspace = DEFAULT_WORKSPACE
    if db_path is None:
        db_path = workspace / "data" / "content_library.db"
    if library_root is None:
        library_root = workspace / "Knowledge" / "content-library"

    result = {"file": str(filepath), "timestamp": datetime.now().isoformat(), "dry_run": dry_run}

    if not filepath.exists():
        result["status"] = "error"
        result["error"] = f"File not found: {filepath}"
        return result

    if content_type is None:
        content_type = detect_content_type(filepath)
    result["content_type"] = content_type

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Failed to read file: {e}"
        return result

    frontmatter, body = parse_frontmatter(content)
    frontmatter, body = normalize_content(filepath, frontmatter, body, normalize=normalize)
    result["normalized"] = normalize
    if frontmatter.get("summary"):
        s = frontmatter["summary"]
        result["summary"] = s[:100] + "..." if len(s) > 100 else s

    title = frontmatter.get("title") or extract_title_from_filename(filepath)
    result["title"] = title

    file_tags = frontmatter.get("tags", "")
    if tags:
        all_tags = set(file_tags.split(",") if file_tags else [])
        all_tags.update(tags)
        file_tags = ",".join(sorted(t.strip() for t in all_tags if t.strip()))
    result["tags"] = file_tags

    word_count = count_words(body)
    result["word_count"] = word_count

    try:
        current_path = str(filepath.relative_to(workspace))
    except ValueError:
        current_path = str(filepath)
    result["source_file_path"] = current_path

    if move:
        canonical = get_canonical_path(library_root, content_type, filepath.name)
        try:
            result["target_path"] = str(canonical.relative_to(workspace))
        except ValueError:
            result["target_path"] = str(canonical)

    if dry_run:
        result["status"] = "dry_run"
        result["action"] = "would_create"
        return result

    conn = ensure_db(db_path)
    try:
        if record_exists(conn, current_path):
            result["status"] = "skipped"
            result["reason"] = "record_exists"
            return result

        if move:
            canonical = get_canonical_path(library_root, content_type, filepath.name)
            if filepath != canonical:
                canonical.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(filepath), str(canonical))
                try:
                    current_path = str(canonical.relative_to(workspace))
                except ValueError:
                    current_path = str(canonical)
                result["moved_to"] = current_path

        record_id = create_record(
            conn=conn, title=title, content_type=content_type,
            source_file_path=current_path,
            content=body[:10000] if body else None,
            tags=file_tags, word_count=word_count,
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
  %(prog)s file.md --tags "authored,medium"
  %(prog)s file.md --db-path ./my-library.db
        """
    )
    parser.add_argument("file", type=Path, help="Path to file to ingest")
    parser.add_argument("--type", "-t", dest="content_type", choices=list(TYPE_DIRECTORIES.keys()),
                        help="Content type (auto-detected if not specified)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would happen without making changes")
    parser.add_argument("--move", "-m", action="store_true", help="Move file to canonical location")
    parser.add_argument("--tags", type=str, help="Comma-separated tags to add")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output except errors")
    parser.add_argument("--normalize", dest="normalize", action=argparse.BooleanOptionalAction, default=True,
                        help="Apply content normalization (default: True, use --no-normalize to disable)")
    parser.add_argument("--db-path", type=Path, help="Path to SQLite database (default: data/content_library.db)")
    parser.add_argument("--library-path", type=Path, help="Path to content library root (default: Knowledge/content-library)")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace root directory (default: current directory)")

    args = parser.parse_args()

    filepath = args.file.resolve()
    workspace = args.workspace.resolve()

    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]

    log_file = setup_logging(workspace, args.dry_run)

    result = ingest_file(
        filepath=filepath, content_type=args.content_type,
        dry_run=args.dry_run, move=args.move, tags=tags,
        normalize=args.normalize, db_path=args.db_path,
        library_root=args.library_path, workspace=workspace,
    )

    log_result(log_file, result)

    if not args.quiet:
        if result["status"] == "error":
            print(f"Error: {result['error']}")
            exit(1)
        elif result["status"] == "skipped":
            print(f"Skipped: {result['file']} (already exists)")
        elif result["status"] == "dry_run":
            print(f"Dry run: Would create record for '{result['title']}'")
            print(f"   Type: {result['content_type']}")
            print(f"   Words: {result['word_count']}")
            if result.get("target_path"):
                print(f"   Would move to: {result['target_path']}")
        else:
            print(f"Created: '{result['title']}'")
            print(f"   ID: {result['record_id']}")
            print(f"   Type: {result['content_type']}")
            if result.get("moved_to"):
                print(f"   Moved to: {result['moved_to']}")

    if args.quiet:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
