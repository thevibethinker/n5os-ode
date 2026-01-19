#!/usr/bin/env python3
"""
Content Library v5 Dedupe Migration

Executes the 8-step migration plan:
1. Backup database
2. Run schema migration (subtype column + id_redirects table)
3. Identify duplicates by URL
4. Merge curated tags from legacy → canonical
5. Create redirects
6. Deprecate legacy duplicates
7. Deprecate orphan items
8. Backfill subtypes
9. Export mapping artifact

Usage:
    python3 content_library_v5_dedupe.py --dry-run  # Preview changes
    python3 content_library_v5_dedupe.py            # Execute migration
"""

import argparse
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/content_library.db")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")
MIGRATIONS_DIR = Path("/home/workspace/N5/data/migrations")

DUPLICATE_RESOLUTION = {
    "https://calendly.com/v-at-careerspan/30min": {
        "canonical": "calendly_30min",
        "legacy": "meeting_booking_vrijen_only_work_30m_primary"
    },
    "https://calendly.com/v-at-careerspan/check-in-with-vrij-careerspan-30m-extended": {
        "canonical": "calendly_check_in_with_vrij_careerspan_30m_extended",
        "legacy": "meeting_booking_vrijen_only_work_30m_extended"
    },
    "https://calendly.com/v-at-careerspan/extended-discussion-with-vrijen": {
        "canonical": "calendly_extended_discussion_with_vrijen",
        "legacy": "meeting_booking_vrijen_only_work_45m_primary"
    },
    "https://calendly.com/v-at-careerspan/touching-base-with-vrijen-15-min": {
        "canonical": "calendly_touching_base_with_vrijen_15_min",
        "legacy": "meeting_booking_vrijen_only_quick_sync_15m"
    },
    "https://calendly.com/v-at-careerspan/friends-family-link-for-vrijen": {
        "canonical": "calendly_friends_family_link_for_vrijen",
        "legacy": "meeting_booking_vrijen_only_friends_family_45m"
    },
    "https://calendly.com/d/3tw-swc-35s/check-in-with-careerspan-founders": {
        "canonical": "calendly_uuid_2df1e52a-1657-4d83-bfa0-5574c3e9fa63",
        "legacy": "meeting_booking_founders_vrijen_logan_check_in_30m"
    },
    "https://calendly.com/d/42r-vhg-brj/extended-chat-with-careerspan-founders": {
        "canonical": "calendly_uuid_a6cec49a-58d1-4cc1-b6aa-f8b0827b0197",
        "legacy": "meeting_booking_founders_vrijen_logan_extended_chat_45m"
    },
    "https://www.notion.so/vattawar/Interviewing-At-McKinsey-3903b5f328e54d11bb2275f8b3eafdcf": {
        "canonical": "guides_mckinsey_consulting_mba",
        "legacy": "case_notes_mckinsey"
    },
    "https://app.mycareerspan.com/create-account?oid=202oEi9w": {
        "canonical": "careerspan_trial_codes_general",
        "legacy": "careerspan_trial_codes_non_profit_employers"
    }
}

ORPHAN_SCHEDULING_IDS = [
    "vrijen_work_30m_primary",
    "vrijen_work_30m_extended",
    "vrijen_work_45m",
    "vrijen_quick_sync_15m",
    "vrijen_friends_family_45m"
]


def log(msg: str, dry_run: bool = False):
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}{msg}")


def step_1_backup(dry_run: bool) -> str:
    """Create timestamped backup of database."""
    log("STEP 1: Creating database backup...", dry_run)
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"content_library_pre_v5_{timestamp}.db"
    
    if dry_run:
        log(f"  Would backup to: {backup_path}", dry_run)
        return str(backup_path)
    
    shutil.copy2(DB_PATH, backup_path)
    log(f"  Backed up to: {backup_path}")
    return str(backup_path)


def step_2_schema_migration(conn: sqlite3.Connection, dry_run: bool) -> dict:
    """Add subtype column and id_redirects table if not exists."""
    log("STEP 2: Running schema migration...", dry_run)
    
    changes = {"columns_added": [], "tables_created": [], "indexes_created": []}
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(items)")
    existing_cols = {row[1] for row in cur.fetchall()}
    
    new_columns = [
        ("subtype", "TEXT"),
        ("summary", "TEXT"),
        ("managed_fields", "TEXT"),
        ("external_id", "TEXT")
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_cols:
            if dry_run:
                log(f"  Would add column: {col_name} {col_type}", dry_run)
            else:
                cur.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
                log(f"  Added column: {col_name} {col_type}")
            changes["columns_added"].append(col_name)
        else:
            log(f"  Column already exists: {col_name}")
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='id_redirects'")
    if not cur.fetchone():
        if dry_run:
            log("  Would create table: id_redirects", dry_run)
        else:
            cur.execute("""
                CREATE TABLE id_redirects (
                    old_id TEXT PRIMARY KEY,
                    new_id TEXT NOT NULL,
                    migrated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            log("  Created table: id_redirects")
        changes["tables_created"].append("id_redirects")
    else:
        log("  Table already exists: id_redirects")
    
    indexes = [
        ("idx_items_subtype", "items(subtype)"),
        ("idx_items_type_subtype", "items(content_type, subtype)"),
        ("idx_items_external_id", "items(external_id)")
    ]
    
    for idx_name, idx_def in indexes:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx_name}'")
        if not cur.fetchone():
            if dry_run:
                log(f"  Would create index: {idx_name}", dry_run)
            else:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
                log(f"  Created index: {idx_name}")
            changes["indexes_created"].append(idx_name)
    
    if not dry_run:
        conn.commit()
    
    return changes


def step_3_identify_duplicates(conn: sqlite3.Connection, dry_run: bool) -> list:
    """Identify duplicates by URL and return list of (old_id, new_id, url) tuples."""
    log("STEP 3: Identifying duplicates by URL...", dry_run)
    
    cur = conn.cursor()
    cur.execute("""
        SELECT url, GROUP_CONCAT(id, ',') as ids, COUNT(*) as cnt
        FROM items 
        WHERE url IS NOT NULL AND url != '' AND deprecated = 0
        GROUP BY url 
        HAVING cnt > 1
    """)
    
    duplicates = []
    for row in cur.fetchall():
        url, ids_str, count = row
        ids = ids_str.split(',')
        
        if url in DUPLICATE_RESOLUTION:
            resolution = DUPLICATE_RESOLUTION[url]
            canonical = resolution["canonical"]
            legacy = resolution["legacy"]
            
            if canonical in ids and legacy in ids:
                duplicates.append((legacy, canonical, url))
                log(f"  Duplicate: {url}")
                log(f"    Canonical: {canonical}")
                log(f"    Legacy: {legacy}")
            else:
                log(f"  WARNING: Expected IDs not found for {url}")
                log(f"    Expected: {canonical}, {legacy}")
                log(f"    Found: {ids}")
        else:
            log(f"  WARNING: Unexpected duplicate URL: {url}")
            log(f"    IDs: {ids}")
    
    log(f"  Found {len(duplicates)} resolvable duplicate pairs")
    return duplicates


def step_4_merge_tags(conn: sqlite3.Connection, duplicates: list, dry_run: bool) -> dict:
    """Merge curated tags from legacy items to canonical items."""
    log("STEP 4: Merging curated tags...", dry_run)
    
    cur = conn.cursor()
    tags_merged = {}
    
    for old_id, new_id, url in duplicates:
        cur.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (old_id,))
        old_tags = cur.fetchall()
        
        if not old_tags:
            log(f"  No tags to merge from {old_id}")
            tags_merged[old_id] = []
            continue
        
        merged_keys = []
        for tag_key, tag_value in old_tags:
            cur.execute("""
                SELECT 1 FROM tags 
                WHERE item_id = ? AND tag_key = ? AND tag_value = ?
            """, (new_id, tag_key, tag_value))
            
            if not cur.fetchone():
                if dry_run:
                    log(f"  Would merge tag: {old_id} -> {new_id}: {tag_key}={tag_value}", dry_run)
                else:
                    cur.execute("""
                        INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                        VALUES (?, ?, ?)
                    """, (new_id, tag_key, tag_value))
                merged_keys.append(tag_key)
        
        unique_keys = list(set(merged_keys))
        tags_merged[old_id] = unique_keys
        log(f"  Merged {len(unique_keys)} unique tag keys from {old_id} -> {new_id}")
    
    if not dry_run:
        conn.commit()
    
    return tags_merged


def step_5_create_redirects(conn: sqlite3.Connection, duplicates: list, dry_run: bool) -> int:
    """Create redirect entries in id_redirects table."""
    log("STEP 5: Creating redirects...", dry_run)
    
    cur = conn.cursor()
    redirects_created = 0
    
    for old_id, new_id, url in duplicates:
        cur.execute("SELECT 1 FROM id_redirects WHERE old_id = ?", (old_id,))
        if cur.fetchone():
            log(f"  Redirect already exists: {old_id} -> {new_id}")
            continue
        
        if dry_run:
            log(f"  Would create redirect: {old_id} -> {new_id}", dry_run)
        else:
            cur.execute("""
                INSERT INTO id_redirects (old_id, new_id)
                VALUES (?, ?)
            """, (old_id, new_id))
            log(f"  Created redirect: {old_id} -> {new_id}")
        redirects_created += 1
    
    if not dry_run:
        conn.commit()
    
    log(f"  Total redirects created: {redirects_created}")
    return redirects_created


def step_6_deprecate_duplicates(conn: sqlite3.Connection, duplicates: list, dry_run: bool) -> int:
    """Mark legacy duplicate items as deprecated."""
    log("STEP 6: Deprecating legacy duplicates...", dry_run)
    
    cur = conn.cursor()
    deprecated_count = 0
    
    old_ids = [d[0] for d in duplicates]
    
    for old_id in old_ids:
        cur.execute("SELECT deprecated FROM items WHERE id = ?", (old_id,))
        row = cur.fetchone()
        if row and row[0] == 1:
            log(f"  Already deprecated: {old_id}")
            continue
        
        if dry_run:
            log(f"  Would deprecate: {old_id}", dry_run)
        else:
            cur.execute("UPDATE items SET deprecated = 1 WHERE id = ?", (old_id,))
            log(f"  Deprecated: {old_id}")
        deprecated_count += 1
    
    if not dry_run:
        conn.commit()
    
    log(f"  Total legacy duplicates deprecated: {deprecated_count}")
    return deprecated_count


def step_7_deprecate_orphans(conn: sqlite3.Connection, dry_run: bool) -> list:
    """Deprecate orphan scheduling items with no URL."""
    log("STEP 7: Deprecating orphan items...", dry_run)
    
    cur = conn.cursor()
    deprecated_orphans = []
    
    for orphan_id in ORPHAN_SCHEDULING_IDS:
        cur.execute("""
            SELECT id, deprecated, url FROM items 
            WHERE id = ?
        """, (orphan_id,))
        row = cur.fetchone()
        
        if not row:
            log(f"  Orphan not found: {orphan_id}")
            continue
        
        item_id, deprecated, url = row
        
        if deprecated == 1:
            log(f"  Already deprecated: {orphan_id}")
            continue
        
        if url:
            log(f"  WARNING: Orphan has URL, skipping: {orphan_id} -> {url}")
            continue
        
        if dry_run:
            log(f"  Would deprecate orphan: {orphan_id}", dry_run)
        else:
            cur.execute("UPDATE items SET deprecated = 1 WHERE id = ?", (orphan_id,))
            log(f"  Deprecated orphan: {orphan_id}")
        deprecated_orphans.append(orphan_id)
    
    if not dry_run:
        conn.commit()
    
    log(f"  Total orphans deprecated: {len(deprecated_orphans)}")
    return deprecated_orphans


def step_8_backfill_subtypes(conn: sqlite3.Connection, dry_run: bool) -> dict:
    """Backfill subtype field based on URL patterns and source."""
    log("STEP 8: Backfilling subtypes...", dry_run)
    
    cur = conn.cursor()
    subtype_counts = {}
    
    subtype_rules = [
        {
            "subtype": "scheduling-link",
            "query": """
                UPDATE items SET subtype = 'scheduling-link'
                WHERE content_type = 'link' 
                AND subtype IS NULL
                AND deprecated = 0
                AND (source = 'calendly-sync' 
                     OR source_file_path LIKE '%calendly%'
                     OR url LIKE '%calendly.com%')
            """
        },
        {
            "subtype": "profile",
            "query": """
                UPDATE items SET subtype = 'profile'
                WHERE content_type = 'link'
                AND subtype IS NULL
                AND deprecated = 0
                AND (url LIKE '%linkedin.com/in/%'
                     OR url LIKE '%github.com/%'
                     OR url LIKE '%vrijenattawar.com%'
                     OR url LIKE '%twitter.com/%'
                     OR url LIKE '%x.com/%')
            """
        },
        {
            "subtype": "trial-code",
            "query": """
                UPDATE items SET subtype = 'trial-code'
                WHERE content_type = 'link'
                AND subtype IS NULL
                AND deprecated = 0
                AND id LIKE '%trial_code%'
            """
        }
    ]
    
    for rule in subtype_rules:
        subtype = rule["subtype"]
        
        if dry_run:
            count_query = rule["query"].replace("UPDATE items SET subtype =", "SELECT COUNT(*) FROM items WHERE subtype IS NULL AND")
            count_query = count_query.replace(f"'{subtype}'", "1=1")
            count_query = count_query.replace("WHERE content_type", "AND content_type")
            
            try:
                cur.execute(f"""
                    SELECT COUNT(*) FROM items
                    WHERE content_type = 'link'
                    AND subtype IS NULL
                    AND deprecated = 0
                    AND (source = 'calendly-sync' 
                         OR source_file_path LIKE '%calendly%'
                         OR url LIKE '%calendly.com%')
                """) if subtype == "scheduling-link" else None
            except:
                pass
            
            log(f"  Would backfill subtype: {subtype}", dry_run)
            subtype_counts[subtype] = "N/A (dry-run)"
        else:
            cur.execute(rule["query"])
            count = cur.rowcount
            subtype_counts[subtype] = count
            log(f"  Backfilled {count} items with subtype: {subtype}")
    
    if not dry_run:
        conn.commit()
        
        cur.execute("""
            SELECT subtype, COUNT(*) FROM items 
            WHERE subtype IS NOT NULL AND deprecated = 0
            GROUP BY subtype
        """)
        for row in cur.fetchall():
            subtype_counts[row[0]] = row[1]
    
    log(f"  Subtype counts: {subtype_counts}")
    return subtype_counts


def step_9_export_mapping(duplicates: list, deprecated_orphans: list, 
                         tags_merged: dict, subtype_counts: dict,
                         dry_run: bool) -> str:
    """Export mapping artifact to JSON."""
    log("STEP 9: Exporting mapping artifact...", dry_run)
    
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = MIGRATIONS_DIR / "content_library_v5_id_mapping.json"
    
    mappings = []
    for old_id, new_id, url in duplicates:
        mappings.append({
            "old_id": old_id,
            "new_id": new_id,
            "url": url,
            "tags_merged": tags_merged.get(old_id, [])
        })
    
    artifact = {
        "version": "1.0",
        "migrated_at": datetime.now().isoformat(),
        "mappings": mappings,
        "deprecated": deprecated_orphans,
        "subtype_backfill": subtype_counts
    }
    
    if dry_run:
        log(f"  Would write artifact to: {artifact_path}", dry_run)
        log(f"  Mappings: {len(mappings)}")
        log(f"  Deprecated orphans: {len(deprecated_orphans)}")
    else:
        with open(artifact_path, 'w') as f:
            json.dump(artifact, f, indent=2)
        log(f"  Wrote artifact to: {artifact_path}")
    
    return str(artifact_path)


def run_validation(conn: sqlite3.Connection) -> dict:
    """Run validation tests and return results."""
    print("\n=== VALIDATION TESTS ===")
    
    cur = conn.cursor()
    results = {}
    
    cur.execute("""
        SELECT url, COUNT(*) as cnt 
        FROM items 
        WHERE url IS NOT NULL AND deprecated = 0
        GROUP BY url 
        HAVING cnt > 1
    """)
    remaining_dups = cur.fetchall()
    results["no_url_duplicates"] = len(remaining_dups) == 0
    print(f"1. No URL duplicates: {'PASS' if results['no_url_duplicates'] else 'FAIL'}")
    if remaining_dups:
        print(f"   Remaining duplicates: {remaining_dups}")
    
    cur.execute("SELECT COUNT(*) FROM id_redirects")
    redirect_count = cur.fetchone()[0]
    results["redirects_created"] = redirect_count
    print(f"2. Redirects created: {redirect_count}")
    
    cur.execute("""
        SELECT COUNT(*) FROM items 
        WHERE deprecated = 1 AND source = 'json_migration'
    """)
    deprecated_legacy = cur.fetchone()[0]
    results["legacy_deprecated"] = deprecated_legacy
    print(f"3. Legacy items deprecated: {deprecated_legacy}")
    
    cur.execute("""
        SELECT subtype, COUNT(*) FROM items 
        WHERE subtype IS NOT NULL AND deprecated = 0
        GROUP BY subtype
    """)
    subtype_counts = {row[0]: row[1] for row in cur.fetchall()}
    results["subtypes_backfilled"] = subtype_counts
    print(f"4. Subtypes backfilled: {subtype_counts}")
    
    artifact_path = MIGRATIONS_DIR / "content_library_v5_id_mapping.json"
    results["artifact_exists"] = artifact_path.exists()
    print(f"5. Mapping artifact exists: {'PASS' if results['artifact_exists'] else 'FAIL'}")
    
    cur.execute("PRAGMA table_info(items)")
    columns = {row[1] for row in cur.fetchall()}
    results["schema_updated"] = all(c in columns for c in ["subtype", "summary", "managed_fields", "external_id"])
    print(f"6. Schema updated: {'PASS' if results['schema_updated'] else 'FAIL'}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Content Library v5 Dedupe Migration")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    print("=" * 60)
    print("CONTENT LIBRARY V5 DEDUPE MIGRATION")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    backup_path = step_1_backup(dry_run)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        schema_changes = step_2_schema_migration(conn, dry_run)
        
        duplicates = step_3_identify_duplicates(conn, dry_run)
        
        tags_merged = step_4_merge_tags(conn, duplicates, dry_run)
        
        redirects_created = step_5_create_redirects(conn, duplicates, dry_run)
        
        duplicates_deprecated = step_6_deprecate_duplicates(conn, duplicates, dry_run)
        
        deprecated_orphans = step_7_deprecate_orphans(conn, dry_run)
        
        subtype_counts = step_8_backfill_subtypes(conn, dry_run)
        
        artifact_path = step_9_export_mapping(
            duplicates, deprecated_orphans, tags_merged, subtype_counts, dry_run
        )
        
        if not dry_run:
            validation_results = run_validation(conn)
        else:
            validation_results = {"dry_run": True}
        
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Backup: {backup_path}")
        print(f"Schema changes: {schema_changes}")
        print(f"Duplicates resolved: {len(duplicates)}")
        print(f"Redirects created: {redirects_created}")
        print(f"Legacy items deprecated: {duplicates_deprecated}")
        print(f"Orphans deprecated: {len(deprecated_orphans)}")
        print(f"Subtypes backfilled: {subtype_counts}")
        print(f"Mapping artifact: {artifact_path}")
        
        if not dry_run:
            print("\nValidation Results:")
            for key, value in validation_results.items():
                print(f"  {key}: {value}")
        
    finally:
        conn.close()
    
    return {
        "duplicates_resolved": len(duplicates),
        "redirects_created": redirects_created,
        "items_deprecated": duplicates_deprecated + len(deprecated_orphans),
        "subtypes_backfilled": subtype_counts,
        "mapping_artifact_path": artifact_path,
        "validation_results": validation_results if not dry_run else None
    }


if __name__ == "__main__":
    main()
