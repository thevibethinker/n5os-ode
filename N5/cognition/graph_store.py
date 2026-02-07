#!/usr/bin/env python3
"""
N5 Graph Store — Entity and relationship CRUD + traversal.

Stores graph data in brain.db (entities and relationships tables).
"""

import sqlite3
import hashlib
import logging
import json
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

LOG = logging.getLogger("graph_store")

BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")


@dataclass
class StoredEntity:
    id: str
    name: str
    type: str
    canonical_name: str
    first_seen_at: str
    last_seen_at: str
    mention_count: int
    source_block_id: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class StoredRelationship:
    id: str
    from_entity_id: str
    to_entity_id: str
    relation_type: str
    confidence: float
    context: str
    source_block_id: Optional[str]
    extracted_at: str


class GraphStore:
    """Graph storage and traversal for N5 Brain."""
    
    def __init__(self, db_path: str = str(BRAIN_DB)):
        self.db_path = db_path
        self._conn = None
    
    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn
    
    def _entity_id(self, name: str) -> str:
        """Generate consistent entity ID from name."""
        canonical = name.lower().strip()
        return hashlib.md5(canonical.encode('utf-8')).hexdigest()
    
    def _relationship_id(self, from_id: str, to_id: str, rel_type: str) -> str:
        """Generate consistent relationship ID."""
        return hashlib.md5(f"{from_id}:{to_id}:{rel_type}".encode('utf-8')).hexdigest()
    
    def add_entity(self, name: str, entity_type: str, context: str = "",
                   source_block_id: str = None, metadata: Dict = None) -> str:
        """
        Add or update an entity.
        
        If entity exists (by canonical_name), increments mention_count and updates last_seen_at.
        
        Args:
            name: Entity name
            entity_type: PERSON, CONCEPT, ORG, BELIEF, TOOL, EVENT
            context: Brief context
            source_block_id: Block where entity was found
            metadata: Additional metadata
            
        Returns:
            Entity ID
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        canonical = name.lower().strip()
        entity_id = self._entity_id(name)
        
        # Check if exists
        cursor.execute("SELECT id, mention_count FROM entities WHERE canonical_name = ?", (canonical,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE entities 
                SET last_seen_at = datetime('now'),
                    mention_count = mention_count + 1
                WHERE id = ?
            """, (existing[0],))
            entity_id = existing[0]
            LOG.debug(f"Updated entity: {name} (mentions: {existing[1] + 1})")
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO entities (id, name, type, canonical_name, first_seen_at, last_seen_at, 
                                      mention_count, source_block_id, metadata)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), 1, ?, ?)
            """, (entity_id, name, entity_type, canonical, source_block_id, 
                  json.dumps(metadata) if metadata else None))
            LOG.debug(f"Added entity: {name} [{entity_type}]")
        
        conn.commit()
        return entity_id
    
    def add_relationship(self, from_entity: str, to_entity: str, relation_type: str,
                        context: str = "", confidence: float = 1.0,
                        source_block_id: str = None) -> str:
        """
        Add a relationship between entities.
        
        Creates entities if they don't exist.
        
        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: BELIEVES, KNOWS, WORKS_WITH, USES, MENTIONS, RELATED_TO
            context: Relationship context
            confidence: Confidence score 0-1
            source_block_id: Block where relationship was found
            
        Returns:
            Relationship ID
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Ensure entities exist
        from_id = self._entity_id(from_entity)
        to_id = self._entity_id(to_entity)
        
        # Check if from_entity exists
        cursor.execute("SELECT id FROM entities WHERE id = ?", (from_id,))
        if not cursor.fetchone():
            self.add_entity(from_entity, "CONCEPT", source_block_id=source_block_id)
        
        # Check if to_entity exists
        cursor.execute("SELECT id FROM entities WHERE id = ?", (to_id,))
        if not cursor.fetchone():
            self.add_entity(to_entity, "CONCEPT", source_block_id=source_block_id)
        
        rel_id = self._relationship_id(from_id, to_id, relation_type)
        
        # Upsert relationship
        cursor.execute("""
            INSERT OR REPLACE INTO relationships 
            (id, from_entity_id, to_entity_id, relation_type, confidence, context, 
             source_block_id, extracted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (rel_id, from_id, to_id, relation_type, confidence, context, source_block_id))
        
        conn.commit()
        LOG.debug(f"Added relationship: {from_entity} --{relation_type}--> {to_entity}")
        return rel_id
    
    def get_entity(self, name_or_id: str) -> Optional[StoredEntity]:
        """
        Look up entity by name or ID.
        
        Args:
            name_or_id: Entity name or ID
            
        Returns:
            StoredEntity or None
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Try by ID first
        cursor.execute("SELECT * FROM entities WHERE id = ?", (name_or_id,))
        row = cursor.fetchone()
        
        if not row:
            # Try by canonical name
            canonical = name_or_id.lower().strip()
            cursor.execute("SELECT * FROM entities WHERE canonical_name = ?", (canonical,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return StoredEntity(
            id=row[0],
            name=row[1],
            type=row[2],
            canonical_name=row[3],
            first_seen_at=row[4],
            last_seen_at=row[5],
            mention_count=row[6],
            source_block_id=row[7],
            metadata=json.loads(row[8]) if row[8] else None
        )
    
    def get_connections(self, entity_name: str, depth: int = 1, 
                       relation_types: List[str] = None) -> Dict[str, Any]:
        """
        Get all entities connected to the given entity via BFS traversal.
        
        Args:
            entity_name: Starting entity name
            depth: How many hops to traverse (1 = direct connections only)
            relation_types: Filter by relationship types (None = all)
            
        Returns:
            Dict with 'center', 'entities', 'relationships'
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        center = self.get_entity(entity_name)
        if not center:
            return {"center": None, "entities": [], "relationships": []}
        
        visited_ids: Set[str] = {center.id}
        frontier: Set[str] = {center.id}
        all_entities: List[StoredEntity] = [center]
        all_relationships: List[Dict] = []
        
        for _ in range(depth):
            if not frontier:
                break
            
            next_frontier: Set[str] = set()
            
            for entity_id in frontier:
                # Get outgoing relationships
                if relation_types:
                    placeholders = ','.join('?' * len(relation_types))
                    cursor.execute(f"""
                        SELECT r.*, e.name as to_name
                        FROM relationships r
                        JOIN entities e ON r.to_entity_id = e.id
                        WHERE r.from_entity_id = ? AND r.relation_type IN ({placeholders})
                    """, [entity_id] + relation_types)
                else:
                    cursor.execute("""
                        SELECT r.*, e.name as to_name
                        FROM relationships r
                        JOIN entities e ON r.to_entity_id = e.id
                        WHERE r.from_entity_id = ?
                    """, (entity_id,))
                
                for row in cursor.fetchall():
                    to_id = row[2]
                    all_relationships.append({
                        "id": row[0],
                        "from_id": row[1],
                        "to_id": to_id,
                        "type": row[3],
                        "confidence": row[4],
                        "context": row[5],
                        "to_name": row[8] if len(row) > 8 else None
                    })
                    if to_id not in visited_ids:
                        next_frontier.add(to_id)
                        visited_ids.add(to_id)
                
                # Get incoming relationships
                if relation_types:
                    cursor.execute(f"""
                        SELECT r.*, e.name as from_name
                        FROM relationships r
                        JOIN entities e ON r.from_entity_id = e.id
                        WHERE r.to_entity_id = ? AND r.relation_type IN ({placeholders})
                    """, [entity_id] + relation_types)
                else:
                    cursor.execute("""
                        SELECT r.*, e.name as from_name
                        FROM relationships r
                        JOIN entities e ON r.from_entity_id = e.id
                        WHERE r.to_entity_id = ?
                    """, (entity_id,))
                
                for row in cursor.fetchall():
                    from_id = row[1]
                    all_relationships.append({
                        "id": row[0],
                        "from_id": from_id,
                        "to_id": row[2],
                        "type": row[3],
                        "confidence": row[4],
                        "context": row[5],
                        "from_name": row[8] if len(row) > 8 else None
                    })
                    if from_id not in visited_ids:
                        next_frontier.add(from_id)
                        visited_ids.add(from_id)
            
            frontier = next_frontier
        
        # Fetch all discovered entities
        for entity_id in visited_ids:
            if entity_id != center.id:
                cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                if row:
                    all_entities.append(StoredEntity(
                        id=row[0], name=row[1], type=row[2], canonical_name=row[3],
                        first_seen_at=row[4], last_seen_at=row[5], mention_count=row[6],
                        source_block_id=row[7], metadata=json.loads(row[8]) if row[8] else None
                    ))
        
        return {
            "center": asdict(center),
            "entities": [asdict(e) for e in all_entities],
            "relationships": all_relationships
        }
    
    def search_entities(self, query: str, entity_type: str = None, 
                       limit: int = 10) -> List[StoredEntity]:
        """
        Fuzzy search for entities by name.
        
        Args:
            query: Search query (matches canonical_name with LIKE)
            entity_type: Filter by type (optional)
            limit: Max results
            
        Returns:
            List of matching entities
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query_like = f"%{query.lower()}%"
        
        if entity_type:
            cursor.execute("""
                SELECT * FROM entities 
                WHERE canonical_name LIKE ? AND type = ?
                ORDER BY mention_count DESC
                LIMIT ?
            """, (query_like, entity_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM entities 
                WHERE canonical_name LIKE ?
                ORDER BY mention_count DESC
                LIMIT ?
            """, (query_like, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append(StoredEntity(
                id=row[0], name=row[1], type=row[2], canonical_name=row[3],
                first_seen_at=row[4], last_seen_at=row[5], mention_count=row[6],
                source_block_id=row[7], metadata=json.loads(row[8]) if row[8] else None
            ))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        entity_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        rel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
        type_counts = dict(cursor.fetchall())
        
        cursor.execute("SELECT relation_type, COUNT(*) FROM relationships GROUP BY relation_type")
        rel_type_counts = dict(cursor.fetchall())
        
        cursor.execute("SELECT name, mention_count FROM entities ORDER BY mention_count DESC LIMIT 10")
        top_entities = cursor.fetchall()
        
        return {
            "total_entities": entity_count,
            "total_relationships": rel_count,
            "entities_by_type": type_counts,
            "relationships_by_type": rel_type_counts,
            "top_entities": [{"name": r[0], "mentions": r[1]} for r in top_entities]
        }
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# CLI for testing
if __name__ == "__main__":
    import sys
    
    store = GraphStore()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "stats":
            stats = store.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif cmd == "search" and len(sys.argv) > 2:
            query = sys.argv[2]
            results = store.search_entities(query)
            for e in results:
                print(f"[{e.type}] {e.name} (mentions: {e.mention_count})")
        
        elif cmd == "connections" and len(sys.argv) > 2:
            entity = sys.argv[2]
            depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = store.get_connections(entity, depth=depth)
            print(f"Center: {result['center']['name'] if result['center'] else 'Not found'}")
            print(f"Connected entities: {len(result['entities'])}")
            print(f"Relationships: {len(result['relationships'])}")
            for rel in result['relationships'][:10]:
                print(f"  {rel.get('from_name', rel['from_id'][:8])} --{rel['type']}--> {rel.get('to_name', rel['to_id'][:8])}")
    else:
        print("Usage: python graph_store.py [stats|search <query>|connections <entity> [depth]]")
    
    store.close()
