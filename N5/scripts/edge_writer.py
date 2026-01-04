#!/usr/bin/env python3
"""
Edge Writer: Insert and update edges in the context graph.

Usage:
    # Add an edge
    python3 edge_writer.py add \
        --source "idea:context-graph" \
        --relation "originated_by" \
        --target "person:animesh-koratana" \
        --meeting "mtg_2026-01-04" \
        --evidence "Animesh's article introduced the concept"
    
    # Register an entity
    python3 edge_writer.py entity \
        --type "idea" \
        --id "context-graph" \
        --name "Context Graph System for N5"
    
    # Bulk import from review queue
    python3 edge_writer.py import --file /path/to/approved_edges.jsonl
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from edge_types import validate_relation, validate_entity_type, generate_slug, EDGE_TYPES

DB_PATH = Path(__file__).parent.parent / "data" / "edges.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def parse_entity_ref(ref: str) -> tuple[str, str]:
    """Parse 'type:id' reference into (type, id)."""
    if ':' not in ref:
        raise ValueError(f"Invalid entity reference '{ref}'. Expected format: 'type:id'")
    entity_type, entity_id = ref.split(':', 1)
    if not validate_entity_type(entity_type):
        raise ValueError(f"Invalid entity type '{entity_type}'. Valid types: person, idea, decision, meeting, position, commitment")
    return entity_type, entity_id


def ensure_entity(conn: sqlite3.Connection, entity_type: str, entity_id: str, name: Optional[str] = None) -> int:
    """Ensure entity exists in registry, create if not. Returns entity rowid."""
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute(
        "SELECT id FROM entities WHERE entity_type = ? AND entity_id = ?",
        (entity_type, entity_id)
    )
    row = cursor.fetchone()
    
    if row:
        return row['id']
    
    # Create new entity
    cursor.execute(
        "INSERT INTO entities (entity_type, entity_id, name) VALUES (?, ?, ?)",
        (entity_type, entity_id, name or entity_id)
    )
    conn.commit()
    return cursor.lastrowid


def add_edge(
    source: str,
    relation: str,
    target: str,
    meeting: Optional[str] = None,
    evidence: Optional[str] = None,
    status: str = "active"
) -> Dict[str, Any]:
    """
    Add a new edge to the graph.
    
    Args:
        source: Source entity reference (e.g., "idea:context-graph")
        relation: Relation type (e.g., "originated_by")
        target: Target entity reference (e.g., "person:animesh")
        meeting: Optional meeting ID where edge was captured
        evidence: Optional quote or description supporting edge
        status: Edge status (default: active)
    
    Returns:
        Dict with edge_id and status
    """
    # Validate relation
    if not validate_relation(relation):
        raise ValueError(f"Invalid relation '{relation}'. Valid relations: {', '.join(EDGE_TYPES.keys())}")
    
    # Parse entity references
    source_type, source_id = parse_entity_ref(source)
    target_type, target_id = parse_entity_ref(target)
    
    conn = get_connection()
    try:
        # Ensure entities exist
        ensure_entity(conn, source_type, source_id)
        ensure_entity(conn, target_type, target_id)
        
        # Check for duplicate
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM edges 
            WHERE source_type = ? AND source_id = ? 
            AND relation = ? 
            AND target_type = ? AND target_id = ?
            AND status = 'active'
        """, (source_type, source_id, relation, target_type, target_id))
        
        existing = cursor.fetchone()
        if existing:
            return {
                "status": "duplicate",
                "edge_id": existing['id'],
                "message": f"Active edge already exists with id {existing['id']}"
            }
        
        # Insert edge
        cursor.execute("""
            INSERT INTO edges (
                source_type, source_id, relation, target_type, target_id,
                context_meeting_id, evidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (source_type, source_id, relation, target_type, target_id, meeting, evidence, status))
        
        conn.commit()
        edge_id = cursor.lastrowid
        
        return {
            "status": "created",
            "edge_id": edge_id,
            "message": f"Edge created: {source} --{relation}--> {target}"
        }
    finally:
        conn.close()


def register_entity(
    entity_type: str,
    entity_id: str,
    name: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Register an entity in the graph.
    
    Args:
        entity_type: Type of entity (person, idea, decision, etc.)
        entity_id: Unique slug for entity
        name: Human-readable name
        metadata: Optional JSON metadata
    
    Returns:
        Dict with entity info
    """
    if not validate_entity_type(entity_type):
        raise ValueError(f"Invalid entity type '{entity_type}'")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute(
            "SELECT id, name FROM entities WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update if name provided
            if name and name != existing['name']:
                cursor.execute(
                    "UPDATE entities SET name = ? WHERE entity_type = ? AND entity_id = ?",
                    (name, entity_type, entity_id)
                )
                conn.commit()
                return {
                    "status": "updated",
                    "entity_id": f"{entity_type}:{entity_id}",
                    "name": name
                }
            return {
                "status": "exists",
                "entity_id": f"{entity_type}:{entity_id}",
                "name": existing['name']
            }
        
        # Create new
        cursor.execute(
            "INSERT INTO entities (entity_type, entity_id, name, metadata) VALUES (?, ?, ?, ?)",
            (entity_type, entity_id, name or entity_id, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        
        return {
            "status": "created",
            "entity_id": f"{entity_type}:{entity_id}",
            "name": name or entity_id
        }
    finally:
        conn.close()


def import_edges(filepath: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Bulk import edges from JSONL file (typically from review queue).
    
    Each line should be JSON with: source, relation, target, meeting, evidence
    
    Returns:
        Summary of import results
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    results = {"created": 0, "duplicates": 0, "errors": []}
    
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                edge_data = json.loads(line)
                
                if dry_run:
                    print(f"[DRY RUN] Would add: {edge_data.get('source')} --{edge_data.get('relation')}--> {edge_data.get('target')}")
                    results["created"] += 1
                    continue
                
                result = add_edge(
                    source=edge_data['source'],
                    relation=edge_data['relation'],
                    target=edge_data['target'],
                    meeting=edge_data.get('meeting'),
                    evidence=edge_data.get('evidence')
                )
                
                if result['status'] == 'created':
                    results["created"] += 1
                elif result['status'] == 'duplicate':
                    results["duplicates"] += 1
                    
            except Exception as e:
                results["errors"].append({"line": line_num, "error": str(e)})
    
    return results


def get_or_create_idea_slug(description: str) -> str:
    """
    Generate or retrieve an idea slug from description.
    Checks if similar idea exists before creating new.
    """
    slug = generate_slug(description, "idea")
    idea_id = slug.split(':', 1)[1]  # Remove prefix for DB lookup
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Check if this exact slug exists
        cursor.execute(
            "SELECT entity_id FROM entities WHERE entity_type = 'idea' AND entity_id = ?",
            (idea_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            return slug
        
        # Create new idea entity
        cursor.execute(
            "INSERT INTO entities (entity_type, entity_id, name) VALUES (?, ?, ?)",
            ("idea", idea_id, description)
        )
        conn.commit()
        
        return slug
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Edge Writer: Add edges to context graph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add edge command
    add_parser = subparsers.add_parser("add", help="Add a single edge")
    add_parser.add_argument("--source", required=True, help="Source entity (type:id)")
    add_parser.add_argument("--relation", required=True, help="Relation type")
    add_parser.add_argument("--target", required=True, help="Target entity (type:id)")
    add_parser.add_argument("--meeting", help="Meeting ID where edge was captured")
    add_parser.add_argument("--evidence", help="Supporting quote or description")
    
    # Register entity command
    entity_parser = subparsers.add_parser("entity", help="Register an entity")
    entity_parser.add_argument("--type", required=True, dest="entity_type", help="Entity type")
    entity_parser.add_argument("--id", required=True, dest="entity_id", help="Entity ID/slug")
    entity_parser.add_argument("--name", help="Human-readable name")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Bulk import from JSONL")
    import_parser.add_argument("--file", required=True, help="Path to JSONL file")
    import_parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    # Slug generator
    slug_parser = subparsers.add_parser("slug", help="Generate idea slug")
    slug_parser.add_argument("description", help="Idea description")
    
    args = parser.parse_args()
    
    try:
        if args.command == "add":
            result = add_edge(
                source=args.source,
                relation=args.relation,
                target=args.target,
                meeting=args.meeting,
                evidence=args.evidence
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "entity":
            result = register_entity(
                entity_type=args.entity_type,
                entity_id=args.entity_id,
                name=args.name
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "import":
            result = import_edges(args.file, dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
            
        elif args.command == "slug":
            slug = get_or_create_idea_slug(args.description)
            print(slug)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

