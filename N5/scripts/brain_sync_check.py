#!/usr/bin/env python3
"""
N5 Brain Sync Check

Validates that brain.db and vectors_v2.db are in sync.
Detects and optionally repairs drift between the two databases.

Usage:
    python3 N5/scripts/brain_sync_check.py              # Check only
    python3 N5/scripts/brain_sync_check.py --repair     # Check and fix
    python3 N5/scripts/brain_sync_check.py --verbose    # Show all details
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Add workspace to path for imports
WORKSPACE = Path("/home/workspace")
sys.path.insert(0, str(WORKSPACE))

BRAIN_DB = WORKSPACE / "N5/cognition/brain.db"
VECTORS_DB = WORKSPACE / "N5/cognition/vectors_v2.db"


def get_connection(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)


def check_resources_sync(brain_conn, vectors_conn, verbose=False):
    """Check if resources table is in sync between both DBs."""
    brain_cursor = brain_conn.cursor()
    vectors_cursor = vectors_conn.cursor()
    
    # Get all resources from both
    brain_cursor.execute("SELECT id, path FROM resources")
    brain_resources = {row[0]: row[1] for row in brain_cursor.fetchall()}
    
    vectors_cursor.execute("SELECT id, path FROM resources")
    vectors_resources = {row[0]: row[1] for row in vectors_cursor.fetchall()}
    
    # Find differences
    in_brain_only = set(brain_resources.keys()) - set(vectors_resources.keys())
    in_vectors_only = set(vectors_resources.keys()) - set(brain_resources.keys())
    
    results = {
        "brain_count": len(brain_resources),
        "vectors_count": len(vectors_resources),
        "in_brain_only": [(rid, brain_resources[rid]) for rid in in_brain_only],
        "in_vectors_only": [(rid, vectors_resources[rid]) for rid in in_vectors_only],
    }
    
    if verbose:
        print(f"\n=== Resources Sync ===")
        print(f"brain.db: {results['brain_count']} resources")
        print(f"vectors_v2.db: {results['vectors_count']} resources")
    
    return results


def check_blocks_sync(brain_conn, vectors_conn, resource_ids: list, verbose=False):
    """Check if blocks for given resources exist in vectors_v2.db."""
    brain_cursor = brain_conn.cursor()
    vectors_cursor = vectors_conn.cursor()
    
    missing_blocks = []
    
    for resource_id, path in resource_ids:
        # Get blocks from brain.db
        brain_cursor.execute(
            "SELECT id FROM blocks WHERE resource_id = ?", (resource_id,)
        )
        brain_blocks = [row[0] for row in brain_cursor.fetchall()]
        
        # Check if they exist in vectors_v2.db
        vectors_cursor.execute(
            "SELECT id FROM blocks WHERE resource_id = ?", (resource_id,)
        )
        vectors_blocks = [row[0] for row in vectors_cursor.fetchall()]
        
        if len(brain_blocks) > 0 and len(vectors_blocks) == 0:
            missing_blocks.append({
                "resource_id": resource_id,
                "path": path,
                "brain_block_count": len(brain_blocks),
                "vectors_block_count": len(vectors_blocks)
            })
    
    return missing_blocks


def check_embeddings_exist(vectors_conn, verbose=False):
    """Check for blocks that exist but have no embeddings."""
    cursor = vectors_conn.cursor()
    
    # Find blocks without embeddings
    cursor.execute("""
        SELECT b.id, b.resource_id, r.path
        FROM blocks b
        JOIN resources r ON b.resource_id = r.id
        LEFT JOIN vectors v ON b.id = v.block_id
        WHERE v.block_id IS NULL
    """)
    
    missing = cursor.fetchall()
    
    if verbose and missing:
        print(f"\n=== Blocks Missing Embeddings ===")
        print(f"Found {len(missing)} blocks without embeddings")
    
    return missing


def check_temporal_schema(brain_conn, vectors_conn, verbose=False):
    """Check that temporal tracking columns exist in both databases."""
    brain_cursor = brain_conn.cursor()
    vectors_cursor = vectors_conn.cursor()
    
    # Get schema for both databases
    brain_cursor.execute("PRAGMA table_info(blocks)")
    brain_block_columns = {row[1] for row in brain_cursor.fetchall()}
    
    brain_cursor.execute("PRAGMA table_info(resources)")
    brain_resource_columns = {row[1] for row in brain_cursor.fetchall()}
    
    vectors_cursor.execute("PRAGMA table_info(blocks)")
    vectors_block_columns = {row[1] for row in vectors_cursor.fetchall()}
    
    vectors_cursor.execute("PRAGMA table_info(resources)")
    vectors_resource_columns = {row[1] for row in vectors_cursor.fetchall()}
    
    # Required temporal columns
    required_block_cols = {'indexed_at', 'valid_from', 'valid_until', 'supersedes_block_id'}
    required_resource_cols = {'first_indexed_at', 'version'}
    
    results = {
        'brain': {
            'blocks_missing': required_block_cols - brain_block_columns,
            'resources_missing': required_resource_cols - brain_resource_columns,
        },
        'vectors': {
            'blocks_missing': required_block_cols - vectors_block_columns,
            'resources_missing': required_resource_cols - vectors_resource_columns,
        },
    }
    
    if verbose:
        print(f"\n=== Temporal Schema Check ===")
        if results['brain']['blocks_missing']:
            print(f"  brain.db blocks missing: {results['brain']['blocks_missing']}")
        if results['brain']['resources_missing']:
            print(f"  brain.db resources missing: {results['brain']['resources_missing']}")
        if results['vectors']['blocks_missing']:
            print(f"  vectors_v2.db blocks missing: {results['vectors']['blocks_missing']}")
        if results['vectors']['resources_missing']:
            print(f"  vectors_v2.db resources missing: {results['vectors']['resources_missing']}")
        
        total_missing = sum(
            len(results['brain']['blocks_missing']) + len(results['brain']['resources_missing']) +
            len(results['vectors']['blocks_missing']) + len(results['vectors']['resources_missing'])
        )
        if total_missing == 0:
            print(f"  ✓ All temporal columns present")
    
    return results


def repair_resources(brain_conn, vectors_conn, missing_resources: list, verbose=False):
    """Copy missing resources from brain.db to vectors_v2.db."""
    brain_cursor = brain_conn.cursor()
    vectors_cursor = vectors_conn.cursor()
    
    repaired = 0
    
    for resource_id, path in missing_resources:
        # Get full resource from brain.db
        brain_cursor.execute(
            "SELECT id, path, hash, last_indexed_at, content_date FROM resources WHERE id = ?",
            (resource_id,)
        )
        resource = brain_cursor.fetchone()
        
        if resource:
            # Insert into vectors_v2.db
            vectors_cursor.execute("""
                INSERT OR REPLACE INTO resources (id, path, hash, last_indexed_at, content_date)
                VALUES (?, ?, ?, ?, ?)
            """, resource)
            
            if verbose:
                print(f"  Synced resource: {path}")
            repaired += 1
    
    vectors_conn.commit()
    return repaired


def repair_blocks(brain_conn, vectors_conn, missing_resources: list, verbose=False):
    """Copy missing blocks from brain.db to vectors_v2.db."""
    brain_cursor = brain_conn.cursor()
    vectors_cursor = vectors_conn.cursor()
    
    repaired = 0
    
    for resource_id, path in missing_resources:
        # Get blocks from brain.db
        brain_cursor.execute("""
            SELECT id, resource_id, block_type, content, start_line, end_line, token_count, content_date
            FROM blocks WHERE resource_id = ?
        """, (resource_id,))
        blocks = brain_cursor.fetchall()
        
        for block in blocks:
            vectors_cursor.execute("""
                INSERT OR REPLACE INTO blocks 
                (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, block)
            repaired += 1
        
        if verbose and blocks:
            print(f"  Synced {len(blocks)} blocks for: {path}")
    
    vectors_conn.commit()
    return repaired


def repair_embeddings(vectors_conn, blocks_without_embeddings: list, verbose=False):
    """Generate embeddings for blocks that are missing them."""
    if not blocks_without_embeddings:
        return 0
    
    try:
        from N5.cognition.n5_memory_client import N5MemoryClient
        client = N5MemoryClient()
    except ImportError:
        print("ERROR: Could not import N5MemoryClient for embedding generation")
        return 0
    
    cursor = vectors_conn.cursor()
    repaired = 0
    
    # Group by resource for cleaner output
    by_resource = {}
    for block_id, resource_id, path in blocks_without_embeddings:
        if path not in by_resource:
            by_resource[path] = []
        by_resource[path].append(block_id)
    
    for path, block_ids in by_resource.items():
        if verbose:
            print(f"  Generating embeddings for: {path} ({len(block_ids)} blocks)")
        
        for block_id in block_ids:
            # Get block content
            cursor.execute("SELECT content FROM blocks WHERE id = ?", (block_id,))
            result = cursor.fetchone()
            if not result:
                continue
            
            content = result[0]
            
            # Generate embedding
            try:
                embedding_blob = client.get_embedding(content)
                cursor.execute(
                    "INSERT OR REPLACE INTO vectors (block_id, embedding) VALUES (?, ?)",
                    (block_id, embedding_blob)
                )
                repaired += 1
            except Exception as e:
                print(f"    ERROR embedding block {block_id[:8]}...: {e}")
    
    vectors_conn.commit()
    return repaired


def main():
    parser = argparse.ArgumentParser(description="N5 Brain Sync Check")
    parser.add_argument("--repair", action="store_true", help="Repair drift (not just detect)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--skip-temporal", action="store_true", help="Skip temporal schema check")
    args = parser.parse_args()
    
    print("=" * 50)
    print("N5 Brain Sync Check")
    print("=" * 50)
    
    brain_conn = get_connection(BRAIN_DB)
    vectors_conn = get_connection(VECTORS_DB)
    
    # 1. Check resources sync
    resources_result = check_resources_sync(brain_conn, vectors_conn, args.verbose)
    
    in_brain_only = resources_result["in_brain_only"]
    in_vectors_only = resources_result["in_vectors_only"]
    
    print(f"\nResources: brain.db={resources_result['brain_count']}, vectors_v2.db={resources_result['vectors_count']}")
    
    if in_brain_only:
        print(f"⚠️  {len(in_brain_only)} resources in brain.db but NOT in vectors_v2.db:")
        for rid, path in in_brain_only[:10]:
            print(f"    - {path.replace('/home/workspace/', '')}")
        if len(in_brain_only) > 10:
            print(f"    ... and {len(in_brain_only) - 10} more")
    
    if in_vectors_only:
        print(f"⚠️  {len(in_vectors_only)} resources in vectors_v2.db but NOT in brain.db:")
        for rid, path in in_vectors_only[:5]:
            print(f"    - {path.replace('/home/workspace/', '')}")
    
    # 2. Check for missing embeddings
    missing_embeddings = check_embeddings_exist(vectors_conn, args.verbose)
    
    if missing_embeddings:
        unique_paths = set(item[2] for item in missing_embeddings)
        print(f"⚠️  {len(missing_embeddings)} blocks missing embeddings across {len(unique_paths)} files")
        if args.verbose:
            for path in list(unique_paths)[:5]:
                print(f"    - {path.replace('/home/workspace/', '')}")
    
    # 3. Summary
    issues_found = len(in_brain_only) + len(in_vectors_only) + len(missing_embeddings)
    
    if issues_found == 0:
        print("\n✓ Databases are in sync. No issues found.")
    else:
        print(f"\n⚠️  Found {issues_found} sync issues.")
        
        if args.repair:
            print("\n--- Repairing ---")
            
            # Repair resources
            if in_brain_only:
                repaired = repair_resources(brain_conn, vectors_conn, in_brain_only, args.verbose)
                print(f"✓ Synced {repaired} resources to vectors_v2.db")
            
            # Repair blocks
            if in_brain_only:
                repaired = repair_blocks(brain_conn, vectors_conn, in_brain_only, args.verbose)
                print(f"✓ Synced {repaired} blocks to vectors_v2.db")
            
            # Re-check for missing embeddings after syncing blocks
            missing_embeddings = check_embeddings_exist(vectors_conn, False)
            
            # Repair embeddings
            if missing_embeddings:
                repaired = repair_embeddings(vectors_conn, missing_embeddings, args.verbose)
                print(f"✓ Generated {repaired} embeddings")
            
            print("\n✓ Repair complete.")
        else:
            print("Run with --repair to fix these issues.")
    
    brain_conn.close()
    vectors_conn.close()
    
    return 0 if issues_found == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
