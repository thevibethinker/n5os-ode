#!/usr/bin/env python3
"""
Positions System - Core knowledge storage with semantic search.

Stores V's compound insights, beliefs, and worldview positions.

Canonical embedding layer:
- Uses `N5/cognition/brain.db` via `N5/cognition/n5_memory_client.py`
- positions.db remains as metadata storage (no longer writes/updates embeddings)
"""

import argparse
import json
import os
import sqlite3
import sys
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "positions.db"
DEFAULT_SIMILARITY_THRESHOLD = 0.75

BRAIN_TAG = "positions"
RESOURCE_PATH_PREFIX = "n5://positions/"

# Evidence types for structured evidence entries
EVIDENCE_TYPES = ["content_library", "meeting", "url", "file", "conversation", "article"]


def _get_memory_client():
    """Lazy import to avoid hard dependency if cognition layer isn't available."""
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from N5.cognition.n5_memory_client import N5MemoryClient
    return N5MemoryClient()


def _position_resource_path(position_id: str) -> str:
    return f"{RESOURCE_PATH_PREFIX}{position_id}"


def _index_position_in_brain(position_id: str, domain: str, title: str, insight: str, content_date: str | None = None) -> None:
    """Upsert a position as a single semantic block in brain.db."""
    client = _get_memory_client()
    path = _position_resource_path(position_id)

    body = f"[Position]\nDomain: {domain}\nID: {position_id}\n\n# {title}\n\n{insight}".strip()
    file_hash = hashlib.md5(body.encode("utf-8")).hexdigest()

    resource_id = client.store_resource(path=path, file_hash=file_hash, content_date=content_date)
    client.delete_resource_blocks(resource_id)
    client.add_block(resource_id, body, block_type="position", start_line=1, end_line=1, content_date=content_date)
    client.tag_resource(path, BRAIN_TAG)


def _extract_position_id_from_path(path: str) -> str | None:
    if not path:
        return None
    if path.startswith(RESOURCE_PATH_PREFIX):
        return path[len(RESOURCE_PATH_PREFIX):]
    return None


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS positions (
            id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            title TEXT NOT NULL,
            insight TEXT NOT NULL,
            components TEXT,
            evidence TEXT,
            connections TEXT,
            stability TEXT DEFAULT 'emerging',
            confidence INTEGER DEFAULT 3,
            formed_date TEXT,
            last_refined TEXT,
            source_conversations TEXT,
            supersedes TEXT,
            embedding BLOB,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reasoning TEXT,
            stakes TEXT,
            conditions TEXT,
            original_excerpt TEXT,
            extraction_method TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_domain ON positions(domain);
        CREATE INDEX IF NOT EXISTS idx_stability ON positions(stability);
    """)
    conn.commit()
    conn.close()


def find_similar(insight: str, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> list[dict]:
    """Find semantically similar positions using the canonical brain.db embeddings."""
    client = _get_memory_client()
    results = client.search(insight, limit=50, tag_filter=BRAIN_TAG, use_hybrid=True)

    filtered: list[dict] = []
    for r in results:
        sim = float(r.get("similarity", 0.0))
        if sim < threshold:
            continue
        pos_id = _extract_position_id_from_path(r.get("path", ""))
        if not pos_id:
            continue
        pos = get_position(pos_id)
        if not pos:
            continue
        filtered.append({
            "id": pos["id"],
            "domain": pos["domain"],
            "title": pos["title"],
            "insight": pos["insight"],
            "stability": pos["stability"],
            "similarity": round(sim, 4),
        })

    filtered.sort(key=lambda x: x["similarity"], reverse=True)
    return filtered


def generate_id(title: str) -> str:
    slug = title.lower()
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = "-".join(slug.split())
    return slug[:50] if slug else str(uuid.uuid4())[:8]


def add_position(
    domain: str,
    title: str,
    insight: str,
    components: list[str] | None = None,
    evidence: list[str] | None = None,
    connections: list[dict] | None = None,
    stability: str = "emerging",
    confidence: int = 3,
    formed_date: str | None = None,
    source_conversations: list[str] | None = None,
    supersedes: list[str] | None = None,
    position_id: str | None = None,
    # New wisdom fields
    reasoning: str | None = None,
    stakes: str | None = None,
    conditions: str | None = None,
    original_excerpt: str | None = None,
    extraction_method: str | None = None,
) -> str:
    init_db()
    
    pos_id = position_id or generate_id(title)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    conn = get_db()
    conn.execute("""
        INSERT INTO positions (
            id, domain, title, insight, components, evidence, connections,
            stability, confidence, formed_date, last_refined, source_conversations,
            supersedes, embedding, created_at, updated_at,
            reasoning, stakes, conditions, original_excerpt, extraction_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pos_id,
        domain,
        title,
        insight,
        json.dumps(components) if components else None,
        json.dumps(evidence) if evidence else None,
        json.dumps(connections) if connections else None,
        stability,
        confidence,
        formed_date,
        now,
        json.dumps(source_conversations) if source_conversations else None,
        json.dumps(supersedes) if supersedes else None,
        None,
        now,
        now,
        reasoning,
        stakes,
        conditions,
        original_excerpt,
        extraction_method,
    ))
    conn.commit()
    conn.close()

    # Canonical embedding write - include reasoning in the indexed text
    indexed_text = insight
    if reasoning:
        indexed_text += f"\n\nReasoning: {reasoning}"
    if stakes:
        indexed_text += f"\n\nStakes: {stakes}"
    _index_position_in_brain(pos_id, domain=domain, title=title, insight=indexed_text, content_date=formed_date)

    return pos_id


def promote_from_candidate(candidate: dict) -> str:
    """Promote an approved candidate to a full position."""
    # Generate title from first ~8 words of insight
    insight = candidate.get("insight", "")
    title_words = insight.split()[:8]
    title = " ".join(title_words)
    if len(title_words) < len(insight.split()):
        title += "..."
    
    return add_position(
        domain=candidate.get("domain", "unknown"),
        title=title,
        insight=insight,
        reasoning=candidate.get("reasoning"),
        stakes=candidate.get("stakes"),
        conditions=candidate.get("conditions"),
        original_excerpt=candidate.get("source_excerpt"),
        extraction_method="b32_v2",
        stability="emerging",
        confidence=3,
        formed_date=candidate.get("extracted_at", "")[:10] if candidate.get("extracted_at") else None,
        source_conversations=[candidate.get("source_meeting")] if candidate.get("source_meeting") else None,
    )


def extend_position(
    position_id: str,
    add_component: str | None = None,
    add_evidence: dict | None = None,
    add_connection: dict | None = None,
    source_conversation: str | None = None,
    bidirectional: bool = True
) -> None:
    conn = get_db()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Position not found: {position_id}")
    
    components = json.loads(row["components"]) if row["components"] else []
    evidence = json.loads(row["evidence"]) if row["evidence"] else []
    connections = json.loads(row["connections"]) if row["connections"] else []
    sources = json.loads(row["source_conversations"]) if row["source_conversations"] else []
    
    if add_component and add_component not in components:
        components.append(add_component)
    if add_evidence and add_evidence not in evidence:
        evidence.append(add_evidence)
    if add_connection:
        existing_targets = {c.get("target_id") for c in connections}
        if add_connection.get("target_id") not in existing_targets:
            connections.append(add_connection)
            
            # Add bidirectional connection
            if bidirectional:
                reverse_relationship = get_reverse_relationship(add_connection.get("relationship", "related"))
                target_id = add_connection.get("target_id")
                try:
                    _add_reverse_connection(conn, target_id, position_id, reverse_relationship)
                except Exception as e:
                    print(f"Warning: Failed to add reverse connection to {target_id}: {e}", file=sys.stderr)
                    
    if source_conversation and source_conversation not in sources:
        sources.append(source_conversation)
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        UPDATE positions SET
            components = ?,
            evidence = ?,
            connections = ?,
            source_conversations = ?,
            last_refined = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        json.dumps(components),
        json.dumps(evidence),
        json.dumps(connections),
        json.dumps(sources),
        now,
        now,
        position_id
    ))
    conn.commit()
    conn.close()


def get_reverse_relationship(relationship: str) -> str:
    """Get the reverse of a relationship for bidirectional connections."""
    reverses = {
        "supports": "supported_by",
        "supported_by": "supports",
        "extends": "extended_by",
        "extended_by": "extends",
        "contradicts": "contradicts",
        "prerequisite": "enables",
        "enables": "prerequisite",
        "implies": "implied_by",
        "implied_by": "implies",
        "related": "related"
    }
    return reverses.get(relationship, "related")


def _add_reverse_connection(conn: sqlite3.Connection, target_id: str, source_id: str, relationship: str) -> None:
    """Add reverse connection to target position (internal helper)."""
    row = conn.execute("SELECT connections FROM positions WHERE id = ?", (target_id,)).fetchone()
    if not row:
        return
    
    connections = json.loads(row["connections"]) if row["connections"] else []
    existing_targets = {c.get("target_id") for c in connections}
    
    if source_id not in existing_targets:
        connections.append({"target_id": source_id, "relationship": relationship})
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE positions SET connections = ?, updated_at = ?
            WHERE id = ?
        """, (json.dumps(connections), now, target_id))


def update_position(
    position_id: str,
    title: str | None = None,
    insight: str | None = None,
    domain: str | None = None,
    stability: str | None = None,
    confidence: int | None = None
) -> None:
    """Update core fields of a position."""
    conn = get_db()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Position not found: {position_id}")
    
    updates = []
    values = []
    
    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if insight is not None:
        updates.append("insight = ?")
        values.append(insight)
        # embeddings are canonical in brain.db; do not write to positions.db
        updates.append("embedding = NULL")
    if domain is not None:
        updates.append("domain = ?")
        values.append(domain)
    if stability is not None:
        updates.append("stability = ?")
        values.append(stability)
    if confidence is not None:
        updates.append("confidence = ?")
        values.append(confidence)
    
    if not updates:
        conn.close()
        return
    
    now = datetime.now(timezone.utc).isoformat()
    updates.append("last_refined = ?")
    values.append(now)
    updates.append("updated_at = ?")
    values.append(now)
    values.append(position_id)

    conn.execute(f"UPDATE positions SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    # Re-index canonical brain entry using latest values
    updated = conn.execute("SELECT domain, title, insight, formed_date FROM positions WHERE id = ?", (position_id,)).fetchone()
    conn.close()
    _index_position_in_brain(
        position_id,
        domain=updated["domain"],
        title=updated["title"],
        insight=updated["insight"],
        content_date=updated["formed_date"],
    )


def delete_position(position_id: str, remove_connections: bool = True) -> None:
    """Delete a position and optionally remove connections to it from other positions."""
    conn = get_db()
    row = conn.execute("SELECT id FROM positions WHERE id = ?", (position_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Position not found: {position_id}")

    if remove_connections:
        # Remove this position from other positions' connections
        all_positions = conn.execute("SELECT id, connections FROM positions WHERE id != ?", (position_id,)).fetchall()
        for pos in all_positions:
            connections = json.loads(pos["connections"]) if pos["connections"] else []
            new_connections = [c for c in connections if c.get("target_id") != position_id]
            if len(new_connections) != len(connections):
                conn.execute("UPDATE positions SET connections = ? WHERE id = ?",
                           (json.dumps(new_connections), pos["id"]))

    conn.execute("DELETE FROM positions WHERE id = ?", (position_id,))
    conn.commit()
    conn.close()

    # Cascade delete from brain.db
    try:
        brain_db_path = Path(__file__).parent.parent / "cognition" / "brain.db"
        brain_conn = sqlite3.connect(brain_db_path)
        path = _position_resource_path(position_id)

        # Find resource ID by path
        row = brain_conn.execute("SELECT id FROM resources WHERE path = ?", (path,)).fetchone()
        if row:
            resource_id = row[0]
            # Delete vectors, blocks, tags, then resource
            brain_conn.execute("""
                DELETE FROM vectors WHERE block_id IN (
                    SELECT id FROM blocks WHERE resource_id = ?
                )
            """, (resource_id,))
            brain_conn.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
            brain_conn.execute("DELETE FROM tags WHERE resource_id = ?", (resource_id,))
            brain_conn.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
            brain_conn.commit()
        brain_conn.close()
    except Exception as e:
        print(f"Warning: Failed to delete from brain.db: {e}", file=sys.stderr)


def cleanup_orphans(dry_run: bool = True) -> list[str]:
    """Find and remove brain.db entries with no matching positions.db record.

    Returns list of orphaned position IDs.
    """
    # Get all position IDs from positions.db
    conn = get_db()
    rows = conn.execute("SELECT id FROM positions").fetchall()
    conn.close()
    positions_db_ids = {row["id"] for row in rows}

    # Query brain.db directly to get all position-tagged resources
    brain_db_path = Path(__file__).parent.parent / "cognition" / "brain.db"
    brain_conn = sqlite3.connect(brain_db_path)
    brain_conn.row_factory = sqlite3.Row

    # Find all resources tagged with "positions"
    brain_resources = brain_conn.execute("""
        SELECT r.id, r.path FROM resources r
        JOIN tags t ON r.id = t.resource_id
        WHERE t.tag = ?
    """, (BRAIN_TAG,)).fetchall()

    # Extract position IDs from paths and find orphans
    orphans = []
    orphan_resource_ids = []
    for row in brain_resources:
        path = row["path"]
        resource_id = row["id"]
        pos_id = _extract_position_id_from_path(path)
        if pos_id and pos_id not in positions_db_ids:
            orphans.append(pos_id)
            orphan_resource_ids.append(resource_id)

    if not dry_run and orphan_resource_ids:
        # Delete orphans directly from brain.db
        for resource_id in orphan_resource_ids:
            try:
                # Delete vectors first
                brain_conn.execute("""
                    DELETE FROM vectors WHERE block_id IN (
                        SELECT id FROM blocks WHERE resource_id = ?
                    )
                """, (resource_id,))
                # Delete blocks
                brain_conn.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
                # Delete tags
                brain_conn.execute("DELETE FROM tags WHERE resource_id = ?", (resource_id,))
                # Delete resource
                brain_conn.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
            except Exception as e:
                print(f"Warning: Failed to delete orphan resource {resource_id}: {e}", file=sys.stderr)
        brain_conn.commit()

    brain_conn.close()
    return orphans


def export_position(position_id: str) -> str:
    """Export a position to markdown format."""
    pos = get_position(position_id)
    if not pos:
        raise ValueError(f"Position not found: {position_id}")
    
    lines = [
        "---",
        f"position_id: {pos['id']}",
        f"domain: {pos['domain']}",
        f"stability: {pos['stability']}",
        f"confidence: {pos['confidence']}",
        f"created: {pos['created_at'][:10] if pos['created_at'] else 'unknown'}",
        f"last_refined: {pos['last_refined'][:10] if pos['last_refined'] else 'unknown'}",
        "---",
        "",
        f"# {pos['title']}",
        "",
        "## Insight",
        "",
        pos['insight'],
        ""
    ]
    
    if pos.get('components'):
        lines.extend(["## Components", ""])
        for c in pos['components']:
            lines.append(f"- {c}")
        lines.append("")
    
    if pos.get('evidence'):
        lines.extend(["## Evidence", ""])
        for e in pos['evidence']:
            if isinstance(e, dict):
                lines.append(f"- [{e.get('type', 'note')}] {e.get('reference', e.get('value', ''))}")
            else:
                lines.append(f"- {e}")
        lines.append("")
    
    if pos.get('connections'):
        lines.extend(["## Connections", ""])
        for c in pos['connections']:
            lines.append(f"- {c.get('relationship', 'related')} → {c.get('target_id', '')}")
        lines.append("")
    
    if pos.get('source_conversations'):
        lines.extend(["## Sources", ""])
        for s in pos['source_conversations']:
            lines.append(f"- {s}")
        lines.append("")
    
    return "\n".join(lines)


def list_domains() -> list[str]:
    """List all unique domains."""
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT domain FROM positions ORDER BY domain").fetchall()
    conn.close()
    return [r["domain"] for r in rows]


def get_position(position_id: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "domain": row["domain"],
        "title": row["title"],
        "insight": row["insight"],
        "components": json.loads(row["components"]) if row["components"] else [],
        "evidence": json.loads(row["evidence"]) if row["evidence"] else [],
        "connections": json.loads(row["connections"]) if row["connections"] else [],
        "stability": row["stability"],
        "confidence": row["confidence"],
        "formed_date": row["formed_date"],
        "last_refined": row["last_refined"],
        "source_conversations": json.loads(row["source_conversations"]) if row["source_conversations"] else [],
        "supersedes": json.loads(row["supersedes"]) if row["supersedes"] else [],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def list_positions(domain: str | None = None) -> list[dict]:
    conn = get_db()
    if domain:
        rows = conn.execute(
            "SELECT id, domain, title, stability, confidence, last_refined FROM positions WHERE domain = ? ORDER BY updated_at DESC",
            (domain,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, domain, title, stability, confidence, last_refined FROM positions ORDER BY updated_at DESC"
        ).fetchall()
    conn.close()
    
    return [
        {
            "id": row["id"],
            "domain": row["domain"],
            "title": row["title"],
            "stability": row["stability"],
            "confidence": row["confidence"],
            "last_refined": row["last_refined"]
        }
        for row in rows
    ]


def check_overlap(insight: str, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> list[dict]:
    return find_similar(insight, threshold)


def parse_evidence(evidence_str: str) -> dict:
    """Parse evidence string into structured format.
    
    Formats:
        content_library:item-id
        meeting:folder-name
        url:https://example.com
        file:path/to/file.md
        conversation:con_XXX
        article:title-or-id
    """
    if ":" not in evidence_str:
        return {"type": "note", "value": evidence_str}
    
    type_part, value_part = evidence_str.split(":", 1)
    type_part = type_part.strip().lower().replace("-", "_")
    value_part = value_part.strip()
    
    if type_part in EVIDENCE_TYPES:
        return {"type": type_part, "reference": value_part}
    else:
        return {"type": "note", "value": evidence_str}


def format_evidence_for_display(evidence: list[dict]) -> list[str]:
    """Format evidence list for human-readable display."""
    lines = []
    for e in evidence:
        if e.get("type") == "note":
            lines.append(f"  - {e.get('value', '')}")
        else:
            lines.append(f"  - [{e.get('type')}] {e.get('reference', '')}")
    return lines


def sync_position_to_entities(position_id: str, delete: bool = False):
    """Sync a single position to edges.db entities table.
    
    Called automatically after add/update/delete operations.
    """
    try:
        from N5.scripts.sync_positions_to_entities import sync_single_position, delete_position_entity
        if delete:
            delete_position_entity(position_id)
            print(f"  ↳ Removed from entities table")
        else:
            sync_single_position(position_id)
            print(f"  ↳ Synced to entities table")
    except ImportError:
        pass  # sync script not available, skip silently
    except Exception as e:
        print(f"  ⚠ Entity sync failed: {e}")


def cmd_add(args):
    sources = [args.source_conversation] if args.source_conversation else None
    
    # Parse evidence entries
    evidence = None
    if args.evidence:
        evidence = [parse_evidence(e) for e in args.evidence]
    
    # Parse component entries
    components = args.components if args.components else None
    
    # Parse connection entries (format: target_id:relationship)
    connections = None
    if args.connections:
        connections = []
        for c in args.connections:
            parts = c.split(":", 1)
            connections.append({
                "target_id": parts[0],
                "relationship": parts[1] if len(parts) > 1 else "related"
            })
    
    position_id = add_position(
        domain=args.domain,
        title=args.title,
        insight=args.insight,
        components=components,
        evidence=evidence,
        connections=connections,
        stability=args.stability,
        confidence=args.confidence,
        source_conversations=sources
    )
    print(f"Added position: {position_id}")
    sync_position_to_entities(position_id)
    
    # Suggest connections if not provided
    if not connections:
        similar = find_similar(args.insight, threshold=0.3)
        related = [s for s in similar if s["id"] != position_id][:3]
        if related:
            print(f"\n💡 Consider connecting to these related positions:")
            for r in related:
                print(f"   [{r['similarity']:.2f}] {r['id']} - {r['title']}")
            print(f"\n   Use: positions.py extend {position_id} --add-connection \"<id>:<relationship>\"")
            print(f"   Relationships: supports, extends, contradicts, prerequisite, implies, related")


def cmd_search(args):
    results = find_similar(args.query, args.threshold)
    if not results:
        print("No similar positions found.")
        return
    print(f"Found {len(results)} similar position(s):\n")
    for r in results:
        print(f"[{r['similarity']:.2f}] {r['id']}")
        print(f"  Domain: {r['domain']} | Stability: {r['stability']}")
        print(f"  Title: {r['title']}")
        print(f"  Insight: {r['insight'][:100]}...")
        print()


def cmd_list(args):
    if args.domains:
        domains = list_domains()
        if not domains:
            print("No domains found.")
            return
        print("Domains:")
        for d in domains:
            print(f"  - {d}")
        return
    
    positions = list_positions(args.domain)
    if not positions:
        print("No positions found.")
        return
    print(f"{'ID':<40} {'Domain':<15} {'Stability':<10} {'Title'}")
    print("-" * 100)
    for p in positions:
        print(f"{p['id']:<40} {p['domain']:<15} {p['stability']:<10} {p['title'][:35]}")


def cmd_get(args):
    pos = get_position(args.id)
    if not pos:
        print(f"Position not found: {args.id}")
        sys.exit(1)
    print(json.dumps(pos, indent=2))


def cmd_extend(args):
    try:
        connection = None
        if args.add_connection:
            parts = args.add_connection.split(":", 1)
            connection = {"target_id": parts[0], "relationship": parts[1] if len(parts) > 1 else "related"}
        
        # Parse evidence into structured format
        evidence = None
        if args.add_evidence:
            evidence = parse_evidence(args.add_evidence)
        
        extend_position(
            args.id,
            add_component=args.add_component,
            add_evidence=evidence,
            add_connection=connection,
            source_conversation=args.source_conversation
        )
        print(f"Extended position: {args.id}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_check_overlap(args):
    results = check_overlap(args.insight, args.threshold)
    if not results:
        print("No overlap found.")
        return
    print(f"Found {len(results)} overlapping position(s):\n")
    for r in results:
        print(f"[{r['similarity']:.2f}] {r['id']} - {r['title']}")


def cmd_suggest_connections(args):
    """Suggest connections for a position based on semantic similarity."""
    pos = get_position(args.id)
    if not pos:
        print(f"Position not found: {args.id}")
        sys.exit(1)
    
    # Find similar positions
    similar = find_similar(pos["insight"], threshold=args.threshold)
    related = [s for s in similar if s["id"] != args.id]
    
    if not related:
        print(f"No related positions found for: {args.id}")
        return
    
    # Filter out already-connected positions
    existing_connections = {c.get("target_id") for c in pos.get("connections", [])}
    unconnected = [r for r in related if r["id"] not in existing_connections]
    
    if not unconnected:
        print(f"All similar positions already connected.")
        return
    
    print(f"Suggested connections for: {pos['title']}\n")
    print(f"{'Similarity':<12} {'ID':<35} {'Title'}")
    print("-" * 90)
    for r in unconnected[:5]:
        print(f"{r['similarity']:<12.2f} {r['id']:<35} {r['title'][:35]}")
    
    print(f"\nTo connect, run:")
    print(f"  python3 positions.py extend {args.id} --add-connection \"<target-id>:<relationship>\"")
    print(f"\nRelationship types: supports, extends, contradicts, prerequisite, implies, related")


def cmd_audit(args):
    """Audit positions for missing evidence and connections."""
    positions = list_positions()
    
    issues = []
    for p in positions:
        pos = get_position(p["id"])
        pos_issues = []
        
        if not pos.get("evidence"):
            pos_issues.append("missing evidence")
        if not pos.get("connections"):
            pos_issues.append("no connections")
        if not pos.get("components"):
            pos_issues.append("no components")
        if not pos.get("source_conversations"):
            pos_issues.append("no source conversation")
        
        if pos_issues:
            issues.append({"id": p["id"], "title": p["title"], "issues": pos_issues})
    
    if not issues:
        print("✅ All positions have evidence, connections, components, and sources.")
        return
    
    print(f"⚠️  Found {len(issues)} position(s) with issues:\n")
    for item in issues:
        print(f"  {item['id']}")
        print(f"    Title: {item['title']}")
        print(f"    Issues: {', '.join(item['issues'])}")
        print()


def cmd_update(args):
    """Update core fields of a position."""
    try:
        update_position(
            args.id,
            title=args.title,
            insight=args.insight,
            domain=args.domain,
            stability=args.stability,
            confidence=args.confidence
        )
        print(f"Updated position: {args.id}")
        sync_position_to_entities(args.id)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_delete(args):
    """Delete a position."""
    if not args.force:
        pos = get_position(args.id)
        if not pos:
            print(f"Position not found: {args.id}")
            sys.exit(1)
        print(f"About to delete: {pos['title']}")
        print(f"  Domain: {pos['domain']}")
        print(f"  Stability: {pos['stability']}")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
    
    try:
        delete_position(args.id, remove_connections=not args.keep_connections)
        print(f"Deleted position: {args.id}")
        sync_position_to_entities(args.id, delete=True)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_export(args):
    """Export a position to markdown."""
    try:
        markdown = export_position(args.id)
        if args.output:
            Path(args.output).write_text(markdown)
            print(f"Exported to: {args.output}")
        else:
            print(markdown)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_cleanup_orphans(args):
    """Find and optionally remove orphaned brain.db entries."""
    dry_run = not args.execute

    orphans = cleanup_orphans(dry_run=dry_run)

    if not orphans:
        print("✅ No orphaned position resources found in brain.db")
        return

    if dry_run:
        print(f"🔍 Found {len(orphans)} orphaned position resource(s) in brain.db:\n")
        for pos_id in orphans:
            print(f"  - {pos_id}")
        print(f"\nRun with --execute to remove these orphans.")
    else:
        print(f"✅ Removed {len(orphans)} orphaned position resource(s) from brain.db:\n")
        for pos_id in orphans:
            print(f"  - {pos_id}")


def main():
    init_db()
    
    parser = argparse.ArgumentParser(description="Positions System - Knowledge storage with semantic search")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a new position")
    add_parser.add_argument("--domain", required=True, help="Domain (e.g., hiring-market)")
    add_parser.add_argument("--title", required=True, help="Position title")
    add_parser.add_argument("--insight", required=True, help="The compound insight")
    add_parser.add_argument("--stability", default="emerging", choices=["emerging", "stable", "canonical"])
    add_parser.add_argument("--confidence", type=int, default=3, choices=[1, 2, 3, 4, 5])
    add_parser.add_argument("--source-conversation", help="Source conversation ID")
    add_parser.add_argument("--evidence", action="append", help="Evidence (format: type:reference). Can be repeated.")
    add_parser.add_argument("--component", dest="components", action="append", help="Component sub-claim. Can be repeated.")
    add_parser.add_argument("--connection", dest="connections", action="append", help="Connection (format: target_id:relationship). Can be repeated.")
    add_parser.set_defaults(func=cmd_add)
    
    # search
    search_parser = subparsers.add_parser("search", help="Semantic search for positions")
    search_parser.add_argument("query", help="Search query text")
    search_parser.add_argument("--threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    search_parser.set_defaults(func=cmd_search)
    
    # list
    list_parser = subparsers.add_parser("list", help="List positions")
    list_parser.add_argument("--domain", help="Filter by domain")
    list_parser.add_argument("--domains", action="store_true", help="List all domains instead of positions")
    list_parser.set_defaults(func=cmd_list)
    
    # get
    get_parser = subparsers.add_parser("get", help="Get a specific position")
    get_parser.add_argument("id", help="Position ID")
    get_parser.set_defaults(func=cmd_get)
    
    # extend
    extend_parser = subparsers.add_parser("extend", help="Extend an existing position")
    extend_parser.add_argument("id", help="Position ID")
    extend_parser.add_argument("--add-component", help="Add a component/sub-claim")
    extend_parser.add_argument("--add-evidence", help="Add evidence (format: type:reference)")
    extend_parser.add_argument("--add-connection", help="Add connection (format: target_id:relationship)")
    extend_parser.add_argument("--source-conversation", help="Source conversation ID")
    extend_parser.set_defaults(func=cmd_extend)
    
    # check-overlap
    overlap_parser = subparsers.add_parser("check-overlap", help="Check for overlapping positions")
    overlap_parser.add_argument("insight", help="Insight text to check")
    overlap_parser.add_argument("--threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    overlap_parser.set_defaults(func=cmd_check_overlap)
    
    # suggest-connections
    suggest_parser = subparsers.add_parser("suggest-connections", help="Suggest connections for a position")
    suggest_parser.add_argument("id", help="Position ID")
    suggest_parser.add_argument("--threshold", type=float, default=0.3, help="Similarity threshold")
    suggest_parser.set_defaults(func=cmd_suggest_connections)
    
    # audit
    audit_parser = subparsers.add_parser("audit", help="Audit positions for missing evidence/connections")
    audit_parser.set_defaults(func=cmd_audit)
    
    # update
    update_parser = subparsers.add_parser("update", help="Update core fields of a position")
    update_parser.add_argument("id", help="Position ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--insight", help="New insight (will re-embed)")
    update_parser.add_argument("--domain", help="New domain")
    update_parser.add_argument("--stability", choices=["emerging", "stable", "canonical"], help="New stability")
    update_parser.add_argument("--confidence", type=int, choices=[1, 2, 3, 4, 5], help="New confidence")
    update_parser.set_defaults(func=cmd_update)
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a position")
    delete_parser.add_argument("id", help="Position ID")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    delete_parser.add_argument("--keep-connections", action="store_true", help="Don't remove connections from other positions")
    delete_parser.set_defaults(func=cmd_delete)
    
    # export
    export_parser = subparsers.add_parser("export", help="Export a position to markdown")
    export_parser.add_argument("id", help="Position ID")
    export_parser.add_argument("--output", "-o", help="Output file path (prints to stdout if not specified)")
    export_parser.set_defaults(func=cmd_export)

    # cleanup-orphans
    cleanup_parser = subparsers.add_parser("cleanup-orphans", help="Find and remove orphaned brain.db entries")
    cleanup_parser.add_argument("--execute", action="store_true", help="Actually remove orphans (default is dry-run)")
    cleanup_parser.set_defaults(func=cmd_cleanup_orphans)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()










