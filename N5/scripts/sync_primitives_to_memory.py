#!/usr/bin/env python3
"""
Sync voice library primitives to semantic memory.

Usage:
  python3 N5/scripts/sync_primitives_to_memory.py sync [--dry-run]
  python3 N5/scripts/sync_primitives_to_memory.py status
  python3 N5/scripts/sync_primitives_to_memory.py resync  # Force resync all
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Load embedding provider config before importing memory client
CONFIG_PATH = Path('/home/workspace/N5/cognition/config.yaml')
if CONFIG_PATH.exists() and 'N5_EMBEDDING_PROVIDER' not in os.environ:
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
            if config.get('embedding_provider'):
                os.environ['N5_EMBEDDING_PROVIDER'] = config['embedding_provider']
    except Exception:
        pass  # Fall back to defaults

# Add N5 to path
sys.path.insert(0, '/home/workspace')
from N5.cognition.n5_memory_client import N5MemoryClient
from N5.lib.paths import BRAIN_DB

# Paths
VOICE_DB = Path('/home/workspace/N5/data/voice_library.db')
PRIMITIVE_PATH_PREFIX = "voice://primitives/"


def get_voice_db() -> sqlite3.Connection:
    """Get connection to voice library database."""
    conn = sqlite3.connect(str(VOICE_DB))
    conn.row_factory = sqlite3.Row
    return conn


def get_approved_primitives() -> List[Dict]:
    """Fetch all approved primitives from voice library."""
    conn = get_voice_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, exact_text, primitive_type, domains_json, 
               distinctiveness_score, notes, created_at, updated_at
        FROM primitives 
        WHERE status = 'approved'
        ORDER BY id
    """)
    
    primitives = []
    for row in cursor.fetchall():
        # Parse domains JSON
        try:
            domains = json.loads(row['domains_json']) if row['domains_json'] else []
        except json.JSONDecodeError:
            domains = []
        
        # Parse notes for extractable_form, context, source
        notes = row['notes'] or ''
        source = 'unknown'
        extractable_form = ''
        context = ''
        
        for part in notes.split(' | '):
            part = part.strip()
            if part.startswith('source:'):
                source = part.replace('source:', '').strip()
            elif part.startswith('extractable_form:'):
                extractable_form = part.replace('extractable_form:', '').strip()
            elif part.startswith('context:'):
                context = part.replace('context:', '').strip()
        
        primitives.append({
            'id': row['id'],
            'exact_text': row['exact_text'],
            'primitive_type': row['primitive_type'],
            'domains': domains,
            'distinctiveness_score': row['distinctiveness_score'],
            'source': source,
            'extractable_form': extractable_form,
            'context': context,
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'notes': notes
        })
    
    conn.close()
    return primitives


def format_primitive_content(p: Dict) -> str:
    """Format primitive for semantic memory storage."""
    lines = [
        f'Voice primitive: "{p["exact_text"]}"',
        f'Type: {p["primitive_type"]}',
    ]
    
    if p['extractable_form']:
        lines.append(f'Pattern: {p["extractable_form"]}')
    
    if p['context']:
        lines.append(f'When to use: {p["context"]}')
    
    if p['domains']:
        lines.append(f'Domains: {", ".join(p["domains"])}')
    
    if p['source']:
        lines.append(f'Source: {p["source"]}')
    
    if p['distinctiveness_score']:
        lines.append(f'Distinctiveness: {p["distinctiveness_score"]:.2f}')
    
    return '\n'.join(lines)


def get_primitive_hash(p: Dict) -> str:
    """Generate hash for primitive content to detect changes."""
    content = f"{p['exact_text']}|{p['primitive_type']}|{json.dumps(p['domains'])}|{p['notes']}"
    return hashlib.md5(content.encode()).hexdigest()


def get_synced_primitives(memory_client: N5MemoryClient) -> Dict[str, str]:
    """Get mapping of primitive IDs to their stored hashes."""
    conn = memory_client._get_db()
    cursor = conn.cursor()
    
    # Find all resources with voice:// prefix
    cursor.execute("""
        SELECT r.path, r.hash 
        FROM resources r
        WHERE r.path LIKE 'voice://primitives/%'
    """)
    
    synced = {}
    for path, hash_val in cursor.fetchall():
        # Extract primitive ID from path
        prim_id = path.replace(PRIMITIVE_PATH_PREFIX, '')
        synced[prim_id] = hash_val
    
    return synced


def sync_primitive(memory_client: N5MemoryClient, p: Dict, dry_run: bool = False) -> bool:
    """Sync a single primitive to semantic memory. Returns True if synced."""
    path = f"{PRIMITIVE_PATH_PREFIX}{p['id']}"
    content = format_primitive_content(p)
    content_hash = get_primitive_hash(p)
    
    if dry_run:
        print(f"  [DRY-RUN] Would sync: {p['id']} ({p['primitive_type']})")
        return True
    
    # Store as resource
    resource_id = memory_client.store_resource(path, content_hash)
    
    # Delete existing blocks for this resource (in case of update)
    memory_client.delete_resource_blocks(resource_id)
    
    # Add block with primitive content
    block_id = memory_client.add_block(
        resource_id=resource_id,
        content=content,
        block_type=f"voice_primitive:{p['primitive_type']}",
        start_line=0,
        end_line=0
    )
    
    # Add tags for domains
    conn = memory_client._get_db()
    cursor = conn.cursor()
    
    # Add domain tags
    for domain in p['domains']:
        cursor.execute("""
            INSERT OR IGNORE INTO tags (resource_id, tag)
            VALUES (?, ?)
        """, (resource_id, f"domain:{domain}"))
    
    # Add type tag
    cursor.execute("""
        INSERT OR IGNORE INTO tags (resource_id, tag)
        VALUES (?, ?)
    """, (resource_id, f"primitive_type:{p['primitive_type']}"))
    
    # Add source tag
    if p['source']:
        cursor.execute("""
            INSERT OR IGNORE INTO tags (resource_id, tag)
            VALUES (?, ?)
        """, (resource_id, f"source:{p['source']}"))
    
    conn.commit()
    return True


def cmd_sync(args):
    """Sync primitives to semantic memory."""
    print("=" * 60)
    print("Voice Primitives → Semantic Memory Sync")
    print("=" * 60)
    
    # Get all approved primitives
    primitives = get_approved_primitives()
    print(f"\nApproved primitives in voice library: {len(primitives)}")
    
    # Initialize memory client
    memory_client = N5MemoryClient()
    
    # Get already synced primitives
    synced = get_synced_primitives(memory_client)
    print(f"Already synced to memory: {len(synced)}")
    
    # Determine what needs syncing
    to_sync = []
    for p in primitives:
        current_hash = get_primitive_hash(p)
        if p['id'] not in synced:
            to_sync.append((p, 'new'))
        elif synced[p['id']] != current_hash:
            to_sync.append((p, 'updated'))
    
    print(f"Need to sync: {len(to_sync)} ({sum(1 for _, t in to_sync if t == 'new')} new, {sum(1 for _, t in to_sync if t == 'updated')} updated)")
    
    if args.dry_run:
        print("\n[DRY-RUN MODE - No changes will be made]\n")
    
    if not to_sync:
        print("\n✓ All primitives already synced!")
        return
    
    # Sync primitives
    synced_count = 0
    errors = []
    
    for p, sync_type in to_sync:
        try:
            if sync_primitive(memory_client, p, dry_run=args.dry_run):
                synced_count += 1
                if not args.dry_run:
                    print(f"  ✓ {p['id']} ({sync_type})")
        except Exception as e:
            errors.append((p['id'], str(e)))
            print(f"  ✗ {p['id']}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"[DRY-RUN] Would sync {synced_count} primitives")
    else:
        print(f"Synced: {synced_count} primitives")
        if errors:
            print(f"Errors: {len(errors)}")
            for pid, err in errors[:5]:
                print(f"  - {pid}: {err}")


def cmd_resync(args):
    """Force resync all primitives (delete existing and re-sync)."""
    print("=" * 60)
    print("Force Resync: Voice Primitives → Semantic Memory")
    print("=" * 60)
    
    memory_client = N5MemoryClient()
    
    # Delete all existing primitive resources
    conn = memory_client._get_db()
    cursor = conn.cursor()
    
    # Get resource IDs to delete
    cursor.execute("""
        SELECT id FROM resources WHERE path LIKE 'voice://primitives/%'
    """)
    resource_ids = [r[0] for r in cursor.fetchall()]
    
    print(f"\nDeleting {len(resource_ids)} existing primitive resources...")
    
    if not args.dry_run:
        for rid in resource_ids:
            memory_client.delete_resource_blocks(rid)
            cursor.execute("DELETE FROM tags WHERE resource_id = ?", (rid,))
            cursor.execute("DELETE FROM resources WHERE id = ?", (rid,))
        conn.commit()
        print(f"  ✓ Deleted {len(resource_ids)} resources")
    else:
        print(f"  [DRY-RUN] Would delete {len(resource_ids)} resources")
    
    # Now sync all
    args_sync = argparse.Namespace(dry_run=args.dry_run)
    cmd_sync(args_sync)


def cmd_status(args):
    """Show sync status."""
    print("=" * 60)
    print("Voice Primitives Sync Status")
    print("=" * 60)
    
    # Get primitives
    primitives = get_approved_primitives()
    print(f"\nVoice Library ({VOICE_DB}):")
    print(f"  Approved primitives: {len(primitives)}")
    
    # Count by type
    type_counts = {}
    for p in primitives:
        t = p['primitive_type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"  By type:")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    - {t}: {count}")
    
    # Check synced
    memory_client = N5MemoryClient()
    synced = get_synced_primitives(memory_client)
    
    print(f"\nSemantic Memory ({BRAIN_DB}):")
    print(f"  Synced primitives: {len(synced)}")
    
    # Check for stale entries
    primitive_ids = {p['id'] for p in primitives}
    synced_ids = set(synced.keys())
    
    orphaned = synced_ids - primitive_ids
    missing = primitive_ids - synced_ids
    
    # Check for content changes
    changed = 0
    for p in primitives:
        if p['id'] in synced:
            if synced[p['id']] != get_primitive_hash(p):
                changed += 1
    
    print(f"\nSync Health:")
    print(f"  Up to date: {len(synced_ids & primitive_ids) - changed}")
    print(f"  Need update: {changed}")
    print(f"  Missing: {len(missing)}")
    print(f"  Orphaned: {len(orphaned)}")
    
    if missing:
        print(f"\n  Missing IDs (first 5): {list(missing)[:5]}")
    if orphaned:
        print(f"  Orphaned IDs (first 5): {list(orphaned)[:5]}")
    
    # Overall status
    total_issues = len(missing) + len(orphaned) + changed
    if total_issues == 0:
        print(f"\n✓ All {len(primitives)} primitives synced and up to date!")
    else:
        print(f"\n⚠ {total_issues} issues found. Run 'sync' to fix.")


def main():
    parser = argparse.ArgumentParser(
        description='Sync voice primitives to semantic memory'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync primitives to memory')
    sync_parser.add_argument('--dry-run', action='store_true', 
                             help='Show what would be synced without making changes')
    sync_parser.set_defaults(func=cmd_sync)
    
    # Resync command
    resync_parser = subparsers.add_parser('resync', help='Force resync all primitives')
    resync_parser.add_argument('--dry-run', action='store_true',
                               help='Show what would be done without making changes')
    resync_parser.set_defaults(func=cmd_resync)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show sync status')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
