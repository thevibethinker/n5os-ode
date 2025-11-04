#!/usr/bin/env python3
"""
Modern Prompt System - Executable Manager
Unified registry for prompts, scripts, and tools with analytics.
"""

import sqlite3
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/executables.db")

@dataclass
class Executable:
    id: str
    name: str
    type: str  # prompt | script | tool
    file_path: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    version: str = "1.0"
    status: str = "active"
    frontmatter: Optional[Dict] = None
    entrypoint: Optional[str] = None
    dependencies: Optional[List[str]] = None
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def register_executable(
    file_path: str,
    exec_type: str,
    exec_id: Optional[str] = None,
    name: Optional[str] = None,
    **metadata
) -> Executable:
    """Register new executable in database."""
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate ID from filename if not provided
        if not exec_id:
            exec_id = path.stem.lower().replace(" ", "-").replace("_", "-")
        
        # Generate name from filename if not provided
        if not name:
            name = path.stem.replace("-", " ").replace("_", " ").title()
        
        # Prepare data
        tags_json = json.dumps(metadata.get('tags', [])) if metadata.get('tags') else None
        deps_json = json.dumps(metadata.get('dependencies', [])) if metadata.get('dependencies') else None
        frontmatter_json = json.dumps(metadata.get('frontmatter', {})) if metadata.get('frontmatter') else None
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO executables (
                id, name, type, file_path, description, category, tags,
                version, status, frontmatter, entrypoint, dependencies, parent_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exec_id,
            name,
            exec_type,
            str(path.absolute()),
            metadata.get('description'),
            metadata.get('category'),
            tags_json,
            metadata.get('version', '1.0'),
            metadata.get('status', 'active'),
            frontmatter_json,
            metadata.get('entrypoint'),
            deps_json,
            metadata.get('parent_id')
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Registered {exec_type}: {exec_id}")
        return get_executable(exec_id)
        
    except sqlite3.IntegrityError as e:
        logger.error(f"✗ Duplicate: {exec_id} ({file_path})")
        raise ValueError(f"Executable already exists: {exec_id}")
    except Exception as e:
        logger.error(f"✗ Failed to register {file_path}: {e}")
        raise

def get_executable(exec_id: str) -> Optional[Executable]:
    """Get single executable by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM executables WHERE id = ?", (exec_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_executable(row)

def list_executables(
    exec_type: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: str = 'active'
) -> List[Executable]:
    """List executables with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM executables WHERE status = ?"
    params = [status]
    
    if exec_type:
        query += " AND type = ?"
        params.append(exec_type)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if tags:
        # Simple tag matching (contains any)
        tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
        query += f" AND ({tag_conditions})"
        params.extend([f'%{tag}%' for tag in tags])
    
    query += " ORDER BY name"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_executable(row) for row in rows]

def search_executables(query: str) -> List[Executable]:
    """Full-text search across executables."""
    if not query or not query.strip():
        logger.error("✗ Error: Search query cannot be empty")
        raise ValueError("Search query cannot be empty")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT e.* FROM executables e
            JOIN executables_fts fts ON e.rowid = fts.rowid
            WHERE executables_fts MATCH ?
            ORDER BY rank
        """, (query.strip(),))
    except Exception as e:
        logger.error(f"✗ Search error: {e}")
        conn.close()
        raise
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_executable(row) for row in rows]

def update_executable(exec_id: str, dry_run: bool = False, **updates):
    """Update executable metadata."""
    if dry_run:
        # Preview mode - show what would change
        existing = get_executable(exec_id)
        if not existing:
            return {"dry_run": True, "operation": "update", "exec_id": exec_id, "error": "Not found"}
        
        changes = {}
        for key, value in updates.items():
            old_value = getattr(existing, key, None)
            if old_value != value:
                changes[key] = {"old": old_value, "new": value}
        
        return {
            "dry_run": True,
            "operation": "update",
            "exec_id": exec_id,
            "name": existing.name,
            "changes": changes
        }
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    set_clauses = []
    params = []
    
    for key, value in updates.items():
        if key in ['tags', 'dependencies', 'frontmatter'] and value:
            value = json.dumps(value)
        set_clauses.append(f"{key} = ?")
        params.append(value)
    
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(exec_id)
    
    query = f"UPDATE executables SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, params)
    
    conn.commit()
    conn.close()
    
    logger.info(f"✓ Updated: {exec_id}")
    return get_executable(exec_id)

def delete_executable(exec_id: str, dry_run: bool = False):
    """Delete executable from database."""
    if dry_run:
        # Preview mode - show what would be deleted
        existing = get_executable(exec_id)
        if not existing:
            return {"dry_run": True, "operation": "delete", "exec_id": exec_id, "found": False}
        
        return {
            "dry_run": True,
            "operation": "delete",
            "exec_id": exec_id,
            "name": existing.name,
            "type": existing.type,
            "file_path": existing.file_path,
            "found": True
        }
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM executables WHERE id = ?", (exec_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if deleted:
        logger.info(f"✓ Deleted: {exec_id}")
    else:
        logger.warning(f"✗ Not found: {exec_id}")
    
    return deleted

def track_invocation(
    exec_id: str,
    conversation_id: Optional[str] = None,
    trigger_method: str = 'direct'
) -> None:
    """Record executable invocation for analytics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO invocations (executable_id, conversation_id, trigger_method)
        VALUES (?, ?, ?)
    """, (exec_id, conversation_id, trigger_method))
    
    conn.commit()
    conn.close()
    
    logger.debug(f"Tracked invocation: {exec_id}")

def get_usage_stats(exec_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """Get usage statistics."""
    if days < 1:
        logger.error(f"✗ Error: Days must be >= 1, got: {days}")
        raise ValueError(f"Days must be >= 1, got: {days}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    since = (datetime.now() - timedelta(days=days)).isoformat()
    
    if exec_id:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_invocations,
                COUNT(DISTINCT conversation_id) as unique_conversations,
                MAX(invoked_at) as last_invoked
            FROM invocations
            WHERE executable_id = ? AND invoked_at >= ?
        """, (exec_id, since))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'executable_id': exec_id,
            'days': days,
            'total_invocations': row['total_invocations'],
            'unique_conversations': row['unique_conversations'],
            'last_invoked': row['last_invoked']
        }
    else:
        cursor.execute("""
            SELECT 
                executable_id,
                COUNT(*) as invocations
            FROM invocations
            WHERE invoked_at >= ?
            GROUP BY executable_id
            ORDER BY invocations DESC
            LIMIT 20
        """, (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            'days': days,
            'top_executables': [
                {'id': row['executable_id'], 'invocations': row['invocations']}
                for row in rows
            ]
        }

def _row_to_executable(row: sqlite3.Row) -> Executable:
    """Convert database row to Executable object."""
    return Executable(
        id=row['id'],
        name=row['name'],
        type=row['type'],
        file_path=row['file_path'],
        description=row['description'],
        category=row['category'],
        tags=json.loads(row['tags']) if row['tags'] else None,
        version=row['version'],
        status=row['status'],
        frontmatter=json.loads(row['frontmatter']) if row['frontmatter'] else None,
        entrypoint=row['entrypoint'],
        dependencies=json.loads(row['dependencies']) if row['dependencies'] else None,
        parent_id=row['parent_id'],
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )

def register_reference(
    file_path: str,
    name: str,
    description: str,
    category: str = "business",
    tags: Optional[List[str]] = None,
    context_tags: Optional[List[str]] = None,
    mutability: str = "living",
    audience: str = "both",
    **metadata
) -> str:
    """
    Convenience wrapper for registering reference documents.
    
    References are living documents that provide context to AI.
    Examples: metrics.md, team_roster.md, product_roadmap.md
    
    Args:
        file_path: Path to reference file (relative to workspace)
        name: Human-readable name
        description: What this reference contains
        category: Classification (business, technical, product, etc.)
        tags: List of searchable tags
        context_tags: Semantic tags for AI context matching
        mutability: 'immutable' | 'versioned' | 'living'
        audience: 'human' | 'both' | 'machine'
    
    Returns:
        ID of registered reference
    """
    ref_id = f"ref_{Path(file_path).stem.replace('-', '_').replace(' ', '_')}"
    
    # Merge tags
    all_tags = tags or []
    if 'reference' not in all_tags:
        all_tags.append('reference')
    
    return register_executable(
        file_path=file_path,
        exec_type="reference",
        exec_id=ref_id,
        name=name,
        description=description,
        category=category,
        tags=all_tags,
        mutability=mutability,
        audience=audience,
        context_tags=','.join(context_tags) if context_tags else None,
        **metadata
    )

def search_references(query: str, **filters) -> List[Dict]:
    """
    Search for reference documents specifically.
    
    Args:
        query: Search term (can be empty string for metadata-only filtering)
        **filters: Additional filters (category, tags, context_tags, mutability, audience)
    
    Returns:
        List of matching references as dicts
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Base query for references only
        sql = """
            SELECT * FROM executables 
            WHERE type = 'reference' 
            AND status = 'active'
        """
        params = []
        
        # Add text search if query provided
        if query:
            sql += " AND id IN (SELECT id FROM executables_fts WHERE executables_fts MATCH ?)"
            params.append(query)
        
        # Add metadata filters
        if 'category' in filters:
            sql += " AND category = ?"
            params.append(filters['category'])
        
        if 'mutability' in filters:
            sql += " AND mutability = ?"
            params.append(filters['mutability'])
        
        if 'audience' in filters:
            sql += " AND audience = ?"
            params.append(filters['audience'])
        
        if 'context_tags' in filters:
            # Simple LIKE match for comma-separated context_tags
            for tag in filters['context_tags']:
                sql += " AND context_tags LIKE ?"
                params.append(f'%{tag}%')
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        return results
    finally:
        conn.close()

def update_reference_validation(ref_id: str, validated_at: Optional[str] = None) -> bool:
    """
    Mark a reference as validated (checked for accuracy/currency).
    
    Args:
        ref_id: Reference ID
        validated_at: ISO timestamp (defaults to now)
    
    Returns:
        True if updated successfully
    """
    if not validated_at:
        validated_at = datetime.utcnow().isoformat() + 'Z'
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE executables SET last_validated = ? WHERE id = ? AND type = 'reference'",
            (validated_at, ref_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def list_stale_references(days: int = 30) -> List[Dict]:
    """
    List references not validated recently.
    
    Args:
        days: Consider stale if not validated in this many days (default 30)
    
    Returns:
        List of stale references with metadata
    """
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM executables 
            WHERE type = 'reference' 
            AND status = 'active'
            AND (last_validated IS NULL OR last_validated < ?)
            ORDER BY last_validated ASC NULLS FIRST
            """,
            (cutoff,)
        )
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        return results
    finally:
        conn.close()

def main() -> int:
    parser = argparse.ArgumentParser(description='N5 Executable Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List executables')
    list_parser.add_argument('--type', choices=['prompt', 'script', 'tool', 'reference'])
    list_parser.add_argument('--category')
    list_parser.add_argument('--tags', nargs='+')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search executables')
    search_parser.add_argument('query', help='Search query')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get executable by ID')
    get_parser.add_argument('id', help='Executable ID')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register new executable')
    register_parser.add_argument('file_path', help='Path to file')
    register_parser.add_argument('--type', required=True, choices=['prompt', 'script', 'tool', 'reference'])
    register_parser.add_argument('--id', help='Executable ID (auto-generated if not provided)')
    register_parser.add_argument('--name', help='Display name')
    register_parser.add_argument('--description', help='Description')
    register_parser.add_argument('--category', help='Category')
    register_parser.add_argument('--tags', nargs='+', help='Tags')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Usage statistics')
    stats_parser.add_argument('--id', help='Executable ID (omit for top 20)')
    stats_parser.add_argument('--days', type=int, default=30)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update executable metadata')
    update_parser.add_argument('id', help='Executable ID')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--category', help='New category')
    update_parser.add_argument('--tags', nargs='+', help='New tags')
    update_parser.add_argument('--status', choices=['active', 'deprecated', 'archived'])
    update_parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete executable')
    delete_parser.add_argument('id', help='Executable ID')
    delete_parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    
    args = parser.parse_args()
    
    try:
        if args.command == 'list':
            results = list_executables(
                exec_type=args.type,
                category=args.category,
                tags=args.tags
            )
            print(f"\nFound {len(results)} executables:\n")
            for exe in results:
                tags_str = f"[{', '.join(exe.tags)}]" if exe.tags else ""
                print(f"  {exe.id:30} {exe.type:8} {exe.category or '':15} {tags_str}")
                if exe.description:
                    print(f"    → {exe.description[:80]}")
        
        elif args.command == 'search':
            results = search_executables(args.query)
            print(f"\nFound {len(results)} matches:\n")
            for exe in results:
                print(f"  {exe.id} ({exe.type})")
                print(f"    {exe.description or 'No description'}\n")
        
        elif args.command == 'get':
            exe = get_executable(args.id)
            if exe:
                print(f"\n{exe.name}")
                print(f"  ID: {exe.id}")
                print(f"  Type: {exe.type}")
                print(f"  File: {exe.file_path}")
                print(f"  Category: {exe.category or 'None'}")
                print(f"  Tags: {exe.tags or []}")
                print(f"  Status: {exe.status}")
                print(f"  Description: {exe.description or 'None'}\n")
            else:
                print(f"✗ Not found: {args.id}")
                return 1
        
        elif args.command == 'register':
            metadata = {
                'description': args.description,
                'category': args.category,
                'tags': args.tags
            }
            exe = register_executable(
                args.file_path,
                args.type,
                exec_id=args.id,
                name=args.name,
                **metadata
            )
            print(f"✓ Registered: {exe.id} → {exe.file_path}")
        
        elif args.command == 'stats':
            stats = get_usage_stats(exec_id=args.id, days=args.days)
            print(f"\nUsage Statistics (last {stats['days']} days):\n")
            if args.id:
                print(f"  Executable: {stats['executable_id']}")
                print(f"  Total invocations: {stats['total_invocations']}")
                print(f"  Unique conversations: {stats['unique_conversations']}")
                print(f"  Last invoked: {stats['last_invoked'] or 'Never'}")
            else:
                print("  Top executables:")
                for item in stats['top_executables']:
                    print(f"    {item['id']:30} {item['invocations']:5} invocations")
        
        
        elif args.command == 'update':
            updates = {}
            if args.name: updates['name'] = args.name
            if args.description: updates['description'] = args.description
            if args.category: updates['category'] = args.category
            if args.tags: updates['tags'] = args.tags
            if args.status: updates['status'] = args.status
            
            if not updates:
                print('No updates specified')
                return 1
            
            dry_run = getattr(args, 'dry_run', False)
            result = update_executable(args.id, dry_run=dry_run, **updates)
            
            if isinstance(result, dict) and result.get('dry_run'):
                print('DRY RUN: Update Preview')
                if result.get('changes'):
                    for k, v in result['changes'].items():
                        print(f'  {k}: {v["old"]} -> {v["new"]}')
                print('Run without --dry-run to apply')
            else:
                print(f'Updated: {result.id}')
        
        elif args.command == 'delete':
            dry_run = getattr(args, 'dry_run', False)
            result = delete_executable(args.id, dry_run=dry_run)
            
            if isinstance(result, dict) and result.get('dry_run'):
                if result['found']:
                    print(f'DRY RUN: Would delete {result["name"]} ({result["exec_id"]})')
                else:
                    print(f'Not found: {result["exec_id"]}')
            else:
                if result:
                    print(f'Deleted: {args.id}')
                else:
                    print(f'Not found: {args.id}')
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
