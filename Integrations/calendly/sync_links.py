#!/usr/bin/env python3
"""
Sync Calendly event types to Content Library.
Creates searchable markdown files AND DB records for each scheduling link.

V5 upgrade: Non-destructive enrichment
- Writes markdown files to Knowledge/content-library/links/calendly/
- Creates/updates DB records with stable IDs
- Merge policy: automation fills missing context fields, never overwrites existing

Usage:
    python3 Integrations/calendly/sync_links.py
    python3 Integrations/calendly/sync_links.py --dry-run
    python3 Integrations/calendly/sync_links.py --db-only  # Skip markdown file generation
"""
import argparse
import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from calendly_client import CalendlyClient

CONTENT_LIBRARY_PATH = Path("/home/workspace/Knowledge/content-library/links/calendly")
DB_PATH = Path("/home/workspace/N5/data/content_library.db")

# Context fields that are "curated" - automation should only fill if empty
CURATED_TAG_KEYS = {"audience", "priority", "use_when", "purpose", "context"}


def slugify(name: str) -> str:
    """Convert name to filename-safe slug."""
    return name.lower().replace(" ", "-").replace("&", "and").replace("/", "-")


def generate_stable_id(event_type: dict) -> str:
    """
    Generate a stable DB ID from Calendly event type.
    
    Strategy (in order of preference):
    1. Use Calendly slug if available
    2. Fall back to UUID from URI
    
    Format: calendly_<identifier>
    This ensures:
    - Uniqueness per Calendly event type
    - Deterministic (same event always gets same ID)
    - Human-readable when possible
    """
    # Prefer slug if available
    if event_type.get("slug"):
        normalized = event_type["slug"].replace("-", "_")
        return f"calendly_{normalized}"
    
    # Fall back to UUID from URI
    calendly_uuid = event_type["uri"].split("/")[-1]
    return f"calendly_uuid_{calendly_uuid}"


def infer_context_defaults(event_type: dict) -> dict:
    """
    Infer conservative context defaults from event type data.
    
    Returns dict of {tag_key: tag_value} for contextual fields.
    Only provides values we can reasonably infer; errs on side of leaving empty.
    """
    name = event_type.get("name", "").lower()
    slug = (event_type.get("slug") or "").lower()
    description = (event_type.get("description_plain") or "").lower()
    duration = event_type.get("duration", 0)
    
    defaults = {}
    
    # Infer audience from name patterns
    if any(term in name for term in ["friends", "family", "personal"]):
        defaults["audience"] = "personal"
    elif any(term in name for term in ["onboarding", "product", "feedback", "enterprise"]):
        defaults["audience"] = "professional"
    elif any(term in name for term in ["investor", "founder"]):
        defaults["audience"] = "professional"
    # Don't set audience if unclear - leave for manual curation
    
    # Infer purpose from event structure
    defaults["purpose"] = "scheduling"  # Always true for Calendly links
    
    # Add duration as tag for searchability
    if duration:
        defaults["duration"] = f"{duration}min"
    
    # Entity tag for ownership
    defaults["entity"] = "vrijen"
    
    # Provider tag
    defaults["provider"] = "calendly"
    
    return defaults


def get_existing_tags(conn: sqlite3.Connection, item_id: str) -> dict:
    """Get existing tags for an item as {key: value} dict."""
    cursor = conn.execute(
        "SELECT tag_key, tag_value FROM tags WHERE item_id = ?",
        (item_id,)
    )
    tags = {}
    for row in cursor:
        key, value = row
        # For multi-value tags, keep the first one (won't overwrite)
        if key not in tags:
            tags[key] = value
    return tags


def merge_tags(existing: dict, new_defaults: dict) -> tuple[dict, list]:
    """
    Merge existing tags with new defaults using non-destructive policy.
    
    For curated fields: only fill if missing
    For managed fields: always update
    
    Returns: (merged_tags, changes_made)
    """
    merged = existing.copy()
    changes = []
    
    for key, value in new_defaults.items():
        if key in CURATED_TAG_KEYS:
            # Curated field: only fill if empty
            if key not in existing or not existing[key]:
                merged[key] = value
                changes.append(f"Added {key}={value} (was empty)")
        else:
            # Managed field: update if different
            if existing.get(key) != value:
                merged[key] = value
                if key in existing:
                    changes.append(f"Updated {key}: {existing[key]} -> {value}")
                else:
                    changes.append(f"Added {key}={value}")
    
    return merged, changes


def upsert_db_record(
    conn: sqlite3.Connection,
    item_id: str,
    event_type: dict,
    file_path: Path,
    dry_run: bool = False
) -> dict:
    """
    Insert or update a DB record for a Calendly event type.
    
    Uses non-destructive merge for context fields.
    
    Returns: {action: 'created'|'updated'|'unchanged', changes: [...]}
    """
    now = datetime.now().isoformat()
    title = event_type["name"]
    url = event_type["scheduling_url"]
    source_file_path = str(file_path)
    calendly_uuid = event_type["uri"].split("/")[-1]
    
    # Build content (markdown body for searchability)
    slug_display = event_type.get('slug') or 'N/A'
    content = f"""# {title}

**Scheduling Link:** {url}

**Duration:** {event_type.get('duration', 0)} minutes

**Slug:** `{slug_display}`

## Description
{event_type.get('description_plain', 'No description provided.')}
"""
    
    # Check if record exists
    existing = conn.execute(
        "SELECT * FROM items WHERE id = ?", (item_id,)
    ).fetchone()
    
    if existing:
        # Record exists - update managed fields, preserve curated context
        existing_tags = get_existing_tags(conn, item_id)
        new_defaults = infer_context_defaults(event_type)
        merged_tags, tag_changes = merge_tags(existing_tags, new_defaults)
        
        if dry_run:
            return {
                "action": "would_update" if tag_changes else "unchanged",
                "changes": tag_changes,
                "existing_tags": existing_tags,
                "merged_tags": merged_tags
            }
        
        # Update managed fields
        conn.execute("""
            UPDATE items SET
                title = ?,
                content = ?,
                url = ?,
                source_file_path = ?,
                updated_at = ?
            WHERE id = ?
        """, (title, content, url, source_file_path, now, item_id))
        
        # Update tags (delete and re-insert with merged values)
        if tag_changes:
            conn.execute("DELETE FROM tags WHERE item_id = ?", (item_id,))
            for key, value in merged_tags.items():
                conn.execute(
                    "INSERT INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                    (item_id, key, value)
                )
        
        return {
            "action": "updated" if tag_changes else "unchanged",
            "changes": tag_changes
        }
    
    else:
        # New record - insert with defaults
        new_defaults = infer_context_defaults(event_type)
        
        if dry_run:
            return {
                "action": "would_create",
                "changes": [f"New record with tags: {new_defaults}"],
                "merged_tags": new_defaults
            }
        
        conn.execute("""
            INSERT INTO items (
                id, title, content_type, content, url, source,
                source_file_path, created_at, updated_at, has_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, title, "link", content, url, "calendly-sync",
            source_file_path, now, now, 1
        ))
        
        # Insert tags
        for key, value in new_defaults.items():
            conn.execute(
                "INSERT INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                (item_id, key, value)
            )
        
        return {
            "action": "created",
            "changes": [f"New record with tags: {new_defaults}"]
        }


def write_markdown_file(event_type: dict, filepath: Path, dry_run: bool = False) -> bool:
    """
    Write/update markdown file for a Calendly event type.
    
    Returns True if file was written/would be written.
    """
    duration = event_type.get("duration", 0)
    calendly_uuid = event_type["uri"].split("/")[-1]
    
    content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: calendly-sync
type: scheduling-link
source: calendly
---

# {event_type['name']}

**Scheduling Link:** {event_type['scheduling_url']}

**Duration:** {duration} minutes

**Slug:** `{event_type.get('slug') or 'N/A'}`

## Description
{event_type.get('description_plain', 'No description provided.')}

## Quick Copy
```
{event_type['scheduling_url']}
```

## Metadata
- **UUID:** `{calendly_uuid}`
- **Color:** {event_type.get('color', 'N/A')}
- **Kind:** {event_type.get('kind', 'N/A')}
- **Pooling Type:** {event_type.get('pooling_type', 'N/A')}
"""
    
    if dry_run:
        return True
    
    filepath.write_text(content)
    return True


def sync_links(dry_run: bool = False, db_only: bool = False):
    """
    Fetch all Calendly event types and sync to Content Library.
    
    Creates:
    1. Markdown files (unless --db-only)
    2. DB records with merged context tags
    """
    try:
        client = CalendlyClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    user = client.get_current_user()
    event_types = client.list_event_types(user_uri=user["uri"])
    
    if not db_only:
        CONTENT_LIBRARY_PATH.mkdir(parents=True, exist_ok=True)
    
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Ensure tags table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            item_id TEXT NOT NULL,
            tag_key TEXT NOT NULL,
            tag_value TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            PRIMARY KEY (item_id, tag_key, tag_value)
        )
    """)
    
    stats = {
        "synced_files": 0,
        "skipped_inactive": 0,
        "db_created": 0,
        "db_updated": 0,
        "db_unchanged": 0,
    }
    
    for et in event_types:
        if not et.get("active"):
            stats["skipped_inactive"] += 1
            continue
        
        # Generate identifiers
        file_slug = slugify(et["name"])
        filename = f"{file_slug}.md"
        filepath = CONTENT_LIBRARY_PATH / filename
        item_id = generate_stable_id(et)
        
        # 1. Write markdown file
        if not db_only:
            write_markdown_file(et, filepath, dry_run)
            stats["synced_files"] += 1
            action_prefix = "[DRY-RUN] " if dry_run else ""
            print(f"{action_prefix}✓ File: {et['name']} → {filename}")
        
        # 2. Upsert DB record
        result = upsert_db_record(conn, item_id, et, filepath, dry_run)
        
        action = result["action"]
        if action in ("created", "would_create"):
            stats["db_created"] += 1
        elif action in ("updated", "would_update"):
            stats["db_updated"] += 1
        else:
            stats["db_unchanged"] += 1
        
        if result["changes"]:
            changes_str = "; ".join(result["changes"][:3])
            if len(result["changes"]) > 3:
                changes_str += f" (+{len(result['changes']) - 3} more)"
            print(f"  DB [{action}]: {changes_str}")
    
    if not dry_run:
        conn.commit()
    conn.close()
    
    # Summary
    print(f"\n{'='*50}")
    mode = "[DRY-RUN] " if dry_run else ""
    print(f"{mode}Sync Complete")
    print(f"  Files synced: {stats['synced_files']}")
    print(f"  Skipped (inactive): {stats['skipped_inactive']}")
    print(f"  DB created: {stats['db_created']}")
    print(f"  DB updated: {stats['db_updated']}")
    print(f"  DB unchanged: {stats['db_unchanged']}")
    if not db_only:
        print(f"  Location: {CONTENT_LIBRARY_PATH}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync Calendly event types to Content Library (files + DB)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Only update DB records, skip markdown file generation"
    )
    
    args = parser.parse_args()
    sync_links(dry_run=args.dry_run, db_only=args.db_only)


if __name__ == "__main__":
    main()
